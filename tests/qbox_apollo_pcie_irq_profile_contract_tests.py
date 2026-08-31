"""Profile construction, hash, and schema contract tests."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest
from qbox_apollo_pcie_irq_profile_support import ROOT, load_module

BUILDER_PATH = ROOT / "scripts/test/prepare_qbox_apollo_pcie_irq_profile.py"
VALIDATOR_PATH = ROOT / "scripts/test/validate_qbox_apollo_pcie_irq_runtime.py"
GATE = (
    ROOT
    / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current"
    / "fvp-reference-gate-current.json"
)
OVERLAY = (
    ROOT
    / "hsoc-stack/tools/qbox-platform/platforms/apollo/test-profile"
    / "apollo-qvp-pcie-irq-overlay.dtso"
)
AP_COMPUTE = (
    ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua"
)


def test_cli_requires_canonical_fvp_reference_gate(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(BUILDER_PATH),
            "--base-disk",
            str(tmp_path / "disk.img"),
            "--base-dtb",
            str(tmp_path / "base.dtb"),
            "--base-initramfs",
            str(tmp_path / "initramfs.cpio.gz"),
            "--output-dir",
            str(tmp_path / "profile"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2
    assert "--fvp-reference-gate" in result.stderr
    assert not (tmp_path / "profile").exists()


def test_reference_gate_is_schema_and_hash_bound(tmp_path: Path) -> None:
    builder = load_module(BUILDER_PATH, "qbox_profile_gate")
    receipt = builder.verify_reference_gate(GATE)
    assert receipt["reference_gate"] == "PASS"
    assert receipt["fvp_qualification"] == "UNSUPPORTED"
    assert receipt["qbox_allowed"] is True
    assert receipt["reason"] == "immutable_ecam_limit"
    assert builder.sha256(GATE) == builder.CANONICAL_FVP_GATE_SHA256
    copied = tmp_path / "copied-gate.json"
    copied.write_bytes(GATE.read_bytes())
    with pytest.raises(RuntimeError, match="fvp_reference_gate_path"):
        builder.verify_reference_gate(copied)


def test_platform_contract_rejects_collection_entry_size_eight(tmp_path: Path) -> None:
    builder = load_module(BUILDER_PATH, "qbox_profile_platform")
    builder.validate_platform_contract(AP_COMPUTE, OVERLAY)
    mutated = tmp_path / "ap_compute.lua"
    mutated.write_text(
        AP_COMPUTE.read_text(encoding="utf-8").replace(
            "gic_its_cte_size = 2;", "gic_its_cte_size = 8;", 1
        ),
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="collection_entry_size"):
        builder.validate_platform_contract(mutated, OVERLAY)


def test_profile_uses_shared_endpoint_bound_probe() -> None:
    builder = load_module(BUILDER_PATH, "qbox_profile_guest")
    assert builder.GUEST_PROBE == ROOT / "scripts/test/apollo_pcie_its_guest.sh"
    assert builder.SHARED_VALIDATOR == (
        ROOT / "scripts/test/validate_apollo_pcie_its_runtime.py"
    )
    legacy_guest = (
        ROOT
        / "hsoc-stack/tools/qbox-platform/platforms/apollo/test-profile"
        / "apollo-qvp-pcie-irq-test.sh"
    ).read_text(encoding="utf-8")
    assert "__QBOX_PCIE_BDF__" not in legacy_guest
    assert "apollo-pcie-its-guest" in legacy_guest


def test_mode_input_manifests_are_distinct_and_provenanced() -> None:
    builder = load_module(BUILDER_PATH, "qbox_profile_modes")
    common = {
        "base_disk": {"path": "/input/disk", "size": 1, "sha256": "1" * 64},
        "base_dtb": {"path": "/input/dtb", "size": 1, "sha256": "2" * 64},
        "base_initramfs": {
            "path": "/input/initramfs",
            "size": 1,
            "sha256": "3" * 64,
        },
    }
    invocation = ["builder", "--output-dir", "/profile"]
    msix = builder.mode_input_payload("msix", common, "4" * 64, "5" * 64, invocation)
    intx = builder.mode_input_payload("intx", common, "4" * 64, "6" * 64, invocation)
    msix_bytes = builder.canonical_bytes(msix)
    intx_bytes = builder.canonical_bytes(intx)
    assert hashlib.sha256(msix_bytes).hexdigest() != hashlib.sha256(intx_bytes).hexdigest()
    assert msix["mode"] == "msix"
    assert msix["boot"]["forbidden_arguments"] == ["pci=nomsi"]
    assert intx["boot"]["required_arguments"] == ["pci=nomsi"]
    assert msix["command"] == {"argv": invocation, "profile_mode": "msix"}
    assert intx["command"] == {"argv": invocation, "profile_mode": "intx"}


def test_validator_cli_requires_profile_manifest() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert "--profile-manifest" in result.stdout
    validator = load_module(VALIDATOR_PATH, "qbox_profile_validator")
    assert validator.SHARED_VALIDATOR == (
        ROOT / "scripts/test/validate_apollo_pcie_its_runtime.py"
    )


def test_profile_schema_is_strict_json() -> None:
    schema_path = ROOT / "tests/schemas/apollo-qbox-pcie-irq-profile.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["$schema"].endswith("2020-12/schema")
    assert schema["additionalProperties"] is False


def test_mode_input_manifest_has_a_strict_schema() -> None:
    builder = load_module(BUILDER_PATH, "qbox_mode_schema")
    artifact = {"path": "/input/base", "size": 1, "sha256": "1" * 64}
    inputs = {
        name: artifact
        for name in (
            "base_disk",
            "base_dtb",
            "base_initramfs",
            "builder",
            "gic_overlay_module",
            "artifact_module",
            "inspect_module",
            "contract_module",
            "profile_schema",
            "input_schema",
            "fvp_reference_gate",
            "linux_image",
            "uki_stub",
            "uki_os_release",
            "kernel_release",
            "ukify",
            "uki_manifest",
            "overlay_source",
            "guest_probe",
            "guest_wrapper",
            "profile_validator",
            "shared_validator",
            "ap_compute",
        )
    }
    payload = builder.mode_input_payload(
        "msix", inputs, "2" * 64, "3" * 64, ["builder", "--output-dir", "/profile"]
    )
    schema_path = ROOT / "tests/schemas/apollo-qbox-pcie-irq-input.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(payload)
    contract_payload = payload["contract"]
    assert isinstance(contract_payload, dict)
    contract_payload["collection_entry_size"] = 8
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(payload)
