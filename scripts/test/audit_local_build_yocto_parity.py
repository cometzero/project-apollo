#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Final, NotRequired, TypedDict


SCHEMA_VERSION: Final = 1
ROOT: Final = Path(__file__).resolve().parents[2]
LOCAL_COMMON: Final = Path("scripts/build/local_build_common.sh")
LOCAL_CONFIG: Final = Path("scripts/build/local_build.conf")
BOOT_DISK: Final = Path("scripts/build/modules/build_boot_disk.sh")
OPTEE: Final = Path("scripts/build/modules/build_optee.sh")
MAXCPUS_PATTERN: Final = re.compile(r"(?:^|\s)maxcpus=([0-9]+)(?=\s|$)")


class RecipeEntry(TypedDict):
    command: NotRequired[str]
    variables: dict[str, str]


class VarsCapture(TypedDict):
    schema_version: int
    recipes: dict[str, RecipeEntry]


class Check(TypedDict):
    id: str
    kind: str
    status: str
    message: str
    local: NotRequired[str]
    yocto: NotRequired[str]
    source: NotRequired[str]
    recipe: NotRequired[str]
    variable: NotRequired[str]


class Report(TypedDict):
    schema_version: int
    status: str
    inputs: dict[str, str | list[str]]
    checks: list[Check]
    out_of_scope: list[dict[str, str]]


@dataclass(frozen=True, slots=True)
class LocalValues:
    machine: str
    rd_aspen_variant: str
    pc_cpus_count: str
    linux_defconfig: str
    bootloader_linux_append: str
    local_build_bootargs: str
    bootargs_uses_variable: bool
    optee_has_versioned_workdir: bool
    optee_platform: str
    uboot_defconfig: str
    linux_dtb: str


class AuditInputError(RuntimeError):
    def __init__(self, path: Path, detail: str) -> None:
        self.path = path
        self.detail = detail
        super().__init__(f"{path}: {detail}")


