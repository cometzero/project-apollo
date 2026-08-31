from __future__ import annotations

from pathlib import Path
import sys
from typing import assert_never, Literal

import pytest

from scripts.test import gic720ae_pcie_irq_validation_ap_map as ap_map
from scripts.test import gic720ae_pcie_irq_validation_contract as contract
from scripts.test import qbox_apollo_pcie_irq_task9 as task9
from scripts.test import qbox_apollo_pcie_irq_task9_process as process
from scripts.test import run_qbox_apollo_pcie_irq_task9 as standalone


Mutation = Literal["malformed", "false_status", "wrong_hash", "wrong_size", "symlink"]


def test_standalone_task9_retains_validated_default_ap_map(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: the legacy standalone CLI without an AP-map override.
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "task9",
            "--fvp-reference-gate",
            "gate.json",
            "--profile-manifest",
            "profile.json",
            "--run-root",
            "run-root",
        ],
    )

    # When: standalone arguments are parsed.
    args = standalone.parse_args()

    # Then: compatibility selects only the historical validated default.
    assert args.ap_map_audit == standalone.DEFAULT_AP_MAP_AUDIT


def write_validator(path: Path, coverage_audit: Path | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if coverage_audit is None:
        source = (
            "import argparse, json\n"
            "p=argparse.ArgumentParser();p.add_argument('--output',required=True);"
            "a,_=p.parse_known_args();open(a.output,'w').write('{}\\n')\n"
        )
    else:
        citation = (
            "a.ap_map_audit" if coverage_audit == Path() else repr(str(coverage_audit))
        )
        source = (
            "import argparse, json\n"
            "p=argparse.ArgumentParser();p.add_argument('--ap-map-audit',required=True);"
            "p.add_argument('--output',required=True);a,_=p.parse_known_args();"
            f"cited={citation};"
            "payload={'passed':True,'ap_9_1_1_memory_map':"
            "{'passed':True,'audit_path':cited}};"
            "open(a.output,'w').write(json.dumps(payload)+'\\n')\n"
        )
    path.write_text(source, encoding="utf-8")


def validator_inputs(tmp_path: Path) -> process.ValidatorInputs:
    run_root = tmp_path / "run/task9"
    for mode in ("msix", "intx"):
        (run_root / mode).mkdir(parents=True)
    audit = tmp_path / "run/ap-map-audit.json"
    audit.write_text('{"passed": true}\n', encoding="utf-8")
    artifact = ap_map.task11_artifact(tmp_path / "run", audit)
    mode_input = task9.ModeInput(tmp_path / "disk", "1" * 64, "2" * 64)
    pins = task9.PinClosure(
        "3" * 64, "4" * 64, "5" * 64, mode_input, mode_input, "6" * 64
    )
    return process.ValidatorInputs(run_root, pins, tmp_path / "profile.json", artifact)


def configure_validators(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    cited_audit: Path | None,
) -> None:
    pair = tmp_path / "scripts/pair.py"
    spi = tmp_path / "scripts/spi.py"
    coverage = tmp_path / "scripts/coverage.py"
    write_validator(pair)
    write_validator(spi)
    write_validator(coverage, cited_audit or Path())
    monkeypatch.setattr(task9, "ROOT", tmp_path)
    monkeypatch.setattr(process, "PAIR_VALIDATOR", pair)
    monkeypatch.setattr(process, "SPI_VALIDATOR", spi)
    monkeypatch.setattr(process, "COVERAGE_AUDIT", coverage)


def test_task9_coverage_cites_exact_run_local_ap_map(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given: Task9 validators and one hash-bound run-local AP-map receipt.
    inputs = validator_inputs(tmp_path)
    configure_validators(tmp_path, monkeypatch, None)
    before = inputs.ap_map_artifact.path.read_bytes()

    # When: the real validator subprocess boundary runs for both IRQ modes.
    process.run_validators(inputs)

    # Then: both coverage results cite the same immutable receipt.
    for mode in ("msix", "intx"):
        coverage = contract.load_object(
            inputs.run_root / f"{mode}-coverage-audit.json", "test_coverage"
        )
        memory = contract.object_value(
            coverage.get("ap_9_1_1_memory_map"), "test_ap_map"
        )
        assert memory["audit_path"] == str(inputs.ap_map_artifact.path)
    assert inputs.ap_map_artifact.path.read_bytes() == before


def test_task9_coverage_rejects_external_ap_map_citation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given: a validator that substitutes another run's success-looking receipt.
    inputs = validator_inputs(tmp_path)
    external = tmp_path / "other-run/ap-map-audit.json"
    external.parent.mkdir()
    external.write_text('{"passed": true}\n', encoding="utf-8")
    configure_validators(tmp_path, monkeypatch, external)

    # When/Then: Task9 rejects the first coverage result at the path boundary.
    with pytest.raises(contract.ValidationError, match="task9_ap_map_path"):
        process.run_validators(inputs)


@pytest.mark.parametrize(
    "mutation",
    ("malformed", "false_status", "wrong_hash", "wrong_size", "symlink"),
)
def test_task11_ap_map_boundary_rejects_malformed_identity(
    tmp_path: Path, mutation: Mutation
) -> None:
    # Given: one malformed run-local audit identity.
    root = tmp_path / "run"
    root.mkdir()
    audit = root / "ap-map-audit.json"
    audit.write_text('{"passed": true}\n', encoding="utf-8")
    expected = ap_map.ExpectedDigest(contract.digest(audit), audit.stat().st_size)
    match mutation:
        case "malformed":
            audit.write_text("{bad", encoding="utf-8")
        case "false_status":
            audit.write_text('{"passed": false}\n', encoding="utf-8")
        case "wrong_hash":
            expected = ap_map.ExpectedDigest("0" * 64, expected.size)
        case "wrong_size":
            expected = ap_map.ExpectedDigest(expected.sha256, expected.size + 1)
        case "symlink":
            target = root / "target.json"
            audit.replace(target)
            audit.symlink_to(target)
        case unreachable:
            assert_never(unreachable)

    # When/Then: parsing fails before the artifact can enter Task9.
    with pytest.raises(contract.ValidationError):
        ap_map.task11_artifact(root, audit, expected)
