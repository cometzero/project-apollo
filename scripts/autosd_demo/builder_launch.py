#!/usr/bin/env python3
"""Create an isolated full-system AArch64 AIB builder (not a demo target)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/run"))
import run_qemu_linux


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--build-dir", type=Path, default=ROOT / "build")
    p.add_argument("--deploy-dir", type=Path)
    p.add_argument("--manifest", type=Path, help="default: BUILD_DIR/autosd/regular.json")
    p.add_argument("--rootfs", type=Path, help="override the manifest source disk")
    p.add_argument("--kernel", type=Path, help="default: Apollo Yocto deploy Image")
    p.add_argument("--qemu", type=Path, help="default: canonical Yocto QEMU provider")
    p.add_argument("--work-dir", type=Path, default=ROOT / "build/autosd/demo-builder-fullsystem")
    p.add_argument("--ssh-port", type=int, default=2226)
    p.add_argument("--dry-run", action="store_true")
    return p


def assert_source_inactive(source, proc_root=Path("/proc")):
    """Reject a disk referenced by a live VM, including aliases via open FDs."""
    for process in proc_root.iterdir():
        if not process.name.isdigit():
            continue
        try:
            command = (process / "cmdline").read_bytes()
            if not any(name in command for name in (b"qemu", b"qbox")):
                continue
            if str(source).encode() in command:
                raise ValueError(f"Source VM is running (PID {process.name}); shut it down before copying its disk")
            for fd in (process / "fd").iterdir():
                try:
                    if fd.samefile(source):
                        raise ValueError(f"Source VM is running (PID {process.name}); shut it down before copying its disk")
                except OSError:
                    continue
        except (FileNotFoundError, PermissionError):
            continue


def make_plan(args):
    if not 1 <= args.ssh_port <= 65535:
        raise ValueError("SSH port must be between 1 and 65535")
    work = args.work_dir.absolute()
    if work.exists():
        raise ValueError(f"Builder output already exists; preserve it and choose a new --work-dir: {work}")
    manifest = args.manifest or args.build_dir / "autosd/regular.json"
    forwarded = ["--build-dir", str(args.build_dir), "--autosd", str(manifest), "--netdev",
                 f"user,id=net0,hostfwd=tcp:127.0.0.1:{args.ssh_port}-:22"]
    for flag, value in (("--rootfs", args.rootfs), ("--kernel", args.kernel),
                        ("--qemu", args.qemu), ("--deploy-dir", args.deploy_dir)):
        if value is not None:
            forwarded += [flag, str(value)]
    plan = run_qemu_linux.make_plan(run_qemu_linux.parser().parse_args(forwarded), work)
    command = plan["command"]
    start = command.index("-chardev")
    end = command.index("-kernel")
    command[start:end] = ["-monitor", "none", "-serial", "stdio"]
    command[-2:] = ["-drive", f"if=none,id=scratch,format=raw,file={str(work / 'scratch.raw').replace(',', ',,')}",
                    "-device", "virtio-blk-device,drive=scratch,bus=virtio-mmio-bus.2"]
    command[command.index("-kernel") + 1] = str(work / "Image")
    command[command.index("-initrd") + 1] = str(work / "initrd.img")
    # Nightly debug/expedited-RCU settings make the TCG builder needlessly slow.
    debug_args = {"slub_debug=FPZ", "rcupdate.rcu_expedited=1", "rcupdate.rcu_normal_after_boot=0"}
    append = command.index("-append") + 1
    command[append] = " ".join(word for word in command[append].split() if word not in debug_args)
    plan["layout"] = "unattended builder; persistent uart.log"
    plan.update(work_dir=str(work), manifest=str(manifest.absolute()), ssh_port=args.ssh_port,
                purpose="isolated full-system AIB builder; direct boot is not UKIBoot qualification")
    return plan


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        plan = make_plan(args)
        source = Path(plan["source_rootfs"]).resolve()
        assert_source_inactive(source)
        if args.dry_run:
            print(json.dumps(plan, indent=2))
            return 0
        work = Path(plan["work_dir"])
        ancestor = work.parent
        while not ancestor.exists():
            ancestor = ancestor.parent
        if shutil.disk_usage(ancestor).free < 32 * 1024**3:
            raise ValueError("At least 32 GiB free space is required for this builder")
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", args.ssh_port))
        work.mkdir(parents=True, exist_ok=False)
        shutil.copyfile(plan["kernel"], work / "Image")
        shutil.copyfile(plan["initrd"], work / "initrd.img")
        subprocess.run(["cp", "--sparse=always", "--reflink=auto", str(source), str(work / "rootfs.wic")], check=True)
        with (work / "scratch.raw").open("xb") as disk:
            disk.truncate(24 * 1024**3)
        plan["kernel_sha256"] = hashlib.sha256((work / "Image").read_bytes()).hexdigest()
        (work / "launch.json").write_text(json.dumps(plan, indent=2) + "\n")
        with (work / "uart.log").open("xb") as log:
            child = subprocess.Popen(plan["command"], env=os.environ | plan["environment"],
                                     stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
            (work / "qemu.pid").write_text(str(child.pid) + "\n")
            return child.wait()
    except (ValueError, OSError) as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    raise SystemExit(main())
