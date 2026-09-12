#!/usr/bin/env python3
"""Require all four TF-M stages to exercise SysTick and TIMER0..3."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

STAGES = ("BL1_1", "BL1_2", "BL2", "RUNTIME")
TIMERS = ("SysTick", "TIMER0", "TIMER1", "TIMER2", "TIMER3")


def validate(text):
    records = []
    errors = []
    counts = Counter()
    for line in text.splitlines():
        if "APOLLO_TIMER_TEST " not in line:
            continue
        fields = dict(re.findall(r"(\w+)=([^\s]+)", line))
        pair = (fields.get("stage"), fields.get("timer"))
        counts[pair] += 1
        records.append(fields)
        try:
            if fields["result"] != "PASS" or pair[0] not in STAGES or pair[1] not in TIMERS:
                raise ValueError("unexpected stage/timer or non-PASS result")
            start, end, spins = (int(fields[key], 0) for key in ("start", "end", "spins"))
            if min(start, end, spins) < 0:
                raise ValueError("negative observation")
            if pair[1] == "SysTick":
                if int(fields["core_hz"], 0) != 100000000:
                    raise ValueError("unexpected SysTick CPU clock")
            elif not ((end - start) & 0xffffffff) or int(fields["freq"], 0) != 125000000 or int(fields["pending"], 0) != 1:
                raise ValueError("timestamp timer needs counter progress, 125MHz and IRQ pending")
        except (KeyError, ValueError) as error:
            errors.append(f"{pair}: {error}")
    for stage in STAGES:
        for timer in TIMERS:
            if counts[stage, timer] != 1:
                errors.append(f"{stage}/{timer}: expected one result, got {counts[stage, timer]}")
    return {"passed": not errors, "expected": 20, "observed": len(records),
            "records": records, "errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rse-log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.rse_log.read_text(errors="replace"))
    result["rse_log"] = str(args.rse_log.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("passed", "expected", "observed", "errors")}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
