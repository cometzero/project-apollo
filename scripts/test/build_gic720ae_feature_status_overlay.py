#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/build_gic720ae_feature_status_overlay.py --help
# 3. Or: python3 scripts/test/build_gic720ae_feature_status_overlay.py --help
# ──────────────────
"""Build a canonical content-addressed GIC-720AE status overlay."""

from __future__ import annotations

import argparse
from pathlib import Path

from gic720ae_contract import (
    ContractError,
    JsonArray,
    JsonObject,
    JsonValue,
    canonical_bytes,
    json_object,
    require_list,
    require_sha,
    require_string,
    sha_bytes,
    sha_path,
    validate,
    write_json,
    yaml_object,
)


PRODUCERS = {"pre_freeze": 19, "ap": 40, "si": 41, "all": 42}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", choices=("ap", "si", "all"), required=True)
    parser.add_argument("--phase", choices=("pre_freeze", "post_freeze"), required=True)
    parser.add_argument("--criteria", type=Path, required=True)
    parser.add_argument("--plan", type=Path, default=Path(".omo/plans/apollo-gic720ae-implementation.md"))
    parser.add_argument("--base-status", type=Path)
    parser.add_argument("--qualification", type=Path)
    parser.add_argument("--source-state", type=Path)
    parser.add_argument("--source-freeze", type=Path)
    parser.add_argument("--replace-prefreeze-rows", action="store_true")
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def rows_from_qualification(path: Path | None) -> list[JsonValue]:
    if path is None:
        return []
    value = json_object(path)
    rows = value.get("rows", [])
    return require_list(rows, "qualification.rows")


def build(args: argparse.Namespace) -> JsonObject:
    matrix = yaml_object(args.criteria)
    criteria_rows = require_list(matrix.get("rows"), "criteria.rows")
    input_shas: list[str] = []
    if args.base_status is not None:
        base = json_object(args.base_status)
        validate(base, args.schema)
        input_shas.append(sha_path(args.base_status))
    qualification_rows = rows_from_qualification(args.qualification)
    selected: JsonArray = []
    for row in criteria_rows:
        if not isinstance(row, dict):
            raise ContractError("malformed_input", "criteria row")
        domain = require_string(row.get("domain"), "row.domain")
        if args.domain == "all" or domain == args.domain:
            selected.append(row)
    statuses: JsonArray = []
    by_id = {
        require_string(row.get("id"), "row.id"): row
        for row in qualification_rows
        if isinstance(row, dict)
    }
    for criterion in selected:
        if not isinstance(criterion, dict):
            raise ContractError("malformed_input", "criterion")
        row_id = require_string(criterion.get("id"), "row.id")
        provided = by_id.get(row_id)
        if isinstance(provided, dict):
            statuses.append(provided)
        else:
            scope = (
                "unverifiable"
                if criterion.get("applicability") == "conditional"
                else "active"
            )
            statuses.append({
                "id": row_id,
                "status": "BLOCKED",
                "scope_class": scope,
                "reason": "missing_current_evidence",
                "evidence": [],
            })
    producer = PRODUCERS["pre_freeze"] if args.phase == "pre_freeze" else PRODUCERS[args.domain]
    input_overlay_shas: JsonArray = []
    input_overlay_shas.extend(sorted(input_shas))
    result: JsonObject = {
        "format_version": 1,
        "criteria_sha": sha_path(args.criteria),
        "plan_sha": sha_path(args.plan),
        "phase": args.phase,
        "producer_task": producer,
        "input_overlay_shas": input_overlay_shas,
        "rows": statuses,
    }
    if args.phase == "pre_freeze":
        if args.source_state is None or args.source_freeze is not None:
            raise ContractError("phase_lineage_mismatch", "pre_freeze needs source-state only")
        source = json_object(args.source_state)
        result["source_state_sha"] = require_sha(
            source.get("source_state_sha"), "source_state_sha"
        )
    else:
        if args.source_freeze is None or args.source_state is not None:
            raise ContractError("phase_lineage_mismatch", "post_freeze needs source-freeze only")
        result["source_freeze_sha"] = sha_path(args.source_freeze)
    validate(result, args.schema)
    return result


def main() -> int:
    args = parse_args()
    try:
        result = build(args)
        data = canonical_bytes(result)
        digest = sha_bytes(data)
        write_json(args.output_dir / f"feature-status-{digest}.json", result)
        return 0
    except ContractError as error:
        write_json(args.output_dir / "feature-status-error.json", {
            "format_version": 1, "verdict": "FAIL", "reason": error.reason,
        })
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
