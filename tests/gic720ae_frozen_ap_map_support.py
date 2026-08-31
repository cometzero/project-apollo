from __future__ import annotations

from pathlib import Path

from scripts.test import gic720ae_pcie_irq_validation_ap_map as ap_map
from scripts.test import gic720ae_pcie_irq_validation_contract as contract
from scripts.test import gic720ae_pcie_irq_validation_provenance as provenance


def provenance_base(binary: Path) -> contract.JsonObject:
    digest: contract.JsonObject = {"sha256": "0" * 64, "size": 0}
    repository: contract.JsonObject = {
        "path": "/tmp/repository",
        "head": "0" * 40,
        "scope_paths": ["scope"],
        "expected_state": "DIRTY_ALLOWED",
        "staged_diff": dict(digest),
        "worktree_diff": dict(digest),
        "untracked_manifest_sha256": "0" * 64,
        "untracked_sources": [],
        "status_entries": [],
    }
    return {
        "schema_version": 1,
        "status": "PASS",
        "closure_state": "PRE_AUDIT",
        "fvp_qualification": "UNSUPPORTED",
        "files": {
            name: {
                "path": f"/tmp/fixture-{index}",
                "sha256": "0" * 64,
                "size": 1,
            }
            for index, name in enumerate(
                (
                    "fvp_reference_gate",
                    "qbox_profile_manifest",
                    "source_contract",
                    *(f"fixture_{item}" for item in range(17)),
                )
            )
        },
        "repositories": {
            name: dict(repository)
            for name in (
                "superproject",
                "linux",
                "trusted_firmware_a",
                "scp_firmware",
                "meta_hsoc_bsp",
                "qbox_platform",
                "qbox_core",
                "qemu",
            )
        },
        "qbox_binary": provenance.binary_identity(binary),
        "ap_memory_map_audit": {"status": "NOT_RUN"},
        "command_order": list(provenance.COMMANDS),
    }


def bound_closure(
    root: Path, binary: Path, audit_text: str = '{"passed": true}\n'
) -> contract.JsonObject:
    root.mkdir()
    audit = root / "ap-map-audit.json"
    audit.write_text(audit_text, encoding="utf-8")
    config = contract.RunConfig(
        root / "gate.json",
        root / "profile.json",
        root,
        None,
        None,
        10,
        binary,
    )
    return provenance.bind_ap_map_audit(
        provenance_base(binary),
        config,
        ap_map.task11_artifact(root, audit),
    )
