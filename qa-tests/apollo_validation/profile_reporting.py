from __future__ import annotations

import json
from pathlib import Path
from typing import TypeAlias

from .profile_results import (
    ProfileCountsJson,
    ProfileResultError,
    ProfileResultJson,
    normalize_profile_run,
    parse_backend,
    profile_counts_json,
    profile_result_json,
    verdict_exit_code,
)


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = (
    JsonScalar
    | list["JsonValue"]
    | dict[str, "JsonValue"]
    | ProfileCountsJson
    | ProfileResultJson
)


def _required_string(summary: dict[str, JsonValue], field: str) -> str:
    value = summary.get(field)
    if not isinstance(value, str) or not value:
        raise ProfileResultError(f"profile summary field {field} must be a string")
    return value


def _dict_items(summary: dict[str, JsonValue], field: str) -> list[JsonValue]:
    value = summary.get(field, [])
    if not isinstance(value, list):
        raise ProfileResultError(f"profile summary field {field} must be an array")
    return value


def apply_profile_summary(run_dir: Path, summary: dict[str, JsonValue]) -> int:
    profile_id = _required_string(summary, "test_profile")
    backend = parse_backend(_required_string(summary, "backend"))
    normalized = normalize_profile_run(run_dir, profile_id, backend)
    summary["status"] = normalized.result.verdict
    summary["exit_code"] = verdict_exit_code(normalized.result.verdict)
    summary["counts"] = profile_counts_json(normalized.counts)
    summary["profile_result"] = profile_result_json(normalized.result)
    summary["blockers"] = [
        *_dict_items(summary, "blockers"),
        *({"reason": reason} for reason in normalized.reasons),
    ]
    summary["artifacts"] = [
        *_dict_items(summary, "artifacts"),
        {"kind": "profile_result", "path": "profile-result.json"},
    ]
    return verdict_exit_code(normalized.result.verdict)


def write_normalized_profile_result(
    run_dir: Path,
    summary: dict[str, JsonValue],
) -> None:
    profile_result = summary.get("profile_result")
    if isinstance(profile_result, dict):
        (run_dir / "profile-result.json").write_text(
            json.dumps(profile_result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
