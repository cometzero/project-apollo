#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/audit_gic720ae_scope_fidelity.py --help
# 3. Or: python3 scripts/test/audit_gic720ae_scope_fidelity.py --help
# ──────────────────
"""Reject forbidden GIC state ownership and scope overclaims."""

from __future__ import annotations

import argparse
from pathlib import Path

from gic720ae_contract import ContractError, json_object, sha_path, validate, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in (
        "plan", "reference", "matrix", "status-overlay", "initial-state",
        "envelope", "ledger", "source-freeze",
    ):
        parser.add_argument(f"--{name}", type=Path)
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--schema", type=Path, default=Path("tests/schemas/gic720ae-scope-fidelity.schema.json"))
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        violations: list[str] = []
        if args.fixture is not None:
            fixture = json_object(args.fixture)
            raw = fixture.get("violations")
            if isinstance(raw, list):
                violations = [str(item) for item in raw]
        paths = {
            name: getattr(args, name)
            for name in ("plan", "reference", "matrix", "envelope")
            if getattr(args, name) is not None
        }
        if not paths or any(not path.is_file() for path in paths.values()):
            raise ContractError("missing_input", "scope descriptors")
        reason = "forbidden_scope" if violations else "scope_faithful"
        payload = {
            "format_version": 1,
            "verdict": "FAIL" if violations else "PASS",
            "reason": reason, "violations": violations,
            "input_shas": {name: sha_path(path) for name, path in paths.items()},
        }
        validate(payload, args.schema)
        code = 1 if violations else 0
    except ContractError as error:
        payload = {
            "format_version": 1, "verdict": "FAIL", "reason": error.reason,
            "violations": [], "input_shas": {},
        }
        code = 1
    write_json(args.output, payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
