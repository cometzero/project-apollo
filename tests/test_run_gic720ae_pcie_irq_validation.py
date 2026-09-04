from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Literal, assert_never

import jsonschema
import pytest

from scripts.test import gic720ae_pcie_irq_validation_contract as validation_contract
from scripts.test import gic720ae_pcie_irq_validation_negative as negative
from scripts.test import gic720ae_pcie_irq_validation_provenance as provenance

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/run_gic720ae_pcie_irq_validation.py"
GATE = (
    ROOT
    / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current/fvp-reference-gate-current.json"
)
PROFILE = (
    ROOT
    / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current"
    / "canonical-profile-v4/manifest.json"
)
FrozenVariant = Literal[
    "appended_newline", "leading_space", "trailing_spaces", "reordered_keys"
]


@pytest.fixture(scope="module")
def current_frozen(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("frozen") / "provenance.json"
    config = validation_contract.RunConfig(
        GATE.resolve(), PROFILE.resolve(), path.parent / "unused", None, None, 1800
    )
    provenance.atomic_write(path, provenance.build(config))
    return path


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def object_field(
    payload: validation_contract.JsonObject, key: str
) -> validation_contract.JsonObject:
    value = payload[key]
    assert isinstance(value, dict)
    return value


def list_field(
    payload: validation_contract.JsonObject, key: str
) -> list[validation_contract.JsonValue]:
    value = payload[key]
    assert isinstance(value, list)
    return value


def int_field(payload: validation_contract.JsonObject, key: str) -> int:
    value = payload[key]
    assert isinstance(value, int)
    return value


def str_field(payload: validation_contract.JsonObject, key: str) -> str:
    value = payload[key]
    assert isinstance(value, str)
    return value


def test_dry_run_reports_exact_phase_order_without_writes(tmp_path: Path) -> None:
    # Given: canonical immutable FVP and QBox profile inputs.
    run_root = tmp_path / "run-20260829T000000Z"

    # When: the complete orchestrator is planned in dry-run mode.
    result = run_cli(
        "--dry-run",
        "--fvp-reference-gate",
        str(GATE),
        "--qbox-profile-manifest",
        str(PROFILE),
        "--run-root",
        str(run_root),
        "--timeout",
        "1800",
    )

    # Then: every process boundary is ordered and no evidence is created.
    assert result.returncode == 0, result.stderr
    phases = [
        "01 parse_hash_inputs",
        "02 validate_fvp_gate",
        "03 provenance_preflight",
        "04 qbox_build",
        "05 ap_memory_map_audit",
        "06 task9_qualification",
        "07 task10_comparison",
        "08 cleanup_audit",
        "09 atomic_final_result",
    ]
    positions = [result.stdout.index(phase) for phase in phases]
    assert positions == sorted(positions)
    assert "./yocto_build.sh --bsp" in result.stdout
    assert "audit_qbox_apollo_ap_memory_map.py" in result.stdout
    assert "run_gic720ae_pcie_irq_validation_task9.py" in result.stdout
    assert "run_gic720ae_pcie_irq_validation_task10.py" in result.stdout
    assert not run_root.exists()


def test_changed_gate_fails_before_build_or_qbox_start(tmp_path: Path) -> None:
    # Given: a schema-shaped gate whose content no longer matches the hard pin.
    gate = tmp_path / "changed-gate.json"
    payload = json.loads(GATE.read_text(encoding="utf-8"))
    payload["reason"] = "changed"
    gate.write_text(json.dumps(payload), encoding="utf-8")
    run_root = tmp_path / "run-20260829T000001Z"

    # When: full mode reaches immutable-input preflight.
    result = run_cli(
        "--fvp-reference-gate",
        str(gate),
        "--qbox-profile-manifest",
        str(PROFILE),
        "--run-root",
        str(run_root),
        "--timeout",
        "1",
    )

    # Then: the hard pin fails closed before any child/evidence boundary.
    assert result.returncode != 0
    assert "fvp_reference_gate_sha256" in result.stderr
    assert not run_root.exists()
    assert hashlib.sha256(gate.read_bytes()).hexdigest() != (
        "5ceb377244eb0e4fddd6e4346a701fa1a75185d0dc689d2e396c917cb3549a82"
    )


def test_negative_self_test_rejects_semantic_success_mutants() -> None:
    # Given: the repository-owned immutable inputs and negative matrix.
    # When: the isolated negative self-test is executed.
    result = run_cli("--self-test-negative")

    # Then: every mutant is rejected without starting FVP or QBox.
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    assert payload["fvp_started"] is False
    assert payload["qbox_started"] is False
    assert all(row["status"] == "PASS" for row in payload["matrix"])


def test_result_schema_accepts_zero_byte_success_child_log() -> None:
    # Given: a successful child whose adapter deliberately emitted no text.
    schema = json.loads(
        (
            ROOT / "tests/schemas/gic720ae-pcie-irq-validation-result.schema.json"
        ).read_text()
    )
    child = {
        "command": ["python3", "silent-adapter.py"],
        "returncode": 0,
        "log": {"path": "/tmp/silent.log", "sha256": "0" * 64, "size": 0},
    }

    # When: the child binding is validated at the result boundary.
    child_schema = {**schema["$defs"]["child"], "$defs": schema["$defs"]}

    # Then: silence remains a valid, hash-bound observable for rc0.
    jsonschema.Draft202012Validator(child_schema).validate(child)


def test_result_schema_rejects_build_pass_with_missing_binary() -> None:
    # Given: a QBox result that misleadingly claims build PASS for no binary.
    schema = json.loads(validation_contract.RESULT_SCHEMA.read_text(encoding="utf-8"))
    payload = negative.base_result()
    payload["qbox"] = {
        "started": False,
        "build": "PASS",
        "binary": {"status": "MISSING", "path": "/missing/platforms-vp"},
    }

    # When/Then: the result boundary rejects the contradictory identity.
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)


