from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path
import stat
from typing import NoReturn, TypeAlias

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from .aggregate_reporting import write_aggregate_outputs
from .validation_matrix import load_validation_matrix
from .reference_policy import profile_requires_fvp_reference
from .validation_types import ValidationProfile


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonMapping: TypeAlias = dict[str, JsonValue]
Backend: TypeAlias = str
EXPECTED_RUNS = 28


@dataclass(frozen=True, slots=True)
class AggregateError(Exception):
    reason: str

    def __str__(self) -> str:
        return self.reason


@dataclass(frozen=True, slots=True)
class SourceResult:
    path: Path
    sha256: str
    captured_at: str
    summary: JsonMapping

    @property
    def profile_id(self) -> str:
        return _string(self.summary.get("test_profile"))

    @property
    def backend(self) -> str:
        return _string(self.summary.get("backend"))

    def as_json(self) -> JsonMapping:
        return {
            "profile_id": self.profile_id,
            "backend": self.backend,
            "path": str(self.path),
            "sha256": self.sha256,
            "captured_at": self.captured_at,
        }


def _fail(reason: str) -> NoReturn:
    raise AggregateError(reason)


def _mapping(value: JsonValue) -> JsonMapping:
    if not isinstance(value, dict):
        _fail("blocked_aggregate_malformed_input")
    return value


def _items(value: JsonValue) -> list[JsonValue]:
    if not isinstance(value, list):
        _fail("blocked_aggregate_malformed_input")
    return value


def _string(value: JsonValue) -> str:
    if not isinstance(value, str) or not value:
        _fail("blocked_aggregate_malformed_input")
    return value


def _integer(value: JsonValue) -> int:
    if type(value) is not int:
        _fail("blocked_aggregate_malformed_input")
    return value


def _read_json(path: Path) -> JsonMapping:
    try:
        loaded: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError):
        _fail("blocked_aggregate_malformed_input")
    return _mapping(loaded)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _timestamp(value: JsonValue) -> datetime:
    try:
        return datetime.fromisoformat(_string(value).replace("Z", "+00:00"))
    except ValueError:
        _fail("blocked_aggregate_malformed_input")


def _source_path(raw: str) -> Path:
    path = Path(raw)
    if ".." in path.parts or any(
        part == "latest" or part.startswith("latest-") for part in path.parts
    ):
        _fail("blocked_aggregate_malformed_input")
    if path.is_symlink() or not path.is_file():
        _fail("blocked_aggregate_malformed_input")
    try:
        mode = path.stat().st_mode
    except OSError:
        _fail("blocked_aggregate_malformed_input")
    if not stat.S_ISREG(mode):
        _fail("blocked_aggregate_malformed_input")
    return path.absolute()


def _validate_result(
    source: SourceResult,
    profile: ValidationProfile,
    backend: Backend,
) -> None:
    summary = source.summary
    if summary.get("test_profile") != profile.profile_id:
        _fail("blocked_aggregate_profile_mismatch")
    image = "nexios-bsp-initramfs" if profile.image == "bsp" else "nexios-image"
    if summary.get("image_profile") != profile.image or summary.get("image") != image:
        _fail("blocked_aggregate_image_mismatch")
    machine = "apollo-fvp" if backend == "fvp" else "apollo-qvp"
    if summary.get("backend") != backend or summary.get("machine") != machine:
        _fail("blocked_aggregate_profile_mismatch")
    if (
        summary.get("status") != "PASS"
        or summary.get("exit_code") != 0
        or _items(summary.get("blockers", []))
    ):
        _fail("blocked_aggregate_failed_result")
    provenance = _mapping(summary.get("provenance"))
    if provenance.get("profile_id") != profile.profile_id:
        _fail("blocked_aggregate_profile_mismatch")
    cpu_count = _integer(provenance.get("cpu_count"))
    if profile.profile_id == "mbpp" and cpu_count != 16:
        _fail("blocked_aggregate_mbpp_topology")
    if cpu_count != profile.cpu_count:
        _fail("blocked_aggregate_cpu_mismatch")
    selectors = tuple(_string(item) for item in _items(provenance.get("selectors")))
    if "test_40_virtualization" in selectors or any("xen" in item.lower() for item in selectors):
        _fail("blocked_aggregate_xen_leakage")
    if selectors != profile.fvp_selectors:
        _fail("blocked_aggregate_selector_mismatch")
    counts = _mapping(summary.get("counts"))
    if _integer(counts.get("total")) == 0:
        _fail("blocked_aggregate_zero_assertions")
    if _integer(counts.get("skipped")) != 0:
        _fail("blocked_aggregate_skipped_result")
    if any(_integer(counts.get(field)) != 0 for field in ("failed", "blocked")):
        _fail("blocked_aggregate_failed_result")
    result = _mapping(summary.get("profile_result"))
    if result.get("profile_id") != profile.profile_id or result.get("backend") != backend:
        _fail("blocked_aggregate_profile_mismatch")
    if result.get("verdict") != "PASS":
        _fail("blocked_aggregate_failed_result")
    expected = tuple(_string(item) for item in _items(result.get("expected")))
    if expected != profile.qbox_assertions:
        _fail("blocked_aggregate_assertion_mismatch")
    assertions = tuple(_mapping(item) for item in _items(result.get("assertions")))
    observed = tuple(_string(item.get("id")) for item in assertions)
    if observed != expected or len(set(observed)) != len(observed):
        _fail("blocked_aggregate_assertion_mismatch")
    if any(item.get("status") == "SKIPPED" for item in assertions):
        _fail("blocked_aggregate_skipped_result")
    if any(item.get("status") != "PASS" for item in assertions):
        _fail("blocked_aggregate_failed_result")
    if any(item.get("coverage_kind") != profile.coverage_kind for item in assertions):
        _fail("blocked_aggregate_semantic_label_mismatch")
    if tuple(_string(item) for item in _items(provenance.get("expected_assertion_ids"))) != expected:
        _fail("blocked_aggregate_assertion_mismatch")
    if provenance.get("coverage_kind") != profile.coverage_kind:
        _fail("blocked_aggregate_semantic_label_mismatch")
    if (
        provenance.get("image") != image
        or provenance.get("image_profile") != profile.image
        or provenance.get("machine") != machine
    ):
        _fail("blocked_aggregate_image_mismatch")
    if _mapping(summary.get("input_revisions")) != _mapping(provenance.get("source_revisions")):
        _fail("blocked_aggregate_revision_mismatch")
    if _integer(counts.get("passed")) != len(expected) or _integer(counts.get("total")) != len(expected):
        _fail("blocked_aggregate_assertion_mismatch")


