#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/capture_gic720ae_yocto_provenance.py --help
# 3. Or: python3 scripts/test/capture_gic720ae_yocto_provenance.py --help
# ──────────────────
"""Capture fresh BitBake outputs, layer heads, and taskhash identities."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shlex
import subprocess

from gic720ae_contract import (
    ContractError, JsonArray, json_object, sha_path, validate, write_json,
)


LAYER_RE = re.compile(r"^\s*(/[^\s\\\\]+)")
SHELL_CONTROL = re.compile(r"[;&|<>`$()\n\r]")
TASK27_CANONICAL_BUILD = (
    "(source layers/poky/oe-init-build-env build >/dev/null &&\n"
    "  MACHINE=apollo-qvp bitbake -c cleansstate linux-yocto-rt\n"
    "  nexios-bsp-initramfs); MACHINE=apollo-qvp ./yocto_build.sh --bsp"
)
TASK27_BUILD_STEPS = (
    ("bitbake", "-c", "cleansstate", "linux-yocto-rt", "nexios-bsp-initramfs"),
    ("./yocto_build.sh", "--bsp"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--producer-mode", choices=("bitbake_taskhash",), required=True)
    parser.add_argument("--build-command", required=True)
    parser.add_argument("--require-taskhash", required=True)
    parser.add_argument("--require-sstate-provenance", action="store_true")
    parser.add_argument("--compare-frozen-provenance", type=Path)
    parser.add_argument("--build-conf", type=Path, required=True)
    parser.add_argument("--bblayers", type=Path, required=True)
    parser.add_argument("--templateconf", type=Path, required=True)
    parser.add_argument("--expect-machine", required=True)
    parser.add_argument("--expect-tmpdir", required=True)
    parser.add_argument("--expect-variant", required=True)
    parser.add_argument("--expect-pc-cpus", required=True)
    parser.add_argument("--linux-source", type=Path, required=True)
    parser.add_argument("--yocto-repos", required=True)
    parser.add_argument("--require-all-bblayer-heads", action="store_true")
    parser.add_argument("--deploy-dir", type=Path, required=True)
    parser.add_argument("--require-outputs", required=True)
    parser.add_argument("--timeout", type=int, default=14400)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--self-test-metadata", type=Path)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def git_root_and_head(path: Path) -> tuple[str, str]:
    root = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        check=False, capture_output=True, text=True, timeout=30,
    )
    if root.returncode != 0:
        raise ContractError("unowned_layer", str(path))
    root_path = root.stdout.strip()
    head = subprocess.run(
        ["git", "-C", root_path, "rev-parse", "HEAD"],
        check=False, capture_output=True, text=True, timeout=30,
    )
    if head.returncode != 0:
        raise ContractError("unowned_layer", root_path)
    return root_path, head.stdout.strip()


def build_argv(args: argparse.Namespace) -> list[str]:
    if args.build_command == TASK27_CANONICAL_BUILD:
        return [TASK27_CANONICAL_BUILD]
    if SHELL_CONTROL.search(args.build_command):
        raise ContractError("forbidden_command", "build command")
    try:
        argv = shlex.split(args.build_command, posix=True)
    except ValueError as error:
        raise ContractError("malformed_command", "build command") from error
    requirements = [
        requirement.split(":", 1)
        for requirement in args.require_taskhash.split(",")
    ]
    allowed: set[tuple[str, ...]] = set()
    for recipe, task in requirements:
        action = task.removeprefix("do_")
        allowed.add(("bitbake", recipe, "-c", action))
        allowed.add(("bitbake", "-c", action, recipe))
    if tuple(argv) not in allowed:
        raise ContractError("forbidden_command", "build command")
    return argv


def task27_environment(args: argparse.Namespace) -> tuple[dict[str, str], Path]:
    workspace = args.build_conf.resolve().parents[2]
    fixed_setup = (
        "source layers/poky/oe-init-build-env build >/dev/null && "
        "env -0"
    )
    try:
        result = subprocess.run(
            ["bash", "-c", fixed_setup],
            cwd=workspace,
            check=False,
            capture_output=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ContractError("build_environment_failed", "oe-init-build-env") from error
    if result.returncode != 0:
        raise ContractError("build_environment_failed", "oe-init-build-env")
    environment = {
        key.decode(): value.decode()
        for entry in result.stdout.split(b"\0")
        if entry
        for key, value in [entry.split(b"=", 1)]
    }
    environment["MACHINE"] = args.expect_machine
    return environment, workspace


def execute(args: argparse.Namespace) -> None:
    argv = build_argv(args)
    if args.dry_run:
        return
    if argv == [TASK27_CANONICAL_BUILD]:
        environment, workspace = task27_environment(args)
        steps = TASK27_BUILD_STEPS
    else:
        environment = dict(os.environ)
        environment["MACHINE"] = args.expect_machine
        workspace = Path.cwd()
        steps = (tuple(argv),)
    for step in steps:
        try:
            result = subprocess.run(
                step, cwd=workspace, check=False, timeout=args.timeout,
                env=environment,
            )
        except subprocess.TimeoutExpired as error:
            raise ContractError("build_timeout", step[0]) from error
        if result.returncode != 0:
            raise ContractError("build_failed", step[0])


def bitbake_environment(
    recipe: str, cwd: Path, process_environment: dict[str, str],
) -> dict[str, str]:
    try:
        result = subprocess.run(
            ["bitbake", "-e", recipe], cwd=cwd, check=False,
            capture_output=True, text=True, timeout=120,
            env=process_environment,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ContractError("bitbake_metadata_unavailable", recipe) from error
    if result.returncode != 0:
        raise ContractError("bitbake_metadata_unavailable", recipe)
    values: dict[str, str] = {}
    for line in result.stdout.splitlines():
        match = re.fullmatch(r'([A-Z0-9_]+)="(.*)"', line)
        if match is not None:
            values[match.group(1)] = match.group(2)
    return values


def live_recipe(
    recipe: str, task: str, workspace: Path,
    process_environment: dict[str, str],
) -> dict[str, str]:
    environment = bitbake_environment(recipe, workspace, process_environment)
    origin = Path(environment.get("FILE", ""))
    stamp = environment.get("STAMP", "")
    sstate_dir = Path(environment.get("SSTATE_DIR", ""))
    if not origin.is_file() or not stamp or not sstate_dir.is_dir():
        raise ContractError("bitbake_metadata_unavailable", recipe)
    task_name = task if task.startswith("do_") else f"do_{task}"
    siginfos = sorted(Path(stamp).parent.glob(
        f"{Path(stamp).name}.{task_name}.sigdata.*"
    ))
    if not siginfos:
        raise ContractError("bitbake_metadata_unavailable", f"{recipe}:{task}")
    siginfo = siginfos[-1]
    taskhash = siginfo.name.rsplit(".sigdata.", 1)[-1]
    sstates = sorted(sstate_dir.glob(f"**/*{taskhash}*"))
    sstate = next((path for path in sstates if path.is_file()), None)
    if sstate is None:
        raise ContractError("bitbake_metadata_unavailable", f"sstate:{taskhash}")
    owner, _ = git_root_and_head(origin.parent)
    return {
        "name": f"{recipe}:{task}", "origin": str(origin.resolve()),
        "owner": owner, "taskhash": taskhash,
        "siginfo": f"{siginfo.resolve()}:{sha_path(siginfo)}",
        "sstate": f"{sstate.resolve()}:{sha_path(sstate)}",
    }


def fixture_recipes(path: Path) -> JsonArray:
    fixture = json_object(path)
    raw = fixture.get("recipes")
    if not isinstance(raw, list):
        raise ContractError("malformed_input", "fixture recipes")
    recipes: JsonArray = []
    for item in raw:
        if not isinstance(item, dict):
            raise ContractError("malformed_input", "fixture recipe")
        origin = Path(str(item.get("origin", "")))
        siginfo = Path(str(item.get("siginfo", "")))
        sstate = Path(str(item.get("sstate", "")))
        taskhash = str(item.get("taskhash", ""))
        if (
            not origin.is_file() or not siginfo.is_file() or not sstate.is_file()
            or taskhash not in siginfo.name or taskhash not in sstate.name
        ):
            raise ContractError("bitbake_metadata_unavailable", "fixture")
        owner, _ = git_root_and_head(origin.parent)
        recipes.append({
            "name": str(item.get("name")), "origin": str(origin.resolve()),
            "owner": owner, "taskhash": taskhash,
            "siginfo": f"{siginfo.resolve()}:{sha_path(siginfo)}",
            "sstate": f"{sstate.resolve()}:{sha_path(sstate)}",
        })
    return recipes


def main() -> int:
    args = parse_args()
    try:
        for path in (args.build_conf, args.bblayers, args.templateconf, args.linux_source):
            if not path.exists():
                raise ContractError("missing_input", str(path))
        execute(args)
        layer_paths = [
            Path(match.group(1))
            for line in args.bblayers.read_text().splitlines()
            if (match := LAYER_RE.match(line)) is not None
        ]
        roots = {git_root_and_head(path) for path in layer_paths}
        layers = [{"path": path, "head": head} for path, head in sorted(roots)]
        if args.self_test_metadata is not None:
            recipes = fixture_recipes(args.self_test_metadata)
        else:
            process_environment, workspace = task27_environment(args)
            recipes = [
                live_recipe(recipe, task, workspace, process_environment)
                for requirement in args.require_taskhash.split(",")
                for recipe, task in [requirement.split(":", 1)]
            ]
        outputs = [args.deploy_dir / name for name in args.require_outputs.split(",")]
        if any(not path.exists() for path in outputs):
            raise ContractError("missing_output", "Yocto deploy")
        payload = {
            "format_version": 1, "verdict": "PASS", "reason": "yocto_provenance_closed",
            "machine": args.expect_machine, "layers": layers, "recipes": recipes,
        }
        validate(payload, args.schema)
        code = 0
    except (ContractError, ValueError) as error:
        reason = error.reason if isinstance(error, ContractError) else "malformed_taskhash"
        payload = {
            "format_version": 1, "verdict": "FAIL", "reason": reason,
            "machine": "apollo-qvp", "layers": [], "recipes": [],
        }
        code = 1
    write_json(args.output, payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
