#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/audit_gic720ae_feature_matrix.py --help
# 3. Or: python3 scripts/test/audit_gic720ae_feature_matrix.py --help
# ──────────────────
"""Audit immutable GIC-720AE criteria against a status overlay."""

from __future__ import annotations

import argparse
from pathlib import Path

from gic720ae_contract import (
    ContractError,
    JsonArray,
    JsonObject,
    json_object,
    require_list,
    require_sha,
    require_string,
    sha_path,
    validate,
    write_json,
    yaml_object,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--status-overlay", type=Path, required=True)
    parser.add_argument("--status-schema", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def overlay_name_is_valid(path: Path) -> bool:
    if path.name == "feature-status-empty.json":
        return True
    return path.name == f"feature-status-{sha_path(path)}.json"


def audit(args: argparse.Namespace) -> tuple[int, JsonObject]:
    before = sha_path(args.matrix)
    matrix = yaml_object(args.matrix)
    overlay = json_object(args.status_overlay)
    validate(matrix, args.schema)
    validate(overlay, args.status_schema)
    if not overlay_name_is_valid(args.status_overlay):
        return 1, {
            "format_version": 1, "verdict": "FAIL",
            "reason": "overlay_filename_hash_mismatch",
            "criteria_unchanged": sha_path(args.matrix) == before,
            "active_rows": 0, "status_counts": {},
        }
    if require_sha(overlay.get("criteria_sha"), "criteria_sha") != before:
        return 1, {
            "format_version": 1, "verdict": "FAIL",
            "reason": "stale_evidence", "criteria_unchanged": True,
            "active_rows": 0, "status_counts": {},
        }
    criteria_rows = require_list(matrix.get("rows"), "rows")
    overlay_rows = require_list(overlay.get("rows"), "rows")
    statuses: dict[str, str] = {}
    for item in overlay_rows:
        if not isinstance(item, dict):
            raise ContractError("malformed_input", "overlay row")
        statuses[require_string(item.get("id"), "row.id")] = require_string(
            item.get("status"), "row.status"
        )
    active_ids: list[str] = []
    for item in criteria_rows:
        if not isinstance(item, dict):
            raise ContractError("malformed_input", "criteria row")
        row_id = require_string(item.get("id"), "row.id")
        applicability = require_string(item.get("applicability"), "applicability")
        if applicability == "active":
            active_ids.append(row_id)
    counts: JsonObject = {}
    resolved: JsonArray = []
    for row_id in active_ids:
        status = statuses.get(row_id, "BLOCKED")
        existing = counts.get(status, 0)
        if not isinstance(existing, int):
            raise ContractError("malformed_input", "status count")
        counts[status] = existing + 1
        resolved.append({"id": row_id, "status": status})
    result: JsonObject = {
        "format_version": 1,
        "verdict": "PASS",
        "reason": "criteria_valid",
        "criteria_sha": before,
        "criteria_unchanged": sha_path(args.matrix) == before,
        "active_rows": len(active_ids),
        "status_counts": counts,
        "rows": resolved,
        "evidence_root": str(args.evidence_root.resolve()),
    }
    return 0, result


def main() -> int:
    args = parse_args()
    try:
        code, result = audit(args)
    except ContractError as error:
        code = 1
        result = {
            "format_version": 1, "verdict": "FAIL", "reason": error.reason,
            "criteria_unchanged": False, "active_rows": 0, "status_counts": {},
        }
    write_json(args.output, result)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