def test_identical_frozen_provenance_bytes_are_accepted(
    tmp_path: Path, current_frozen: Path
) -> None:
    # Given: an exact byte copy of the current frozen provenance closure.
    frozen = tmp_path / "identical.json"
    frozen.write_bytes(current_frozen.read_bytes())
    run_root = tmp_path / "run-identical"

    # When: dry-run validates the frozen closure before any child boundary.
    result = run_cli(
        "--dry-run",
        "--frozen-provenance",
        str(frozen),
        "--run-root",
        str(run_root),
    )

    # Then: the exact bytes pass and no run child is created.
    assert result.returncode == 0, result.stderr
    assert not run_root.exists()


@pytest.mark.parametrize(
    "variant",
    ["appended_newline", "leading_space", "trailing_spaces", "reordered_keys"],
)
def test_same_json_with_different_bytes_fails_before_qbox(
    tmp_path: Path, current_frozen: Path, variant: FrozenVariant
) -> None:
    # Given: schema-valid provenance with identical JSON meaning but changed bytes.
    original = current_frozen.read_bytes()
    payload = json.loads(original)
    match variant:
        case "appended_newline":
            mutated = original + b"\n"
        case "leading_space":
            mutated = b" " + original
        case "trailing_spaces":
            mutated = original.rstrip(b"\n") + b"  \n"
        case "reordered_keys":
            reordered = {key: payload[key] for key in reversed(tuple(payload))}
            mutated = (json.dumps(reordered, indent=2) + "\n").encode()
        case unreachable:
            assert_never(unreachable)
    frozen = tmp_path / f"{variant}.json"
    frozen.write_bytes(mutated)
    run_root = tmp_path / f"run-{variant}"

    # When: the preflight compares the frozen provenance.
    result = run_cli(
        "--dry-run",
        "--frozen-provenance",
        str(frozen),
        "--run-root",
        str(run_root),
    )

    # Then: byte drift is nonzero before QBox/build/result creation.
    assert result.returncode != 0
    assert "frozen_provenance_bytes" in result.stderr
    assert not run_root.exists()


def test_failed_build_records_missing_binary_without_claiming_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given: a real failing build child and an absent configured QBox binary.
    build = tmp_path / "yocto_build.sh"
    build.write_text("#!/bin/sh\nexit 17\n", encoding="utf-8")
    build.chmod(0o755)
    binary = tmp_path / "missing-platforms-vp"
    closure_path = tmp_path / "run/provenance.json"
    closure = provenance.empty_for_test(binary)
    config = validation_contract.RunConfig(
        GATE, PROFILE, tmp_path / "run", None, None, 10, binary
    )
    monkeypatch.setattr(validation_contract, "ROOT", tmp_path)

    # When: the execution boundary observes qbox_build rc=17.
    returncode = __import__(
        "scripts.test.gic720ae_pcie_irq_validation_execution", fromlist=["execute"]
    ).execute(config, closure)

    # Then: an atomic schema-valid FAIL result identifies the missing binary.
    payload = json.loads((tmp_path / "run/result.json").read_text(encoding="utf-8"))
    validation_contract.validate_schema(
        payload, validation_contract.RESULT_SCHEMA, "result_schema"
    )
    assert returncode == 1
    assert payload["overall"] == "FAIL"
    assert payload["qbox"] == {
        "started": False,
        "build": "FAIL",
        "binary": {"status": "MISSING", "path": str(binary)},
    }
    assert closure_path.is_file()
