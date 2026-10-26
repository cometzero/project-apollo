#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Report validated Dhrystone loop ROI scores from fixed-clock Apollo O3 runs."""

import argparse
import json
import math
from pathlib import Path
import re

from benchmark import roi_statistics


def positive(value, name, integer=False):
    if (type(value) not in (int, float) or not math.isfinite(value)
            or value <= 0 or (integer and value != int(value))):
        raise ValueError(f"{name} must be finite and positive" +
                         (" integer" if integer else ""))
    return value


def summarize(directory):
    directory = Path(directory)
    result = json.loads((directory / "result.json").read_text())
    if (result.get("status") != "PASS" or result.get("workload") != "command"
            or type(result.get("returncode")) is not int
            or result["returncode"] != 0 or result.get("timeout") is not False):
        raise ValueError("launcher command did not complete successfully")
    output = directory / "m5out"
    serial = (output / "system.platform.terminal").read_text(errors="replace")
    markers = re.findall(r"^DHRY_GEM5_RESULT[^\r\n]*", serial, re.M)
    match = re.fullmatch(
        r"DHRY_GEM5_RESULT status=PASS runs=([0-9]+) warmup=([0-9]+) cpu=0 scope=loop",
        markers[0]) if len(markers) == 1 else None
    exits = re.findall(r"^APOLLO_WORKLOAD_EXIT=([^\r\n]*)", serial, re.M)
    if (match is None or exits != ["0"] or "GEM5_CONTROL_RUN" in serial
            or re.search(r"status=FAIL|Kernel panic|Segmentation fault", serial)):
        raise ValueError("require one validated CPU0 loop result and successful guest exit")
    runs, warmup = map(int, match.groups())
    for name, value in (("runs", runs), ("warmup", warmup)):
        positive(value, name, integer=True)
        if value > 10000000:
            raise ValueError(f"{name} exceeds supported executable limit")
    events = json.loads((output / "roi-events.json").read_text())
    if (not isinstance(events, list) or len(events) != 3
            or any(not isinstance(event, dict) for event in events)
            or [event.get("phase") for event in events] !=
            ["warmup", "roi_begin", "roi_end"]):
        raise ValueError("require exactly one switch/warmup, begin, end lifecycle")
    ticks = [event.get("tick") for event in events]
    if (any(type(tick) is not int or tick < 0 for tick in ticks)
            or not ticks[0] < ticks[1] < ticks[2]):
        raise ValueError("ROI ticks must be strictly increasing nonnegative integers")
    if (output / "online-activity.jsonl").exists():
        raise ValueError("online clock changes are not supported by this collector")
    stats, indices, _ = roi_statistics(output, ticks[1], ticks[2])
    sim_frequency = positive(stats["simFreq"], "simFreq", integer=True)
    config = json.loads((output / "config.json").read_text())
    cpus = config["system"]["roi_cpu"]
    cpu0 = [cpu for cpu in cpus if cpu.get("cpu_id") == 0]
    if (len(cpu0) != 1 or cpu0[0].get("type") != "BaseO3CPU"
            or cpu0[0].get("path") != "system.roi_cpu0"):
        raise ValueError("require Apollo CPU0 BaseO3CPU ROI configuration")
    clock_ref = cpu0[0]["clk_domain"]
    domain = config
    for component in clock_ref.split("."):
        domain = domain[component]
    if (domain.get("path") != clock_ref or domain.get("type") != "SrcClockDomain"
            or not isinstance(domain.get("clock"), list) or len(domain["clock"]) != 1):
        raise ValueError("require an actual single-frequency source clock domain")
    period = positive(domain["clock"][0], "CPU clock period", integer=True)
    cycles = positive(stats["system.roi_cpu0.numCycles"], "CPU0 cycles", integer=True)
    instructions = positive(stats["system.roi_cpu0.thread_0.numInsts"],
                            "CPU0 committed instructions", integer=True)
    seconds = positive((ticks[2] - ticks[1]) / sim_frequency, "ROI seconds")
    cpu_hz = positive(sim_frequency / period, "CPU frequency")
    rate = positive(runs / seconds, "Dhrystones per second")
    host_cost = {name: positive(stats[name], name) for name in
                 ("hostSeconds", "hostInstRate") if name in stats}
    return dict(
        status="PASS", tool="dhry-gem5", evidence="UNCALIBRATED_AP_MODEL",
        scope="loop", runs=runs, warmup_runs=warmup, cpu=0,
        roi_begin_tick=ticks[1], roi_end_tick=ticks[2],
        switch_tick=ticks[0], warmup_ticks=ticks[1] - ticks[0],
        roi_ticks=ticks[2] - ticks[1], stats_block_indices=indices,
        host_simulation_cost=host_cost,
        simulated_seconds=seconds, sim_frequency_hz=sim_frequency,
        cpu_clock_domain=clock_ref, cpu_clock_period_ticks=period,
        cpu_frequency_hz=cpu_hz, cpu_cycles=cycles,
        committed_instructions=instructions, cycles_per_iteration=cycles / runs,
        ipc=instructions / cycles, dhrystones_per_second=rate,
        dmips=rate / 1757, dmips_per_mhz=rate / 1757 / (cpu_hz / 1e6),
        limitations=["Modified loop ROI; not the original guest CPU-time score",
                     "Includes ROI instrumentation and any in-ROI interrupts",
                     "Single run; no variance or hardware calibration claim"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    args = parser.parse_args()
    try:
        result = summarize(args.run_directory)
    except (ValueError, KeyError, OSError, TypeError, AttributeError) as error:
        parser.exit(1, f"Invalid Dhrystone evidence: {error}\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
