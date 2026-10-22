# SPDX-License-Identifier: BSD-3-Clause
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class ControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        directory = Path(cls.temp.name)
        cls.binary = directory / "control"
        stub = directory / "m5-stub.c"
        stub.write_text("""
#define _GNU_SOURCE
#include <stdint.h>
#include <errno.h>
#include <sched.h>
#include <sys/wait.h>
#include <inttypes.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
void m5_checkpoint(uint64_t a, uint64_t b) {
    printf("checkpoint %" PRIu64 " %" PRIu64 "\\n", a, b);
}
void m5_work_begin(uint64_t a, uint64_t b) {
    printf("begin %" PRIu64 " %" PRIu64 "\\n", a, b);
    fflush(stdout);
}
void m5_work_end(uint64_t a, uint64_t b) {
    printf("end %" PRIu64 " %" PRIu64 "\\n", a, b);
}
uint64_t m5_read_file(void *buffer, uint64_t length, uint64_t offset) {
    if (getenv("INVALID_READ")) return length + 1;
    if (offset >= 9000) return 0;
    if (length > 9000 - offset) length = 9000 - offset;
    memset(buffer, 'x', length);
    return length;
}
int sched_setaffinity(pid_t pid, size_t size, const cpu_set_t *set) {
    if (pid != 0 || size != sizeof(*set) || !CPU_ISSET(0, set) ||
        CPU_COUNT(set) != 1 || getenv("AFFINITY_FAIL")) {
        errno = EINVAL;
        return -1;
    }
    return 0;
}
pid_t __real_waitpid(pid_t pid, int *status, int options);
pid_t __wrap_waitpid(pid_t pid, int *status, int options) {
    static int interrupted;
    if (getenv("WAIT_EINTR") && !interrupted++) {
        errno = EINTR;
        return -1;
    }
    return __real_waitpid(pid, status, options);
}
""")
        source = Path(__file__).with_name("control.c")
        include = source.parents[2] / "hsoc-stack/tools/gem5/include"
        subprocess.run(["cc", "-std=c11", "-O2", "-Wall", "-Wextra",
                        "-Werror", "-I", str(include), str(source), str(stub),
                        "-Wl,--wrap=waitpid", "-o", str(cls.binary)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_control_actions_and_arguments(self):
        expected = {"checkpoint": "checkpoint 0 0\n",
                    "switch": f"begin {0x5a535743} 0\n",
                    "begin": "begin 0 0\n", "end": "end 0 0\n"}
        for action, output in expected.items():
            with self.subTest(action=action):
                self.assertEqual(subprocess.check_output(
                    [str(self.binary), action], text=True), output)
        for arguments in ([], ["unknown"], ["begin", "extra"], ["run"]):
            self.assertEqual(subprocess.run(
                [str(self.binary), *arguments], capture_output=True).returncode, 2)

    def test_readfile_chunks_and_failures(self):
        self.assertEqual(subprocess.check_output(
            [str(self.binary), "readfile"]), b"x" * 9000)
        run = subprocess.run([str(self.binary), "readfile"],
                             env={**os.environ, "INVALID_READ": "1"},
                             capture_output=True)
        self.assertEqual(run.returncode, 1)

        with open("/dev/full", "wb") as output:
            run = subprocess.run([str(self.binary), "readfile"], stdout=output,
                                 stderr=subprocess.PIPE)
        self.assertEqual(run.returncode, 1)

    def test_run_command_roi_and_exit_status(self):
        cases = [(["/bin/sh", "-c", "printf 'child-output\\n'"], 0),
                 (["/bin/sh", "-c", "exit 7"], 7),
                 (["/bin/sh", "-c", "kill -TERM $$"], 143),
                 (["/no/such/gem5-command"], 127)]
        for command, status in cases:
            with self.subTest(command=command):
                run = subprocess.run([str(self.binary), "run", *command],
                                     capture_output=True, text=True,
                                     env={**os.environ, "WAIT_EINTR": "1"})
                self.assertEqual(run.returncode, status)
                lines = run.stdout.splitlines()
                self.assertIn("cpu=0 scope=whole-command", lines[0])
                self.assertEqual(lines[1:3], [f"begin {0x5a535743} 0", "begin 0 0"])
                self.assertEqual(lines[-1], "end 0 0")
                if status == 0:
                    self.assertEqual(lines[3:-1], ["child-output"])

    def test_affinity_failure_does_not_begin_roi(self):
        run = subprocess.run([str(self.binary), "run", "/bin/true"],
                             env={**os.environ, "AFFINITY_FAIL": "1"},
                             capture_output=True)
        self.assertEqual(run.returncode, 1)
        self.assertEqual(run.stdout, b"")


if __name__ == "__main__":
    unittest.main()
