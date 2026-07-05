#!/usr/bin/env python3

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import subprocess
import sys
from time import monotonic

from run_test_qbox_lane_defs import QboxInputs
from run_test_qbox_lanes import run_qbox_lanes


type JsonValue = (
    None | bool | int | float | str | Sequence[JsonValue] | Mapping[str, JsonValue]
)
type JsonObject = Mapping[str, JsonValue]


@dataclass(frozen=True, slots=True)
class Lane:
    name: str
    argv: list[str]
    command: list[str]
    cwd: Path
    stdout_log: Path
    stderr_log: Path
    env: dict[str, str]


@dataclass(frozen=True, slots=True)
class LaneInputs:
    root: Path
    run_dir: Path
    stamp: str
    commands_file: Path
    plan: Path | None
    dry_run: bool
    include_qbox_runtime: bool
    skip_runtime: bool
    timeout_fvp: str
    machine: str


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _rel(path: Path, base: Path) -> str:
    return os.path.relpath(path, base)


def _lane_paths(inputs: LaneInputs) -> tuple[Path, Path, Path]:
    static_dir = inputs.run_dir / "extra/static"
    project_dir = inputs.run_dir / "extra/project-pytest"
    sw_unit_dir = inputs.run_dir / "extra/sw-ref-stack/unittests"
    return static_dir, project_dir, sw_unit_dir


def build_lanes(inputs: LaneInputs) -> list[Lane]:
    static_dir, project_dir, sw_unit_dir = _lane_paths(inputs)
    sw_cwd = inputs.root / "sw-ref-stack/test_automation"
    sw_cache = _rel(sw_unit_dir / "cache", sw_cwd)
    sw_junit = _rel(sw_unit_dir / "junit.xml", sw_cwd)
    return [
        Lane(
            name="extra-static-compileall",
            argv=[
                f"PYTHONPYCACHEPREFIX={static_dir / 'pycache'}",
                "python3",
                "-m",
                "compileall",
                "scripts",
                "tests",
                "sw-ref-stack/test_automation",
            ],
            command=["python3", "-m", "compileall", "scripts", "tests", "sw-ref-stack/test_automation"],
            cwd=inputs.root,
            stdout_log=static_dir / "stdout.log",
            stderr_log=static_dir / "stderr.log",
            env={"PYTHONPYCACHEPREFIX": str(static_dir / "pycache")},
        ),
        Lane(
            name="extra-project-pytest",
            argv=[
                "pytest",
                "tests",
                "-o",
                f"cache_dir={project_dir / 'cache'}",
                "--junitxml",
                str(project_dir / "junit.xml"),
            ],
            command=[
                "pytest",
                "tests",
                "-o",
                f"cache_dir={project_dir / 'cache'}",
                "--junitxml",
                str(project_dir / "junit.xml"),
            ],
            cwd=inputs.root,
            stdout_log=project_dir / "stdout.log",
            stderr_log=project_dir / "stderr.log",
            env={},
        ),
        Lane(
            name="extra-sw-ref-stack-unittests",
            argv=[
                "cd",
                "sw-ref-stack/test_automation",
                "&&",
                "PYTHONDONTWRITEBYTECODE=1",
                "PYTHONPATH=.",
                "pytest",
                "unittests",
                "-o",
                f"cache_dir={sw_cache}",
                "--junitxml",
                sw_junit,
            ],
            command=["pytest", "unittests", "-o", f"cache_dir={sw_cache}", "--junitxml", sw_junit],
            cwd=sw_cwd,
            stdout_log=sw_unit_dir / "stdout.log",
            stderr_log=sw_unit_dir / "stderr.log",
            env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": "."},
        ),
    ]


def _append(commands_file: Path, record: JsonObject) -> None:
    commands_file.parent.mkdir(parents=True, exist_ok=True)
    with commands_file.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")


