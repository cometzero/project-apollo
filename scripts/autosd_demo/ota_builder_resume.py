#!/usr/bin/env python3
"""Restart the existing private AIB builder without copying its large disks."""
import json
import os
from pathlib import Path
import socket
import subprocess

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "build/autosd/demo-ota-followup"
BUILDER = ROOT / "build/autosd/demo-builder-fullsystem"


def main():
    WORK.mkdir(exist_ok=True)
    for directory in (BUILDER, WORK):
        pidfile = directory / "qemu.pid"
        if pidfile.exists():
            cmdline = Path("/proc") / pidfile.read_text().strip() / "cmdline"
            if cmdline.exists() and str(BUILDER / "rootfs.wic").encode() in cmdline.read_bytes():
                raise SystemExit("Builder is already running")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 2226))
    launch = json.loads((BUILDER / "launch.json").read_text())
    environment = json.loads((ROOT / "build/autosd/demo-regular-session/launch.json").read_text())["environment"]
    with (WORK / "builder-uart.log").open("xb") as log:
        child = subprocess.Popen(launch["command"], env=os.environ | environment,
                                 stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
        (WORK / "qemu.pid").write_text(str(child.pid) + "\n")
        return child.wait()


if __name__ == "__main__":
    raise SystemExit(main())
