#!/usr/bin/env python3
"""Validate SI CL1 guest measurements and prepare exact gem5 ROI replay."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import re


def stats_blocks(path):
    blocks = []
    current = None
    for line in path.read_text().splitlines():
        if "Begin Simulation Statistics" in line:
            if current is not None:
                raise ValueError("nested statistics block")
            current = {}
        elif "End Simulation Statistics" in line:
            if current is None:
                raise ValueError("unmatched statistics end")
            blocks.append(current)
            current = None
        elif current is not None:
            fields = line.split()
            if len(fields) >= 2:
                try:
                    current[fields[0]] = (
                        int(fields[1])
                        if re.fullmatch(r"[+-]?\d+", fields[1])
                        else float(fields[1])
                    )
                except ValueError:
                    pass  # Histogram metadata; required scalars are checked below.
    if current is not None:
        raise ValueError("truncated statistics block")
    return blocks



TARGETS = {"TCM", "L1", "L2", "SRAM_NC"}
OPS = {"read", "write", "chase"}
COUNTER_HZ = 100_000_000
SIM_FREQ = 1_000_000_000_000


def number(record, key, base=0):
    try:
        value = int(record[key], base)
    except (KeyError, ValueError) as exc:
        raise ValueError(f"missing/invalid {key}: {record}") from exc
    if value < 0:
        raise ValueError(f"negative {key}")
    return value


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def records(text):
    result = {}
    for line in text.splitlines():
        # UART logs may contain a prompt or a simulator prefix before a line.
        offset = line.find("SI_CL1_")
        if offset < 0:
            continue
        fields = line[offset:].strip("\x04\r\n").split()
        values = {}
        for field in fields[1:]:
            key, sep, value = field.partition("=")
            require(sep and key not in values, f"invalid field: {line}")
            values[key] = value
        result.setdefault(fields[0], []).append(values)
    return result


def one(grouped, name):
    rows = grouped.get(name, [])
    require(len(rows) == 1, f"expected one {name}, found {len(rows)}")
    return rows[0]


def distribution(values):
    ordered = sorted(values)
    require(bool(ordered), "empty latency distribution")
    return {
        "samples": len(ordered),
        "min_ns": ordered[0] * 1e9 / COUNTER_HZ,
        "mean_ns": sum(ordered) * 1e9 / COUNTER_HZ / len(ordered),
        "p50_ns": ordered[math.ceil(len(ordered) * 0.50) - 1] * 1e9 / COUNTER_HZ,
        "p95_ns": ordered[math.ceil(len(ordered) * 0.95) - 1] * 1e9 / COUNTER_HZ,
        "max_ns": ordered[-1] * 1e9 / COUNTER_HZ,
    }


def analyze(serial, backend):
    grouped = records(serial.read_text(errors="replace"))
    start = one(grouped, "SI_CL1_START")
    result = one(grouped, "SI_CL1_RESULT")
    require(number(start, "version") == 1, "unsupported guest record version")
    require(number(start, "cpus") == 4, "expected four CL1 CPUs")
    require(number(start, "counter_hz") == COUNTER_HZ, "unexpected counter frequency")
    require(result.get("status") == "PASS", "guest did not report functional PASS")
    require(number(result, "failures") == 0, "guest reported failures")
    for field in ("cpu_mask", "tcm_mask"):
        require(number(result, field, 16) == 0xF, f"incomplete {field}")
    cpus = grouped.get("SI_CL1_CPU", [])
    require(len(cpus) == 4, "missing/duplicate CPU records")
    require({number(c, "cpu") for c in cpus} == set(range(4)), "invalid logical CPU set")
    require(
        {number(c, "mpidr", 16) & 0xFF00FFFFFF for c in cpus}
        == {0x10000, 0x10100, 0x10200, 0x10300},
        "invalid MPIDR set",
    )
    for cpu in cpus:
        require(number(cpu, "el") == 1, "Zephyr is not at EL1")
        require(number(cpu, "sctlr", 16) & 0x1005 == 0x1005,
                "EL1 MPU or caches are disabled")
        require(cpu.get("private") == "PASS", "TCM private-memory test failed")
    maps = grouped.get("SI_CL1_MAP", [])
    require(len(maps) == 3, "expected TCM/MM/SRAM_NC mappings")
    require({m.get("target") for m in maps} == {"TCM", "MM", "SRAM_NC"},
            "incomplete memory mapping records")
    for mapping in maps:
        require(mapping.get("status") == "PASS", "MPU mapping failed")
        require(number(mapping, "matches") == 1, "missing/overlapping MPU region")
        base, size, attr = {
            "TCM": (0x100100000, 128 * 1024, 0x44),
            "MM": (0x40000000, 8 * 1024 * 1024, 0xFF),
            "SRAM_NC": (0x48000000, 8 * 1024 * 1024, 0x44),
        }[mapping["target"]]
        require((number(mapping, "base", 16), number(mapping, "bytes"),
                 number(mapping, "mair", 16)) == (base, size, attr),
                "unexpected memory address, size or attributes")

    memory, schedule = [], []
    seen = set()
    for row in grouped.get("SI_CL1_MEM", []):
        key = row.get("target"), row.get("op")
        require(key[0] in TARGETS and key[1] in OPS, "unknown memory case")
        require(key not in seen, f"duplicate memory case: {key}")
        seen.add(key)
        require(row.get("status") == "PASS", f"memory checksum failure: {key}")
        require(number(row, "irq_masked") == 1, "memory ROI was not IRQ-masked")
        hz, ticks = number(row, "counter_hz"), number(row, "ticks")
        begin, end = number(row, "begin"), number(row, "end")
        require(hz == COUNTER_HZ and ticks > 0, "invalid memory duration/frequency")
        require(end > begin and end - begin == ticks, "memory ROI boundary mismatch")
        size, iterations = number(row, "ws_bytes"), number(row, "iterations")
        require(size == (16 * 1024 if key[0] in {"TCM", "L1"} else 256 * 1024),
                "working set differs from the verified cache/TCM profile")
        useful, accesses = number(row, "useful_bytes"), number(row, "accesses")
        require(size > 0 and iterations > 0 and accesses > 0, "empty memory test")
        require(iterations == (4 if key[1] == "chase" else 8),
                "iteration count differs from the verified benchmark")
        require(useful == accesses * 8, "useful byte count disagrees with 64-bit accesses")
        if key[1] != "chase":
            require(useful == size * iterations, "stream byte count mismatch")
        if key[1] == "read":
            expected = sum(i ^ 0x13579BDF for i in range(size // 8)) * iterations
        elif key[1] == "write":
            expected = 0x2468ACE0 + iterations - 1
        else:
            expected = {"TCM": 0x100100000, "L1": 0x40000000,
                        "L2": 0x40000000, "SRAM_NC": 0x48000000}[key[0]]
            require(accesses == size // 64 * iterations, "pointer-chase load count mismatch")
        require(number(row, "checksum", 16) == expected, "independent checksum mismatch")
        seconds = ticks / hz
        memory.append({
            "target": key[0], "op": key[1], "ws_bytes": size,
            "iterations": iterations, "useful_bytes": useful, "accesses": accesses,
            "begin": begin, "end": end, "ticks": ticks,
            "checksum": expected,
            "sim_seconds": seconds, "useful_GB_s": useful / seconds / 1e9,
            "ns_per_access": seconds * 1e9 / accesses,
        })
        schedule.append({"name": "-".join(key),
                         "begin_tick": begin * (SIM_FREQ // hz),
                         "end_tick": end * (SIM_FREQ // hz)})
    require(seen == {(t, op) for t in TARGETS for op in OPS}, "incomplete memory cases")
    require(number(result, "mem_cases") == len(memory), "memory count mismatch")
    schedule.sort(key=lambda row: row["begin_tick"])
    for left, right in zip(schedule, schedule[1:]):
        require(left["end_tick"] < right["begin_tick"], "overlapping memory ROIs")

    irq = {}
    samples = grouped.get("SI_CL1_IRQ_SAMPLE", [])
    require(number(result, "irq_samples") == len(samples) == 48, "IRQ sample count mismatch")
    summaries = grouped.get("SI_CL1_IRQ", [])
    require(len(summaries) == 5, "expected five IRQ summaries")
    for phase, cpu, count in [("idle", 0, 16)] + [("loaded", c, 8) for c in range(4)]:
        label = f"{phase}/cpu{cpu}"
        selected = [s for s in samples if s.get("phase") == phase and number(s, "cpu") == cpu]
        require(len(selected) == count, f"expected {count} {label} IRQ samples")
        require({number(s, "sample") for s in selected} == set(range(count)),
                f"invalid {label} IRQ sample indices")
        selected.sort(key=lambda row: number(row, "sample"))
        irq_ticks, dispatch_ticks = [], []
        previous = -1
        for sample in selected:
            deadline, isr, thread = (number(sample, k) for k in ("scheduled", "isr", "thread"))
            require(previous < deadline <= isr <= thread <= number(sample, "finish"),
                    "invalid IRQ timestamp order")
            previous = deadline
            irq_ticks.append(isr - deadline)
            dispatch_ticks.append(thread - isr)
        summary = [s for s in summaries if s.get("phase") == phase and number(s, "cpu") == cpu]
        require(len(summary) == 1, f"missing/duplicate IRQ summary: {label}")
        summary = summary[0]
        require(summary.get("source") == "CNTP_PPI29", "unexpected interrupt source")
        require(summary.get("status") == "PASS" and number(summary, "samples") == count,
                "incomplete IRQ test")
        period = number(summary, "period_ticks")
        deadlines = [number(s, "scheduled") for s in selected]
        gaps = [right - left for left, right in zip(deadlines, deadlines[1:])]
        require(period > 0 and all(gap > 0 and gap % period == 0 for gap in gaps),
                f"IRQ releases do not follow the reported period: {label}")
        skipped = sum(gap // period - 1 for gap in gaps)
        require(number(summary, "skipped") == skipped,
                f"IRQ skipped count disagrees with release gaps: {label}")
        for prefix, values in (("irq", irq_ticks), ("thread", dispatch_ticks)):
            for suffix, value in (("min", min(values)), ("max", max(values)), ("sum", sum(values))):
                require(number(summary, prefix + "_" + suffix) == value,
                        f"IRQ raw/summary mismatch: {label}")
        irq[label] = {"period_ticks": period, "skipped": skipped,
                      "timer_to_isr": distribution(irq_ticks),
                      "isr_to_thread": distribution(dispatch_ticks)}
    realtime = []
    rt_records = grouped.get("SI_CL1_RT", [])
    require(number(result, "rt_tasks") == len(rt_records) == 4, "RT task count mismatch")
    require({number(r, "cpu") for r in rt_records} == set(range(4)), "invalid RT CPU set")
    for row in rt_records:
        require(row.get("status") == "PASS", "RT functional test failed")
        parsed = {key: number(row, key) for key in (
            "cpu", "priority", "period_ticks", "deadline_ticks", "releases",
            "deadline_miss", "skipped", "exec_min", "exec_max", "exec_sum", "response_max",
        )}
        require(parsed["releases"] == 8, "RT task did not complete eight jobs")
        irq_summary = irq[f"loaded/cpu{parsed['cpu']}"]
        require(all(parsed[k] == irq_summary[k] for k in ("period_ticks", "skipped")),
                "RT/IRQ period or skipped count mismatch")
        require(number(row, "checksum", 16) == 0xF5C603B3, "RT checksum mismatch")
        require(0 < parsed["deadline_ticks"] <= parsed["period_ticks"], "invalid RT deadline")
        require(parsed["exec_min"] <= parsed["exec_max"], "invalid RT execution times")
        raw = [s for s in samples if s["phase"] == "loaded"
               and number(s, "cpu") == parsed["cpu"]]
        execution = [number(s, "finish") - number(s, "thread") for s in raw]
        response = [number(s, "finish") - number(s, "scheduled") for s in raw]
        for field, value in (("exec_min", min(execution)), ("exec_max", max(execution)),
                             ("exec_sum", sum(execution)), ("response_max", max(response)),
                             ("deadline_miss", sum(t > parsed["deadline_ticks"] for t in response))):
            require(parsed[field] == value, f"RT raw/summary mismatch: {field}")
        schedulable = parsed["deadline_miss"] == 0 and parsed["skipped"] == 0
        require(row.get("schedulable") == ("PASS" if schedulable else "FAIL"),
                "RT schedulability result disagrees with counters")
        parsed["schedulable"] = schedulable
        realtime.append(parsed)
    loads = grouped.get("SI_CL1_LOAD", [])
    require(len(loads) == 4 and {number(r, "cpu") for r in loads} == set(range(4)),
            "incomplete background load records")
    require(all(number(r, "passes") > 0 for r in loads), "background load did not execute")
    return {
        "schema": 1, "backend": backend, "functional_status": "PASS",
        "qualification": "MODEL_ONLY" if backend == "gem5" else "FUNCTIONAL_ONLY",
        "serial": str(serial.resolve()),
        "serial_sha256": hashlib.sha256(serial.read_bytes()).hexdigest(),
        "counter_hz": COUNTER_HZ, "cpus": cpus, "mappings": maps,
        "memory": memory, "interrupts": irq, "realtime": realtime,
        "background_load": loads,
        "schedulability_status": "PASS" if all(r["schedulable"] for r in realtime) else "FAIL",
        "roi_schedule": schedule,
        "roi_schedule_qualification": "Requires gem5 simFreq=1THz, counter epoch=0 and deterministic replay",
    }


def simulator_evidence(directory):
    manifest = json.loads((directory / "manifest.json").read_text())
    result = json.loads((directory / "run-result.json").read_text())
    require(manifest["returncode"] == 0, "gem5 process did not exit successfully")
    require(result["exit_cause"] == "UART received EOT", "gem5 did not receive guest EOT")
    require((result["sim_hz"], result["counter_hz"], result["counter_epoch_tick"])
            == (SIM_FREQ, COUNTER_HZ, 0), "unsupported simulator/counter timebase")
    return {
        "directory": str(directory.resolve()), "cpu": result["cpu"],
        "elf_sha256": manifest["elf_sha256"], "gem5_sha256": manifest["gem5_sha256"],
        "configuration_sha256": manifest["configuration_sha256"],
        "configuration_args": manifest["configuration_args"],
        "host_seconds": manifest["host_seconds"],
        "serial_sha256": hashlib.sha256((directory / "system.platform.terminal").read_bytes()).hexdigest(),
        "config_json_sha256": hashlib.sha256((directory / "config.json").read_bytes()).hexdigest(),
    }


def memory_path_evidence(memory, stats):
    """Check the default profile's measured data path, allowing 1% ROI edge traffic."""
    def count(path, name):
        # Classic cache and SimpleMemory suppress zero-valued vector totals.
        return stats.get(f"system.{path}.{name}::total", 0)

    target, op = memory["target"], memory["op"]
    l1 = count("cpu0.dcache", "overallAccesses")
    l2 = count("l2", "overallAccesses")
    traffic = {path: count(path, "bytesRead") + count(path, "bytesWritten")
               for path in ("cpu0.dtcm", "mm_sram", "nc_sram")}
    if target in {"TCM", "SRAM_NC"}:
        path = "cpu0.dtcm" if target == "TCM" else "nc_sram"
        transferred = count(path, "bytesWritten" if op == "write" else "bytesRead")
        require(abs(transferred / memory["useful_bytes"] - 1) <= 0.01,
                f"{target}-{op}: backing traffic differs by more than 1%")
        require(l1 == l2 == 0 and all(v == 0 for p, v in traffic.items() if p != path),
                f"{target}-{op}: unexpected cached/shared data path")
    else:
        require(l1 > 0 and all(v == 0 for v in traffic.values()),
                f"{target}-{op}: missing cache traffic or unexpected backing access")
        if target == "L1":
            require(count("cpu0.dcache", "overallHits") / l1 >= 0.99 and l2 == 0,
                    f"L1-{op}: working set did not stay in L1")
        else:
            lines = memory["accesses"] if op == "chase" else memory["useful_bytes"] / 64
            require(count("cpu0.dcache", "overallMisses") >= 0.99 * lines
                    and l2 >= 0.99 * lines
                    and count("l2", "overallHits") / l2 >= 0.99,
                    f"L2-{op}: insufficient L1 miss/L2 hit coverage")
    return {"status": "PASS", "target": target, "op": op,
            "l1_accesses": l1, "l2_accesses": l2, "backing_bytes": traffic}


