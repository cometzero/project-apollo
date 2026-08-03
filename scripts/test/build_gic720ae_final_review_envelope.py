#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/build_gic720ae_final_review_envelope.py --help
# 3. Or: python3 scripts/test/build_gic720ae_final_review_envelope.py --help
# ──────────────────
"""Build the immutable content-addressed final review envelope."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from gic720ae_contract import (
    ContractError, canonical_bytes, sha_bytes, sha_path, validate, write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in (
        "plan", "initial-state", "source-freeze", "report-only-digest",
        "release-result", "repository-state-before", "repository-state-after",
        "ledger-snapshot", "ledger-chain", "yocto-provenance",
        "default-deploy-manifest", "default-deploy-stable-contract",
        "feature-criteria", "status-overlay", "command-manifest",
        "direct-measurement-schema",
    ):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--runtime-provenance-dir", type=Path, required=True)
    parser.add_argument("--reviewer-prompts", required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        named = {
            name: getattr(args, name)
            for name in (
                "plan", "initial_state", "source_freeze", "report_only_digest",
                "release_result", "repository_state_before", "repository_state_after",
                "ledger_snapshot", "ledger_chain", "yocto_provenance",
                "default_deploy_manifest", "default_deploy_stable_contract",
                "feature_criteria", "status_overlay", "command_manifest",
                "direct_measurement_schema",
            )
        }
        prompts = [Path(item) for item in args.reviewer_prompts.split(",") if item]
        provenance = sorted(args.runtime_provenance_dir.glob("*provenance*.json"))
        all_paths = list(named.values()) + prompts + provenance
        if any(not path.is_file() for path in all_paths):
            raise ContractError("missing_input", "envelope artifact")
        artifacts = [
            {"path": str(path.resolve()), "sha256": sha_path(path)}
            for path in sorted(all_paths, key=lambda item: str(item))
        ]
        payload = {
            "format_version": 1,
            "plan_sha": sha_path(args.plan),
            "source_freeze_sha": sha_path(args.source_freeze),
            "ledger_chain_sha": sha_path(args.ledger_chain),
            "artifacts": artifacts,
        }
        validate(payload, args.schema)
        digest = sha_bytes(canonical_bytes(payload))
        addressed = args.output.parent / f"envelope-{digest}.json"
        write_json(addressed, payload)
        write_json(args.output, payload)
        os.chmod(addressed, 0o444)
        os.chmod(args.output, 0o444)
        return 0
    except ContractError as error:
        write_json(args.output, {
            "format_version": 1, "verdict": "FAIL", "reason": error.reason,
        })
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
