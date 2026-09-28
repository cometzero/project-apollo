#!/usr/bin/env python3
"""Guest-only SBSA watchdog diagnostics; inspection never opens the device."""
import argparse
import array
import fcntl
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import time


SETOPTIONS = 0x80045704
KEEPALIVE = 0x80045705
SETTIMEOUT = 0xC0045706
GETTIMEOUT = 0x80045707
GETTIMELEFT = 0x8004570A
SYSFS = Path("/sys/class/watchdog/watchdog0")


def ioctl_int(fd, request, value=0):
    data = array.array("i", [value])
    fcntl.ioctl(fd, request, data, True)
    return data[0]


def snapshot(root=SYSFS):
    result = {}
    for name in ("identity", "state", "status", "bootstatus", "timeout",
                 "nowayout", "min_timeout", "max_timeout"):
        try:
            result[name] = (root / name).read_text().strip()
        except OSError as exc:
            result[name] = {"unavailable": str(exc)}
    # A stopped SBSA timer has no meaningful deadline. Its driver can subtract
    # the running counter from a stale WCV and report an unsigned underflow.
    # Avoid even reading timeleft unless the watchdog is known to be active.
    if result["state"] == "active":
        try:
            result["timeleft"] = (root / "timeleft").read_text().strip()
        except OSError as exc:
            result["timeleft"] = {"unavailable": str(exc), "valid": False}
    else:
        result["timeleft"] = {
            "valid": False,
            "reason": "countdown unavailable unless watchdog state is active",
        }
    return result


def systemd_policy():
    """Query PID 1 policy without opening or changing any watchdog device."""
    properties = ("RuntimeWatchdogUSec", "RebootWatchdogUSec")
    output = subprocess.check_output(
        ["systemctl", "show", *("--property=" + key for key in properties)],
        text=True, timeout=5)
    values = dict(line.split("=", 1) for line in output.splitlines() if "=" in line)
    if any(not values.get(key) for key in properties):
        raise RuntimeError("systemd watchdog policy response is incomplete")
    return {key: values[key] for key in properties}


def owners(device, proc=Path("/proc")):
    """Match device numbers, not path spelling (/dev/watchdog is an alias)."""
    target = os.stat(device)
    if not stat.S_ISCHR(target.st_mode):
        raise RuntimeError("watchdog must be a character device")
    numbers = {target.st_rdev}
    # The legacy misc-device alias can have a different device number.
    try:
        numbers.add(os.stat("/dev/watchdog").st_rdev)
    except FileNotFoundError:
        pass
    found = []
    for process in proc.iterdir():
        if not process.name.isdigit():
            continue
        try:
            for entry in (process / "fd").iterdir():
                try:
                    item = entry.stat()
                    if stat.S_ISCHR(item.st_mode) and item.st_rdev in numbers:
                        found.append({"pid": int(process.name), "fd": entry.name})
                except FileNotFoundError:
                    continue
        except FileNotFoundError:
            continue
    return found


def preflight(device, timeout):
    if os.geteuid() != 0:
        raise RuntimeError("active tests require root")
    current = snapshot()
    if current["identity"] != "SBSA Generic Watchdog":
        raise RuntimeError("only SBSA Generic Watchdog is supported")
    if current["nowayout"] != "0" or current["state"] != "inactive":
        raise RuntimeError("watchdog must be inactive and stoppable (nowayout=0)")
    maximum = current["max_timeout"]
    if isinstance(maximum, str) and int(maximum) and timeout > int(maximum):
        raise RuntimeError("timeout exceeds driver maximum")
    cmdline = Path("/proc/cmdline").read_text().split()
    if any(arg.replace("-", "_").startswith("sbsa_gwdt.action=")
           and arg.replace("-", "_") != "sbsa_gwdt.action=0"
           for arg in cmdline):
        raise RuntimeError("action=1 panic mode is not supported")
    runtime = subprocess.check_output(
        ["systemctl", "show", "--property=RuntimeWatchdogUSec", "--value"],
        text=True, timeout=5).strip()
    if runtime not in ("0", "0us", "0s"):
        raise RuntimeError("systemd RuntimeWatchdog must be disabled")
    active = owners(device)
    if active:
        raise RuntimeError("watchdog already owned: " + json.dumps(active))
    return current


class Recorder:
    def __init__(self, output):
        self.path = Path(output)
        self.path.mkdir(parents=True, exist_ok=False)
        self.log = (self.path / "events.jsonl").open("x", buffering=1)

    def emit(self, event, **fields):
        item = dict(event=event, pid=os.getpid(), monotonic_s=time.monotonic(),
                    realtime_ns=time.time_ns(), **fields)
        line = json.dumps(item, sort_keys=True)
        print(line, flush=True)
        self.log.write(line + "\n")
        self.log.flush()
        os.fsync(self.log.fileno())

    def finish(self, result):
        (self.path / "result.json").write_text(json.dumps(result, indent=2) + "\n")
        self.log.close()


