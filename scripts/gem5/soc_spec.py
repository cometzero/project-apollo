#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Read-only Apollo SoC campaign inventory, comparisons and target decisions.

This does not run gem5 or replace verify_config.py. Reports preserve execution,
measurement, configuration and target status separately. Output must be new.
"""

import argparse
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import re

import benchmark


NORMALIZATION = "apollo-host-path-port-v1"
STATUSES = {"PASS", "FAIL", "ERROR", "TIMEOUT", "SKIP", "UNSUPPORTED", "NOT_RUN"}
# Schema 1 is the launcher's native import closure plus these AP configuration
# inputs. The selected candidate profile has its own input hash, not a source
# exception that can silently remove common defaults from this contract.
MODEL_SOURCE_SCHEMA = 1
MODEL_SOURCE_REQUIRED = (
    "configs/zena_cmn/run_fs.py", "configs/zena_cmn/parameters.py",
    "configs/zena_cmn/ruby_system_builder.py", "configs/zena_cmn/chi_topology.py",
    "configs/zena_cmn/profiles/default.yaml",
    "configs/ruby/__init__.py", "configs/ruby/CHI_config.py",
    "configs/topologies/__init__.py", "configs/topologies/CustomMesh.py",
    "configs/topologies/BaseTopology.py",
    "configs/example/arm/zena_css.py", "configs/example/arm/zena_css_models.py",
)
WORKLOAD_FIELDS = (
    "benchmark", "mode", "kernel", "workers", "passes", "working_set_bytes",
    "warmup_passes", "initialization_before_switch", "channel_phase_spread",
    "affinity", "width", "height", "frames", "frame_pool", "cpu", "foreground_cpu",
    "background_cpus", "background_mode", "background_kib", "seed",
    "background_kib_per_worker", "input_sha256", "frame_reuse", "arrival_policy",
    "fixture", "normalization", "state", "arrival", "queue_policy",
    "output_validation_scope", "timing_scope", "roi_includes", "counter_hz",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite(value, *, positive=False):
    return (type(value) in (int, float) and math.isfinite(value)
            and (value > 0 if positive else value >= 0))


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid(value):
        raise ValueError(f"nonfinite JSON number: {value}")

    return json.loads(Path(path).read_text(), object_pairs_hook=pairs,
                      parse_constant=invalid)


def digest(path):
    path = Path(path)
    before = path.stat()
    value = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            value.update(block)
    after = path.stat()
    require((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
            f"input changed during hashing: {path}")
    return value.hexdigest()


def json_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False,
                                     separators=(",", ":")).encode()).hexdigest()


def canonical_config(config, run):
    """Normalize run-local file paths and one host-only listener field."""
    prefix = str(Path(run).resolve()) + "/"

    def normalize(value):
        if isinstance(value, dict):
            return {key: normalize(child) for key, child in value.items()}
        if isinstance(value, list):
            return [normalize(child) for child in value]
        if isinstance(value, str) and value.startswith(prefix):
            return "<RUN>/" + value[len(prefix):]
        return value

    result = normalize(config)
    result["system"]["platform"]["terminal"]["port"] = "<HOST_CONSOLE_PORT>"
    return result


def changed(left, right):
    """Keep structural types; escape literal dots/backslashes in field names."""
    result = {}

    def visit(a, b, prefix):
        if type(a) is not type(b):
            result[prefix] = dict(before=a, after=b)
        elif isinstance(a, dict):
            for key in sorted(a.keys() | b.keys()):
                escaped = key.replace("\\", "\\\\").replace(".", "\\.")
                path = f"{prefix}.{escaped}" if prefix else escaped
                if key not in a or key not in b:
                    result[path] = dict(before=a.get(key), after=b.get(key),
                                        before_present=key in a, after_present=key in b)
                else:
                    visit(a[key], b[key], path)
        elif isinstance(a, list) and len(a) == len(b):
            for index, (first, second) in enumerate(zip(a, b)):
                visit(first, second, f"{prefix}.{index}")
        elif a != b:
            result[prefix] = dict(before=a, after=b)

    visit(left, right, "")
    return result


def metric(value, unit, *, statistic="aggregate", samples=1,
           sample_definition="completed-roi"):
    require(finite(value), "metric must be finite and nonnegative")
    return dict(value=value, unit=unit, statistic=statistic, samples=samples,
                sample_definition=sample_definition, confidence_policy="observed")


def saved_verification(run, report_path, launch, native):
    """Bind an existing verifier report offline; never invoke its native oracle."""
    if not report_path.is_file():
        return dict(status="NOT_RUN", reason="missing configuration verification")
    report = read_json(report_path)
    require(report.get("status") == "PASS" and not report.get("failures")
            and report.get("device_tree", {}).get("status") == "PASS",
            "configuration/DT verification failed")
    hashes = report["artifact_hashes"]
    for name in ("config.json", "system.dtb", "resolved-profile.json"):
        require(hashes.get(name) == digest(run / "m5out" / name),
                f"stale configuration verification: {name}")
    require(hashes.get("gem5") == launch.get("gem5_sha256"),
            "configuration verifier used a different native binary")
    require(native.get("source_sha256"), "missing native source identity")
    for name, expected in native["source_sha256"].items():
        require(hashes.get(name) == expected,
                f"verifier/model source identity mismatch: {name}")
    require(hashes.get("oracle_loaded_sources") and hashes.get("verifier")
            and hashes.get("oracle"), "unbound verifier/oracle provenance")
    if launch.get("model_sources_schema") == MODEL_SOURCE_SCHEMA:
        loaded = hashes["oracle_loaded_sources"]
        sources = launch.get("model_sources_sha256")
        require(isinstance(loaded, dict) and isinstance(sources, dict),
                "missing bound native import closure")
        for name, expected in loaded.items():
            require(sources.get(name) == expected,
                    f"launch/verifier model dependency mismatch: {name}")
    return dict(status="PASS", path=str(report_path), sha256=digest(report_path),
                scope="saved report bound to artifacts; native oracle not rerun")


def input_identity(run, launch, native):
    """Historical hashes remain evidence; changed/missing files forbid reuse."""
    rows = {name: value for name, value in native.get("assets", {}).items()
            if value.get("path")}
    rows["gem5"] = dict(path=launch["inputs"]["gem5"],
                        sha256=launch["gem5_sha256"])
    require({"kernel", "bootloader", "initrd", "gem5"} <= rows.keys(),
            "incomplete input identity")
    errors = []
    for name, key in (("profile", "profile_sha256"), ("original_kernel", "original_kernel_sha256")):
        rows[name] = dict(path=launch["inputs"].get("profile" if name == "profile" else "kernel"),
                          sha256=launch.get(key))
    for name, item in rows.items():
        try:
            require(isinstance(item["sha256"], str)
                    and re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None,
                    f"invalid input digest: {name}")
            require(digest(item["path"]) == item["sha256"], f"changed input: {name}")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(str(exc))
    hashes = {name: item["sha256"] for name, item in rows.items()}
    for name, launch_key in (("initrd", "guest_initrd_sha256"), ("bootloader", "bootloader_sha256")):
        if not launch.get(launch_key) or launch[launch_key] != hashes[name]:
            errors.append(f"launch/native identity mismatch: {name}")
    original = native.get("original_kernel")
    if original is not None:
        try:
            require(original["sha256"] == launch.get("original_kernel_sha256")
                    and digest(original["path"]) == original["sha256"],
                    "launch/native identity mismatch: original kernel")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(str(exc))
    try:
        hashes["readfile"] = digest(native["readfile"])
        require(launch.get("readfile_sha256") == hashes["readfile"]
                and digest(run / "guest-init.sh") == hashes["readfile"],
                "missing or mismatched launch-bound readfile identity")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(str(exc))
    return hashes, errors


def model_provenance(launch, native):
    """Check recorded provenance without upgrading or rewriting past launches.

    This validates the supported capture contract and its files offline, not a
    replay of Python imports or a complete dynamic-linker dependency closure.
    """
    if not {"model_sources_schema", "model_sources_sha256"} & launch.keys():
        return dict(status="NOT_RECORDED", scope="HISTORICAL_LIMITED",
                    reason="launch predates model dependency provenance")
    try:
        require(type(launch.get("model_sources_schema")) is int
                and launch["model_sources_schema"] == MODEL_SOURCE_SCHEMA,
                "unsupported or missing model source schema")
        sources = launch.get("model_sources_sha256")
        require(isinstance(sources, dict) and sources, "missing model source map")
        for name, expected in sources.items():
            require(isinstance(name, str) and Path(name).is_absolute()
                    and str(Path(name).resolve()) == name,
                    f"noncanonical model source path: {name}")
            require(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected),
                    f"invalid model source digest: {name}")
        suffix = "/configs/zena_cmn/run_fs.py"
        roots = [Path(name[:-len(suffix)]) for name in sources if name.endswith(suffix)]
        require(len(roots) == 1, "model source map needs one AP configuration root")
        root = roots[0]
        required = {str((root / name).resolve()) for name in MODEL_SOURCE_REQUIRED}
        required.update(str(path.resolve()) for path in (root / "configs/zena_cmn").rglob("*.py"))
        require(required <= sources.keys(),
                f"incomplete model source coverage: {sorted(required - sources.keys())}")
        require(any(Path(name).parts[-2:] == ("yaml", "__init__.py") for name in sources),
                "model source map lacks native YAML parser")
        require(isinstance(native.get("source_sha256"), dict) and native["source_sha256"],
                "missing native source identity")
        for name, expected in native["source_sha256"].items():
            require(sources.get(str((root / name).resolve())) == expected,
                    f"launch/native model source mismatch: {name}")
        for name, expected in sources.items():
            require(digest(name) == expected, f"changed model dependency: {name}")
        return dict(status="PASS", scope="DEPENDENCY_BOUND", schema=MODEL_SOURCE_SCHEMA,
                    source_count=len(sources),
                    binding="recorded native import closure and AP configuration inputs; files rehashed offline")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return dict(status="FAIL", scope="DEPENDENCY_UNVERIFIED", reason=str(exc))


def guest_result(console, marker):
    rows = [json.loads(line.split(marker, 1)[1]) for line in console.splitlines()
            if line.startswith(marker)]
    require(len(rows) == 1 and rows[0].get("result") == "PASS",
            "one passing guest result is required")
    require(rows[0].get("host", False) is False, "host execution is not a gem5 ROI")
    return rows[0]


def inspect_run(directory, *, config_verification=None):
    run = Path(directory).resolve()
    record = dict(run=str(run), execution_status="NOT_RUN", source_status=None,
                  measurement_validity="NOT_EVALUATED", reasons=[], metrics={},
                  readiness_scope="NOT_EVALUATED",
                  configuration_verification={"status": "NOT_RUN"})
    if not (run / "result.json").is_file():
        record["reasons"].append("missing result.json")
        return record
    try:
        record["artifact_hashes"] = {str(path.relative_to(run)): digest(path)
            for path in (run / "launch.json", run / "result.json", run / "guest-init.sh",
                         run / "m5out/manifest.json", run / "m5out/config.json",
                         run / "m5out/resolved-profile.json", run / "m5out/roi-events.json",
                         run / "m5out/roi-summary.json", run / "m5out/stats.txt",
                         run / "m5out/system.platform.terminal") if path.is_file()}
        result = read_json(run / "result.json")
        status = result.get("status")
        record["source_status"] = status
        record["execution_status"] = ("TIMEOUT" if result.get("timeout") is True
                                      else status if status in STATUSES else "UNSUPPORTED")
        record["qualification"] = result.get("qualification", "UNQUALIFIED")
        if record["execution_status"] != "PASS":
            record["reasons"].append("execution did not complete a passing workload")
            return record
        require(result.get("returncode") == 0 and result.get("timeout") is False,
                "passing result lacks normal process completion")
        launch = read_json(run / "launch.json")
        native = read_json(run / "m5out/manifest.json")
        config = read_json(run / "m5out/config.json")
        profile = read_json(run / "m5out/resolved-profile.json")
        canonical = canonical_config(config, run)
        inputs, input_errors = input_identity(run, launch, native)
        record["identity"] = dict(
            inputs=inputs, source_sha256=native.get("source_sha256"),
            model_sources_schema=launch.get("model_sources_schema"),
            model_sources_sha256=launch.get("model_sources_sha256"),
            raw_config_sha256=digest(run / "m5out/config.json"),
            canonical_config_sha256=json_digest(canonical),
            normalization=NORMALIZATION, profile=profile,
            canonical_config=canonical,
            readfile_identity_scope="launch hash must bind native readfile and guest-init.sh for readiness",
        )
        record["input_integrity"] = dict(status="FAIL" if input_errors else "PASS",
                                         errors=input_errors)
        record["model_provenance"] = model_provenance(launch, native)
        record["readiness_scope"] = record["model_provenance"]["scope"]
        report = Path(config_verification) if config_verification else run / "m5out/config-verification.json"
        try:
            record["configuration_verification"] = saved_verification(run, report, launch, native)
        except (ValueError, OSError, KeyError, TypeError) as exc:
            record["configuration_verification"] = dict(status="FAIL", reason=str(exc))
        console_path = run / "m5out/system.platform.terminal"
        console = console_path.read_text(errors="replace").replace("\r", "")
        # Built-in cache/dram guests exit gem5 directly after their checked result.
        # Other workloads return through the shell and must retain its exit marker.
        if launch.get("workload") not in ("cache", "dram"):
            require("APOLLO_WORKLOAD_EXIT=0\n" in console,
                    "missing guest workload completion marker")
        events = read_json(run / "m5out/roi-events.json")
        require([row["phase"] for row in events] == ["warmup", "roi_begin", "roi_end"],
                "incomplete or ambiguous ROI lifecycle")
        begin, end = events[1]["tick"], events[2]["tick"]
        require(type(events[0]["tick"]) is int and 0 <= events[0]["tick"] < begin
                and all("case_id" not in event for event in events), "invalid O3 warmup lifecycle")
        stats, indices, online = benchmark.roi_statistics(run / "m5out", begin, end)
        require(not online, "offline DSE requires fixed-clock single-window ROI")
        frequency = stats.get("simFreq")
        require(finite(frequency, positive=True), "missing valid simFreq")
        seconds = (end - begin) / frequency
        workload = launch.get("workload")
        if workload in ("cache", "dram"):
            guest = guest_result(console, "APOLLO_BENCH_RESULT ")
            measured = benchmark.summarize(run / "m5out", console_path,
                                          mode=workload, size_bytes=guest["working_set_bytes"],
                                          passes=guest["passes"], warmup_passes=guest["warmup_passes"])
            require(measured == result.get("measurement"), "stored measurement differs from raw evidence")
        elif workload == "dram-multicore":
            guest = guest_result(console, "CMN_RESULT ")
            measured = benchmark.summarize_block(stats, console, begin, end, indices[0])
            stored = result.get("measurement", {})
            for key in ("guest", "roi", "application", "dram"):
                require(measured[key] == stored.get(key), f"stored {key} differs from raw evidence")
            summary_path = run / "m5out/roi-summary.json"
            if summary_path.is_file():
                summary = read_json(summary_path)
                require(all(summary.get(key) == measured[key] for key in
                            ("guest", "roi", "application", "dram")),
                        "roi-summary.json differs from raw evidence")
            require(guest.get("initialization_before_switch") is True,
                    "memory workload did not initialize before switch")
            require(type(guest.get("warmup_passes")) is int and guest["warmup_passes"] > 0,
                    "missing actual warmup")
            require(type(guest.get("workers")) is int and 1 <= guest["workers"] <= profile["cpu"]["cores"],
                    "invalid active worker count")
            mode = guest["benchmark"]
            arrays = {"read": 1, "copy": 2, "stream": 3}[mode]
            for key in ("working_set_bytes", "useful_bytes", "checksum", "warmup_checksum"):
                require(type(guest.get(key)) is int and guest[key] >= 0, f"invalid memory field: {key}")
            require(guest["working_set_bytes"] > 0, "empty memory workload")
            if "memory_mode" in launch:
                require(mode == {"triad": "stream"}.get(launch["memory_mode"], launch["memory_mode"]),
                        "guest memory mode differs from launch")
            require(guest["working_set_bytes"] % arrays == 0 and type(guest["passes"]) is int
                    and guest["passes"] > 0, "invalid memory workload dimensions")
            require(guest["useful_bytes"] == guest["working_set_bytes"] * guest["passes"],
                    "incorrect useful byte count")
            expected_checksum = guest["working_set_bytes"] * guest["passes"] // 8 if mode == "read" else 0
            require(guest["checksum"] == expected_checksum, "memory checksum mismatch")
            require(guest["warmup_checksum"] == (guest["working_set_bytes"] * guest["warmup_passes"] // 8
                                                  if mode == "read" else 0), "warmup checksum mismatch")
            require(guest.get("kernel") == ("neon" if mode == "read" else "scalar")
                    and guest.get("affinity") == "0..workers-1"
                    and guest.get("channel_phase_spread") is False,
                    "unexpected memory kernel/placement")
            channels = measured["dram"]["channels"]
            require(len(channels) == profile["memory"]["channels"], "missing memory channel")
            require(all(finite(row.get(direction)) for row in channels.values()
                        for direction in ("Read", "Written")), "missing or invalid memory channel counter")
            require(all(finite(row.get("Read"), positive=True) for row in channels.values()),
                    "missing memory channel read traffic")
            if mode != "read":
                require(all(finite(row.get("Written"), positive=True) for row in channels.values()),
                        "missing memory channel write traffic")
        elif workload == "command" and any(line.startswith("APOLLO_IMAGE_RESULT ")
                                            for line in console.splitlines()):
            from image_summary import summarize_image
            guest = guest_result(console, "APOLLO_IMAGE_RESULT ")
            measured = summarize_image(run / "m5out", console_path)
            require(measured == result.get("measurement"), "stored image measurement differs from raw evidence")
            workload = "image"
        else:
            raise ValueError(f"unsupported measured workload: {workload}")
        workers = guest.get("workers", 1)
        cpus = (list(range(workers)) if workload == "dram-multicore" else
                [int(cpu) for cpu in measured["worker_committed_instructions"]] if workload == "image" else [0])
        configured = {cpu["cpu_id"]: cpu for cpu in config["system"]["roi_cpu"]}
        # ArmO3CPU inherits its serialized SimObject type from BaseO3CPU.
        require(native.get("roi_cpu") == "ArmO3CPU"
                and len(configured) == len(config["system"]["roi_cpu"])
                and all(cpu in configured and configured[cpu]["type"] in ("BaseO3CPU", "ArmO3CPU") for cpu in cpus),
                "active worker is not a configured O3 CPU")
        committed = {}
        for name, value in stats.items():
            match = re.fullmatch(r"system\.roi_cpu(\d+)\.commitStats0\.numInsts", name)
            if match:
                cpu = int(match[1])
                require(cpu not in committed, "ambiguous O3 instruction counters")
                committed[cpu] = value
        require(all(finite(committed.get(cpu), positive=True) for cpu in cpus),
                "missing O3 execution on an active core")
        record["workload"] = {"kind": workload, **{key: guest[key] for key in WORKLOAD_FIELDS if key in guest}}
        record["roi"] = dict(begin_tick=begin, end_tick=end, seconds=seconds,
                             stats_block_index=indices[0])
        metrics = record["metrics"]
        metrics["roi_seconds"] = metric(seconds, "s")
        useful = guest.get("useful_bytes")
        if finite(useful):
            metrics["useful_GB_s"] = metric(useful / seconds / 1e9, "GB/s")
        reads = [value for name, value in stats.items() if name.endswith(".dramBytesRead")]
        writes = [value for name, value in stats.items() if name.endswith(".dramBytesWritten")]
        if reads and writes and all(finite(value) for value in reads + writes):
            total = sum(reads) + sum(writes)
            metrics["dram_GB_s"] = metric(total / seconds / 1e9, "GB/s")
            if finite(useful, positive=True):
                metrics["dram_to_useful_ratio"] = metric(total / useful, "ratio")
        if finite(guest.get("dependent_loads"), positive=True):
            metrics["ns_per_dependent_load"] = metric(seconds * 1e9 / guest["dependent_loads"], "ns/load")
        if workload == "image":
            application = measured["application"]
            samples = application["frame_latency_ns"]["sample_count"]
            for field, statistic in (("observed_max", "max"), ("median", "median")):
                metrics[f"frame_latency_{statistic}_ns"] = metric(
                    application["frame_latency_ns"][field], "ns", statistic=statistic,
                    samples=samples, sample_definition="completed-frame")
            metrics["foreground_frames_per_second"] = metric(application["foreground_frames_per_second"], "frame/s")
            record["sample_scope"] = "observed frames only; maximum is not WCET or a population tail bound"
        record["measurement_validity"] = "VALID"
    except (ValueError, OSError, KeyError, TypeError, IndexError, ZeroDivisionError, ImportError) as exc:
        record["measurement_validity"] = "INVALID"
        record["reasons"].append(str(exc))
    return record


UNITS = {
    "ns": ("time", 1e-9), "us": ("time", 1e-6), "ms": ("time", 1e-3), "s": ("time", 1),
    "B/s": ("bandwidth", 1), "MB/s": ("bandwidth", 1e6), "GB/s": ("bandwidth", 1e9),
    "frame/s": ("frame/s", 1), "bytes": ("bytes", 1), "count": ("count", 1),
    "ratio": ("ratio", 1), "ns/load": ("ns/load", 1),
}


def evaluate_target(target, observation, *, valid=True):
    answer = dict(target=target.get("id"), status="UNDECIDED")
    try:
        for key in ("id", "version", "scenario", "metric", "statistic", "unit", "comparator",
                    "sample_definition", "confidence_policy", "basis", "owner"):
            require(isinstance(target.get(key), str) and bool(target[key]), f"missing target {key}")
        require(valid and observation is not None, "missing valid measurement/config/input evidence")
        require(target["comparator"] in ("<=", ">="), "unsupported comparator")
        for key in ("statistic", "sample_definition", "confidence_policy"):
            require(observation.get(key) == target[key], f"{key} mismatch")
        require(type(target.get("min_samples")) is int and target["min_samples"] > 0,
                "missing minimum sample policy")
        require(type(observation.get("samples")) is int and observation["samples"] >= target["min_samples"],
                "insufficient samples")
        value, limit, margin = observation["value"], target.get("limit"), target.get("margin")
        require(all(finite(v) for v in (value, limit, margin)), "invalid value/limit/margin")
        source, dest = UNITS[observation["unit"]], UNITS[target["unit"]]
        require(source[0] == dest[0], "unit dimension mismatch")
        # Decimal preserves explicitly stated equality boundaries after conversion.
        value = Decimal(str(value)) * Decimal(str(source[1])) / Decimal(str(dest[1]))
        limit, margin = Decimal(str(limit)), Decimal(str(margin))
        upper = target["comparator"] == "<="
        require(not upper or margin < 1, "upper-bound margin must be below one")
        if limit == 0:
            require(isinstance(target.get("absolute_rule"), str) and target["absolute_rule"]
                    and finite(target.get("absolute_threshold")) and margin == 0,
                    "zero-limit target requires explicit absolute rule and zero ratio margin")
            threshold = Decimal(str(target["absolute_threshold"]))
            headroom = None
        else:
            threshold = limit * (1 - margin if upper else 1 + margin)
            headroom = 1 - value / limit if upper else value / limit - 1
        require(math.isfinite(threshold), "nonfinite target threshold")
        require(headroom is None or math.isfinite(headroom), "nonfinite target headroom")
        answer.update(status="MEETS" if (value <= threshold if upper else value >= threshold)
                      else "DOES_NOT_MEET", value=float(value), unit=target["unit"],
                      threshold=float(threshold), nominal_headroom=float(headroom) if headroom is not None else None)
    except (ValueError, KeyError, TypeError) as exc:
        answer["reason"] = str(exc)
    return answer


def convergence(before, after, relative_tolerance, absolute_tolerance=None):
    require(finite(before) and finite(after) and finite(relative_tolerance), "invalid convergence input")
    if before == 0:
        require(absolute_tolerance is None or finite(absolute_tolerance), "invalid absolute tolerance")
        return dict(status="UNDECIDED" if absolute_tolerance is None else
                    "PASS" if abs(after - before) <= absolute_tolerance else "FAIL",
                    relative_change=None, absolute_change=after - before)
    delta = (after - before) / before
    return dict(status="PASS" if abs(delta) <= relative_tolerance else "FAIL", relative_change=delta)


def case_ready(record):
    return (record.get("execution_status") == "PASS" and record.get("measurement_validity") == "VALID"
            and record.get("input_integrity", {}).get("status") == "PASS"
            and record.get("model_provenance", {}).get("status") == "PASS"
            and record.get("identity", {}).get("model_sources_schema") == MODEL_SOURCE_SCHEMA
            and bool(record.get("identity", {}).get("model_sources_sha256"))
            and record.get("configuration_verification", {}).get("status") == "PASS")


def compare_cases(before, after, specification):
    answer = dict(id=specification["id"], status="UNDECIDED")
    try:
        require(specification.get("kind", "comparison") in ("comparison", "convergence"),
                "unsupported comparison kind")
        require(case_ready(before) and case_ready(after), "comparison lacks valid bound evidence")
        require(before["identity"]["source_sha256"] == after["identity"]["source_sha256"],
                "model sources differ")
        require(before["identity"]["model_sources_schema"] == after["identity"]["model_sources_schema"]
                and before["identity"]["model_sources_sha256"] == after["identity"]["model_sources_sha256"],
                "model dependency provenance differs")
        deltas = {}
        for name, a, b in (("profile", before["identity"]["profile"], after["identity"]["profile"]),
                           ("config", before["identity"]["canonical_config"], after["identity"]["canonical_config"]),
                           ("inputs", before["identity"]["inputs"], after["identity"]["inputs"]),
                           ("workload", before["workload"], after["workload"])):
            delta = changed(a, b)
            allowed = specification.get("allowed_" + name + "_changes", [])
            require(isinstance(allowed, list) and all(isinstance(v, str) for v in allowed),
                    "invalid declared change list")
            require(set(delta) <= set(allowed), f"undeclared {name} changes: {sorted(set(delta) - set(allowed))}")
            deltas[name] = delta
        if specification.get("kind") == "convergence":
            require(not deltas["profile"] and not deltas["config"]
                    and set(deltas["inputs"]) <= {"readfile"},
                    "convergence cannot change hardware or executable inputs")
            require(set(deltas["workload"]) <= {"passes", "warmup_passes", "frames"},
                    "convergence must retain workload dimensions and placement")
            require(len(deltas["workload"]) == 1, "convergence must increase one sampling/warmup dimension")
            count = next(iter(deltas["workload"].values()))
            require(type(count["before"]) is int and type(count["after"]) is int
                    and 0 < count["before"] < count["after"], "convergence requires an increased loop count")
        metrics = {}
        for name in specification["metrics"]:
            first, second = before["metrics"][name], after["metrics"][name]
            require(all(first[k] == second[k] for k in ("unit", "statistic", "sample_definition", "confidence_policy")),
                    f"incompatible metric: {name}")
            row = dict(before=first["value"], after=second["value"], unit=first["unit"],
                       relative_change=None if first["value"] == 0 else second["value"] / first["value"] - 1)
            if specification.get("kind") == "convergence":
                require(name in ("useful_GB_s", "dram_GB_s", "dram_to_useful_ratio", "ns_per_dependent_load",
                                 "foreground_frames_per_second", "frame_latency_median_ns"),
                        "convergence requires a normalized metric")
                row.update(convergence(first["value"], second["value"], specification["relative_tolerance"],
                                       specification.get("absolute_tolerance")))
            metrics[name] = row
        require(metrics, "comparison has no metrics")
        answer.update(status="PASS", changes=deltas, metrics=metrics)
        if specification.get("kind") == "convergence":
            states = {row["status"] for row in metrics.values()}
            answer["status"] = "FAIL" if "FAIL" in states else "UNDECIDED" if "UNDECIDED" in states else "PASS"
    except (ValueError, KeyError, TypeError) as exc:
        answer["reason"] = str(exc)
    return answer


def candidate_consistency(records):
    """A candidate names one hardware/source/input configuration across scenarios."""
    known = [row for row in records if row.get("identity")]
    missing = [row["id"] for row in records if not row.get("identity")]
    differences = {}
    if known:
        baseline = known[0]

        def identity(row):
            value = row["identity"]
            return dict(profile=value["profile"], config=value["canonical_config"],
                        source_sha256=value["source_sha256"],
                        model_sources_schema=value.get("model_sources_schema"),
                        model_sources_sha256=value.get("model_sources_sha256"),
                        inputs={key: digest for key, digest in value["inputs"].items()
                                if key != "readfile"})

        for row in known[1:]:
            delta = changed(identity(baseline), identity(row))
            if delta:
                differences[row["id"]] = delta
    return dict(status="FAIL" if differences else "UNDECIDED" if missing else "PASS",
                reference_case=known[0]["id"] if known else None,
                differences=differences, missing_identity=missing)


def campaign_report(campaign, base):
    require(type(campaign.get("schema")) is int and campaign["schema"] == 1
            and isinstance(campaign.get("id"), str) and campaign["id"], "invalid campaign schema/id")
    cases = campaign["cases"]
    require(isinstance(cases, list) and cases, "campaign requires cases")
    ids = [row["id"] for row in cases]
    require(len(set(ids)) == len(ids), "duplicate case ID")
    scenarios = campaign.get("required_scenarios", [])
    require(isinstance(scenarios, list) and len(set(scenarios)) == len(scenarios)
            and all(isinstance(s, str) and s for s in scenarios), "invalid required scenarios")
    targets = campaign.get("targets", [])
    target_ids = [target["id"] for target in targets]
    require(len(set(target_ids)) == len(target_ids), "duplicate target ID")
    require(all(target.get("scenario") in scenarios for target in targets),
            "every target scenario must be listed in required_scenarios")
    records = {}
    for case in cases:
        require(all(isinstance(case.get(key), str) and case[key] for key in ("id", "candidate", "scenario", "run")),
                "incomplete case identity")
        report = case.get("config_verification")
        record = inspect_run(Path(base) / case["run"],
                             config_verification=Path(base) / report if report else None)
        record.update(id=case["id"], candidate=case["candidate"], scenario=case["scenario"])
        if (record["execution_status"] == "PASS"
                and record["measurement_validity"] == "VALID"):
            workload = record.get("workload", {})
            for key, expected in case.get("workload_contract", {}).items():
                actual = workload.get(key)
                if key not in workload or type(actual) is not type(expected) or actual != expected:
                    record["measurement_validity"] = "INVALID"
                    record["reasons"].append(f"requested workload mismatch: {key}")
        record["targets"] = [evaluate_target(t, record["metrics"].get(t.get("metric")), valid=case_ready(record))
                             for t in targets if t.get("scenario") == case["scenario"]]
        records[case["id"]] = record
    decisions = []
    for candidate in sorted({case["candidate"] for case in cases}):
        group = [row for row in records.values() if row["candidate"] == candidate]
        evaluated = [target for row in group for target in row["targets"]]
        states = {row["status"] for row in evaluated}
        missing = sorted(set(scenarios) - {row["scenario"] for row in group})
        untargeted = sorted(set(scenarios) - {t.get("scenario") for t in targets})
        consistency = candidate_consistency(group)
        if consistency["status"] == "FAIL":
            decision = "UNDECIDED"
        elif "DOES_NOT_MEET" in states:
            decision = "MODEL_INFEASIBLE"
        elif not targets:
            decision = "UNDECIDED"
        elif (missing or untargeted or not scenarios or "UNDECIDED" in states
              or not evaluated or consistency["status"] != "PASS"):
            decision = "UNDECIDED"
        else:
            # Runtime metrics alone cannot prove model robustness or physical feasibility.
            decision = "CONDITIONAL"
        decisions.append(dict(candidate=candidate, decision=decision,
                              identity_consistency=consistency,
                              assessment_scope="EXPLORATORY" if not targets else "DECLARED_TARGETS",
                              missing_scenarios=missing, scenarios_without_targets=untargeted,
                              cost_decision="UNDECIDED", reason=("candidate hardware/source/input identity differs across cases"
                                  if consistency["status"] == "FAIL" else
                                  "PPA/robustness/IP evidence requires separate assessment")))
    comparisons = [compare_cases(records[row["baseline"]], records[row["candidate"]], row)
                   for row in campaign.get("comparisons", [])]
    return dict(schema=1, id=campaign["id"], qualification="MODEL_EXPLORATION_NOT_SILICON",
                cases=list(records.values()), comparisons=comparisons, decisions=decisions,
                targets=targets, required_scenarios=scenarios)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    inventory = commands.add_parser("inventory", help="inspect existing runs without changing them")
    inventory.add_argument("runs", nargs="+", type=Path)
    inventory.add_argument("--output", required=True, type=Path)
    report = commands.add_parser("report", help="evaluate an explicit campaign JSON")
    report.add_argument("campaign", type=Path)
    report.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    require(not args.output.exists(), "output already exists")
    if args.action == "inventory":
        result = dict(schema=1, runs=[inspect_run(path) for path in args.runs])
    else:
        result = campaign_report(read_json(args.campaign), args.campaign.resolve().parent)
        result["campaign_sha256"] = digest(args.campaign)
    with args.output.open("x") as output:
        json.dump(result, output, indent=2, allow_nan=False)
        output.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"soc-spec: {error}")
