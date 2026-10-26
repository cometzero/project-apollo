# SPDX-License-Identifier: BSD-3-Clause
"""Reject incomplete or mismatched loop ROI evidence before reporting DMIPS."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/gem5"))
import summarize_dhrystone as REPORT


class DhrystoneReportTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / "m5out"
        self.output.mkdir()
        self.write_json(self.root / "result.json", dict(
            status="PASS", workload="command", returncode=0, timeout=False))
        self.serial = self.output / "system.platform.terminal"
        self.serial.write_text("DHRY_GEM5_RESULT status=PASS runs=10000 "
                               "warmup=1000 cpu=0 scope=loop\nAPOLLO_WORKLOAD_EXIT=0\n")
        self.events = [dict(phase=phase, tick=tick) for phase, tick in
                       zip(("warmup", "roi_begin", "roi_end"), (100, 1000, 1001000))]
        self.write_json(self.output / "roi-events.json", self.events)
        self.config = dict(system=dict(
            roi_cpu=[dict(cpu_id=0, type="BaseO3CPU", path="system.roi_cpu0",
                          clk_domain="system.actual_clock")],
            actual_clock=dict(path="system.actual_clock", type="SrcClockDomain", clock=[500])))
        self.write_json(self.output / "config.json", self.config)
        self.stats = self.output / "stats.txt"
        self.block = ("---------- Begin Simulation Statistics ----------\n"
                      "finalTick 1001000\nsimTicks 1000000\nsimFreq 1000000000000\n"
                      "system.roi_cpu0.numCycles 2000\n"
                      "system.roi_cpu0.thread_0.numInsts 6000\n"
                      "---------- End Simulation Statistics ----------\n")
        self.stats.write_text(self.block)

    @staticmethod
    def write_json(path, data):
        path.write_text(json.dumps(data))

    def test_score_uses_roi_and_actual_clock(self):
        result = REPORT.summarize(self.root)
        self.assertEqual(result["simulated_seconds"], 0.000001)
        self.assertEqual(result["cycles_per_iteration"], 0.2)
        self.assertEqual(result["ipc"], 3)
        self.assertEqual(result["cpu_frequency_hz"], 2000000000)
        self.assertAlmostEqual(result["dmips"], 10000000000 / 1757)
        self.assertAlmostEqual(result["dmips_per_mhz"], 10000000000 / 1757 / 2000)

    def test_selects_exact_block_not_first_or_last(self):
        other = self.block.replace("finalTick 1001000", "finalTick 2001000")
        self.stats.write_text(other + self.block + other)
        self.assertEqual(REPORT.summarize(self.root)["stats_block_indices"], [1])

    def test_host_cost_does_not_change_score(self):
        before = REPORT.summarize(self.root)
        self.stats.write_text(self.block.replace(
            "finalTick", "hostSeconds 123.0\nhostInstRate 456.0\nfinalTick"))
        after = REPORT.summarize(self.root)
        self.assertEqual(before["dmips"], after["dmips"])
        self.assertEqual(after["host_simulation_cost"],
                         dict(hostSeconds=123.0, hostInstRate=456.0))
        self.assertEqual(after["warmup_ticks"], 900)

    def test_stats_corruption(self):
        for text in (self.block * 2,
                     self.block.replace("simTicks 1000000", "simTicks 999999"),
                     self.block.split("---------- End")[0],
                     self.block.replace("system.roi_cpu0.numCycles 2000\n", "")):
            with self.subTest(text=text):
                self.stats.write_text(text)
                with self.assertRaises((ValueError, KeyError)):
                    REPORT.summarize(self.root)

    def test_nonfinite_nonpositive_and_fractional_counters(self):
        for original in ("simFreq 1000000000000", "numCycles 2000", "numInsts 6000"):
            for value in ("nan", "inf", "-1", "0", "1.5"):
                with self.subTest(original=original, value=value):
                    self.stats.write_text(self.block.replace(original, original.split()[0] + " " + value))
                    with self.assertRaises(ValueError):
                        REPORT.summarize(self.root)

    def test_rejects_wrong_cpu_or_clock(self):
        for key, value in (("type", "AtomicSimpleCPU"), ("cpu_id", 1),
                           ("path", "system.cpu0")):
            config = json.loads(json.dumps(self.config))
            config["system"]["roi_cpu"][0][key] = value
            self.write_json(self.output / "config.json", config)
            with self.assertRaises(ValueError):
                REPORT.summarize(self.root)
        for value in ([500, 1000], [float("nan")], [0], [True]):
            self.config["system"]["actual_clock"]["clock"] = value
            self.write_json(self.output / "config.json", self.config)
            with self.assertRaises(ValueError):
                REPORT.summarize(self.root)

    def test_rejects_bad_lifecycle(self):
        for events in (self.events[:2], self.events * 2,
                       [self.events[0], dict(phase="roi_begin", tick=100), self.events[2]],
                       [self.events[0], dict(phase="roi_begin", tick=1000.0), self.events[2]]):
            self.write_json(self.output / "roi-events.json", events)
            with self.assertRaises(ValueError):
                REPORT.summarize(self.root)

    def test_rejects_ambiguous_or_failed_guest(self):
        good = self.serial.read_text()
        for text in (good * 2, good.replace("status=PASS", "status=FAIL"),
                     good.replace("scope=loop", "scope=whole-command"),
                     good.replace("EXIT=0", "EXIT=1"), good + "Kernel panic\n",
                     good + "GEM5_CONTROL_RUN cpu=0 scope=whole-command\n"):
            self.serial.write_text(text)
            with self.assertRaises(ValueError):
                REPORT.summarize(self.root)

    def test_rejects_failed_launcher(self):
        for overrides in (dict(status="FAIL"), dict(workload="boot"),
                          dict(returncode=-15), dict(timeout=True)):
            self.write_json(self.root / "result.json", dict(
                dict(status="PASS", workload="command", returncode=0, timeout=False),
                **overrides))
            with self.assertRaises(ValueError):
                REPORT.summarize(self.root)

    def test_rejects_online_clock_changes(self):
        (self.output / "online-activity.jsonl").write_text("")
        with self.assertRaises(ValueError):
            REPORT.summarize(self.root)


if __name__ == "__main__":
    unittest.main()
