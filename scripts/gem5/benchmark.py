# SPDX-License-Identifier: BSD-3-Clause
"""Build and summarize the AP-only Linux benchmark using simulated ROI ticks."""

import json
import math
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] /
                       "hsoc-stack/tools/gem5/scripts/zena_cmn"))
from summarize_roi import stats_blocks
from analyze_roofline import cache_metrics, cache_paths


def build_benchmark(gem5_source, output, compiler="aarch64-linux-gnu-gcc"):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [compiler, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
         "-static", "-pthread", "-march=armv8-a", "-mno-outline-atomics",
         "-I", str(Path(gem5_source) / "workloads/zena_cmn"),
         str(Path(__file__).with_suffix(".c")), "-o", str(output)],
        check=True,
    )
    return output


def summarize(outdir, serial_log):
    """Reject incomplete runs; throughput is useful bytes, not bus traffic."""
    outdir = Path(outdir)
    results = [
        json.loads(line.split("APOLLO_BENCH_RESULT ", 1)[1])
        for line in Path(serial_log).read_text(errors="replace").splitlines()
        if "APOLLO_BENCH_RESULT " in line
    ]
    if len(results) != 1 or results[0]["result"] != "PASS":
        raise ValueError("one successful guest benchmark result is required")
    result = results[0]
    for key in ("working_set_bytes", "passes", "useful_bytes", "dependent_loads",
                "checksum", "expected"):
        if type(result[key]) is not int or result[key] < 0:
            raise ValueError(f"invalid guest benchmark field: {key}")
    if result["host"] or result["checksum"] != result["expected"]:
        raise ValueError("host execution or incorrect checksum is not a gem5 ROI")
    events = json.loads((outdir / "roi-events.json").read_text())
    if [event["phase"] for event in events] != [
        "warmup", "roi_begin", "roi_end"
    ]:
        raise ValueError("incomplete or ambiguous ROI lifecycle")
    ticks = events[2]["tick"] - events[1]["tick"]
    blocks = stats_blocks((outdir / "stats.txt").read_text())
    # gem5 dumps at workend, then optionally once more at simulator exit.
    if len(blocks) not in (1, 2):
        raise ValueError("expected a complete ROI dump and optional exit dump")
    for index, stats in enumerate(blocks):
        if not {"simFreq", "simTicks", "finalTick"}.issubset(stats):
            raise ValueError("missing ROI timing statistics")
        if (stats["finalTick"] - stats["simTicks"] != events[1]["tick"] or
                stats["finalTick"] < events[2]["tick"]):
            raise ValueError("statistics do not belong to the recorded ROI")
        if index == 0 and stats["finalTick"] != events[2]["tick"]:
            raise ValueError("first statistics dump is not the ROI end")
    frequencies = {stats["simFreq"] for stats in blocks}
    if ticks <= 0 or len(frequencies) != 1:
        raise ValueError("positive ROI ticks and one simFreq are required")
    frequency = frequencies.pop()
    if not isinstance(frequency, (int, float)) or not 0 < frequency < float("inf"):
        raise ValueError("invalid simFreq")
    seconds = ticks / frequency
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("invalid simulated duration")
    result.update(
        evidence="uncalibrated-gem5-linux-roi",
        roi_ticks=ticks,
        roi_seconds=seconds,
        useful_GB_per_second=result["useful_bytes"] / seconds / 1e9,
    )
    if result["dependent_loads"]:
        result["ns_per_dependent_load"] = (
            seconds * 1e9 / result["dependent_loads"]
        )
    config = outdir / "config.json"
    if config.is_file():
        result["cache_counters"] = cache_metrics(
            blocks[0], cache_paths(json.loads(config.read_text())))
    reads = [value for key, value in blocks[0].items()
             if key.endswith(".dramBytesRead")]
    result["dram_read_bytes"] = (
        sum(reads) if reads and all(value is not None for value in reads)
        else None
    )
    return result
