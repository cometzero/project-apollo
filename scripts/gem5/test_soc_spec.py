# SPDX-License-Identifier: BSD-3-Clause
"""Offline decision tests; no native gem5, compiler or simulator is invoked."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

import benchmark
import soc_spec as spec


def write_json(path, value):
    path.write_text(json.dumps(value))


def target(**updates):
    value = dict(id="exploratory-latency", version="1", scenario="alone",
                 metric="ns_per_dependent_load", statistic="aggregate", comparator="<=",
                 limit=20, unit="ns/load", min_samples=1, margin=0.1,
                 sample_definition="completed-roi", confidence_policy="observed",
                 basis="synthetic test fixture, not a product target", owner="test")
    value.update(updates)
    return value


def fixture(run, *, port=3456, model_root=None):
    """Write realistic tiny multicore raw evidence, not self-attested metrics."""
    out = run / "m5out"
    out.mkdir(parents=True)
    for name in ("gem5", "kernel", "original-kernel", "bootloader", "initrd"):
        (run / name).write_text(name)
    (run / "input-profile.yaml").write_text("cpu:\n  clock: 1GHz\n")
    (run / "guest-init.sh").write_text("apollo-bench --mode read --passes 2\n")
    model_root = model_root or run.parent / "model-sources"
    model_paths = (*spec.MODEL_SOURCE_REQUIRED, "configs/zena_cmn/model.py",
                   "native-python/yaml/__init__.py", "native-python/collections/__init__.py")
    for name in model_paths:
        path = model_root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text("fixture dependency: " + name)
    sources = {str((model_root / name).resolve()): spec.digest(model_root / name)
               for name in model_paths}
    source = {"configs/zena_cmn/model.py": spec.digest(model_root / "configs/zena_cmn/model.py")}
    native = dict(source_sha256=source, roi_cpu="ArmO3CPU", readfile=str(run / "guest-init.sh"),
                  original_kernel=dict(path=str(run / "original-kernel"),
                      sha256=spec.digest(run / "original-kernel"), wrapped_image=True),
                  assets={name: dict(path=str(run / name), sha256=spec.digest(run / name))
                          for name in ("kernel", "bootloader", "initrd")})
    write_json(out / "manifest.json", native)
    launch = dict(workload="dram-multicore", inputs=dict(gem5=str(run / "gem5"),
                      kernel=str(run / "original-kernel"), profile=str(run / "input-profile.yaml")),
                  gem5_sha256=spec.digest(run / "gem5"),
                  readfile_sha256=spec.digest(run / "guest-init.sh"),
                  guest_initrd_sha256=spec.digest(run / "initrd"),
                  bootloader_sha256=spec.digest(run / "bootloader"),
                  original_kernel_sha256=spec.digest(run / "original-kernel"),
                  model_sources_schema=1, model_sources_sha256=sources,
                  profile_sha256=spec.digest(run / "input-profile.yaml"))
    write_json(run / "launch.json", launch)
    config = dict(system=dict(platform=dict(terminal=dict(port=port)),
                              roi_cpu=[dict(cpu_id=0, type="BaseO3CPU")],
                              readfile=str(run / "guest-init.sh"), clock=1000))
    write_json(out / "config.json", config)
    write_json(out / "resolved-profile.json", dict(cpu=dict(cores=1), memory=dict(channels=2)))
    (out / "system.dtb").write_bytes(b"tiny dtb fixture")
    guest = dict(result="PASS", benchmark="read", kernel="neon", workers=1, passes=2,
                 working_set_bytes=4096, useful_bytes=8192, checksum=1024,
                 warmup_passes=1, warmup_checksum=512, initialization_before_switch=True,
                 channel_phase_spread=False, affinity="0..workers-1")
    serial = "CMN_RESULT " + json.dumps(guest) + "\nAPOLLO_WORKLOAD_EXIT=0\n"
    (out / "system.platform.terminal").write_text(serial)
    write_json(out / "roi-events.json", [dict(phase="warmup", tick=100),
               dict(phase="roi_begin", tick=1000), dict(phase="roi_end", tick=3000)])
    stats = dict(simFreq=1000000000000, simTicks=2000, finalTick=3000,
                 **{"system.roi_cpu0.commitStats0.numInsts": 100,
                    "system.mem_ctrls0.dram.dramBytesRead": 4096,
                    "system.mem_ctrls0.dram.dramBytesWritten": 0,
                    "system.mem_ctrls1.dram.dramBytesRead": 4096,
                    "system.mem_ctrls1.dram.dramBytesWritten": 0})
    (out / "stats.txt").write_text(
        "---------- Begin Simulation Statistics ----------\n"
        + "".join(f"{key} {value}\n" for key, value in stats.items())
        + "---------- End Simulation Statistics ----------\n")
    measurement = benchmark.summarize_block(stats, serial, 1000, 3000, 0)
    write_json(out / "roi-summary.json", measurement)
    write_json(run / "result.json", dict(status="PASS", returncode=0, timeout=False,
               qualification="UNCALIBRATED_PROXY", measurement=measurement))
    write_json(out / "config-verification.json", dict(status="PASS", failures=[],
               device_tree=dict(status="PASS"), artifact_hashes={
                   **{name: spec.digest(out / name) for name in
                      ("config.json", "resolved-profile.json", "system.dtb")},
                   **source, "gem5": launch["gem5_sha256"], "verifier": "2" * 64,
                   "oracle": "3" * 64, "oracle_loaded_sources": sources}))
    return run


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run = fixture(self.root / "run")

    def test_builtin_cache_exits_directly_without_shell_marker(self):
        launch = spec.read_json(self.run / "launch.json")
        launch["workload"] = "cache"
        write_json(self.run / "launch.json", launch)
        config_path = self.run / "m5out/config.json"
        config = spec.read_json(config_path)
        cache = lambda name: {"cache": {"path": name}}
        config["system"].update(cpu=[dict(cpu_id=0, l1d=cache("l1"), l2=cache("l2"))],
                                ruby=dict(rnf=[dict(dsu_l3=cache("l3"))],
                                          hnf=[dict(cntrl=cache("slc"))]))
        write_json(config_path, config)
        verification = self.run / "m5out/config-verification.json"
        checked = spec.read_json(verification)
        checked["artifact_hashes"]["config.json"] = spec.digest(config_path)
        write_json(verification, checked)
        serial = self.run / "m5out/system.platform.terminal"
        guest = dict(mode="cache", result="PASS", working_set_bytes=4096,
                     passes=2, warmup_passes=1, useful_bytes=1024,
                     dependent_loads=128, checksum=2, expected=2, host=False)
        serial.write_text("APOLLO_BENCH_RESULT " + json.dumps(guest) + "\n")
        measured = benchmark.summarize(self.run / "m5out", serial,
                                       mode="cache", size_bytes=4096, passes=2)
        result = spec.read_json(self.run / "result.json")
        result["measurement"] = measured
        write_json(self.run / "result.json", result)
        row = spec.inspect_run(self.run)
        self.assertTrue(spec.case_ready(row), row)
        guest["checksum"] = 0
        serial.write_text("APOLLO_BENCH_RESULT " + json.dumps(guest) + "\n")
        self.assertEqual(spec.inspect_run(self.run)["measurement_validity"], "INVALID")

    def test_shell_workload_still_requires_completion_marker(self):
        serial = self.run / "m5out/system.platform.terminal"
        serial.write_text(serial.read_text().replace("APOLLO_WORKLOAD_EXIT=0\n", ""))
        self.assertIn("missing guest workload completion marker", spec.inspect_run(self.run)["reasons"])

    def test_raw_evidence_validates_without_modification(self):
        before = {str(p): spec.digest(p) for p in self.run.rglob("*") if p.is_file()}
        row = spec.inspect_run(self.run)
        self.assertEqual(row["measurement_validity"], "VALID", row)
        self.assertTrue(spec.case_ready(row), row)
        self.assertEqual(row["model_provenance"]["status"], "PASS")
        self.assertEqual(row["readiness_scope"], "DEPENDENCY_BOUND")
        self.assertEqual(row["identity"]["model_sources_sha256"],
                         spec.read_json(self.run / "launch.json")["model_sources_sha256"])
        self.assertAlmostEqual(row["metrics"]["useful_GB_s"]["value"], 4096)
        self.assertEqual(row["metrics"]["dram_to_useful_ratio"]["value"], 1)
        self.assertIn("m5out/roi-summary.json", row["artifact_hashes"])
        self.assertEqual(before, {str(p): spec.digest(p) for p in self.run.rglob("*") if p.is_file()})

    def test_legacy_provenance_keeps_raw_history_without_automatic_upgrade(self):
        launch_path = self.run / "launch.json"
        launch = spec.read_json(launch_path)
        del launch["model_sources_schema"]
        del launch["model_sources_sha256"]
        write_json(launch_path, launch)
        before = {str(p): spec.digest(p) for p in self.root.rglob("*") if p.is_file()}
        row = spec.inspect_run(self.run)
        self.assertEqual(row["measurement_validity"], "VALID")
        self.assertEqual(row["input_integrity"]["status"], "PASS")
        self.assertEqual(row["model_provenance"]["status"], "NOT_RECORDED")
        self.assertEqual(row["readiness_scope"], "HISTORICAL_LIMITED")
        self.assertIsNone(row["identity"]["model_sources_sha256"])
        self.assertFalse(spec.case_ready(row))
        self.assertEqual(before, {str(p): spec.digest(p) for p in self.root.rglob("*") if p.is_file()})

    def test_external_dependencies_are_bound_and_never_rewritten(self):
        launch = spec.read_json(self.run / "launch.json")
        before = {str(p): spec.digest(p) for p in self.run.rglob("*") if p.is_file()}
        for suffix in ("configs/ruby/CHI_config.py", "configs/topologies/CustomMesh.py",
                       "configs/zena_cmn/profiles/default.yaml", "native-python/yaml/__init__.py"):
            with self.subTest(dependency=suffix):
                path = next(Path(name) for name in launch["model_sources_sha256"] if name.endswith(suffix))
                original = path.read_text()
                path.write_text(original + "\nchanged after execution\n")
                row = spec.inspect_run(self.run)
                self.assertEqual(row["measurement_validity"], "VALID")
                self.assertEqual(row["model_provenance"]["status"], "FAIL", row)
                self.assertIn("changed model dependency", row["model_provenance"]["reason"])
                self.assertEqual(row["readiness_scope"], "DEPENDENCY_UNVERIFIED")
                self.assertFalse(spec.case_ready(row))
                path.write_text(original)
        self.assertEqual(before, {str(p): spec.digest(p) for p in self.run.rglob("*") if p.is_file()})

    def test_new_provenance_requires_supported_complete_native_bound_map(self):
        path = self.run / "launch.json"
        original = spec.read_json(path)
        variants = []
        for key in ("model_sources_schema", "model_sources_sha256"):
            value = copy.deepcopy(original)
            del value[key]
            variants.append(value)
        variants.extend({**original, "model_sources_schema": schema} for schema in (True, 2, "1"))
        variants.append({**original, "model_sources_sha256": {}})
        for suffix in (*spec.MODEL_SOURCE_REQUIRED, "configs/zena_cmn/model.py",
                       "native-python/yaml/__init__.py"):
            value = copy.deepcopy(original)
            name = next(name for name in value["model_sources_sha256"] if name.endswith(suffix))
            del value["model_sources_sha256"][name]
            variants.append(value)
        for name, expected in (("relative.py", "0" * 64),
                               (str(self.root / "not-recorded.py"), "invalid")):
            value = copy.deepcopy(original)
            value["model_sources_sha256"][name] = expected
            variants.append(value)
        for index, value in enumerate(variants):
            with self.subTest(variant=index):
                write_json(path, value)
                row = spec.inspect_run(self.run)
                self.assertEqual(row["measurement_validity"], "VALID", row)
                self.assertEqual(row["model_provenance"]["status"], "FAIL", row)
                self.assertFalse(spec.case_ready(row))
        write_json(path, original)
        native_path = self.run / "m5out/manifest.json"
        native = spec.read_json(native_path)
        native["source_sha256"]["configs/zena_cmn/model.py"] = "0" * 64
        write_json(native_path, native)
        row = spec.inspect_run(self.run)
        self.assertIn("launch/native model source mismatch", row["model_provenance"]["reason"])
        self.assertFalse(spec.case_ready(row))

    def test_saved_oracle_closure_cannot_escape_launch_provenance(self):
        launch_path = self.run / "launch.json"
        original = spec.read_json(launch_path)
        dependency = next(name for name in original["model_sources_sha256"]
                          if name.endswith("collections/__init__.py"))
        for missing in (False, True):
            with self.subTest(missing=missing):
                launch = copy.deepcopy(original)
                if missing:
                    del launch["model_sources_sha256"][dependency]
                else:
                    launch["model_sources_sha256"][dependency] = "0" * 64
                write_json(launch_path, launch)
                row = spec.inspect_run(self.run)
                self.assertEqual(row["measurement_validity"], "VALID")
                self.assertEqual(row["configuration_verification"]["status"], "FAIL")
                self.assertIn("launch/verifier model dependency mismatch",
                              row["configuration_verification"]["reason"])
                self.assertFalse(spec.case_ready(row))

    def test_ports_and_run_paths_only_are_normalized(self):
        other = fixture(self.root / "other", port=9876)
        a, b = spec.inspect_run(self.run), spec.inspect_run(other)
        self.assertNotEqual(a["identity"]["raw_config_sha256"], b["identity"]["raw_config_sha256"])
        self.assertEqual(a["identity"]["canonical_config_sha256"], b["identity"]["canonical_config_sha256"])
        config = spec.read_json(other / "m5out/config.json")
        for key, value in (("clock", 500), ("guest_address", 0x80000000)):
            with self.subTest(key=key):
                altered = copy.deepcopy(config)
                altered["system"][key] = value
                self.assertNotEqual(spec.json_digest(spec.canonical_config(config, other)),
                                    spec.json_digest(spec.canonical_config(altered, other)))

    def test_missing_and_stale_verification_do_not_qualify_metrics(self):
        report = self.run / "m5out/config-verification.json"
        report.unlink()
        row = spec.inspect_run(self.run)
        self.assertEqual(row["measurement_validity"], "VALID")
        self.assertEqual(row["configuration_verification"]["status"], "NOT_RUN")
        self.assertFalse(spec.case_ready(row))
        write_json(report, dict(status="PASS", device_tree=dict(status="PASS"), artifact_hashes={}))
        row = spec.inspect_run(self.run)
        self.assertEqual(row["configuration_verification"]["status"], "FAIL")
        self.assertFalse(spec.case_ready(row))

    def test_changed_or_missing_binary_keeps_historical_measurement_but_blocks_decision(self):
        for remove in (False, True):
            with self.subTest(remove=remove):
                binary = self.run / "gem5"
                binary.unlink() if remove else binary.write_text("changed binary")
                row = spec.inspect_run(self.run)
                self.assertEqual(row["measurement_validity"], "VALID")
                self.assertEqual(row["input_integrity"]["status"], "FAIL")
                self.assertFalse(spec.case_ready(row))

    def test_missing_roi_and_duplicate_stats_fail_closed(self):
        events = self.run / "m5out/roi-events.json"
        original = events.read_text()
        events.unlink()
        self.assertEqual(spec.inspect_run(self.run)["measurement_validity"], "INVALID")
        events.write_text(original)
        stats = self.run / "m5out/stats.txt"
        stats.write_text(stats.read_text() * 2)
        self.assertEqual(spec.inspect_run(self.run)["measurement_validity"], "INVALID")

    def test_readfile_is_bound_to_launch_without_discarding_raw_history(self):
        launch_path = self.run / "launch.json"
        launch = spec.read_json(launch_path)
        for missing in (True, False):
            with self.subTest(missing_launch_hash=missing):
                altered = copy.deepcopy(launch)
                if missing:
                    del altered["readfile_sha256"]
                else:
                    (self.run / "guest-init.sh").write_text("changed command after execution\n")
                write_json(launch_path, altered)
                row = spec.inspect_run(self.run)
                self.assertEqual(row["measurement_validity"], "VALID", row)
                self.assertEqual(row["input_integrity"]["status"], "FAIL")
                self.assertFalse(spec.case_ready(row))

        (self.run / "guest-init.sh").write_text("apollo-bench --mode read --passes 2\n")
        write_json(launch_path, {key: value for key, value in launch.items()
                                if key not in ("readfile_sha256", "original_kernel_sha256", "profile_sha256")})
        historical = spec.inspect_run(self.run)
        self.assertEqual(historical["measurement_validity"], "VALID")
        self.assertFalse(spec.case_ready(historical))

    def test_launch_assets_cross_bind_native_and_original_kernel(self):
        launch_path = self.run / "launch.json"
        launch = spec.read_json(launch_path)
        native = spec.read_json(self.run / "m5out/manifest.json")
        self.assertNotEqual(launch["original_kernel_sha256"], native["assets"]["kernel"]["sha256"])
        self.assertTrue(spec.case_ready(spec.inspect_run(self.run)))
        for key in ("guest_initrd_sha256", "bootloader_sha256", "original_kernel_sha256", "profile_sha256"):
            with self.subTest(key=key):
                write_json(launch_path, {**launch, key: "0" * 64})
                row = spec.inspect_run(self.run)
                self.assertEqual(row["measurement_validity"], "VALID")
                self.assertEqual(row["input_integrity"]["status"], "FAIL")
                self.assertFalse(spec.case_ready(row))
        write_json(launch_path, launch)
        native["original_kernel"]["sha256"] = "0" * 64
        write_json(self.run / "m5out/manifest.json", native)
        self.assertFalse(spec.case_ready(spec.inspect_run(self.run)))

    def test_invalid_write_counters_cannot_qualify_read_workload(self):
        path = self.run / "m5out/stats.txt"
        original = path.read_text()
        serial = (self.run / "m5out/system.platform.terminal").read_text()
        for value in ("-1", "nan", "missing"):
            with self.subTest(value=value):
                path.write_text("".join(line for line in original.splitlines(keepends=True)
                                        if "dramBytesWritten" not in line) if value == "missing" else
                                original.replace("dramBytesWritten 0", "dramBytesWritten " + value))
                stats, _, _ = benchmark.roi_statistics(self.run / "m5out", 1000, 3000)
                measured = benchmark.summarize_block(stats, serial, 1000, 3000, 0)
                write_json(self.run / "m5out/roi-summary.json", measured)
                write_json(self.run / "result.json", dict(status="PASS", returncode=0,
                                                         timeout=False, measurement=measured))
                row = spec.inspect_run(self.run)
                self.assertEqual(row["measurement_validity"], "INVALID", row)
                self.assertFalse(spec.case_ready(row))

    def test_checksum_and_stored_measurement_must_match(self):
        serial = self.run / "m5out/system.platform.terminal"
        original = serial.read_text()
        serial.write_text(original.replace('"checksum": 1024', '"checksum": 0'))
        self.assertEqual(spec.inspect_run(self.run)["measurement_validity"], "INVALID")
        serial.write_text(original)
        path = self.run / "result.json"
        result = spec.read_json(path)
        result["measurement"]["application"]["GB_s"] += 1
        write_json(path, result)
        self.assertEqual(spec.inspect_run(self.run)["measurement_validity"], "INVALID")

    def test_padded_cpu_index_and_missing_active_core(self):
        stats = self.run / "m5out/stats.txt"
        stats.write_text(stats.read_text().replace("roi_cpu0.", "roi_cpu00."))
        self.assertTrue(spec.case_ready(spec.inspect_run(self.run)))
        stats.write_text(stats.read_text().replace("numInsts 100", "numInsts 0"))
        self.assertEqual(spec.inspect_run(self.run)["measurement_validity"], "INVALID")

    def test_execution_statuses_preserved_and_command_exit_insufficient(self):
        path = self.run / "result.json"
        original = spec.read_json(path)
        for status in ("TIMEOUT", "FAIL", "ERROR", "UNSUPPORTED", "SKIP", "NOT_RUN"):
            with self.subTest(status=status):
                write_json(path, dict(status=status, timeout=status == "TIMEOUT"))
                row = spec.inspect_run(self.run)
                self.assertEqual(row["execution_status"], status)
                self.assertEqual(row["measurement_validity"], "NOT_EVALUATED")
                self.assertIn("result.json", row["artifact_hashes"])
        write_json(path, original)
        launch = spec.read_json(self.run / "launch.json")
        launch["workload"] = "command"
        write_json(self.run / "launch.json", launch)
        self.assertEqual(spec.inspect_run(self.run)["measurement_validity"], "INVALID")

    def test_image_collector_integration_retains_frame_samples_and_zero_dram(self):
        from test_image_summary import ImageSummaryTests

        image = ImageSummaryTests()
        image.setUp()
        self.addCleanup(image.doCleanups)
        image.config["system"].setdefault("platform", {})["terminal"] = dict(port=1234)
        image.write()
        for name in ("config.json", "roi-events.json", "stats.txt"):
            (self.run / "m5out" / name).write_bytes((image.out / name).read_bytes())
        serial = self.run / "m5out/system.platform.terminal"
        serial.write_text(image.serial.read_text() + "APOLLO_WORKLOAD_EXIT=0\n")
        launch = spec.read_json(self.run / "launch.json")
        launch["workload"] = "command"
        write_json(self.run / "launch.json", launch)
        write_json(self.run / "result.json", dict(status="PASS", returncode=0, timeout=False,
                                                  measurement=image.collect()))
        write_json(self.run / "m5out/resolved-profile.json", dict(cpu=dict(cores=4), memory=dict(channels=4)))
        report_path = self.run / "m5out/config-verification.json"
        report = spec.read_json(report_path)
        for name in ("config.json", "resolved-profile.json"):
            report["artifact_hashes"][name] = spec.digest(self.run / "m5out" / name)
        write_json(report_path, report)
        row = spec.inspect_run(self.run)
        self.assertTrue(spec.case_ready(row), row)
        self.assertEqual(row["workload"]["kind"], "image")
        self.assertEqual(row["workload"]["background_kib_per_worker"], 4)
        self.assertEqual(row["metrics"]["dram_GB_s"]["value"], 0)
        latency = row["metrics"]["frame_latency_max_ns"]
        self.assertEqual(latency["value"], 110000)
        self.assertEqual(latency["samples"], 4)
        self.assertEqual(latency["sample_definition"], "completed-frame")
        self.assertEqual(spec.evaluate_target(target(unit="ns", statistic="max", limit=110000,
            margin=0, min_samples=4, sample_definition="completed-frame"), latency)["status"], "MEETS")


class TargetTests(unittest.TestCase):
    def test_upper_and_lower_bound_equality_and_headroom(self):
        for comparator, value, limit, margin in (("<=", 18, 20, .1), (">=", 12, 10, .2)):
            with self.subTest(comparator=comparator):
                row = spec.evaluate_target(target(comparator=comparator, limit=limit, margin=margin),
                                           spec.metric(value, "ns/load"))
                self.assertEqual(row["status"], "MEETS", row)
                self.assertAlmostEqual(row["nominal_headroom"], margin)
                bad = value + .01 if comparator == "<=" else value - .01
                self.assertEqual(spec.evaluate_target(target(comparator=comparator, limit=limit, margin=margin),
                                 spec.metric(bad, "ns/load"))["status"], "DOES_NOT_MEET")

    def test_unit_conversion_preserves_decimal_boundary(self):
        row = spec.evaluate_target(target(unit="ms", limit=20), spec.metric(18000000, "ns"))
        self.assertEqual(row["status"], "MEETS", row)
        self.assertEqual(row["value"], 18)

    def test_zero_target_requires_explicit_absolute_rule(self):
        observation = spec.metric(0, "ns/load")
        self.assertEqual(spec.evaluate_target(target(limit=0, margin=0), observation)["status"], "UNDECIDED")
        row = spec.evaluate_target(target(limit=0, margin=0, absolute_rule="exact-zero",
                                         absolute_threshold=0), observation)
        self.assertEqual(row["status"], "MEETS")
        self.assertIsNone(row["nominal_headroom"])

    def test_invalid_inputs_statistics_samples_and_evidence_are_undecided(self):
        observation = spec.metric(1, "ns/load")
        for updates in (dict(margin=1), dict(limit=-1), dict(limit=float("nan")),
                        dict(limit=True), dict(min_samples=2), dict(statistic="p99"),
                        dict(unit="GB/s"), dict(sample_definition="frame"),
                        dict(confidence_policy="confidence-95"), dict(owner="")):
            with self.subTest(updates=updates):
                self.assertEqual(spec.evaluate_target(target(**updates), observation)["status"], "UNDECIDED")
        self.assertEqual(spec.evaluate_target(target(), observation, valid=False)["status"], "UNDECIDED")
        self.assertEqual(spec.evaluate_target(target(), None)["status"], "UNDECIDED")


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run = fixture(self.root / "run")
        self.campaign = dict(schema=1, id="exploratory-test", required_scenarios=["alone"],
            cases=[dict(id="a-alone", candidate="A", scenario="alone", run="run")],
            targets=[target(metric="useful_GB_s", comparator=">=", unit="GB/s", limit=1, margin=0)])

    def test_required_coverage_and_failure_priority(self):
        def decision():
            return spec.campaign_report(self.campaign, self.root)["decisions"][0]["decision"]
        self.assertEqual(decision(), "CONDITIONAL")
        self.campaign["required_scenarios"].append("interference")
        self.assertEqual(decision(), "UNDECIDED")
        self.campaign["targets"][0]["limit"] = 10000
        self.assertEqual(decision(), "MODEL_INFEASIBLE")
        self.campaign["targets"] = []
        self.assertEqual(decision(), "UNDECIDED")

    def test_targets_cannot_escape_required_scenario_coverage(self):
        self.campaign["targets"].append(target(id="omitted-scenario", scenario="interference"))
        with self.assertRaisesRegex(ValueError, "required_scenarios"):
            spec.campaign_report(self.campaign, self.root)

    def test_candidate_requires_same_hardware_sources_and_inputs(self):
        self.campaign["required_scenarios"].append("interference")
        self.campaign["targets"].append({**self.campaign["targets"][0],
                                         "id": "interference", "scenario": "interference"})
        for field in ("clock", "profile", "source", "firmware", "readfile"):
            with self.subTest(field=field):
                other = fixture(self.root / field, port=4567,
                                model_root=self.root / "other-sources" if field == "source" else None)
                self.campaign["cases"] = [self.campaign["cases"][0], dict(
                    id="a-interference", candidate="A", scenario="interference", run=field)]
                out = other / "m5out"
                verifier = spec.read_json(out / "config-verification.json")
                if field in ("clock", "profile"):
                    name = "config.json" if field == "clock" else "resolved-profile.json"
                    data = spec.read_json(out / name)
                    data["system" if field == "clock" else "cpu"]["clock"] = 500
                    write_json(out / name, data)
                    verifier["artifact_hashes"][name] = spec.digest(out / name)
                elif field == "source":
                    native = spec.read_json(out / "manifest.json")
                    key = "configs/zena_cmn/model.py"
                    path = self.root / "other-sources" / key
                    path.write_text("different model source")
                    native["source_sha256"][key] = spec.digest(path)
                    write_json(out / "manifest.json", native)
                    verifier["artifact_hashes"][key] = spec.digest(path)
                    verifier["artifact_hashes"]["oracle_loaded_sources"][str(path)] = spec.digest(path)
                    launch = spec.read_json(other / "launch.json")
                    launch["model_sources_sha256"][str(path)] = spec.digest(path)
                    write_json(other / "launch.json", launch)
                else:
                    launch = spec.read_json(other / "launch.json")
                    path = other / ("bootloader" if field == "firmware" else "guest-init.sh")
                    path.write_text("another " + field)
                    key = "bootloader_sha256" if field == "firmware" else "readfile_sha256"
                    launch[key] = spec.digest(path)
                    write_json(other / "launch.json", launch)
                    if field == "firmware":
                        native = spec.read_json(out / "manifest.json")
                        native["assets"]["bootloader"]["sha256"] = spec.digest(path)
                        write_json(out / "manifest.json", native)
                write_json(out / "config-verification.json", verifier)
                report = spec.campaign_report(self.campaign, self.root)
                self.assertTrue(all(spec.case_ready(case) for case in report["cases"]))
                decision = report["decisions"][0]
                self.assertEqual(decision["decision"], "CONDITIONAL" if field == "readfile" else "UNDECIDED")
                self.assertEqual(decision["identity_consistency"]["status"], "PASS" if field == "readfile" else "FAIL")

    def test_container_type_and_literal_dotted_keys_are_not_normalized(self):
        self.assertEqual(set(spec.changed({"x": [1000]}, {"x": {"0": 1000}})), {"x"})
        delta = spec.changed({"x": {"a.b": 1, "a": {"b": 2}}},
                             {"x": {"a.b": 2, "a": {"b": 1}}})
        self.assertEqual(set(delta), {r"x.a\.b", "x.a.b"})
        before = spec.inspect_run(self.run)
        after = copy.deepcopy(before)
        before["identity"]["canonical_config"]["system"]["clock_vector"] = [1000]
        after["identity"]["canonical_config"]["system"]["clock_vector"] = {"0": 1000}
        self.assertEqual(spec.compare_cases(before, after,
            dict(id="type-mismatch", metrics=["useful_GB_s"]))["status"], "UNDECIDED")

    def test_contract_is_deferred_without_a_completed_valid_measurement(self):
        self.campaign["cases"][0]["workload_contract"] = dict(workers=16)
        result_path = self.run / "result.json"
        completed = spec.read_json(result_path)
        result_path.unlink()
        row = spec.campaign_report(self.campaign, self.root)["cases"][0]
        self.assertEqual(row["execution_status"], "NOT_RUN")
        self.assertEqual(row["measurement_validity"], "NOT_EVALUATED")
        self.assertEqual(row["reasons"], ["missing result.json"])
        for status in ("FAIL", "ERROR", "TIMEOUT", "SKIP", "UNSUPPORTED", "NOT_RUN"):
            with self.subTest(status=status):
                write_json(result_path, dict(status=status, timeout=status == "TIMEOUT"))
                expected = spec.inspect_run(self.run)
                actual = spec.campaign_report(self.campaign, self.root)["cases"][0]
                self.assertEqual(actual["execution_status"], expected["execution_status"])
                self.assertEqual(actual["measurement_validity"], expected["measurement_validity"])
                self.assertEqual(actual["reasons"], expected["reasons"])
        write_json(result_path, completed)
        (self.run / "m5out/roi-events.json").unlink()
        expected = spec.inspect_run(self.run)
        actual = spec.campaign_report(self.campaign, self.root)["cases"][0]
        self.assertEqual(actual["execution_status"], "PASS")
        self.assertEqual(actual["measurement_validity"], "INVALID")
        self.assertEqual(actual["reasons"], expected["reasons"])

    def test_completed_measurement_requires_requested_fields_and_values(self):
        for contract in (dict(workers=16), dict(workers=True), dict(not_reported=None)):
            with self.subTest(contract=contract):
                self.campaign["cases"][0]["workload_contract"] = contract
                actual = spec.campaign_report(self.campaign, self.root)["cases"][0]
                self.assertEqual(actual["execution_status"], "PASS")
                self.assertEqual(actual["measurement_validity"], "INVALID")
                self.assertTrue(any("requested workload mismatch" in reason for reason in actual["reasons"]))
        self.campaign["cases"][0]["workload_contract"] = dict(workers=1)
        actual = spec.campaign_report(self.campaign, self.root)["cases"][0]
        self.assertEqual(actual["measurement_validity"], "VALID")

    def test_missing_run_and_workload_contract_cannot_pass(self):
        self.campaign["cases"][0]["run"] = "missing"
        row = spec.campaign_report(self.campaign, self.root)
        self.assertEqual(row["decisions"][0]["decision"], "UNDECIDED")
        self.assertEqual(row["cases"][0]["execution_status"], "NOT_RUN")
        self.campaign["cases"][0].update(run="run", workload_contract=dict(workers=16))
        row = spec.campaign_report(self.campaign, self.root)
        self.assertEqual(row["cases"][0]["measurement_validity"], "INVALID")
        self.assertEqual(row["decisions"][0]["decision"], "UNDECIDED")

    def test_comparison_requires_declared_profile_and_effective_deltas(self):
        a = spec.inspect_run(self.run)
        b = copy.deepcopy(a)
        comparison = dict(id="compare", metrics=["useful_GB_s"])
        self.assertEqual(spec.compare_cases(a, b, comparison)["status"], "PASS")
        b["identity"]["profile"]["cpu"]["cores"] = 2
        b["identity"]["canonical_config"]["system"]["clock"] = 500
        self.assertEqual(spec.compare_cases(a, b, comparison)["status"], "UNDECIDED")
        comparison["allowed_profile_changes"] = ["cpu.cores"]
        self.assertEqual(spec.compare_cases(a, b, comparison)["status"], "UNDECIDED")
        comparison["allowed_config_changes"] = ["system.clock"]
        self.assertEqual(spec.compare_cases(a, b, comparison)["status"], "PASS")
        b["identity"]["source_sha256"]["configs/zena_cmn/model.py"] = "9" * 64
        self.assertEqual(spec.compare_cases(a, b, comparison)["status"], "UNDECIDED")

    def test_comparisons_and_candidate_identity_reject_dependency_deltas(self):
        before = spec.inspect_run(self.run)
        before["id"] = "before"
        comparison = dict(id="source-change", metrics=["useful_GB_s"])
        for suffix in ("configs/ruby/CHI_config.py", "configs/topologies/CustomMesh.py",
                       "configs/zena_cmn/profiles/default.yaml"):
            for missing in (False, True):
                with self.subTest(dependency=suffix, missing=missing):
                    after = copy.deepcopy(before)
                    after["id"] = "after"
                    sources = after["identity"]["model_sources_sha256"]
                    name = next(name for name in sources if name.endswith(suffix))
                    if missing:
                        del sources[name]
                    else:
                        sources[name] = "0" * 64
                    answer = spec.compare_cases(before, after, comparison)
                    self.assertEqual(answer["status"], "UNDECIDED", answer)
                    self.assertIn("dependency provenance differs", answer["reason"])
                    self.assertEqual(spec.candidate_consistency([before, after])["status"], "FAIL")

    def test_convergence_rejects_raw_duration_and_hardware_changes(self):
        a = spec.inspect_run(self.run)
        b = copy.deepcopy(a)
        b["workload"]["passes"] = 4
        comparison = dict(id="steady", kind="convergence", metrics=["useful_GB_s"],
                          relative_tolerance=.01, allowed_workload_changes=["passes"])
        self.assertEqual(spec.compare_cases(a, a, comparison)["status"], "UNDECIDED")
        self.assertEqual(spec.compare_cases(a, b, comparison)["status"], "PASS")
        comparison["metrics"] = ["roi_seconds"]
        self.assertEqual(spec.compare_cases(a, b, comparison)["status"], "UNDECIDED")
        comparison["metrics"] = ["useful_GB_s"]
        b["identity"]["profile"]["cpu"]["cores"] = 2
        comparison["allowed_profile_changes"] = ["cpu.cores"]
        self.assertEqual(spec.compare_cases(a, b, comparison)["status"], "UNDECIDED")

    def test_zero_baseline_convergence_requires_absolute_tolerance(self):
        self.assertEqual(spec.convergence(0, 0, .1)["status"], "UNDECIDED")
        self.assertEqual(spec.convergence(0, .1, .1, .1)["status"], "PASS")
        self.assertEqual(spec.convergence(0, .2, .1, .1)["status"], "FAIL")
        self.assertEqual(spec.convergence(100, 110, .1)["status"], "PASS")

    def test_cli_writes_new_output_and_rejects_overwrite(self):
        path = self.root / "campaign.json"
        write_json(path, self.campaign)
        output = self.root / "report.json"
        self.assertEqual(spec.main(["report", str(path), "--output", str(output)]), 0)
        row = spec.read_json(output)
        self.assertEqual(row["campaign_sha256"], spec.digest(path))
        self.assertEqual(row["decisions"][0]["cost_decision"], "UNDECIDED")
        with self.assertRaisesRegex(ValueError, "already exists"):
            spec.main(["inventory", str(self.run), "--output", str(output)])

    def test_ambiguous_json_and_duplicate_case_ids_rejected(self):
        path = self.root / "bad.json"
        for payload in ('{"id":1,"id":2}', '{"number":NaN}'):
            path.write_text(payload)
            with self.assertRaises(ValueError):
                spec.read_json(path)
        self.campaign["cases"].append(self.campaign["cases"][0])
        with self.assertRaisesRegex(ValueError, "duplicate case"):
            spec.campaign_report(self.campaign, self.root)


if __name__ == "__main__":
    unittest.main()
