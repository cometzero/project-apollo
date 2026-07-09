#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
from datetime import UTC, datetime
from typing import Final


SCHEMA_VERSION: Final = 1
DESCRIPTION: Final = (
    "Collect allowlisted Yocto variables from recipe-specific BitBake environments."
)
DEFAULT_MACHINE: Final = "apollo-fvp"
DEFAULT_RECIPES: Final = (
    "nexios-image",
    "u-boot",
    "linux-yocto-rt",
    f"firmware-{DEFAULT_MACHINE}",
    "trusted-firmware-m",
    "scp-firmware",
    "trusted-firmware-a",
    "optee-os",
    "zephyr-demos-cl1",
    "qbox-apollo-qvp-native",
)
ALLOWLISTED_VARIABLES: Final = frozenset(
    {
        "MACHINE",
        "DISTRO",
        "BB_VERSION",
        "TEMPLATECONF",
        "RD_ASPEN_VARIANT",
        "PC_CPUS_COUNT_DEFAULT",
        "IMAGE_FSTYPES",
        "IMAGE_ROOTFS_SIZE",
        "IMAGE_INSTALL",
        "BOOTLOADER_LINUX_APPEND",
        "UBOOT_MACHINE",
        "UBOOT_CONFIG",
        "KBUILD_DEFCONFIG",
        "KERNEL_DEVICETREE",
        "KERNEL_FEATURES",
        "KERNEL_DEBUG_INFO",
        "OPTEEMACHINE",
        "PLATFORM",
        "TF_A_PLATFORM",
        "TFM_PLATFORM",
        "SCP_PLATFORM",
        "ZEPHYR_BOARD",
        "ZEPHYR_APPLICATION",
        "KERNEL_CONSOLE",
        "INITRD_ARCHIVE",
        "EFI_ARCH",
        "AUTO_AD_NEXIOS_UKI_A",
        "AUTO_AD_NEXIOS_UKI_B",
        "AUTO_AD_NEXIOS_UKI_CMDLINE_A",
        "AUTO_AD_NEXIOS_UKI_CMDLINE_B",
        "UKIFY_CMD",
        "UEFI_SECURE_BOOT",
        "UKI_SB_KEY",
        "UKI_SB_CERT",
        "QBOX_APOLLO_BUILD_TARGET",
        "HSOC_APOLLO_QBOX_SRC",
        "HSOC_APOLLO_QBOX_PLATFORM_SRC",
        "HSOC_APOLLO_QEMU_SRC",
        "EXTERNALSRC",
        "EXTERNALSRC_BUILD",
    }
)
BITBAKE_VARIABLE_ALIASES: Final = {
    "TFA_PLATFORM": "TF_A_PLATFORM",
}
EXTRA_SOURCE_VARIABLES: Final = frozenset({"EXTRA_OEMAKE"})
BITBAKE_VARIABLES: Final = (
    ALLOWLISTED_VARIABLES | frozenset(BITBAKE_VARIABLE_ALIASES) | EXTRA_SOURCE_VARIABLES
)
RECIPE_REQUIRED_VARIABLES: Final = {
    "nexios-image": ("BOOTLOADER_LINUX_APPEND",),
    "u-boot": ("UBOOT_MACHINE",),
    "linux-yocto-rt": ("KBUILD_DEFCONFIG", "KERNEL_DEVICETREE"),
    "optee-os": ("PLATFORM",),
}
CONFIG_FILES: Final = ("local.conf", "bblayers.conf", "templateconf.cfg")
ASSIGNMENT_RE: Final = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
RECIPE_RE: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9+_.:-]*$")
MACHINE_RE: Final = re.compile(
    r'^\s*MACHINE\s*(?:\?\?=|\?=|:=|\+=|=)\s*"([^"]+)"'
)


class CollectVarsError(RuntimeError):
    pass


class BitBakeEnvParseError(CollectVarsError):
    pass


class MissingVariablesError(CollectVarsError):
    def __init__(self, recipe: str, missing: list[str]) -> None:
        self.recipe = recipe
        self.missing = tuple(missing)
        joined = ", ".join(missing)
        super().__init__(f"{recipe}: missing required variable(s): {joined}")


class BitBakeCommandError(CollectVarsError):
    pass


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def parse_recipe_list(value: str) -> list[str]:
    recipes = [part.strip() for part in value.split(",") if part.strip()]
    invalid = [recipe for recipe in recipes if not RECIPE_RE.fullmatch(recipe)]
    if invalid:
        joined = ", ".join(invalid)
        raise argparse.ArgumentTypeError(f"invalid recipe name(s): {joined}")
    if not recipes:
        raise argparse.ArgumentTypeError("at least one recipe is required")
    return recipes


def _decode_assignment_value(name: str, raw_value: str) -> tuple[str, bool]:
    text = raw_value.lstrip()
    if not text:
        return "", True
    quote = text[0]
    if quote not in {"'", '"'}:
        return text.rstrip("\n"), True

    value: list[str] = []
    index = 1
    while index < len(text):
        char = text[index]
        if char == quote:
            trailing = text[index + 1 :].strip()
            if trailing:
                raise BitBakeEnvParseError(
                    f"{name}: unexpected trailing text after quoted assignment"
                )
            return "".join(value), True
        if quote == '"' and char == "\\":
            if index + 1 >= len(text):
                value.append(char)
                index += 1
                continue
            next_char = text[index + 1]
            if next_char == "\n":
                index += 2
                continue
            if next_char in {'"', "\\", "$", "`"}:
                value.append(next_char)
                index += 2
                continue
        value.append(char)
        index += 1
    return "".join(value), False


