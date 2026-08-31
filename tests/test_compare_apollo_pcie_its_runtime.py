from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
COMPARATOR = ROOT / "scripts/test/compare_apollo_pcie_its_runtime.py"
SCHEMA = ROOT / "tests/schemas/apollo-pcie-its-boundary-comparison.schema.json"
FVP = ROOT / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current/fvp-reference-gate-current.json"
PROFILE = ROOT / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current/canonical-profile-v4/manifest.json"
F3_RUN = ROOT / ".omo/evidence/apollo-gic-its/final/F3/cycle2/run-current-r5/task9"
type JsonValue = str | int | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
type Json = dict[str, JsonValue]


def msix_input_sha256_from_profile(profile: Path) -> str:
    manifest = json.loads(profile.read_text(encoding="utf-8"))
    assert isinstance(manifest, dict)
    artifacts = manifest["artifacts"]
    assert isinstance(artifacts, dict)
    input_manifest = artifacts["msix_input_manifest"]
    assert isinstance(input_manifest, dict)
    declared_path = input_manifest["path"]
    declared_sha256 = input_manifest["sha256"]
    assert isinstance(declared_path, str)
    assert isinstance(declared_sha256, str)
    observed_sha256 = hashlib.sha256(Path(declared_path).read_bytes()).hexdigest()
    assert observed_sha256 == declared_sha256
    return observed_sha256


