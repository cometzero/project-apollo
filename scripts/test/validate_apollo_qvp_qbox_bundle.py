#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import stat
import sys
from typing import Final


DEFAULT_REQUIRED_TARGETS: Final = tuple(
    "platforms-vp keep_alive addrtr router gs_memory host_scr loader "
    "char_backend_file char_backend_stdio uart-pl011 global_peripheral_initiator "
    "cpu_arm_cortexA720AE cpu_arm_cortexR82 arm_gicv3 arm_gicv3_its qemu_gpex "
    "virtio_mmio_blk virtio_mmio_net virtio_mmio_rng arm_smmuv3 mmu720ae reset_gpio "
    "pl031 sbsa_gwdt cpu_arm_cortexM55 nvic_armv7m ApolloRseCPU qemu_cc3xx "
    "qemu_arm_arch_timer_mmio qemu_hexagon_qtimer mhu320ae gicx00_multiview "
    "gic720ae_messreg zena_fmu zena_ssu host_cmn_cyprus host_gtimer "
    "host_ni710ae_nci host_ppu cc3xx dma350 rse_atu rse_integrity_checker "
    "rse_kmu rse_lcm rse_protection_ctrl rse_sam strata_flash_j3 host_smcf_mgi "
    "host_system_pll reset_fanout rse_sysctrl".split()
)
JsonScalar = str | int | float | bool | None
JsonValue = JsonScalar | list[str] | list["JsonValue"] | dict[str, "JsonValue"]
LD_ASSIGN_RE: Final = re.compile(r"^\s*(?:export\s+)?LD_LIBRARY_PATH=(?P<value>.+?)\s*$")


@dataclass(frozen=True, slots=True)
class MissingRequired:
    id: str
    path: str
    kind: str
    reason: str

    def to_json(self) -> dict[str, JsonValue]:
        return {"id": self.id, "path": self.path, "kind": self.kind, "reason": self.reason}


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    missing: tuple[MissingRequired, ...]
    details: dict[str, JsonValue]

    def to_json(self) -> dict[str, JsonValue]:
        status = "pass" if not self.missing else "fail"
        return {"name": self.name, "status": status, "details": self.details}


def missing_file(path: Path, item_id: str, kind: str, reason: str) -> MissingRequired | None:
    if path.is_file():
        return None
    return MissingRequired(item_id, path.as_posix(), kind, reason)


def read_manifest(bundle: Path) -> tuple[dict[str, JsonValue] | None, tuple[MissingRequired, ...]]:
    path = bundle / "qbox-apollo-qvp-manifest.json"
    if not path.exists():
        return None, ()
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return None, (MissingRequired("manifest:json", path.as_posix(), "manifest", f"invalid JSON: {error.msg}"),)
    if isinstance(loaded, dict):
        return loaded, ()
    return None, (MissingRequired("manifest:shape", path.as_posix(), "manifest", "manifest root must be a JSON object"),)


def string_list(value: JsonValue | None) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def targets_from_manifest(manifest: dict[str, JsonValue] | None) -> list[str]:
    if manifest is None:
        return list(DEFAULT_REQUIRED_TARGETS)
    targets = string_list(manifest.get("required_targets"))
    return targets if targets else list(DEFAULT_REQUIRED_TARGETS)


def check_executable(bundle: Path) -> Check:
    path = bundle / "platforms-vp"
    if path.is_file() and bool(path.stat().st_mode & stat.S_IXUSR):
        return Check("executable", (), {"path": "platforms-vp"})
    missing = MissingRequired("executable:platforms-vp", path.as_posix(), "executable", "missing or not executable")
    return Check("executable", (missing,), {"path": "platforms-vp"})


def compatibility_lua_path(manifest: dict[str, JsonValue] | None) -> str | None:
    if manifest is None:
        return None
    paths = manifest.get("compatibility_paths")
    if not isinstance(paths, dict):
        return None
    lua_path = paths.get("apollo_qvp_lua")
    return lua_path if isinstance(lua_path, str) else None


def check_lua_config(bundle: Path, manifest: dict[str, JsonValue] | None) -> Check:
    expected = Path("platforms/apollo/apollo-qvp.lua")
    if (bundle / expected).is_file():
        return Check("lua-config", (), {"path": expected.as_posix()})
    compat = compatibility_lua_path(manifest)
    if compat is not None and (bundle / compat).is_file():
        return Check("lua-config", (), {"expected_path": expected.as_posix(), "compatibility_path": compat})
    missing = MissingRequired(
        "lua:apollo-qvp",
        (bundle / expected).as_posix(),
        "lua-config",
        "missing apollo-qvp.lua or manifest-declared compatibility path",
    )
    return Check("lua-config", (missing,), {"path": expected.as_posix()})


def module_paths(target: str) -> tuple[Path, Path]:
    return Path("lib") / f"{target}.so", Path("lib") / f"lib{target}.so"


