#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import shlex
import shutil
import sys
import time


DESCRIPTION = "Open a local Apollo build artifact with the configured GDB."


@dataclass(frozen=True)
class DebugComponent:
    name: str
    domain: str
    debugger: str
    elf: Path
    gdb_script: Path
    has_debug_info: bool = False
    remote: str | None = None
    gdb_thread: int | None = None
    mpidr: str | None = None


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
            remote=record.get("remote") if isinstance(record.get("remote"), str) else None,
            gdb_thread=(
                record.get("gdb_thread")
                if isinstance(record.get("gdb_thread"), int)
                else None
            ),
            mpidr=record.get("mpidr") if isinstance(record.get("mpidr"), str) else None,
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
    wait_log_marker: tuple[Path, str, float] | None = None,
    resume: bool = False,
) -> list[str]:
    command = [component.debugger, "-q"]
    if batch:
        command.append("--batch")
    command.extend(("-x", str(component.gdb_script)))
    for symbol in breakpoints:
        command.extend(("-ex", f"break {symbol}"))
    if wait_log_marker is not None:
        log, marker, timeout = wait_log_marker
        wait_command = shlex.join(
            (
                sys.executable,
                str(Path(__file__).resolve()),
                "--wait-log-marker-only",
                str(log),
                marker,
                "--wait-seconds",
                str(timeout),
            )
        )
        command.extend(("-ex", f"shell {wait_command}"))
    if remote is not None:
        command.extend(("-ex", f"target remote {remote}"))
        if component.gdb_thread is not None:
            command.extend(("-ex", f"thread {component.gdb_thread}"))
    if attach_pid is not None:
        command.extend(("-p", str(attach_pid)))
    if resume:
        command.extend(("-ex", "continue"))
    if program_args:
        command.extend(("--args", str(component.elf), *program_args))
    return command


def print_components(components: dict[str, DebugComponent]) -> None:
    for name, component in sorted(components.items()):
        state = "debug-info" if component.has_debug_info else "symbols-only"
        print(f"{name:40} {component.domain:18} {component.debugger:14} {state}")


def endpoint_port(endpoint: str) -> int:
    _, separator, value = endpoint.rpartition(":")
    if not separator:
        raise ValueError(f"invalid remote endpoint: {endpoint}")
    port = int(value)
    if not 0 < port < 65536:
        raise ValueError(f"invalid remote port: {port}")
    return port


def listening_ports() -> set[int]:
    ports: set[int] = set()
    for table in (Path("/proc/net/tcp"), Path("/proc/net/tcp6")):
        try:
            lines = table.read_text(encoding="ascii").splitlines()[1:]
        except OSError:
            continue
        for line in lines:
            fields = line.split()
            if len(fields) > 3 and fields[3] == "0A":
                ports.add(int(fields[1].rsplit(":", 1)[1], 16))
    return ports


def wait_for_remote(endpoint: str, *, timeout: float, interval: float = 0.2) -> bool:
    port = endpoint_port(endpoint)
    deadline = time.monotonic() + timeout
    while True:
        if port in listening_ports():
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(interval)


def wait_for_log_marker(
    log: Path, marker: str, *, timeout: float, interval: float = 0.05
) -> bool:
    deadline = time.monotonic() + timeout
    while True:
        try:
            contents = log.read_text(encoding="utf-8", errors="replace")
        except FileNotFoundError:
            contents = ""
        if marker in contents:
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(interval)


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=root / "build/local-apollo-qvp/debug/symbols.json",
    )
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--wait-remote-only", metavar="HOST:PORT")
    parser.add_argument(
        "--wait-log-marker-only",
        nargs=2,
        metavar=("LOG", "MARKER"),
    )
    parser.add_argument("component", nargs="?")
    connection = parser.add_mutually_exclusive_group()
    connection.add_argument("--attach", type=int, metavar="PID")
    connection.add_argument("--remote", metavar="HOST:PORT")
    parser.add_argument("--break", dest="breakpoints", action="append", default=[])
    parser.add_argument(
        "--wait-log-marker",
        nargs=2,
        metavar=("LOG", "MARKER"),
    )
    parser.add_argument("--batch", action="store_true")
    parser.add_argument("--wait-remote", action="store_true")
    parser.add_argument("--wait-seconds", type=float, default=600.0)
    parser.add_argument("--continue", dest="resume", action="store_true")
    parser.add_argument("--args", dest="program_args", nargs=argparse.REMAINDER)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.wait_log_marker_only is not None:
        log_value, marker = args.wait_log_marker_only
        log = Path(log_value).resolve()
        print(
            f"Waiting for GDB attach marker in {log}: {marker}",
            flush=True,
        )
        if not wait_for_log_marker(log, marker, timeout=args.wait_seconds):
            print(
                f"error: timed out waiting for marker in {log}",
                file=sys.stderr,
            )
            return 3
        print(f"GDB attach marker found in {log}")
        return 0
    if args.wait_remote_only is not None:
        try:
            ready = wait_for_remote(
                args.wait_remote_only, timeout=args.wait_seconds
            )
        except ValueError as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
        if not ready:
            print(
                f"error: timed out waiting for {args.wait_remote_only}",
                file=sys.stderr,
            )
            return 3
        print(f"GDB endpoint ready: {args.wait_remote_only}")
        return 0
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
    remote = args.remote or component.remote
    if args.wait_remote:
        if remote is None:
            print(
                "error: --wait-remote requires a remote endpoint",
                file=sys.stderr,
            )
            return 2
        if not wait_for_remote(remote, timeout=args.wait_seconds):
            print(f"error: timed out waiting for {remote}", file=sys.stderr)
            return 3
    if args.program_args and (args.attach is not None or remote is not None):
        print("error: --args cannot be combined with --attach or --remote", file=sys.stderr)
        return 2
    if shutil.which(component.debugger) is None:
        print(f"error: debugger not found: {component.debugger}", file=sys.stderr)
        return 2

    command = build_gdb_command(
        component,
        batch=args.batch,
        attach_pid=args.attach,
        remote=remote,
        breakpoints=tuple(args.breakpoints),
        program_args=tuple(args.program_args or ()),
        wait_log_marker=(
            (Path(args.wait_log_marker[0]).resolve(), args.wait_log_marker[1], args.wait_seconds)
            if args.wait_log_marker is not None
            else None
        ),
        resume=args.resume,
    )
    os.execvp(command[0], command)


if __name__ == "__main__":
    raise SystemExit(main())
