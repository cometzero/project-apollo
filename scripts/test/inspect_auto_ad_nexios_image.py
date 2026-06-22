#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from auto_ad_nexios_image_inspector_artifacts import (  # noqa: E402
    check_filesystems,
    inspect_host_fixture_evidence,
    inspect_runtime_evidence,
    inspect_secure_boot_parse_log,
    inspect_uboot_artifacts,
    inspect_verity,
)
from auto_ad_nexios_image_inspector_lib import (  # noqa: E402
    DEFAULT_EXPECTED, ESP_TYPE, EXPECTED_ORDER, LINUX_TYPE, MISC_CRC_OFFSET,
    MISC_HEADER_SIZE, MISC_MAGIC, MISC_SIZE, MISC_VERSION, SECTOR_SIZE,
    SLOT_UKI_FILES, InspectError, check_partition_contract, copy_from_fat,
    crc32_misc_header, inspect_esp_slots, parse_expect_partitions,
    parse_misc_blob, parse_sgdisk, parse_size, read_exact,
)

DEFAULT_EVIDENCE_ROOT = Path(".omo/evidence/auto-ad-nexios-yocto-boot")


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Inspect an auto-ad-nexios Apollo FVP A/B WIC image."
    )
    parser.add_argument("--wic", required=True, help="path to the .wic image")
    parser.add_argument(
        "--deploy-dir",
        help="deploy directory containing dm-verity side artifacts",
    )
    parser.add_argument(
        "--expect-partitions",
        default=",".join(f"{name}={size}" for name, size in DEFAULT_EXPECTED.items()),
        help="comma-separated partition contract, for example boot_a=128M,...",
    )
    parser.add_argument(
        "--expect-default-slot",
        choices=("A", "B"),
        default="A",
        help="expected slot encoded in the misc partition",
    )
    parser.add_argument(
        "--uefi-secure-boot",
        choices=("0", "1"),
        default=os.environ.get("UEFI_SECURE_BOOT"),
        help="if 1, require UKIs to contain a PE certificate table",
    )
    parser.add_argument("--json", help="write a JSON inspection summary")
    parser.add_argument(
        "--negative-suite",
        action="store_true",
        help="run fixture-backed negative slot and integrity checks",
    )
    parser.add_argument(
        "--work-dir",
        help="directory for negative-suite evidence artifacts",
    )
    parser.add_argument(
        "--host-fixture-evidence",
        default=str(DEFAULT_EVIDENCE_ROOT / "task-07-host-fixture-result.json"),
        help="task 7 U-Boot host fixture result JSON for fallback behavior evidence",
    )
    parser.add_argument(
        "--negative-runtime-evidence",
        default=str(DEFAULT_EVIDENCE_ROOT / "task-12-negative-runtime-result.json"),
        help="task 12 corrupted-rootro runtime result JSON for dm-verity evidence",
    )
    parser.add_argument(
        "--secure-boot-parse-log",
        default=str(DEFAULT_EVIDENCE_ROOT / "task-12-negative" / "secure-boot-parse.log"),
        help="BitBake parse log proving UEFI_SECURE_BOOT=1 without keys fails",
    )
    return parser.parse_args(argv)


def inspect_misc(wic, misc_part, expected_slot):
    info = parse_misc_blob(read_exact(wic, misc_part["offset"], MISC_SIZE))
    if expected_slot and info["slot"] != expected_slot:
        raise InspectError(
            f"misc default slot mismatch: expected {expected_slot}, got {info['slot']}"
        )
    if info["attempts"] != 3:
        raise InspectError(f"misc attempts mismatch: expected 3, got {info['attempts']}")
    if info["flags"] != 0x0002:
        raise InspectError(
            f"misc flags mismatch: expected 0x0002, got {info['flags']:#06x}"
        )
    if info["generation"] != 0:
        raise InspectError(f"misc generation mismatch: expected 0, got {info['generation']}")
    return info


def detect_image_base(wic):
    name = Path(wic).name
    return name[:-4] if name.endswith(".wic") else name


def inspect(args):
    wic = Path(args.wic)
    if not wic.exists():
        raise InspectError(f"WIC image does not exist: {wic}")
    expected = parse_expect_partitions(args.expect_partitions)
    if list(expected) != EXPECTED_ORDER:
        raise InspectError("--expect-partitions must list exactly: " + ",".join(EXPECTED_ORDER))
    partitions = parse_sgdisk(wic)
    by_name = check_partition_contract(partitions, expected)
    deploy_dir = Path(args.deploy_dir) if args.deploy_dir else wic.parent
    return {
        "wic": str(wic),
        "gpt": True,
        "partitions": partitions,
        "filesystems": check_filesystems(wic, by_name),
        "misc": inspect_misc(wic, by_name["misc"], args.expect_default_slot),
        "esp": inspect_esp_slots(wic, by_name, args.uefi_secure_boot, deploy_dir),
        "dm_verity": inspect_verity(deploy_dir, detect_image_base(wic)),
        "u_boot": inspect_uboot_artifacts(deploy_dir),
        "result": "PASS",
    }


