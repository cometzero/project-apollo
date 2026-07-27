#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# ─── How to run ───
# Imported by run_agent_{fvp,qbox}_debug.py.

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
from typing import Literal

from agent_debug_common import (
    CommandOutcome,
    Deadline,
    Runner,
    pc_matches,
    pc_text,
    terminate_runner,
    wait_server,
)


DebugMode = Literal["probe", "server"]
DebugStatus = Literal["passed", "ready", "failed", "timeout"]


@dataclass(frozen=True, slots=True)
class DebugResult:
    schema_version: int
    backend: str
    mode: DebugMode
    status: DebugStatus
    passed: bool
    target: str
    component: str
    breakpoint: str
    expected_pc: str
    observed_pc: str | None
    breakpoint_hit: bool
    timed_out: bool
    debugger_returncode: int | None
    runner_returncode: int | None
    elapsed_seconds: float
    runner_log: str
    debugger_log: str | None
    runtime_out_dir: str
    cleanup_completed: bool
    runner_command: tuple[str, ...]
    message: str


@dataclass(frozen=True, slots=True)
class ResultWriter:
    backend: str
    mode: DebugMode
    target: str
    component: str
    breakpoint: str
    expected_pc: int
    out_dir: Path
    result_path: Path
    runner_log: Path
    command: tuple[str, ...]
    deadline: Deadline

    def write(
        self,
        *,
        status: DebugStatus,
        passed: bool,
        hit: bool,
        observed: int | None,
        timed_out: bool,
        debugger_returncode: int | None,
        runner_returncode: int | None,
        cleanup_completed: bool,
        debugger_log: Path | None,
        message: str,
    ) -> None:
        result = DebugResult(
            schema_version=1,
            backend=self.backend,
            mode=self.mode,
            status=status,
            passed=passed,
            target=self.target,
            component=self.component,
            breakpoint=self.breakpoint,
            expected_pc=hex(self.expected_pc),
            observed_pc=pc_text(observed),
            breakpoint_hit=hit,
            timed_out=timed_out,
            debugger_returncode=debugger_returncode,
            runner_returncode=runner_returncode,
            elapsed_seconds=self.deadline.elapsed(),
            runner_log=str(self.runner_log.resolve()),
            debugger_log=(
                str(debugger_log.resolve()) if debugger_log is not None else None
            ),
            runtime_out_dir=str(self.out_dir.resolve()),
            cleanup_completed=cleanup_completed,
            runner_command=self.command,
            message=message,
        )
        self.result_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.result_path.with_suffix(self.result_path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(asdict(result), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, self.result_path)


def stop_with_failure(
    writer: ResultWriter,
    runner: Runner,
    *,
    outcome: CommandOutcome,
    debugger_log: Path | None,
    message: str,
) -> int:
    cleanup = terminate_runner(runner)
    timed_out = outcome.timed_out or outcome.returncode == 2
    writer.write(
        status="timeout" if timed_out else "failed",
        passed=False,
        hit=False,
        observed=None,
        timed_out=timed_out,
        debugger_returncode=outcome.returncode,
        runner_returncode=runner.process.returncode,
        cleanup_completed=cleanup,
        debugger_log=debugger_log,
        message=message,
    )
    print(writer.result_path)
    return 3 if timed_out else 4


def stop_before_debugger(
    writer: ResultWriter,
    runner: Runner,
    *,
    message: str,
) -> int:
    timed_out = runner.process.poll() is None
    cleanup = terminate_runner(runner)
    writer.write(
        status="timeout" if timed_out else "failed",
        passed=False,
        hit=False,
        observed=None,
        timed_out=timed_out,
        debugger_returncode=None,
        runner_returncode=runner.process.returncode,
        cleanup_completed=cleanup,
        debugger_log=None,
        message=message,
    )
    print(writer.result_path)
    return 3 if timed_out else 4


def finish_probe(
    writer: ResultWriter,
    runner: Runner,
    *,
    outcome: CommandOutcome,
    observed: int | None,
    debugger_log: Path,
    passed_message: str,
    failed_message: str,
) -> int:
    hit = outcome.returncode == 0 and pc_matches(writer.expected_pc, observed)
    cleanup = terminate_runner(runner)
    passed = hit and not outcome.timed_out
    writer.write(
        status="passed" if passed else ("timeout" if outcome.timed_out else "failed"),
        passed=passed,
        hit=hit,
        observed=observed,
        timed_out=outcome.timed_out,
        debugger_returncode=outcome.returncode,
        runner_returncode=runner.process.returncode,
        cleanup_completed=cleanup,
        debugger_log=debugger_log,
        message=passed_message if passed else failed_message,
    )
    print(writer.result_path)
    return 0 if passed else (3 if outcome.timed_out else 4)


def serve_debugger(
    writer: ResultWriter,
    runner: Runner,
    *,
    ready_message: str,
    stopped_message: str,
) -> int:
    writer.write(
        status="ready",
        passed=True,
        hit=False,
        observed=None,
        timed_out=False,
        debugger_returncode=None,
        runner_returncode=None,
        cleanup_completed=False,
        debugger_log=None,
        message=ready_message,
    )
    print(writer.result_path, flush=True)
    cleanup = wait_server(runner)
    writer.write(
        status="ready",
        passed=True,
        hit=False,
        observed=None,
        timed_out=False,
        debugger_returncode=None,
        runner_returncode=runner.process.returncode,
        cleanup_completed=cleanup,
        debugger_log=None,
        message=stopped_message,
    )
    return 0
