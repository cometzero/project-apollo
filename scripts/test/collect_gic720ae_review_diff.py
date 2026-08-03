#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/collect_gic720ae_review_diff.py --help
# 3. Or: python3 scripts/test/collect_gic720ae_review_diff.py --help
# ──────────────────
"""Collect deterministic Git objects and diffs for external review."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

from gic720ae_contract import (
    ContractError, JsonArray, canonical_bytes, sha_bytes, validate, write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repos", required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--envelope", type=Path, required=True)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--source-freeze", type=Path)
    parser.add_argument("--expected-sha-fixture", type=Path)
    parser.add_argument("--schema", type=Path, default=Path("tests/schemas/gic720ae-code-review.schema.json"))
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def git(repo: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *arguments], check=False,
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise ContractError("git_query_failed", str(repo))
    return result.stdout


def main() -> int:
    args = parse_args()
    try:
        descriptors = tuple(
            path for path in (args.plan, args.envelope, args.ledger, args.source_freeze)
            if path is not None
        )
        if any(not path.is_file() for path in descriptors):
            raise ContractError("missing_input", "descriptor chain")
        repositories = [item for item in args.repos.split(",") if item]
        records: JsonArray = [
            {
                "path": repo,
                "head": git(Path(repo), "rev-parse", "HEAD").strip(),
                "index": git(Path(repo), "write-tree").strip(),
                "diff": git(Path(repo), "diff", "--binary", "HEAD"),
            }
            for repo in repositories
        ]
        diff_sha = sha_bytes(canonical_bytes(records))
        if args.expected_sha_fixture is not None:
            raise ContractError("stale_state", "review diff")
        payload = {
            "format_version": 1, "verdict": "PASS", "reason": "diff_collected",
            "repositories": repositories, "diff_sha": diff_sha,
        }
        validate(payload, args.schema)
        code = 0
    except ContractError as error:
        payload = {
            "format_version": 1, "verdict": "FAIL", "reason": error.reason,
            "repositories": [], "diff_sha": "0" * 64,
        }
        code = 1
    write_json(args.output, payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
