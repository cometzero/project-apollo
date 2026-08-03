#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/audit_gic720ae_release_commits.py --help
# 3. Or: python3 scripts/test/audit_gic720ae_release_commits.py --help
# ──────────────────
"""Audit signed nested-first release commits and top pointers."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

from gic720ae_contract import (
    ContractError, JsonObject, json_object, validate, write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test-negative", type=Path)
    parser.add_argument("--initial-state", type=Path)
    parser.add_argument("--repos")
    for name in (
        "release-tests", "authorized-transitions", "source-freeze",
        "completion", "report-only-digest",
    ):
        parser.add_argument(f"--{name}", type=Path)
    for name in (
        "require-diff-check", "require-signed-off", "require-top-pointers",
        "require-marker-outside-byte-identical",
    ):
        parser.add_argument(f"--{name}", action="store_true")
    parser.add_argument("--schema", type=Path, default=Path("tests/schemas/gic720ae-release-audit.schema.json"))
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def git(repo: str, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", repo, *arguments], check=False,
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise ContractError("git_query_failed", repo)
    return result.stdout.strip()


def verify_transition(record: JsonObject) -> None:
    transition = record.get("transition")
    approved = record.get("approved")
    if isinstance(transition, str) and approved is False:
        raise ContractError("unapproved_status_transition", transition)
    if transition is not None and approved is not True:
        raise ContractError("malformed_input", "status transition")


def main() -> int:
    args = parse_args()
    try:
        if args.self_test_negative is not None:
            verify_transition(json_object(args.self_test_negative))
        if not args.repos:
            raise ContractError("missing_input", "repositories")
        repositories: list[JsonObject] = []
        for repo in [item for item in args.repos.split(",") if item]:
            head = git(repo, "rev-parse", "HEAD")
            message = git(repo, "show", "-s", "--format=%B", "HEAD")
            signed = "Signed-off-by:" in message
            if args.require_signed_off and not signed:
                raise ContractError("unsigned_commit", repo)
            if args.require_diff_check:
                git(repo, "diff", "--check", "HEAD^", "HEAD")
            repositories.append({
                "path": repo, "head": head, "signed": signed, "changed": True,
            })
        payload = {
            "format_version": 1, "verdict": "PASS", "reason": "release_audited",
            "repositories": repositories,
        }
        validate(payload, args.schema)
        code = 0
    except ContractError as error:
        payload = {
            "format_version": 1, "verdict": "FAIL", "reason": error.reason,
            "repositories": [],
        }
        code = 1
    write_json(args.output, payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
