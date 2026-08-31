from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPARATOR = ROOT / "scripts/test/compare_apollo_pcie_its_runtime.py"
FVP = (
    ROOT
    / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current"
    / "fvp-reference-gate-current.json"
)
PROFILE = (
    ROOT
    / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current"
    / "canonical-profile-v4/manifest.json"
)
CURRENT_RUN = ROOT / ".omo/evidence/apollo-gic-its/final/F3/cycle2/run-current-r5/task9"
HISTORICAL_RUN = (
    ROOT
    / ".omo/evidence/apollo-gic-its/task-11/verifier-remediation-1"
    / "run-20260829T060747Z/task9"
)


def test_task10_rejects_byte_modified_current_profile(tmp_path: Path) -> None:
    # Given: a parseable copy of the current profile with changed bytes.
    mutated_profile = tmp_path / "mutated-profile.json"
    mutated_profile.write_bytes(PROFILE.read_bytes() + b"\n ")
    assert mutated_profile.read_bytes() != PROFILE.read_bytes()
    assert isinstance(json.loads(mutated_profile.read_text(encoding="utf-8")), dict)
    output = tmp_path / "comparison.json"
    profile_before = PROFILE.read_bytes()
    fvp_before = FVP.read_bytes()

    # When: the real Task10 CLI evaluates the modified profile and current r5 run.
    result = subprocess.run(
        [
            sys.executable,
            str(COMPARATOR),
            "--fvp-reference-gate",
            str(FVP),
            "--qbox-profile-manifest",
            str(mutated_profile),
            "--qbox-run-root",
            str(CURRENT_RUN),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    # Then: the hash gate fails closed without changing authoritative inputs.
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert result.returncode == 1
    assert payload["status"] == "FAIL"
    assert payload["reason"] == "profile_hash"
    assert payload["fvp_qualification"] == "UNSUPPORTED"
    assert payload["device_equivalence"] == "NOT_COMPARABLE"
    assert PROFILE.read_bytes() == profile_before
    assert FVP.read_bytes() == fvp_before


def test_task10_rejects_historical_runtime_under_final_profile(tmp_path: Path) -> None:
    # Given: the final profile paired with a historical pre-regeneration run.
    output = tmp_path / "comparison.json"
    # When: the real Task10 CLI evaluates the mixed closure.
    result = subprocess.run(
        [
            sys.executable,
            str(COMPARATOR),
            "--fvp-reference-gate",
            str(FVP),
            "--qbox-profile-manifest",
            str(PROFILE),
            "--qbox-run-root",
            str(HISTORICAL_RUN),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    # Then: it fails closed at the first historical qualification pin.
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert result.returncode == 1
    assert payload["status"] == "FAIL"
    assert payload["reason"] == "qualification_fvp_pin"
