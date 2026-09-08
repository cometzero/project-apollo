#!/usr/bin/env python3
"""Verify Monitor faults and Linux recovery on an already booted QVP BSP."""

import argparse
import json
from pathlib import Path
import subprocess
import time

from qbox_runtime_injection_support import (
    ApiClient, HttpRequest, capture_log_offsets, post_action_failures,
)


POLICY = "/sys/devices/system/cpu/cpufreq/policy0/"
EEPROM = "od -An -tx1 -N1 /sys/bus/i2c/devices/5-0050/eeprom"


class Verification:
    def __init__(self, args):
        self.args = args
        self.client = ApiClient(args.monitor)
        self.records = []
        self.active = set()

    def api(self, method, path, payload=None, expected=200):
        reply = self.client.request(HttpRequest(method, path, payload, 10))
        self.records.append(dict(method=method, path=path, payload=payload,
                                 http_status=reply.status, response=reply.body))
        assert reply.status == expected, reply
        return reply.body

    def guest(self, command, timeout=30, check=True):
        if check:
            command = "set -e; " + command
        result = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=3",
             "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
             "-p", str(self.args.ssh_port), "root@127.0.0.1", command],
            text=True, capture_output=True, timeout=timeout,
        )
        self.records.append(dict(guest_command=command, returncode=result.returncode,
                                 stdout=result.stdout, stderr=result.stderr))
        if check:
            assert result.returncode == 0, result.stderr
        return result

    def submit(self, target, action, **fields):
        result = self.api("POST", "/api/v1/injections",
                          dict(schema_version=1, target=target, action=action, **fields), 202)
        if result["state"] not in ("completed", "cancelled", "failed"):
            self.active.add(result["id"])
        return result

    def wait_state(self, request, expected):
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            result = self.api("GET", f"/api/v1/injections/{request['id']}")
            if result["state"] == expected:
                if expected in ("completed", "cancelled", "failed"):
                    self.active.discard(request["id"])
                return result
            assert result["state"] not in ("failed", "cancelled", "completed"), result
            time.sleep(0.1)
        raise AssertionError(f"request did not reach {expected}: {result}")

    def signal(self):
        self.guest(EEPROM)
        fault = self.submit("apollo.irq.i2c5", "force-low")
        self.wait_state(fault, "active")
        failed = self.guest(EEPROM, check=False)
        assert failed.returncode != 0 and failed.returncode != 255, failed
        self.api("DELETE", f"/api/v1/injections/{fault['id']}")
        self.active.discard(fault["id"])
        self.guest(EEPROM)

    def hipc(self):
        self.guest("ip link set ethsi1 up; "
                   "ip link show ethsi1.200 >/dev/null 2>&1 || "
                   "ip link add link ethsi1 name ethsi1.200 type vlan id 200; "
                   "ip addr replace 192.168.1.2/24 dev ethsi1.200; "
                   "ip link set ethsi1.200 up; ping -c 2 -W 2 192.168.1.1")

    def reset(self, drop=False):
        markers = {
            "qbox-rse.log": "SCMI Comms subscribed to power state notifications",
            "qbox-safety-island-cl0.log": "[FWK] Module initialization complete!",
            # Zephyr reboot plus the HIPC ping below proves the selected service.
            "qbox-safety-island-cl1.log": "*** Booting Zephyr OS build",
        }
        offsets = capture_log_offsets(self.args.runtime_dir)
        old_boot = self.guest("cat /proc/sys/kernel/random/boot_id").stdout.strip()
        self.guest(f"echo performance > {POLICY}scaling_governor; "
                   f"echo 2500000 > {POLICY}scaling_max_freq")
        pending = self.submit("apollo.gpio.rse0.pin0", "read",
                              trigger=dict(type="relative-simulation-time", delay_ns=300_000_000_000))
        if drop:
            self.hipc()
            fault = self.submit("platform.host_ap_si_cl1_mhu_pbx", "drop-next-doorbell",
                                parameters=dict(channel=0))
            self.wait_state(fault, "active")
            failed = self.guest("ping -c 1 -W 2 192.168.1.1", check=False)
            assert failed.returncode == 1, failed
            self.wait_state(fault, "completed")
        reset = self.submit("apollo.control.system-reset", "pulse",
                            parameters=dict(duration_ns=1000))
        self.wait_state(reset, "completed")
        cancelled = self.wait_state(pending, "cancelled")
        assert cancelled["result"] in ("cancelled-by-reset", "stale-generation"), cancelled
        deadline = time.monotonic() + self.args.boot_timeout
        while time.monotonic() < deadline:
            try:
                result = self.guest("cat /proc/sys/kernel/random/boot_id", check=False)
                if result.returncode == 0 and result.stdout.strip() != old_boot:
                    break
            except subprocess.TimeoutExpired:
                pass
            time.sleep(2)
        else:
            raise AssertionError("guest did not return with a new boot ID")
        self.guest(f"test \"$(cat {POLICY}scaling_driver)\" = scmi; "
                   f"echo performance > {POLICY}scaling_governor; "
                   f"echo 2000000 > {POLICY}scaling_max_freq")
        for _ in range(30):
            frequency = self.guest(f"cat {POLICY}cpuinfo_cur_freq").stdout.strip()
            if frequency == "2000000":
                break
            time.sleep(0.2)
        else:
            raise AssertionError(f"SCMI frequency did not recover: {frequency}")
        self.guest(EEPROM)
        if drop:
            self.hipc()
        fresh = self.submit("apollo.gpio.rse0.pin0", "read")
        assert fresh["generation"] > pending["generation"], fresh
        for name, marker in markers.items():
            with (self.args.runtime_dir / name).open("rb") as stream:
                stream.seek(offsets[name])
                appended = stream.read().decode(errors="replace")
            assert marker in appended, f"missing fresh {name} marker: {marker}"
            self.records.append(dict(reboot_log=name, marker=marker, passed=True))
        self.api("POST", "/api/v1/injections",
                 dict(schema_version=1, target="apollo.gpio.rse0.pin0", action="read",
                      expected_generation=pending["generation"]), 409)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--monitor", default="http://127.0.0.1:18080")
    parser.add_argument("--ssh-port", type=int, default=8022)
    parser.add_argument("--boot-timeout", type=int, default=600)
    parser.add_argument("--scenario", choices=("signal", "doorbell", "reset", "all"), default="all")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    check = Verification(args)
    result = dict(passed=False, scenarios=[], records=check.records)
    offsets = capture_log_offsets(args.runtime_dir)
    try:
        check.api("GET", "/api/v1/injection-capabilities")
        if args.scenario in ("signal", "all"):
            check.signal()
            result["scenarios"].append("i2c-irq-force-clear-recovery")
        if args.scenario in ("doorbell", "all"):
            check.reset(drop=True)
            result["scenarios"].append("hipc-doorbell-drop-reset-recovery")
        if args.scenario == "reset":
            check.reset()
            result["scenarios"].append("system-reset-generation-recovery")
        result["post_action_failures"] = post_action_failures(args.runtime_dir, offsets)
        assert not result["post_action_failures"], result["post_action_failures"]
        result["passed"] = True
    except Exception as error:
        result["error"] = str(error)
    finally:
        for request_id in sorted(check.active):
            try:
                check.api("DELETE", f"/api/v1/injections/{request_id}")
            except Exception as error:
                result.setdefault("cleanup_errors", []).append(str(error))
        (args.out_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "records"}))
    return 0 if result["passed"] and not result.get("cleanup_errors") else 1


if __name__ == "__main__":
    raise SystemExit(main())
