#!/usr/bin/env python3
"""Bounded transient service watchdog demo; never changes PID 1 watchdog policy."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import uuid


def worker():
    address = os.environ["NOTIFY_SOCKET"]
    if address.startswith("@"):
        address = "\0" + address[1:]
    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as channel:
        channel.connect(address)
        channel.send(b"READY=1\nWATCHDOG=1")
        for _ in range(4):
            time.sleep(1)
            channel.send(b"WATCHDOG=1")
            print("service watchdog fed", flush=True)
        print("intentionally withholding service watchdog notification", flush=True)
        time.sleep(40)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.worker:
        worker()
        return 1
    if os.geteuid() or args.out is None:
        parser.error("root and --out required")
    args.out.mkdir(parents=True, exist_ok=False)
    unit = "apollo-watchdog-demo-" + uuid.uuid4().hex + ".service"
    result = {"id": "WD03", "status": "FAIL", "unit": unit,
              "scope": "systemd service watchdog only; no hardware reset"}
    owned = False
    attempted = False
    def command(*argv):
        value = subprocess.run(argv, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, timeout=30)
        print(value.stdout, end="", flush=True)
        return value
    try:
        existing = command("systemctl", "show", unit, "--property=LoadState", "--value")
        if existing.stdout.strip() != "not-found":
            raise RuntimeError("Generated transient unit name is not demonstrably unused")
        attempted = True
        created = command("systemd-run", "--unit", unit, "--property=Type=notify",
                          "--property=NotifyAccess=main", "--property=WatchdogSec=5s",
                          "--property=TimeoutStartSec=15s", "--property=RuntimeMaxSec=45s",
                          "--property=Restart=no", "--property=LimitCORE=0",
                          "--property=WatchdogSignal=SIGTERM", sys.executable,
                          str(Path(__file__).resolve()), "--worker")
        owned = created.returncode == 0
        if not owned:
            raise RuntimeError("Transient unit creation failed")
        properties = command("systemctl", "show", unit, "--property=MainPID",
                             "--property=WatchdogUSec", "--property=RuntimeMaxUSec")
        result["properties"] = properties.stdout.strip()
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            state = command("systemctl", "show", unit, "--property=Result", "--value")
            if state.returncode == 0 and state.stdout.strip() == "watchdog":
                result.update(status="PASS", service_result="watchdog")
                break
            time.sleep(1)
        journal = command("journalctl", "--no-pager", "-u", unit)
        (args.out / "journal.log").write_text(journal.stdout)
    except Exception as error:
        result["error"] = str(error)
    finally:
        if attempted:
            try:
                cleanup = command("systemctl", "stop", unit)
                reset = command("systemctl", "reset-failed", unit)
                absent = command("systemctl", "show", unit, "--property=LoadState", "--value")
                result["cleanup_status"] = "PASS" if (
                    cleanup.returncode == reset.returncode == 0 or absent.stdout.strip() == "not-found") else "FAIL"
            except Exception as error:
                result.update(cleanup_status="FAIL", cleanup_error=str(error))
            if result["cleanup_status"] != "PASS":
                result["status"] = "FAIL"
        (args.out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result), flush=True)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
