#!/usr/bin/env python3
"""Create an isolated full-system AArch64 AIB builder (not a demo target)."""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/run"))
from autosd_uki import inspect_uki


def main():
    work = ROOT / "build/autosd/demo-builder-fullsystem"
    previous = ROOT / "build/autosd/demo-regular-session"
    pidfile = previous / "qemu.pid"
    if pidfile.exists():
        proc = Path("/proc") / pidfile.read_text().strip() / "cmdline"
        if proc.exists() and str(previous / "rootfs.wic").encode() in proc.read_bytes():
            raise SystemExit("Source demo VM is running; shut it down before copying its disk")
    if shutil.disk_usage(ROOT).free < 32 * 1024**3:
        raise SystemExit("At least 32 GiB free space is required for this builder")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 2226))
    work.mkdir(exist_ok=False)
    launch = json.loads((previous / "launch.json").read_text())
    # Use the immutable UKI already captured by the prior boot, not changing deploy symlinks.
    uki = previous / "autosd.efi"
    section = inspect_uki(uki)["sections"][".linux"]
    with uki.open("rb") as source:
        source.seek(section["offset"])
        (work / "Image").write_bytes(source.read(section["size"]))
    shutil.copyfile(ROOT / "build/autosd/regular-initrd.img", work / "initrd.img")
    # Source was shut down before copying; cp preserves sparse holes.
    subprocess.run(["cp", "--sparse=always", "--reflink=auto", str(previous / "rootfs.wic"), str(work / "rootfs.wic")], check=True)
    with (work / "scratch.raw").open("xb") as disk:
        disk.truncate(24 * 1024**3)
    manifest = json.loads((ROOT / "build/autosd/regular.json").read_text())
    command = [launch["command"][0], "-machine", "apollo-qvp", "-accel", "tcg", "-smp", "4", "-m", "4080M",
               "-display", "none", "-monitor", "none", "-serial", "stdio", "-kernel", str(work / "Image"),
               "-initrd", str(work / "initrd.img"), "-append", manifest["bootargs"],
               "-drive", f"if=none,id=rootfs,format=raw,file={work}/rootfs.wic",
               "-device", "virtio-blk-device,drive=rootfs,bus=virtio-mmio-bus.0",
               "-netdev", "user,id=net0,hostfwd=tcp:127.0.0.1:2226-:22",
               "-device", "virtio-net-device,netdev=net0,bus=virtio-mmio-bus.1",
               "-drive", f"if=none,id=scratch,format=raw,file={work}/scratch.raw",
               "-device", "virtio-blk-device,drive=scratch,bus=virtio-mmio-bus.2"]
    (work / "launch.json").write_text(json.dumps({"command": command, "kernel_sha256": section["sha256"], "purpose": "isolated full-system AIB builder; direct boot is not UKIBoot qualification"}, indent=2) + "\n")
    env = os.environ | launch["environment"]
    with (work / "uart.log").open("wb") as log:
        child = subprocess.Popen(command, env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
        (work / "qemu.pid").write_text(str(child.pid) + "\n")
        return child.wait()


if __name__ == "__main__":
    raise SystemExit(main())
