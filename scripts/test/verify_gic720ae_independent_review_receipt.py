#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/verify_gic720ae_independent_review_receipt.py --help
# 3. Or: python3 scripts/test/verify_gic720ae_independent_review_receipt.py --help
# ──────────────────
"""Verify an external reviewer receipt without creating a verdict."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess

from gic720ae_contract import (
    ContractError, JsonValue, canonical_bytes, json_object, read_bytes,
    require_list, require_string, sha_bytes, sha_path, validate, write_json,
    yaml_object,
)


LEAF_TYPES = {
    "file_sha256", "git_object", "git_head", "git_index", "command_replay",
}
MEASUREMENT_NAME = re.compile(r"^f[1-4]-direct-measurements\.([0-9a-f]{64})\.json$")
CANONICAL_REGISTRY = (
    Path(__file__).resolve().parents[2]
    / "tests/commands/gic720ae-final-manual-qa.yaml"
)
CANONICAL_REGISTRY_SHA = (
    "a76ff96cfa747b7ca4c191c8091535901073dbf9827a06a928bef741eeb7d3f5"
)
SHELL_PROGRAMS = {"sh", "bash", "dash", "zsh", "ksh", "fish"}
CONTROL_ARG = re.compile(r"[;&|<>`$()\n\r]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test-negative", type=Path)
    parser.add_argument("--role")
    parser.add_argument("--events", type=Path)
    parser.add_argument("--message", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--envelope", type=Path)
    parser.add_argument("--ledger-chain", type=Path)
    parser.add_argument("--require-source-state", type=Path)
    parser.add_argument("--prior-receipts")
    parser.add_argument("--require-nonparticipation", action="store_true")
    parser.add_argument("--require-unique-session", action="store_true")
    parser.add_argument("--receipt-schema", type=Path, required=True)
    parser.add_argument("--direct-measurement-manifest", type=Path)
    parser.add_argument("--direct-measurement-schema", type=Path)
    parser.add_argument(
        "--command-registry", type=Path,
        default=Path("tests/commands/gic720ae-final-manual-qa.yaml"),
    )
    parser.add_argument("--recompute-leaves", action="store_true")
    parser.add_argument("--forbid-collector-only", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def negative_reason(path: Path) -> str:
    fixture = json_object(path)
    participated = fixture.get("participated_tasks")
    if isinstance(participated, list) and participated:
        return "reviewer_not_independent"
    leaves = fixture.get("leaves")
    if isinstance(leaves, list) and any(
        isinstance(item, dict) and item.get("type") not in LEAF_TYPES
        for item in leaves
    ):
        return "collector_only_measurement"
    return "malformed_fixture"


def run_git(repo: Path, arguments: list[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        check=False, capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise ContractError("measurement_failed", "git query")
    return result.stdout.strip()


def replay_command(
    leaf: dict[str, JsonValue], registry_path: Path,
) -> str:
    if (
        registry_path.is_symlink()
        or not registry_path.is_file()
        or registry_path.resolve() != CANONICAL_REGISTRY
        or sha_path(registry_path) != CANONICAL_REGISTRY_SHA
    ):
        raise ContractError("forbidden_command", "noncanonical registry")
    command_id = require_string(leaf.get("command_id"), "command_id")
    registry = yaml_object(registry_path)
    commands = require_list(registry.get("commands"), "commands")
    matches = [
        item for item in commands
        if isinstance(item, dict) and item.get("id") == command_id
    ]
    if len(matches) != 1:
        raise ContractError("forbidden_command", command_id)
    command = matches[0]
    if command.get("measurement") != "command_replay":
        raise ContractError("forbidden_command", command_id)
    raw_argv = require_list(command.get("argv"), "argv")
    if not raw_argv or any(not isinstance(item, str) for item in raw_argv):
        raise ContractError("malformed_input", "registry argv")
    argv = [item for item in raw_argv if isinstance(item, str)]
    executable = Path(argv[0]).name
    if (
        executable in SHELL_PROGRAMS
        or "-c" in argv
        or any(CONTROL_ARG.search(item) for item in argv)
    ):
        raise ContractError("forbidden_command", command_id)
    policy = registry.get("policy")
    if not isinstance(policy, dict) or policy.get("shell_text_allowed") is not False:
        raise ContractError("forbidden_command", "registry policy")
    timeout = policy.get("timeout_seconds")
    if not isinstance(timeout, int) or timeout < 1:
        raise ContractError("malformed_input", "registry timeout")
    cwd = Path(require_string(leaf.get("value"), "leaf.value"))
    try:
        result = subprocess.run(
            argv, cwd=cwd, check=False, capture_output=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ContractError("measurement_failed", command_id) from error
    argv_value: list[JsonValue] = []
    argv_value.extend(argv)
    material: dict[str, JsonValue] = {
        "argv": argv_value, "command_id": command_id,
        "exit_code": result.returncode,
        "stderr_sha256": sha_bytes(result.stderr),
        "stdout_sha256": sha_bytes(result.stdout),
    }
    return sha_bytes(canonical_bytes(material))


def recompute_leaf(
    leaf: dict[str, JsonValue], registry_path: Path,
) -> str:
    leaf_type = require_string(leaf.get("type"), "leaf.type")
    value = require_string(leaf.get("value"), "leaf.value")
    if leaf_type not in LEAF_TYPES:
        raise ContractError("collector_only_measurement", leaf_type)
    if leaf_type == "file_sha256":
        return sha_path(Path(value))
    if leaf_type in {"git_head", "git_index", "git_object"}:
        repo = Path(value)
        command = {
            "git_head": ["rev-parse", "HEAD"],
            "git_index": ["write-tree"],
            "git_object": ["rev-parse", "HEAD^{tree}"],
        }[leaf_type]
        return sha_bytes(run_git(repo, command).encode())
    if leaf_type == "command_replay":
        return replay_command(leaf, registry_path)
    raise ContractError("collector_only_measurement", leaf_type)


def verify_measurements(args: argparse.Namespace) -> str:
    if args.direct_measurement_manifest is None or args.direct_measurement_schema is None:
        raise ContractError("missing_input", "direct measurement manifest")
    manifest = json_object(args.direct_measurement_manifest)
    validate(manifest, args.direct_measurement_schema)
    if manifest.get("command_registry_sha") != sha_path(args.command_registry):
        raise ContractError("stale_evidence", "command registry")
    name_match = MEASUREMENT_NAME.fullmatch(args.direct_measurement_manifest.name)
    if name_match is None or name_match.group(1) != sha_path(args.direct_measurement_manifest):
        raise ContractError("measurement_filename_hash_mismatch", "manifest")
    leaves = require_list(manifest.get("leaves"), "leaves")
    for raw in leaves:
        if not isinstance(raw, dict):
            raise ContractError("malformed_input", "measurement leaf")
        measured = recompute_leaf(raw, args.command_registry)
        if measured != raw.get("digest"):
            raise ContractError("direct_measurement_mismatch", str(raw.get("value")))
    return sha_path(args.direct_measurement_manifest)


def verify_live(args: argparse.Namespace) -> dict[str, JsonValue]:
    paths = (args.events, args.message, args.plan, args.envelope, args.ledger_chain)
    if any(path is None for path in paths):
        raise ContractError("missing_input", "review descriptor chain")
    receipt = json_object(args.message)
    validate(receipt, args.receipt_schema)
    if receipt.get("participated_tasks") != []:
        raise ContractError("reviewer_not_independent", "participated tasks")
    if args.role is not None and receipt.get("reviewer_identity") != args.role:
        raise ContractError("reviewer_identity_mismatch", args.role)
    if receipt.get("events_sha") != sha_path(args.events):
        raise ContractError("stale_evidence", "events")
    message_material = dict(receipt)
    message_material.pop("message_sha", None)
    if receipt.get("message_sha") != sha_bytes(canonical_bytes(message_material)):
        raise ContractError("stale_evidence", "message")
    if receipt.get("plan_sha") != sha_path(args.plan):
        raise ContractError("stale_evidence", "plan")
    if receipt.get("envelope_sha") != sha_path(args.envelope):
        raise ContractError("stale_evidence", "envelope")
    envelope = json_object(args.envelope)
    if receipt.get("source_freeze_sha") != envelope.get("source_freeze_sha"):
        raise ContractError("stale_evidence", "source freeze")
    measurement_sha = verify_measurements(args)
    if receipt.get("direct_measurement_sha") != measurement_sha:
        raise ContractError("direct_measurement_mismatch", "manifest")
    for line in read_bytes(args.events).decode().splitlines():
        json.loads(line)
    return receipt


def main() -> int:
    args = parse_args()
    try:
        if args.self_test_negative is not None:
            write_json(args.output, {
                "format_version": 1, "verdict": "FAIL",
                "reason": negative_reason(args.self_test_negative),
            })
            return 1
        receipt = verify_live(args)
        write_json(args.output, receipt)
        return 0
    except (ContractError, json.JSONDecodeError) as error:
        reason = error.reason if isinstance(error, ContractError) else "malformed_input"
        write_json(args.output, {
            "format_version": 1, "verdict": "FAIL", "reason": reason,
        })
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
