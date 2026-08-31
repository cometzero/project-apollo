#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.0"]
# ///
# ─── How to run ───
# python3 scripts/test/prepare_qbox_apollo_pcie_irq_profile.py --help

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Final

import jsonschema

try:
    import qbox_apollo_pcie_irq_artifacts as artifact_io
    import qbox_apollo_pcie_irq_contract as profile_contract
    import qbox_apollo_pcie_irq_gic_overlay as gic_overlay
    import qbox_apollo_pcie_irq_inspect as profile_inspect
except ModuleNotFoundError:
    from scripts.test import qbox_apollo_pcie_irq_artifacts as artifact_io
    from scripts.test import qbox_apollo_pcie_irq_contract as profile_contract
    from scripts.test import qbox_apollo_pcie_irq_gic_overlay as gic_overlay
    from scripts.test import qbox_apollo_pcie_irq_inspect as profile_inspect

AP_COMPUTE = profile_contract.AP_COMPUTE
CONTRACT_MODULE = profile_contract.CONTRACT_MODULE
CANONICAL_FVP_GATE = profile_contract.CANONICAL_FVP_GATE
CANONICAL_FVP_GATE_SHA256 = profile_contract.CANONICAL_FVP_GATE_SHA256
GUEST_PROBE = profile_contract.GUEST_PROBE
GUEST_WRAPPER = profile_contract.GUEST_WRAPPER
INPUT_SCHEMA = profile_contract.INPUT_SCHEMA
OVERLAY = profile_contract.OVERLAY
PROFILE_SCHEMA = profile_contract.PROFILE_SCHEMA
ROOT = profile_contract.ROOT
SHARED_VALIDATOR = profile_contract.SHARED_VALIDATOR
GIC_OVERLAY_MODULE = Path(gic_overlay.__file__).resolve()
Artifact = profile_contract.Artifact
JsonObject = profile_contract.JsonObject
JsonValue = profile_contract.JsonValue
Mode = profile_contract.Mode
ProfileError = profile_contract.ProfileError
artifact = profile_contract.artifact
canonical_bytes = profile_contract.canonical_bytes
contained = profile_contract.contained
contract = profile_contract.contract
has_symlink = profile_contract.has_symlink
mode_input_payload = profile_contract.mode_input_payload
require_file = profile_contract.require_file
sha256 = profile_contract.sha256
validate_platform_contract = profile_contract.validate_platform_contract
verify_reference_gate = profile_contract.verify_reference_gate

DESCRIPTION: Final = "Build gate-bound Apollo QBox PCIe MSI-X and INTx profiles."
DEFAULT_DEPLOY: Final = ROOT / "build/local-apollo-qvp/deploy/boot"
DEFAULT_OUT: Final = ROOT / "build/qbox-apollo-qvp/pcie-irq-profile"
fdt_cells = gic_overlay.fdt_cells
gic_symbol = gic_overlay.gic_symbol
validate_base_gic = gic_overlay.validate_base_gic
prepare_gic_symbol_base = gic_overlay.prepare_gic_symbol_base
validate_warning_clean_overlay = gic_overlay.validate_warning_clean_overlay


def artifact_map(items: dict[str, Artifact]) -> JsonObject:
    payload: JsonObject = {}
    for name, item in items.items():
        payload[name] = item
    return payload


