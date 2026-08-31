from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

from scripts.test import gic720ae_pcie_irq_validation_contract as contract
from scripts.test import gic720ae_pcie_irq_validation_negative as negative
from scripts.test import gic720ae_pcie_irq_validation_provenance as provenance
from scripts.test import gic720ae_pcie_irq_validation_workflow as workflow

ROOT = Path(__file__).resolve().parents[1]
PROVENANCE_SCHEMA = json.loads(contract.PROVENANCE_SCHEMA.read_text(encoding="utf-8"))
RESULT_SCHEMA = json.loads(contract.RESULT_SCHEMA.read_text(encoding="utf-8"))


def file_binding() -> contract.JsonObject:
    return {"path": "/tmp/ap-map-audit.json", "sha256": "a" * 64, "size": 17}


def repository_binding() -> contract.JsonObject:
    digest: contract.JsonObject = {"sha256": "0" * 64, "size": 0}
    return {
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


def bound_provenance() -> contract.JsonObject:
    repository = repository_binding()
    return {
        "schema_version": 1,
        "status": "PASS",
        "closure_state": "AUDIT_BOUND",
        "fvp_qualification": "UNSUPPORTED",
        "files": {
            f"fixture_{index}": {
                "path": f"/tmp/fixture-{index}",
                "sha256": "0" * 64,
                "size": 1,
            }
            for index in range(20)
        },
        "repositories": {
            name: copy.deepcopy(repository)
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
        "qbox_binary": {
            "status": "PRESENT",
            "path": "/tmp/platforms-vp",
            "sha256": "b" * 64,
        },
        "command_order": list(provenance.COMMANDS),
        "ap_memory_map_audit": file_binding(),
    }


def child_binding() -> contract.JsonObject:
    return {
        "command": ["python3", "adapter.py"],
        "returncode": 0,
        "log": {"path": "/tmp/child.log", "sha256": "c" * 64, "size": 0},
    }


def phase_records(audit_status: str) -> list[contract.JsonValue]:
    statuses = {
        "parse_hash_inputs": "PASS",
        "validate_fvp_gate": "PASS",
        "provenance_preflight": "PASS",
        "qbox_build": "PASS",
        "ap_memory_map_audit": audit_status,
        "task9_qualification": "PASS" if audit_status == "PASS" else "NOT_RUN",
        "task10_comparison": "PASS" if audit_status == "PASS" else "NOT_RUN",
        "cleanup_audit": "PASS" if audit_status == "PASS" else "NOT_RUN",
        "atomic_final_result": "PASS" if audit_status == "PASS" else "NOT_RUN",
    }
    return [{"name": name, "status": statuses[name]} for name in workflow.PHASES]


def full_pass_result() -> contract.JsonObject:
    payload = negative.base_result()
    payload.update(
        {
            "overall": "PASS",
            "reason": "ok",
            "qbox": {
                "started": True,
                "build": "PASS",
                "binary": {
                    "status": "PRESENT",
                    "path": "/tmp/platforms-vp",
                    "sha256": "b" * 64,
                },
            },
            "ap_memory_map_audit": {
                "status": "PASS",
                "artifact": file_binding(),
            },
            "task9": {
                "status": "PASS",
                "artifacts": {f"artifact_{index}": index for index in range(15)},
            },
            "task10": {
                "status": "PASS",
                "comparison": file_binding(),
            },
            "children": {
                name: child_binding()
                for name in ("qbox_build", "ap_memory_map_audit", "task9", "task10")
            },
            "cleanup": {
                "status": "PASS",
                "residual_pids": [],
                "receipts": {"msix": file_binding(), "intx": file_binding()},
            },
            "phases": phase_records("PASS"),
        }
    )
    return payload


def audit_fail_result() -> contract.JsonObject:
    payload = negative.base_result()
    payload.update(
        {
            "qbox": {
                "started": False,
                "build": "PASS",
                "binary": {
                    "status": "PRESENT",
                    "path": "/tmp/platforms-vp",
                    "sha256": "b" * 64,
                },
            },
            "ap_memory_map_audit": {"status": "FAIL"},
            "children": {
                "qbox_build": child_binding(),
                "ap_memory_map_audit": child_binding(),
            },
            "phases": phase_records("FAIL"),
        }
    )
    return payload


def validate(payload: contract.JsonObject, schema: contract.JsonObject) -> None:
    jsonschema.Draft202012Validator(schema).validate(payload)


def test_current_valid_schema_shapes_are_pinned() -> None:
    # Given: current bound provenance plus full, audit-fail, and pre-audit results.
    preaudit = negative.base_result()

    # When: every legitimate shape crosses its current schema boundary.
    validate(bound_provenance(), PROVENANCE_SCHEMA)
    validate(full_pass_result(), RESULT_SCHEMA)
    validate(audit_fail_result(), RESULT_SCHEMA)
    validate(preaudit, RESULT_SCHEMA)

    # Then: no valid current contract is rejected before schema hardening.


def test_provenance_rejects_removed_ap_map_binding() -> None:
    # Given: valid emitted provenance with its mandatory audit binding removed.
    payload = bound_provenance()
    del payload["ap_memory_map_audit"]

    # When/Then: the provenance schema fails closed.
    with pytest.raises(jsonschema.ValidationError):
        validate(payload, PROVENANCE_SCHEMA)


def test_preaudit_provenance_accepts_explicit_not_run_state() -> None:
    # Given: an internal pre-audit closure that has not yet bound fresh bytes.
    payload = bound_provenance()
    payload["closure_state"] = "PRE_AUDIT"
    payload["ap_memory_map_audit"] = {"status": "NOT_RUN"}

    # When: the typed pre-audit state crosses the provenance boundary.
    validate(payload, PROVENANCE_SCHEMA)

    # Then: only the explicit NOT_RUN variant is accepted before audit execution.


def test_bound_provenance_rejects_not_run_audit_state() -> None:
    # Given: emitted AUDIT_BOUND provenance whose binding is replaced by NOT_RUN.
    payload = bound_provenance()
    payload["ap_memory_map_audit"] = {"status": "NOT_RUN"}

    # When/Then: post-audit provenance cannot masquerade as an internal closure.
    with pytest.raises(jsonschema.ValidationError):
        validate(payload, PROVENANCE_SCHEMA)


@pytest.mark.parametrize(
    ("field", "invalid"),
    (("path", ""), ("sha256", "bad"), ("size", -1)),
)
def test_provenance_rejects_invalid_ap_map_binding_fields(
    field: str,
    invalid: contract.JsonValue,
) -> None:
    # Given: emitted provenance with one malformed audit identity field.
    payload = bound_provenance()
    audit = contract.object_value(
        payload.get("ap_memory_map_audit"), "test_ap_map_binding"
    )
    audit[field] = invalid

    # When/Then: malformed path, hash, and size cannot validate.
    with pytest.raises(jsonschema.ValidationError):
        validate(payload, PROVENANCE_SCHEMA)


@pytest.mark.parametrize("mutation", ("removed", "not_run"))
def test_audit_fail_result_requires_fail_status(
    mutation: str,
) -> None:
    # Given: a result whose phase records that the AP-map audit ran and failed.
    payload = audit_fail_result()
    if mutation == "removed":
        del payload["ap_memory_map_audit"]
    else:
        payload["ap_memory_map_audit"] = {"status": "NOT_RUN"}

    # When/Then: missing or NOT_RUN audit state contradicts the FAIL phase.
    with pytest.raises(jsonschema.ValidationError):
        validate(payload, RESULT_SCHEMA)


def test_pass_result_requires_bound_audit_artifact() -> None:
    # Given: an overall PASS result with audit PASS but no artifact identity.
    payload = full_pass_result()
    payload["ap_memory_map_audit"] = {"status": "PASS"}

    # When/Then: PASS without an exact binding fails closed.
    with pytest.raises(jsonschema.ValidationError):
        validate(payload, RESULT_SCHEMA)


@pytest.mark.parametrize(
    ("phase_status", "audit_status"),
    (("PASS", "FAIL"), ("FAIL", "PASS"), ("NOT_RUN", "FAIL")),
)
def test_result_rejects_audit_status_phase_contradictions(
    phase_status: str,
    audit_status: str,
) -> None:
    # Given: a failure result whose audit object contradicts its phase record.
    payload = audit_fail_result()
    payload["phases"] = phase_records(phase_status)
    payload["ap_memory_map_audit"] = {"status": audit_status}
    if audit_status == "PASS":
        payload["ap_memory_map_audit"] = {
            "status": "PASS",
            "artifact": file_binding(),
        }

    # When/Then: phase and audit status must agree exactly.
    with pytest.raises(jsonschema.ValidationError):
        validate(payload, RESULT_SCHEMA)
