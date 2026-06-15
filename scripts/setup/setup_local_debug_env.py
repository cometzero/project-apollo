#!/usr/bin/env python3
"""Prepare local Apollo FVP debug symbols and command files."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Iterable


@dataclass(frozen=True)
class Component:
    name: str
    label: str
    domain: str
    target: str
    elf_candidates: tuple[str, ...]
    default_symbols: tuple[str, ...]
    source_roots: tuple[str, ...]


AP_TARGET = "RD_ASD.css.app00.cluster.cpu0"
RSE_TARGET = "RD_ASD.css.smb.rseil.rse.cpu"
SI_CL0_TARGET = "RD_ASD.css.smb.si.cluster0.cpu0"
SI_CL1_TARGET = "RD_ASD.css.smb.si.cluster1.cpu0"

COMPONENTS = (
    Component(
        "tfm-bl1_1",
        "TF-M BL1_1",
        "rse",
        RSE_TARGET,
        ("work/trusted-firmware-m/bin/bl1_1.elf",),
        ("Reset_Handler", "_start", "main"),
        ("hsoc-stack/components/system_mgmt/trusted-firmware-m",),
    ),
    Component(
        "tfm-bl1_2",
        "TF-M BL1_2",
        "rse",
        RSE_TARGET,
        ("work/trusted-firmware-m/bin/bl1_2.elf",),
        ("Reset_Handler", "_start", "main"),
        ("hsoc-stack/components/system_mgmt/trusted-firmware-m",),
    ),
    Component(
        "tfm-bl2",
        "TF-M BL2",
        "rse",
        RSE_TARGET,
        ("work/trusted-firmware-m/bin/bl2.elf",),
        ("Reset_Handler", "_start", "main"),
        ("hsoc-stack/components/system_mgmt/trusted-firmware-m",),
    ),
    Component(
        "tfm-s",
        "TF-M secure runtime",
        "rse",
        RSE_TARGET,
        ("work/trusted-firmware-m/bin/tfm_s.elf",),
        ("tfm_core_init", "main", "Reset_Handler", "_start"),
        ("hsoc-stack/components/system_mgmt/trusted-firmware-m",),
    ),
    Component(
        "scp-si0",
        "SCP-firmware SI0 RAMFW",
        "safety_island_cl0",
        SI_CL0_TARGET,
        ("work/scp-firmware/bin/apollo-fvp-si0-bl2.elf",),
        ("arch_exception_reset", "platform_init_hook", "fwk_arch_init"),
        ("hsoc-stack/components/system_mgmt/scp-firmware",),
    ),
    Component(
        "si-cl1-zephyr",
        "Safety Island CL1 Zephyr demo",
        "safety_island_cl1",
        SI_CL1_TARGET,
        (
            "../tmp_baremetal/deploy/images/apollo-fvp/zephyr-demos-cl1.elf",
            "deploy/firmware/zephyr-demos-cl1.elf",
        ),
        ("z_cstart", "main"),
        ("hsoc-stack/components/system_mgmt/zephyrproject/safety_island",),
    ),
    Component(
        "tfa-bl2",
        "TF-A BL2",
        "tf_a",
        AP_TARGET,
        ("work/trusted-firmware-a/apollo_fvp/debug/bl2/bl2.elf",),
        ("bl2_main", "_start"),
        ("hsoc-stack/components/primary_compute/trusted-firmware-a",),
    ),
    Component(
        "tfa-bl31",
        "TF-A BL31",
        "tf_a",
        AP_TARGET,
        ("work/trusted-firmware-a/apollo_fvp/debug/bl31/bl31.elf",),
        ("bl31_main", "_start"),
        ("hsoc-stack/components/primary_compute/trusted-firmware-a",),
    ),
    Component(
        "optee-core",
        "OP-TEE core",
        "optee",
        AP_TARGET,
        ("work/optee-os/core/tee.elf",),
        ("_start", "generic_boot_init_primary", "init_primary_helper"),
        ("hsoc-stack/components/primary_compute/optee-os",),
    ),
    Component(
        "u-boot",
        "U-Boot",
        "u_boot_linux",
        AP_TARGET,
        ("work/u-boot/u-boot",),
        ("_start", "board_init_f", "main_loop"),
        ("hsoc-stack/components/primary_compute/u-boot",),
    ),
    Component(
        "linux",
        "Linux kernel",
        "u_boot_linux",
        AP_TARGET,
        ("work/linux/vmlinux",),
        ("start_kernel", "rest_init"),
        ("hsoc-stack/components/primary_compute/linux",),
    ),
    Component(
        "buildroot-busybox",
        "Buildroot BusyBox initramfs",
        "u_boot_linux",
        AP_TARGET,
        ("work/buildroot/build/busybox-*/busybox_unstripped",),
        ("main", "run_applet_no_and_exit"),
        ("hsoc-stack/components/primary_compute/buildroot",),
    ),
)


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def run_text(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, errors="replace")


def first_existing(root: Path, patterns: Iterable[str]) -> Path | None:
    for pattern in patterns:
        matches = sorted(root.glob(pattern))
        for match in matches:
            if match.is_file():
                return match.resolve()
    return None


def elf_sections(elf: Path) -> dict[str, bool]:
    try:
        out = run_text(["readelf", "-S", str(elf)])
    except (OSError, subprocess.CalledProcessError):
        return {"symtab": False, "debug_info": False, "debug_line": False}
    return {
        "symtab": ".symtab" in out,
        "debug_info": ".debug_info" in out,
        "debug_line": ".debug_line" in out,
    }


def elf_class(elf: Path) -> str:
    try:
        out = run_text(["file", str(elf)]).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    if "ELF 32-bit" in out and "ARM" in out:
        return "arm"
    if "ELF 64-bit" in out and "aarch64" in out:
        return "aarch64"
    return "unknown"


def defined_symbols(elf: Path) -> dict[str, int]:
    symbols: dict[str, int] = {}
    try:
        out = run_text(["nm", "-n", "--defined-only", str(elf)])
    except (OSError, subprocess.CalledProcessError):
        return symbols
    for line in out.splitlines():
        fields = line.split()
        if len(fields) < 3:
            continue
        addr, kind, name = fields[0], fields[1], fields[2]
        if kind.lower() not in {"t", "w"}:
            continue
        try:
            symbols.setdefault(name, int(addr, 16))
        except ValueError:
            continue
    return symbols


def quote(path: Path) -> str:
    return shlex.quote(str(path))


def write_gdb_script(
    out: Path,
    root: Path,
    component: Component,
    elf: Path,
    symbols: dict[str, int],
) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "set pagination off",
        "set confirm off",
        "set debuginfod enabled off",
        f"# {component.label}",
        f"# FVP Iris target: {component.target}",
    ]
    for source in component.source_roots:
        source_path = root / source
        if source_path.exists():
            lines.append(f"directory {source_path}")
    lines.extend(
        [
            f"file {elf}",
            "info files",
        ]
    )
    for name in component.default_symbols:
        if name in symbols:
            lines.append(f"info address {name}")
            lines.append(f"break {name}")
    lines.extend(
        [
            "",
            "# FVP_Zena_CSS_Cfg2 exposes Iris, not a GDB remote stub.",
            "# Use scripts/debug/local_debug_iris.py to set runtime breakpoints.",
        ]
    )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readme(out_dir: Path, manifest: Path, components: dict[str, dict]) -> None:
    component_lines = []
    for name, info in sorted(components.items()):
        symbols = ", ".join(info.get("symbols", {}).keys()) or "no default symbol"
        component_lines.append(
            f"- `{name}`: `{info['elf']}` target `{info['target']}` symbols {symbols}"
        )

    readme = f"""# Apollo FVP Local Debug Environment

