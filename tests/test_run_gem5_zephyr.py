"""Launcher failures must not become successful benchmark measurements."""

import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/gem5"))
import run_zephyr as launcher


class ZephyrLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.binary = self.root / "gem5.opt"
        self.binary.write_text("fake executable")
        self.elf = self.root / "zephyr.elf"
        self.elf.write_bytes(b"ELF fixture")
        self.config = self.root / "configs/zena_si_cl1/run.py"
        self.config.parent.mkdir(parents=True)
        self.config.write_text("# config fixture")
        self.out = self.root / "output"

    def invoke(self, runner):
        argv = ["run_zephyr.py", "--headless", "--gem5", str(self.binary),
                "--elf", str(self.elf), "--out-dir", str(self.out)]
        with patch.object(launcher, "SOURCE", self.root), patch.object(sys, "argv", argv), \
             patch.object(launcher, "run", runner), contextlib.redirect_stdout(io.StringIO()):
            return launcher.main()

    def test_timeout_retains_failure_manifest(self):
        self.assertEqual(self.invoke(lambda *a: (-15, True, 0.1)), 124)
        manifest = json.loads((self.out / "manifest.json").read_text())
        self.assertEqual(manifest["returncode"], 124)
        self.assertTrue(manifest["timeout"])
        self.assertEqual(manifest["configuration_args"]["cpu"], "minor")
        self.assertEqual(json.loads((self.out / "result.json").read_text())["status"], "FAIL")

    def test_marker_only_is_not_benchmark_pass(self):
        def run(*args):
            (self.out / "system.platform.terminal").write_text("SI_CL1_RESULT status=PASS\n")
            return 0, False, 0.1
        self.assertNotEqual(self.invoke(run), 0)
        self.assertEqual(json.loads((self.out / "result.json").read_text())["status"], "FAIL")

    def test_existing_output_is_never_reused(self):
        self.out.mkdir()
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.invoke(lambda *a: self.fail("simulator should not run"))

    def test_nonfinite_timeout_is_rejected_before_input_resolution(self):
        for timeout in ("nan", "inf", "-inf"):
            with self.subTest(timeout=timeout), \
                 patch.object(sys, "argv", ["run_zephyr.py", "--timeout=" + timeout]), \
                 patch.object(launcher, "resolve") as resolve, \
                 contextlib.redirect_stderr(io.StringIO()), \
                 self.assertRaises(SystemExit) as stopped:
                launcher.main()
            self.assertEqual(stopped.exception.code, 2)
            resolve.assert_not_called()


if __name__ == "__main__":
    unittest.main()
