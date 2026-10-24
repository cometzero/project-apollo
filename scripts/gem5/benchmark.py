# SPDX-License-Identifier: BSD-3-Clause
"""Summarize the AP-only Linux benchmark using simulated ROI ticks."""

import json
import math
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] /
                       "hsoc-stack/tools/gem5/scripts/zena_cmn"))
from summarize_roi import stats_blocks, summarize_block
from analyze_roofline import cache_metrics, cache_paths


def roi_epochs(path, begin, end):
    """Require an ordered ledger that covers the ROI once, without clipping."""
    selected, next_tick, last_epoch = [], begin, None
    for line in path.read_text().splitlines():
        epoch = json.loads(line)
        start, stop = epoch["begin_tick"], epoch["end_tick"]
        if type(start) is not int or type(stop) is not int or start < 0 or stop <= start:
            raise ValueError("invalid online epoch boundaries")
        if stop <= begin or start >= end:
            continue
        if (epoch.get("phase") != "roi_begin" or start != next_tick or stop > end
                or type(epoch.get("epoch")) is not int or epoch["epoch"] < 0
                or (last_epoch is not None and epoch["epoch"] != last_epoch + 1)):
            raise ValueError("online epochs must cover ROI without gaps or overlap")
        selected.append(epoch)
        next_tick, last_epoch = stop, epoch["epoch"]
    if next_tick != end:
        raise ValueError("online epochs do not cover the complete ROI")
    return selected


def summarize_power(outdir):
    """Report only completed ROI energy, never the runtime's warmup/exit total."""
    outdir = Path(outdir)
    events = json.loads((outdir / "roi-events.json").read_text())
    if [event["phase"] for event in events] != ["warmup", "roi_begin", "roi_end"]:
        raise ValueError("power measurement requires one complete O3 ROI")
    begin, end = events[1]["tick"], events[2]["tick"]
    stats, indices, online = roi_statistics(outdir, begin, end)
    if not online:
        raise ValueError("power measurement requires online epoch accounting")
    activity = roi_epochs(outdir / "online-activity.jsonl", begin, end)
    energy = roi_epochs(outdir / "online-energy.jsonl", begin, end)
    thermal = roi_epochs(outdir / "online-thermal.jsonl", begin, end)
    if len(activity) != len(energy) or len(activity) != len(thermal):
        raise ValueError("power ledgers disagree on epoch count")
    qualifications = ("SYNTHETIC", "UNCALIBRATED", "CALIBRATED")
    total, labels = 0.0, set()
    temperatures = None
    for active, joules, heat in zip(activity, energy, thermal):
        identity = tuple(active[key] for key in ("epoch", "begin_tick", "end_tick"))
        if any(tuple(row[key] for key in ("epoch", "begin_tick", "end_tick")) != identity
               for row in (joules, heat)):
            raise ValueError("power ledgers disagree on epoch boundaries")
        seconds = (active["end_tick"] - active["begin_tick"]) / stats["simFreq"]
        if any(type(row.get("seconds")) not in (int, float)
               or not math.isclose(row["seconds"], seconds, rel_tol=1e-12, abs_tol=0)
               for row in (active, joules, heat)):
            raise ValueError("power epoch duration does not match simulated ticks")
        if (joules.get("coverage") != "COMPLETE_LEDGER"
                or joules.get("unconfigured_actors") != []
                or joules.get("qualification") not in qualifications):
            raise ValueError("incomplete or unqualified power energy")
        actors = joules["actors"]
        names = [actor["actor"] for actor in actors]
        if (not names or len(set(names)) != len(names)
                or set(names) != {actor["actor"] for actor in active["actors"]}):
            raise ValueError("power actor coverage mismatch")
        subtotal = 0.0
        for actor in actors:
            values = [actor.get(key) for key in ("dynamic_j", "leakage_j", "total_j")]
            if any(type(value) not in (int, float) or not math.isfinite(value) or value < 0
                   for value in values):
                raise ValueError("invalid actor energy")
            if not math.isclose(values[0] + values[1], values[2], rel_tol=1e-12, abs_tol=0):
                raise ValueError("actor energy does not balance")
            subtotal += values[2]
        value = joules.get("total_j")
        if (type(value) not in (int, float) or not math.isfinite(value) or value < 0
                or not math.isclose(value, subtotal, rel_tol=1e-12, abs_tol=0)):
            raise ValueError("invalid total epoch energy")
        current = heat["temperature_c"]
        if (not current or (temperatures is not None and set(current) != set(temperatures))
                or any(type(t) not in (int, float) or not math.isfinite(t) or t <= -273.15
                       for t in current.values())):
            raise ValueError("invalid thermal epoch temperatures")
        temperatures = current
        total += value
        labels.add(joules["qualification"])
    summary = json.loads((outdir / "online-power-summary.json").read_text())
    thermal_qualification = summary.get("thermal_qualification")
    if thermal_qualification not in ("SYNTHETIC_RC", "ASSUMED_RC", "CALIBRATED_RC"):
        raise ValueError("missing thermal qualification")
    seconds = (end - begin) / stats["simFreq"]
    if not math.isfinite(total) or not math.isfinite(total / seconds):
        raise ValueError("nonfinite accumulated ROI energy or power")
    return dict(measurement="ONLINE_MODEL_ACTIVITY_NOT_SILICON",
                qualification=next(label for label in qualifications if label in labels),
                thermal_qualification=thermal_qualification, begin_tick=begin, end_tick=end,
                roi_seconds=seconds, energy_j=total, average_w=total / seconds,
                epochs=len(energy), stats_block_indices=indices, temperature_c=temperatures)


