from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
import json
from pathlib import Path
from typing import Final, assert_never

from run_test_oeqa_result import OeqaResultState, classify_oeqa_result_path


type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]

EXIT_FAIL: Final = 1
EXIT_BLOCKED: Final = 2


class StepState(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True, slots=True)
class CommandInputs:
    run_dir: Path
    record: JsonObject
    index: int


@dataclass(frozen=True, slots=True)
class StepResult:
    step: JsonObject
    blockers: list[JsonObject]
    artifacts: list[JsonObject]
    failed: bool
    blocked: bool


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _json_object(value: JsonValue) -> JsonObject:
    return value if isinstance(value, dict) else {}


def _json_objects(value: JsonValue) -> list[JsonObject]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _str_value(value: JsonValue) -> str:
    return value if isinstance(value, str) else ""


def _bool_value(value: JsonValue, default: bool) -> bool:
    return value if isinstance(value, bool) else default


def _int_value(value: JsonValue) -> int | None:
    if isinstance(value, int):
        return value
    return None


def _float_value(value: JsonValue) -> float:
    return float(value) if isinstance(value, int | float) else 0.0


def _read_json(path: Path) -> JsonObject:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _record_path(run_dir: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute() or path == run_dir or path.is_relative_to(run_dir):
        return path
    return run_dir / path


def _artifact_entries(run_dir: Path, artifacts: list[JsonObject]) -> list[JsonObject]:
    entries: list[JsonObject] = []
    for artifact in artifacts:
        raw_path = _str_value(artifact.get("path"))
        if not raw_path:
            continue
        path = _record_path(run_dir, raw_path)
        entries.append({
            "kind": _str_value(artifact.get("kind")),
            "path": str(path),
            "exists": path.exists(),
        })
    return entries


def _missing_required_logs(inputs: CommandInputs) -> list[JsonObject]:
    if not _bool_value(inputs.record.get("required"), True):
        return []
    blockers: list[JsonObject] = []
    for key in ("stdout_log", "stderr_log", "combined_log"):
        raw_path = _str_value(inputs.record.get(key))
        if raw_path and not _record_path(inputs.run_dir, raw_path).exists():
            blockers.append({
                "reason": "blocked_missing_command_log",
                "command": _str_value(inputs.record.get("name")) or f"command-{inputs.index}",
                "path": raw_path,
            })
    return blockers


def _oeqa_evidence(run_dir: Path, artifacts: list[JsonObject]) -> tuple[list[str], list[JsonObject]]:
    failed: list[str] = []
    blockers: list[JsonObject] = []
    for artifact in artifacts:
        if _str_value(artifact.get("kind")) != "oeqa_result":
            continue
        path = _record_path(run_dir, _str_value(artifact.get("path")))
        if path.suffix != ".json":
            continue
        evidence = classify_oeqa_result_path(path)
        match evidence.state:
            case OeqaResultState.FAIL:
                failed.extend(evidence.failed_tests)
            case OeqaResultState.MALFORMED:
                blockers.append({"reason": "blocked_malformed_oeqa_result", "path": str(path)})
            case OeqaResultState.PASS:
                continue
            case unreachable:
                assert_never(unreachable)
    return failed, blockers


def _state_for(record: JsonObject, oeqa_failed: list[str], blockers: list[JsonObject]) -> StepState:
    exit_code = _int_value(record.get("exit_code"))
    raw_status = _str_value(record.get("status")).lower()
    if oeqa_failed or (exit_code is not None and exit_code != 0):
        return StepState.FAIL
    match raw_status:
        case "pass" | "passed" | "ok" | "":
            return StepState.BLOCKED if blockers else StepState.PASS
        case "fail" | "failed" | "error":
            return StepState.FAIL
        case "blocked":
            return StepState.BLOCKED
        case "skipped" | "skip":
            return StepState.SKIPPED
        case _:
            return StepState.BLOCKED


def _step_result(inputs: CommandInputs) -> StepResult:
    artifacts = _json_objects(inputs.record.get("artifacts"))
    oeqa_failed, oeqa_blockers = _oeqa_evidence(inputs.run_dir, artifacts)
    blockers = _json_objects(inputs.record.get("blockers")) + _missing_required_logs(inputs) + oeqa_blockers
    state = _state_for(inputs.record, oeqa_failed, blockers)
    name = _str_value(inputs.record.get("name")) or f"command-{inputs.index}"
    step: JsonObject = {
        "name": name,
        "status": state.value,
        "required": _bool_value(inputs.record.get("required"), True),
        "exit_code": inputs.record.get("exit_code"),
        "duration_s": _float_value(inputs.record.get("duration_s")),
        "artifacts": _artifact_entries(inputs.run_dir, artifacts),
        "blockers": blockers,
        "oeqa_failed": oeqa_failed,
    }
    match state:
        case StepState.FAIL:
            return StepResult(step, blockers, _artifact_entries(inputs.run_dir, artifacts), True, False)
        case StepState.BLOCKED:
            return StepResult(step, blockers, _artifact_entries(inputs.run_dir, artifacts), False, True)
        case StepState.PASS | StepState.SKIPPED:
            return StepResult(step, blockers, _artifact_entries(inputs.run_dir, artifacts), False, False)
        case unreachable:
            assert_never(unreachable)


def _load_commands(run_dir: Path) -> tuple[list[JsonObject], list[JsonObject]]:
    path = run_dir / "commands.jsonl"
    if not path.exists():
        return [], [{"reason": "blocked_missing_commands_record", "path": str(path)}]
    commands: list[JsonObject] = []
    blockers: list[JsonObject] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            blockers.append({"reason": "blocked_malformed_command_record", "line": index})
            continue
        if isinstance(data, dict):
            commands.append(data)
        else:
            blockers.append({"reason": "blocked_malformed_command_record", "line": index})
    return commands, blockers


def summarize_run(run_dir: Path) -> tuple[JsonObject, int]:
    commands, command_blockers = _load_commands(run_dir)
    manifest = _read_json(run_dir / "manifest.json")
    plan = _read_json(run_dir / "plan.json")
    step_results = [_step_result(CommandInputs(run_dir, record, index)) for index, record in enumerate(commands, start=1)]
    blockers = command_blockers + [blocker for result in step_results for blocker in result.blockers]
    failed = any(result.failed for result in step_results)
    blocked = bool(blockers) or any(result.blocked for result in step_results)
    if failed:
        status = "FAIL"
        exit_code = EXIT_FAIL
    elif blocked:
        status = "BLOCKED"
        exit_code = EXIT_BLOCKED
    else:
        status = "PASS"
        exit_code = 0
    started = next((_str_value(command.get("started_at")) for command in commands if _str_value(command.get("started_at"))), _now())
    finished = next((_str_value(command.get("finished_at")) for command in reversed(commands) if _str_value(command.get("finished_at"))), _now())
    return {
        "status": status,
        "exit_code": exit_code,
        "started_at": started,
        "finished_at": finished,
        "duration_s": round(sum(_float_value(command.get("duration_s")) for command in commands), 6),
        "run_dir": str(run_dir),
        "active_config": manifest,
        "commands": commands,
        "included": _json_object(plan.get("included")),
        "excluded": _json_objects(plan.get("excluded")),
        "run_note": (
            "Generated by ./run_test.sh. Inspect commands.jsonl and per-lane logs in this run "
            "directory before acting on PASS, FAIL, or BLOCKED."
        ),
        "steps": [result.step for result in step_results],
        "artifacts": [artifact for result in step_results for artifact in result.artifacts],
        "blockers": blockers,
    }, exit_code
