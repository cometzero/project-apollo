from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
QA_ROOT = ROOT / "qa-tests"


def test_run_test_runner_is_importable_from_qa_tests() -> None:
    # Given: an isolated import path containing only the repository QA root.
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(QA_ROOT)

    # When: the public runner module is invoked through that import path.
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "apollo_validation.cli",
            "root-run",
            "--root",
            str(ROOT),
            "--",
            "--help",
        ],
        cwd=ROOT,
        env=environment,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: qa-tests owns a complete, executable runner package.
    assert result.returncode == 0, result.stderr
