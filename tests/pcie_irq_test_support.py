"""Host-only inputs; these fixtures are never qualification evidence."""

from __future__ import annotations

from pathlib import Path
import importlib

import pytest


def qbox_comparator():
    # The public entry point establishes its sibling-module import path.
    importlib.import_module("scripts.test.compare_apollo_pcie_its_runtime")
    return importlib.import_module("apollo_pcie_its_comparator_qbox")


def gate_fixture() -> dict:
    return {
        "schema_version": 1, "reference_gate": "PASS",
        "fvp_qualification": "UNSUPPORTED", "reason": "immutable_ecam_limit",
        "configuration_applied": True, "qbox_started": False,
        "claims": {name: False for name in (
            "endpoint_enumeration", "physical_its_delivery", "qbox_equivalence",
        )},
        "cleanup": {"status": "PASS"},
    }


def require_archived_evidence(*paths: Path) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        pytest.skip("archived F2/F3 qualification replay requires: " + ", ".join(missing))


def profile_fixture(root: Path) -> dict:
    """Schema-valid metadata for early rejection tests, with no boot artifacts."""
    artifact = {"path": str(root / "not-a-runtime-artifact"), "size": 1, "sha256": "0" * 64}
    return {
        "schema_version": 2,
        "profile": "apollo-qvp-pcie-irq",
        "fvp_reference": {
            "path": str(root / "gate.json"), "sha256": "0" * 64,
            "reference_gate": "PASS", "fvp_qualification": "UNSUPPORTED",
            "reason": "immutable_ecam_limit",
        },
        "contract": {
            "bdf": "0000:00:01.0", "requester_id": 8, "device_id": 8,
            "stream_id": 64, "event_id_base": 0, "its_translator": "0x20850040",
            "legacy_gpex_spi_input": 301, "legacy_gic_intid": 333,
            "virtio_mmio_hwirq": 293, "collection_entry_size": 2,
        },
        "inputs": {name: dict(artifact) for name in (
            "base_disk", "base_dtb", "base_initramfs", "builder", "gic_overlay_module",
            "artifact_module", "inspect_module", "contract_module", "profile_schema",
            "input_schema", "fvp_reference_gate", "linux_image", "uki_stub",
            "uki_os_release", "kernel_release", "ukify", "uki_manifest", "overlay_source",
            "guest_probe", "guest_wrapper", "profile_validator", "shared_validator", "ap_compute",
        )},
        "modes": {mode: {
            "mode": mode, "boot_arguments": [],
            "artifacts": {name: dict(artifact) for name in ("input_manifest", "uki", "initramfs", "disk")},
        } for mode in ("msix", "intx")},
        "artifacts": {name: dict(artifact) for name in (
            "overlay", "dtb", "msix_input_manifest", "msix_uki", "msix_initramfs", "msix_disk",
            "intx_input_manifest", "intx_uki", "intx_initramfs", "intx_disk",
        )},
        "command": {"argv": ["host-test", "fixture"], "cwd": str(root)},
    }
