# SPDX-License-Identifier: BSD-3-Clause
"""Host functional/measurement-contract tests; no simulator timing claim."""

import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest


@unittest.skipUnless(shutil.which("cc"), "host C compiler required")
class ImageBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.directory = Path(cls.temp.name)
        cls.source = Path(__file__).with_name("image_bench.c").resolve()
        cls.include = cls.source.parents[2] / "hsoc-stack/tools/gem5/workloads/zena_cmn"
        cls.binary = cls.directory / "image-bench"
        cls.cpus = sorted(os.sched_getaffinity(0))
        cls.compile(cls.binary)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @classmethod
    def compile(cls, binary, extra=()):
        subprocess.run(
            ["cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-pthread",
             f"-I{cls.include}", str(cls.source), *map(str, extra), "-o", str(binary)],
            check=True, text=True, capture_output=True,
        )

    def execute(self, *options, binary=None, affinity=None):
        return subprocess.run(
            [str(binary or self.binary), "--host", *map(str, options)],
            capture_output=True, text=True, timeout=15,
            preexec_fn=(lambda: os.sched_setaffinity(0, affinity)) if affinity else None,
        )

    @staticmethod
    def records(result, prefix):
        return [json.loads(line[len(prefix) + 1:])
                for line in result.stdout.splitlines() if line.startswith(prefix + " ")]

    @staticmethod
    def output_hash(width, height, pool):
        digest = 14695981039346656037
        for slot in range(pool):
            for channel in range(3):
                for pixel in range(width * height):
                    value = (pixel * 13 + channel * 37 + slot * 17
                             + (pixel // width) * 3) % 256
                    for byte in struct.pack("<f", (value - 128) / 128):
                        digest = ((digest ^ byte) * 1099511628211) % 2**64
        return f"{digest:016x}"

    def check_result(self, result, width, height, frames, pool, warmup,
                     background_cpus=(), mode="none", bg_kib=0):
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        records = self.records(result, "APOLLO_IMAGE_RESULT")
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["result"], "PASS")
        self.assertIs(record["host"], True)
        self.assertEqual(record["kernel"], "rgb_u8_hwc_to_f32_chw")
        self.assertEqual(record["state"], "steady_state_warmup_requested")
        self.assertEqual(record["arrival"], "closed_loop")
        self.assertEqual(record["queue_policy"], "one_in_flight_no_drop")
        for key, expected in (("width", width), ("height", height), ("frames", frames),
                              ("frame_pool", pool), ("warmup_passes", warmup)):
            self.assertEqual(record[key], expected)
        self.assertEqual(record["counter"], "CLOCK_MONOTONIC_RAW")
        self.assertEqual(record["counter_hz"], 1_000_000_000)
        self.assertEqual(record["working_set_bytes"], width * height * 15 * pool)
        self.assertEqual(record["useful_bytes"], width * height * 15 * frames)
        self.assertEqual(record["validated_elements"], width * height * 3 * pool)
        self.assertEqual(record["output_mismatches"], 0)
        self.assertEqual(record["output_hash_fnv1a64"], self.output_hash(width, height, pool))
        self.assertEqual(record["output_validation_scope"],
                         "every_element_of_each_final_pool_buffer")
        self.assertEqual(record["background_cpus"], list(background_cpus))
        self.assertEqual(record["background_workers"], len(background_cpus))
        self.assertEqual(record["background_mode"], mode)
        self.assertEqual(record["background_kib_per_worker"], bg_kib)
        begin, end = record["roi_start_tick"], record["roi_end_tick"]
        self.assertGreater(end, begin)
        self.assertEqual(record["roi_elapsed_ns"], end - begin)
        frame_records = self.records(result, "APOLLO_IMAGE_FRAME")
        self.assertEqual(len(frame_records), frames)
        for index, frame in enumerate(frame_records):
            self.assertEqual(frame["frame"], index)
            self.assertEqual(frame["slot"], index % pool)
            self.assertLessEqual(begin, frame["release_tick"])
            self.assertLessEqual(frame["release_tick"], frame["start_tick"])
            self.assertLessEqual(frame["start_tick"], frame["finish_tick"])
            self.assertLessEqual(frame["finish_tick"], end)
            self.assertEqual(frame["duration_ns"], frame["finish_tick"] - frame["start_tick"])
            if index:
                self.assertEqual(frame["release_tick"], frame_records[index - 1]["finish_tick"])
        background_records = self.records(result, "APOLLO_IMAGE_BACKGROUND")
        self.assertEqual([r["cpu"] for r in background_records], list(background_cpus))
        for worker in background_records:
            self.assertEqual(worker["mode"], mode)
            self.assertGreater(worker["completed_chunks"], 0)
            self.assertEqual(worker["useful_bytes"], worker["completed_chunks"] * 4096
                             * (2 if mode == "copy" else 1))
            self.assertLessEqual(begin, worker["start_tick"])
            self.assertLessEqual(worker["start_tick"], worker["finish_tick"])
            self.assertLessEqual(worker["finish_tick"], end)
            overlap = max(0, min(worker["finish_tick"], frame_records[-1]["finish_tick"])
                          - max(worker["start_tick"], frame_records[0]["start_tick"]))
            self.assertEqual(worker["foreground_overlap_ticks"], overlap)
            self.assertGreater(overlap, 0)
        self.assertEqual(record["background_useful_bytes"],
                         sum(r["useful_bytes"] for r in background_records))
        # All detailed output follows the host ROI end record, never occurs inside ROI.
        self.assertLess(result.stdout.index("CMN_HOST_ROI"),
                        result.stdout.index("APOLLO_IMAGE_FRAME"))
        if background_records:
            self.assertLess(result.stdout.index("CMN_HOST_ROI"),
                            result.stdout.index("APOLLO_IMAGE_BACKGROUND"))
        return record

    def test_all_output_pixels_match_independent_reference_for_frame_pools(self):
        for width, height, frames, pool, warmup in (
            (17, 13, 4, 2, 1), (1, 1, 3, 1, 2), (31, 19, 7, 3, 2),
        ):
            with self.subTest(width=width, height=height, pool=pool):
                result = self.execute("--width", width, "--height", height,
                                      "--frames", frames, "--frame-pool", pool,
                                      "--warmup", warmup)
                self.check_result(result, width, height, frames, pool, warmup)

    def test_background_read_copy_and_explicit_affinity(self):
        if len(self.cpus) < 3:
            self.skipTest("three available CPUs required for foreground and two workers")
        selected = self.cpus[1:3]
        for mode in ("read", "copy"):
            with self.subTest(mode=mode):
                result = self.execute("--width", 257, "--height", 193,
                                      "--frames", 4, "--frame-pool", 2,
                                      "--warmup", 2, "--cpu", self.cpus[0],
                                      "--background-cpus", ",".join(map(str, selected)),
                                      "--background-mode", mode, "--background-kib", 16)
                record = self.check_result(result, 257, 193, 4, 2, 2, selected, mode, 16)
                self.assertEqual(record["cpu"], self.cpus[0])

    def test_default_host_cpu_uses_inherited_cpuset(self):
        selected = self.cpus[-1]
        result = self.execute("--width", 2, "--height", 3, "--frames", 2,
                              "--frame-pool", 1, affinity={selected})
        record = self.check_result(result, 2, 3, 2, 1, 1)
        self.assertEqual(record["cpu"], selected)

    def test_invalid_options_fail_before_starting_workers(self):
        cases = [
            ["--width", "0"], ["--width", "-1"], ["--width", " 1"],
            ["--height", "16385"], ["--frames", "1", "--frame-pool", "2"],
            ["--warmup", "0"], ["--frame-pool", "0"], ["--frames", "abc"],
            ["--width", "16384", "--height", "16384"], ["--cpu", "1024"],
            ["--background-cpus", ""], ["--background-cpus", "1,"],
            ["--background-mode", "write"], ["--background-mode", "read"],
            ["--background-kib", "4"], ["--background-kib", "3"],
            ["--cold-start"], ["--width"],
            ["--cpu", str(self.cpus[0]), "--background-cpus", str(self.cpus[0])],
            ["--background-cpus", "1", "--background-cpus", "2"],
        ]
        if len(self.cpus) >= 2:
            cases.append(["--cpu", str(self.cpus[0]), "--background-cpus",
                          f"{self.cpus[1]},{self.cpus[1]}"])
        for options in cases:
            with self.subTest(options=options):
                result = self.execute(*options)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertNotIn("APOLLO_IMAGE_READY", result.stdout)
                self.assertNotIn("APOLLO_IMAGE_RESULT", result.stdout)

    def test_unavailable_cpu_is_rejected(self):
        if len(self.cpus) < 2:
            self.skipTest("two available CPUs required")
        result = self.execute("--cpu", self.cpus[1], affinity={self.cpus[0]})
        self.assertEqual(result.returncode, 2)
        self.assertIn("unavailable", result.stderr)

    def test_complete_output_oracle_rejects_corruption(self):
        harness = self.directory / "oracle.c"
        harness.write_text(
            '#define main image_bench_main\n'
            f'#include "{self.source}"\n#undef main\n'
            'int main(void) {\n'
            ' pixels = 6; pool = 2;\n'
            ' input = malloc(36); output = malloc(36 * sizeof(float));\n'
            ' if (!input || !output) return 2;\n'
            ' for (unsigned i=0;i<36;++i) input[i]=(uint8_t)(i*7);\n'
            ' image(0); image(1);\n'
            ' uint64_t digest, mismatches;\n'
            ' if (!validate_output(&digest,&mismatches) || mismatches) return 3;\n'
            ' output[35] = 1024.0f;\n'
            ' if (validate_output(&digest,&mismatches) || mismatches != 1) return 4;\n'
            ' free(output); free(input); return 0;\n}\n'
        )
        binary = self.directory / "oracle"
        subprocess.run(["cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                        "-pthread", f"-I{self.include}", str(harness), "-o", str(binary)],
                       check=True, capture_output=True, text=True)
        subprocess.run([str(binary)], check=True, capture_output=True, timeout=5)

    def test_partial_thread_creation_failure_does_not_leave_waiting_workers(self):
        if len(self.cpus) < 3:
            self.skipTest("three available CPUs required")
        wrapper = self.directory / "fail_thread.c"
        wrapper.write_text(
            '#include <pthread.h>\n#include <errno.h>\n'
            'int __real_pthread_create(pthread_t *, const pthread_attr_t *, '
            'void *(*)(void *), void *);\n'
            'int __wrap_pthread_create(pthread_t *t, const pthread_attr_t *a, '
            'void *(*f)(void *), void *v) {\n'
            ' static int calls;\n'
            ' if (++calls == 2) return EAGAIN;\n'
            ' return __real_pthread_create(t,a,f,v);\n}\n'
        )
        binary = self.directory / "fail-thread"
        self.compile(binary, (wrapper, "-Wl,--wrap=pthread_create"))
        result = self.execute("--width", 16, "--height", 16, "--cpu", self.cpus[0],
                              "--background-cpus", ",".join(map(str, self.cpus[1:3])),
                              "--background-kib", 4, binary=binary)
        self.assertEqual(result.returncode, 1)
        self.assertIn("pthread_create", result.stderr)
        self.assertNotIn("APOLLO_IMAGE_RESULT", result.stdout)


if __name__ == "__main__":
    unittest.main()
