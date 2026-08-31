#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Final

import jsonschema

from apollo_fvp_pcie_limit_manifest import FIXTURE_ROOT, MANIFEST_PATH, MANIFEST_SHA256, ManifestError, load_manifest, verify_inputs

ROOT: Final = Path(__file__).resolve().parents[2]
EXPECTED_PROFILE_SHA: Final = "5ef9fa5f0c7720ab635bbcc24903ced40d4d4ae8261b3b692adf3fbbf8b044bf"
EXPECTED_FVPCONF_SHA: Final = "939f75887144826e9779d0fee244162e5a5a3250fb0bd9edddcd805837ba0b7a"
EXPECTED_FVP_SHA: Final = "28b63033b06f083b74fcf954ac05cd0f2bd8fcc6babac0bdc5cecd0159f96c05"
EXPECTED_ESR: Final = "0x00000000be000211"
EXPECTED_ELR: Final = "0xffff8000807d08f0"
EXPECTED_ECAM: Final = "0x10040000000"
EXPECTED_ENDPOINT: Final = "0004:00:1f.0"
type JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
type JsonObject = dict[str, JsonValue]


@dataclass(frozen=True, slots=True)
class LimitError(Exception):
    reason: str

    def __str__(self) -> str:
        return self.reason


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise LimitError(reason)


def object_value(value: JsonValue, reason: str) -> JsonObject:
    if not isinstance(value, dict):
        raise LimitError(reason)
    return value


def list_value(value: JsonValue, reason: str) -> list[JsonValue]:
    if not isinstance(value, list):
        raise LimitError(reason)
    return value


def string_value(value: JsonValue, reason: str) -> str:
    if not isinstance(value, str):
        raise LimitError(reason)
    return value


def load_object(path: Path) -> JsonObject:
    try:
        value: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LimitError("malformed_input") from error
    return object_value(value, "malformed_input")


def text(name: str) -> str:
    return (FIXTURE_ROOT / name).read_text(encoding="utf-8")


def parameters(argv: list[JsonValue]) -> set[str]:
    values = [string_value(value, "argv") for value in argv]
    return {values[index + 1] for index, token in enumerate(values[:-1]) if token == "--parameter"}


def validate() -> JsonObject:
    manifest = load_manifest(MANIFEST_PATH)
    inputs = verify_inputs(manifest)
    identity = load_object(FIXTURE_ROOT / "source-identity.json")
    binary = object_value(identity.get("binary"), "identity")
    require(binary.get("name") == "FVP_Zena_CSS_Cfg2" and binary.get("sha256") == EXPECTED_FVP_SHA, "identity")
    require(identity.get("profile_sha256") == EXPECTED_PROFILE_SHA and identity.get("fvpconf_sha256") == EXPECTED_FVPCONF_SHA, "identity")
    profile = load_object(FIXTURE_ROOT / "profile.json")
    configuration = object_value(profile.get("configuration"), "profile")
    require(profile.get("machine") == "apollo-fvp" and configuration == {"its_count": 1, "pcie_hierarchy": "<default>", "pcie_ats_supported": True}, "profile")
    runtime = load_object(FIXTURE_ROOT / "runtime-result.json")
    require(runtime.get("status") == "fail" and runtime.get("reason") == "canonical_runner_failed", "runtime")
    require(runtime.get("configuration_applied") is True and runtime.get("qbox_started") is False, "runtime")
    detail = object_value(runtime.get("detail"), "runtime")
    require(detail.get("configuration_applied") is True and detail.get("runner_rc") == -2, "runtime")
    processes = list_value(detail.get("observed_fvp_processes"), "runtime")
    require(len(processes) == 1, "pid_argv")
    process = object_value(processes[0], "pid_argv")
    require(process.get("pid") == 1493733, "pid_argv")
    argv = list_value(process.get("argv"), "pid_argv")
    require(string_value(argv[0], "pid_argv") == binary["name"], "pid_argv")
    required = {"css.gic_distributor.ITS-count=1", "pcie_group_0.pcie4.hierarchy_file_name=<default>", "pcie_group_0.pcie4.pcie_rc.ahci0.endpoint.ats_supported=true"}
    require(required <= parameters(argv), "configuration")
    fvpconf, scp, ns, secure, process_log, outcome, cleanup, boundary = (text(name) for name in ("fvpconf.excerpt", "scp.log", "ns.log", "secure.log", "process.log", "outcome.txt", "cleanup.txt", "source-boundary.txt"))
    require("css.gic_distributor.ITS-count=1" in fvpconf and "pcie_group_0.pcie4.hierarchy_file_name=<default>" in fvpconf and "pcie_group_0.pcie4.pcie_rc.ahci0.endpoint.ats_supported=true" in fvpconf, "fvpconf")
    require(scp.count("RNSAM setup complete") == 1, "scp")
    require("ITS@0x0000000020840000:" in ns and ns.count("PCI host bridge to bus 0004:00") == 1, "root_bus")
    require(re.search(r"\b0004:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7]\b", ns) is None, "endpoint_present")
    require("RAS: Uncontainable RAS Error Handler (EL3)" in secure and secure.count(f"esr_el3        = {EXPECTED_ESR}") == 1 and secure.count(f"elr_el3        = {EXPECTED_ELR}") == 1, "serror_tuple")
    require(f"cfg_start={EXPECTED_ECAM}" in process_log and "cfg_end=0x1004fffffff" in process_log and outcome.strip() == "same_root_bus_serror", "ecam_address")
    require("remaining_observed_fvp=0" in cleanup and "qbox_started=false" in cleanup, "cleanup")
    require("No editable Fast Models platform project was found" in boundary and "proprietary" in boundary, "source_boundary")
    return {"schema_version": 1, "reference_gate": "PASS", "fvp_qualification": "UNSUPPORTED", "qbox_allowed": True, "reason": "immutable_ecam_limit", "source_boundary": "prebuilt_fvp_source_unavailable", "tuple": {"ecam": EXPECTED_ECAM, "esr_el3": EXPECTED_ESR, "elr_el3": EXPECTED_ELR, "endpoint": EXPECTED_ENDPOINT}, "claims": {"physical_its_delivery": False, "endpoint_enumeration": False, "qbox_equivalence": False}, "runtime": {"profile_sha256": EXPECTED_PROFILE_SHA, "fvp_argv_sha256": hashlib.sha256(json.dumps(argv, separators=(",", ":")).encode()).hexdigest()}, "manifest_sha256": MANIFEST_SHA256, "inputs": inputs, "profile_fvp_path": string_value(binary.get("name"), "identity")}


def write_atomic(path: Path, payload: JsonObject) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, encoding="utf-8", delete=False) as stream:
        json.dump(payload, stream, sort_keys=True, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the immutable offline Apollo FVP PCIe ECAM limitation")
    parser.add_argument("--schema", type=Path, default=ROOT / "tests/schemas/apollo-fvp-pcie-limit.schema.json")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        payload = validate()
        jsonschema.Draft202012Validator(load_object(args.schema)).validate(payload)
    except (LimitError, ManifestError, jsonschema.ValidationError, OSError) as error:
        reason = error.reason if isinstance(error, (LimitError, ManifestError)) else "schema"
        payload = {"schema_version": 1, "reference_gate": "FAIL", "fvp_qualification": "UNSUPPORTED", "qbox_allowed": False, "reason": reason, "source_boundary": "prebuilt_fvp_source_unavailable", "claims": {"physical_its_delivery": False, "endpoint_enumeration": False, "qbox_equivalence": False}, "inputs": {}}
    write_atomic(args.output, payload)
    return 0 if payload["reference_gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
