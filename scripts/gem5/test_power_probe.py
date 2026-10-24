# SPDX-License-Identifier: BSD-3-Clause
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class PowerProbeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("cc"), "host C compiler required")
    def test_scmi_policy_sensor_and_checksum_contract(self):
        source = Path(__file__).with_name("power_probe.c").resolve()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            harness = root / "probe.c"
            harness.write_text(
                '#define sched_setaffinity test_setaffinity\n'
                f'#define POWER_SYSFS_ROOT "{root / "sys"}"\n'
                f'#include "{source}"\n'
                'int test_setaffinity(pid_t pid, size_t size, const cpu_set_t *set) {\n'
                ' return pid == 0 && size == sizeof(*set) && CPU_ISSET(0, set) '
                '&& CPU_COUNT(set) == 1 ? 0 : -1;\n}\n')
            binary = root / "probe"
            subprocess.run(["cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                            str(harness), "-o", str(binary)], check=True,
                           capture_output=True)

            def populate(cpus):
                shutil.rmtree(root / "sys", ignore_errors=True)
                for cluster in range(cpus // 4):
                    policy = root / "sys/devices/system/cpu/cpufreq" / f"policy{cluster * 4}"
                    policy.mkdir(parents=True)
                    (policy / "scaling_driver").write_text("scmi\n")
                    (policy / "scaling_cur_freq").write_text("1800000\n")
                    zone = root / "sys/class/thermal" / f"thermal_zone{cluster}"
                    zone.mkdir(parents=True)
                    (zone / "type").write_text(f"cluster{cluster}-thermal\n")
                    (zone / "temp").write_text("40000\n")

            def run(cpus):
                return subprocess.run([str(binary), str(cpus), "1800000"],
                                      text=True, capture_output=True, timeout=5)

            for cpus in (4, 16):
                with self.subTest(cpus=cpus):
                    populate(cpus)
                    result = run(cpus)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("checksum=16781312 expected=16781312", result.stdout)
                    self.assertEqual(result.stdout.count("APOLLO_POWER_POLICY"), cpus // 4)
                    self.assertEqual(result.stdout.count("APOLLO_POWER_SENSOR"), cpus // 4)
                    for policy in (root / "sys/devices/system/cpu/cpufreq").iterdir():
                        self.assertEqual((policy / "scaling_setspeed").read_text(), "1800000")
                        self.assertEqual((policy / "scaling_governor").read_text(), "userspace\n")

            populate(4)
            self.assertNotEqual(run(16).returncode, 0)
            policy = root / "sys/devices/system/cpu/cpufreq/policy0"
            zone = root / "sys/class/thermal/thermal_zone0"
            for filename, invalid in ((policy / "scaling_driver", "other"),
                                      (policy / "scaling_cur_freq", "2000000"),
                                      (zone / "type", "unknown"),
                                      (zone / "temp", "not-a-number")):
                with self.subTest(filename=filename.name):
                    original = filename.read_text()
                    filename.write_text(invalid)
                    self.assertNotEqual(run(4).returncode, 0)
                    filename.write_text(original)
            result = subprocess.run([str(binary), "8", "1800000"], capture_output=True)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