def iter_stats_blocks(path):
    """Parse one complete native block at a time, including trailing diagnostics."""
    lines = None
    with path.open() as source:
        for line in source:
            if "Begin Simulation Statistics" in line:
                if lines is not None:
                    raise ValueError("nested statistics block")
                lines = [line]
            elif "End Simulation Statistics" in line:
                if lines is None:
                    raise ValueError("statistics end without begin")
                lines.append(line)
                yield stats_blocks("".join(lines))[0]
                lines = None
            elif lines is not None:
                lines.append(line)
    if lines is not None:
        raise ValueError("truncated statistics block")


def roi_statistics(outdir, begin, end):
    """Select exact ROI windows in one pass without retaining full stats history."""
    if type(begin) is not int or type(end) is not int or begin < 0 or end <= begin:
        raise ValueError("ROI end must follow a nonnegative integer begin tick")
    ledger = outdir / "online-activity.jsonl"
    if not ledger.is_file():
        selected, indices = None, []
        for index, block in enumerate(iter_stats_blocks(outdir / "stats.txt")):
            if block.get("finalTick") == end and block.get("simTicks") == end - begin:
                selected = block
                indices.append(index)
        if len(indices) != 1:
            raise ValueError("require exactly one stats dump matching the ROI begin/end")
        return selected, indices, False
    windows = {
        (epoch["end_tick"], epoch["end_tick"] - epoch["begin_tick"]):
        (order, epoch["frequency_hz"])
        for order, epoch in enumerate(roi_epochs(ledger, begin, end))
    }
    # Rates, occupancies, voltages and histograms cannot be added across resets.
    additive = re.compile(
        r"(?:\.commitStats0\.numInsts|\.dramBytes(?:Read|Written)"
        r"|\.m_demand_(?:hits|misses))$")
    totals, counts, indices = {}, {}, []
    frequency = None
    for index, block in enumerate(iter_stats_blocks(outdir / "stats.txt")):
        window = windows.get((block.get("finalTick"), block.get("simTicks")))
        if window is None:
            continue
        order, expected_frequency = window
        current = block.get("simFreq")
        if (order != len(indices) or type(current) not in (int, float)
                or not math.isfinite(current) or current <= 0
                or expected_frequency != current
                or (frequency is not None and frequency != current)):
            raise ValueError("duplicate, reordered or invalid online epoch statistics")
        frequency = current
        indices.append(index)
        for key, value in block.items():
            if not additive.search(key):
                continue
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError(f"invalid additive epoch counter: {key}")
            totals[key] = totals.get(key, 0) + value
            counts[key] = counts.get(key, 0) + 1
    if len(indices) != len(windows):
        raise ValueError("missing exact statistics for an online epoch")
    for key, count in counts.items():
        # BaseCPU suppresses numInsts when its own prerequisite is zero.
        if count != len(windows) and not key.endswith(".commitStats0.numInsts"):
            raise ValueError(f"missing additive epoch counter: {key}")
    totals.update(simFreq=frequency, simTicks=end - begin, finalTick=end)
    return totals, indices, True


def summarize_multicore(outdir, serial_log, *, workers, size_bytes, passes, channels, mode="read"):
    """Validate pinned memory work; size_bytes is the size of each array."""
    if mode not in ("read", "copy", "triad"):
        raise ValueError("unsupported memory mode")
    arrays = {"read": 1, "copy": 2, "triad": 3}[mode]
    outdir = Path(outdir)
    events = json.loads((outdir / "roi-events.json").read_text())
    if [event["phase"] for event in events] != ["warmup", "roi_begin", "roi_end"]:
        raise ValueError("incomplete or ambiguous ROI lifecycle")
    begin, end = events[1]["tick"], events[2]["tick"]
    stats, indices, online = roi_statistics(outdir, begin, end)
    serial_text = Path(serial_log).read_text(errors="replace")
    result = summarize_block(stats, serial_text, begin, end,
                             None if online else indices[0])
    if online:
        result["roi"].update(stats_block_indices=indices, accounting="contiguous_online_epochs")
        result["limitations"].append(
            "Online summary retains additive counters only; inspect per-epoch stats for other metrics.")
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
    committed = {}
    for name, value in stats.items():
        match = re.fullmatch(r"system\.roi_cpu(\d+)\.commitStats0\.numInsts", name)
        if match:
            cpu = int(match[1])
            if cpu in committed:
                raise ValueError("ambiguous O3 committed instruction counters")
            committed[cpu] = value
    instructions = {str(cpu): committed.get(cpu) for cpu in range(workers)}
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
    stats, indices, online = roi_statistics(outdir, begin, end)
    index = None if online else indices[0]
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
    if online:
        result.update(stats_block_indices=indices, accounting="contiguous_online_epochs")
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
