#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import subprocess
from time import monotonic

from run_test_qbox_lane_defs import (
    QboxInputs,
    QboxLane,
    ctest_lanes,
    qbox_build_arg,
    qbox_build_dir,
    runtime_lanes,
    static_lanes,
)


type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]


@dataclass(frozen=True, slots=True)
class LaneResult:
    failed: bool
    blocked: bool
    blockers: tuple[JsonObject, ...]


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _rel(path: Path, base: Path) -> str:
    return os.path.relpath(path, base)


def _append(commands_file: Path, record: JsonObject) -> None:
    commands_file.parent.mkdir(parents=True, exist_ok=True)
    with commands_file.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")


def _artifact(lane: QboxLane, inputs: QboxInputs) -> list[JsonObject]:
    if lane.artifact_path is None:
        return []
    return [{"kind": "path", "path": _rel(lane.artifact_path, inputs.run_dir)}]


def _read_json(path: Path) -> JsonObject:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _result_path(lane: QboxLane) -> Path | None:
    if lane.artifact_path is None:
        return None
    if lane.artifact_path.name == "result.json":
        return lane.artifact_path
    return lane.artifact_path / "result.json"


def _result_blockers(lane: QboxLane) -> tuple[JsonObject, ...]:
    result_path = _result_path(lane)
    if result_path is None:
        return ()
    result = _read_json(result_path)
    blocker = result.get("blocker")
    if isinstance(blocker, str) and blocker:
        return ({"reason": blocker},)
    if isinstance(blocker, dict) and isinstance(blocker.get("reason"), str) and blocker.get("reason"):
        return (blocker,)
    return ()


def _record_dry_run(inputs: QboxInputs, lane: QboxLane) -> None:
    now = _now()
    _append(
        inputs.commands_file,
        {
            "name": lane.name,
            "argv": lane.argv,
            "required": lane.required,
            "status": "skipped",
            "started_at": now,
            "finished_at": now,
            "duration_s": 0.0,
            "artifacts": _artifact(lane, inputs),
        },
    )


def _run_lane(inputs: QboxInputs, lane: QboxLane) -> LaneResult:
    lane.stdout_log.parent.mkdir(parents=True, exist_ok=True)
    lane.stderr_log.parent.mkdir(parents=True, exist_ok=True)
    started_at = _now()
    started = monotonic()
    with lane.stdout_log.open("w", encoding="utf-8") as stdout:
        with lane.stderr_log.open("w", encoding="utf-8") as stderr:
            try:
                result = subprocess.run(
                    lane.command,
                    cwd=lane.cwd,
                    check=False,
                    text=True,
                    stdout=stdout,
                    stderr=stderr,
                )
                returncode = result.returncode
            except OSError as exc:
                stderr.write(f"{exc}\n")
                returncode = 127
    blockers = _result_blockers(lane)
    if blockers:
        status = "blocked"
    else:
        status = "pass" if returncode == 0 else "fail"
    record: JsonObject = {
        "name": lane.name,
        "argv": lane.argv,
        "required": lane.required,
        "status": status,
        "started_at": started_at,
        "finished_at": _now(),
        "duration_s": round(monotonic() - started, 6),
        "stdout_log": _rel(lane.stdout_log, inputs.run_dir),
        "stderr_log": _rel(lane.stderr_log, inputs.run_dir),
        "artifacts": _artifact(lane, inputs),
    }
    if blockers:
        record["blockers"] = list(blockers)
    else:
        record["exit_code"] = returncode
    _append(inputs.commands_file, record)
    return LaneResult(status == "fail", status == "blocked", blockers)


def _record_missing_build(inputs: QboxInputs, name: str, required: bool) -> None:
    now = _now()
    record: JsonObject = {
        "name": name,
        "argv": ["ctest", "--test-dir", qbox_build_arg()],
        "required": required,
        "status": "blocked" if required else "skipped",
        "started_at": now,
        "finished_at": now,
        "duration_s": 0.0,
        "reason": "blocked_missing_qbox_build" if required else "skipped_optional_missing_qbox_build",
    }
    if required:
        record["blockers"] = [{"reason": "blocked_missing_qbox_build", "path": str(qbox_build_dir(inputs))}]
    _append(inputs.commands_file, record)


def _record_gated_runtime(inputs: QboxInputs, lane: QboxLane, check: LaneResult) -> None:
    now = _now()
    blocked = check.blocked
    reason = "blocked_qbox_check_only_preflight" if blocked else "skipped_failed_qbox_check_only"
    record: JsonObject = {
        "name": lane.name,
        "argv": lane.argv,
        "required": lane.required,
        "status": "blocked" if blocked else "skipped",
        "started_at": now,
        "finished_at": now,
        "duration_s": 0.0,
        "reason": reason,
        "artifacts": _artifact(lane, inputs),
    }
    if blocked:
        record["blockers"] = [{"reason": reason}, *check.blockers]
    _append(inputs.commands_file, record)


def _record_skipped_runtime(inputs: QboxInputs, lane: QboxLane) -> None:
    now = _now()
    _append(
        inputs.commands_file,
        {
            "name": lane.name,
            "argv": lane.argv,
            "required": False,
            "status": "skipped",
            "started_at": now,
            "finished_at": now,
            "duration_s": 0.0,
            "reason": "skipped_runtime_requested",
            "artifacts": _artifact(lane, inputs),
        },
    )


def _run_each(inputs: QboxInputs, lanes: list[QboxLane]) -> LaneResult:
    failed = False
    blocked = False
    blockers: list[JsonObject] = []
    for lane in lanes:
        if inputs.dry_run:
            _record_dry_run(inputs, lane)
            continue
        result = _run_lane(inputs, lane)
        failed = result.failed or failed
        blocked = result.blocked or blocked
        blockers.extend(result.blockers)
    return LaneResult(failed, blocked, tuple(blockers))


def _run_runtime(inputs: QboxInputs, lanes: list[QboxLane]) -> LaneResult:
    if inputs.skip_runtime:
        for lane in lanes:
            _record_skipped_runtime(inputs, lane)
        return LaneResult(False, False, ())
    if inputs.dry_run or not lanes:
        return _run_each(inputs, lanes)
    check = _run_lane(inputs, lanes[0])
    if check.failed or check.blocked:
        for lane in lanes[1:]:
            _record_gated_runtime(inputs, lane, check)
        return check
    return _run_each(inputs, lanes[1:])


def run_qbox_lanes(inputs: QboxInputs) -> int:
    static_result = _run_each(inputs, static_lanes(inputs))
    if not qbox_build_dir(inputs).is_dir():
        _record_missing_build(inputs, "qbox-ctest", False)
        _record_missing_build(inputs, "qbox-full-runtime", inputs.include_runtime)
        return 2 if inputs.include_runtime else (1 if static_result.failed else 0)
    ctest_result = _run_each(inputs, ctest_lanes(inputs))
    runtime_result = _run_runtime(inputs, runtime_lanes(inputs))
    if static_result.failed or ctest_result.failed or runtime_result.failed:
        return 1
    if static_result.blocked or ctest_result.blocked or runtime_result.blocked:
        return 2
    return 0