def _included_extra(plan: Path | None) -> set[str] | None:
    if plan is None:
        return None
    data = json.loads(plan.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return set()
    included = data.get("included", {})
    if not isinstance(included, dict):
        return set()
    extra = included.get("extra", [])
    if not isinstance(extra, list):
        return set()
    return {item for item in extra if isinstance(item, str)}


def _selected_local_lanes(inputs: LaneInputs) -> list[Lane]:
    lanes = build_lanes(inputs)
    included = _included_extra(inputs.plan)
    if included is None:
        return lanes
    return [lane for lane in lanes if lane.name in included]


def _record_dry_run(inputs: LaneInputs, lane: Lane) -> None:
    now = _now()
    _append(
        inputs.commands_file,
        {
            "name": lane.name,
            "argv": lane.argv,
            "required": True,
            "status": "skipped",
            "started_at": now,
            "finished_at": now,
            "duration_s": 0.0,
        },
    )


def _run_lane(inputs: LaneInputs, lane: Lane) -> int:
    lane.stdout_log.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(lane.env)
    started_at = _now()
    started = monotonic()
    with lane.stdout_log.open("w", encoding="utf-8") as stdout:
        with lane.stderr_log.open("w", encoding="utf-8") as stderr:
            try:
                result = subprocess.run(
                    lane.command,
                    cwd=lane.cwd,
                    env=env,
                    check=False,
                    text=True,
                    stdout=stdout,
                    stderr=stderr,
                )
                returncode = result.returncode
            except OSError as exc:
                stderr.write(f"{exc}\n")
                returncode = 127
    finished_at = _now()
    duration = round(monotonic() - started, 6)
    status = "pass" if returncode == 0 else "fail"
    _append(
        inputs.commands_file,
        {
            "name": lane.name,
            "argv": lane.argv,
            "required": True,
            "status": status,
            "exit_code": returncode,
            "started_at": started_at,
            "finished_at": finished_at,
            "duration_s": duration,
            "stdout_log": _rel(lane.stdout_log, inputs.run_dir),
            "stderr_log": _rel(lane.stderr_log, inputs.run_dir),
        },
    )
    return returncode


def run_lanes(inputs: LaneInputs) -> int:
    failed = False
    for lane in _selected_local_lanes(inputs):
        if inputs.dry_run:
            _record_dry_run(inputs, lane)
            continue
        failed = _run_lane(inputs, lane) != 0 or failed
    qbox_rc = run_qbox_lanes(
        QboxInputs(
            root=inputs.root,
            run_dir=inputs.run_dir,
            commands_file=inputs.commands_file,
            dry_run=inputs.dry_run,
            include_runtime=inputs.include_qbox_runtime,
            skip_runtime=inputs.skip_runtime,
            timeout_fvp=inputs.timeout_fvp,
            machine=inputs.machine,
        )
    )
    if qbox_rc == 2 and not failed:
        return 2
    return 1 if failed or qbox_rc else 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run cheap extra validation lanes.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--stamp", required=True)
    parser.add_argument("--commands-file", type=Path, required=True)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--include-qbox-runtime", action="store_true")
    parser.add_argument("--skip-runtime", action="store_true")
    parser.add_argument("--timeout-fvp", default="600")
    parser.add_argument(
        "--machine",
        default="apollo-fvp",
        choices=("apollo-fvp", "apollo-qvp"),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    include_qbox_runtime = args.include_qbox_runtime or os.environ.get("INCLUDE_QBOX_RUNTIME") == "1"
    return run_lanes(
        LaneInputs(
            root=Path.cwd(),
            run_dir=args.run_dir,
            stamp=args.stamp,
            commands_file=args.commands_file,
            plan=args.plan,
            dry_run=args.dry_run,
            include_qbox_runtime=include_qbox_runtime,
            skip_runtime=args.skip_runtime,
            timeout_fvp=args.timeout_fvp,
            machine=args.machine,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
