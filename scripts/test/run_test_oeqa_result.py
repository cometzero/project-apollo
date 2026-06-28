from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import json
from pathlib import Path
from typing import Final


type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]

FAILED_STATUSES: Final = {"error", "fail", "failed"}


class OeqaResultState(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    MALFORMED = "malformed"


@dataclass(frozen=True, slots=True)
class OeqaResultEvidence:
    state: OeqaResultState
    failed_tests: list[str]


def _json_object(value: JsonValue) -> JsonObject:
    return value if isinstance(value, dict) else {}


def _json_objects(value: JsonValue) -> list[JsonObject]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _str_value(value: JsonValue) -> str:
    return value if isinstance(value, str) else ""


def _int_value(value: JsonValue) -> int | None:
    return value if type(value) is int else None


def _status(test: JsonObject) -> str:
    return _str_value(test.get("status") or test.get("result") or test.get("outcome")).lower()


def _has_failure_flag(data: JsonObject) -> bool:
    failures = _int_value(data.get("failures"))
    failed = _int_value(data.get("failed"))
    return (
        (failures is not None and failures > 0)
        or (failed is not None and failed > 0)
        or data.get("failed") is True
        or data.get("passed") is False
        or data.get("success") is False
    )


def classify_oeqa_result(data: JsonObject) -> OeqaResultEvidence:
    failed_tests: list[str] = []
    result_count = 0
    for test in _json_objects(data.get("tests")):
        status = _status(test)
        if not status:
            continue
        result_count += 1
        if status in FAILED_STATUSES:
            failed_tests.append(_str_value(test.get("name")) or "unnamed_oeqa_test")
    for result_set in data.values():
        result = _json_object(_json_object(result_set).get("result"))
        for name, test_value in result.items():
            status = _status(_json_object(test_value))
            if not status:
                continue
            result_count += 1
            if status in FAILED_STATUSES:
                failed_tests.append(name)
    if failed_tests or _has_failure_flag(data):
        return OeqaResultEvidence(OeqaResultState.FAIL, failed_tests or ["oeqa_result_failed"])
    if result_count > 0:
        return OeqaResultEvidence(OeqaResultState.PASS, [])
    return OeqaResultEvidence(OeqaResultState.MALFORMED, [])


def classify_oeqa_result_path(path: Path) -> OeqaResultEvidence:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return OeqaResultEvidence(OeqaResultState.MALFORMED, [])
    if not isinstance(data, dict):
        return OeqaResultEvidence(OeqaResultState.MALFORMED, [])
    return classify_oeqa_result(data)
