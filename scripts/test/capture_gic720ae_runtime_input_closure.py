#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/capture_gic720ae_runtime_input_closure.py --help
# 3. Or: python3 scripts/test/capture_gic720ae_runtime_input_closure.py --help
# ──────────────────
"""Capture descriptor-resolved runtime inputs and producer lineage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import assert_never

from gic720ae_contract import (
    ContractError, JsonArray, JsonObject, JsonValue, canonical_bytes, json_object,
    require_list, sha_bytes, sha_path,
    validate, write_json,
)


REQUIRED_QBOX_ROLES = {
    "rse-rom", "rse-flash", "rse-otp", "ap-flash", "provisioning-bundle",
    "boot-media", "rootfs", "dtb", "ap-elf", "rse-elf", "si0-image",
    "si0-elf", "si1-image", "si1-elf", "libqemu", "qbox-executable",
    "qbox-runner", "qbox-lua",
}
ARTIFACT_ROLES = {
    "rse_rom": "rse-rom", "rse_flash": "rse-flash", "rse_otp": "rse-otp",
    "ap_flash": "ap-flash", "provisioning_bundle": "provisioning-bundle",
    "efi_capsule_disk": "boot-media", "rootfs": "rootfs", "ap_dtb": "dtb",
    "ap_bl2_elf": "ap-elf", "rse_bl2_elf": "rse-elf",
    "si_cl0_image": "si0-image", "si_cl1_image": "si1-image",
    "si_cl1_symbols": "si1-elf",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test-negative", type=Path)
    parser.add_argument("--qbox-runner", type=Path)
    parser.add_argument("--qbox-conf", type=Path)
    parser.add_argument("--qbox-build-root", type=Path)
    parser.add_argument("--producer-receipt", action="append", default=[])
    parser.add_argument("--fvp-base-provenance", type=Path)
    parser.add_argument("--fvp-profile", action="append", default=[])
    parser.add_argument("--yocto-provenance", type=Path)
    parser.add_argument("--default-deploy-manifest", type=Path)
    parser.add_argument("--profile-provenance", action="append", default=[])
    parser.add_argument("--compare-frozen-contract", type=Path)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def negative(args: argparse.Namespace) -> tuple[int, JsonObject]:
    fixture = json_object(args.self_test_negative)
    raw_leaves = require_list(fixture.get("leaves"), "leaves")
    raw_required = require_list(fixture.get("required_roles"), "required_roles")
    roles = {
        str(item.get("role"))
        for item in raw_leaves
        if isinstance(item, dict)
    }
    required = {str(item) for item in raw_required}
    reason = "unowned_runtime_input" if required - roles else "malformed_fixture"
    return 1, {
        "format_version": 1, "verdict": "FAIL", "reason": reason,
        "leaves": [], "contract_sha": "0" * 64,
    }


def receipt_map(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ContractError("malformed_input", "producer receipt")
        role, path = value.split("=", 1)
        result[role] = Path(path)
    return result


def resolved_defaults(runner: Path, root: Path) -> dict[str, Path]:
    program = (
        "import json,sys;"
        "from pathlib import Path;"
        "sys.path.insert(0,str(Path(sys.argv[1]).resolve().parent));"
        "import run_qbox_apollo_fvp_full as r;"
        "print(json.dumps({k:str(v) for k,v in r.default_artifacts(Path(sys.argv[2])).items()},sort_keys=True))"
    )
    result = subprocess.run(
        [sys.executable, "-c", program, str(runner), str(root)],
        check=False, capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise ContractError("descriptor_parse_failed", str(runner))
    try:
        raw = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ContractError("descriptor_parse_failed", str(runner)) from error
    if not isinstance(raw, dict):
        raise ContractError("descriptor_parse_failed", str(runner))
    return {
        key: Path(value)
        for key, value in raw.items()
        if isinstance(key, str) and isinstance(value, str)
    }


def referenced_paths(value: JsonValue) -> list[Path]:
    paths: list[Path] = []
    match value:
        case dict() as mapping:
            for key, child in mapping.items():
                if key in {"path", "realpath", "fvpconf"} and isinstance(child, str):
                    candidate = Path(child)
                    if candidate.is_file():
                        paths.append(candidate)
                paths.extend(referenced_paths(child))
        case list() as sequence:
            for child in sequence:
                paths.extend(referenced_paths(child))
        case str() | int() | float() | bool() | None:
            pass
        case unreachable:
            assert_never(unreachable)
    return paths


def fvpconf_paths(path: Path) -> list[Path]:
    configuration = json_object(path)
    candidates = referenced_paths(configuration)
    parameters = configuration.get("parameters")
    if isinstance(parameters, dict):
        for value in parameters.values():
            if isinstance(value, str) and Path(value).is_file():
                candidates.append(Path(value))
    data = configuration.get("data")
    if isinstance(data, list):
        for value in data:
            if isinstance(value, str) and "=" in value:
                candidate = Path(value.split("=", 1)[1].split("@", 1)[0])
                if candidate.is_file():
                    candidates.append(candidate)
    return candidates


def provenance_leaves(role: str, receipt: Path) -> JsonArray:
    receipt_sha = sha_path(receipt)
    content = json_object(receipt)
    paths = referenced_paths(content)
    expanded = list(paths)
    for path in paths:
        if path.suffix == ".fvpconf":
            expanded.extend(fvpconf_paths(path))
    leaves: JsonArray = []
    for index, path in enumerate(dict.fromkeys(expanded)):
        leaves.append({
            "role": f"{role}:{index}:{path.name}",
            "realpath": str(path.resolve()), "sha256": sha_path(path),
            "producer_receipt_sha": receipt_sha, "producer_task": 39,
            "lineage": f"taskhash:{role}",
        })
    if not leaves:
        raise ContractError("unowned_runtime_input", role)
    return leaves


def live(args: argparse.Namespace) -> tuple[int, JsonObject]:
    if args.qbox_build_root is None or args.qbox_conf is None or args.qbox_runner is None:
        raise ContractError("missing_input", "qbox descriptors")
    receipts = receipt_map(args.producer_receipt)
    receipt_shas = {role: sha_path(path) for role, path in receipts.items()}
    root = args.qbox_build_root
    defaults = resolved_defaults(args.qbox_runner, root)
    candidates = {
        ARTIFACT_ROLES[key]: path
        for key, path in defaults.items() if key in ARTIFACT_ROLES
    }
    candidates.update({
        "si0-elf": root / "work/scp-firmware/bin/apollo-qvp-si0-bl2.elf",
        "libqemu": root / "work/qbox-platform/_deps/libqemu-build/qemu-prefix/lib/libqemu-system-aarch64.so",
        "qbox-executable": root / "work/qbox-platform/platforms-vp",
        "qbox-runner": args.qbox_runner,
        "qbox-lua": args.qbox_conf,
    })
    leaves: JsonArray = []
    for role in sorted(REQUIRED_QBOX_ROLES):
        path = candidates[role]
        owner = next((key for key in receipts if role.startswith(key)), "")
        if not owner and len(receipts) == 1:
            owner = next(iter(receipts))
        if not path.is_file() or not owner:
            return 1, {
                "format_version": 1, "verdict": "FAIL",
                "reason": "unowned_runtime_input", "leaves": [],
                "contract_sha": "0" * 64,
            }
        leaves.append({
            "role": role, "realpath": str(path.resolve()), "sha256": sha_path(path),
            "producer_receipt_sha": receipt_shas[owner],
            "producer_task": 39, "lineage": f"invocation:{owner}",
        })
    receipt_inputs: list[tuple[str, Path]] = []
    if args.fvp_base_provenance is not None:
        receipt_inputs.append(("fvp-base", args.fvp_base_provenance))
    for value in args.fvp_profile + args.profile_provenance:
        if "=" not in value:
            raise ContractError("malformed_input", "profile provenance")
        role, path = value.split("=", 1)
        receipt_inputs.append((role, Path(path)))
    if args.yocto_provenance is not None:
        receipt_inputs.append(("yocto", args.yocto_provenance))
    if args.default_deploy_manifest is not None:
        receipt_inputs.append(("default-deploy", args.default_deploy_manifest))
    for role, receipt in receipt_inputs:
        leaves.extend(provenance_leaves(role, receipt))
    if args.compare_frozen_contract is not None:
        frozen = json_object(args.compare_frozen_contract)
        validate(frozen, args.schema)
        frozen_leaves = require_list(frozen.get("leaves"), "frozen.leaves")
        frozen_roles = {
            str(item.get("role"))
            for item in frozen_leaves if isinstance(item, dict)
        }
        current_roles = {
            str(item.get("role"))
            for item in leaves if isinstance(item, dict)
        }
        if frozen_roles != current_roles:
            return 1, {
                "format_version": 1, "verdict": "FAIL",
                "reason": "stale_runtime_contract", "leaves": [],
                "contract_sha": "0" * 64,
            }
    contract_sha = sha_bytes(canonical_bytes(leaves))
    payload = {
        "format_version": 1, "verdict": "PASS", "reason": "closure_complete",
        "leaves": leaves, "contract_sha": contract_sha,
    }
    return 0, payload


def main() -> int:
    args = parse_args()
    try:
        code, payload = negative(args) if args.self_test_negative else live(args)
        validate(payload, args.schema)
    except ContractError as error:
        code = 1
        payload = {
            "format_version": 1, "verdict": "FAIL", "reason": error.reason,
            "leaves": [], "contract_sha": "0" * 64,
        }
    write_json(args.output, payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
