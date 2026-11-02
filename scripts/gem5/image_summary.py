# SPDX-License-Identifier: BSD-3-Clause
"""Read-only validation of the synthetic image workload and native O3 ROI."""

import functools
import json
import math
from pathlib import Path
import re
import statistics
import struct

from benchmark import cache_metrics, roi_statistics


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(record, key, minimum=0, maximum=None):
    value = record.get(key)
    require(type(value) is int and value >= minimum
            and (maximum is None or value <= maximum), f"invalid {key}")
    return value


def finite(value, name, positive=False):
    require(type(value) in (int, float) and math.isfinite(value)
            and (value > 0 if positive else value >= 0), f"invalid {name}")
    return value


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise ValueError(f"nonfinite JSON value: {value}")

    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


@functools.lru_cache(maxsize=16)
def fixture_hash(width, height, pool):
    """Independent rgb_formula_v1 oracle, canonical little-endian float bytes."""
    values = [struct.pack("<f", (value - 128) / 128) for value in range(256)]
    digest = 14695981039346656037
    for slot in range(pool):
        for channel in range(3):
            for pixel in range(width * height):
                value = (pixel * 13 + channel * 37 + slot * 17
                         + pixel // width * 3) & 255
                for byte in values[value]:
                    digest = ((digest ^ byte) * 1099511628211) & ((1 << 64) - 1)
    return f"{digest:016x}"


def guest_records(serial_log):
    records = {name: [] for name in ("RESULT", "FRAME", "BACKGROUND")}
    order = []
    for line in Path(serial_log).read_text(errors="strict").splitlines():
        line = line.strip()
        if not line.startswith("APOLLO_IMAGE_"):
            continue
        if line == "APOLLO_IMAGE_READY initialization=atomic scope=synthetic_exploratory":
            order.append("READY")
            continue
        name, separator, payload = line.removeprefix("APOLLO_IMAGE_").partition(" ")
        require(separator and name in records, "unknown or malformed image marker")
        record = strict_json(payload)
        require(type(record) is dict, "image marker must contain an object")
        records[name].append(record)
        order.append(name)
    require(len(records["RESULT"]) == 1, "require exactly one image result")
    require(order == ["READY"] + ["BACKGROUND"] * len(records["BACKGROUND"])
            + ["FRAME"] * len(records["FRAME"]) + ["RESULT"],
            "incomplete, extra or reordered image markers")
    return records["RESULT"][0], records["FRAME"], records["BACKGROUND"]


def validate_guest(guest, frames, background, expected):
    constants = dict(schema=1, result="PASS", host=False,
                     kernel="rgb_u8_hwc_to_f32_chw", fixture="rgb_formula_v1",
                     normalization="(value-128)/128", scope="synthetic_exploratory",
                     state="steady_state_warmup_requested", arrival="closed_loop",
                     queue_policy="one_in_flight_no_drop", counter="CNTVCT_EL0",
                     output_validation_scope="every_element_of_each_final_pool_buffer",
                     timing_scope="kernel_calls_with_counter_and_completion_barrier",
                     roi_includes="start_barrier_frames_background_completion_barrier",
                     output_mismatches=0)
    for key, value in constants.items():
        require(type(guest.get(key)) is type(value) and guest[key] == value,
                f"guest contract mismatch: {key}")
    width = integer(guest, "width", 1, 16384)
    height = integer(guest, "height", 1, 16384)
    count = integer(guest, "frames", 1, 4096)
    pool = integer(guest, "frame_pool", 1, 64)
    integer(guest, "warmup_passes", 1, 1024)
    cpu = integer(guest, "cpu", 0, 1023)
    workers = integer(guest, "background_workers", 0, 15)
    cpus = guest.get("background_cpus")
    require(type(cpus) is list and len(cpus) == workers
            and all(type(item) is int and 0 <= item < 1024 for item in cpus)
            and len(set(cpus + [cpu])) == workers + 1, "invalid background CPU set")
    require(len(frames) == count and count >= pool, "incomplete frame pool coverage")
    require(len(background) == workers, "incomplete background records")
    mode = guest.get("background_mode")
    require(mode in (("read", "copy") if workers else ("none",)), "invalid background mode")
    kib = integer(guest, "background_kib_per_worker", 4 if workers else 0, 262144)
    require(kib % 4 == 0 and (workers or kib == 0), "invalid background size")
    arrays = 2 if mode == "copy" else 1
    working_set = width * height * 15 * pool
    for key, value in dict(working_set_bytes=working_set,
                           useful_bytes=width * height * 15 * count,
                           validated_elements=width * height * 3 * pool).items():
        require(integer(guest, key) == value, f"inconsistent {key}")
    allocation = integer(guest, "allocated_bytes", 1, 1024 ** 3)
    require(allocation >= working_set + kib * 1024 * workers * arrays,
            "allocation is smaller than workload buffers")
    frequency = integer(guest, "counter_hz", 1, (1 << 32) - 1)
    begin, end = integer(guest, "roi_start_tick"), integer(guest, "roi_end_tick")
    ns = lambda ticks: ticks * 1_000_000_000 // frequency
    require(end > begin and integer(guest, "roi_elapsed_ns", 1) == ns(end - begin),
            "invalid guest ROI duration")
    for index, frame in enumerate(frames):
        require(integer(frame, "frame") == index and integer(frame, "slot") == index % pool,
                "reordered frame or wrong pool slot")
        release, start, finish = [integer(frame, key) for key in
                                  ("release_tick", "start_tick", "finish_tick")]
        require(begin <= release <= start < finish <= end, "invalid frame timestamps")
        require(index == 0 or release == frames[index - 1]["finish_tick"],
                "invalid closed-loop frame release")
        require(integer(frame, "duration_ns", 1) == ns(finish - start),
                "frame duration disagrees with counter ticks")
        frame["response_ns"] = ns(finish - release)
    total_background = 0
    for index, worker in enumerate(background):
        require(integer(worker, "cpu") == cpus[index] and worker.get("mode") == mode,
                "background worker mismatch")
        chunks = integer(worker, "completed_chunks", 1)
        useful = integer(worker, "useful_bytes", 1)
        require(useful == chunks * 4096 * arrays, "background useful bytes mismatch")
        start, finish = integer(worker, "start_tick"), integer(worker, "finish_tick")
        require(begin <= start < finish <= end, "invalid background timestamps")
        require(finish >= frames[-1]["finish_tick"],
                "background finished before final foreground frame")
        overlap = max(0, min(finish, frames[-1]["finish_tick"])
                      - max(start, frames[0]["start_tick"]))
        require(integer(worker, "foreground_overlap_ticks", 1) == overlap,
                "background did not overlap foreground")
        total_background += useful
    require(integer(guest, "background_useful_bytes") == total_background,
            "background aggregate mismatch")
    if expected is not None:
        require(type(expected) is dict, "expected must be a field mapping")
        for key, value in expected.items():
            require(key in guest and type(guest[key]) is type(value) and guest[key] == value,
                    f"requested image workload mismatch: {key}")
    require(guest.get("output_hash_fnv1a64") == fixture_hash(width, height, pool),
            "output hash disagrees with independent fixture oracle")
    return [cpu] + cpus


def summarize_image(outdir, serial_log, *, expected=None):
    """Validate artifacts without rewriting them; expected uses guest field names.

    Per-frame response_ns includes release-to-start overhead. duration_ns covers
    the kernel plus memory completion; both use CNTVCT, not gem5 simTicks.
    """
    outdir = Path(outdir)
    guest, frames, background = guest_records(serial_log)
    workers = validate_guest(guest, frames, background, expected)
    events = strict_json((outdir / "roi-events.json").read_text())
    require(type(events) is list and len(events) == 3
            and all(type(event) is dict for event in events)
            and [event.get("phase") for event in events] == ["warmup", "roi_begin", "roi_end"],
            "incomplete or ambiguous O3 ROI lifecycle")
    warmup, begin, end = [integer(event, "tick") for event in events]
    require(warmup < begin < end and all("case_id" not in event for event in events),
            "invalid O3 warmup/ROI boundaries")
    stats, indices, online = roi_statistics(outdir, begin, end)
    frequency = finite(stats.get("simFreq"), "simFreq", positive=True)
    seconds = (end - begin) / frequency
    guest_seconds = (guest["roi_end_tick"] - guest["roi_start_tick"]) / guest["counter_hz"]
    require(guest_seconds <= seconds + 1 / guest["counter_hz"],
            "guest counter interval exceeds native ROI duration")
    system = strict_json((outdir / "config.json").read_text())["system"]
    timer, counter = system["platform"]["timer"], system["platform"]["counter"]
    require(timer.get("type") == "GenericTimer" and counter.get("type") == "SystemCounter"
            and timer.get("counter") == counter.get("path"), "unresolved architected counter")
    counter_hz = integer(timer, "cntfrq", 1)
    require(counter.get("freqs") == [counter_hz],
            "variable SystemCounter frequencies lack runtime frequency evidence")
    require(guest["counter_hz"] == counter_hz, "guest counter_hz differs from configured counter")
    configured = {cpu["cpu_id"]: cpu for cpu in system["roi_cpu"]}
    require(len(configured) == len(system["roi_cpu"]), "duplicate configured CPU IDs")
    # ArmO3CPU inherits the native BaseO3CPU SimObject type. The switched CPU
    # references the original CPU's ArmISA object by path in config.json.
    isas = {isa["path"]: isa for cpu in system["cpu"] + system["roi_cpu"]
            for isa in cpu.get("isa", []) if type(isa) is dict}
    require(all(cpu in configured and configured[cpu].get("type") in ("ArmO3CPU", "BaseO3CPU")
                for cpu in workers), "worker is not a configured O3 CPU")
    for cpu in workers:
        references = configured[cpu].get("isa", [])
        resolved = [isas.get(isa, {}) if type(isa) is str else isa for isa in references]
        require(resolved and all(type(isa) is dict and isa.get("type") == "ArmISA"
                                 for isa in resolved), "O3 worker has no resolved ArmISA")
    committed = {}
    for name, value in stats.items():
        match = re.fullmatch(r"system\.roi_cpu(\d+)\.commitStats0\.numInsts", name)
        if match:
            cpu = int(match[1])
            require(cpu not in committed, "ambiguous O3 instruction counters")
            committed[cpu] = finite(value, name)
    instructions = {str(cpu): finite(committed.get(cpu), f"O3 instructions for CPU {cpu}", True)
                    for cpu in workers}
    channels = {}
    for name, value in stats.items():
        match = re.fullmatch(r"system\.mem_ctrls(\d+)\.dram\.dramBytes(Read|Written)", name)
        if match:
            channel, direction = str(int(match[1])), match[2]
            require(direction not in channels.setdefault(channel, {}), "ambiguous DRAM counter")
            channels[channel][direction] = finite(value, name)
    require(set(channels) == {str(index) for index in range(len(system["mem_ctrls"]))}
            and bool(channels) and all(set(row) == {"Read", "Written"} for row in channels.values()),
            "missing configured DRAM counters")
    paths = {
        "L1": [cpu["l1d"]["cache"]["path"] for cpu in system["cpu"]],
        "L2": [cpu["l2"]["cache"]["path"] for cpu in system["cpu"]],
        "L3": [rnf["dsu_l3"]["cache"]["path"] for rnf in system["ruby"]["rnf"]],
        "SLC_proxy": [home["cntrl"]["cache"]["path"] for home in system["ruby"]["hnf"]],
    }
    require(all(paths.values()), "missing cache inventory")
    caches = cache_metrics(stats, paths)
    for level, metrics in caches.items():
        finite(metrics["hits"], level + " hits")
        finite(metrics["misses"], level + " misses")
    foreground_seconds = (frames[-1]["finish_tick"] - frames[0]["release_tick"]) / guest["counter_hz"]

    def observed(key):
        values = [frame[key] for frame in frames]
        return dict(sample_count=len(values), median=statistics.median(values), observed_max=max(values),
                    statistic_scope="observed_frames_only")

    read = sum(channel["Read"] for channel in channels.values())
    written = sum(channel["Written"] for channel in channels.values())
    result = dict(
        qualification="MODEL_ONLY", guest=guest, frames=frames, background=background,
        roi=dict(begin_tick=begin, end_tick=end, ticks=end - begin, frequency_hz=frequency,
                 seconds=seconds, tick_source="gem5_simTicks", stats_block_indices=indices,
                 stats_block_index=None if online else indices[0],
                 accounting="contiguous_online_epochs" if online else "exact_native_roi"),
        application=dict(useful_bytes=guest["useful_bytes"], GB_s=guest["useful_bytes"] / seconds / 1e9,
                         frames_per_second=len(frames) / seconds,
                         throughput_scope="native_roi_including_background_completion",
                         guest_roi_seconds=guest_seconds, foreground_seconds=foreground_seconds,
                         foreground_frames_per_second=len(frames) / foreground_seconds,
                         foreground_GB_s=guest["useful_bytes"] / foreground_seconds / 1e9,
                         foreground_scope="first_release_to_last_finish_CNTVCT_EL0",
                         frame_latency_ns=observed("response_ns"),
                         kernel_latency_ns=observed("duration_ns")),
        dram=dict(read_bytes=read, write_bytes=written, GB_s=(read + written) / seconds / 1e9,
                  availability="available", channels=channels),
        cache_counters=caches,
        cache_counter_scope="all configured cores, DSUs and Home nodes, including OS traffic",
        worker_committed_instructions=instructions,
        limitations=[
            "Synthetic RGB normalization is exploratory, not an autonomous-driving application qualification.",
            "Latency summaries describe observed closed-loop frames; no p99 or WCET guarantee.",
            "Output oracle checks every element of final pool buffers, not every intermediate frame output.",
            "CNTVCT frame ticks and native gem5 simTicks have separate frequencies and origins.",
            "DRAM counters include OS traffic and serviced bursts; dirty cache lines need not be drained.",
        ])
    if online:
        result["limitations"].append("Online epochs retain additive counters only.")
    json.dumps(result, allow_nan=False)
    return result