def invoke(tmp_path: Path, *, fvp: Path = FVP, profile: Path = PROFILE, run: Path = F3_RUN) -> tuple[int, Json]:
    output = tmp_path / "comparison.json"
    result = subprocess.run(
        [
            sys.executable,
            str(COMPARATOR),
            "--fvp-reference-gate", str(fvp),
            "--qbox-profile-manifest", str(profile),
            "--qbox-run-root", str(run),
            "--output", str(output),
        ],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    return result.returncode, json.loads(output.read_text(encoding="utf-8"))


def relocated_run_root(tmp_path: Path) -> Path:
    if not F3_RUN.is_dir():
        pytest.fail(f"planned F3 Task11 run root is missing: {F3_RUN}")
    copied = tmp_path / "relocated" / "task9"
    copied.mkdir(parents=True)
    for name in ("qualification.json", "pcie-runtime-validation.json", "spi-runtime-validation.json"):
        shutil.copy2(F3_RUN / name, copied / name)
    for mode in ("msix", "intx"):
        target = copied / mode
        target.mkdir()
        for name in ("result.json", "qbox-primary-console.log"):
            shutil.copy2(F3_RUN / mode / name, target / name)
        coverage = json.loads((F3_RUN / f"{mode}-coverage-audit.json").read_text(encoding="utf-8"))
        coverage["runtime_result"] = str((target / "result.json").absolute())
        (copied / f"{mode}-coverage-audit.json").write_text(json.dumps(coverage), encoding="utf-8")
    return copied


def module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("task10_comparator", COMPARATOR)
    assert spec is not None and spec.loader is not None
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def test_boundary_comparator_emits_only_supported_boundary_rows(tmp_path: Path) -> None:
    # Given: the canonical profile binds a concrete MSI-X input manifest.
    expected_msix_input_sha256 = msix_input_sha256_from_profile(PROFILE)

    # When: the comparator reads the current authoritative F3 runtime closure.
    returncode, payload = invoke(tmp_path)

    # Then: the output binding agrees with both the profile declaration and bytes.
    assert returncode == 0
    assert payload["status"] == "PASS"
    assert payload["fvp_qualification"] == "UNSUPPORTED"
    assert payload["device_equivalence"] == "NOT_COMPARABLE"
    bindings = payload["bindings"]
    assert isinstance(bindings, dict)
    assert bindings["fvp_gate_schema_version"] == 1
    assert bindings["pcie_runtime_schema_version"] == 2
    assert bindings["msix_input_sha256"] == expected_msix_input_sha256
    raw_rows = payload["rows"]
    assert isinstance(raw_rows, dict)
    rows: dict[str, Json] = {key: value for key, value in raw_rows.items() if isinstance(value, dict)}
    assert rows["fvp_ecam_first_read_serror"]["status"] == "UNSUPPORTED"
    assert rows["qbox_msix_its_lpi"]["status"] == "PASS"
    assert rows["qbox_intx_hwirq333"]["status"] == "PASS"
    assert rows["qbox_spi_zero_pci_delta"]["status"] == "PASS"
    assert rows["qbox_intx_ap_map"]["status"] == "PASS"
    assert not any("fvp_msix" in str(row["id"]) or "parity" in str(row["id"]) for row in rows.values())
    validator = jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    validator.validate(payload)
    for mutation in (
        lambda value: value["rows"].pop("qbox_intx_ap_map"),
        lambda value: value["bindings"].pop("run_id"),
        lambda value: value["rows"].update({"unknown": dict(value["rows"]["qbox_intx_ap_map"])}),
        lambda value: value["bindings"].update({"unknown": "0" * 64}),
        lambda value: value["rows"]["qbox_msix_its_lpi"]["bindings"].append("unknown"),
    ):
        forged = json.loads(json.dumps(payload))
        mutation(forged)
        with pytest.raises(jsonschema.ValidationError):
            validator.validate(forged)
    comparator = module()
    with pytest.raises(comparator.BoundaryError):
        comparator.strict_rows(list(rows.values())[:-1] + [dict(rows["qbox_msix_its_lpi"], id="qbox_msix_endpoint")], bindings)
    wrong_ref = json.loads(json.dumps(list(rows.values())))
    wrong_ref[4]["bindings"] = ["intx_rootfs_sha256"]
    with pytest.raises(comparator.BoundaryError):
        comparator.strict_rows(wrong_ref, bindings)


def test_boundary_comparator_accepts_relocated_authoritative_f3_root(tmp_path: Path) -> None:
    returncode, payload = invoke(tmp_path, run=relocated_run_root(tmp_path))
    assert returncode == 0
    assert payload["status"] == "PASS"
    bindings = payload["bindings"]
    assert isinstance(bindings, dict)
    assert bindings["run_id"] == "task9"


def test_boundary_comparator_fails_closed_when_run_binding_is_stale(tmp_path: Path) -> None:
    stale = relocated_run_root(tmp_path)
    qualification = stale / "qualification.json"
    payload = json.loads(qualification.read_text(encoding="utf-8"))
    payload["run_id"] = "forged-run"
    qualification.write_text(json.dumps(payload), encoding="utf-8")
    returncode, report = invoke(tmp_path, run=stale)
    assert returncode == 1
    assert report["status"] == "FAIL"
    assert report["reason"] == "run_id"


def test_boundary_comparator_rejects_forged_fvp_positive_claim(tmp_path: Path) -> None:
    forged = tmp_path / "fvp.json"
    payload = json.loads(FVP.read_text(encoding="utf-8"))
    payload["claims"]["physical_its_delivery"] = True
    forged.write_text(json.dumps(payload), encoding="utf-8")
    returncode, report = invoke(tmp_path, fvp=forged)
    assert returncode == 1
    assert report["status"] == "FAIL"
    assert report["reason"] in {"fvp_hash", "fvp_claims"}


def test_boundary_comparator_rejects_unbound_rootfs_and_nested_ap_map_mutant(
    tmp_path: Path,
) -> None:
    copied = relocated_run_root(tmp_path)
    coverage = copied / "msix-coverage-audit.json"
    payload = json.loads(coverage.read_text(encoding="utf-8"))
    payload["ap_9_1_1_memory_map"]["passed"] = False
    coverage.write_text(json.dumps(payload), encoding="utf-8")
    qualification = copied / "qualification.json"
    payload = json.loads(qualification.read_text(encoding="utf-8"))
    payload["modes"]["msix"]["rootfs_sha256"] = "0" * 64
    qualification.write_text(json.dumps(payload), encoding="utf-8")
    comparator = module()
    with pytest.raises(comparator.BoundaryError):
        comparator.qbox_rows(json.loads(PROFILE.read_text(encoding="utf-8")), copied)


@pytest.mark.parametrize("input_name", ["fvp", "profile"])
def test_boundary_comparator_fails_closed_for_malformed_or_wrong_input_classes(
    tmp_path: Path, input_name: str
) -> None:
    cases = {
        "missing": tmp_path / "missing.json",
        "scalar": tmp_path / "scalar.json",
        "array": tmp_path / "array.json",
        "malformed": tmp_path / "malformed.json",
        "wrong_version": tmp_path / "wrong-version.json",
    }
    cases["scalar"].write_text("1", encoding="utf-8")
    cases["array"].write_text("[]", encoding="utf-8")
    cases["malformed"].write_text("{", encoding="utf-8")
    wrong_version = json.loads(FVP.read_text(encoding="utf-8"))
    wrong_version["schema_version"] = 99
    cases["wrong_version"].write_text(json.dumps(wrong_version), encoding="utf-8")
    for path in cases.values():
        arguments = {input_name: path}
        returncode, report = invoke(tmp_path, **arguments)
        assert returncode == 1
        assert report["status"] == "FAIL"