def copy_slot_uki_fixture(wic, by_name, work_dir):
    esp_dir = work_dir / "esp-fixture"
    result = {}
    for slot in ("boot_a", "boot_b"):
        slot_dir = esp_dir / slot / "EFI" / "Linux"
        slot_dir.mkdir(parents=True, exist_ok=True)
        uki_path = slot_dir / Path(SLOT_UKI_FILES[slot]).name
        copy_from_fat(wic, by_name[slot], SLOT_UKI_FILES[slot], uki_path)
        result[slot] = str(uki_path)
    return result


def run_negative_suite(args):
    wic = Path(args.wic)
    work_dir = Path(args.work_dir) if args.work_dir else wic.parent / "negative-suite"
    work_dir.mkdir(parents=True, exist_ok=True)

    expected = parse_expect_partitions(args.expect_partitions)
    partitions = parse_sgdisk(wic)
    by_name = check_partition_contract(partitions, expected)
    summary = inspect(args)
    (work_dir / "positive-inspection.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )

    misc_blob = bytearray(read_exact(wic, by_name["misc"]["offset"], MISC_SIZE))
    valid_misc = work_dir / "misc-valid.bin"
    valid_misc.write_bytes(misc_blob)
    misc_blob[0] ^= 0x01
    corrupt_misc = work_dir / "misc-corrupt.bin"
    corrupt_misc.write_bytes(misc_blob)
    misc_error = ""
    try:
        parse_misc_blob(bytes(misc_blob))
    except InspectError as exc:
        misc_error = str(exc)
    if not misc_error:
        raise InspectError("corrupt misc fixture was accepted")

    esp_files = copy_slot_uki_fixture(wic, by_name, work_dir)
    missing_a = Path(esp_files["boot_a"])
    missing_a.unlink()
    fallback_b = Path(esp_files["boot_b"])
    if fallback_b.name != "auto-ad-nexios-b.efi" or not fallback_b.exists():
        raise InspectError("missing selected UKI fixture did not expose fallback B")

    corrupt_misc_evidence, missing_uki_evidence = inspect_host_fixture_evidence(
        args.host_fixture_evidence
    )

    negative = {
        "bad_dm_verity_root": inspect_runtime_evidence(args.negative_runtime_evidence),
        "corrupt_misc": {
            **corrupt_misc_evidence,
            "corrupt_fixture": str(corrupt_misc),
            "observed_error": misc_error,
            "expected_behavior": "invalid misc defaults to slot A",
        },
        "missing_selected_uki": {
            **missing_uki_evidence,
            "removed": str(missing_a),
            "fallback": str(fallback_b),
            "expected_behavior": "missing selected A UKI tries alternate B once",
        },
        "secure_boot_without_keys": inspect_secure_boot_parse_log(args.secure_boot_parse_log),
        "unsigned_default": {
            "status": "INFO_ONLY",
            "policy": "not a negative behavior; positive inspection records unsigned UKIs",
        },
    }
    required_statuses = [
        negative["bad_dm_verity_root"]["status"],
        negative["corrupt_misc"]["status"],
        negative["missing_selected_uki"]["status"],
        negative["secure_boot_without_keys"]["status"],
    ]
    result = (
        "PASS"
        if all(status == "PASS" for status in required_statuses)
        else "EXTERNAL_EVIDENCE_REQUIRED"
    )
    report = {
        "result": result,
        "work_dir": str(work_dir),
        "negative": negative,
    }
    (work_dir / "negative-suite.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    return report


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        if args.negative_suite:
            summary = run_negative_suite(args)
        else:
            summary = inspect(args)
    except InspectError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    if args.json:
        Path(args.json).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    if args.negative_suite:
        negative = summary["negative"]
        print(
            f"{summary['result']}: negative_suite={summary['result']} "
            f"corrupt_misc={negative['corrupt_misc']['status']} "
            f"missing_selected_uki_fallback={negative['missing_selected_uki']['status']} "
            f"bad_dm_verity_root={negative['bad_dm_verity_root']['status']} "
            f"secure_boot_parse={negative['secure_boot_without_keys']['status']}"
        )
        return 0
    print(
        "PASS: partition_contract=PASS misc_default_slot="
        f"{summary['misc']['slot']} esp=PASS dm_verity=PASS"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
