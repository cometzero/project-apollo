# SPDX-License-Identifier: BSD-3-Clause
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from summarize_tools import parse_tool, summarize


STREAM = ("Array size = 65536 (elements), Offset = 0 (elements)\n"
          "Each kernel will be executed 10 times.\n"
          "Your clock granularity/precision appears to be 1 microseconds.\n"
          + "".join(f"{name}: 1000 0.000025 0.000020 0.000030\n"
                    for name in ("Copy", "Scale", "Add", "Triad"))
          + "Solution Validates: avg error less than epsilon\n")


class ToolSummaryTests(unittest.TestCase):
    def test_stream_requires_validation_and_finite_resolved_times(self):
        self.assertEqual(parse_tool("stream", STREAM)["measurements"][0]["timing_quality"],
                         "SUFFICIENT_TIMER_TICKS")
        low = STREAM.replace("0.000020", "0.000001")
        self.assertEqual(parse_tool("stream", low)["measurements"][0]["timing_quality"],
                         "LOW_RESOLUTION")
        for invalid in (STREAM.replace("Solution Validates:", "missing"),
                        STREAM + "Failed Validation on array a[]",
                        STREAM.replace("0.000020", "0.000000"),
                        STREAM.replace("1000", "inf"),
                        STREAM.replace("0.000025", "nan"),
                        STREAM.replace("65536", "1024")):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                parse_tool("stream", invalid)

    def test_lmbench_exact_working_sets(self):
        sizes = [512, 1024, 2048, 3072, 4096, 6144, 8192, 12288,
                 16384, 24576, 32768, 49152, 65536, 98304, 131072,
                 196608, 262144, 393216, 524288, 786432, 1048576]
        marker = ("# modified lmbench lat_mem_rd: sample-usec=200 "
                  "(ENOUGH override; calibrated overhead)\n")
        text = marker + "".join(f"{size / 1048576:.5f} 2.500\n" for size in sizes)
        self.assertEqual(len(parse_tool("lmbench", text)["measurements"]), 21)
        for invalid in (text.rsplit("\n", 2)[0], text.replace("2.500", "nan"),
                        text.replace("1.00000", "2.00000"),
                        text.replace(marker, ""), text + marker,
                        text.replace("sample-usec=200", "sample-usec=500")):
            with self.assertRaises(ValueError):
                parse_tool("lmbench", invalid)

    def test_tiny_preserves_page_modes_and_zero_extra_latency(self):
        bw = ("Settings: bandwidth-size-kib=16 latency-size-kib=1024 "
              "duration-ms=1 repeats=1 latency-count=16384\n"
              + "".join(f"kernel {i} : 10.0 MB/s\n" for i in range(26)))
        group = ("block size : single random read / dual random read, [MADV_NOHUGEPAGE]\n"
                 + "".join(f"{2**i} : 0.0 ns / 2.0 ns\n" for i in range(10, 21)))
        result = parse_tool("tinymembench", bw + group + group.replace("NOHUGE", "HUGE"))
        self.assertEqual(len(result["latency"]), 2)
        self.assertEqual(result["latency"][0]["measurements"][0]["single_extra_ns"], 0)
        for invalid in (bw, bw + group.replace("2.0 ns", "nan ns"),
                        (bw + group).replace("10.0 MB/s", "0 MB/s"),
                        bw + group.replace("1048576 :", "2097152 :"),
                        (bw + group).replace("latency-count=16384", "latency-count=1024")):
            with self.assertRaises(ValueError):
                parse_tool("tinymembench", invalid)

    def test_evidence_links_first_stats_block_to_whole_command(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out = root / "m5out"
            out.mkdir()
            (root / "result.json").write_text('{"status":"PASS"}')
            (root / "uart.log").write_text(
                "GEM5_CONTROL_RUN cpu=0 scope=whole-command\n" + STREAM)
            (out / "roi-events.json").write_text(json.dumps([
                dict(phase="warmup", tick=10), dict(phase="roi_begin", tick=100),
                dict(phase="roi_end", tick=300)]))
            stats = ("---------- Begin Simulation Statistics ----------\n"
                     "simFreq 1000000000000\nsimTicks 200\nfinalTick 300\n"
                     "---------- End Simulation Statistics ----------\n")
            (out / "stats.txt").write_text(stats)
            (out / "config.json").write_text('{}')
            with patch("summarize_tools.cache_paths", return_value={}):
                result = summarize(root, "stream")
                self.assertEqual(result["whole_command"]["roi_ticks"], 200)
                (out / "stats.txt").write_text(stats.replace("finalTick 300", "finalTick 301"))
                with self.assertRaises(ValueError):
                    summarize(root, "stream")
                (root / "result.json").write_text('{"status":"FAIL"}')
                with self.assertRaises(ValueError):
                    summarize(root, "stream")


if __name__ == "__main__":
    unittest.main()
