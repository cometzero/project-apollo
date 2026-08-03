#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/audit_gic720ae_release_policy.py --help
# 3. Or: python3 scripts/test/audit_gic720ae_release_policy.py --help
# ──────────────────
"""Audit fresh-build and status-transition release policy."""

from __future__ import annotations

import argparse
from pathlib import Path

from gic720ae_contract import ContractError, json_object, validate, write_json


REQUIRED_BUILDS = {"linux", "qbox", "scp", "zephyr"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test-negative", type=Path)
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        source = args.self_test_negative or args.policy
        if source is None:
            raise ContractError("missing_input", "release policy")
        policy = json_object(source)
        builds_raw = policy.get("fresh_builds", [])
        builds = {str(item) for item in builds_raw} if isinstance(builds_raw, list) else set()
        if "linux" not in builds:
            reason = "missing_fresh_linux_build"
            code = 1
        elif not REQUIRED_BUILDS.issubset(builds):
            reason = "missing_fresh_build"
            code = 1
        elif policy.get("approved") is False:
            reason = "unapproved_transition"
            code = 1
        else:
            reason = "release_policy_valid"
            code = 0
        payload = {
            "format_version": 1, "verdict": "PASS" if code == 0 else "FAIL",
            "reason": reason, "fresh_builds": sorted(builds),
            "transitions": [str(policy.get("transition"))] if policy.get("transition") else [],
        }
        validate(payload, args.schema)
    except ContractError as error:
        code = 1
        payload = {
            "format_version": 1, "verdict": "FAIL", "reason": error.reason,
            "fresh_builds": [], "transitions": [],
        }
    write_json(args.output, payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
