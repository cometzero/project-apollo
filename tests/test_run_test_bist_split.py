from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/run_test_manifest.py"


def run_manifest(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_bist_markers_are_split_from_functional_to_extended(tmp_path: Path) -> None:
    functional_dir = tmp_path / "functional"
    extended_dir = tmp_path / "extended"

    functional = run_manifest(
        "write-conf",
        "--build-dir",
        "build",
        "--machine",
        "apollo-fvp",
        "--run-dir",
        str(functional_dir),
        "--kind",
        "functional",
    )
    extended = run_manifest(
        "write-conf",
        "--build-dir",
        "build",
        "--machine",
        "apollo-fvp",
        "--run-dir",
        str(extended_dir),
        "--kind",
        "extended",
    )

    assert functional.returncode == 0, functional.stderr
    assert extended.returncode == 0, extended.stderr
    functional_text = (functional_dir / "conf/oeqa-functional.conf").read_text(encoding="utf-8")
    extended_tokens = (
        (extended_dir / "conf/oeqa-extended.conf")
        .read_text(encoding="utf-8")
        .replace('"', " ")
        .split()
    )
    assert "test_02_safety_boot" not in functional_text
    assert "test_lbist" not in functional_text
    assert "test_mbist" not in functional_text
    assert "test_02_safety_boot.TestSafetyBoot.test_lbist" in extended_tokens
    assert "test_02_safety_boot.TestSafetyBoot.test_mbist" in extended_tokens
    assert "test_02_safety_boot" not in extended_tokens