def replay_evidence(metrics, directory):
    replay = analyze(directory / "system.platform.terminal", "gem5")
    replay_sim = simulator_evidence(directory)
    require(replay_sim["cpu"] in {"minor", "timing"}, "atomic execution is not timing evidence")
    for key in ("cpu", "elf_sha256", "gem5_sha256", "configuration_sha256", "configuration_args"):
        require(metrics["simulator"][key] == replay_sim[key], f"replay input differs: {key}")
    for key in ("memory", "interrupts", "realtime", "background_load"):
        require(metrics[key] == replay[key], f"guest replay is not deterministic: {key}")
    result = json.loads((directory / "run-result.json").read_text())
    expected = [{"name": roi["name"], "phase": phase, "tick": roi[phase + "_tick"]}
                for roi in metrics["roi_schedule"] for phase in ("begin", "end")]
    require(result["roi_complete"] and result["roi_events"] == expected,
            "simulator did not visit every ROI boundary")
    blocks = stats_blocks(directory / "stats.txt")
    rows = []
    for roi in metrics["roi_schedule"]:
        matched = [b for b in blocks if b.get("finalTick") == roi["end_tick"]
                   and b.get("simTicks") == roi["end_tick"] - roi["begin_tick"]]
        require(len(matched) == 1, f"expected exactly one stats block: {roi['name']}")
        block = matched[0]
        require(block.get("simFreq") == SIM_FREQ, "unexpected stats tick frequency")
        selected = {key: value for key, value in block.items()
                    if key.endswith("::total") and any(part in key for part in (
                        ".overallHits", ".overallMisses", ".overallAccesses",
                        ".bytesRead", ".bytesWritten", ".numReads", ".numWrites"))}
        require(bool(selected), "cache/memory counters are missing")
        memory = next(m for m in metrics["memory"] if f"{m['target']}-{m['op']}" == roi["name"])
        rows.append({**roi, "path": memory_path_evidence(memory, selected), "stats": selected})
    return {"status": "PASS", "definition": "identical guest timing and exact counter-derived ROI blocks",
            "simulator": replay_sim, "memory_rois": rows}


