"""Reject incomplete SI CL1 measurements and keep deadline failures visible."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/gem5"))
import report_si_cl1 as REPORT



def complete_log():
    lines = ["SI_CL1_START version=1 cpus=4 counter_hz=100000000"]
    for cpu in range(4):
        lines.append(f"SI_CL1_CPU cpu={cpu} mpidr={0x80010000 + cpu * 256:x} "
                     "el=1 sctlr=1005 dtcm=100100023 private=PASS")
    for target, base, size, attr in (("TCM", "100100000", 131072, "44"),
                                     ("MM", "40000000", 8388608, "ff"),
                                     ("SRAM_NC", "48000000", 8388608, "44")):
        lines.append(f"SI_CL1_MAP target={target} base={base} bytes={size} "
                     f"mair={attr} matches=1 status=PASS")
    begin = 1000
    for target in ("TCM", "L1", "L2", "SRAM_NC"):
        size = 16384 if target in {"TCM", "L1"} else 262144
        for op in ("read", "write", "chase"):
            repeats = 4 if op == "chase" else 8
            accesses = size // (64 if op == "chase" else 8) * repeats
            expected = {
                "read": 0x4D5E6FFE000 if size == 16384 else 0x4D5EFFFE0000,
                "write": 0x2468ACE7,
                "chase": {"TCM": 0x100100000, "L1": 0x40000000,
                          "L2": 0x40000000, "SRAM_NC": 0x48000000}[target],
            }[op]
            lines.append(f"SI_CL1_MEM target={target} op={op} ws_bytes={size} "
                         f"iterations={repeats} useful_bytes={accesses * 8} accesses={accesses} ticks=1000 "
                         f"counter_hz=100000000 begin={begin} end={begin + 1000} "
                         f"checksum={expected:x} irq_masked=1 status=PASS")
            begin += 2000
    for phase, cpu, count in [("idle", 0, 16)] + [("loaded", c, 8) for c in range(4)]:
        for sample in range(count):
            deadline = 1000 + sample * 100
            lines.append(f"SI_CL1_IRQ_SAMPLE phase={phase} cpu={cpu} sample={sample} "
                         f"scheduled={deadline} isr={deadline + 1 + sample} "
                         f"thread={deadline + 21 + sample} finish={deadline + 31 + sample}")
        lines.append(f"SI_CL1_IRQ phase={phase} cpu={cpu} source=CNTP_PPI29 samples={count} "
                     f"period_ticks=100 irq_min=1 irq_max={count} irq_sum={count * (count + 1) // 2} "
                     f"thread_min=20 thread_max=20 thread_sum={count * 20} skipped=0 status=PASS")
    for cpu in range(4):
        lines.append(f"SI_CL1_RT cpu={cpu} priority=4 period_ticks=100 "
                     "deadline_ticks=100 releases=8 deadline_miss=0 skipped=0 "
                     "exec_min=10 exec_max=10 exec_sum=80 response_max=38 "
                     "checksum=f5c603b3 status=PASS schedulable=PASS")
        lines.append(f"SI_CL1_LOAD cpu={cpu} ws_bytes=131072 passes=1")
    lines.append("SI_CL1_RESULT status=PASS failures=0 cpu_mask=f tcm_mask=f "
                 "mem_cases=12 rt_tasks=4 irq_samples=48")
    return "\n".join(lines) + "\n\x04"


class SiCl1ReportTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.serial = Path(self.temp.name) / "serial.log"

    def analyze(self, text, backend="gem5"):
        self.serial.write_text(text)
        return REPORT.analyze(self.serial, backend)

    def test_counter_units_and_replay_boundaries(self):
        result = self.analyze(complete_log())
        self.assertEqual(result["qualification"], "MODEL_ONLY")
        self.assertAlmostEqual(result["memory"][0]["sim_seconds"], 10e-6)
        self.assertAlmostEqual(result["memory"][0]["useful_GB_s"], 13.1072)
        self.assertEqual(result["roi_schedule"][0], {
            "name": "TCM-read", "begin_tick": 10_000_000, "end_tick": 20_000_000,
        })
        latency = result["interrupts"]["idle/cpu0"]["timer_to_isr"]
        self.assertEqual(latency["min_ns"], 10)
        self.assertEqual(latency["p95_ns"], 160)
        self.assertEqual(result["interrupts"]["loaded/cpu0"]["isr_to_thread"]["max_ns"], 200)

    def test_qemu_is_only_functional_evidence(self):
        result = self.analyze(complete_log(), "qemu")
        self.assertEqual(result["qualification"], "FUNCTIONAL_ONLY")

    def test_qbox_is_only_functional_evidence(self):
        result = self.analyze(complete_log(), "qbox")
        self.assertEqual(result["qualification"], "FUNCTIONAL_ONLY")

    def test_deadline_miss_is_not_hidden_by_functional_pass(self):
        text = complete_log().replace("deadline_miss=0", "deadline_miss=8", 1)
        text = text.replace("deadline_ticks=100", "deadline_ticks=30", 1)
        text = text.replace("schedulable=PASS", "schedulable=FAIL", 1)
        result = self.analyze(text)
        self.assertEqual(result["functional_status"], "PASS")
        self.assertEqual(result["schedulability_status"], "FAIL")

    def test_rejects_truncated_and_concatenated_runs(self):
        text = complete_log()
        for invalid in (text.split("SI_CL1_RESULT")[0], text + text):
            with self.subTest(invalid=invalid[-100:]):
                with self.assertRaises(ValueError):
                    self.analyze(invalid)

    def test_rejects_bad_units_time_order_and_guest_failures(self):
        for old, new in (
            ("counter_hz=100000000", "counter_hz=1000000"),
            ("end=2000", "end=2001"),
            ("isr=1001", "isr=999"),
            ("thread=1021", "thread=1000"),
            ("useful_bytes=131072", "useful_bytes=1"),
            ("tcm_mask=f", "tcm_mask=7"),
            ("private=PASS", "private=FAIL"),
            ("matches=1", "matches=2"),
            ("failures=0", "failures=1"),
            ("passes=1", "passes=0"),
            ("irq_max=16", "irq_max=17"),
            ("checksum=4d5e6ffe000", "checksum=0"),
            ("checksum=f5c603b3", "checksum=0"),
            ("irq_masked=1", "irq_masked=0"),
            ("response_max=38", "response_max=39"),
            ("exec_sum=80", "exec_sum=81"),
            ("skipped=0", "skipped=1"),
        ):
            with self.subTest(old=old):
                with self.assertRaises(ValueError):
                    self.analyze(complete_log().replace(old, new, 1))

    def test_replay_requires_same_inputs_guest_times_and_stats_boundaries(self):
        metrics = self.analyze(complete_log())
        directory = Path(self.temp.name)
        (directory / "system.platform.terminal").write_text(complete_log())
        manifest = {"returncode": 0, "elf_sha256": "elf", "gem5_sha256": "binary",
                    "configuration_sha256": "config", "configuration_args": {
                        "cpu": "minor", "sram_latency": "20ns", "tcm_latency": "1ns"},
                    "host_seconds": 1}
        result = {"exit_cause": "UART received EOT", "sim_hz": REPORT.SIM_FREQ,
                  "counter_hz": REPORT.COUNTER_HZ, "counter_epoch_tick": 0, "cpu": "minor",
                  "roi_complete": True,
                  "roi_events": [{"name": r["name"], "phase": p, "tick": r[p + "_tick"]}
                                 for r in metrics["roi_schedule"] for p in ("begin", "end")]}
        (directory / "manifest.json").write_text(json.dumps(manifest))
        (directory / "run-result.json").write_text(json.dumps(result))
        (directory / "config.json").write_text("{}")
        blocks = []
        for roi, memory in zip(metrics["roi_schedule"], metrics["memory"]):
            target, op = memory["target"], memory["op"]
            if target in {"TCM", "SRAM_NC"}:
                path = "cpu0.dtcm" if target == "TCM" else "nc_sram"
                stat = "bytesWritten" if op == "write" else "bytesRead"
                traffic = f"system.{path}.{stat}::total {memory['useful_bytes']}\n"
            else:
                traffic = "system.cpu0.dcache.overallAccesses::total 1\n"
                if target == "L1":
                    traffic += "system.cpu0.dcache.overallHits::total 1\n"
                else:
                    lines = memory["accesses"] if op == "chase" else memory["useful_bytes"] // 64
                    traffic = (f"system.cpu0.dcache.overallAccesses::total {lines}\n"
                               f"system.cpu0.dcache.overallMisses::total {lines}\n"
                               f"system.l2.overallAccesses::total {lines}\n"
                               f"system.l2.overallHits::total {lines}\n")
            blocks.append("---------- Begin Simulation Statistics ----------\n"
                          f"finalTick {roi['end_tick']}\n"
                          f"simTicks {roi['end_tick'] - roi['begin_tick']}\n"
                          f"simFreq {REPORT.SIM_FREQ}\n"
                          f"{traffic}"
                          "---------- End Simulation Statistics ----------\n")
        (directory / "stats.txt").write_text("".join(blocks))
        metrics["simulator"] = REPORT.simulator_evidence(directory)
        self.assertEqual(REPORT.replay_evidence(metrics, directory)["status"], "PASS")
        (directory / "stats.txt").write_text("".join(blocks[1:]))
        with self.assertRaisesRegex(ValueError, "stats block"):
            REPORT.replay_evidence(metrics, directory)
        (directory / "stats.txt").write_text("".join(blocks))
        for key in ("elf_sha256", "gem5_sha256", "configuration_sha256"):
            changed = {**manifest, key: "changed"}
            (directory / "manifest.json").write_text(json.dumps(changed))
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "replay input differs: " + key):
                REPORT.replay_evidence(metrics, directory)
        for key in ("sram_latency", "tcm_latency"):
            changed = {**manifest, "configuration_args": {**manifest["configuration_args"], key: "30ns"}}
            (directory / "manifest.json").write_text(json.dumps(changed))
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "replay input differs: configuration_args"):
                REPORT.replay_evidence(metrics, directory)
        (directory / "manifest.json").write_text(json.dumps(manifest))
        other = directory / "other.log"
        other.write_text(complete_log() + "\n")
        process = subprocess.run([
            sys.executable, REPORT.__file__, str(other), "--backend", "gem5",
            "--gem5-dir", str(directory), "--output", str(directory / "report"),
        ], capture_output=True, text=True)
        self.assertEqual(process.returncode, 1)
        self.assertIn("serial log does not belong", process.stderr)

    def test_rejects_wrong_memory_path_and_allows_small_roi_edge(self):
        memory = {"target": "SRAM_NC", "op": "chase", "useful_bytes": 131072}
        stats = {"system.nc_sram.bytesRead::total": 131080}
        self.assertEqual(REPORT.memory_path_evidence(memory, stats)["status"], "PASS")
        for invalid in ({}, {"system.nc_sram.bytesRead::total": 65536},
                        {**stats, "system.cpu0.dcache.overallAccesses::total": 1}):
            with self.assertRaises(ValueError):
                REPORT.memory_path_evidence(memory, invalid)
        with self.assertRaises(ValueError):
            REPORT.memory_path_evidence({"target": "L2", "op": "read", "useful_bytes": 2097152}, {
                "system.cpu0.dcache.overallAccesses::total": 100,
                "system.cpu0.dcache.overallHits::total": 100,
            })
        with self.assertRaises(ValueError):
            REPORT.memory_path_evidence({"target": "L2", "op": "write", "useful_bytes": 2097152}, {
                "system.cpu0.dcache.overallAccesses::total": 262144,
                "system.cpu0.dcache.overallMisses::total": 1,
                "system.l2.overallAccesses::total": 1,
                "system.l2.overallHits::total": 1,
            })

    def test_rejects_unreported_skipped_release(self):
        lines = complete_log().splitlines()
        for index, line in enumerate(lines):
            if not line.startswith("SI_CL1_IRQ_SAMPLE phase=loaded cpu=0 "):
                continue
            fields = dict(field.split("=") for field in line.split()[1:])
            if fields["sample"] == "0":
                continue
            for key in ("scheduled", "isr", "thread", "finish"):
                fields[key] = str(int(fields[key]) + 100)
            lines[index] = "SI_CL1_IRQ_SAMPLE " + " ".join(f"{k}={v}" for k, v in fields.items())
        with self.assertRaisesRegex(ValueError, "skipped count"):
            self.analyze("\n".join(lines))


if __name__ == "__main__":
    unittest.main()