Generated by `scripts/setup/setup_local_debug_env.py`.

This environment has two parts:

- GDB command files under `gdb/` load the unstripped ELF files so symbols,
  source paths, and breakpoint locations are visible in GDB.
- `scripts/debug/run_local_fvp_debug.sh` starts FVP with an Iris debug server.
  `scripts/debug/local_debug_iris.py` can connect to that server, set breakpoints
  from `{manifest.name}`, run the model, and stop when a breakpoint is hit.

FVP_Zena_CSS_Cfg2 does not expose a GDB remote stub. For live target control
use Iris or an Iris-capable debugger such as Arm Development Studio. GDB is
still useful here for symbol and source inspection.

## Start A Halted Debug Session

```bash
scripts/debug/run_local_fvp_debug.sh --no-attach --iris-port 7100
```

Attach an Iris-capable debugger to `localhost:7100`, or set and run a
breakpoint from the command line:

```bash
scripts/debug/local_debug_iris.py --port 7100 \\
  --manifest {manifest} \\
  --break tfm-bl1_1:Reset_Handler \\
  --run --timeout 60
```

## Inspect Symbols With GDB

```bash
gdb-multiarch -x {out_dir / "gdb/u-boot.gdb"}
gdb-multiarch -x {out_dir / "gdb/linux.gdb"}
```

## Components

{chr(10).join(component_lines)}
"""
    (out_dir / "README.md").write_text(readme, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    root = workspace_root()
    parser.add_argument(
        "--local-build-dir",
        type=Path,
        default=root / "build/local-apollo-fvp",
    )
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args()

    local_build = args.local_build_dir.resolve()
    out_dir = (args.out_dir or local_build / "debug").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    components: dict[str, dict] = {}
    missing: list[str] = []
    for component in COMPONENTS:
        elf = first_existing(local_build, component.elf_candidates)
        if elf is None:
            missing.append(component.name)
            continue
        symbols = defined_symbols(elf)
        selected = {
            name: f"0x{symbols[name]:x}"
            for name in component.default_symbols
            if name in symbols
        }
        sections = elf_sections(elf)
        script_path = out_dir / "gdb" / f"{component.name}.gdb"
        write_gdb_script(script_path, root, component, elf, symbols)
        components[component.name] = {
            "label": component.label,
            "domain": component.domain,
            "target": component.target,
            "elf": str(elf),
            "gdb_script": str(script_path),
            "arch": elf_class(elf),
            "has_symtab": sections["symtab"],
            "has_debug_info": sections["debug_info"],
            "has_debug_line": sections["debug_line"],
            "default_symbol": next(iter(selected), None),
            "symbols": selected,
        }

    manifest = {
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
    manifest_path = out_dir / "symbols.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    write_readme(out_dir, manifest_path, components)

    print(f"debug manifest: {manifest_path}")
    print(f"gdb scripts: {out_dir / 'gdb'}")
    if missing:
        print("missing components: " + ", ".join(missing), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