def markdown(metrics):
    lines = ["# SI CL1 실행 결과", "",
             f"Backend: `{metrics['backend']}`, 기능: **PASS**, "
             f"주기 작업 deadline: **{metrics['schedulability_status']}**.", "",
             "측정값은 guest counter 기준이다. QEMU 값은 기능 검사이며, gem5 값도 실물 보정 전 모델값이다.", "",
             "| 대상 | 동작 | working set (KiB) | 시간 (µs) | 유효 GB/s | ns/access |",
             "|---|---|---:|---:|---:|---:|"]
    for row in metrics["memory"]:
        lines.append(f"| {row['target']} | {row['op']} | {row['ws_bytes'] / 1024:g} | "
                     f"{row['sim_seconds'] * 1e6:.3f} | {row['useful_GB_s']:.3f} | "
                     f"{row['ns_per_access']:.3f} |")
    lines += ["", "chase의 GB/s는 실제 SRAM bus traffic이 아니라 8-byte 종속 load의 유효 처리량이다.", "",
              "| 조건 | 경계 | samples | min (ns) | mean (ns) | p95 (ns) | max (ns) |",
              "|---|---|---:|---:|---:|---:|---:|"]
    for phase, boundaries in metrics["interrupts"].items():
        for boundary in ("timer_to_isr", "isr_to_thread"):
            row = boundaries[boundary]
            lines.append(f"| {phase} | {boundary} | {row['samples']} | {row['min_ns']:.1f} | "
                         f"{row['mean_ns']:.1f} | {row['p95_ns']:.1f} | {row['max_ns']:.1f} |")
    lines += ["", "p95는 nearest-rank 방식이다. 조건별 8/16 samples의 관찰 최대값은 WCET 보증이 아니다.", "",
              "| CPU | priority | period (µs) | deadline (µs) | releases | misses | skipped | max response (µs) |",
              "|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in metrics["realtime"]:
        us = 1e6 / metrics["counter_hz"]
        lines.append(f"| {row['cpu']} | {row['priority']} | {row['period_ticks'] * us:g} | "
                     f"{row['deadline_ticks'] * us:g} | {row['releases']} | {row['deadline_miss']} | "
                     f"{row['skipped']} | {row['response_max'] * us:.2f} |")
    lines += ["", f"Serial SHA256: `{metrics['serial_sha256']}`.", ""]
    if "simulator" in metrics:
        sim = metrics["simulator"]
        lines += [f"CPU: `{sim['cpu']}`, host time: {sim['host_seconds']:.2f} s.",
                  f"ELF SHA256: `{sim['elf_sha256']}`.",
                  f"gem5 SHA256: `{sim['gem5_sha256']}`.", ""]
    if "replay" in metrics:
        lines += ["Deterministic ROI replay 및 12개 메모리 경로: **PASS**. "
                  "TCM/NC byte 오차 허용은 1%, cache hit 판정은 99% 이상이다. "
                  "구간별 counter와 경로 검사는 metrics.json에 보존했다.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("serial", type=Path)
    parser.add_argument("--backend", required=True, choices=("qemu", "qbox", "gem5"))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--gem5-dir", type=Path, help="attach native simulator provenance")
    parser.add_argument("--replay-dir", type=Path, help="verify deterministic replay and extract ROI statistics")
    args = parser.parse_args()
    if args.replay_dir and not args.gem5_dir:
        parser.error("--replay-dir requires --gem5-dir from the initial run")
    if args.gem5_dir and args.backend != "gem5":
        parser.error("--gem5-dir requires --backend gem5")
    try:
        metrics = analyze(args.serial, args.backend)
        if args.gem5_dir:
            metrics["simulator"] = simulator_evidence(args.gem5_dir)
            require(metrics["serial_sha256"] == metrics["simulator"]["serial_sha256"],
                    "serial log does not belong to the supplied gem5 run")
            if metrics["simulator"]["cpu"] == "atomic":
                metrics["qualification"] = "FUNCTIONAL_ONLY"
        if args.replay_dir:
            metrics["replay"] = replay_evidence(metrics, args.replay_dir)
    except (KeyError, OSError, ValueError) as exc:
        parser.exit(1, f"SI CL1 analysis failed: {exc}\n")
    args.output.mkdir(parents=True, exist_ok=True)
    for name, value in (("metrics.json", metrics), ("roi-schedule.json", metrics["roi_schedule"])):
        (args.output / name).write_text(json.dumps(value, indent=2) + "\n")
    (args.output / "report.md").write_text(markdown(metrics))
    with (args.output / "memory.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(metrics["memory"][0]))
        writer.writeheader()
        writer.writerows(metrics["memory"])
    print(f"SI CL1 functional PASS; schedulability {metrics['schedulability_status']}: {args.output}")


if __name__ == "__main__":
    main()
