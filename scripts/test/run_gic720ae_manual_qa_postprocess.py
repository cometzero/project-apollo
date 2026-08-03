#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/run_gic720ae_manual_qa_postprocess.py --help
# 3. Or: python3 scripts/test/run_gic720ae_manual_qa_postprocess.py --help
# ──────────────────
"""Postprocess external manual-QA artifacts without creating approval."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from pathlib import Path

from gic720ae_contract import (
    ContractError, JsonValue, json_object, sha_path, validate, write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test-negative", type=Path)
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--reviewer-receipt", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--envelope", type=Path)
    parser.add_argument("--receipt-schema", type=Path)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def verify_required_surfaces(record: Mapping[str, JsonValue]) -> None:
    if record.get("qbox") is True and record.get("fvp") is False:
        raise ContractError("missing_fvp_evidence", "manual QA")
    if "qbox" in record or "fvp" in record:
        if record.get("qbox") is not True or record.get("fvp") is not True:
            raise ContractError("malformed_input", "manual QA surfaces")


def main() -> int:
    args = parse_args()
    try:
        if args.self_test_negative is not None:
            verify_required_surfaces(json_object(args.self_test_negative))
        paths = (args.reviewer_receipt, args.plan, args.envelope)
        if args.run_dir is None or any(path is None or not path.is_file() for path in paths):
            raise ContractError("missing_input", "manual QA")
        qualification = args.run_dir / "result.json"
        if not qualification.is_file():
            raise ContractError("missing_input", "qualification")
        result = json_object(qualification)
        receipt = json_object(args.reviewer_receipt)
        if args.receipt_schema is not None:
            validate(receipt, args.receipt_schema)
        if result.get("verdict") != "PASS":
            raise ContractError("qualification_failed", "runtime")
        verdict = receipt.get("verdict")
        if verdict not in {"APPROVE", "REJECT"}:
            raise ContractError("malformed_input", "reviewer verdict")
        payload = {
            "format_version": 1, "verdict": verdict,
            "reason": "reviewer_decision_verified",
            "qualification_sha": sha_path(qualification),
            "reviewer_receipt_sha": sha_path(args.reviewer_receipt),
        }
        validate(payload, args.schema)
        code = 0 if verdict == "APPROVE" else 1
    except ContractError as error:
        payload = {
            "format_version": 1, "verdict": "REJECT", "reason": error.reason,
            "qualification_sha": "0" * 64, "reviewer_receipt_sha": "0" * 64,
        }
        code = 1
    write_json(args.output, payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
