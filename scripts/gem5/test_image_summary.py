# SPDX-License-Identifier: BSD-3-Clause
"""Corrupt-artifact tests for the read-only image ROI collector."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from image_summary import fixture_hash, summarize_image


class ImageSummaryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.out = Path(self.directory.name)
        self.serial = self.out / "uart.log"
        self.guest = dict(
            schema=1, result="PASS", host=False, kernel="rgb_u8_hwc_to_f32_chw",
            fixture="rgb_formula_v1", normalization="(value-128)/128",
            scope="synthetic_exploratory", state="steady_state_warmup_requested",
            arrival="closed_loop", queue_policy="one_in_flight_no_drop",
            width=2, height=2, frames=4, frame_pool=2, warmup_passes=1, cpu=2,
            background_workers=2, background_cpus=[0, 3], background_mode="copy",
            background_kib_per_worker=4, working_set_bytes=120, useful_bytes=240,
            background_useful_bytes=24576, allocated_bytes=16632,
            counter="CNTVCT_EL0", counter_hz=1_000_000,
            roi_start_tick=100, roi_end_tick=600, roi_elapsed_ns=500_000,
            output_validation_scope="every_element_of_each_final_pool_buffer",
            validated_elements=24, output_mismatches=0,
            # Golden output from the native C workload's final-pool oracle.
            output_hash_fnv1a64="76694a812f406f7d",
            timing_scope="kernel_calls_with_counter_and_completion_barrier",
            roi_includes="start_barrier_frames_background_completion_barrier")
        self.frames = [dict(frame=index, slot=index % 2, release_tick=release,
                            start_tick=start, finish_tick=finish, duration_ns=(finish - start) * 1000)
                       for index, (release, start, finish) in enumerate([
                           (105, 110, 210), (210, 215, 315),
                           (315, 320, 420), (420, 430, 530)])]
        self.background = [dict(cpu=cpu, mode="copy", completed_chunks=chunks,
                                useful_bytes=chunks * 8192, start_tick=108,
                                finish_tick=550, foreground_overlap_ticks=420)
                           for cpu, chunks in ((0, 1), (3, 2))]
        self.events = [dict(phase="warmup", tick=100),
                       dict(phase="roi_begin", tick=1_000_000),
                       dict(phase="roi_end", tick=601_000_000)]
        self.config = dict(system=dict(
            cpu=[dict(cpu_id=i, l1d=dict(cache=dict(path=f"system.cpu{i}.l1")),
                      l2=dict(cache=dict(path=f"system.cpu{i}.l2")),
                      isa=[dict(type="ArmISA", path=f"system.cpu{i}.isa")]) for i in range(4)],
            roi_cpu=[dict(cpu_id=i, type="BaseO3CPU", isa=[f"system.cpu{i}.isa"])
                     for i in range(4)],
            platform=dict(timer=dict(type="GenericTimer", cntfrq=1_000_000,
                                     counter="system.platform.counter"),
                          counter=dict(type="SystemCounter", path="system.platform.counter",
                                       freqs=[1_000_000])),
            mem_ctrls=[{} for _ in range(4)],
            ruby=dict(rnf=[dict(dsu_l3=dict(cache=dict(path="dsu0.l3")))],
                      hnf=[dict(cntrl=dict(cache=dict(path="home0.slc")))])))
        self.counters = {f"system.roi_cpu{i}.commitStats0.numInsts": 100 if i != 1 else 0
                         for i in range(4)}
        # A cache-resident image is valid without any DRAM traffic.
        for channel in range(4):
            for direction in ("Read", "Written"):
                self.counters[f"system.mem_ctrls{channel}.dram.dramBytes{direction}"] = 0
        for path in ([f"system.cpu{i}.{level}" for i in range(4) for level in ("l1", "l2")]
                     + ["dsu0.l3", "home0.slc"]):
            self.counters[path + ".m_demand_hits"] = 4
            self.counters[path + ".m_demand_misses"] = 1
        self.write()

    def stats(self, *, begin=1_000_000, end=601_000_000):
        counters = dict(simFreq=1_000_000_000_000, simTicks=end - begin, finalTick=end)
        counters.update(self.counters)
        return ("---------- Begin Simulation Statistics ----------\n"
                + "".join(f"{key} {value}\n" for key, value in counters.items())
                + "---------- End Simulation Statistics ----------\n")

    def write(self):
        lines = ["APOLLO_IMAGE_READY initialization=atomic scope=synthetic_exploratory"]
        for name, records in (("BACKGROUND", self.background), ("FRAME", self.frames),
                              ("RESULT", [self.guest])):
            lines.extend("APOLLO_IMAGE_" + name + " " + json.dumps(record) for record in records)
        self.serial.write_text("\n".join(lines) + "\n")
        (self.out / "roi-events.json").write_text(json.dumps(self.events))
        (self.out / "config.json").write_text(json.dumps(self.config))
        (self.out / "stats.txt").write_text(self.stats())

    def collect(self, **kwargs):
        return summarize_image(self.out, self.serial, **kwargs)

    def test_independent_oracle_matches_native_c_output(self):
        self.assertEqual(fixture_hash(2, 2, 2), "76694a812f406f7d")

    def test_valid_arbitrary_affinity_zero_dram_and_no_artifact_writes(self):
        before = {path.name: path.read_bytes() for path in self.out.iterdir()}
        result = self.collect(expected=dict(width=2, height=2, frames=4, frame_pool=2,
                                            warmup_passes=1, cpu=2, background_cpus=[0, 3]))
        self.assertEqual(result["worker_committed_instructions"], {"2": 100, "0": 100, "3": 100})
        self.assertEqual(result["dram"]["read_bytes"], 0)
        self.assertEqual(len(result["dram"]["channels"]), 4)
        self.assertEqual(result["cache_counters"]["L1"]["hits"], 16)
        self.assertEqual(result["application"]["frame_latency_ns"],
                         dict(sample_count=4, median=105000.0, observed_max=110000,
                              statistic_scope="observed_frames_only"))
        self.assertEqual(result["application"]["kernel_latency_ns"]["observed_max"], 100000)
        self.assertAlmostEqual(result["roi"]["seconds"], 0.0006)
        self.assertAlmostEqual(result["application"]["foreground_seconds"], 0.000425)
        self.assertGreater(result["application"]["foreground_frames_per_second"],
                           result["application"]["frames_per_second"])
        json.dumps(result, allow_nan=False)
        self.assertEqual(before, {path.name: path.read_bytes() for path in self.out.iterdir()})

    def test_serial_contract_and_oracle_fail_closed(self):
        valid = copy.deepcopy(self.guest)
        mutations = dict(result="FAIL", host=True, schema=True, fixture="unrecognized",
                         kernel="copy", normalization="value/255", counter="simTicks",
                         state="cold", output_validation_scope="checksum_only",
                         output_mismatches=1, output_hash_fnv1a64="0000000000000000",
                         validated_elements=23, working_set_bytes=121, useful_bytes=241,
                         allocated_bytes=100, background_useful_bytes=0,
                         frames=3, frame_pool=5, warmup_passes=0,
                         counter_hz=0, roi_elapsed_ns=1, background_workers=3,
                         background_cpus=[0, 2], background_kib_per_worker=5)
        for key, value in mutations.items():
            with self.subTest(key=key):
                self.guest = {**valid, key: value}
                self.write()
                with self.assertRaises(ValueError):
                    self.collect()

    def test_requested_settings_must_match(self):
        for requested in (dict(width=3), dict(height=3), dict(frames=8), dict(frame_pool=1),
                          dict(warmup_passes=2), dict(cpu=1), dict(background_cpus=[0, 1]),
                          dict(background_mode="read"), dict(background_kib_per_worker=8),
                          dict(cpu=True), dict(unknown=0)):
            with self.subTest(requested=requested), self.assertRaises(ValueError):
                self.collect(expected=requested)

    def test_extra_truncated_and_reordered_markers_rejected(self):
        valid = self.serial.read_text()
        lines = valid.splitlines(keepends=True)
        mutations = [valid + lines[-1], valid + lines[3], valid + lines[1],
                     "".join(lines[:-1]), "".join(lines[:3] + lines[4:]),
                     "".join(lines[:1] + lines[2:]), valid + "APOLLO_IMAGE_RESULT {",
                     valid + "APOLLO_IMAGE_UNKNOWN {}\n",
                     "".join(lines[:3] + [lines[4], lines[3]] + lines[5:]),
                     valid.replace('"schema": 1', '"schema": 1, "schema": 1')]
        for index, content in enumerate(mutations):
            with self.subTest(index=index):
                self.serial.write_text(content)
                with self.assertRaises(ValueError):
                    self.collect()

    def test_frame_temporal_corruption(self):
        valid = copy.deepcopy(self.frames)
        for index, key, value in ((0, "release_tick", 99), (1, "frame", 0),
                                  (1, "slot", 0), (1, "release_tick", 211),
                                  (1, "start_tick", 209), (1, "finish_tick", 215),
                                  (1, "finish_tick", 601), (1, "duration_ns", 999),
                                  (1, "finish_tick", True)):
            with self.subTest(index=index, key=key):
                self.frames = copy.deepcopy(valid)
                self.frames[index][key] = value
                self.write()
                with self.assertRaises(ValueError):
                    self.collect()

    def test_background_temporal_and_accounting_corruption(self):
        valid = copy.deepcopy(self.background)
        for key, value in dict(cpu=1, mode="read", completed_chunks=0, useful_bytes=4096,
                              start_tick=99, finish_tick=601, foreground_overlap_ticks=0).items():
            with self.subTest(key=key):
                self.background = copy.deepcopy(valid)
                self.background[0][key] = value
                self.write()
                with self.assertRaises(ValueError):
                    self.collect()
        self.background = copy.deepcopy(valid)
        self.background[0].update(start_tick=535, finish_tick=550, foreground_overlap_ticks=1)
        self.write()
        with self.assertRaisesRegex(ValueError, "overlap"):
            self.collect()

    def test_background_cannot_finish_before_final_foreground_frame(self):
        # This record has valid bytes and positive overlap, but violates the
        # foreground stop release -> background acquire/finish ordering.
        self.background[0].update(finish_tick=210, foreground_overlap_ticks=100)
        self.write()
        with self.assertRaisesRegex(ValueError, "before final foreground frame"):
            self.collect()
        # Equal counter ticks remain valid at the architectural timer granularity.
        self.background[0].update(finish_tick=530, foreground_overlap_ticks=420)
        self.write()
        self.collect()

    def test_native_roi_lifecycle_and_exact_window(self):
        valid = copy.deepcopy(self.events)
        for events in (valid[:2], valid + valid[-1:], [valid[1], valid[0], valid[2]],
                       [{**valid[0], "tick": True}] + valid[1:],
                       [{**valid[0], "tick": valid[1]["tick"]}] + valid[1:],
                       [{**valid[0], "case_id": 1}] + valid[1:]):
            with self.subTest(events=events):
                self.events = events
                self.write()
                with self.assertRaises(ValueError):
                    self.collect()
        self.events = valid
        self.write()
        for stats in (self.stats(end=700_000_000), self.stats() * 2,
                      self.stats().replace("---------- End Simulation Statistics ----------", ""),
                      self.stats().replace("simFreq 1000000000000", "simFreq 2000000000000")):
            with self.subTest(stats=stats[:100]):
                (self.out / "stats.txt").write_text(stats)
                with self.assertRaises(ValueError):
                    self.collect()

    def test_native_missing_or_nonfinite_worker_memory_and_cache_counters(self):
        valid = self.counters.copy()
        keys = ["system.roi_cpu3.commitStats0.numInsts",
                "system.mem_ctrls3.dram.dramBytesRead", "home0.slc.m_demand_hits"]
        for key in keys:
            for value in (None, "nan", "inf", -1):
                with self.subTest(key=key, value=value):
                    self.counters = valid.copy()
                    if value is None:
                        self.counters.pop(key)
                    else:
                        self.counters[key] = value
                    self.write()
                    with self.assertRaises(ValueError):
                        self.collect()
        self.counters = valid.copy()
        self.counters[keys[0]] = 0
        self.write()
        with self.assertRaises(ValueError):
            self.collect()

    def test_native_unconfigured_worker_and_ambiguous_alias(self):
        self.config["system"]["roi_cpu"][3]["type"] = "ArmAtomicSimpleCPU"
        self.write()
        with self.assertRaisesRegex(ValueError, "configured O3"):
            self.collect()
        self.config["system"]["roi_cpu"][3]["type"] = "BaseO3CPU"
        self.counters["system.roi_cpu03.commitStats0.numInsts"] = 100
        self.write()
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            self.collect()

    def test_native_o3_requires_resolved_arm_isa(self):
        self.config["system"]["cpu"][3]["isa"][0]["type"] = "RiscvISA"
        self.write()
        with self.assertRaisesRegex(ValueError, "ArmISA"):
            self.collect()
        self.config["system"]["cpu"][3]["isa"][0]["type"] = "ArmISA"
        self.config["system"]["roi_cpu"][3]["isa"] = ["unresolved.isa"]
        self.write()
        with self.assertRaisesRegex(ValueError, "ArmISA"):
            self.collect()

    def test_guest_counter_frequency_bound_to_native_timer(self):
        # A self-consistent forged faster CNTVCT would pass a duration-only
        # containment check. Bind its scale to the configured architected timer.
        self.guest["counter_hz"] *= 2
        self.guest["roi_elapsed_ns"] //= 2
        for frame in self.frames:
            frame["duration_ns"] //= 2
        self.write()
        with self.assertRaisesRegex(ValueError, "configured counter"):
            self.collect()
        self.config["system"]["platform"]["timer"]["cntfrq"] *= 2
        self.write()
        with self.assertRaisesRegex(ValueError, "variable SystemCounter"):
            self.collect()

    def test_negative_cache_counter_cannot_cancel_positive_counter(self):
        self.counters["system.cpu0.l1.m_demand_hits"] = -4
        self.counters["system.cpu1.l1.m_demand_hits"] = 12
        self.write()
        with self.assertRaisesRegex(ValueError, "L1 hits"):
            self.collect()

    def test_no_background_supported(self):
        self.guest.update(background_workers=0, background_cpus=[], background_mode="none",
                          background_kib_per_worker=0, background_useful_bytes=0,
                          allocated_bytes=248)
        self.background = []
        self.write()
        result = self.collect()
        self.assertEqual(result["background"], [])
        self.assertEqual(result["worker_committed_instructions"], {"2": 100})

    def test_online_epochs_aggregate_only_exact_additive_roi(self):
        ledger = [dict(epoch=index, phase="roi_begin", begin_tick=begin, end_tick=end,
                       frequency_hz=1e12)
                  for index, (begin, end) in enumerate(((1_000_000, 301_000_000),
                                                        (301_000_000, 601_000_000)))]
        (self.out / "online-activity.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in ledger))
        (self.out / "stats.txt").write_text(self.stats(end=301_000_000)
                                             + self.stats(begin=301_000_000))
        result = self.collect()
        self.assertEqual(result["roi"]["stats_block_indices"], [0, 1])
        self.assertIsNone(result["roi"]["stats_block_index"])
        self.assertEqual(result["cache_counters"]["L1"]["hits"], 32)
        self.assertEqual(result["worker_committed_instructions"]["3"], 200)


if __name__ == "__main__":
    unittest.main()
