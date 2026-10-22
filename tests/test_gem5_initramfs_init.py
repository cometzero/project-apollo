# SPDX-License-Identifier: MIT
"""Exercise the guest init with fake tools; never mount or modify host paths."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


INIT = Path(__file__).resolve().parents[1] / (
    "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/initrdscripts/"
    "nexios-gem5-init/init"
)


class Gem5InitTests(unittest.TestCase):
    def run_init(self, failed_mount="", workload=False, cmdline="",
                 readfile=False, failed_control=""):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tools = root / "tools"
            tools.mkdir()
            console = root / "console"
            console.touch()
            workload_script = root / "workload.sh"
            if workload:
                workload_script.write_text(
                    'printf "workload dispatched source=etc\\n" >> "$TRACE"\n'
                    'exit 7\n'
                )
            runtime_script = root / "runtime-workload.sh"
            programs = {
                "mkdir": "exit 0\n",
                "mount": 'printf "mount %s\\n" "$*" >> "$TRACE"\n'
                         '[ "$2" != "$FAIL_MOUNT" ]\n',
                "grep": "exit 1\n",
                "cat": 'printf "%s\\n" "$CMDLINE"\n',
                "gem5-control":
                    'printf "control %s\\n" "$1" >> "$TRACE"\n'
                    '[ "$1" != "$FAIL_CONTROL" ] || exit 1\n'
                    'case "$1" in\n'
                    'checkpoint) ;;\n'
                    'readfile) printf "%s" "$READFILE" ;;\n'
                    '*) exit 99 ;;\nesac\n',
            }
            for name, body in programs.items():
                target = tools / name
                target.write_text("#!/bin/sh\n" + body)
                target.chmod(0o755)
            # Python preserves PS1; a noninteractive host shell may clear it.
            for name, body in {
                "sh": 'with open(os.environ["TRACE"], "a") as stream:\n'
                      '    stream.write("prompt " + os.environ["PS1"] + "\\n")\n',
                "setsid": 'with open(os.environ["TRACE"], "a") as stream:\n'
                          '    stream.write("setsid " + " ".join(sys.argv[1:]) + "\\n")\n'
                          'assert sys.argv[1] == "-c"\n'
                          'os.execvp(sys.argv[2], sys.argv[2:])\n',
            }.items():
                target = tools / name
                target.write_text(f"#!{sys.executable}\nimport os, sys\n" + body)
                target.chmod(0o755)
            source = INIT.read_text()
            replacements = {
                "export PATH=/sbin:/bin:/usr/sbin:/usr/bin":
                    f"export PATH='{tools}'",
                "/dev/console": str(console),
                "/etc/gem5-workload.sh": str(workload_script),
                "/run/gem5-workload.sh": str(runtime_script),
                "/usr/bin/gem5-workload": str(tools / "gem5-workload"),
                "/usr/bin/gem5-control": str(tools / "gem5-control"),
            }
            for original, replacement in replacements.items():
                self.assertIn(original, source)
                source = source.replace(original, replacement)
            wrapper = INIT.with_name("gem5-workload").read_text()
            for original in ("/run/gem5-workload.sh", "/etc/gem5-workload.sh"):
                self.assertIn(original, wrapper)
                wrapper = wrapper.replace(original, replacements[original])
            (tools / "gem5-workload").write_text(wrapper)
            (tools / "gem5-workload").chmod(0o755)
            script = root / "init"
            script.write_text(source)
            trace = root / "trace"
            run = subprocess.run(
                ["/bin/sh", str(script)],
                env={"PATH": str(tools), "TRACE": str(trace),
                     "FAIL_MOUNT": failed_mount, "CMDLINE": cmdline,
                     "FAIL_CONTROL": failed_control,
                     "READFILE": (
                         'printf "workload dispatched source=readfile\\n" >> "$TRACE"\n'
                         'exit 9\n' if readfile else "")},
                text=True, capture_output=True, timeout=5, check=True,
            )
            return run.stdout, console.read_text(), trace.read_text()

    def test_each_mount_failure_never_announces_ready(self):
        for mount in ("proc", "sysfs", "devtmpfs", "devpts", "tmpfs"):
            with self.subTest(mount=mount):
                stdout, console, trace = self.run_init(failed_mount=mount)
                self.assertIn("NEXIOS_GEM5_INITRAMFS_FAILED", stdout)
                self.assertNotIn("NEXIOS_GEM5_INITRAMFS_READY", stdout + console)
                self.assertIn("prompt nexios-gem5-failed# ", trace)
                self.assertNotIn("setsid", trace)
                self.assertNotIn("workload dispatched", trace)

    def test_normal_path_announces_ready_and_selects_console_shell(self):
        stdout, _, trace = self.run_init()
        self.assertEqual(stdout, "NEXIOS_GEM5_INITRAMFS_READY\n")
        self.assertEqual(trace.count("mount -t "), 5)
        self.assertIn("setsid -c sh\n", trace)
        self.assertIn("prompt nexios-gem5# ", trace)
        self.assertNotIn("workload dispatched", trace)
        self.assertIn("control readfile\n", trace)
        self.assertNotIn("control checkpoint", trace)

    def test_optional_workload_reports_status_before_console_shell(self):
        stdout, _, trace = self.run_init(workload=True)
        self.assertEqual(stdout, "NEXIOS_GEM5_INITRAMFS_READY\n"
                         "NEXIOS_GEM5_WORKLOAD_EXIT status=7\n")
        self.assertLess(trace.index("workload dispatched"), trace.index("setsid"))
        self.assertIn("prompt nexios-gem5# ", trace)

    def test_checkpoint_precedes_readfile_and_runtime_workload(self):
        stdout, _, trace = self.run_init(
            workload=True, readfile=True,
            cmdline="console=ttyAMA0 gem5.checkpoint=1 quiet",
        )
        self.assertEqual(stdout, "NEXIOS_GEM5_INITRAMFS_READY\n"
                         "NEXIOS_GEM5_WORKLOAD_EXIT status=9\n")
        self.assertLess(trace.index("control checkpoint"),
                        trace.index("control readfile"))
        self.assertLess(trace.index("control readfile"),
                        trace.index("workload dispatched source=readfile"))
        self.assertLess(trace.index("workload dispatched"), trace.index("setsid"))
        self.assertNotIn("source=etc", trace)

    def test_control_failure_prevents_workload_dispatch(self):
        for operation in ("checkpoint", "readfile"):
            with self.subTest(operation=operation):
                stdout, _, trace = self.run_init(
                    workload=True, readfile=True, failed_control=operation,
                    cmdline="gem5.checkpoint=1",
                )
                self.assertIn("NEXIOS_GEM5_INITRAMFS_FAILED", stdout)
                self.assertNotIn("workload dispatched", trace)
                self.assertNotIn("setsid", trace)
                self.assertIn("prompt nexios-gem5-failed# ", trace)
                if operation == "checkpoint":
                    self.assertNotIn("control readfile", trace)


if __name__ == "__main__":
    unittest.main()