def _assignment_value(name: str, raw_value: str, following: list[str]) -> tuple[str, int]:
    value_text = raw_value
    consumed = 0
    while True:
        value, closed = _decode_assignment_value(name, value_text)
        if closed:
            return value, consumed
        if consumed >= len(following):
            raise BitBakeEnvParseError(f"{name}: unterminated quoted assignment")
        value_text += following[consumed]
        consumed += 1


def parse_bitbake_env(raw: str) -> dict[str, str]:
    variables: dict[str, str] = {}
    lines = raw.splitlines(keepends=True)
    index = 0
    while index < len(lines):
        match = ASSIGNMENT_RE.match(lines[index])
        if match is None:
            index += 1
            continue
        name = match.group(1)
        if name not in BITBAKE_VARIABLES:
            index += 1
            continue
        value, consumed = _assignment_value(name, match.group(2), lines[index + 1 :])
        if name == "EXTRA_OEMAKE":
            for token in shlex.split(value):
                if token.startswith("PLATFORM="):
                    variables["PLATFORM"] = token.removeprefix("PLATFORM=")
            index += consumed + 1
            continue
        output_name = BITBAKE_VARIABLE_ALIASES.get(name, name)
        variables[output_name] = value
        index += consumed + 1
    return dict(sorted(variables.items()))


def require_recipe_variables(recipe: str, variables: dict[str, str]) -> None:
    required = ["MACHINE", *RECIPE_REQUIRED_VARIABLES.get(recipe, ())]
    missing = [name for name in required if not variables.get(name)]
    if missing:
        raise MissingVariablesError(recipe, missing)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def config_paths(build_dir: Path) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    conf_dir = build_dir / "conf"
    for name in CONFIG_FILES:
        path = conf_dir / name
        entry = {"path": str(path)}
        if path.is_file():
            entry["sha256"] = sha256_file(path)
        result[name] = entry
    return result


def shell_command(build_dir_arg: Path, recipe: str) -> str:
    build_dir = shlex.quote(str(build_dir_arg))
    recipe_name = shlex.quote(recipe)
    return (
        "set -euo pipefail; "
        f"set +u; source layers/poky/oe-init-build-env {build_dir} >/dev/null; "
        f"set -u; bitbake -e {recipe_name}"
    )


def command_text(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def collect_recipe(root: Path, build_dir_arg: Path, recipe: str, timeout: int) -> dict[str, object]:
    command = ["bash", "-lc", shell_command(build_dir_arg, recipe)]
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise BitBakeCommandError(
            f"{recipe}: timed out after {timeout}s while running bitbake -e"
        ) from exc

    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        detail = f": {stderr}" if stderr else ""
        raise BitBakeCommandError(
            f"{recipe}: bitbake -e failed with exit code {completed.returncode}{detail}"
        )

    variables = parse_bitbake_env(completed.stdout)
    require_recipe_variables(recipe, variables)
    return {"command": command_text(command), "variables": variables}


def build_dir_path(root: Path, build_dir_arg: Path) -> Path:
    if build_dir_arg.is_absolute():
        return build_dir_arg
    return root / build_dir_arg


def machine_from_build_dir(build_dir: Path) -> str:
    local_conf = build_dir / "conf" / "local.conf"
    try:
        lines = local_conf.read_text(encoding="utf-8").splitlines()
    except OSError:
        return DEFAULT_MACHINE
    machine = ""
    for line in lines:
        match = MACHINE_RE.match(line)
        if match:
            machine = match.group(1).strip()
    return machine or DEFAULT_MACHINE


def default_recipes_for_machine(machine: str) -> tuple[str, ...]:
    default_firmware_recipe = f"firmware-{DEFAULT_MACHINE}"
    active_firmware_recipe = f"firmware-{machine}"
    return tuple(
        active_firmware_recipe if recipe == default_firmware_recipe else recipe
        for recipe in DEFAULT_RECIPES
    )


def write_collection(args: argparse.Namespace) -> Path:
    root = workspace_root()
    recipes = parse_recipe_list(args.recipes)
    build_dir = build_dir_path(root, args.build_dir)
    collected = {
        recipe: collect_recipe(root, args.build_dir, recipe, args.timeout)
        for recipe in recipes
    }
    result = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(tz=UTC).isoformat().replace("+00:00", "Z"),
        "repo_root": str(root),
        "build_dir": str(build_dir),
        "config_paths": config_paths(build_dir),
        "recipes": collected,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return args.output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--recipes")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--build-dir", type=Path, default=Path("build"))
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    build_dir = build_dir_path(workspace_root(), args.build_dir)
    machine = machine_from_build_dir(build_dir)
    if args.recipes is None:
        args.recipes = ",".join(default_recipes_for_machine(machine))
    if args.output is None:
        args.output = args.build_dir / f"local-{machine}/yocto-local-build-vars.json"
    return args


def main() -> int:
    try:
        output = write_collection(parse_args())
    except CollectVarsError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except argparse.ArgumentTypeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
