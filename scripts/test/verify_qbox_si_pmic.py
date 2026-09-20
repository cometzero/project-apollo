#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify single-PMIC minimal SCP probe and Linux ownership from captured logs.

Run verify_qbox_si_pmic_guest.sh and verify_qbox_i2c_multi_slave.sh in Linux,
then pass their separate output logs and the complete SI CL0 UART boot log.
elapsed_us is SCP timer time, not host wall time. Use --max-elapsed-us only
with a declared simulated-time budget; this tool does not infer host speed.
PASS covers the identity probe and ownership only. Rail configuration and
GPIO tests must explicitly report SKIP under the default-preservation policy.
"""
import argparse
import json
from pathlib import Path
import re


ADDRESSES = {"0x48"}
CLIENTS = {"0-0050", "0-0051", "0-0052"}


def fields(text):
    return dict(re.findall(r"([a-z_]+)=([^\s|]+)", text))


def records(text, prefix):
    return [fields(line.split(prefix, 1)[1]) for line in text.splitlines()
            if prefix in line]


def qualify(scp, guest, eeprom, max_elapsed_us=None):
    errors = []

    def require(condition, reason):
        if not condition:
            errors.append(reason)

    lines = scp.splitlines()
    begins = [i for i, line in enumerate(lines) if "[TPS6594] begin " in line]
    completes = [i for i, line in enumerate(lines) if "[TPS6594] complete " in line]
    power = [i for i, line in enumerate(lines) if "[TPS6594] power-ready" in line]
    ready = [(i, fields(line)) for i, line in enumerate(lines)
             if "[TPS6594] ready " in line]
    checks = [(i, fields(line)) for i, line in enumerate(lines)
              if "[TPS6594] check " in line]
    require(len(begins) == len(completes) == len(power) == 1,
            "require one begin, complete, and power-ready marker from one boot")
    require(not any("[TPS6594] failed" in line for line in lines),
            "SCP PMIC initialization failed")
    require(len(ready) == 1 and {r.get("address") for _, r in ready} == ADDRESSES,
            "require exactly one PMIC ready record at 0x48")
    require(len(checks) == 1 and {r.get("address") for _, r in checks} == ADDRESSES,
            "require exactly one PMIC check record at 0x48")
    for _, record in ready:
        expected = {"rails": "9", "gpio": "11", "policy": "preserve",
                    "rtc": "untouched"}
        require(all(record.get(k) == v for k, v in expected.items()),
                f"incomplete PMIC inventory evidence: {record.get('address')}")
        require("faults" not in record,
                "minimal probe must not claim fault mask initialization")
    for check_line, record in checks:
        expected = {"probe": "PASS", "rail_config": "SKIP", "gpio_test": "SKIP"}
        require(all(record.get(k) == v for k, v in expected.items()),
                f"incomplete PMIC minimal probe evidence: {record.get('address')}")
        require(not {"gpio_loopback", "rail_readback", "mask_readback"} & record.keys(),
                "minimal probe must not claim full initialization checks")
        matching = [i for i, r in ready if r.get("address") == record.get("address")]
        require(len(matching) == 1 and matching[0] < check_line
                and not any(matching[0] < i < check_line for i, _ in ready),
                f"PMIC check must follow its ready record: {record.get('address')}")
    elapsed_us = None
    if len(begins) == len(completes) == len(power) == 1:
        require(begins[0] < completes[0] < power[0],
                "PMIC completion must precede power initialization gate")
        require(all(begins[0] < i < completes[0] for i, _ in ready),
                "PMIC ready records outside initialization window")
        require(all(begins[0] < i < completes[0] for i, _ in checks),
                "PMIC check records outside initialization window")
        require(fields(lines[begins[0]]).get("count") == "1",
                "incorrect PMIC begin count")
        complete = fields(lines[completes[0]])
        require(complete.get("count") == "1", "incorrect PMIC complete count")
        try:
            elapsed_us = int(complete["elapsed_us"])
            require(elapsed_us > 0, "invalid SCP elapsed time")
            if max_elapsed_us is not None:
                require(elapsed_us <= max_elapsed_us, "SCP elapsed budget exceeded")
        except (KeyError, ValueError):
            errors.append("missing or invalid SCP elapsed_us")

    guest_records = records(guest, "APOLLO_SI_PMIC_GUEST|")
    require(not any(r.get("status") == "FAIL" for r in guest_records),
            "Linux ownership check failed")
    ownership = [r for r in guest_records if r.get("event") == "ownership"]
    require(len(ownership) == 1 and all(ownership[0].get(k) == v for k, v in
            {"pmics": "0", "regulators": "0", "children": "0", "status": "PASS"}.items()),
            "Linux PMIC ownership absence not verified")
    require(any(r.get("event") == "rtc" and r.get("driver") == "rtc-pl031"
                and r.get("status") == "PASS" and r.get("count", "0").isdigit()
                and int(r["count"]) >= 1 for r in guest_records),
            "Linux PL031 RTC not verified")
    inventories = [r for r in guest_records if r.get("event") == "eeprom"]
    require(len(inventories) == 3 and {r.get("client") for r in inventories} == CLIENTS
            and all(r.get("status") == "PASS" and r.get("driver") == "at24"
                    for r in inventories), "AP EEPROM inventory not verified")
    finals = [r for r in guest_records if r.get("event") == "final"]
    require(len(finals) == 1 and finals[0].get("status") == "PASS",
            "Linux ownership script did not complete")

    traffic = records(eeprom, "APOLLO_I2C_MULTI_SLAVE|")
    require(not any(r.get("status") == "FAIL" or r.get("event") in
                    {"fail", "worker-fail"} for r in traffic), "EEPROM traffic failed")
    final = [r for r in traffic if r.get("event") == "final"]
    require(len(final) == 1 and all(final[0].get(k) == v for k, v in
            {"status": "PASS", "clients": "3", "rounds": "8", "bytes": "256"}.items()),
            "concurrent EEPROM traffic did not complete")
    restored = [r for r in traffic if r.get("event") == "restore"]
    require(len(restored) == 3 and {r.get("client") for r in restored} == CLIENTS
            and all(r.get("status") == "PASS" for r in restored),
            "EEPROM original data restoration not verified")
    return {"status": "FAIL" if errors else "PASS", "errors": errors,
            "scp_elapsed_us": elapsed_us, "scp_elapsed_clock": "firmware timer",
            "host_elapsed_seconds": None,
            "rail_configuration": "SKIP", "gpio_test": "SKIP",
            "scope": "single PMIC presence probe and ownership; default registers preserved; "
                     "rail/GPIO functionality and runtime PMIC IRQ delivery unqualified"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scp-log", type=Path, required=True)
    parser.add_argument("--guest-log", type=Path, required=True)
    parser.add_argument("--eeprom-log", type=Path, required=True)
    parser.add_argument("--max-elapsed-us", type=int)
    args = parser.parse_args()
    result = qualify(args.scp_log.read_text(errors="replace"),
                     args.guest_log.read_text(errors="replace"),
                     args.eeprom_log.read_text(errors="replace"), args.max_elapsed_us)
    print(json.dumps(result, indent=2))
    return result["status"] != "PASS"


if __name__ == "__main__":
    raise SystemExit(main())
