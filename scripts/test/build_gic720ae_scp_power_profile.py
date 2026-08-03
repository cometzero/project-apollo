#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
ISOLATED_ROOT = ROOT / "build/gic720ae-scp-power-test"
REQUIRED_OWNERS = (
    ".", "hsoc-stack/components/system_mgmt/scp-firmware",
    "hsoc-stack/yocto/meta-hsoc-auto-solutions", "hsoc-stack/yocto/meta-hsoc-bsp",
    "layers/meta-arm", "layers/poky",
)
FORBIDDEN_DEFAULT = ("test-gic-power", "test gic_power", "FWK_MODULE_IDX_TEST_GIC_POWER")
DEFAULT_CONFIGURE_RECORD = ROOT / "scripts/build/modules/build_scp.sh"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force-clean-build", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--require-local-build-source-closure", action="store_true")
    parser.add_argument("--require-recipe-sysroot-taskhash", action="store_true")
    parser.add_argument("--platform", choices=("apollo-qvp",), required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--default-configure-record", type=Path)
    parser.add_argument("--profile-output", type=Path, required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head(path: Path) -> str:
    result = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], check=False, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise ValueError(f"unowned_source:{path}")
    return result.stdout.strip()


def write_output(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def default_counts(path: Path) -> dict[str, int]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return {token: text.count(token) for token in FORBIDDEN_DEFAULT}


def select_task_provenance(values: dict[str, str]) -> dict[str, str]:
    required = ("STAMP", "SSTATE_DIR", "PN", "PV", "PR", "SSTATE_PKGARCH", "SSTATE_VERSION")
    if any(not values.get(key) for key in required):
        raise ValueError("missing_recipe_sysroot_taskhash")
    stamp = Path(values["STAMP"])
    sstate = Path(values["SSTATE_DIR"])
    package_target = stamp.parent.parent.name
    package_arch = values["SSTATE_PKGARCH"]
    if values["PN"] != "scp-firmware" or package_target != f"{package_arch}-poky-linux" or package_arch != "apollo_qvp":
        raise ValueError("missing_recipe_sysroot_taskhash")
    marker_pattern = re.compile(
        rf"{re.escape(stamp.name)}\.do_prepare_recipe_sysroot\.([0-9a-f]{{64}})"
    )
    markers = [
        path for path in stamp.parent.glob(f"{stamp.name}.do_prepare_recipe_sysroot.*")
        if (match := marker_pattern.fullmatch(path.name)) is not None
    ]
    if len(markers) != 1 or not sstate.is_dir():
        raise ValueError("missing_recipe_sysroot_taskhash")
    taskhash = marker_pattern.fullmatch(markers[0].name).group(1)
    sigdata = Path(f"{stamp}.do_prepare_recipe_sysroot.sigdata.{taskhash}")
    if not sigdata.is_file():
        raise ValueError("missing_recipe_sysroot_taskhash")
    sstate_prefix = (
        f"sstate:scp-firmware:{package_target}:{values['PV']}:{values['PR']}:"
        f"{package_arch}:{values['SSTATE_VERSION']}:{taskhash}_prepare_recipe_sysroot"
    )
    suffix = re.compile(rf"{re.escape(sstate_prefix)}(?:\.tar\.[^.]+|\.tgz)\.siginfo")
    matches = [
        path for path in sstate.glob(f"*/*/{sstate_prefix}*.siginfo")
        if suffix.fullmatch(path.name) is not None
    ]
    if not matches:
        raise ValueError("missing_recipe_sysroot_taskhash")
    if len(matches) != 1:
        raise ValueError("ambiguous_recipe_sysroot_taskhash")
    return {
        "required_task": "scp-firmware:do_prepare_recipe_sysroot",
        "platform": "apollo-qvp",
        "machine": "apollo-qvp",
        "task_target": package_target,
        "taskhash": taskhash,
        "siginfo": f"{sigdata.resolve()}:{sha256(sigdata)}",
        "sstate": f"{matches[0].resolve()}:{sha256(matches[0])}",
    }


def task_provenance() -> dict[str, str]:
    command = ["bash", "-lc", "source layers/poky/oe-init-build-env build >/dev/null && MACHINE=apollo-qvp bitbake -e scp-firmware"]
    result = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True, timeout=180)
    if result.returncode != 0:
        raise ValueError("missing_recipe_sysroot_taskhash")
    values = {
        key: value.strip('"')
        for key, value in (
            line.split("=", 1)
            for line in result.stdout.splitlines()
            if line.startswith(("STAMP=", "SSTATE_DIR=", "PN=", "PV=", "PR=", "SSTATE_PKGARCH=", "SSTATE_VERSION="))
        )
    }
    return select_task_provenance(values)


def active_bblayer_heads() -> list[dict[str, str]]:
    records: dict[str, str] = {}
    for line in (ROOT / "build/conf/bblayers.conf").read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*(/\S+)", line)
        if match is not None:
            layer = Path(match.group(1))
            root = subprocess.run(["git", "-C", str(layer), "rev-parse", "--show-toplevel"], check=False, capture_output=True, text=True, timeout=30)
            if root.returncode != 0:
                raise ValueError(f"unowned_bblayer:{layer}")
            repository = Path(root.stdout.strip())
            records[str(repository)] = git_head(repository)
    if not records:
        raise ValueError("missing_active_bblayers")
    return [{"path": path, "head": head} for path, head in sorted(records.items())]


def main() -> int:
    args = parse_args()
    command = [f"LOCAL_BUILD_DIR={args.output_root}", "SCP_ENABLE_GIC_POWER_TEST=1", "./local_build.sh", "scp-firmware", "clean-build"]
    payload: dict[str, object] = {"format_version": 1, "verdict": "FAIL", "reason": "unknown", "command": command, "outputs": [], "default_exclusion": {}, "provenance": {}}
    try:
        output_root = args.output_root.resolve()
        allowed = output_root == ISOLATED_ROOT or (args.check_only and output_root.name == ISOLATED_ROOT.name)
        if not allowed:
            raise ValueError("nonisolated_output_root")
        if args.source.resolve() != (ROOT / "hsoc-stack/components/system_mgmt/scp-firmware").resolve():
            raise ValueError("source_closure_failed")
        default_record = args.default_configure_record or DEFAULT_CONFIGURE_RECORD
        if not default_record.is_file():
            raise ValueError("missing_default_configure_record")
        counts = default_counts(default_record)
        payload["default_exclusion"] = counts
        if any(counts.values()):
            raise ValueError("default_configuration_contaminated")
        if not args.check_only:
            environment = dict(os.environ, LOCAL_BUILD_DIR=str(output_root), SCP_ENABLE_GIC_POWER_TEST="1")
            result = subprocess.run(["./local_build.sh", "scp-firmware", "clean-build"], cwd=ROOT, env=environment, check=False, timeout=7200)
            if result.returncode != 0:
                raise ValueError("scp_power_build_failed")
        binary = output_root / "deploy/firmware/si0_ramfw.bin"
        elf = output_root / "work/scp-firmware/bin/apollo-qvp-si0-bl2.elf"
        if not binary.is_file() or not elf.is_file():
            raise ValueError("missing_output")
        provenance = {"owners": {owner: git_head(ROOT / owner) for owner in REQUIRED_OWNERS}, "active_bblayer_heads": active_bblayer_heads(), "default_configure_record": str(default_record.resolve())}
        provenance.update({"required_task": "scp-firmware:do_prepare_recipe_sysroot"})
        if args.require_recipe_sysroot_taskhash and not args.check_only:
            provenance.update(task_provenance())
        payload.update({"verdict": "PASS", "reason": "isolated_scp_power_profile_ready", "outputs": [{"role": "si0_ramfw.bin", "path": str(binary.resolve()), "sha256": sha256(binary)}, {"role": "apollo-qvp-si0-bl2.elf", "path": str(elf.resolve()), "sha256": sha256(elf)}], "provenance": provenance})
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        payload["reason"] = str(error).split(":", 1)[0]
    write_output(args.profile_output, payload)
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
