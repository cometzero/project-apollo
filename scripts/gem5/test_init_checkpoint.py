# SPDX-License-Identifier: BSD-3-Clause
"""Exercise the real init checkpoint block against disposable sysfs fixtures."""
import subprocess
import tempfile
import unittest
from pathlib import Path

INIT = (Path(__file__).resolve().parents[2] /
        "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/initrdscripts/"
        "nexios-gem5-init/init")


class InitCheckpointTests(unittest.TestCase):
    def run_fixture(self, clusters=1, failure=None, checkpoint=True):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "run").mkdir()
            (root / "cmdline").write_text("gem5.checkpoint=1" if checkpoint else "console=ttyAMA0")
            checks_quiesced, checks_restored = [], []
            for cluster in range(clusters):
                zone = root / f"sys/class/thermal/thermal_zone{cluster}"
                policy = root / f"sys/devices/system/cpu/cpufreq/policy{cluster * 4}"
                zone.mkdir(parents=True)
                policy.mkdir(parents=True)
                mode = "enabled" if cluster % 2 == 0 else "disabled"
                governor = "schedutil" if cluster % 2 == 0 else "performance"
                (zone / "type").write_text(f"cluster{cluster}-thermal\n")
                (zone / "mode").write_text(mode + "\n")
                (policy / "scaling_driver").write_text("scmi\n")
                (policy / "scaling_governor").write_text(governor + "\n")
                checks_quiesced += [f'test "$(cat {zone}/mode)" = disabled || return 1',
                                    f'test "$(cat {policy}/scaling_governor)" = userspace || return 1']
                checks_restored += [f'test "$(cat {zone}/mode)" = {mode} || return 1',
                                   f'test "$(cat {policy}/scaling_governor)" = {governor} || return 1']
            if failure == "quiesce":
                (root / "sys/class/thermal/thermal_zone0/mode").unlink()
            if failure == "empty-governor":
                (root / "sys/devices/system/cpu/cpufreq/policy0/scaling_governor").write_text("")

            source = INIT.read_text()
            definitions = source[:source.index("mkdir -p /proc")]
            block = source[source.index('case " $(cat /proc/cmdline) "'):source.index("if test -s /run/gem5-workload.sh")]
            script = definitions + '''
failed_init() { echo failed >> EVENTS; exit 90; }
sleep() {
    test "$1" = 0.05 || return 1
    echo settle >> EVENTS
    SLEEP_RESULT
}
gem5_control() {
    case "$1" in
        checkpoint)
            QUIESCED_CHECKS
            echo checkpoint >> EVENTS
            CHECKPOINT_RESULT
            ;;
        readfile)
            RESTORED_CHECKS
            echo readfile >> EVENTS
            echo 'echo workload'
            ;;
        *) return 1 ;;
    esac
}
''' + block
            script = script.replace("EVENTS", str(root / "events"))
            script = script.replace("QUIESCED_CHECKS", "\n".join(checks_quiesced) or ":")
            script = script.replace("RESTORED_CHECKS", "\n".join(checks_restored) or ":")
            script = script.replace("SLEEP_RESULT", "return 1" if failure == "sleep" else ":")
            checkpoint_result = ":"
            if failure == "checkpoint":
                checkpoint_result = "return 1"
            if failure == "restore":
                path = root / "sys/devices/system/cpu/cpufreq/policy0/scaling_governor"
                checkpoint_result = f"rm {path} && mkdir {path}"
            script = script.replace("CHECKPOINT_RESULT", checkpoint_result)
            # Replace only literal production paths, before fixture paths are present.
            script = script.replace("/proc/cmdline", str(root / "cmdline"))
            script = script.replace("/usr/bin/gem5-control", "gem5_control")
            script = script.replace("/run/gem5-", str(root / "run/gem5-"))
            # The fixtures already contain absolute /tmp paths; match only source prefixes.
            script = script.replace(" in /sys/", f" in {root}/sys/")
            script = script.replace('> "/sys/', f'> "{root}/sys/')
            result = subprocess.run(["sh", "-c", script], capture_output=True, text=True, timeout=5)
            events = (root / "events").read_text().splitlines() if (root / "events").exists() else []
            workload = root / "run/gem5-workload.sh"
            return result, events, workload.read_text() if workload.exists() else None

    def test_ap4_ap16_restore_before_readfile(self):
        for clusters in (1, 4):
            with self.subTest(clusters=clusters):
                result, events, workload = self.run_fixture(clusters)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(events, ["settle", "checkpoint", "readfile"])
                self.assertEqual(workload, "echo workload\n")
                self.assertIn("NEXIOS_GEM5_CHECKPOINT_POWER_QUIESCED", result.stdout)
                self.assertIn("NEXIOS_GEM5_CHECKPOINT_POWER_RESTORED", result.stdout)

    def test_no_scmi_or_no_checkpoint_preserves_flow(self):
        for clusters, checkpoint, events in ((0, True, ["checkpoint", "readfile"]),
                                            (1, False, ["readfile"])):
            result, actual, workload = self.run_fixture(clusters, checkpoint=checkpoint)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(actual, events)
            self.assertEqual(workload, "echo workload\n")
            self.assertNotIn("CHECKPOINT_POWER_", result.stdout)

    def test_failures_never_read_workload(self):
        for failure in ("quiesce", "empty-governor", "sleep", "checkpoint", "restore"):
            with self.subTest(failure=failure):
                result, events, workload = self.run_fixture(failure=failure)
                self.assertEqual(result.returncode, 90, result.stderr)
                self.assertNotIn("readfile", events)
                self.assertIsNone(workload)
                self.assertEqual(events[-1], "failed")


if __name__ == "__main__":
    unittest.main()
