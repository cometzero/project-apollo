#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat

import jsonschema


STABLE_ROLES = {
    "kernel": "Image",
    "dtb": "apollo-qvp.dtb",
    "wic": "nexios-bsp-initramfs-apollo-qvp.wic",
    "qboxconf": "nexios-bsp-initramfs-apollo-qvp.qboxconf",
    "si0": "si0_ramfw.bin",
    "si1": "zephyr-demos-cl1.bin",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_exclusion(root: Path) -> dict[str, bool]:
    manifest = root / "nexios-bsp-initramfs-apollo-qvp.manifest"
    package_text = manifest.read_text(encoding="utf-8") if manifest.exists() else ""
    paths = [path.relative_to(root).as_posix() for path in root.rglob("*")]
    return {
        "gic720ae-selftest": "gic720ae-selftest" not in package_text,
        "gic720ae_test.ko": not any("gic720ae_test.ko" in path for path in paths),
        "overlay": not any("gic720ae" in path for path in paths),
    }


def entry(path: Path, role: str, include_link_identity: bool) -> dict[str, object]:
    metadata = path.lstat()
    if path.is_symlink():
        resolved = path.resolve(strict=True)
        record: dict[str, object] = {
            "role": role,
            "kind": "symlink",
            "sha256": sha256(resolved),
            "mode": stat.S_IMODE(resolved.stat().st_mode),
        }
        if include_link_identity:
            record["link_text"] = os.readlink(path)
            record["resolved_realpath"] = str(resolved)
        return record
    if not path.is_file():
        raise ValueError(f"unsupported deploy entry: {path}")
    return {
        "role": role,
        "kind": "regular",
        "sha256": sha256(path),
        "mode": stat.S_IMODE(metadata.st_mode),
    }


def capture(root: Path, mode: str) -> dict[str, object]:
    if mode == "complete-instance":
        paths = sorted(
            path
            for path in root.rglob("*")
            if path.is_symlink() or path.is_file()
        )
        entries = [
            entry(path, path.relative_to(root).as_posix(), True)
            for path in paths
        ]
    else:
        entries = [
            entry(root / relative, role, False)
            for role, relative in STABLE_ROLES.items()
        ]
    exclusions = package_exclusion(root)
    if not all(exclusions.values()):
        raise ValueError("default deploy contains opt-in profile content")
    return {
        "format_version": 1,
        "mode": mode,
        "verdict": "PASS",
        "reason": "default_deploy_captured",
        "entries": entries,
        "package_exclusion": exclusions,
    }


def comparable(payload: dict[str, object]) -> tuple[object, object]:
    return payload.get("entries"), payload.get("package_exclusion")


def write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument(
        "--mode", choices=("complete-instance", "stable-contract"), required=True,
    )
    parser.add_argument("--compare", type=Path)
    parser.add_argument("--compare-stable-contract", type=Path)
    parser.add_argument("--stable-contract-output", type=Path)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    code = 0
    try:
        payload = capture(args.root.resolve(), args.mode)
        if args.compare is not None:
            baseline = json.loads(args.compare.read_text(encoding="utf-8"))
            if args.mode != "complete-instance" or comparable(payload) != comparable(baseline):
                payload["verdict"] = "FAIL"
                payload["reason"] = "default_deploy_contaminated"
                code = 1
        if args.compare_stable_contract is not None:
            baseline = json.loads(
                args.compare_stable_contract.read_text(encoding="utf-8")
            )
            if args.mode != "stable-contract" or comparable(payload) != comparable(baseline):
                payload["verdict"] = "FAIL"
                payload["reason"] = "default_deploy_contract_mismatch"
                code = 1
        if args.stable_contract_output is not None:
            stable = capture(args.root.resolve(), "stable-contract")
            jsonschema.validate(stable, json.loads(args.schema.read_text()))
            write(args.stable_contract_output, stable)
    except (OSError, ValueError, json.JSONDecodeError):
        payload = {
            "format_version": 1,
            "mode": args.mode,
            "verdict": "FAIL",
            "reason": "default_deploy_capture_failed",
            "entries": [],
            "package_exclusion": {
                "gic720ae-selftest": True,
                "gic720ae_test.ko": True,
                "overlay": True,
            },
        }
        code = 1
    jsonschema.validate(payload, json.loads(args.schema.read_text()))
    write(args.output, payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
