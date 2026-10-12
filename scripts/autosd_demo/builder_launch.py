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
from autosd_manifest import autosd_manifest
from run_qbox_autosd import required


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--build-dir", type=Path, default=ROOT / "build")
    p.add_argument("--deploy-dir", type=Path)
    p.add_argument("--manifest", type=Path, help="default: BUILD_DIR/autosd/regular.json")
    p.add_argument("--rootfs", type=Path, help="override the manifest source disk")
    p.add_argument("--modules", type=Path)
    p.add_argument("--guestfish", default="guestfish")
    p.add_argument("--uki", type=Path, help="default: Apollo BSP UKI")
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
    manifest = manifest.absolute()
    inputs = autosd_manifest(manifest)
    source = required(args.rootfs or Path(inputs["rootfs"]), "builder rootfs")
    deploy = (args.deploy_dir or args.build_dir / "tmp_baremetal/deploy/images/apollo-qvp").absolute()
    uki = required(args.uki or deploy / "nexios-bsp-initramfs-a.efi", "builder UKI")
    command = [str(ROOT / "run_qbox_autosd.sh"), "--autosd", str(manifest),
               "--rootfs", str(source), "--uki", str(uki),
               "--build-dir", str(args.build_dir.absolute()), "--deploy-dir", str(deploy),
               "--headless", "--out-dir", str(work / "vm"),
               "--ssh-port", str(args.ssh_port), "--scratch-disk", str(work / "scratch.raw"),
               "--timeout", "14400", "--modules-archive",
               str(args.modules or deploy / "modules-apollo-qvp.tgz"), "--guestfish", args.guestfish]
    return {"command": command, "environment": {}, "source_rootfs": str(source),
            "uki": str(uki), "work_dir": str(work), "manifest": str(manifest),
            "ssh_port": args.ssh_port, "purpose": "isolated full-system QBox AIB builder"}


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
        with (work / "scratch.raw").open("xb") as disk:
            disk.truncate(24 * 1024**3)
        plan["uki_sha256"] = hashlib.sha256(Path(plan["uki"]).read_bytes()).hexdigest()
        (work / "launch.json").write_text(json.dumps(plan, indent=2) + "\n")
        with (work / "uart.log").open("xb") as log:
            child = subprocess.Popen(plan["command"], env=os.environ | plan["environment"],
                                     stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
            (work / "launcher.pid").write_text(str(child.pid) + "\n")
            return child.wait()
    except (ValueError, OSError) as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    raise SystemExit(main())
