#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/verify_gic720ae_ledger_chain.py --help
# 3. Or: python3 scripts/test/verify_gic720ae_ledger_chain.py --help
# ──────────────────
"""Recompute the canonical GIC-720AE ledger chain from genesis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from gic720ae_contract import (
    ContractError, JsonObject, canonical_bytes, json_object, read_bytes, sha_bytes,
    validate, write_json,
)


ZERO = "0" * 64


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test-negative", type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def records(path: Path) -> list[JsonObject]:
    if path.suffix == ".jsonl":
        parsed: list[JsonObject] = []
        for line in read_bytes(path).decode().splitlines():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ContractError("malformed_input", "ledger record")
            parsed.append(value)
        return parsed
    value = json_object(path).get("records")
    if not isinstance(value, list):
        raise ContractError("malformed_input", "ledger.records")
    return [item for item in value if isinstance(item, dict)]


def recompute(path: Path) -> tuple[bool, list[JsonObject], str]:
    previous = ZERO
    output: list[JsonObject] = []
    valid = True
    for index, raw in enumerate(records(path)):
        sequence = raw.get("sequence")
        kind = raw.get("kind")
        payload = raw.get("payload", {})
        payload_sha = sha_bytes(canonical_bytes(payload))
        material = {
            "sequence": sequence, "kind": kind,
            "payload_sha": payload_sha, "previous_sha": previous,
        }
        record_sha = sha_bytes(canonical_bytes(material))
        valid = valid and sequence == index
        valid = valid and raw.get("previous_sha") == previous
        valid = valid and raw.get("record_sha") == record_sha
        output.append({**material, "record_sha": record_sha})
        previous = record_sha
    return valid and bool(output), output, previous


def main() -> int:
    args = parse_args()
    path = args.self_test_negative or args.ledger
    if path is None:
        raise SystemExit("--ledger is required")
    try:
        valid, chain, root = recompute(path)
        reason = "ledger_chain_valid" if valid else "broken_ledger_chain"
        payload = {
            "format_version": 1, "verdict": "PASS" if valid else "FAIL",
            "reason": reason, "genesis_sha": chain[0]["record_sha"] if chain else ZERO,
            "final_root": root, "records": chain,
        }
        validate(payload, args.schema)
        code = 0 if valid else 1
    except (ContractError, json.JSONDecodeError):
        code = 1
        payload = {
            "format_version": 1, "verdict": "FAIL",
            "reason": "broken_ledger_chain", "genesis_sha": ZERO,
            "final_root": ZERO, "records": [],
        }
    write_json(args.output, payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
