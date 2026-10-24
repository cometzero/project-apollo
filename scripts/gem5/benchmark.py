# SPDX-License-Identifier: BSD-3-Clause
"""Summarize the AP-only Linux benchmark using simulated ROI ticks."""

import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] /
                       "hsoc-stack/tools/gem5/scripts/zena_cmn"))
from summarize_roi import stats_blocks, summarize as summarize_cmn
from analyze_roofline import cache_metrics, cache_paths


def summarize_multicore(outdir, serial_log, *, workers, size_bytes, passes, channels, mode="read"):
    """Validate pinned memory work; size_bytes is the size of each array."""
    if mode not in ("read", "copy", "triad"):
        raise ValueError("unsupported memory mode")
    arrays = {"read": 1, "copy": 2, "triad": 3}[mode]
    outdir = Path(outdir)
    events = json.loads((outdir / "roi-events.json").read_text())
    if [event["phase"] for event in events] != ["warmup", "roi_begin", "roi_end"]:
        raise ValueError("incomplete or ambiguous ROI lifecycle")
    stats_text = (outdir / "stats.txt").read_text()
    result = summarize_cmn(stats_text, Path(serial_log).read_text(errors="replace"),
                           events[1]["tick"], events[2]["tick"])
    expected = dict(benchmark="stream" if mode == "triad" else mode,
                    kernel="neon" if mode == "read" else "scalar", workers=workers, passes=passes,
                    working_set_bytes=size_bytes * arrays, useful_bytes=size_bytes * arrays * passes,
                    warmup_passes=1, initialization_before_switch=True,
                    channel_phase_spread=False, affinity="0..workers-1",
                    checksum=size_bytes * passes // 8 if mode == "read" else 0,
                    warmup_checksum=size_bytes // 8 if mode == "read" else 0)
    guest = result["guest"]
    for key, value in expected.items():
        if type(guest.get(key)) is not type(value) or guest[key] != value:
            raise ValueError(f"guest workload mismatch: {key}")
    stats = stats_blocks(stats_text)[result["roi"]["stats_block_index"]]
    instructions = {str(cpu): stats.get(f"system.roi_cpu{cpu}.commitStats0.numInsts")
                    for cpu in range(workers)}
    if any(value is None or value <= 0 for value in instructions.values()):
        raise ValueError("missing O3 committed instructions for a pinned worker")
    traffic = result["dram"]["channels"]
    if len(traffic) != channels or any((item.get("Read") or 0) <= 0 for item in traffic.values()):
        raise ValueError("missing read traffic on a configured DRAM channel")
    if mode != "read" and any((item.get("Written") or 0) <= 0 for item in traffic.values()):
        raise ValueError("missing write traffic on a configured DRAM channel")
    result["worker_committed_instructions"] = instructions
    result["memory_mode"] = mode
    result["array_bytes"] = size_bytes
    config = outdir / "config.json"
    if config.is_file():
        system = json.loads(config.read_text())["system"]
        paths = {
            "L1": [cpu["l1d"]["cache"]["path"] for cpu in system["cpu"]],
            "L2": [cpu["l2"]["cache"]["path"] for cpu in system["cpu"]],
            "L3": [rnf["dsu_l3"]["cache"]["path"] for rnf in system["ruby"]["rnf"]],
            "SLC_proxy": [home["cntrl"]["cache"]["path"] for home in system["ruby"]["hnf"]],
        }
        result["cache_counters"] = cache_metrics(stats, paths)
        result["cache_counter_scope"] = "all configured cores, DSUs and Home nodes, including OS traffic"
    (outdir / "roi-summary.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    # Full native counter sets remain in roi-summary.json for bottleneck analysis.
    return {key: value for key, value in result.items() if key != "counters"}


def summarize(outdir, serial_log, *, mode, size_bytes, passes):
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
    if result["host"] is not False or result["checksum"] != result["expected"]:
        raise ValueError("host execution or incorrect checksum is not a gem5 ROI")
    if mode not in ("cache", "dram"):
        raise ValueError("unsupported benchmark mode")
    loads = size_bytes // 64 * passes if mode == "cache" else 0
    checksum = passes if mode == "cache" else size_bytes // 8 * passes
    expected = dict(mode=mode, working_set_bytes=size_bytes, passes=passes,
                    warmup_passes=1, dependent_loads=loads,
                    useful_bytes=loads * 8 if mode == "cache" else size_bytes * passes,
                    checksum=checksum, expected=checksum)
    for key, value in expected.items():
        if type(result.get(key)) is not type(value) or result[key] != value:
            raise ValueError(f"guest workload mismatch: {key}")
    events = json.loads((outdir / "roi-events.json").read_text())
    if [event["phase"] for event in events] != [
        "warmup", "roi_begin", "roi_end"
    ]:
        raise ValueError("incomplete or ambiguous ROI lifecycle")
    begin, end = events[1]["tick"], events[2]["tick"]
    if type(begin) is not int or type(end) is not int or begin < 0 or end <= begin:
        raise ValueError("ROI end must follow a nonnegative integer begin tick")
    ticks = end - begin
    blocks = stats_blocks((outdir / "stats.txt").read_text())
    candidates = [(index, block) for index, block in enumerate(blocks)
                  if block.get("finalTick") == end and block.get("simTicks") == ticks]
    if len(candidates) != 1:
        raise ValueError("require exactly one stats dump matching the ROI begin/end")
    index, stats = candidates[0]
    frequency = stats.get("simFreq")
    if type(frequency) not in (int, float) or not 0 < frequency < float("inf"):
        raise ValueError("invalid simFreq")
    seconds = ticks / frequency
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("invalid simulated duration")
    result.update(
        evidence="uncalibrated-gem5-linux-roi",
        roi_ticks=ticks,
        roi_seconds=seconds,
        stats_block_index=index,
        useful_GB_per_second=result["useful_bytes"] / seconds / 1e9,
    )
    if result["dependent_loads"]:
        result["ns_per_dependent_load"] = (
            seconds * 1e9 / result["dependent_loads"]
        )
    config = outdir / "config.json"
    if config.is_file():
        result["cache_counters"] = cache_metrics(
            stats, cache_paths(json.loads(config.read_text())))
    reads = [value for key, value in stats.items()
             if key.endswith(".dramBytesRead")]
    result["dram_read_bytes"] = (
        sum(reads) if reads and all(value is not None for value in reads)
        else None
    )
    return result
