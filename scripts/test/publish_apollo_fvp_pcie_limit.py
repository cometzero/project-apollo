#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Final

import jsonschema

from apollo_fvp_pcie_limit_manifest import FIXTURE_ROOT, MANIFEST_SHA256, ManifestError, hash_file
from validate_apollo_fvp_pcie_limit import LimitError, JsonObject, JsonValue, load_object, validate as validate_limit

ROOT: Final = Path(__file__).resolve().parents[2]
SCHEMA: Final = ROOT / "tests/schemas/apollo-fvp-pcie-limit-producer.schema.json"


@dataclass(frozen=True, slots=True)
class ProducerError(Exception):
    reason: str

    def __str__(self) -> str:
        return self.reason


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ProducerError(reason)


def object_value(value: JsonValue, reason: str) -> JsonObject:
    if not isinstance(value, dict):
        raise ProducerError(reason)
    return value


def list_value(value: JsonValue, reason: str) -> list[JsonValue]:
    if not isinstance(value, list):
        raise ProducerError(reason)
    return value


def string_value(value: JsonValue, reason: str) -> str:
    if not isinstance(value, str):
        raise ProducerError(reason)
    return value


def raw_fields(raw: JsonObject, expected_argv_hash: str) -> JsonObject:
    require(raw.get("status") == "fail" and raw.get("reason") == "canonical_runner_failed", "raw_status")
    require(raw.get("configuration_applied") is True and raw.get("qbox_started") is False, "raw_configuration")
    detail = object_value(raw.get("detail"), "raw_detail")
    require(detail.get("runner_rc") == -2, "raw_child_rc")
    processes = list_value(detail.get("observed_fvp_processes"), "raw_process")
    require(len(processes) == 1, "raw_process")
    argv = list_value(object_value(processes[0], "raw_process").get("argv"), "raw_argv")
    values = [string_value(value, "raw_argv") for value in argv]
    argv_hash = hashlib.sha256(json.dumps(values, separators=(",", ":")).encode()).hexdigest()
    require(argv_hash == expected_argv_hash, "raw_argv")
    return {"status": "fail", "reason": "canonical_runner_failed", "runner_rc": -2, "fvp_argv_sha256": argv_hash}


def publish() -> JsonObject:
    limit = validate_limit()
    runtime = load_object(FIXTURE_ROOT / "runtime-result.json")
    limit_runtime = object_value(limit.get("runtime"), "limit_runtime")
    raw = raw_fields(runtime, string_value(limit_runtime.get("fvp_argv_sha256"), "limit_runtime"))
    return {"schema_version": 1, "reference_gate": "PASS", "fvp_qualification": "UNSUPPORTED", "qbox_allowed": True, "reason": "immutable_ecam_limit", "configuration_applied": True, "qbox_started": False, "hashes": {"manifest_sha256": MANIFEST_SHA256, "limit_receipt_sha256": hashlib.sha256(json.dumps(limit, sort_keys=True, separators=(",", ":")).encode()).hexdigest(), "raw_result_sha256": hash_file(FIXTURE_ROOT / "runtime-result.json")}, "raw": raw, "cleanup": {"status": "PASS", "qbox_started": False}, "claims": {"physical_its_delivery": False, "endpoint_enumeration": False, "qbox_equivalence": False}}


def failure(reason: str) -> JsonObject:
    return {"schema_version": 1, "reference_gate": "FAIL", "fvp_qualification": "UNSUPPORTED", "qbox_allowed": False, "reason": reason, "configuration_applied": False, "qbox_started": False, "hashes": {"manifest_sha256": "0" * 64, "limit_receipt_sha256": "0" * 64, "raw_result_sha256": "0" * 64}, "raw": {"status": "unknown", "reason": reason, "runner_rc": -1, "fvp_argv_sha256": "0" * 64}, "cleanup": {"status": "FAIL", "qbox_started": False}, "claims": {"physical_its_delivery": False, "endpoint_enumeration": False, "qbox_equivalence": False}}


def write_atomic(path: Path, payload: JsonObject) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, encoding="utf-8", delete=False) as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
        temporary = Path(stream.name)
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish the offline Apollo FVP PCIe ECAM limitation gate")
    parser.add_argument("--schema", type=Path, default=SCHEMA)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        require(args.schema.absolute() == SCHEMA, "schema_path")
        payload = publish()
        jsonschema.Draft202012Validator(load_object(args.schema)).validate(payload)
    except (ProducerError, ManifestError, LimitError, jsonschema.ValidationError, OSError) as error:
        reason = error.reason if isinstance(error, (ProducerError, ManifestError, LimitError)) else "schema"
        payload = failure(reason)
    write_atomic(args.output, payload)
    return 0 if payload["reference_gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
