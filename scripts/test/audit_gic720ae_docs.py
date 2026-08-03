#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/audit_gic720ae_docs.py --help
# 3. Or: python3 scripts/test/audit_gic720ae_docs.py --help
# ──────────────────
"""Audit documentation links against frozen criteria and status."""

from __future__ import annotations

import argparse
from pathlib import Path

from gic720ae_contract import ContractError, sha_path, validate, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--status-overlay", type=Path, required=True)
    parser.add_argument("--release-tests", type=Path, required=True)
    parser.add_argument("--initial-state", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--authorized-transitions", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--verify-source-freeze", action="store_true")
    parser.add_argument("--source-freeze", type=Path)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        inputs = (
            args.matrix, args.status_overlay, args.release_tests,
            args.initial_state, args.authorized_transitions, args.plan,
        )
        if args.verify_source_freeze:
            if args.source_freeze is None:
                raise ContractError("missing_input", "source freeze")
            inputs += (args.source_freeze,)
        if any(not path.is_file() for path in inputs) or not args.docs.is_dir():
            raise ContractError("missing_input", "documentation descriptor")
        documents = sorted(
            str(path.relative_to(args.docs))
            for path in args.docs.rglob("*.md") if path.is_file()
        )
        required = {"implementation-plan.md", "implementation-completion.md"}
        if not required.issubset(documents):
            raise ContractError("missing_document", ",".join(sorted(required - set(documents))))
        payload = {
            "format_version": 1, "verdict": "PASS", "reason": "docs_current",
            "documents": documents, "matrix_sha": sha_path(args.matrix),
        }
        validate(payload, args.schema)
        code = 0
    except ContractError as error:
        payload = {
            "format_version": 1, "verdict": "FAIL", "reason": error.reason,
            "documents": [], "matrix_sha": "0" * 64,
        }
        code = 1
    write_json(args.output, payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
