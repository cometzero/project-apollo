#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Validate reduced Linux tool runs; tool timings and whole-command ROI differ."""
import argparse
import json
import math
from pathlib import Path
import re

from benchmark import cache_metrics, cache_paths, stats_blocks


def positive(value):
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError("expected a finite positive measurement")
    return value


def parse_tool(tool, text):
    if tool == "lmbench":
        marker = ("# modified lmbench lat_mem_rd: sample-usec=200 "
                  "(ENOUGH override; calibrated overhead)")
        markers = re.findall(r"^# modified lmbench lat_mem_rd:.*$", text, re.M)
        if [line.rstrip("\r") for line in markers] != [marker]:
            raise ValueError("expected one modified lmbench 200 us timing marker")
        rows = re.findall(r"^\s*(\d+\.\d+)\s+(\S+)\s*$", text, re.M)
        sizes = [512, 1024, 2048, 3072]
        k = 4096
        while k <= 1048576:
            sizes.append(k)
            k += 2 ** k.bit_length() // 4
        if len(rows) != len(sizes):
            raise ValueError("expected all 21 lmbench size measurements")
        values = []
        for (size, latency), expected in zip(rows, sizes):
            if abs(float(size) - expected / 1048576) > .0000051:
                raise ValueError("unexpected lmbench working-set sequence")
            values.append(dict(working_set_bytes=expected,
                               ns_per_load=positive(latency)))
        return dict(settings=dict(sample_usec=200, maximum_working_set_bytes=1048576,
                                  stride_bytes=64, repetitions=1),
                    measurements=values, scope="absolute dependent-load latency",
                    limitations=["modified lmbench; not a standard upstream score",
                                 "single repetition; 200 us target interval limits precision",
                                 "ENOUGH override skips interval discovery; timing and loop overhead remain calibrated"])
    if tool == "stream":
        arrays = re.findall(r"Array size = (\d+) \(elements\), Offset = (\d+) \(elements\)", text)
        repeats = re.findall(r"Each kernel will be executed (\d+) times\.", text)
        if arrays != [("65536", "0")] or repeats != ["10"]:
            raise ValueError("expected STREAM 65536 elements, offset zero, ten iterations")
        settings = dict(array_elements=65536, offset_elements=0, iterations=10)
        if "Solution Validates:" not in text or "Failed Validation" in text:
            raise ValueError("STREAM numerical validation did not pass")
        quantum = re.search(r"precision appears to be (\d+) microseconds", text)
        if quantum:
            quantum = positive(quantum[1])
        elif "less than one microsecond" in text:
            quantum = 1.0  # STREAM itself conservatively uses one microsecond.
        else:
            raise ValueError("missing STREAM timer precision")
        rows = re.findall(r"^(Copy|Scale|Add|Triad):\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$", text, re.M)
        if [r[0] for r in rows] != ["Copy", "Scale", "Add", "Triad"]:
            raise ValueError("expected four STREAM kernels")
        values = []
        for name, rate, average, minimum, maximum in rows:
            rate, average, minimum, maximum = map(positive, (rate, average, minimum, maximum))
            if not minimum <= average <= maximum:
                raise ValueError("inconsistent STREAM timing interval")
            values.append(dict(kernel=name, MB_per_second=rate,
                               average_seconds=average, minimum_seconds=minimum,
                               maximum_seconds=maximum,
                               timing_quality="LOW_RESOLUTION" if minimum * 1e6 < 20 * quantum else "SUFFICIENT_TIMER_TICKS"))
        return dict(settings=settings, measurements=values, timer_quantum_us=quantum,
                    scope="cache-resident STREAM; read plus write bytes",
                    limitations=["reduced arrays; not an official DRAM STREAM score"])
    settings_rows = re.findall(
        r"Settings: bandwidth-size-kib=(\d+) latency-size-kib=(\d+) "
        r"duration-ms=(\d+) repeats=(\d+) latency-count=(\d+)", text)
    if settings_rows != [("16", "1024", "1", "1", "16384")]:
        raise ValueError("unexpected tinymembench settings")
    settings = dict(zip(("bandwidth_size_kib", "latency_size_kib", "duration_ms",
                         "repeats", "latency_count"), map(int, settings_rows[0])))
    bandwidth = re.findall(r"^\s*([^:\n]+?)\s*:\s*(\S+) MB/s(?:\s+\([^\n]*\))?\s*$", text, re.M)
    if len(bandwidth) != 26:
        raise ValueError("expected all 26 AArch64 bandwidth kernels")
    groups = []
    for section in text.split("block size : single random read / dual random read")[1:]:
        rows = re.findall(r"^\s*(\d+)\s*:\s*(\S+) ns\s*/\s*(\S+) ns\s*$", section, re.M)
        if [int(row[0]) for row in rows] != [2 ** n for n in range(10, 21)]:
            raise ValueError("expected latency sizes 1 KiB through 1 MiB")
        values = []
        for size, single, dual in rows:
            single, dual = float(single), float(dual)
            if any(not math.isfinite(v) or v < 0 for v in (single, dual)):
                raise ValueError("invalid extra latency")
            values.append(dict(working_set_bytes=int(size), single_extra_ns=single,
                               dual_extra_ns=dual))
        groups.append(dict(page_mode=section.splitlines()[0].strip(" ,"), measurements=values))
    if not 1 <= len(groups) <= 2:
        raise ValueError("missing or ambiguous latency page modes")
    return dict(settings=settings, bandwidth=[dict(kernel=name.strip(), MB_per_second=positive(rate))
                           for name, rate in bandwidth], latency=groups,
                scope="copy rates count copied bytes; latency subtracts baseline",
                limitations=["one repetition; no variance estimate or numerical checksum",
                             "16384 reads: approximately 0.061 ns timer quantization per access",
                             "zero extra latency may reflect subtraction and clamping"])


def summarize(directory, tool):
    directory = Path(directory)
    if json.loads((directory / "result.json").read_text()).get("status") != "PASS":
        raise ValueError("launcher did not PASS")
    serial = (directory / "uart.log").read_text(errors="replace")
    if serial.count("GEM5_CONTROL_RUN cpu=0 scope=whole-command") != 1:
        raise ValueError("one CPU0 whole-command run is required")
    output = directory / "m5out"
    events = json.loads((output / "roi-events.json").read_text())
    if [event["phase"] for event in events] != ["warmup", "roi_begin", "roi_end"]:
        raise ValueError("incomplete ROI lifecycle")
    ticks = events[2]["tick"] - events[1]["tick"]
    blocks = stats_blocks((output / "stats.txt").read_text())
    if len(blocks) not in (1, 2):
        raise ValueError("expected ROI dump and optional exit dump")
    stats = blocks[0]
    if (ticks <= 0 or stats.get("simTicks") != ticks or
            stats.get("finalTick") != events[2]["tick"]):
        raise ValueError("first statistics block does not match ROI ticks")
    frequency = positive(stats["simFreq"])
    config = json.loads((output / "config.json").read_text())
    return dict(tool=tool, status="PASS", evidence="uncalibrated-gem5-linux-model",
                tool_results=parse_tool(tool, serial), whole_command=dict(
                    scope="fork, exec, kernel, allocation, calibration and measurement",
                    roi_ticks=ticks, simulated_seconds=ticks / frequency,
                    cache_counters=cache_metrics(stats, cache_paths(config))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("tool", choices=("lmbench", "tinymembench", "stream"))
    args = parser.parse_args()
    try:
        result = summarize(args.run_directory, args.tool)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Invalid benchmark evidence: {error}\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
