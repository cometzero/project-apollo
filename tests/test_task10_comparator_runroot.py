from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Protocol, runtime_checkable

import pytest
from pcie_irq_test_support import profile_fixture, qbox_comparator, require_archived_evidence

ROOT = Path(__file__).resolve().parents[1]
COMPARATOR = ROOT / "scripts/test/compare_apollo_pcie_its_runtime.py"
ADAPTER = ROOT / "scripts/test/run_gic720ae_pcie_irq_validation_task10.py"
FVP = ROOT / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current/fvp-reference-gate-current.json"
PROFILE = ROOT / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current/canonical-profile-v4/manifest.json"
TASK9 = ROOT / ".omo/evidence/apollo-gic-its/final/F3/cycle2/run-current-r5/task9"
type JsonValue = str | int | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
type Json = dict[str, JsonValue]

@runtime_checkable
class ComparatorModule(Protocol):
    qbox_rows: Callable[[Json, Path], tuple[list[JsonValue], Json]]


def invoke(script: Path, output: Path, run_root: Path) -> tuple[int, Json]:
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--fvp-reference-gate", str(FVP),
            "--qbox-profile-manifest", str(PROFILE),
            "--qbox-run-root", str(run_root),
            "--output", str(output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode, json.loads(output.read_text(encoding="utf-8"))


def copy_root(source: Path, destination: Path, *, run_id: str | None = None) -> None:
    destination.mkdir(parents=True)
    for name in ("qualification.json", "pcie-runtime-validation.json", "spi-runtime-validation.json"):
        shutil.copy2(source / name, destination / name)
    if run_id is not None:
        qualification = json.loads((destination / "qualification.json").read_text(encoding="utf-8"))
        qualification["run_id"] = run_id
        (destination / "qualification.json").write_text(json.dumps(qualification), encoding="utf-8")
    for mode in ("msix", "intx"):
        target = destination / mode
        target.mkdir()
        for name in ("result.json", "qbox-primary-console.log"):
            shutil.copy2(source / mode / name, target / name)
        coverage = json.loads((source / f"{mode}-coverage-audit.json").read_text(encoding="utf-8"))
        coverage["runtime_result"] = str((target / "result.json").absolute())
        (destination / f"{mode}-coverage-audit.json").write_text(json.dumps(coverage), encoding="utf-8")


def comparator_module() -> ComparatorModule:
    spec = importlib.util.spec_from_file_location("task10_comparator_runroot", COMPARATOR)
    assert spec is not None and spec.loader is not None
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    assert isinstance(loaded, ComparatorModule)
    return loaded


def test_task10_adapter_uses_explicit_comparator_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    spec = importlib.util.spec_from_file_location("task10_adapter_unit", ADAPTER)
    assert spec is not None and spec.loader is not None
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    paths = tuple(tmp_path / name for name in ("gate.json", "profile.json", "run", "output.json"))
    calls = []
    monkeypatch.setattr(adapter.comparator, "compare", lambda *args: calls.append(args) or 17)
    monkeypatch.setattr(sys, "argv", [str(ADAPTER),
        "--fvp-reference-gate", str(paths[0]), "--qbox-profile-manifest", str(paths[1]),
        "--qbox-run-root", str(paths[2]), "--output", str(paths[3]),
    ])
    assert adapter.main() == 17
    assert calls == [paths]


def test_comparator_binds_each_relocated_root_without_cross_run_leak(tmp_path: Path) -> None:
    require_archived_evidence(PROFILE, TASK9)
    comparator = comparator_module()
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    roots = tuple(
        tmp_path / "relocated" / run_id
        for run_id in ("authoritative-alpha", "authoritative-beta")
    )
    for root in roots:
        copy_root(TASK9, root, run_id=root.name)
    assert roots[0] != roots[1]
    expected_qualification_hashes = {
        root: hashlib.sha256((root / "qualification.json").read_bytes()).hexdigest()
        for root in roots
    }
    assert expected_qualification_hashes[roots[0]] != expected_qualification_hashes[roots[1]]

    for order in (roots, tuple(reversed(roots))):
        observed_rows: list[list[JsonValue]] = []
        for root in order:
            rows, bindings = comparator.qbox_rows(profile, root)
            observed_rows.append(rows)
            assert bindings["run_id"] == root.name
            assert bindings["qualification_sha256"] == expected_qualification_hashes[root]
        assert observed_rows[0] == observed_rows[1]


def test_comparator_accepts_relocated_bound_root(tmp_path: Path) -> None:
    require_archived_evidence(FVP, PROFILE, TASK9)
    relocated = tmp_path / "relocated" / "task9"
    copy_root(TASK9, relocated)
    returncode, payload = invoke(COMPARATOR, tmp_path / "relocated.json", relocated)
    assert returncode == 0
    assert payload["status"] == "PASS"


def test_comparator_rejects_symlink_root(tmp_path: Path) -> None:
    comparator = qbox_comparator()
    target = tmp_path / "target"
    target.mkdir()
    symlink = tmp_path / "task9"
    symlink.symlink_to(target, target_is_directory=True)
    with pytest.raises(comparator.BoundaryError, match="qbox_run_root"):
        comparator.run_root(symlink)


def test_comparator_rejects_missing_root_and_symlinked_artifact(tmp_path: Path) -> None:
    comparator = qbox_comparator()
    with pytest.raises(comparator.BoundaryError, match="qbox_run_root"):
        comparator.run_root(tmp_path / "missing")
    copied = tmp_path / "copied" / "task9"
    (copied / "msix").mkdir(parents=True)
    target = tmp_path / "result.json"
    target.write_text("{}", encoding="utf-8")
    result = copied / "msix/result.json"
    result.symlink_to(target)
    with pytest.raises(comparator.BoundaryError, match="msix_result"):
        comparator.contained_file(copied, "msix/result.json", "msix_result")


def test_comparator_rejects_coverage_escape_and_cross_run_mix(tmp_path: Path) -> None:
    comparator = qbox_comparator()
    escaped = tmp_path / "escaped" / "task9"
    escaped.mkdir(parents=True)
    coverage_path = escaped / "msix-coverage-audit.json"
    coverage = {"passed": True, "runtime_result": str(tmp_path / "another-run/result.json")}
    coverage_path.write_text(json.dumps(coverage), encoding="utf-8")
    with pytest.raises(comparator.BoundaryError, match="msix_coverage"):
        comparator.coverage_binding(escaped, "msix", escaped / "msix/result.json")

    # Minimal inputs reach the result binding gate, then deliberately fail there.
    mixed = tmp_path / "mixed" / "task9"
    (mixed / "msix").mkdir(parents=True)
    result_path = mixed / "msix/result.json"
    result_path.write_text('{"status": "original"}', encoding="utf-8")
    log = mixed / "msix/qbox-primary-console.log"
    log.write_text("host fixture only", encoding="utf-8")
    (mixed / "qualification.json").write_text(json.dumps({
        "run_id": mixed.name, "schema_version": 1, "status": "pass",
        "pins": {"fvp_reference_gate_sha256": comparator.FVP_SHA256,
                 "profile_manifest_sha256": comparator.PROFILE_SHA256},
        "process_cleanup": {"status": "PASS", "residual_pids": []},
        "modes": {"msix": {"result_sha256": hashlib.sha256(result_path.read_bytes()).hexdigest(),
                           "primary_log_sha256": hashlib.sha256(log.read_bytes()).hexdigest()}},
    }), encoding="utf-8")
    (mixed / "pcie-runtime-validation.json").write_text(json.dumps({
        "schema_version": 2, "status": "pass",
        "profile_manifest": {"sha256": comparator.PROFILE_SHA256},
    }), encoding="utf-8")
    result_path.write_text('{"status": "forged"}', encoding="utf-8")
    with pytest.raises(comparator.BoundaryError, match="msix_runner_binding"):
        comparator.qbox_rows(profile_fixture(tmp_path), mixed)
