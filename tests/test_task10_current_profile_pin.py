from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from pcie_irq_test_support import gate_fixture, profile_fixture, qbox_comparator
from scripts.test import compare_apollo_pcie_its_runtime as comparator


def test_task10_rejects_byte_modified_pinned_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Local pins exercise byte identity without manufacturing qualification evidence.
    gate = tmp_path / "gate.json"
    profile = tmp_path / "profile.json"
    gate.write_text(json.dumps(gate_fixture()), encoding="utf-8")
    profile.write_text(json.dumps(profile_fixture(tmp_path)), encoding="utf-8")
    profile_before, gate_before = profile.read_bytes(), gate.read_bytes()
    monkeypatch.setattr(comparator, "FVP_SHA256", hashlib.sha256(gate_before).hexdigest())
    monkeypatch.setattr(comparator, "PROFILE_SHA256", hashlib.sha256(profile_before).hexdigest())
    mutated_profile = tmp_path / "mutated-profile.json"
    mutated_profile.write_bytes(profile_before + b"\n ")
    assert json.loads(mutated_profile.read_bytes()) == json.loads(profile_before)
    output = tmp_path / "comparison.json"

    result = comparator.compare(gate, mutated_profile, tmp_path / "absent-run", output)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert result == 1
    assert payload["status"] == "FAIL"
    assert payload["reason"] == "profile_hash"
    assert payload["fvp_qualification"] == "UNSUPPORTED"
    assert payload["device_equivalence"] == "NOT_COMPARABLE"
    assert profile.read_bytes() == profile_before
    assert gate.read_bytes() == gate_before
    assert not (tmp_path / "absent-run").exists()


def test_task10_rejects_runtime_with_different_gate_pin(tmp_path: Path) -> None:
    # A run from another gate cannot be paired with the currently pinned profile.
    qbox = qbox_comparator()
    (tmp_path / "qualification.json").write_text(json.dumps({
        "run_id": tmp_path.name,
        "schema_version": 1,
        "status": "pass",
        "pins": {"fvp_reference_gate_sha256": "0" * 64},
    }), encoding="utf-8")

    with pytest.raises(qbox.BoundaryError, match="qualification_fvp_pin"):
        qbox.qbox_rows(profile_fixture(tmp_path), tmp_path)
