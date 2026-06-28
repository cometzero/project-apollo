#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
import json
from pathlib import Path
import sys
from typing import assert_never


type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]


class SummaryStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True, slots=True)
class InternalSummaryInput:
    summary_path: Path
    run_dir: Path
    status: SummaryStatus
    exit_code: int
    reason: str


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _summary_status(raw_status: str) -> SummaryStatus:
    match raw_status:
        case "PASS":
            return SummaryStatus.PASS
        case "FAIL":
            return SummaryStatus.FAIL
        case "BLOCKED":
            return SummaryStatus.BLOCKED
        case _:
            return SummaryStatus.BLOCKED


def exit_code_for(status: SummaryStatus) -> int:
    match status:
        case SummaryStatus.PASS:
            return 0
        case SummaryStatus.FAIL:
            return 1
        case SummaryStatus.BLOCKED:
            return 2
        case unreachable:
            assert_never(unreachable)


def read_status(summary_path: Path) -> SummaryStatus:
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return SummaryStatus.BLOCKED
    value = data.get("status", "BLOCKED")
    return _summary_status(value if isinstance(value, str) else "BLOCKED")


def write_internal_summary(inputs: InternalSummaryInput) -> int:
    now = _now()
    summary: JsonObject = {
        "status": inputs.status.value,
        "exit_code": inputs.exit_code,
        "started_at": now,
        "finished_at": now,
        "duration_s": 0.0,
        "run_dir": str(inputs.run_dir),
        "active_config": {},
        "commands": [],
        "included": {},
        "excluded": [],
        "steps": [],
        "artifacts": [],
        "blockers": [{"reason": inputs.reason}],
    }
    inputs.summary_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = inputs.summary_path.with_name(f".{inputs.summary_path.name}.tmp")
    tmp_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp_path.replace(inputs.summary_path)
    return 0


def clear_summary(summary_path: Path) -> int:
    try:
        summary_path.unlink()
    except FileNotFoundError:
        pass
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage run_test.sh final result files.")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    clear = subparsers.add_parser("clear-summary")
    clear.add_argument("--summary", type=Path, required=True)
    clear.set_defaults(func=run_clear_summary)
    status = subparsers.add_parser("status")
    status.add_argument("--summary", type=Path, required=True)
    status.set_defaults(func=run_status)
    exit_code = subparsers.add_parser("exit-code")
    exit_code.add_argument("--status", choices=[item.value for item in SummaryStatus], required=True)
    exit_code.set_defaults(func=run_exit_code)
    internal = subparsers.add_parser("internal-summary")
    internal.add_argument("--summary", type=Path, required=True)
    internal.add_argument("--run-dir", type=Path, required=True)
    internal.add_argument("--status", choices=[item.value for item in SummaryStatus], required=True)
    internal.add_argument("--exit-code", type=int, required=True)
    internal.add_argument("--reason", required=True)
    internal.set_defaults(func=run_internal_summary)
    return parser.parse_args(argv)


def run_clear_summary(args: argparse.Namespace) -> int:
    return clear_summary(args.summary)


def run_status(args: argparse.Namespace) -> int:
    print(read_status(args.summary).value)
    return 0


def run_exit_code(args: argparse.Namespace) -> int:
    print(exit_code_for(_summary_status(args.status)))
    return 0


def run_internal_summary(args: argparse.Namespace) -> int:
    return write_internal_summary(
        InternalSummaryInput(
            summary_path=args.summary,
            run_dir=args.run_dir,
            status=_summary_status(args.status),
            exit_code=args.exit_code,
            reason=args.reason,
        )
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
