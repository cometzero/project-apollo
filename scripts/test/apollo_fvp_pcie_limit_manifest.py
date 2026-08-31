from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Final

import jsonschema

ROOT: Final = Path(__file__).resolve().parents[2]
FIXTURE_ROOT: Final = ROOT / "tests/fixtures/gic720ae/pcie-its/fvp-limit"
MANIFEST_PATH: Final = FIXTURE_ROOT / "manifest.json"
MANIFEST_SCHEMA_PATH: Final = ROOT / "tests/schemas/apollo-fvp-pcie-limit-manifest.schema.json"
MANIFEST_SHA256: Final = "fba17ada62536b3f4cacc1dbaeb43168464ffbff4593c1a699e673d68922d38f"
type JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
type JsonObject = dict[str, JsonValue]


@dataclass(frozen=True, slots=True)
class ManifestError(Exception):
    reason: str

    def __str__(self) -> str:
        return self.reason


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ManifestError(reason)


def hash_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ManifestError("input_path")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_object(path: Path) -> JsonObject:
    try:
        value: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ManifestError("manifest_schema") from error
    if not isinstance(value, dict):
        raise ManifestError("manifest_schema")
    return value


def load_manifest(path: Path) -> JsonObject:
    require(path.absolute() == MANIFEST_PATH, "manifest_path")
    require(hash_file(path) == MANIFEST_SHA256, "manifest_hash")
    try:
        jsonschema.Draft202012Validator(json_object(MANIFEST_SCHEMA_PATH)).validate(json_object(path))
    except jsonschema.ValidationError as error:
        raise ManifestError("manifest_schema") from error
    return json_object(path)


def verify_inputs(manifest: JsonObject) -> JsonObject:
    inputs = manifest.get("inputs")
    if not isinstance(inputs, dict):
        raise ManifestError("manifest_schema")
    regular_files = {path.name for path in FIXTURE_ROOT.iterdir() if path.is_file()}
    listed_paths: set[str] = set()
    verified: JsonObject = {}
    for role, entry_value in inputs.items():
        if not isinstance(entry_value, dict):
            raise ManifestError("manifest_schema")
        path_value = entry_value.get("path")
        expected_hash = entry_value.get("sha256")
        if not isinstance(path_value, str) or not isinstance(expected_hash, str):
            raise ManifestError("manifest_schema")
        path = FIXTURE_ROOT / path_value
        require(path.parent == FIXTURE_ROOT and path.name == path_value, "input_path")
        require(path_value not in listed_paths, "fixture_inventory")
        listed_paths.add(path_value)
        actual_hash = hash_file(path)
        require(actual_hash == expected_hash, "input_hash")
        fixture_path = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else path.name
        verified[role] = {"path": fixture_path, "sha256": actual_hash}
    require(regular_files == listed_paths | {MANIFEST_PATH.name}, "fixture_inventory")
    return verified
