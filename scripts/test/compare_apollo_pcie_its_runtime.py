#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.0"]
# ///
# ─── How to run ───
# python3 scripts/test/compare_apollo_pcie_its_runtime.py --help
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apollo_pcie_its_boundary_contract as contract
import apollo_pcie_its_boundary_io as boundary_io
from apollo_pcie_its_comparator_qbox import BoundaryError, qbox_rows

ROOT = Path(__file__).resolve().parents[2]
FVP_SHA256 = "5ceb377244eb0e4fddd6e4346a701fa1a75185d0dc689d2e396c917cb3549a82"
PROFILE_SHA256 = "d0fd532fc4e07edbe02d62ae06cb6afb84663b69cdf0f139729bc3a3f65cf03b"
SCHEMA = ROOT / "tests/schemas/apollo-pcie-its-boundary-comparison.schema.json"
type JsonValue = str | int | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
type Json = dict[str, JsonValue]


def need(value: JsonValue | None, expected: JsonValue, reason: str) -> None:
    if value != expected:
        raise BoundaryError(reason)


def object_at(value: JsonValue | None, reason: str) -> Json:
    if not isinstance(value, dict):
        raise BoundaryError(reason)
    return value


def rows_for_fvp(gate: Json) -> list[JsonValue]:
    need(gate.get("schema_version"), 1, "fvp_schema_version")
    need(gate.get("reference_gate"), "PASS", "fvp_reference_gate")
    need(gate.get("fvp_qualification"), "UNSUPPORTED", "fvp_qualification")
    need(gate.get("reason"), "immutable_ecam_limit", "fvp_reason")
    need(gate.get("configuration_applied"), True, "fvp_configuration")
    need(gate.get("qbox_started"), False, "fvp_qbox_started")
    claims = object_at(gate.get("claims"), "fvp_claims")
    if any(claims.get(name) is not False for name in ("endpoint_enumeration", "physical_its_delivery", "qbox_equivalence")):
        raise BoundaryError("fvp_claims")
    cleanup = object_at(gate.get("cleanup"), "fvp_cleanup")
    need(cleanup.get("status"), "PASS", "fvp_cleanup")
    return [{"id": item.key, "scope": item.scope, "status": "UNSUPPORTED", "detail": item.detail, "bindings": list(item.refs)} for item in contract.ROWS if item.scope == "FVP"]


def strict_rows(rows: list[JsonValue], bindings: Json) -> Json:
    records = [object_at(item, "row") for item in rows]
    identifiers = [record.get("id") for record in records]
    if set(bindings) != contract.BINDINGS or len(identifiers) != len(set(identifiers)) or set(identifiers) != set(contract.ROW_BY_KEY):
        raise BoundaryError("row_ids")
    for record in records:
        refs = contract.normalize_refs(record.get("bindings"))
        required = contract.ROW_BY_KEY[str(record.get("id"))].refs
        if refs != tuple(sorted(required)):
            raise BoundaryError("row_bindings")
    return {str(record["id"]): record for record in records}


def compare(fvp_reference_gate: Path, qbox_profile_manifest: Path, qbox_run_root: Path, output: Path) -> int:
    bindings: Json = {
        "fvp_reference_gate_sha256": boundary_io.digest(fvp_reference_gate) if fvp_reference_gate.is_file() else "",
        "qbox_profile_manifest_sha256": boundary_io.digest(qbox_profile_manifest) if qbox_profile_manifest.is_file() else "",
    }
    try:
        need(bindings["fvp_reference_gate_sha256"], FVP_SHA256, "fvp_hash")
        need(bindings["qbox_profile_manifest_sha256"], PROFILE_SHA256, "profile_hash")
        gate = boundary_io.load_json(fvp_reference_gate, "fvp_json")
        rows = rows_for_fvp(gate)
        bindings["fvp_gate_schema_version"] = gate["schema_version"]
        qbox_rows_value, qbox_bindings = qbox_rows(boundary_io.load_json(qbox_profile_manifest, "profile_json"), qbox_run_root)
        bindings.update(qbox_bindings)
        payload: Json = {"schema_version": 1, "status": "PASS", "reason": "ok", "fvp_qualification": "UNSUPPORTED", "device_equivalence": "NOT_COMPARABLE", "bindings": bindings, "rows": strict_rows(rows + qbox_rows_value, bindings)}
    except (BoundaryError, OSError, TypeError, ValueError, KeyError, IndexError) as error:
        payload = {"schema_version": 1, "status": "FAIL", "reason": str(error) or error.__class__.__name__, "fvp_qualification": "UNSUPPORTED", "device_equivalence": "NOT_COMPARABLE", "bindings": bindings, "rows": {}}
    try:
        jsonschema.Draft202012Validator(boundary_io.load_json(SCHEMA, "output_schema")).validate(payload)
    except (BoundaryError, jsonschema.ValidationError):
        payload["status"] = "FAIL"
        payload["reason"] = "output_schema"
    boundary_io.atomic_write(output, payload)
    return 0 if payload["status"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare immutable Task 10 evidence closures.")
    parser.add_argument("--fvp-reference-gate", type=Path, required=True)
    parser.add_argument("--qbox-profile-manifest", type=Path, required=True)
    parser.add_argument("--qbox-run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    return compare(args.fvp_reference_gate, args.qbox_profile_manifest, args.qbox_run_root, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
