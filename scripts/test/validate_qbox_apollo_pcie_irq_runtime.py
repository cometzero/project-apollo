#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.0"]
# ///
# ─── How to run ───
# python3 scripts/test/validate_qbox_apollo_pcie_irq_runtime.py --help

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import jsonschema

try:
    import qbox_apollo_pcie_irq_contract as profile_contract
    import qbox_apollo_pcie_irq_inspect as profile_inspect
except ModuleNotFoundError:
    from scripts.test import qbox_apollo_pcie_irq_contract as profile_contract
    from scripts.test import qbox_apollo_pcie_irq_inspect as profile_inspect

CANONICAL_FVP_GATE = profile_contract.CANONICAL_FVP_GATE
CANONICAL_FVP_GATE_SHA256 = profile_contract.CANONICAL_FVP_GATE_SHA256
INPUT_SCHEMA = profile_contract.INPUT_SCHEMA
PROFILE_SCHEMA = profile_contract.PROFILE_SCHEMA
ROOT = profile_contract.ROOT
SHARED_VALIDATOR = profile_contract.SHARED_VALIDATOR
JsonObject = profile_contract.JsonObject
JsonValue = profile_contract.JsonValue
ProfileError = profile_contract.ProfileError
contained = profile_contract.contained
contract = profile_contract.contract
has_symlink = profile_contract.has_symlink
load_object = profile_contract.load_object
object_field = profile_contract.object_field
require_file = profile_contract.require_file
sha256 = profile_contract.sha256
string_field = profile_contract.string_field
verify_reference_gate = profile_contract.verify_reference_gate
artifact_path = profile_contract.verified_artifact_path
validate_disk_slots = profile_inspect.validate_disk_slots
validate_distinct_mode_artifacts = profile_inspect.validate_distinct_mode_artifacts
validate_mode_payload = profile_inspect.validate_mode_payload


def validate_profile(path: Path) -> tuple[JsonObject, dict[str, str]]:
    profile_path = require_file(path, "profile_manifest")
    profile_dir = profile_path.parent
    payload = load_object(profile_path, "profile_manifest")
    schema = load_object(PROFILE_SCHEMA, "profile_schema")
    try:
        jsonschema.Draft202012Validator(schema).validate(payload)
    except jsonschema.ValidationError as error:
        raise ProfileError("profile_schema") from error
    reference = object_field(payload.get("fvp_reference"), "fvp_reference")
    if (
        reference.get("path") != str(CANONICAL_FVP_GATE)
        or reference.get("sha256") != CANONICAL_FVP_GATE_SHA256
    ):
        raise ProfileError("fvp_reference")
    verify_reference_gate(Path(str(reference["path"])))
    if payload.get("contract") != contract():
        raise ProfileError("profile_contract")
    inputs = object_field(payload.get("inputs"), "profile_inputs")
    input_paths = {
        name: artifact_path(entry, ROOT, f"profile_input:{name}")
        for name, entry in inputs.items()
    }
    generated = object_field(payload.get("artifacts"), "profile_artifacts")
    try:
        validate_distinct_mode_artifacts(generated)
    except ProfileError as error:
        raise ProfileError("mode_identity") from error
    paths = {
        name: artifact_path(entry, profile_dir, f"profile_artifact:{name}")
        for name, entry in generated.items()
    }
    modes = object_field(payload.get("modes"), "profile_modes")
    command = object_field(payload.get("command"), "profile_command")
    input_schema = load_object(INPUT_SCHEMA, "input_schema")
    argv = command.get("argv")
    if not isinstance(argv, list) or not all(isinstance(value, str) for value in argv):
        raise ProfileError("profile_command")
    input_hashes: dict[str, str] = {}
    for mode in ("msix", "intx"):
        mode_entry = object_field(modes.get(mode), f"profile_mode:{mode}")
        artifacts = object_field(mode_entry.get("artifacts"), f"profile_mode:{mode}")
        for name in ("input_manifest", "uki", "initramfs", "disk"):
            if artifacts.get(name) != generated.get(f"{mode}_{name}"):
                raise ProfileError(f"profile_mode_artifact:{mode}:{name}")
        mode_manifest = load_object(
            paths[f"{mode}_input_manifest"], f"mode_manifest:{mode}"
        )
        try:
            jsonschema.Draft202012Validator(input_schema).validate(mode_manifest)
        except jsonschema.ValidationError as error:
            raise ProfileError(f"mode_schema:{mode}") from error
        mode_command = object_field(
            mode_manifest.get("command"), f"mode_command:{mode}"
        )
        boot = object_field(mode_manifest.get("boot"), f"mode_boot:{mode}")
        required = ["pci=nomsi"] if mode == "intx" else []
        forbidden = [] if mode == "intx" else ["pci=nomsi"]
        if mode_manifest.get("mode") != mode:
            raise ProfileError("mode_identity")
        if (
            mode_manifest.get("platform") != "qbox"
            or mode_manifest.get("contract") != contract()
            or mode_manifest.get("inputs") != inputs
            or mode_manifest.get("fvp_reference_gate_sha256")
            != CANONICAL_FVP_GATE_SHA256
            or mode_command != {"argv": argv, "profile_mode": mode}
            or boot.get("required_arguments") != required
            or boot.get("forbidden_arguments") != forbidden
        ):
            raise ProfileError(f"mode_manifest:{mode}")
        boot_values = mode_entry.get("boot_arguments")
        if not isinstance(boot_values, list) or not all(
            isinstance(value, str) for value in boot_values
        ):
            raise ProfileError(f"mode_bootargs:{mode}")
        boot_arguments = [
            string_field(value, f"mode_bootargs:{mode}") for value in boot_values
        ]
        if any(value not in boot_arguments for value in required) or any(
            value in boot_arguments for value in forbidden
        ):
            raise ProfileError(f"mode_bootargs:{mode}")
        command_line_sha = hashlib.sha256(" ".join(boot_arguments).encode()).hexdigest()
        if boot.get("command_line_sha256") != command_line_sha:
            raise ProfileError(f"mode_bootargs:{mode}")
        try:
            validate_mode_payload(
                mode,
                paths[f"{mode}_input_manifest"],
                paths[f"{mode}_uki"],
                paths[f"{mode}_initramfs"],
                paths["dtb"],
                boot_arguments,
                input_paths["guest_probe"],
                input_paths["guest_wrapper"],
            )
            validate_disk_slots(paths[f"{mode}_disk"], paths[f"{mode}_uki"])
        except ProfileError as error:
            raise ProfileError("mode_identity") from error
        input_hashes[mode] = sha256(paths[f"{mode}_input_manifest"])
    return payload, input_hashes