def prepare(
    gate: Path,
    base_disk: Path,
    base_dtb: Path,
    base_initramfs: Path,
    output_dir: Path,
    command: list[str],
) -> Path:
    artifact_io.require_tools()
    verify_reference_gate(gate)
    validate_platform_contract(AP_COMPUTE, OVERLAY)
    validate_warning_clean_overlay()
    derived, msix_arguments = artifact_io.uki_inputs(base_disk)
    if (
        derived.get(base_dtb.name) != base_dtb.absolute()
        or derived.get(base_initramfs.name) != base_initramfs.absolute()
    ):
        raise ProfileError("stale_base_inputs")
    sources = {
        "base_disk": base_disk,
        "base_dtb": base_dtb,
        "base_initramfs": base_initramfs,
        "builder": Path(__file__).resolve(),
        "gic_overlay_module": GIC_OVERLAY_MODULE,
        "artifact_module": Path(artifact_io.__file__).resolve(),
        "inspect_module": Path(profile_inspect.__file__).resolve(),
        "contract_module": CONTRACT_MODULE,
        "profile_schema": PROFILE_SCHEMA,
        "input_schema": INPUT_SCHEMA,
        "fvp_reference_gate": CANONICAL_FVP_GATE,
        "linux_image": derived["Image"],
        "uki_stub": derived["linuxaa64.efi.stub"],
        "uki_os_release": derived["os-release"],
        "kernel_release": derived["kernel.release"],
        "ukify": derived["ukify"],
        "uki_manifest": derived["uki_manifest"],
        "overlay_source": OVERLAY,
        "guest_probe": GUEST_PROBE,
        "guest_wrapper": GUEST_WRAPPER,
        "profile_validator": ROOT
        / "scripts/test/validate_qbox_apollo_pcie_irq_runtime.py",
        "shared_validator": SHARED_VALIDATOR,
        "ap_compute": AP_COMPUTE,
    }
    checked = {
        name: require_file(path, f"input_path:{name}") for name, path in sources.items()
    }
    output = output_dir.absolute()
    if not contained(output, ROOT) or has_symlink(output) or output.exists():
        raise ProfileError("output_path")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=f".{output.name}.tmp-", dir=output.parent
    ) as temporary:
        staging = Path(temporary)
        symbolized_base = staging / ".apollo-qvp-gic-symbol.dtb"
        prepare_gic_symbol_base(base_dtb, symbolized_base)
        overlay, merged = artifact_io.compile_overlay(symbolized_base, staging)
        symbolized_base.unlink()
        input_artifacts: dict[str, Artifact] = {
            name: artifact(path) for name, path in checked.items()
        }
        modes: JsonObject = {}
        generated: dict[str, Artifact] = {
            "overlay": artifact(overlay, output / overlay.name),
            "dtb": artifact(merged, output / merged.name),
        }
        uki_build_inputs = {
            "Image": checked["linux_image"],
            "linuxaa64.efi.stub": checked["uki_stub"],
            "os-release": checked["uki_os_release"],
            "kernel.release": checked["kernel_release"],
            "ukify": checked["ukify"],
        }
        modes_to_build: tuple[Mode, ...] = ("msix", "intx")
        input_schema = json.loads(INPUT_SCHEMA.read_text(encoding="utf-8"))
        for mode in modes_to_build:
            arguments = [*msix_arguments]
            if mode == "intx":
                arguments.append("pci=nomsi")
            command_line_sha = hashlib.sha256(" ".join(arguments).encode()).hexdigest()
            mode_manifest = staging / f"apollo-qvp-pcie-{mode}-input.json"
            payload = mode_input_payload(
                mode,
                input_artifacts,
                CANONICAL_FVP_GATE_SHA256,
                command_line_sha,
                command,
            )
            jsonschema.Draft202012Validator(input_schema).validate(payload)
            mode_manifest.write_bytes(canonical_bytes(payload))
            initramfs = staging / f"apollo-qvp-pcie-{mode}-initramfs.cpio.gz"
            uki = staging / f"apollo-qvp-pcie-{mode}.efi"
            disk = staging / f"apollo-qvp-pcie-{mode}-disk.img"
            artifact_io.build_initramfs(base_initramfs, initramfs, mode, mode_manifest)
            artifact_io.build_uki(uki, merged, initramfs, uki_build_inputs, arguments)
            artifact_io.copy_disk(base_disk, disk)
            artifact_io.replace_uki(disk, uki)
            profile_inspect.validate_mode_payload(
                mode,
                mode_manifest,
                uki,
                initramfs,
                merged,
                arguments,
                GUEST_PROBE,
                GUEST_WRAPPER,
            )
            profile_inspect.validate_disk_slots(disk, uki)
            mode_items = {
                "input_manifest": mode_manifest,
                "uki": uki,
                "initramfs": initramfs,
                "disk": disk,
            }
            exposed = {
                name: artifact(path, output / path.name)
                for name, path in mode_items.items()
            }
            argument_payload: list[JsonValue] = [value for value in arguments]
            mode_payload: JsonObject = {
                "mode": mode,
                "boot_arguments": argument_payload,
                "artifacts": artifact_map(exposed),
            }
            modes[mode] = mode_payload
            generated.update({f"{mode}_{name}": item for name, item in exposed.items()})
        profile_inspect.validate_distinct_mode_artifacts(artifact_map(generated))
        reference_payload: JsonObject = {
            "path": str(CANONICAL_FVP_GATE),
            "sha256": CANONICAL_FVP_GATE_SHA256,
            "reference_gate": "PASS",
            "fvp_qualification": "UNSUPPORTED",
            "reason": "immutable_ecam_limit",
        }
        command_values: list[JsonValue] = [value for value in command]
        command_payload: JsonObject = {"argv": command_values, "cwd": str(ROOT)}
        manifest: JsonObject = {
            "schema_version": 2,
            "profile": "apollo-qvp-pcie-irq",
            "fvp_reference": reference_payload,
            "contract": contract(),
            "inputs": artifact_map(input_artifacts),
            "modes": modes,
            "artifacts": artifact_map(generated),
            "command": command_payload,
        }
        schema = json.loads(PROFILE_SCHEMA.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(manifest)
        manifest_path = staging / "manifest.json"
        manifest_path.write_bytes(canonical_bytes(manifest))
        os.replace(staging, output)
    return output / "manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--fvp-reference-gate", required=True, type=Path)
    parser.add_argument(
        "--base-disk", type=Path, default=DEFAULT_DEPLOY / "apollo-qvp-local-disk.img"
    )
    parser.add_argument(
        "--base-dtb", type=Path, default=DEFAULT_DEPLOY / "apollo-qvp.dtb"
    )
    parser.add_argument(
        "--base-initramfs", type=Path, default=DEFAULT_DEPLOY / "initramfs.cpio.gz"
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        manifest = prepare(
            args.fvp_reference_gate,
            args.base_disk,
            args.base_dtb,
            args.base_initramfs,
            args.output_dir,
            [sys.executable, *sys.argv],
        )
    except (
        ProfileError,
        OSError,
        json.JSONDecodeError,
        jsonschema.ValidationError,
    ) as error:
        print(error)
        return 1
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