def run_active(args, record):
    before = preflight(args.device, args.timeout)
    record.emit("preflight", snapshot=before)
    # The kernel's exclusive open closes the race after the read-only checks.
    fd = os.open(args.device, os.O_WRONLY | os.O_CLOEXEC)
    result = {"status": "FAIL", "mode": args.command}
    try:
        actual = ioctl_int(fd, SETTIMEOUT, args.timeout)
        queried = ioctl_int(fd, GETTIMEOUT)
        if actual != args.timeout or queried != actual:
            raise RuntimeError("driver timeout differs from requested timeout")
        ioctl_int(fd, KEEPALIVE)
        start = time.monotonic()
        record.emit("ready", timeout_s=actual, ws0_expected_after_s=actual / 2,
                    ws1_expected_after_s=actual, action=0,
                    device=args.device, fd_held_open=True)
        if args.command == "keepalive":
            deadline = start + args.duration
            while time.monotonic() < deadline:
                time.sleep(min(actual / 4, max(0, deadline - time.monotonic())))
                before_ping = ioctl_int(fd, GETTIMELEFT)
                if not 0 <= before_ping <= actual:
                    raise RuntimeError("GETTIMELEFT before feeding is outside timeout range: " + str(before_ping))
                ioctl_int(fd, KEEPALIVE)
                after_ping = ioctl_int(fd, GETTIMELEFT)
                if not 0 <= after_ping <= actual:
                    raise RuntimeError("GETTIMELEFT after feeding is outside timeout range: " + str(after_ping))
                record.emit("keepalive", before_ping_timeleft_s=before_ping,
                            timeleft_s=after_ping)
            result["status"] = "PASS"
            result["scope"] = "ioctl keepalive and survival only, not reset qualification"
        else:
            # Never close the descriptor to cause expiry: watchdog core can
            # keep pinging after an unexpected close. Hold it without writes.
            deadline = start + actual + args.grace
            ws0_reported = False
            while time.monotonic() < deadline:
                elapsed = time.monotonic() - start
                if elapsed >= actual / 2 and not ws0_reported:
                    record.emit("ws0-expected", elapsed_s=elapsed,
                                observed=False, fd_held_open=True)
                    ws0_reported = True
                time.sleep(min(0.25, max(0, deadline - time.monotonic())))
            result["status"] = "NOT_OBSERVED"
            result["reason"] = "process survived deadline; host must verify WS1/reset evidence"
            record.emit("expiry-deadline", **result)
    finally:
        try:
            ioctl_int(fd, SETOPTIONS, 1)  # WDIOS_DISABLECARD
            record.emit("disabled")
        except OSError as exc:
            record.emit("disable-error", error=str(exc))
            # Magic close is supported by sbsa_gwdt; do not silently claim stop.
            os.write(fd, b"V")
        finally:
            os.close(fd)
        after = snapshot()
        record.emit("after", snapshot=after)
        if after.get("state") != "inactive":
            result["status"] = "FAIL"
            result["reason"] = "watchdog stop not confirmed"
    return result


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("command", nargs="?", default="inspect",
                     choices=("inspect", "keepalive", "expiry"))
    cli.add_argument("--device", default="/dev/watchdog0", choices=("/dev/watchdog0",))
    cli.add_argument("--output", default="watchdog-" + time.strftime("%Y%m%d-%H%M%S"))
    cli.add_argument("--timeout", type=int, default=20, help="whole WS1 timeout in seconds")
    cli.add_argument("--duration", type=float, default=30)
    cli.add_argument("--grace", type=float, default=5)
    cli.add_argument("--acknowledge-reset", action="store_true")
    return cli


def main(argv=None):
    cli = parser()
    args = cli.parse_args(argv)
    if not 4 <= args.timeout <= 60 or not 1 <= args.duration <= 300 or not 1 <= args.grace <= 60:
        cli.error("timeout must be 4..60s, duration 1..300s, grace 1..60s")
    if args.command == "expiry" and not args.acknowledge_reset:
        cli.error("expiry may reset the guest: --acknowledge-reset required")
    record = Recorder(args.output)
    result = {"status": "FAIL", "mode": args.command}

    def interrupted(signum, frame):
        raise InterruptedError("signal " + str(signum))

    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    try:
        if args.command == "inspect":
            result = {"status": "INSPECTED", "snapshot": snapshot(),
                      "systemd_policy": systemd_policy(), "device_opened": False}
            record.emit("inspect", **result)
        else:
            result = run_active(args, record)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        result = {"status": "FAIL", "error": str(exc), "mode": args.command}
        record.emit("error", **result)
    finally:
        record.finish(result)
    return 0 if result["status"] in ("PASS", "INSPECTED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
