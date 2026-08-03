#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
from typing import Final

import jsonschema
import yaml


ROOT: Final = Path(__file__).resolve().parents[2]
STAGES: Final = (1, 2, 3, 4)
type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]


@dataclass(frozen=True, slots=True)
class ValidationFailure(RuntimeError):
    reason: str
    detail: str

    def __str__(self) -> str:
        return self.detail


@dataclass(frozen=True, slots=True)
class SourceFile:
    path: str
    lines: tuple[str, ...]


def read_file(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except FileNotFoundError as exc:
        raise ValidationFailure("missing-input", f"missing input: {path}") from exc


def load_yaml(path: Path) -> JsonObject:
    try:
        value = yaml.safe_load(read_file(path))
    except yaml.YAMLError as exc:
        raise ValidationFailure("invalid-matrix", f"invalid YAML: {path}") from exc
    if not isinstance(value, dict):
        raise ValidationFailure("invalid-matrix", "matrix root must be an object")
    return value


def load_schema(path: Path) -> JsonObject:
    try:
        value = json.loads(read_file(path))
    except json.JSONDecodeError as exc:
        raise ValidationFailure("invalid-schema", f"invalid JSON schema: {path}") from exc
    if not isinstance(value, dict):
        raise ValidationFailure("invalid-schema", "schema root must be an object")
    return value


def validate_schema(matrix: JsonObject, schema: JsonObject) -> None:
    try:
        jsonschema.Draft202012Validator(schema).validate(matrix)
    except jsonschema.SchemaError as exc:
        raise ValidationFailure("invalid-schema", exc.message) from exc
    except jsonschema.ValidationError as exc:
        raise ValidationFailure("schema-validation-failed", exc.message) from exc


def verified_sources(matrix: JsonObject) -> dict[str, SourceFile]:
    sources = matrix["sources"]
    if not isinstance(sources, dict):
        raise ValidationFailure("schema-validation-failed", "sources must be an object")
    source_files: dict[str, SourceFile] = {}
    for name, source in sources.items():
        if not isinstance(name, str) or not isinstance(source, dict):
            raise ValidationFailure("schema-validation-failed", "source entries must be objects")
        raw_path = source.get("path")
        expected_hash = source.get("sha256")
        if not isinstance(raw_path, str) or not isinstance(expected_hash, str):
            raise ValidationFailure("schema-validation-failed", "source entry is incomplete")
        path = ROOT / raw_path
        if path.is_symlink() or not path.is_file() or ROOT not in path.resolve().parents:
            raise ValidationFailure("invalid-source-evidence", f"unsafe source path: {raw_path}")
        actual_hash = hashlib.sha256(read_file(path)).hexdigest()
        if actual_hash != expected_hash:
            raise ValidationFailure("stale-source-evidence", f"source hash changed: {raw_path}")
        try:
            lines = tuple(read_file(path).decode("utf-8").splitlines())
        except UnicodeDecodeError as exc:
            raise ValidationFailure("invalid-source-evidence", f"source is not UTF-8 text: {raw_path}") from exc
        source_files[name] = SourceFile(raw_path, lines)
    return source_files


def parse_line_ranges(raw_ranges: str) -> tuple[tuple[int, int], ...]:
    ranges: list[tuple[int, int]] = []
    for raw_range in raw_ranges.split(","):
        bounds = raw_range.split("-", 1)
        start = int(bounds[0])
        end = int(bounds[-1])
        if start < 1 or start > end:
            raise ValidationFailure("invalid-source-evidence", f"invalid source range: {raw_ranges}")
        ranges.append((start, end))
    return tuple(ranges)


def validate_reference(feature_id: str, stage: int, reference: JsonObject, sources: dict[str, SourceFile]) -> None:
    source_name = reference.get("source")
    raw_ranges = reference.get("lines")
    anchor = reference.get("anchor")
    if not isinstance(source_name, str) or not isinstance(raw_ranges, str) or not isinstance(anchor, str):
        raise ValidationFailure("invalid-source-evidence", f"incomplete evidence for {feature_id} stage {stage}")
    source = sources.get(source_name)
    if source is None:
        raise ValidationFailure("invalid-source-evidence", f"unknown evidence source for {feature_id} stage {stage}")
    ranges = parse_line_ranges(raw_ranges)
    if any(end > len(source.lines) for _, end in ranges):
        raise ValidationFailure("invalid-source-evidence", f"out-of-range evidence for {feature_id} stage {stage}")
    cited = "\n".join(line for start, end in ranges for line in source.lines[start - 1 : end])
    if anchor not in cited:
        raise ValidationFailure("invalid-source-evidence", f"ungrounded anchor for {feature_id} stage {stage}")


def issue(feature: str, reason: str, stage: int | None = None) -> JsonObject:
    result: JsonObject = {"feature": feature, "reason": reason}
    if stage is not None:
        result["stage"] = stage
    return result


def evaluate_feature(feature: JsonObject, sources: dict[str, SourceFile]) -> tuple[JsonObject, list[JsonObject]]:
    feature_id = feature["id"]
    active = feature["active"]
    stages = feature["stages"]
    if not isinstance(feature_id, str) or not isinstance(active, bool) or not isinstance(stages, list):
        raise ValidationFailure("schema-validation-failed", "feature is incomplete")
    stage_by_number: dict[int, JsonObject] = {}
    errors: list[JsonObject] = []
    for item in stages:
        if not isinstance(item, dict) or not isinstance(item.get("stage"), int):
            raise ValidationFailure("schema-validation-failed", f"invalid stage in {feature_id}")
        stage = item["stage"]
        if stage in stage_by_number:
            errors.append(issue(feature_id, "duplicate-stage", stage))
        stage_by_number[stage] = item
        evidence = item.get("source_evidence")
        if not isinstance(evidence, list):
            raise ValidationFailure("schema-validation-failed", f"invalid evidence in {feature_id}")
        for reference in evidence:
            if not isinstance(reference, dict):
                raise ValidationFailure("invalid-source-evidence", f"invalid evidence in {feature_id} stage {stage}")
            validate_reference(feature_id, stage, reference, sources)
    selected = [stage for stage, item in stage_by_number.items() if item.get("status") == "selected"]
    if active and set(stage_by_number) != set(STAGES):
        errors.append(issue(feature_id, "missing-or-unknown-stage"))
    if active and len(selected) != 1:
        errors.append(issue(feature_id, "duplicate-selection"))
    selected_stage = selected[0] if len(selected) == 1 else None
    if active and selected_stage is not None:
        for stage in range(1, selected_stage):
            prior = stage_by_number.get(stage)
            if prior is None or prior.get("status") not in {"not-applicable", "unavailable"} or not prior.get("source_evidence"):
                errors.append(issue(feature_id, f"missing-stage-1..{selected_stage - 1}-evidence", stage))
    return {
        "id": feature_id,
        "active": active,
        "selected_stage": selected_stage,
        "selected_stage_count": len(selected),
        "prior_stage_evidence_complete": not any(
            isinstance(error["reason"], str) and error["reason"].startswith("missing-stage-") for error in errors
        ),
    }, errors


def evaluate(matrix: JsonObject) -> JsonObject:
    sources = verified_sources(matrix)
    features = matrix["features"]
    if not isinstance(features, list):
        raise ValidationFailure("schema-validation-failed", "features must be an array")
    reports: list[JsonObject] = []
    errors: list[JsonObject] = []
    for feature in features:
        if not isinstance(feature, dict):
            raise ValidationFailure("schema-validation-failed", "feature must be an object")
        report, feature_errors = evaluate_feature(feature, sources)
        reports.append(report)
        errors.extend(feature_errors)
    active = [report for report in reports if report["active"]]
    if errors:
        reason = str(errors[0]["reason"])
        return {"format_version": 1, "reason": reason, "active_feature_count": len(active), "features": reports, "errors": errors}
    return {
        "format_version": 1,
        "reason": "validation_surfaces_selected",
        "active_feature_count": len(active),
        "features": reports,
        "sources": {name: source.path for name, source in sources.items()},
    }


def write_json(path: Path, report: JsonObject) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select a GIC-720AE validation surface from a fail-closed ledger.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--matrix", type=Path)
    group.add_argument("--self-test-negative", type=Path)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    matrix_path = args.matrix if args.matrix is not None else args.self_test_negative
    if matrix_path is None:
        raise AssertionError("argparse requires a matrix")
    try:
        matrix = load_yaml(matrix_path)
        schema = load_schema(args.schema)
        validate_schema(matrix, schema)
        report = evaluate(matrix)
        write_json(args.output, report)
        if report["reason"] != "validation_surfaces_selected":
            print(json.dumps({"status": "fail", "reason": report["reason"]}, sort_keys=True), file=sys.stderr)
            return 1
        print(json.dumps({"status": "pass", "output": str(args.output)}, sort_keys=True))
        return 0
    except ValidationFailure as exc:
        report = {"format_version": 1, "reason": exc.reason, "detail": exc.detail}
        write_json(args.output, report)
        print(json.dumps({"status": "fail", "reason": exc.reason}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