def _validate_references(results: dict[tuple[str, str], SourceResult]) -> None:
    for (profile_id, backend), source in results.items():
        if backend != "qbox":
            continue
        fvp = results[(profile_id, "fvp")]
        raw_accepted = source.summary.get("accepted_fvp_reference")
        if not isinstance(raw_accepted, dict):
            if source.summary.get("comparison_mode") != "standalone":
                _fail("blocked_aggregate_fvp_reference_mismatch")
            if profile_requires_fvp_reference(profile_id):
                _fail("blocked_aggregate_fvp_reference_mismatch")
            continue
        accepted = raw_accepted
        fvp_provenance = _mapping(fvp.summary.get("provenance"))
        if (
            accepted.get("run_id") != fvp.summary.get("run_id")
            or Path(_string(accepted.get("path"))).absolute() != fvp.path
            or accepted.get("summary_sha256") != fvp.sha256
            or accepted.get("semantic_profile_digest")
            != fvp_provenance.get("semantic_profile_digest")
        ):
            _fail("blocked_aggregate_fvp_reference_mismatch")
        fvp_revisions = _mapping(fvp_provenance.get("source_revisions"))
        qbox_revisions = _mapping(_mapping(source.summary.get("provenance")).get("source_revisions"))
        if any(qbox_revisions.get(key) != value for key, value in fvp_revisions.items()):
            _fail("blocked_aggregate_revision_mismatch")


def aggregate_validation(matrix_path: Path, run_set_path: Path, out_dir: Path) -> None:
    matrix = load_validation_matrix(matrix_path)
    run_set = _read_json(run_set_path)
    schema_path = Path(__file__).resolve().parents[1] / "schema/validation-run-set.schema.json"
    try:
        Draft202012Validator(
            _read_json(schema_path),
            format_checker=FormatChecker(),
        ).validate(run_set)
    except ValidationError:
        _fail("blocked_aggregate_malformed_input")
    if run_set.get("matrix_sha256") != _sha256(matrix_path.read_bytes()):
        _fail("blocked_aggregate_malformed_input")
    not_before = _timestamp(run_set.get("not_before"))
    sources: list[SourceResult] = []
    paths: set[Path] = set()
    for raw in _items(run_set.get("results")):
        entry = _mapping(raw)
        path = _source_path(_string(entry.get("path")))
        if path in paths:
            _fail("blocked_aggregate_duplicate_result")
        paths.add(path)
        captured_at = _string(entry.get("captured_at"))
        if _timestamp(captured_at) < not_before:
            _fail("blocked_aggregate_stale_result")
        digest = _string(entry.get("sha256"))
        if _sha256(path.read_bytes()) != digest:
            _fail("blocked_aggregate_malformed_input")
        sources.append(SourceResult(path, digest, captured_at, _read_json(path)))
    by_key: dict[tuple[str, str], SourceResult] = {}
    profiles = {item.profile_id: item for item in matrix.profiles}
    for source in sources:
        profile = profiles.get(source.profile_id)
        if profile is None or source.backend not in {"fvp", "qbox"}:
            _fail("blocked_aggregate_profile_mismatch")
        key = (source.profile_id, source.backend)
        if key in by_key:
            _fail("blocked_aggregate_duplicate_result")
        by_key[key] = source
        _validate_result(source, profile, source.backend)
    expected_keys = {(item.profile_id, backend) for item in matrix.profiles for backend in ("fvp", "qbox")}
    if set(by_key) != expected_keys or len(sources) != EXPECTED_RUNS:
        _fail("blocked_aggregate_missing_result")
    _validate_references(by_key)
    if out_dir.exists() and any(out_dir.iterdir()):
        _fail("blocked_aggregate_output_not_empty")
    write_aggregate_outputs(out_dir, matrix, [item.as_json() for item in sources])
