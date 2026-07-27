#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# ─── How to run ───
# Imported by run_agent_{fvp,qbox}_debug.py.

from __future__ import annotations

import atexit
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import time
PC_RE = re.compile(r"\bagent_debug_pc=(0x[0-9a-fA-F]+)\b")


class AgentDebugError(RuntimeError):
    """Report an invalid agent-debug input or runtime boundary."""


@dataclass(frozen=True, slots=True)
class DebugComponent:
    name: str
    debugger: str
    elf: Path
    gdb_script: Path


@dataclass(frozen=True, slots=True)
class Runner:
    process: subprocess.Popen[str]
    command: tuple[str, ...]
    log: Path


@dataclass(frozen=True, slots=True)
class CommandOutcome:
    returncode: int | None
    timed_out: bool


@dataclass(frozen=True, slots=True)
class Deadline:
    started: float
    timeout: float

    def remaining(self) -> float:
        return max(0.0, self.timeout - (time.monotonic() - self.started))

    def elapsed(self) -> float:
        return round(time.monotonic() - self.started, 3)


def load_component(manifest: Path, name: str) -> DebugComponent:
    try:
        decoded = json.loads(manifest.read_text(encoding="utf-8"))
        record = decoded["components"][name]
        debugger = record["debugger"]
        elf = Path(record["elf"]).resolve()
        gdb_script = Path(record["gdb_script"]).resolve()
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise AgentDebugError(
            f"debug manifest has no usable {name} record: {error}"
        ) from error
    if not isinstance(debugger, str) or not debugger:
        raise AgentDebugError(f"debug manifest {name}.debugger is invalid")
    for field, path in (("elf", elf), ("gdb_script", gdb_script)):
        if not path.is_file():
            raise AgentDebugError(f"debug manifest {name}.{field} is missing: {path}")
    return DebugComponent(name=name, debugger=debugger, elf=elf, gdb_script=gdb_script)


def runner_command(values: list[str]) -> tuple[str, ...]:
    command = values[1:] if values and values[0] == "--" else values
    if not command:
        raise AgentDebugError("runner command is required after --")
    return tuple(command)


def start_runner(command: tuple[str, ...], cwd: Path, log: Path) -> Runner:
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8", errors="replace") as stream:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=stream,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            text=True,
        )
    runner = Runner(process=process, command=command, log=log)
    atexit.register(terminate_runner, runner)
    return runner


def endpoint_parts(endpoint: str) -> tuple[str, int]:
    host, separator, raw_port = endpoint.rpartition(":")
    if not separator or not host:
        raise AgentDebugError(f"invalid debug endpoint: {endpoint}")
    try:
        port = int(raw_port)
    except ValueError as error:
        raise AgentDebugError(f"invalid debug endpoint: {endpoint}") from error
    if not 0 < port < 65536:
        raise AgentDebugError(f"invalid debug endpoint: {endpoint}")
    return host, port


def wait_for_port(endpoint: str, deadline: Deadline, runner: Runner) -> bool:
    host, port = endpoint_parts(endpoint)
    while deadline.remaining() > 0:
        if runner.process.poll() is not None:
            return False
        with socket.socket() as connection:
            connection.settimeout(min(0.2, deadline.remaining()))
            if connection.connect_ex((host, port)) == 0:
                return True
        time.sleep(0.05)
    return False


def wait_for_marker(
    log: Path,
    marker: str,
    deadline: Deadline,
    runner: Runner,
) -> bool:
    while deadline.remaining() > 0:
        if runner.process.poll() is not None:
            return False
        try:
            if marker in log.read_text(encoding="utf-8", errors="replace"):
                return True
        except FileNotFoundError:
            pass
        time.sleep(0.05)
    return False


def run_logged(
    command: list[str],
    cwd: Path,
    log: Path,
    timeout: float,
) -> CommandOutcome:
    log.parent.mkdir(parents=True, exist_ok=True)
    if timeout <= 0:
        return CommandOutcome(returncode=None, timed_out=True)
    with log.open("w", encoding="utf-8", errors="replace") as stream:
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                stdout=stream,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return CommandOutcome(returncode=None, timed_out=True)
    return CommandOutcome(returncode=completed.returncode, timed_out=False)


def observed_pc(log: Path) -> int | None:
    try:
        match = PC_RE.search(log.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return None
    return int(match.group(1), 16) if match else None


def pc_text(value: int | None) -> str | None:
    return hex(value) if value is not None else None


def pc_matches(expected: int, observed: int | None) -> bool:
    return observed is not None and (expected & ~1) == (observed & ~1)


def process_tree(root_pid: int) -> tuple[set[int], set[int]]:
    pending = [root_pid]
    pids: set[int] = set()
    groups: set[int] = set()
    while pending:
        pid = pending.pop()
        if pid in pids:
            continue
        pids.add(pid)
        try:
            groups.add(os.getpgid(pid))
            children = Path(f"/proc/{pid}/task/{pid}/children").read_text()
        except (OSError, ProcessLookupError):
            continue
        pending.extend(int(value) for value in children.split())
    return pids, groups


def signal_process_groups(groups: set[int], signum: signal.Signals) -> None:
    for group in groups:
        try:
            os.killpg(group, signum)
        except ProcessLookupError:
            pass


def terminate_runner(runner: Runner) -> bool:
    process = runner.process
    pids, groups = process_tree(process.pid)
    if process.poll() is None:
        signal_process_groups(groups, signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            signal_process_groups(groups, signal.SIGKILL)
            process.wait(timeout=5)
    signal_process_groups(groups, signal.SIGKILL)
    cleanup_deadline = time.monotonic() + 1
    while time.monotonic() < cleanup_deadline:
        if all(not Path(f"/proc/{pid}").exists() for pid in pids):
            break
        time.sleep(0.05)
    return process.poll() is not None and all(
        not Path(f"/proc/{pid}").exists() for pid in pids
    )


def wait_server(runner: Runner) -> bool:
    stop_requested = False

    def request_stop(_signum, _frame) -> None:
        nonlocal stop_requested
        stop_requested = True

    previous_term = signal.signal(signal.SIGTERM, request_stop)
    previous_int = signal.signal(signal.SIGINT, request_stop)
    try:
        while not stop_requested and runner.process.poll() is None:
            time.sleep(0.2)
    finally:
        signal.signal(signal.SIGTERM, previous_term)
        signal.signal(signal.SIGINT, previous_int)
    return terminate_runner(runner)
