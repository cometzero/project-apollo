from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.test import gic720ae_pcie_irq_validation_contract as contract
from scripts.test import gic720ae_pcie_irq_validation_execution as execution
from scripts.test import gic720ae_pcie_irq_validation_provenance as provenance

ROOT = Path(__file__).resolve().parents[1]
GATE = (
    ROOT
    / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current"
    / "fvp-reference-gate-current.json"
)
PROFILE = (
    ROOT
    / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current"
    / "canonical-profile-v4/manifest.json"
)


def test_successful_build_without_qbox_binary_records_atomic_fail(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given: a successful real build child that emits no QBox binary.
    build = tmp_path / "yocto_build.sh"
    build.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    build.chmod(0o755)
    binary = tmp_path / "missing-platforms-vp"
    run_root = tmp_path / "run"
    config = contract.RunConfig(GATE, PROFILE, run_root, None, None, 10, binary)
    closure = provenance.empty_for_test(binary)
    monkeypatch.setattr(contract, "ROOT", tmp_path)

    # When: the orchestrator checks the build product before Task9.
    returncode = execution.execute(config, closure)

    # Then: one schema-valid atomic FAIL identifies the missing binary.
    payload = json.loads((run_root / "result.json").read_text(encoding="utf-8"))
    contract.validate_schema(payload, contract.RESULT_SCHEMA, "result_schema")
    assert returncode == 1
    assert payload["overall"] == "FAIL"
    assert payload["reason"] == "qbox_binary_missing"
    assert payload["qbox"] == {
        "started": False,
        "build": "FAIL",
        "binary": {"status": "MISSING", "path": str(binary)},
    }
    assert payload["phases"][3] == {"name": "qbox_build", "status": "FAIL"}
