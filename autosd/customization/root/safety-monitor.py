#!/usr/bin/python3
"""Development health monitor; latch unhealthy ADAS until operator recovery."""
import json
import os
from pathlib import Path
import subprocess
import time

STATE = Path("/run/apollo-safety/state.json")
PROBE_TIMEOUT = float(os.environ.get("APOLLO_PROBE_TIMEOUT", "2"))


def probe():
    try:
        return subprocess.run(
            ["podman", "exec", "apollo-adas", "/workload", "health", "/run/heartbeat"],
            timeout=PROBE_TIMEOUT, check=False, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def write_state(state, failures):
    temporary = STATE.with_suffix(".tmp")
    temporary.write_text(json.dumps({"state": state, "failures": failures,
                                      "monotonic": time.monotonic()}) + "\n")
    temporary.replace(STATE)
    print(f"APOLLO_SAFETY state={state} failures={failures}", flush=True)


def main():
    # A service restart must not clear a fault latched earlier in this boot.
    if STATE.exists() and json.loads(STATE.read_text())["state"] == "FAULT_LATCHED":
        raise SystemExit("Operator must clear the fault before restarting the monitor")
    failures = 0
    write_state("STARTING", failures)
    while True:
        failures = 0 if probe() else failures + 1
        if failures >= 3:
            write_state("FAULT_LATCHED", failures)
            # Stop requests remain bounded. A failed stop is a distinct error.
            subprocess.run(["systemctl", "stop", "apollo-adas.service"],
                           timeout=60, check=True)
            return
        write_state("HEALTHY" if not failures else "DEGRADED", failures)
        time.sleep(1)


if __name__ == "__main__":
    main()
