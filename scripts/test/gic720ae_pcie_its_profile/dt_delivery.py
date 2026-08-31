from __future__ import annotations

from pathlib import Path
import re
from typing import Final

from .build import BuildContext, one, run
from .contract import (
    JsonObject,
    JsonValue,
    ProfileError,
    hash_record,
    hash_record_json,
    sha256_file,
    validate_dtb_contract,
)


DT_DELIVERY_MODE: Final = "absent_firmware_fip_hw_config"


def validate_fip_hw_config(extracted: Path, generated: Path) -> None:
    if not extracted.is_file() or not generated.is_file():
        raise ProfileError("fip_hw_config_missing")
    if sha256_file(extracted) != sha256_file(generated):
        raise ProfileError("fip_hw_config_mismatch")


def validate_uki_sections(sections: dict[str, list[str]]) -> None:
    if set(sections) != {"a", "b"}:
        raise ProfileError("uki_slot_missing")
    if any(".dtb" in values for values in sections.values()):
        raise ProfileError("unexpected_uki_dtb")


def linux_dtb_reference(path: Path, runtime_consumption: str) -> JsonObject:
    if runtime_consumption != "deferred":
        raise ProfileError("false_linux_dtb_consumption_claim")
    return {
        "artifact": hash_record_json(hash_record("linux-raw-dtb", path)),
        "role": "reference_only",
        "runtime_consumption": "deferred",
        "host_contract": validate_dtb_contract(path),
    }


def section_names(output: str) -> list[str]:
    names: list[str] = []
    for line in output.splitlines():
        match = re.match(r"\s*\d+\s+(\.\S+)", line)
        if match is not None:
            names.append(match.group(1))
    if not names:
        raise ProfileError("uki_section_manifest_missing")
    return names


def extract_uki_manifests(
    context: BuildContext,
    wic: Path,
) -> tuple[list[JsonValue], list[Path]]:
    manifests: list[JsonValue] = []
    files: list[Path] = []
    sections: dict[str, list[str]] = {}
    verification = context.layout.artifacts / "verification"
    for slot in ("a", "b"):
        uki = verification / f"{slot}.efi"
        uki.parent.mkdir(parents=True, exist_ok=True)
        run(
            context,
            [
                "mcopy", "-o", "-i", f"{wic}@@1048576",
                f"::/EFI/Linux/{slot}-slot/auto-ad-nexios-{slot}.efi", str(uki),
            ],
            f"extract-uki-{slot}.log",
        )
        output = run(
            context,
            ["llvm-objdump", "-h", str(uki)],
            f"uki-{slot}-sections.log",
        )
        section_list = section_names(output)
        sections[slot] = section_list
        manifests.append({
            "slot": slot,
            "uki": hash_record_json(hash_record(f"uki-{slot}", uki)),
            "sections": [name for name in section_list],
            "dtb_present": False,
        })
        files.append(uki)
    validate_uki_sections(sections)
    return manifests, files


def inspect_dt_delivery(
    context: BuildContext,
    artifacts: dict[str, Path],
) -> tuple[JsonObject, list[Path]]:
    manifests, uki_files = extract_uki_manifests(context, artifacts["wic"])
    fiptool = one(
        list(context.layout.tmp.glob(
            "sysroots-components/x86_64/fiptool-native/usr/bin/fiptool"
        )),
        "fiptool",
    )
    fip = context.layout.deploy_image / "fip.bin"
    extracted = context.layout.artifacts / "verification/fip-hw-config.dtb"
    run(
        context,
        [str(fiptool), "unpack", "--force", "--hw-config", str(extracted), str(fip)],
        "extract-fip-hw-config.log",
    )
    generated = one(
        list(context.layout.tmp.glob(
            "work/*/trusted-firmware-a/*/build/apollo_fvp/debug/fdts/apollo_fvp_fvp.dtb"
        )),
        "generated-tfa-hw-config",
    )
    validate_fip_hw_config(extracted, generated)
    firmware_contract = validate_dtb_contract(extracted)
    slots: list[JsonValue] = [value for value in manifests]
    delivery: JsonObject = {
        "mode": DT_DELIVERY_MODE,
        "uki_slots": slots,
        "firmware_fip_hw_config": {
            "extracted": hash_record_json(hash_record("fip-hw-config", extracted)),
            "generated": hash_record_json(hash_record("generated-tfa-hw-config", generated)),
            "byte_identical": True,
            "host_contract": firmware_contract,
        },
        "linux_raw_dtb": linux_dtb_reference(artifacts["dtb"], "deferred"),
        "u_boot_candidate_order": [
            "fixed:0x8fc00000",
            "prior-stage-x1:0x80000000",
            "prior-stage-x0",
            "internal-control-dtb",
        ],
        "runtime_selection": "deferred-to-todo7-live-fdt",
    }
    return delivery, [*uki_files, extracted, generated, fiptool.resolve(), fip.resolve()]
