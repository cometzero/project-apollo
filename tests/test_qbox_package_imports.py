from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_si_cl1_pfdi_probe_imports_from_workspace_package() -> None:
    result = subprocess.run(
        [sys.executable, "-c", "import scripts.run.qbox_si_cl1_pfdi_probe"],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
