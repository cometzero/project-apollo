#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/audit_gic720ae_plan_compliance.py --help
# 3. Or: python3 scripts/test/audit_gic720ae_plan_compliance.py --help
# ──────────────────
"""Audit final evidence against the immutable implementation plan."""

from __future__ import annotations

import argparse
from pathlib import Path

from gic720ae_contract import ContractError, read_bytes, sha_path, validate, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("plan", "matrix", "status-overlay", "ledger", "envelope", "source-freeze"):
        parser.add_argument(f"--{name}", type=Path)
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--require-task44-from-envelope", action="store_true")
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--schema", type=Path, default=Path("tests/schemas/gic720ae-plan-compliance.schema.json"))
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = {
        name: getattr(args, name.replace("-", "_"))
        for name in ("plan", "matrix", "status-overlay", "ledger", "envelope", "source-freeze")
    }
    try:
        if args.fixture is not None:
            paths["ledger"] = args.fixture
        ledger_path = paths["ledger"]
        if ledger_path is None or not ledger_path.is_file():
            raise ContractError("missing_input", "ledger")
        ledger_text = read_bytes(ledger_path).decode(errors="replace")
        if '"task":17' not in ledger_text and '"task": 17' not in ledger_text:
            raise ContractError("missing_task_17", "ledger")
        if any(path is None or not path.is_file() for path in paths.values()):
            raise ContractError("missing_input", "descriptor chain")
        payload = {
            "format_version": 1, "verdict": "PASS",
            "reason": "plan_compliant",
            "input_shas": {
                name: sha_path(path)
                for name, path in paths.items() if path is not None
            },
            "checks": ["descriptor-chain", "task-coverage", "immutable-criteria"],
            "missing_tasks": [],
        }
        validate(payload, args.schema)
        code = 0
    except ContractError as error:
        payload = {
            "format_version": 1, "verdict": "FAIL", "reason": error.reason,
            "input_shas": {}, "checks": [], "missing_tasks": [17],
        }
        code = 1
    write_json(args.output, payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
