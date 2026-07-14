#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import subprocess
import sys


DESCRIPTION = "Open a local Apollo build artifact with the configured GDB."


@dataclass(frozen=True)
class DebugComponent:
    name: str
    domain: str
    debugger: str
    elf: Path
    gdb_script: Path
    has_debug_info: bool = False


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_components(manifest: Path) -> dict[str, DebugComponent]:
    decoded = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(decoded, dict):
        raise ValueError("manifest root must be an object")
    records = decoded.get("components")
    if not isinstance(records, dict):
        raise ValueError("manifest does not contain a components object")

    components: dict[str, DebugComponent] = {}
    for name, record in records.items():
        if not isinstance(name, str) or not isinstance(record, dict):
            raise ValueError("manifest contains an invalid component record")
        domain = record.get("domain")
        debugger = record.get("debugger")
        elf = record.get("elf")
        gdb_script = record.get("gdb_script")
        has_debug_info = record.get("has_debug_info", False)
        if (
            not isinstance(domain, str)
            or not isinstance(debugger, str)
            or not isinstance(elf, str)
            or not isinstance(gdb_script, str)
        ):
            raise ValueError(f"component {name} has incomplete GDB metadata")
        components[name] = DebugComponent(
            name=name,
            domain=domain,
            debugger=debugger,
            elf=Path(elf),
            gdb_script=Path(gdb_script),
            has_debug_info=has_debug_info is True,
        )
    return components


def build_gdb_command(
    component: DebugComponent,
    *,
    batch: bool = False,
    attach_pid: int | None = None,
    remote: str | None = None,
    breakpoints: tuple[str, ...] = (),
    program_args: tuple[str, ...] = (),
) -> list[str]:
    command = [component.debugger, "-q"]
    if batch:
        command.append("--batch")
    command.extend(("-x", str(component.gdb_script)))
    if remote is not None:
        command.extend(("-ex", f"target remote {remote}"))
    for symbol in breakpoints:
        command.extend(("-ex", f"break {symbol}"))
    if attach_pid is not None:
        command.extend(("-p", str(attach_pid)))
    if program_args:
        command.extend(("--args", str(component.elf), *program_args))
    return command


def print_components(components: dict[str, DebugComponent]) -> None:
    for name, component in sorted(components.items()):
        state = "debug-info" if component.has_debug_info else "symbols-only"
        print(f"{name:40} {component.domain:18} {component.debugger:14} {state}")


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=root / "build/local-apollo-qvp/debug/symbols.json",
    )
    parser.add_argument("--list", action="store_true")
    parser.add_argument("component", nargs="?")
    connection = parser.add_mutually_exclusive_group()
    connection.add_argument("--attach", type=int, metavar="PID")
    connection.add_argument("--remote", metavar="HOST:PORT")
    parser.add_argument("--break", dest="breakpoints", action="append", default=[])
    parser.add_argument("--batch", action="store_true")
    parser.add_argument("--args", dest="program_args", nargs=argparse.REMAINDER)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        components = load_components(args.manifest.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: cannot read debug manifest: {error}", file=sys.stderr)
        return 2

    if args.list:
        print_components(components)
        return 0
    if args.component is None:
        print("error: COMPONENT is required unless --list is used", file=sys.stderr)
        return 2
    component = components.get(args.component)
    if component is None:
        print(f"error: unknown component: {args.component}", file=sys.stderr)
        return 2
    if args.program_args and (args.attach is not None or args.remote is not None):
        print("error: --args cannot be combined with --attach or --remote", file=sys.stderr)
        return 2
    if shutil.which(component.debugger) is None:
        print(f"error: debugger not found: {component.debugger}", file=sys.stderr)
        return 2

    command = build_gdb_command(
        component,
        batch=args.batch,
        attach_pid=args.attach,
        remote=args.remote,
        breakpoints=tuple(args.breakpoints),
        program_args=tuple(args.program_args or ()),
    )
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