def run_shared(log: Path, mode: str, digest: str, output: Path) -> JsonObject:
    result = subprocess.run(
        [
            sys.executable,
            str(SHARED_VALIDATOR),
            "--log",
            str(log),
            "--platform",
            "qbox",
            "--mode",
            mode,
            "--input-sha256",
            digest,
            "--output",
            str(output),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    payload = load_object(output, f"shared_validator:{mode}")
    expected_rc = 0 if payload.get("status") == "pass" else 1
    if result.returncode != expected_rc:
        raise ProfileError(f"shared_validator_rc:{mode}")
    return payload


def validate_pair(profile_path: Path, msix_log: Path, intx_log: Path) -> JsonObject:
    profile, hashes = validate_profile(profile_path)
    logs = {
        "msix": require_file(msix_log, "msix_log"),
        "intx": require_file(intx_log, "intx_log"),
    }
    with tempfile.TemporaryDirectory(prefix="apollo-qbox-pcie-validator-") as temporary:
        directory = Path(temporary)
        results = {
            mode: run_shared(logs[mode], mode, hashes[mode], directory / f"{mode}.json")
            for mode in ("msix", "intx")
        }
    checks = {
        "profile_gate": True,
        "mode_identity": True,
        "msix_endpoint_bound": results["msix"].get("status") == "pass",
        "intx_endpoint_bound": results["intx"].get("status") == "pass",
    }
    profile_identity: JsonObject = {
        "path": str(profile_path.absolute()),
        "sha256": sha256(profile_path),
    }
    hash_payload: JsonObject = {}
    for mode, digest in hashes.items():
        hash_payload[mode] = digest
    result_payload: JsonObject = {}
    for mode, result in results.items():
        result_payload[mode] = result
    check_payload: JsonObject = {}
    for name, passed in checks.items():
        check_payload[name] = passed
    return {
        "schema_version": 2,
        "status": "pass" if all(checks.values()) else "fail",
        "reason": "ok" if all(checks.values()) else "shared_contract",
        "profile_manifest": profile_identity,
        "fvp_reference": profile["fvp_reference"],
        "contract": contract(),
        "input_sha256": hash_payload,
        "msix": result_payload["msix"],
        "intx": result_payload["intx"],
        "checks": check_payload,
    }


def atomic_write(path: Path, payload: JsonObject) -> None:
    absolute = path.absolute()
    if not contained(absolute, ROOT) or has_symlink(absolute):
        raise ProfileError("output_path")
    absolute.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=absolute.parent, delete=False) as stream:
        stream.write(profile_contract.canonical_bytes(payload))
        temporary = Path(stream.name)
    os.replace(temporary, absolute)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Apollo QBox PCIe IRQ evidence."
    )
    parser.add_argument("--profile-manifest", type=Path, required=True)
    parser.add_argument("--msix-log", type=Path, required=True)
    parser.add_argument("--intx-log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = validate_pair(args.profile_manifest, args.msix_log, args.intx_log)
    except (ProfileError, OSError) as error:
        payload = {
            "schema_version": 2,
            "status": "fail",
            "reason": str(error),
        }
    try:
        atomic_write(args.output, payload)
    except ProfileError as error:
        print(error)
        return 1
    print(args.output)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
