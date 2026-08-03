#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/capture_gic720ae_runtime_provenance.py --help
# 3. Or: python3 scripts/test/capture_gic720ae_runtime_provenance.py --help
# ──────────────────
"""Capture a fresh local-build invocation and source/output closure."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess

from gic720ae_contract import ContractError, sha_path, validate, write_json


REQUIRED_OWNERS = {
    ".", "arm-zena-css", "hsoc-stack/tools/qbox", "hsoc-stack/tools/qbox-platform",
    "hsoc-stack/tools/qemu", "hsoc-stack/tools/buildroot",
    "hsoc-stack/components/system_mgmt/trusted-firmware-m",
    "hsoc-stack/components/system_mgmt/scp-firmware",
    "hsoc-stack/components/system_mgmt/zephyrproject/zephyr",
    "hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src",
    "hsoc-stack/components/primary_compute/trusted-firmware-a",
    "hsoc-stack/components/primary_compute/optee_os",
    "hsoc-stack/components/primary_compute/u-boot",
    "hsoc-stack/components/primary_compute/linux",
    "hsoc-stack/yocto/meta-hsoc-auto-solutions",
    "hsoc-stack/yocto/meta-hsoc-bsp", "layers/meta-arm", "layers/poky",
}
SHELL_CONTROL = re.compile(r"[;&|<>`$()\n\r]")
COMPONENT_ACTIONS = {
    "qbox": ("./local_build.sh", "clean-build"),
    "qbox-task17": ("./local_build.sh", "clean-build"),
    "qbox-task38": ("./local_build.sh", "clean-build"),
    "scp-cl0": ("./local_build.sh", "scp-firmware", "clean-build"),
    "scp-power-test": (
        "python3", "scripts/test/build_gic720ae_scp_power_profile.py",
    ),
    "zephyr-qbox-standard": ("west", "build"),
    "zephyr-qbox-standard-task38": ("west", "build"),
    "zephyr-qbox-extirq": ("west", "build"),
    "zephyr-qbox-extirq-task38": ("west", "build"),
    "fvp-standard": ("python3", "scripts/test/build_gic720ae_fvp_profiles.py"),
    "fvp-extirq": ("python3", "scripts/test/build_gic720ae_fvp_profiles.py"),
    "fvp-power": ("python3", "scripts/test/build_gic720ae_fvp_profiles.py"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", required=True)
    parser.add_argument("--producer-mode", choices=("clean_build", "taskhash"), required=True)
    parser.add_argument("--cwd", type=Path, default=Path("."))
    parser.add_argument("--build-command", required=True)
    parser.add_argument("--source-repos", required=True)
    parser.add_argument("--require-local-build-source-closure", action="store_true")
    parser.add_argument("--require-recipe-sysroot-taskhash", action="store_true")
    parser.add_argument("--config-files")
    parser.add_argument("--require-cache-value", action="append", default=[])
    parser.add_argument("--require-local-qemu-source", type=Path)
    parser.add_argument("--require-outputs", required=True)
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def git_head(path: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=False, capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise ContractError("unowned_source", str(path))
    return result.stdout.strip()


def command_argv(args: argparse.Namespace) -> tuple[list[str], dict[str, str]]:
    if SHELL_CONTROL.search(args.build_command):
        raise ContractError("forbidden_command", args.build_command)
    try:
        words = shlex.split(args.build_command, posix=True)
    except ValueError as error:
        raise ContractError("malformed_command", args.build_command) from error
    environment = dict(os.environ)
    if words and words[0] == "QBOX_USE_SYSTEM_LIBQEMU=OFF":
        environment["QBOX_USE_SYSTEM_LIBQEMU"] = "OFF"
        words = words[1:]
    prefix = COMPONENT_ACTIONS.get(args.component)
    if prefix is None or tuple(words) != prefix:
        raise ContractError("forbidden_command", args.build_command)
    return words, environment


def execute(args: argparse.Namespace) -> None:
    argv, environment = command_argv(args)
    if args.dry_run:
        return
    process = subprocess.Popen(
        argv, cwd=args.cwd, env=environment, start_new_session=True,
    )
    try:
        return_code = process.wait(timeout=args.timeout)
    except subprocess.TimeoutExpired as error:
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        raise ContractError("build_timeout", args.component) from error
    if return_code != 0:
        raise ContractError("build_failed", args.component)


def owner_for(path: Path, sources: list[str]) -> str:
    resolved = path.resolve()
    matches = [
        source for source in sources
        if source != "." and resolved.is_relative_to(Path(source).resolve())
    ]
    if matches:
        return max(matches, key=len)
    text = str(path)
    mapping = (
        ("qbox-platform", "hsoc-stack/tools/qbox-platform"),
        ("trusted-firmware-a", "hsoc-stack/components/primary_compute/trusted-firmware-a"),
        ("trusted-firmware-m", "hsoc-stack/components/system_mgmt/trusted-firmware-m"),
        ("scp-firmware", "hsoc-stack/components/system_mgmt/scp-firmware"),
        ("zephyr", "hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src"),
        ("boot/", "hsoc-stack/tools/buildroot"),
    )
    for marker, owner in mapping:
        if marker in text:
            return owner
    return args_component_owner(sources)


def args_component_owner(sources: list[str]) -> str:
    nested = [source for source in sources if source != "."]
    if not nested:
        raise ContractError("unowned_runtime_input", "output")
    return nested[0]


def main() -> int:
    args = parse_args()
    try:
        sources = [item for item in args.source_repos.split(",") if item]
        if args.require_local_build_source_closure and not REQUIRED_OWNERS.issubset(sources):
            missing = sorted(REQUIRED_OWNERS - set(sources))
            raise ContractError("missing_source_owner", ",".join(missing))
        execute(args)
        source_records = [
            {"path": source, "head": git_head(args.cwd / source)}
            for source in sources
        ]
        output_paths = [args.cwd / item for item in args.require_outputs.split(",") if item]
        if any(not path.is_file() for path in output_paths):
            raise ContractError("missing_output", "fresh build output")
        outputs = [
            {
                "role": path.name, "path": str(path.resolve()),
                "sha256": sha_path(path), "owner": owner_for(path, sources),
            }
            for path in output_paths
        ]
        payload = {
            "format_version": 1, "verdict": "PASS", "reason": "fresh_build_closed",
            "component": args.component, "action": args.build_command,
            "sources": source_records, "outputs": outputs,
        }
        validate(payload, args.schema)
        code = 0
    except (ContractError, ValueError) as error:
        reason = error.reason if isinstance(error, ContractError) else "malformed_command"
        payload = {
            "format_version": 1, "verdict": "FAIL", "reason": reason,
            "component": args.component, "action": args.build_command,
            "sources": [], "outputs": [],
        }
        code = 1
    write_json(args.output, payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
