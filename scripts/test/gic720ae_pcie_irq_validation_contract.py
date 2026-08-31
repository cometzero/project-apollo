from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import jsonschema

ROOT: Final = Path(__file__).resolve().parents[2]
GATE_SHA256: Final = "5ceb377244eb0e4fddd6e4346a701fa1a75185d0dc689d2e396c917cb3549a82"
PROFILE_SHA256: Final = (
    "d0fd532fc4e07edbe02d62ae06cb6afb84663b69cdf0f139729bc3a3f65cf03b"
)
PROVENANCE_SCHEMA: Final = (
    ROOT / "tests/schemas/gic720ae-pcie-irq-validation-provenance.schema.json"
)
RESULT_SCHEMA: Final = (
    ROOT / "tests/schemas/gic720ae-pcie-irq-validation-result.schema.json"
)
QBOX_BINARY: Final = ROOT / "build/local-apollo-qvp/work/qbox-platform/platforms-vp"
QBOX_CONFIG: Final = (
    ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua"
)
HASH_RE: Final = re.compile(r"^[0-9a-f]{64}$")
JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject = dict[str, JsonValue]


@dataclass(frozen=True, slots=True)
class ValidationError(Exception):
    reason: str

    def __str__(self) -> str:
        return self.reason


@dataclass(frozen=True, slots=True)
class RunConfig:
    gate: Path
    profile: Path
    run_root: Path
    provenance_output: Path | None
    frozen_provenance: Path | None
    timeout: int
    qbox_binary: Path = QBOX_BINARY


@dataclass(frozen=True, slots=True)
class ChildResult:
    command: tuple[str, ...]
    returncode: int
    log: Path


def digest(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValidationError(f"input_path:{path}")
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def load_object(path: Path, reason: str) -> JsonObject:
    try:
        value: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValidationError(reason) from error
    if not isinstance(value, dict):
        raise ValidationError(reason)
    return value


def object_value(value: JsonValue, reason: str) -> JsonObject:
    if not isinstance(value, dict):
        raise ValidationError(reason)
    return value


def string_value(value: JsonValue, reason: str) -> str:
    if not isinstance(value, str):
        raise ValidationError(reason)
    return value


def require_hash(path: Path, expected: str, reason: str) -> None:
    if not HASH_RE.fullmatch(expected) or digest(path) != expected:
        raise ValidationError(reason)


def validate_gate(path: Path) -> JsonObject:
    require_hash(path, GATE_SHA256, "fvp_reference_gate_sha256")
    gate = load_object(path, "fvp_reference_gate_json")
    claims = object_value(gate.get("claims"), "fvp_reference_gate_claims")
    cleanup = object_value(gate.get("cleanup"), "fvp_reference_gate_cleanup")
    required = (
        gate.get("schema_version") == 1
        and gate.get("reference_gate") == "PASS"
        and gate.get("fvp_qualification") == "UNSUPPORTED"
        and gate.get("reason") == "immutable_ecam_limit"
        and gate.get("configuration_applied") is True
        and gate.get("qbox_allowed") is True
        and gate.get("qbox_started") is False
        and cleanup.get("status") == "PASS"
        and cleanup.get("qbox_started") is False
        and all(
            claims.get(name) is False
            for name in (
                "endpoint_enumeration",
                "physical_its_delivery",
                "qbox_equivalence",
            )
        )
    )
    if not required:
        raise ValidationError("fvp_reference_gate_semantics")
    return gate


def profile_bindings(path: Path) -> tuple[JsonObject, dict[str, tuple[Path, str]]]:
    require_hash(path, PROFILE_SHA256, "qbox_profile_manifest_sha256")
    profile = load_object(path, "qbox_profile_manifest_json")
    if (
        profile.get("schema_version") != 2
        or profile.get("profile") != "apollo-qvp-pcie-irq"
    ):
        raise ValidationError("qbox_profile_manifest_semantics")
    fvp = object_value(profile.get("fvp_reference"), "qbox_profile_fvp_reference")
    if (
        fvp.get("sha256") != GATE_SHA256
        or fvp.get("reference_gate") != "PASS"
        or fvp.get("fvp_qualification") != "UNSUPPORTED"
    ):
        raise ValidationError("qbox_profile_fvp_reference")
    bindings: dict[str, tuple[Path, str]] = {}
    for section_name in ("inputs", "artifacts"):
        section = object_value(
            profile.get(section_name), f"qbox_profile_{section_name}"
        )
        for name, raw_entry in section.items():
            entry = object_value(raw_entry, f"qbox_profile_{section_name}:{name}")
            artifact_path = Path(
                string_value(entry.get("path"), f"qbox_profile_path:{name}")
            )
            expected = string_value(entry.get("sha256"), f"qbox_profile_sha256:{name}")
            require_hash(
                artifact_path, expected, f"qbox_profile_artifact_sha256:{name}"
            )
            bindings[f"profile_{section_name}_{name}"] = (artifact_path, expected)
    return profile, bindings


def validate_schema(payload: JsonObject, schema_path: Path, reason: str) -> None:
    schema = load_object(schema_path, f"{reason}_schema")
    try:
        jsonschema.Draft202012Validator(schema).validate(payload)
    except jsonschema.ValidationError as error:
        raise ValidationError(reason) from error


def validate_run_root(path: Path) -> Path:
    if ".." in path.parts or path.is_symlink():
        raise ValidationError("run_root")
    resolved = path.absolute()
    if resolved.exists():
        raise ValidationError("stale_run_root")
    for parent in resolved.parents:
        if parent.is_symlink():
            raise ValidationError("run_root_symlink")
    return resolved


def validate_output_path(path: Path) -> Path:
    if ".." in path.parts or path.is_symlink():
        raise ValidationError("output_path")
    absolute = path.absolute()
    if any(parent.is_symlink() for parent in absolute.parents):
        raise ValidationError("output_path_symlink")
    return absolute
