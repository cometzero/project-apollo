from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import stat
from typing import NoReturn, TypeAlias

from .provenance import (
    JsonValue,
    ProfileProvenance,
    SharedInput,
    sha256_bytes,
)
from .source_revisions import SourceRevisionError, validate_fvp_source_revisions


JsonMapping: TypeAlias = dict[str, JsonValue]
XEN_SELECTOR = "test_40_virtualization"


@dataclass(frozen=True, slots=True)
class FVPReferenceError(Exception):
    reason: str

    def __str__(self) -> str:
        return self.reason


@dataclass(frozen=True, slots=True)
class AcceptedFVPReference:
    run_id: str
    path: Path
    summary_sha256: str
    semantic_profile_digest: str

    def as_json(self) -> dict[str, JsonValue]:
        return {
            "run_id": self.run_id,
            "path": str(self.path),
            "summary_sha256": self.summary_sha256,
            "semantic_profile_digest": self.semantic_profile_digest,
        }


@dataclass(frozen=True, slots=True)
class FVPReferenceRequest:
    root: Path
    path: Path
    qbox_run_id: str
    current: ProfileProvenance


def _fail(reason: str) -> NoReturn:
    raise FVPReferenceError(reason)


def _mapping(value: JsonValue, field: str) -> JsonMapping:
    if not isinstance(value, dict):
        _fail("blocked_fvp_reference_malformed")
    return value


def _items(value: JsonValue, field: str) -> list[JsonValue]:
    if not isinstance(value, list):
        _fail("blocked_fvp_reference_malformed")
    return value


def _string(value: JsonValue, field: str) -> str:
    if not isinstance(value, str) or not value:
        _fail("blocked_fvp_reference_malformed")
    return value


def _integer(value: JsonValue, field: str) -> int:
    if type(value) is not int:
        _fail("blocked_fvp_reference_malformed")
    return value


def _strings(value: JsonValue, field: str) -> tuple[str, ...]:
    return tuple(_string(item, field) for item in _items(value, field))


