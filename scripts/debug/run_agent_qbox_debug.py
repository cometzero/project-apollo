#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# ─── How to run ───
# python3 scripts/debug/run_agent_qbox_debug.py --help

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
import time

from agent_debug_common import (
    AgentDebugError,
    CommandOutcome,
    Deadline,
    Runner,
    endpoint_parts,
    load_component,
    observed_pc,
    run_logged,
    runner_command,
    start_runner,
    wait_for_marker,
)
from agent_debug_result import (
    ResultWriter,
    finish_probe,
    serve_debugger,
    stop_before_debugger,
    stop_with_failure,
)

QBOX_ENTRY_RE = re.compile(
    r"QBox GDB entry breakpoint reached:\s*(0x[0-9a-fA-F]+)"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a bounded headless QBox GDB probe or debug server."
    )
    parser.add_argument("--mode", choices=("probe", "server"), required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--component", required=True)
    parser.add_argument("--breakpoint", required=True)
    parser.add_argument("--expected-pc", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--wait-log", type=Path)
    parser.add_argument("--wait-marker")
    parser.add_argument("--runner-cwd", type=Path, default=Path.cwd())
    parser.add_argument("runner", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if (args.wait_log is None) != (args.wait_marker is None):
        parser.error("--wait-log and --wait-marker must be used together")
    if args.result is None:
        args.result = args.out_dir / "debug-result.json"
    return args


def gdb_command(
    debugger: str,
    gdb_script: Path,
    endpoint: str,
    *,
    resume: bool,
) -> list[str]:
    command = [
        debugger,
        "-q",
        "--batch",
        "-x",
        str(gdb_script),
        "-ex",
        f"target remote {endpoint}",
    ]
    if resume:
        command.extend(("-ex", "continue"))
    command.extend(
        (
            "-ex",
            'printf "agent_debug_pc=0x%lx\\n", (unsigned long)$pc',
            "-ex",
            "info threads",
            "-ex",
            "thread apply all bt 12",
            "-ex",
            "info registers",
            "-ex",
            "x/8i $pc",
            "-ex",
            "info line *$pc",
            "-ex",
            "detach",
        )
    )
    return command


def gdb_symbol_command(
    debugger: str,
    gdb_script: Path,
    pc: int,
) -> list[str]:
    address = hex(pc)
    return [
        debugger,
        "-q",
        "--batch",
        "-x",
        str(gdb_script),
        "-ex",
        f'printf "agent_debug_pc=0x%lx\\n", (unsigned long){address}',
        "-ex",
        f"info symbol {address}",
        "-ex",
        f"info line *{address}",
        "-ex",
        f"list *{address}",
        "-ex",
        f"x/8i {address}",
    ]


def entry_marker_pc(log: Path) -> int | None:
    try:
        matches = QBOX_ENTRY_RE.findall(
            log.read_text(encoding="utf-8", errors="replace")
        )
    except OSError:
        return None
    return int(matches[-1], 16) if matches else None


def retryable_connection_failure(log: Path) -> bool:
    try:
        output = log.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return any(
        marker in output
        for marker in (
            "Connection refused",
            "Connection timed out",
            "No route to host",
        )
    )


def run_probe_gdb(
    command: list[str],
    cwd: Path,
    log: Path,
    deadline: Deadline,
    runner: Runner,
) -> CommandOutcome:
    while deadline.remaining() > 0:
        outcome = run_logged(command, cwd, log, deadline.remaining())
        if outcome.timed_out or outcome.returncode == 0:
            return outcome
        if runner.process.poll() is not None or not retryable_connection_failure(log):
            return outcome
        time.sleep(min(0.05, deadline.remaining()))
    return CommandOutcome(returncode=None, timed_out=True)


def wait_for_listening_endpoint(
    endpoint: str,
    deadline: Deadline,
    runner: Runner,
) -> bool:
    _host, port = endpoint_parts(endpoint)
    encoded_port = f"{port:04X}"
    while deadline.remaining() > 0:
        if runner.process.poll() is not None:
            return False
        for table in (Path("/proc/net/tcp"), Path("/proc/net/tcp6")):
            try:
                rows = table.read_text(encoding="ascii").splitlines()[1:]
            except OSError:
                continue
            for row in rows:
                fields = row.split()
                listening = (
                    len(fields) > 3
                    and fields[1].endswith(f":{encoded_port}")
                    and fields[3] == "0A"
                )
                if listening:
                    return True
        time.sleep(0.05)
    return False


def main() -> int:
    args = parse_args()
    args.out_dir = args.out_dir.resolve()
    args.result = args.result.resolve()
    args.runner_cwd = args.runner_cwd.resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    deadline = Deadline(started=time.monotonic(), timeout=args.timeout)
    runner_log = args.out_dir / "agent-runner.log"
    gdb_log = args.out_dir / "gdb.log"
    try:
        command = runner_command(args.runner)
        component = load_component(args.manifest.resolve(), args.component)
        if args.wait_log is not None:
            args.wait_log = args.wait_log.resolve()
            args.wait_log.parent.mkdir(parents=True, exist_ok=True)
            args.wait_log.write_text("", encoding="utf-8")
        active_runner = start_runner(command, args.runner_cwd, runner_log)
    except (AgentDebugError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    writer = ResultWriter(
        backend="qbox-gdb",
        mode=args.mode,
        target=args.target,
        component=args.component,
        breakpoint=args.breakpoint,
        expected_pc=args.expected_pc,
        out_dir=args.out_dir,
        result_path=args.result,
        runner_log=runner_log,
        command=command,
        deadline=deadline,
    )
    if args.mode == "server":
        endpoint_ready = (
            wait_for_marker(
                args.wait_log,
                args.wait_marker,
                deadline,
                active_runner,
            )
            if args.wait_log is not None
            else wait_for_listening_endpoint(args.endpoint, deadline, active_runner)
        )
        if not endpoint_ready:
            return stop_before_debugger(
                writer,
                active_runner,
                message="debug server marker did not become ready",
            )
        return serve_debugger(
            writer,
            active_runner,
            ready_message=f"debug server ready at {args.endpoint}",
            stopped_message="debug server stopped",
        )

    if args.wait_log is not None and not wait_for_marker(
        args.wait_log,
        args.wait_marker,
        deadline,
        active_runner,
    ):
        return stop_before_debugger(
            writer,
            active_runner,
            message="entry breakpoint marker did not become ready",
        )

    if args.wait_log is not None:
        observed = entry_marker_pc(args.wait_log)
        if observed is None:
            return stop_with_failure(
                writer,
                active_runner,
                outcome=CommandOutcome(returncode=1, timed_out=False),
                debugger_log=None,
                message="entry marker did not contain a guest PC",
            )
        outcome = run_logged(
            gdb_symbol_command(
                component.debugger,
                component.gdb_script,
                observed,
            ),
            args.runner_cwd,
            gdb_log,
            deadline.remaining(),
        )
    else:
        outcome = run_probe_gdb(
            gdb_command(
                component.debugger,
                component.gdb_script,
                args.endpoint,
                resume=True,
            ),
            args.runner_cwd,
            gdb_log,
            deadline,
            active_runner,
        )
        observed = observed_pc(gdb_log)
    if active_runner.process.poll() is not None:
        return stop_with_failure(
            writer,
            active_runner,
            outcome=outcome,
            debugger_log=gdb_log,
            message="QBox runner exited before the GDB probe completed",
        )
    return finish_probe(
        writer,
        active_runner,
        outcome=outcome,
        observed=observed,
        debugger_log=gdb_log,
        passed_message=(
            "entry event and ELF symbols captured"
            if args.wait_log is not None
            else "breakpoint snapshot captured"
        ),
        failed_message="GDB probe failed",
    )


if __name__ == "__main__":
    raise SystemExit(main())
