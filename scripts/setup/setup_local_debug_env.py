#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import TypedDict


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from local_debug_components import (  # noqa: E402
    COMPONENTS,
    HOST_COMPONENTS,
    Component,
    ComponentRecord,
    qbox_plugin_components,
)
from local_debug_support import (  # noqa: E402
    defined_symbols,
    elf_arch,
    elf_build_id,
    elf_sections,
    first_existing,
    install_build_id_debug_file,
    resolve_elf,
    shared_library_paths,
    write_gdb_script,
    write_readme,
)


DESCRIPTION = "Prepare GDB symbols and command files for local Apollo builds."


class DebugManifest(TypedDict):
    workspace: str
    local_build_dir: str
    out_dir: str
    iris_python: str
    components: dict[str, ComponentRecord]
    missing: list[str]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def clean_generated_files(out_dir: Path) -> None:
    for script in (out_dir / "gdb").glob("*.gdb"):
        script.unlink()
    for debug_file in (out_dir / ".build-id").glob("*/*.debug"):
        debug_file.unlink()


def select_symbols(component: Component, elf: Path) -> tuple[dict[str, int], dict[str, str]]:
    symbols = defined_symbols(elf)
    selected = {
        name: f"0x{symbols[name]:x}"
        for name in component.default_symbols
        if name in symbols
    }
    return symbols, selected


def component_record(
    component: Component,
    elf: Path,
    script_path: Path,
    selected: dict[str, str],
) -> ComponentRecord:
    sections = elf_sections(elf)
    return {
        "label": component.label,
        "domain": component.domain,
        "target": component.target,
        "elf": str(elf),
        "gdb_script": str(script_path),
        "debugger": component.debugger,
        "arch": elf_arch(elf),
        "has_symtab": sections["symtab"],
        "has_debug_info": sections["debug_info"],
        "has_debug_line": sections["debug_line"],
        "default_symbol": next(iter(selected), None),
        "symbols": selected,
    }


def add_libqemu_debug_file(
    root: Path,
    out_dir: Path,
    elf: Path,
    record: ComponentRecord,
) -> None:
    runtime = first_existing(
        root,
        (
            "build/tmp_baremetal/sysroots-components/x86_64/"
            "qbox-libqemu-native/usr/lib/libqemu-system-aarch64.so",
        ),
    )
    symbol_build_id = elf_build_id(elf)
    if symbol_build_id is not None:
        record["build_id"] = symbol_build_id
    if runtime is None or elf_build_id(runtime) != symbol_build_id:
        return
    installed = install_build_id_debug_file(out_dir, elf)
    if installed is None:
        return
    _, debug_file = installed
    record["runtime_elf"] = str(runtime)
    record["debug_file"] = str(debug_file)


def generate_manifest(root: Path, local_build: Path, out_dir: Path) -> DebugManifest:
    out_dir.mkdir(parents=True, exist_ok=True)
    clean_generated_files(out_dir)
    components: dict[str, ComponentRecord] = {}
    missing: list[str] = []
    specs = COMPONENTS + HOST_COMPONENTS + qbox_plugin_components(local_build)
    solib_paths = shared_library_paths(root, local_build)

    for component in specs:
        elf = resolve_elf(root, local_build, component)
        if elf is None:
            missing.append(component.name)
            continue
        symbols, selected = select_symbols(component, elf)
        script_path = out_dir / "gdb" / f"{component.name}.gdb"
        write_gdb_script(
            script_path,
            root,
            out_dir,
            component,
            elf,
            symbols,
            solib_paths,
        )
        record = component_record(component, elf, script_path, selected)
        if component.name == "libqemu-aarch64":
            add_libqemu_debug_file(root, out_dir, elf, record)
        components[component.name] = record

    return {
        "workspace": str(root),
        "local_build_dir": str(local_build),
        "out_dir": str(out_dir),
        "iris_python": str(
            root
            / "build/tmp_baremetal/sysroots-components/x86_64/"
            "fvp-rd-aspen-native/usr/lib/fvp/fvp-rd-aspen/Iris/Python"
        ),
        "components": components,
        "missing": missing,
    }


def main() -> int:
    root = workspace_root()
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "--local-build-dir",
        type=Path,
        default=root / "build/local-apollo-qvp",
    )
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args()

    local_build = args.local_build_dir.resolve()
    out_dir = (args.out_dir or local_build / "debug").resolve()
    manifest = generate_manifest(root, local_build, out_dir)
    manifest_path = out_dir / "symbols.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_readme(out_dir, manifest_path, manifest["components"])

    print(f"debug manifest: {manifest_path}")
    print(f"gdb scripts: {out_dir / 'gdb'}")
    if manifest["missing"]:
        print(
            "missing components: " + ", ".join(manifest["missing"]),
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
