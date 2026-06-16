#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import TypeAlias


SRAM_NAMES = (
    "host_si_cl0_sram",
    "host_si_cl1_sram",
    "host_ap_shared_sram",
    "host_ap_bl2_header_sram",
)
SRAM_FILE_PATTERNS = (
    "host-si-cl*-sram.bin",
    "host-ap-*-sram.bin",
)
DESCRIPTION = "Check QBox SRAM DMI fast-path machine-readable run evidence."
DIRECT_FILE_ALIAS_COUNTERS = (
    ("bl2_load_accel", "direct_file_alias_hits"),
    ("bl2_boot_enc_accel", "decrypt_direct_file_alias_hits"),
    ("bl2_img_hash_accel", "direct_file_alias_hits"),
)
JsonValue: TypeAlias = (
    None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
)
JsonObject: TypeAlias = dict[str, JsonValue]


def read_json_object(path: Path) -> JsonObject:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CheckError(f"{path}: file not found") from exc
    except json.JSONDecodeError as exc:
        raise CheckError(
            f"{path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(data, dict):
        raise CheckError(f"{path}: expected a JSON object")
    return data


class CheckError(Exception):
    pass


def dict_at(data: JsonObject, key: str) -> JsonObject:
    value = data.get(key)
    if not isinstance(value, dict):
        raise CheckError(f"missing or invalid object: {key}")
    return value


def nested_dict(data: JsonObject, keys: tuple[str, ...]) -> JsonObject | None:
    current: JsonValue = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current if isinstance(current, dict) else None


def load_run_result(path: Path) -> tuple[JsonObject, Path]:
    result = read_json_object(path)
    if "host_sram_backing" in result:
        return result, path
    child_value = result.get("child_result")
    if isinstance(child_value, str) and child_value:
        child_path = Path(child_value)
        if not child_path.is_absolute():
            child_path = path.parent / child_path
        child = read_json_object(child_path)
        if "host_sram_backing" in child:
            return child, child_path
    child_status = result.get("child_status")
    if isinstance(child_status, dict) and "host_sram_backing" in child_status:
        return child_status, path
    return result, path


def profile_from_result(result: JsonObject) -> JsonObject | None:
    return nested_dict(result, ("qbox_perf_profile", "rse_hotpath_profile", "stats"))


def load_profile(args: argparse.Namespace, result: JsonObject) -> JsonObject | None:
    profile_path = args.profile
    if profile_path is not None:
        return read_json_object(profile_path)
    profile = profile_from_result(result)
    if profile is not None:
        return profile
    if args.out_dir is None:
        return None
    default_path = args.out_dir / "qbox-perf-profile" / "rse-hotpath-profile.json"
    if not default_path.exists():
        return None
    return read_json_object(default_path)


def int_value(data: JsonObject, key: str) -> int:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise CheckError(f"missing or invalid integer counter: {key}")
    return value


def check_expected_mode(result: JsonObject, expected: str) -> list[str]:
    backing = dict_at(result, "host_sram_backing")
    errors = []
    for name in SRAM_NAMES:
        entry = backing.get(name)
        if not isinstance(entry, dict):
            errors.append(f"host_sram_backing.{name}: missing object")
            continue
        mode = entry.get("mode")
        if mode != expected:
            errors.append(
                f"host_sram_backing.{name}.mode: expected {expected!r}, got {mode!r}"
            )
        if expected == "shared_memory" and entry.get("shared_memory") is not True:
            errors.append(f"host_sram_backing.{name}.shared_memory is not true")
        if expected == "shared_memory" and entry.get("map_file"):
            errors.append(f"host_sram_backing.{name}.map_file is set")
        if expected == "shared_memory" and entry.get("file_created") is True:
            errors.append(f"host_sram_backing.{name}.file_created is true")
    return errors


def check_no_sram_files(out_dir: Path) -> list[str]:
    found = []
    for pattern in SRAM_FILE_PATTERNS:
        found.extend(str(path) for path in sorted(out_dir.rglob(pattern)))
    return [f"unexpected SRAM backing files: {', '.join(found)}"] if found else []


def check_no_direct_alias(
    result: JsonObject,
    profile: JsonObject | None,
    require_profile_counters: bool = False,
) -> list[str]:
    errors = []
    summary = result.get("rse_direct_file_aliases_summary")
    legacy = result.get("rse_direct_si_sram_alias")
    if isinstance(summary, dict):
        if summary.get("enabled") is True or summary.get("raw_spec_present") is True:
            errors.append("rse_direct_file_aliases_summary reports direct aliases")
    elif isinstance(legacy, dict):
        if legacy.get("enabled") is True or legacy.get("direct_file_aliases"):
            errors.append("rse_direct_si_sram_alias reports direct aliases")
    else:
        errors.append("missing direct-file-alias summary")
    if profile is None:
        return errors
    for section, key in DIRECT_FILE_ALIAS_COUNTERS:
        counter_path = f"stats.{section}.{key}"
        section_data = profile.get(section)
        if not isinstance(section_data, dict):
            if require_profile_counters:
                errors.append(f"missing direct-file-alias counter section: stats.{section}")
            continue
        value = section_data.get(key)
        if isinstance(value, bool) or not isinstance(value, int):
            if require_profile_counters:
                errors.append(f"missing or invalid direct-file-alias counter: {counter_path}")
            continue
        if value != 0:
            errors.append(f"{counter_path} is nonzero: {value}")
    return errors


def check_bl2_hits(profile: JsonObject | None) -> list[str]:
    if profile is None:
        return ["missing RSE hotpath profile for accelerator hit check"]
    errors = []
    load = dict_at(profile, "bl2_load_accel")
    img_hash = dict_at(profile, "bl2_img_hash_accel")
    boot_enc = dict_at(profile, "bl2_boot_enc_accel")
    if int_value(load, "hits") <= 0:
        errors.append("stats.bl2_load_accel.hits is zero")
    if int_value(img_hash, "hits") <= 0:
        errors.append("stats.bl2_img_hash_accel.hits is zero")
    if int_value(load, "dmi_failures") != 0:
        errors.append("stats.bl2_load_accel.dmi_failures is nonzero")
    if int_value(img_hash, "dmi_failures") != 0:
        errors.append("stats.bl2_img_hash_accel.dmi_failures is nonzero")
    if int_value(load, "direct_file_alias_hits") != 0:
        errors.append("stats.bl2_load_accel.direct_file_alias_hits is nonzero")
    if int_value(img_hash, "direct_file_alias_hits") != 0:
        errors.append("stats.bl2_img_hash_accel.direct_file_alias_hits is nonzero")
    if int_value(boot_enc, "decrypt_dmi_failures") != 0:
        errors.append("stats.bl2_boot_enc_accel.decrypt_dmi_failures is nonzero")
    if int_value(boot_enc, "decrypt_direct_file_alias_hits") != 0:
        errors.append(
            "stats.bl2_boot_enc_accel.decrypt_direct_file_alias_hits is nonzero"
        )
    if int_value(boot_enc, "decrypt_hits") <= 0 and int_value(load, "hits") <= 0:
        errors.append(
            "stats.bl2_boot_enc_accel.decrypt_hits is zero without "
            "bl2_load_accel full-image decrypt coverage"
        )
    return errors


def check_zero_dmi_failures(profile: JsonObject | None) -> list[str]:
    if profile is None:
        return ["missing RSE hotpath profile for DMI failure check"]
    errors = []
    pending: list[tuple[str, JsonObject]] = [("profile", profile)]
    while pending:
        path, data = pending.pop()
        for key, value in sorted(data.items()):
            counter_path = f"{path}.{key}"
            if isinstance(value, dict):
                pending.append((counter_path, value))
                continue
            if not key.endswith("dmi_failures"):
                continue
            if isinstance(value, bool) or not isinstance(value, int):
                errors.append(f"{counter_path} is not an integer")
            elif value != 0:
                errors.append(f"{counter_path} is nonzero: {value}")
    return errors


def check_pass_mode(result: JsonObject, expected: str) -> list[str]:
    actual = result.get("pass_mode")
    if actual != expected:
        return [f"pass_mode: expected {expected!r}, got {actual!r}"]
    return []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--result", required=True, type=Path, help="result.json path")
    parser.add_argument("--out-dir", type=Path, help="run output directory")
    parser.add_argument("--expect-mode", help="expected host_sram_backing mode")
    parser.add_argument("--expect-pass-mode", help="expected result pass_mode")
    parser.add_argument("--require-no-sram-files", action="store_true")
    parser.add_argument("--require-no-direct-file-alias", action="store_true")
    parser.add_argument("--profile", type=Path, help="rse-hotpath-profile.json path")
    parser.add_argument("--require-bl2-accelerator-hits", action="store_true")
    parser.add_argument("--require-zero-dmi-failures", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    try:
        result, result_path = load_run_result(args.result)
        profile = load_profile(args, result)
        if args.expect_pass_mode:
            errors.extend(check_pass_mode(result, args.expect_pass_mode))
        if args.expect_mode:
            errors.extend(check_expected_mode(result, args.expect_mode))
        if args.require_no_sram_files:
            if args.out_dir is None:
                errors.append("--require-no-sram-files requires --out-dir")
            else:
                errors.extend(check_no_sram_files(args.out_dir))
        if args.require_no_direct_file_alias:
            errors.extend(
                check_no_direct_alias(
                    result,
                    profile,
                    require_profile_counters=args.profile is not None,
                )
            )
        if args.require_bl2_accelerator_hits:
            errors.extend(check_bl2_hits(profile))
        if args.require_zero_dmi_failures:
            errors.extend(check_zero_dmi_failures(profile))
    except CheckError as exc:
        errors.append(str(exc))
        result_path = args.result
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: SRAM DMI fast-path evidence OK ({result_path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
