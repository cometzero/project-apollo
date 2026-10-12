"""Process ownership and argument checks for the idle measurement harness."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/test"))
import measure_scp_idle as idle


class IdleHarnessTest(unittest.TestCase):
    def test_launcher_owns_runtime_until_measurement_ends(self):
        args = SimpleNamespace(out_dir=Path("run"), si_cl0_image=Path("si.bin"),
                               rse_flash=Path("flash.img"), monitor_port=18110)
        command = idle.launch_command(args)
        self.assertIn("--keep-running-after-pass", command)
        self.assertIn("--foreground-runtime", command)
        self.assertNotIn("--stats", command)
        self.assertEqual(command[command.index("--timeout") + 1], "0")

    def test_owned_native_rejects_foreign_and_reused_pid(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            (out / "board-launch.json").write_text(json.dumps(dict(pid=30, start_ticks=100)))
            launcher = SimpleNamespace(pid=10)
            with patch.object(idle, "process_identity", side_effect=lambda pid: {30: (20, 100), 20: (10, 50)}[pid]):
                self.assertEqual(idle.owned_native(out, launcher), 30)
            with patch.object(idle, "process_identity", return_value=(1, 100)):
                self.assertIsNone(idle.owned_native(out, launcher))
            with patch.object(idle, "process_identity", return_value=(10, 101)):
                self.assertIsNone(idle.owned_native(out, launcher))

    def test_positive_duration(self):
        self.assertEqual(idle.positive("30"), 30)
        for value in ("nan", "inf", "0", "-1"):
            with self.assertRaises(argparse.ArgumentTypeError):
                idle.positive(value)


if __name__ == "__main__":
    unittest.main()
