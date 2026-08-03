#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema", "pyyaml"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/gic720ae_contract.py
# 3. This module is normally imported by Task 5 tools.
# ──────────────────
"""Shared deterministic I/O boundaries for GIC-720AE validation tools."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import TypeAlias

import jsonschema
from jsonschema.exceptions import SchemaError, ValidationError
import yaml


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]
JsonArray: TypeAlias = list[JsonValue]
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class ContractError(Exception):
    reason: str
    detail: str

    def __str__(self) -> str:
        return f"{self.reason}: {self.detail}"


def canonical_bytes(value: JsonValue) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_bytes(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ContractError("forbidden_input", f"not a regular file: {path}")
    try:
        return path.read_bytes()
    except OSError as error:
        raise ContractError("missing_input", str(path)) from error


def sha_path(path: Path) -> str:
    return sha_bytes(read_bytes(path))


def json_object(path: Path) -> JsonObject:
    try:
        value = json.loads(read_bytes(path))
    except json.JSONDecodeError as error:
        raise ContractError("malformed_input", str(path)) from error
    if not isinstance(value, dict):
        raise ContractError("malformed_input", f"expected object: {path}")
    return value


def yaml_object(path: Path) -> JsonObject:
    try:
        value = yaml.safe_load(read_bytes(path))
    except yaml.YAMLError as error:
        raise ContractError("malformed_input", str(path)) from error
    if not isinstance(value, dict):
        raise ContractError("malformed_input", f"expected mapping: {path}")
    return value


def validate(instance: JsonValue, schema_path: Path) -> None:
    schema = json_object(schema_path)
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(instance)
    except SchemaError as error:
        raise ContractError("invalid_schema", str(schema_path)) from error
    except ValidationError as error:
        raise ContractError("schema_validation_failed", error.json_path) from error


def require_sha(value: JsonValue, field: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise ContractError("malformed_input", f"{field} is not SHA256")
    return value


def require_string(value: JsonValue, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContractError("malformed_input", f"{field} is not a string")
    return value


def require_list(value: JsonValue, field: str) -> list[JsonValue]:
    if not isinstance(value, list):
        raise ContractError("malformed_input", f"{field} is not an array")
    return value


def write_json(path: Path, value: JsonValue) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_bytes(canonical_bytes(value))
    except OSError as error:
        raise ContractError("output_error", str(path)) from error


def failure(reason: str, *, checks: list[str] | None = None) -> JsonObject:
    check_values: JsonArray = []
    if checks is not None:
        check_values.extend(checks)
    return {
        "format_version": 1,
        "verdict": "FAIL",
        "reason": reason,
        "checks": check_values,
        "input_shas": {},
    }


def artifact(path: Path, producer_task: int) -> JsonObject:
    return {
        "path": str(path.resolve()),
        "sha256": sha_path(path),
        "producer_task": producer_task,
    }


if __name__ == "__main__":
    raise SystemExit(0)