def check_shared_libraries(bundle: Path, targets: list[str]) -> tuple[Check, tuple[Path, ...]]:
    missing: list[MissingRequired] = []
    library_dirs: set[Path] = set()
    for relpath in (Path("lib/libqbox.so"), Path("lib/libqemu-system-aarch64.so")):
        found = missing_file(bundle / relpath, f"shared:{relpath.name}", "shared-library", "required shared library is missing")
        if found is None:
            library_dirs.add(relpath.parent)
        else:
            missing.append(found)
    for target in targets:
        if target == "platforms-vp":
            continue
        first, second = module_paths(target)
        found_path = next((relpath for relpath in (first, second) if (bundle / relpath).is_file()), None)
        if found_path is None:
            missing.append(MissingRequired(f"module:{target}", (bundle / first).as_posix(), "module", "required QBox module is missing"))
        else:
            library_dirs.add(found_path.parent)
    details: dict[str, JsonValue] = {
        "required_targets": targets,
        "required_library_dirs": sorted(path.as_posix() for path in library_dirs),
    }
    return Check("shared-libraries", tuple(missing), details), tuple(sorted(library_dirs))


def manifest_entries(manifest: dict[str, JsonValue] | None) -> list[dict[str, JsonValue]]:
    if manifest is None:
        return []
    entries = manifest.get("required_artifacts")
    if not isinstance(entries, list):
        return []
    return [entry for entry in entries if isinstance(entry, dict)]


def check_manifest(bundle: Path, manifest: dict[str, JsonValue] | None) -> Check:
    missing: list[MissingRequired] = []
    entries = manifest_entries(manifest)
    for index, entry in enumerate(entries):
        rel = entry.get("relative_path")
        if not isinstance(rel, str):
            missing.append(MissingRequired(f"manifest:required_artifacts:{index}", "qbox-apollo-qvp-manifest.json", "manifest", "required_artifacts entry is missing relative_path"))
            continue
        relpath = Path(rel)
        if relpath.is_absolute() or ".." in relpath.parts:
            missing.append(MissingRequired(f"manifest:required_artifacts:{index}", rel, "manifest", "relative_path must stay inside the bundle"))
            continue
        found = missing_file(bundle / relpath, f"manifest:required_artifacts:{rel}", "manifest-artifact", "manifest required artifact is missing")
        if found is not None:
            missing.append(found)
    return Check("manifest", tuple(missing), {"present": manifest is not None, "required_artifacts": len(entries)})


def ld_library_path_values(env_text: str) -> list[str]:
    values: list[str] = []
    for line in env_text.splitlines():
        match = LD_ASSIGN_RE.match(line)
        if match is not None:
            values.append(match.group("value"))
    return values


def ld_value_covers_dir(value: str, bundle: Path, rel_dir: Path) -> bool:
    rel = rel_dir.as_posix()
    markers = (
        f"${{QBOX_APOLLO_QVP_BUNDLE_DIR}}/{rel}",
        f"$QBOX_APOLLO_QVP_BUNDLE_DIR/{rel}",
        str(bundle / rel_dir),
        f"./{rel}",
        rel,
    )
    return any(marker in value for marker in markers)


def check_env(bundle: Path, library_dirs: tuple[Path, ...]) -> Check:
    path = bundle / "qbox-apollo-qvp-env.sh"
    if not path.is_file():
        missing = MissingRequired("env:file", path.as_posix(), "environment", "environment file is missing")
        return Check("environment", (missing,), {"path": "qbox-apollo-qvp-env.sh"})
    values = ld_library_path_values(path.read_text(encoding="utf-8"))
    missing = [
        MissingRequired(f"env:ld_library_path:{rel_dir.as_posix()}", path.as_posix(), "environment", f"LD_LIBRARY_PATH does not cover {rel_dir.as_posix()}")
        for rel_dir in library_dirs
        if not any(ld_value_covers_dir(value, bundle, rel_dir) for value in values)
    ]
    if not values:
        missing.append(MissingRequired("env:ld_library_path", path.as_posix(), "environment", "LD_LIBRARY_PATH is not set or exported"))
    details = {"path": "qbox-apollo-qvp-env.sh", "required_library_dirs": [path.as_posix() for path in library_dirs]}
    return Check("environment", tuple(missing), details)


def validate_bundle(bundle: Path) -> dict[str, JsonValue]:
    resolved = bundle.resolve()
    manifest, manifest_missing = read_manifest(resolved)
    shared_check, library_dirs = check_shared_libraries(resolved, targets_from_manifest(manifest))
    checks = (
        check_executable(resolved),
        check_lua_config(resolved, manifest),
        shared_check,
        check_manifest(resolved, manifest),
        check_env(resolved, library_dirs or (Path("lib"),)),
    )
    missing = [item for check in checks for item in check.missing]
    missing.extend(manifest_missing)
    return {
        "status": "pass" if not missing else "fail",
        "bundle": str(resolved),
        "missing_required": [item.to_json() for item in missing],
        "checks": [check.to_json() for check in checks],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an Apollo QVP Yocto QBox bundle.")
    parser.add_argument("--bundle", required=True, type=Path, help="qbox-apollo-qvp bundle directory")
    parser.add_argument("--output", required=True, type=Path, help="JSON report output path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    result = validate_bundle(args.bundle)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