def read_text(path: Path) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def source_common_values() -> dict[str, str]:
    names = (
        "MACHINE",
        "RD_ASPEN_VARIANT",
        "PC_CPUS_COUNT",
        "LINUX_DEFCONFIG",
        "BOOTLOADER_LINUX_APPEND",
        "LOCAL_BUILD_BOOTARGS",
        "OPTEE_PLATFORM",
        "UBOOT_MACHINE",
        "KERNEL_DEVICETREE",
    )
    script = (
        "set -euo pipefail; "
        "source scripts/build/local_build_common.sh; "
        + " ".join(f'printf "%s=%s\\n" {name} "${{{name}}}";' for name in names)
    )
    env = {
        "PATH": os.environ.get("PATH", ""),
    }
    completed = subprocess.run(
        ["bash", "-lc", script],
        cwd=ROOT,
        check=False,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise AuditInputError(
            ROOT / LOCAL_CONFIG,
            completed.stderr.strip() or "failed to source local_build_common.sh",
        )
    values: dict[str, str] = {}
    for line in completed.stdout.splitlines():
        name, value = line.split("=", 1)
        values[name] = value
    return values


def local_values() -> LocalValues:
    boot_disk = read_text(BOOT_DISK)
    optee = read_text(OPTEE)
    sourced = source_common_values()
    return LocalValues(
        machine=sourced["MACHINE"],
        rd_aspen_variant=sourced["RD_ASPEN_VARIANT"],
        pc_cpus_count=sourced["PC_CPUS_COUNT"],
        linux_defconfig=sourced["LINUX_DEFCONFIG"],
        bootloader_linux_append=sourced["BOOTLOADER_LINUX_APPEND"],
        local_build_bootargs=sourced["LOCAL_BUILD_BOOTARGS"],
        bootargs_uses_variable='setenv bootargs "${LOCAL_BUILD_BOOTARGS}"' in boot_disk,
        optee_has_versioned_workdir="optee-os/4.7.0" in optee,
        optee_platform=sourced["OPTEE_PLATFORM"],
        uboot_defconfig=sourced["UBOOT_MACHINE"],
        linux_dtb=Path(sourced["KERNEL_DEVICETREE"]).name,
    )


def parse_capture(path: Path) -> VarsCapture:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AuditInputError(path, f"invalid JSON: {exc.msg}") from exc
    if not isinstance(raw, dict):
        raise AuditInputError(path, "top-level JSON value must be an object")
    if raw.get("schema_version") != SCHEMA_VERSION:
        raise AuditInputError(path, f"schema_version must be {SCHEMA_VERSION}")
    recipes = raw.get("recipes")
    if not isinstance(recipes, dict):
        raise AuditInputError(path, "missing recipes object")
    parsed: dict[str, RecipeEntry] = {}
    for recipe, entry in recipes.items():
        if not isinstance(recipe, str) or not isinstance(entry, dict):
            raise AuditInputError(path, "recipe entries must be objects")
        variables = entry.get("variables")
        if not isinstance(variables, dict):
            raise AuditInputError(path, f"{recipe}: missing variables object")
        parsed[recipe] = {
            "command": str(entry.get("command", "")),
            "variables": {str(name): str(value) for name, value in variables.items()},
        }
    return {"schema_version": SCHEMA_VERSION, "recipes": parsed}


def yocto_var(capture: VarsCapture, recipe: str, variable: str) -> str | None:
    entry = capture["recipes"].get(recipe)
    if entry is None:
        return None
    value = entry["variables"].get(variable)
    if value is None or value == "":
        return None
    return value.strip()


def missing_check(check_id: str, recipe: str, variable: str) -> Check:
    return {
        "id": check_id,
        "kind": "missing_yocto_var",
        "status": "fail",
        "recipe": recipe,
        "variable": variable,
        "message": f"missing_yocto_var: capture {variable} from {recipe}",
    }


def compare_check(check_id: str, local: str, yocto: str | None, recipe: str, variable: str, source: str) -> Check:
    if yocto is None:
        return missing_check(check_id, recipe, variable)
    status = "pass" if local == yocto else "fail"
    message = f"{source} matches Yocto {recipe}:{variable}"
    if status == "fail":
        message = f"{source} drift: local {local!r} != Yocto {recipe}:{variable} {yocto!r}"
    return {
        "id": check_id,
        "kind": "value_match",
        "status": status,
        "local": local,
        "yocto": yocto,
        "recipe": recipe,
        "variable": variable,
        "source": source,
        "message": message,
    }


def local_check(check_id: str, ok: bool, source: str, message: str) -> Check:
    return {
        "id": check_id,
        "kind": "local_source",
        "status": "pass" if ok else "fail",
        "source": source,
        "message": message,
    }


def bootloader_linux_append_maxcpus_check(capture: VarsCapture) -> Check | None:
    machine = yocto_var(capture, "nexios-image", "MACHINE")
    pc_cpus_count = yocto_var(capture, "nexios-image", "PC_CPUS_COUNT_DEFAULT")
    bootargs = yocto_var(capture, "nexios-image", "BOOTLOADER_LINUX_APPEND")
    if machine is None or pc_cpus_count is None or bootargs is None:
        return None
    maxcpus_match = MAXCPUS_PATTERN.search(bootargs)
    if maxcpus_match is None:
        ok = pc_cpus_count != "8"
        message = "captured BOOTLOADER_LINUX_APPEND has no maxcpus token"
        if not ok:
            message = "captured BOOTLOADER_LINUX_APPEND must contain maxcpus=8 for PC_CPUS_COUNT_DEFAULT=8"
        return {
            "id": "bootloader_linux_append_maxcpus",
            "kind": "captured_bootargs",
            "status": "pass" if ok else "fail",
            "recipe": "nexios-image",
            "variable": "BOOTLOADER_LINUX_APPEND",
            "source": "nexios-image:BOOTLOADER_LINUX_APPEND",
            "message": message,
        }
    maxcpus = maxcpus_match.group(1)
    status = "pass" if maxcpus == pc_cpus_count else "fail"
    message = f"captured BOOTLOADER_LINUX_APPEND maxcpus={maxcpus} matches captured PC_CPUS_COUNT_DEFAULT={pc_cpus_count}"
    if status == "fail":
        message = (
            f"captured BOOTLOADER_LINUX_APPEND maxcpus={maxcpus} does not match "
            f"captured PC_CPUS_COUNT_DEFAULT={pc_cpus_count}"
        )
    return {
        "id": "bootloader_linux_append_maxcpus",
        "kind": "captured_bootargs",
        "status": status,
        "local": maxcpus,
        "yocto": pc_cpus_count,
        "recipe": "nexios-image",
        "variable": "BOOTLOADER_LINUX_APPEND",
        "source": "nexios-image:BOOTLOADER_LINUX_APPEND",
        "message": message,
    }


def build_checks(capture: VarsCapture, local: LocalValues) -> list[Check]:
    bootargs_var = yocto_var(capture, "nexios-image", "BOOTLOADER_LINUX_APPEND")
    if bootargs_var is not None:
        bootargs_var = " ".join(bootargs_var.split())
    local_bootargs_tail = " ".join(local.bootloader_linux_append.split())
    expected_bootargs = (
        "console=ttyAMA0,115200 earlycon=pl011,0x1A400000 root=/dev/ram0 rw rdinit=/init loglevel=7"
    )
    if bootargs_var is not None:
        expected_bootargs = f"{expected_bootargs} {bootargs_var}"
    checks = [
        compare_check("machine", local.machine, yocto_var(capture, "nexios-image", "MACHINE"), "nexios-image", "MACHINE", str(LOCAL_CONFIG)),
        compare_check("pc_cpus_count", local.pc_cpus_count, yocto_var(capture, "nexios-image", "PC_CPUS_COUNT_DEFAULT"), "nexios-image", "PC_CPUS_COUNT_DEFAULT", str(LOCAL_CONFIG)),
        compare_check("rd_aspen_variant", local.rd_aspen_variant, yocto_var(capture, "nexios-image", "RD_ASPEN_VARIANT"), "nexios-image", "RD_ASPEN_VARIANT", str(LOCAL_CONFIG)),
        compare_check("uboot_defconfig", local.uboot_defconfig, yocto_var(capture, "u-boot", "UBOOT_MACHINE"), "u-boot", "UBOOT_MACHINE", str(LOCAL_CONFIG)),
        compare_check("linux_dtb", local.linux_dtb, Path(yocto_var(capture, "linux-yocto-rt", "KERNEL_DEVICETREE") or "").name or None, "linux-yocto-rt", "KERNEL_DEVICETREE", str(LOCAL_CONFIG)),
        compare_check("linux_defconfig", local.linux_defconfig, yocto_var(capture, "linux-yocto-rt", "KBUILD_DEFCONFIG"), "linux-yocto-rt", "KBUILD_DEFCONFIG", str(LOCAL_CONFIG)),
        compare_check("optee_platform", local.optee_platform, yocto_var(capture, "optee-os", "PLATFORM"), "optee-os", "PLATFORM", str(LOCAL_CONFIG)),
    ]
    checks.append(
        missing_check("bootloader_linux_append_capture", "nexios-image", "BOOTLOADER_LINUX_APPEND")
        if bootargs_var is None
        else compare_check("bootloader_linux_append_capture", local_bootargs_tail, bootargs_var, "nexios-image", "BOOTLOADER_LINUX_APPEND", str(LOCAL_CONFIG))
    )
    checks.append(
        missing_check("boot_disk_bootargs", "nexios-image", "BOOTLOADER_LINUX_APPEND")
        if bootargs_var is None
        else compare_check("boot_disk_bootargs", local.local_build_bootargs, expected_bootargs, "nexios-image", "BOOTLOADER_LINUX_APPEND", str(BOOT_DISK))
    )
    maxcpus_check = bootloader_linux_append_maxcpus_check(capture)
    if maxcpus_check is not None:
        checks.append(maxcpus_check)
    checks.append(
        local_check(
            "boot_disk_bootargs_source",
            local.bootargs_uses_variable,
            str(BOOT_DISK),
            "boot disk bootargs must be derived from Yocto-captured BOOTLOADER_LINUX_APPEND, not a setenv literal",
        )
    )
    checks.append(
        local_check(
            "optee_workdir_source",
            not local.optee_has_versioned_workdir,
            str(OPTEE),
            "OP-TEE workdir must resolve the Yocto optee-os workdir instead of hard-coding optee-os/4.7.0",
        )
    )
    return checks


def out_of_scope() -> list[dict[str, str]]:
    return [
        {"id": "full_product_rootfs", "reason": "local-build does not rebuild nexios-image rootfs package contents"},
        {"id": "wic_image_layout", "reason": "Yocto WIC partition layout remains Yocto-only product image behavior"},
        {"id": "dm_verity_image", "reason": "dm-verity ext4.verity generation is outside local component build parity"},
        {"id": "product_image_packaging", "reason": "license, package QA, sstate, UKI/A-B, and final product image assembly stay in Yocto"},
    ]


def build_report(vars_path: Path) -> Report:
    capture = parse_capture(vars_path)
    checks = build_checks(capture, local_values())
    status = "fail" if any(check["status"] == "fail" for check in checks) else "pass"
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "inputs": {
            "vars": str(vars_path),
            "repo_root": str(ROOT),
            "local_files": [str(LOCAL_CONFIG), str(LOCAL_COMMON), str(BOOT_DISK), str(OPTEE)],
        },
        "checks": checks,
        "out_of_scope": out_of_scope(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit local-build parity against captured Yocto variables.")
    parser.add_argument("--vars", required=True, type=Path, help="Yocto variable JSON from collect_yocto_local_build_vars.py")
    parser.add_argument("--output", required=True, type=Path, help="Path to write audit JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = build_report(args.vars)
    except AuditInputError as exc:
        report = {
            "schema_version": SCHEMA_VERSION,
            "status": "fail",
            "inputs": {"vars": str(args.vars), "repo_root": str(ROOT), "local_files": []},
            "checks": [{"id": "input", "kind": "input_error", "status": "fail", "message": str(exc)}],
            "out_of_scope": out_of_scope(),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if report["status"] == "fail":
        failed = ", ".join(check["kind"] for check in report["checks"] if check["status"] == "fail")
        print(f"audit status: fail ({failed})", file=sys.stderr)
        return 1
    print("audit status: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
