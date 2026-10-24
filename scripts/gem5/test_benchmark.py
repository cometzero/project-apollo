# SPDX-License-Identifier: BSD-3-Clause
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from benchmark import summarize, summarize_multicore


class BenchmarkTests(unittest.TestCase):
    def test_multicore_summary_checks_workers_channels_and_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            serial = out / "serial.log"
            guest = dict(result="PASS", benchmark="read", kernel="neon", workers=16,
                         passes=1, working_set_bytes=67108864, useful_bytes=67108864,
                         warmup_passes=1, initialization_before_switch=True,
                         channel_phase_spread=False, affinity="0..workers-1", checksum=8388608,
                         warmup_checksum=8388608)
            serial.write_text("CMN_RESULT " + json.dumps(guest) + "\n")
            (out / "roi-events.json").write_text(json.dumps([
                dict(phase="warmup", tick=100), dict(phase="roi_begin", tick=1000),
                dict(phase="roi_end", tick=3000)]))
            counters = "".join(
                f"system.roi_cpu{i}.commitStats0.numInsts 100\n"
                f"system.mem_ctrls{i}.dram.dramBytesRead 4194304\n"
                f"system.mem_ctrls{i}.dram.dramBytesWritten 0\n" for i in range(16))
            cpus = [dict(cpu_id=i, l1d=dict(cache=dict(path=f"cpu{i}.l1")),
                         l2=dict(cache=dict(path=f"cpu{i}.l2"))) for i in range(16)]
            rnf = [dict(dsu_l3=dict(cache=dict(path=f"dsu{i}.l3"))) for i in range(4)]
            hnf = [dict(cntrl=dict(cache=dict(path=f"home{i}.cache"))) for i in range(8)]
            (out / "config.json").write_text(json.dumps(
                dict(system=dict(cpu=cpus, ruby=dict(rnf=rnf, hnf=hnf)))))
            paths = ([f"cpu{i}.{level}" for i in range(16) for level in ("l1", "l2")]
                     + [f"dsu{i}.l3" for i in range(4)] + [f"home{i}.cache" for i in range(8)])
            counters += "".join(f"{path}.m_demand_hits 4\n{path}.m_demand_misses 1\n"
                                for path in paths)
            stats = self.stats().replace("finalTick 3000\n", "finalTick 3000\n" + counters)
            # Ignore diagnostic warmup/partial ROI dumps and the exit dump.
            (out / "stats.txt").write_text(
                self.stats(999, 999) + self.stats(2000, 1000) + stats + self.stats(4000, 3000))

            def collect():
                return summarize_multicore(out, serial, workers=16, size_bytes=67108864,
                                           passes=1, channels=16)

            summary = collect()
            self.assertEqual(summary["dram"]["read_bytes"], 67108864)
            self.assertEqual(summary["roi"]["stats_block_index"], 2)
            self.assertEqual(len(summary["worker_committed_instructions"]), 16)
            self.assertEqual(summary["cache_counters"]["L1"]["hits"], 64)
            self.assertEqual(summary["cache_counters"]["L2"]["hits"], 64)
            self.assertEqual(summary["cache_counters"]["L3"]["hits"], 16)
            self.assertEqual(summary["cache_counters"]["SLC_proxy"]["hits"], 32)
            self.assertTrue((out / "roi-summary.json").is_file())
            padded = re.sub(r"system\.roi_cpu(\d+)\.",
                            lambda m: f"system.roi_cpu{int(m[1]):02d}.", stats)
            (out / "stats.txt").write_text(padded)
            self.assertEqual(collect()["worker_committed_instructions"],
                             summary["worker_committed_instructions"])
            (out / "stats.txt").write_text(padded.replace(
                "finalTick 3000\n",
                "finalTick 3000\nsystem.roi_cpu0.commitStats0.numInsts 100\n"))
            with self.assertRaisesRegex(ValueError, "ambiguous"):
                collect()
            (out / "stats.txt").write_text(stats)
            for key, value in (("checksum", 1), ("workers", 4), ("kernel", "scalar")):
                serial.write_text("CMN_RESULT " + json.dumps({**guest, key: value}) + "\n")
                with self.assertRaises(ValueError):
                    collect()
            serial.write_text("CMN_RESULT " + json.dumps(guest) + "\n")
            for broken in (
                stats.replace("system.roi_cpu15.commitStats0.numInsts 100", "system.roi_cpu15.commitStats0.numInsts 0"),
                stats.replace("system.mem_ctrls15.dram.dramBytesRead 4194304", "system.mem_ctrls15.dram.dramBytesRead 0"),
                stats.replace("finalTick 3000", "finalTick 4000"),
            ):
                (out / "stats.txt").write_text(broken)
                with self.assertRaises(ValueError):
                    collect()

    def test_multicore_copy_and_triad_require_exact_payload_and_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            serial = out / "serial.log"
            (out / "roi-events.json").write_text(json.dumps([
                dict(phase="warmup", tick=100), dict(phase="roi_begin", tick=1000),
                dict(phase="roi_end", tick=3000)]))
            counters = "".join(
                f"system.roi_cpu{i}.commitStats0.numInsts 100\n"
                f"system.mem_ctrls{i}.dram.dramBytesRead 4096\n"
                f"system.mem_ctrls{i}.dram.dramBytesWritten 4096\n" for i in range(4))
            stats = self.stats().replace("finalTick 3000\n", "finalTick 3000\n" + counters)
            (out / "stats.txt").write_text(stats)
            for mode, guest_mode, arrays in (("copy", "copy", 2), ("triad", "stream", 3)):
                guest = dict(result="PASS", benchmark=guest_mode, kernel="scalar", workers=4,
                             passes=2, working_set_bytes=1048576 * arrays,
                             useful_bytes=2097152 * arrays, warmup_passes=1,
                             initialization_before_switch=True, channel_phase_spread=False,
                             affinity="0..workers-1", checksum=0, warmup_checksum=0)

                def collect(**overrides):
                    serial.write_text("CMN_RESULT " + json.dumps({**guest, **overrides}))
                    return summarize_multicore(out, serial, workers=4, size_bytes=1048576,
                                               passes=2, channels=4, mode=mode)

                self.assertEqual(collect()["application"]["useful_bytes"], 2097152 * arrays)
                for key, value in (("working_set_bytes", 1048576), ("useful_bytes", 2097152),
                                   ("passes", 1), ("kernel", "neon"), ("benchmark", "read"),
                                   ("checksum", 1), ("warmup_checksum", 1)):
                    with self.subTest(mode=mode, field=key), self.assertRaises(ValueError):
                        collect(**{key: value})
                for direction in ("Read", "Written"):
                    (out / "stats.txt").write_text(stats.replace(
                        f"system.mem_ctrls3.dram.dramBytes{direction} 4096",
                        f"system.mem_ctrls3.dram.dramBytes{direction} 0"))
                    with self.subTest(mode=mode, missing=direction), self.assertRaises(ValueError):
                        collect()
                (out / "stats.txt").write_text(stats)
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
        binary = Path(self.temp.name) / "benchmark-aarch64"
        subprocess.run([
            "aarch64-linux-gnu-gcc", "-O2", "-static", "-pthread",
            "-march=armv8-a", "-mno-outline-atomics", "-I",
            str(root / "hsoc-stack/tools/gem5/workloads/zena_cmn"),
            str(Path(__file__).with_name("benchmark.c")), "-o", str(binary),
        ], check=True)
        assembly = subprocess.check_output(
            ["aarch64-linux-gnu-objdump", "-d", "--disassemble=main",
             str(binary)], text=True,
        )
        instructions = {
            int(address, 16): (opcode, mnemonic, operands)
            for address, opcode, mnemonic, operands in re.findall(
                r"^\s*([0-9a-f]+):\s+([0-9a-f]{8})\s+(\S+)[ \t]*(.*)$",
                assembly, re.MULTILINE)
        }
        following = {}
        preceding = {address: [] for address in instructions}
        for address, (_, mnemonic, operands) in instructions.items():
            targets = [] if mnemonic in ("ret", "br") else [address + 4]
            if mnemonic == "b" or mnemonic.startswith("b.") or mnemonic in (
                    "cbz", "cbnz", "tbz", "tbnz"):
                target = int(re.search(r"\b([0-9a-f]+)\s+<", operands)[1], 16)
                targets = [target] if mnemonic == "b" else targets + [target]
            following[address] = [target for target in targets
                                  if target in instructions]
            for target in following[address]:
                preceding[target].append(address)

        def check_barriers(code):
            def boundaries(marker, reverse=False):
                edges = preceding if reverse else following
                pending, seen, found = list(edges[marker]), set(), set()
                while pending:
                    address = pending.pop()
                    if address in seen:
                        continue
                    seen.add(address)
                    opcode, mnemonic, operands = code[address]
                    if opcode == "d5033f9f":
                        found.add(address)
                    elif opcode in ("ff5a0110", "ff5b0110") or not edges[address] or (
                            mnemonic in ("bl", "blr") and (
                                not reverse or re.search(r"<(chase|read_array)[>.]", operands))):
                        found.add(None)
                    else:
                        pending.extend(edges[address])
                return found

            begins = [address for address, insn in code.items() if insn[0] == "ff5a0110"]
            ends = [address for address, insn in code.items() if insn[0] == "ff5b0110"]
            self.assertEqual((len(begins), len(ends)), (2, 1))
            # Block placement may put ROI begin after end in objdump output.
            # Only ROI begin has barriers before and after; switch precedes warmup.
            roi_begins = [address for address in begins
                          if None not in boundaries(address, True)
                          and None not in boundaries(address)]
            self.assertEqual(len(roi_begins), 1)
            barriers = set()
            for marker in (roi_begins[0], ends[0]):
                for reverse in (False, True):
                    found = boundaries(marker, reverse)
                    self.assertTrue(found)
                    self.assertNotIn(None, found)
                    barriers.update(found)
            self.assertEqual(len(barriers), 4)
            return barriers

        barriers = check_barriers(instructions)
        for address in barriers:
            with self.subTest(removed_barrier=hex(address)):
                broken = {**instructions, address: ("d503201f", "nop", "")}
                with self.assertRaises(AssertionError):
                    check_barriers(broken)

    def test_roi_summary_requires_simulation_and_complete_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            serial = out / "serial.log"
            result = dict(result="PASS", mode="cache", checksum=2, expected=2, host=False,
                          working_set_bytes=32768, passes=2, warmup_passes=1,
                          useful_bytes=8192, dependent_loads=1024)

            def collect(**requested):
                return summarize(out, serial, **dict(
                    dict(mode="cache", size_bytes=32768, passes=2), **requested))

            serial.write_text("APOLLO_BENCH_RESULT " + json.dumps(result))
            events = [
                dict(phase="warmup", tick=100),
                dict(phase="roi_begin", tick=1000),
                dict(phase="roi_end", tick=3000),
            ]
            (out / "roi-events.json").write_text(json.dumps(events))
            (out / "stats.txt").write_text(self.stats())
            summary = collect()
            self.assertEqual(summary["roi_ticks"], 2000)
            self.assertAlmostEqual(summary["ns_per_dependent_load"], 2 / 1024)
            for bad in (float("nan"), -1, True):
                serial.write_text("APOLLO_BENCH_RESULT " + json.dumps(
                    {**result, "useful_bytes": bad}))
                with self.assertRaises(ValueError):
                    collect()
            serial.write_text("APOLLO_BENCH_RESULT " + json.dumps(result))
            for requested in (dict(mode="dram"), dict(size_bytes=65536), dict(passes=1)):
                with self.subTest(requested=requested), self.assertRaises(ValueError):
                    collect(**requested)
            for key, value in (("mode", "dram"), ("working_set_bytes", 65536),
                               ("passes", 1), ("warmup_passes", 0), ("dependent_loads", 200)):
                serial.write_text("APOLLO_BENCH_RESULT " + json.dumps({**result, key: value}))
                with self.subTest(field=key), self.assertRaises(ValueError):
                    collect()
            serial.write_text("APOLLO_BENCH_RESULT " + json.dumps(result))
            for broken in (events[:2], events + [events[-1]],
                           [events[0], events[2], events[1]]):
                (out / "roi-events.json").write_text(json.dumps(broken))
                with self.assertRaises(ValueError):
                    collect()
            (out / "roi-events.json").write_text(json.dumps(events))
            (out / "stats.txt").write_text(self.stats() + self.stats(4000, 3000))
            self.assertEqual(collect()["roi_ticks"], 2000)
            roi_stats = self.stats().replace(
                "finalTick 3000\n", "finalTick 3000\nsystem.mem_ctrls0.dram.dramBytesRead 64\n")
            (out / "stats.txt").write_text(self.stats(999, 999) + self.stats(2000, 1000)
                                          + roi_stats + self.stats(4000, 3000))
            summary = collect()
            self.assertEqual(summary["stats_block_index"], 2)
            self.assertEqual(summary["dram_read_bytes"], 64)
            for broken in (
                self.stats(4000, 3000),
                self.stats(3000, 1000),
                self.stats() + self.stats(),
                self.stats().replace("simTicks 2000\n", ""),
                self.stats().replace(
                    "---------- End Simulation Statistics ----------\n", ""
                ),
            ):
                (out / "stats.txt").write_text(broken)
                with self.assertRaises(ValueError):
                    collect()
            (out / "stats.txt").write_text(self.stats())
            result["host"] = True
            serial.write_text("APOLLO_BENCH_RESULT " + json.dumps(result))
            with self.assertRaises(ValueError):
                collect()
            result.update(mode="dram", host=False, checksum=8192, expected=8192,
                          useful_bytes=65536, dependent_loads=0)
            serial.write_text("APOLLO_BENCH_RESULT " + json.dumps(result))
            summary = collect(mode="dram")
            self.assertAlmostEqual(summary["useful_GB_per_second"], 32768)
            self.assertNotIn("ns_per_dependent_load", summary)


if __name__ == "__main__":
    unittest.main()
