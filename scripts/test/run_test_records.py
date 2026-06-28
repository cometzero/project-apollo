#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import sys


type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]


@dataclass(frozen=True, slots=True)
class RecordInput:
    commands_file: Path
    name: str
    status: str
    exit_code: int | None
    required: bool
    stdout_log: str
    stderr_log: str
    artifact_path: str
    blockers_path: Path | None
    reason: str
    argv: list[str]


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _json_object(value: JsonValue) -> JsonObject:
    return value if isinstance(value, dict) else {}


def _json_objects(value: JsonValue) -> list[JsonObject]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _str_value(value: JsonValue) -> str:
    return value if isinstance(value, str) else ""


def _read_json(path: Path) -> JsonObject:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _blockers(path: Path | None, reason: str) -> list[JsonObject]:
    if path is None or not path.is_file():
        return [{"reason": reason}] if reason else []
    data = _read_json(path)
    blockers = _json_objects(data.get("blockers"))
    raw_reason = _str_value(data.get("reason"))
    if not blockers and raw_reason:
        return [{"reason": raw_reason, "path": str(path)}]
    if not blockers and reason:
        return [{"reason": reason}]
    return blockers


def init_records(commands_file: Path) -> int:
    commands_file.parent.mkdir(parents=True, exist_ok=True)
    with commands_file.open("w", encoding="utf-8"):
        pass
    return 0


def append_record(inputs: RecordInput) -> int:
    now = _now()
    record: JsonObject = {
        "name": inputs.name,
        "argv": inputs.argv,
        "required": inputs.required,
        "status": inputs.status,
        "started_at": now,
        "finished_at": now,
        "duration_s": 0.0,
    }
    if inputs.exit_code is not None:
        record["exit_code"] = inputs.exit_code
    if inputs.stdout_log:
        record["stdout_log"] = inputs.stdout_log
    if inputs.stderr_log:
        record["stderr_log"] = inputs.stderr_log
    if inputs.artifact_path:
        record["artifacts"] = [{"kind": "json", "path": inputs.artifact_path}]
    blockers = _blockers(inputs.blockers_path, inputs.reason)
    if blockers:
        record["blockers"] = blockers
    inputs.commands_file.parent.mkdir(parents=True, exist_ok=True)
    with inputs.commands_file.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")
    return 0


def _parse_exit_code(value: str) -> int | None:
    return int(value) if value else None


def _parse_bool(value: str) -> bool:
    return value == "true"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage run_test.sh command records.")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    init = subparsers.add_parser("init")
    init.add_argument("--commands-file", type=Path, required=True)
    init.set_defaults(func=run_init)
    append = subparsers.add_parser("append")
    append.add_argument("--commands-file", type=Path, required=True)
    append.add_argument("--name", required=True)
    append.add_argument("--status", required=True)
    append.add_argument("--exit-code", default="")
    append.add_argument("--required", choices=("true", "false"), required=True)
    append.add_argument("--stdout-log", default="")
    append.add_argument("--stderr-log", default="")
    append.add_argument("--artifact-path", default="")
    append.add_argument("--blockers-path", type=Path)
    append.add_argument("--reason", default="")
    append.add_argument("--argv", action="append", default=[])
    append.set_defaults(func=run_append)
    return parser.parse_args(argv)


def run_init(args: argparse.Namespace) -> int:
    return init_records(args.commands_file)


def run_append(args: argparse.Namespace) -> int:
    blockers_path = args.blockers_path if isinstance(args.blockers_path, Path) else None
    return append_record(
        RecordInput(
            commands_file=args.commands_file,
            name=args.name,
            status=args.status,
            exit_code=_parse_exit_code(args.exit_code),
            required=_parse_bool(args.required),
            stdout_log=args.stdout_log,
            stderr_log=args.stderr_log,
            artifact_path=args.artifact_path,
            blockers_path=blockers_path,
            reason=args.reason,
            argv=args.argv,
        )
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        return args.func(args)
    except OSError as exc:
        print(f"run_test_records.py: {exc}", file=sys.stderr)
        return 70


if __name__ == "__main__":
    raise SystemExit(main())
