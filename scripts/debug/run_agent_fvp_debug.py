#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# ─── How to run ───
# python3 scripts/debug/run_agent_fvp_debug.py --help

from __future__ import annotations

import argparse
from pathlib import Path
import shlex
import sys
import time

from agent_debug_common import (
    AgentDebugError,
    Deadline,
    load_component,
    observed_pc,
    run_logged,
    runner_command,
    start_runner,
    wait_for_port,
)
from agent_debug_result import (
    ResultWriter,
    finish_probe,
    serve_debugger,
    stop_before_debugger,
    stop_with_failure,
)


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a bounded headless FVP Iris/GDB probe or debug server."
    )
    parser.add_argument("--mode", choices=("probe", "server"), required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--component", required=True)
    parser.add_argument("--breakpoint", required=True)
    parser.add_argument("--expected-pc", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--iris-instance", required=True)
    parser.add_argument("--iris-port", type=int, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--cornea", type=Path, required=True)
    parser.add_argument(
        "--iris-helper",
        type=Path,
        default=ROOT / "scripts/debug/local_debug_iris.py",
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--runner-cwd", type=Path, default=ROOT)
    parser.add_argument("runner", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if not 0 < args.iris_port < 65536:
        parser.error("--iris-port must be in range 1..65535")
    if args.result is None:
        args.result = args.out_dir / "debug-result.json"
    return args


def iris_command(args: argparse.Namespace, timeout: float) -> list[str]:
    return [
        str(args.iris_helper),
        "--port",
        str(args.iris_port),
        "--manifest",
        str(args.manifest),
        "--break",
        f"{args.component}:{args.breakpoint}",
        "--run",
        "--timeout",
        str(timeout),
    ]


def gdb_command(
    debugger: str,
    gdb_script: Path,
    cornea: Path,
    iris_port: int,
    iris_instance: str,
) -> list[str]:
    proxy = shlex.join(
        (
            str(cornea),
            "--port",
            str(iris_port),
            "gdb-proxy",
            iris_instance,
        )
    )
    return [
        debugger,
        "-q",
        "--batch",
        "-x",
        str(gdb_script),
        "-ex",
        "set remote noack-packet off",
        "-ex",
        f"target remote | {proxy}",
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
        "disconnect",
    ]


def main() -> int:
    args = parse_args()
    args.out_dir = args.out_dir.resolve()
    args.result = args.result.resolve()
    args.runner_cwd = args.runner_cwd.resolve()
    args.manifest = args.manifest.resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    deadline = Deadline(started=time.monotonic(), timeout=args.timeout)
    runner_log = args.out_dir / "fvp_stdout.log"
    iris_log = args.out_dir / "iris-probe.log"
    prime_log = args.out_dir / "cornea-prime.log"
    gdb_log = args.out_dir / "gdb.log"
    try:
        command = runner_command(args.runner)
        component = load_component(args.manifest, args.component)
        active_runner = start_runner(command, args.runner_cwd, runner_log)
    except (AgentDebugError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    writer = ResultWriter(
        backend="fvp-iris",
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
    endpoint = f"127.0.0.1:{args.iris_port}"
    if not wait_for_port(endpoint, deadline, active_runner):
        return stop_before_debugger(
            writer,
            active_runner,
            message="Iris endpoint did not become ready",
        )

    if args.mode == "server":
        return serve_debugger(
            writer,
            active_runner,
            ready_message=f"Iris server ready at {endpoint}",
            stopped_message="Iris server stopped",
        )

    iris_outcome = run_logged(
        iris_command(args, deadline.remaining()),
        args.runner_cwd,
        iris_log,
        deadline.remaining(),
    )
    if iris_outcome.returncode != 0:
        return stop_with_failure(
            writer,
            active_runner,
            outcome=iris_outcome,
            debugger_log=iris_log,
            message="Iris breakpoint probe failed",
        )

    prime = run_logged(
        [
            str(args.cornea),
            "--port",
            str(args.iris_port),
            "register-read",
            args.iris_instance,
            "PC",
        ],
        args.runner_cwd,
        prime_log,
        deadline.remaining(),
    )
    if prime.returncode == 0:
        gdb_outcome = run_logged(
            gdb_command(
                component.debugger,
                component.gdb_script,
                args.cornea,
                args.iris_port,
                args.iris_instance,
            ),
            args.runner_cwd,
            gdb_log,
            deadline.remaining(),
        )
    else:
        gdb_outcome = prime
    observed = observed_pc(gdb_log)
    return finish_probe(
        writer,
        active_runner,
        outcome=gdb_outcome,
        observed=observed,
        debugger_log=gdb_log,
        passed_message="breakpoint snapshot captured",
        failed_message="FVP GDB probe failed",
    )


if __name__ == "__main__":
    raise SystemExit(main())
