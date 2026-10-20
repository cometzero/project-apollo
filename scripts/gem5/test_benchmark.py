# SPDX-License-Identifier: BSD-3-Clause
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from benchmark import build_benchmark, summarize


class BenchmarkTests(unittest.TestCase):
    @staticmethod
    def stats(final_tick=3000, sim_ticks=2000):
        return (
            "---------- Begin Simulation Statistics ----------\n"
            f"simFreq 1000000000000 # ticks/s\nsimTicks {sim_ticks}\n"
            f"finalTick {final_tick}\n"
            "---------- End Simulation Statistics ----------\n"
        )

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.binary = Path(cls.temp.name) / "benchmark"
        source = Path(__file__).with_name("benchmark.c")
        root = source.parents[2]
        subprocess.run(
            ["cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
             "-pthread", "-I",
             str(root / "hsoc-stack/tools/gem5/workloads/zena_cmn"),
             str(source), "-o", str(cls.binary)],
            check=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_kernels_and_rejected_arguments(self):
        for mode in ("cache", "dram"):
            with self.subTest(mode=mode):
                run = subprocess.run(
                    [str(self.binary), "--host", "--mode", mode,
                     "--size-kib", "32", "--passes", "3"],
                    check=True, capture_output=True, text=True,
                )
                result = json.loads(
                    run.stdout.split("APOLLO_BENCH_RESULT ", 1)[1]
                )
                self.assertEqual(result["result"], "PASS")
                self.assertEqual(result["checksum"], result["expected"])
                self.assertEqual(result["useful_bytes"],
                                 32 * 1024 * 3 // (8 if mode == "cache" else 1))
        for args in (["--mode", "typo"], ["--passes", "0"],
                     ["--size-kib", "262145"], ["--passes", "1025"]):
            self.assertEqual(subprocess.run(
                [str(self.binary), "--host", *args],
                capture_output=True,
            ).returncode, 2)

    @unittest.skipUnless(
        shutil.which("aarch64-linux-gnu-gcc") and
        shutil.which("aarch64-linux-gnu-objdump"),
        "AArch64 compiler and objdump required",
    )
    def test_aarch64_roi_markers_have_serializing_barriers(self):
        root = Path(__file__).resolve().parents[2]
        binary = build_benchmark(
            root / "hsoc-stack/tools/gem5",
            Path(self.temp.name) / "benchmark-aarch64",
        )
        assembly = subprocess.check_output(
            ["aarch64-linux-gnu-objdump", "-d", "--disassemble=main",
             str(binary)], text=True,
        )
        opcodes = re.findall(r"^\s*[0-9a-f]+:\s+([0-9a-f]{8})\s", assembly,
                             re.MULTILINE)
        # Switch remains unwrapped; both ROI markers have DSB SY on each side.
        self.assertEqual(
            [opcode for opcode in opcodes
             if opcode in ("ff5a0110", "ff5b0110", "d5033f9f")],
            ["ff5a0110", "d5033f9f", "ff5a0110", "d5033f9f",
             "d5033f9f", "ff5b0110", "d5033f9f"],
        )

    def test_roi_summary_requires_simulation_and_complete_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            serial = out / "serial.log"
            result = dict(result="PASS", checksum=3, expected=3, host=False,
                          working_set_bytes=32768, passes=2,
                          useful_bytes=1600, dependent_loads=200)
            serial.write_text("APOLLO_BENCH_RESULT " + json.dumps(result))
            events = [
                dict(phase="warmup", tick=100),
                dict(phase="roi_begin", tick=1000),
                dict(phase="roi_end", tick=3000),
            ]
            (out / "roi-events.json").write_text(json.dumps(events))
            (out / "stats.txt").write_text(self.stats())
            summary = summarize(out, serial)
            self.assertEqual(summary["roi_ticks"], 2000)
            self.assertAlmostEqual(summary["ns_per_dependent_load"], .01)
            for bad in (float("nan"), -1, True):
                serial.write_text("APOLLO_BENCH_RESULT " + json.dumps(
                    {**result, "useful_bytes": bad}))
                with self.assertRaises(ValueError):
                    summarize(out, serial)
            serial.write_text("APOLLO_BENCH_RESULT " + json.dumps(result))
            for broken in (events[:2], events + [events[-1]],
                           [events[0], events[2], events[1]]):
                (out / "roi-events.json").write_text(json.dumps(broken))
                with self.assertRaises(ValueError):
                    summarize(out, serial)
            (out / "roi-events.json").write_text(json.dumps(events))
            (out / "stats.txt").write_text(self.stats() + self.stats(4000, 3000))
            self.assertEqual(summarize(out, serial)["roi_ticks"], 2000)
            for broken in (
                self.stats(4000, 3000),
                self.stats(3000, 1000),
                self.stats() + self.stats() + self.stats(),
                self.stats().replace("simTicks 2000\n", ""),
                self.stats().replace(
                    "---------- End Simulation Statistics ----------\n", ""
                ),
            ):
                (out / "stats.txt").write_text(broken)
                with self.assertRaises(ValueError):
                    summarize(out, serial)
            (out / "stats.txt").write_text(self.stats())
            result["host"] = True
            serial.write_text("APOLLO_BENCH_RESULT " + json.dumps(result))
            with self.assertRaises(ValueError):
                summarize(out, serial)


if __name__ == "__main__":
    unittest.main()
