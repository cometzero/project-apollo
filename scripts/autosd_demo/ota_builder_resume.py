#!/usr/bin/env python3
"""Restart the existing private AIB builder through the canonical full-system launcher."""
import json
import argparse
import os
from pathlib import Path
import socket
import subprocess

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "build/autosd/demo-ota-followup"
BUILDER = ROOT / "build/autosd/demo-builder-fullsystem"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=WORK,
                        help="Evidence directory; builder-uart.log must not already exist")
    args = parser.parse_args()
    work = args.out.resolve()
    work.mkdir(parents=True, exist_ok=True)
    for directory in (BUILDER, WORK, work):
        pidfile = directory / "launcher.pid"
        if pidfile.exists():
            cmdline = Path("/proc") / pidfile.read_text().strip() / "cmdline"
            if cmdline.exists() and str(BUILDER / "rootfs.wic").encode() in cmdline.read_bytes():
                raise SystemExit("Builder is already running")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 2226))
    launch = json.loads((BUILDER / "launch.json").read_text())
    command = list(launch["command"])
    if not Path(command[0]).name == "run_qbox_autosd.sh":
        raise SystemExit("Legacy direct-QEMU builders cannot be resumed; create a full-system builder")
    previous = Path(command[command.index("--out-dir") + 1])
    receipt = json.loads((previous / "result.json").read_text())
    if receipt.get("status") != "POWERED_OFF" or not receipt.get("poweroff_observed"):
        raise SystemExit("Builder must have a recorded normal poweroff before copying its disks")
    for flag, value in (("--out-dir", work / "vm"), ("--rootfs", previous / "rootfs.wic"),
                        ("--scratch-disk", previous / "efi-capsule.img")):
        command[command.index(flag) + 1] = str(value)
    environment = launch.get("environment", {})
    with (work / "builder-uart.log").open("xb") as log:
        child = subprocess.Popen(command, env=os.environ | environment,
                                 stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
        (work / "launcher.pid").write_text(str(child.pid) + "\n")
        return child.wait()


if __name__ == "__main__":
    raise SystemExit(main())