def _safe_bytes(root: Path, raw_path: Path, missing_reason: str) -> tuple[Path, bytes]:
    root = root.resolve()
    if ".." in raw_path.parts or any(part == "latest" or part.startswith("latest-") for part in raw_path.parts):
        _fail("blocked_fvp_reference_path")
    candidate = raw_path if raw_path.is_absolute() else root / raw_path
    try:
        relative = candidate.absolute().relative_to(root)
    except ValueError:
        _fail("blocked_fvp_reference_path")
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            _fail("blocked_fvp_reference_path")
    if not candidate.is_file():
        _fail(missing_reason)
    try:
        descriptor = os.open(candidate, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(descriptor, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                _fail("blocked_fvp_reference_path")
            data = stream.read()
        return candidate.absolute(), data
    except OSError:
        _fail(missing_reason)


def _parse_json(data: bytes) -> JsonMapping:
    try:
        loaded: JsonValue = json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError):
        _fail("blocked_fvp_reference_malformed")
    return _mapping(loaded, "root")


def _validate_assertions(summary: JsonMapping, current: ProfileProvenance) -> None:
    result = _mapping(summary.get("profile_result"), "profile_result")
    if result.get("version") != 1:
        _fail("blocked_fvp_reference_malformed")
    if result.get("profile_id") != current.profile_id:
        _fail("blocked_fvp_reference_profile_mismatch")
    if result.get("backend") != "fvp":
        _fail("blocked_fvp_reference_backend")
    if result.get("verdict") != "PASS":
        _fail("blocked_fvp_reference_status")
    expected = _strings(result.get("expected"), "profile_result.expected")
    if expected != current.expected_assertion_ids:
        _fail("blocked_fvp_reference_expected_mismatch")
    observed: list[str] = []
    for raw in _items(result.get("assertions"), "profile_result.assertions"):
        assertion = _mapping(raw, "profile_result.assertions[]")
        observed.append(_string(assertion.get("id"), "assertion.id"))
        if assertion.get("status") != "PASS":
            _fail("blocked_fvp_reference_assertions_incomplete")
        if assertion.get("coverage_kind") != current.coverage_kind:
            _fail("blocked_fvp_reference_assertions_incomplete")
    if set(observed) != set(expected) or len(observed) != len(set(observed)):
        _fail("blocked_fvp_reference_assertions_incomplete")
    counts = _mapping(summary.get("counts"), "counts")
    total = len(expected)
    if (
        _integer(counts.get("passed"), "counts.passed") != total
        or _integer(counts.get("total"), "counts.total") != total
        or any(
            _integer(counts.get(field), f"counts.{field}") != 0
            for field in ("failed", "blocked", "skipped")
        )
    ):
        _fail("blocked_fvp_reference_assertions_incomplete")


def _shared_inputs(value: JsonValue) -> tuple[SharedInput, ...]:
    parsed: list[SharedInput] = []
    for raw in _items(value, "provenance.shared_inputs"):
        item = _mapping(raw, "provenance.shared_inputs[]")
        parsed.append(
            SharedInput(
                _string(item.get("path"), "shared.path"),
                _string(item.get("git_blob_sha256"), "shared.git_blob_sha256"),
            )
        )
    return tuple(parsed)


def _source_revisions(value: JsonValue) -> dict[str, str]:
    raw = _mapping(value, "provenance.source_revisions")
    parsed: dict[str, str] = {}
    for key, revision in raw.items():
        if not isinstance(revision, str):
            _fail("blocked_fvp_reference_source_revision_malformed")
        parsed[key] = revision
    return parsed


def _validate_runtime_inputs(root: Path, value: JsonValue) -> None:
    seen: set[str] = set()
    reasons: dict[str, str] = {
        "testdata": "blocked_fvp_reference_testdata_drift",
        "runtime_config": "blocked_fvp_reference_runtime_config_drift",
        "image_artifact": "blocked_fvp_reference_image_artifact_drift",
    }
    for raw in _items(value, "provenance.runtime_inputs"):
        item = _mapping(raw, "provenance.runtime_inputs[]")
        kind = _string(item.get("kind"), "runtime.kind")
        reason = reasons.get(kind)
        if reason is None or kind in seen:
            _fail("blocked_fvp_reference_malformed")
        seen.add(kind)
        path, data = _safe_bytes(
            root,
            Path(_string(item.get("path"), "runtime.path")),
            reason,
        )
        if sha256_bytes(data) != _string(item.get("sha256"), "runtime.sha256"):
            _fail(reason)
        if path.name.startswith("latest-"):
            _fail("blocked_fvp_reference_path")
    if seen != set(reasons):
        _fail("blocked_fvp_reference_malformed")


def _validate_provenance(
    root: Path,
    value: JsonValue,
    current: ProfileProvenance,
) -> str:
    provenance = _mapping(value, "provenance")
    if provenance.get("version") != 1:
        _fail("blocked_fvp_reference_malformed")
    if provenance.get("profile_id") != current.profile_id:
        _fail("blocked_fvp_reference_profile_mismatch")
    selectors = _strings(provenance.get("selectors"), "provenance.selectors")
    if XEN_SELECTOR in selectors:
        _fail("blocked_fvp_reference_xen")
    if selectors != current.selectors:
        _fail("blocked_fvp_reference_selector_mismatch")
    if _strings(provenance.get("expected_assertion_ids"), "provenance.expected") != current.expected_assertion_ids:
        _fail("blocked_fvp_reference_expected_mismatch")
    if provenance.get("coverage_kind") != current.coverage_kind:
        _fail("blocked_fvp_reference_assertions_incomplete")
    if provenance.get("image_profile") != current.image_profile or provenance.get("image") != current.image:
        _fail("blocked_fvp_reference_image_mismatch")
    if provenance.get("machine") != "apollo-fvp":
        _fail("blocked_fvp_reference_backend")
    if _integer(provenance.get("cpu_count"), "provenance.cpu_count") != current.cpu_count:
        _fail("blocked_fvp_reference_cpu_mismatch")
    if provenance.get("profile_snapshot_sha256") != current.profile_snapshot_sha256:
        _fail("blocked_fvp_reference_profile_snapshot_drift")
    shared_inputs = _shared_inputs(provenance.get("shared_inputs"))
    shared_contract_matches = shared_inputs == current.shared_inputs
    if not shared_contract_matches:
        _fail("blocked_fvp_reference_shared_input_drift")
    semantic_digest = _string(provenance.get("semantic_profile_digest"), "provenance.semantic")
    if semantic_digest != current.semantic_profile_digest:
        _fail("blocked_fvp_reference_semantic_drift")
    try:
        validate_fvp_source_revisions(
            root,
            _source_revisions(provenance.get("source_revisions")),
            current.source_revisions,
            shared_contract_matches,
        )
    except SourceRevisionError as error:
        _fail(error.reason)
    _validate_runtime_inputs(root, provenance.get("runtime_inputs"))
    return semantic_digest


def validate_fvp_reference(request: FVPReferenceRequest) -> AcceptedFVPReference:
    path, data = _safe_bytes(request.root, request.path, "blocked_fvp_reference_missing")
    if path.name != "summary.json":
        _fail("blocked_fvp_reference_path")
    summary = _parse_json(data)
    if summary.get("status") != "PASS" or summary.get("exit_code") != 0:
        _fail("blocked_fvp_reference_status")
    if summary.get("backend") != "fvp" or summary.get("machine") != "apollo-fvp":
        _fail("blocked_fvp_reference_backend")
    run_id = _string(summary.get("run_id"), "run_id")
    if run_id == request.qbox_run_id:
        _fail("blocked_fvp_reference_duplicate_run_id")
    if run_id != path.parent.name or Path(_string(summary.get("run_dir"), "run_dir")).resolve() != path.parent:
        _fail("blocked_fvp_reference_path")
    if summary.get("test_profile") != request.current.profile_id:
        _fail("blocked_fvp_reference_profile_mismatch")
    if summary.get("image_profile") != request.current.image_profile or summary.get("image") != request.current.image:
        _fail("blocked_fvp_reference_image_mismatch")
    _validate_assertions(summary, request.current)
    digest = _validate_provenance(
        request.root,
        summary.get("provenance"),
        request.current,
    )
    return AcceptedFVPReference(run_id, path, sha256_bytes(data), digest)
