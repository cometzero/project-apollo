#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
from collections.abc import Mapping, Sequence
from typing import Final, TypeAlias

import jsonschema


ROOT: Final = Path(__file__).resolve().parents[2]
COMMANDS: Final = ("--version", "--list-instances", "--list-params")
TIMEOUT_SECONDS: Final = 30
PCI_PREFIX: Final = "pcie_group_0.pcie4"
JsonValue: TypeAlias = (
    str | int | float | bool | None | Sequence["JsonValue"] | Mapping[str, "JsonValue"]
)
ModelObject: TypeAlias = dict[str, str | bool]
ModelObjects: TypeAlias = dict[str, ModelObject]
ModelParameters: TypeAlias = dict[str, dict[str, str]]
TopologyFile: TypeAlias = dict[str, str | bool | None]
AddressMap: TypeAlias = dict[str, dict[str, str]]


@dataclass(frozen=True, slots=True)
class InputError(Exception):
    reason: str
    detail: str

    def __str__(self) -> str:
        return self.detail


@dataclass(frozen=True, slots=True)
class CommandRecord:
    argv: list[str]
    exit_code: int
    stdout_sha256: str
    stderr_sha256: str


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    try:
        return sha256_bytes(path.read_bytes())
    except FileNotFoundError as exc:
        raise InputError("missing_input", f"missing input: {path}") from exc


def timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds")


def load_json_object(path: Path, reason: str) -> dict[str, JsonValue]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InputError(reason, f"missing JSON input: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(reason, f"invalid JSON input: {path}") from exc
    if not isinstance(value, dict):
        raise InputError(reason, f"JSON input must be an object: {path}")
    return value


def string_map(value: JsonValue, label: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise InputError("malformed_input", f"{label} must be an object")
    result: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not isinstance(item, str):
            raise InputError("malformed_input", f"{label} must contain string keys and values")
        result[key] = item
    return result


def command(fvp: Path, argument: str) -> tuple[CommandRecord, str]:
    try:
        process = subprocess.Popen(
            [str(fvp), argument],
            cwd=ROOT,
            env={"LC_ALL": "C", "LANG": "C", "PATH": os.environ.get("PATH", "")},
            start_new_session=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError as exc:
        raise InputError("command_failed", f"cannot start FVP {argument}: {fvp}") from exc
    try:
        stdout, stderr = process.communicate(timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as exc:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise InputError("command_timeout", f"FVP metadata command timed out: {argument}") from exc
    record = CommandRecord(
        argv=[str(fvp), argument],
        exit_code=process.returncode,
        stdout_sha256=sha256_bytes(stdout.encode("utf-8")),
        stderr_sha256=sha256_bytes(stderr.encode("utf-8")),
    )
    if process.returncode != 0:
        raise InputError("command_failed", f"FVP metadata command failed: {argument}")
    if not stdout.strip():
        raise InputError("empty_output", f"FVP metadata command produced no output: {argument}")
    return record, stdout


def model_objects(instances: str) -> ModelObjects:
    required = {
        "pcie4": (f"{PCI_PREFIX}", "BasePlatformPCISBSA"),
        "pci_smmu": (f"{PCI_PREFIX}.pci_smmuv3", "SMMUv3_FOR_PCIE"),
        "msi_rewriter": (f"{PCI_PREFIX}.pci_smmuv3_msirewriter", "MSIRewriter"),
        "root_complex": (f"{PCI_PREFIX}.pcie_rc", "PCIeRootComplex"),
        "ahci0": (f"{PCI_PREFIX}.pcie_rc.ahci0.ahci", "AHCI_SATA"),
    }
    result: ModelObjects = {}
    for name, (path, component) in required.items():
        matching = next((line for line in instances.splitlines() if path in line and component in line), "")
        result[name] = {"path": path, "component": component, "present": bool(matching)}
    return result


def model_parameters(params: str) -> ModelParameters:
    selected = (
        "css.gic_distributor.ITS-count",
        f"{PCI_PREFIX}.hierarchy_file_name",
        f"{PCI_PREFIX}.pcie_rc.ahci0.endpoint.ats_supported",
        f"{PCI_PREFIX}.pcie_rc.ahci0.endpoint.msix_support",
        f"{PCI_PREFIX}.pcie_rc.ahci0.endpoint.uses_interrupt",
        f"{PCI_PREFIX}.pcie_rc.ahci0.ahci.image_path",
        f"{PCI_PREFIX}.cfg_start",
        f"{PCI_PREFIX}.cfg_end",
        f"{PCI_PREFIX}.mem0_start",
        f"{PCI_PREFIX}.mem0_end",
        f"{PCI_PREFIX}.mem1_start",
        f"{PCI_PREFIX}.mem1_end",
    )
    result: ModelParameters = {}
    for line in params.splitlines():
        for key in selected:
            if not line.startswith(f"{key}="):
                continue
            current, _, comment = line.partition(" #")
            value = current.removeprefix(f"{key}=").strip()
            default_match = re.search(r"default = '([^']*)'", comment)
            if default_match is None:
                raise InputError("malformed_model_output", f"missing declared default for {key}")
            result[key] = {"current": value, "default": default_match.group(1)}
    missing = [key for key in selected if key not in result]
    if missing:
        raise InputError("malformed_model_output", f"missing model parameters: {', '.join(missing)}")
    return result


def require_declared_value(parameters: dict[str, str], key: str, expected: str) -> str:
    value = parameters.get(key)
    if value != expected:
        raise InputError("configuration_not_declared", f"missing or unexpected declared value for {key}")
    return expected


def topology_file(fvp: Path, name: str) -> TopologyFile:
    candidate = fvp.parent / name
    if not candidate.is_file():
        return {"name": name, "path": str(candidate), "present": False, "sha256": None}
    return {"name": name, "path": str(candidate.resolve()), "present": True, "sha256": sha256_file(candidate)}


def ap_visible_addresses(ni_topology: Path) -> AddressMap:
    if not ni_topology.is_file():
        return {}
    content = ni_topology.read_text(encoding="utf-8")
    values: AddressMap = {}
    for label, section in (("ecam_x1_1", "m_EXMAXI_PCIE1x_1_CFG_IO"), ("mmio_high_x1_1", "m_EXMACEL_PCIE1x_1_IO")):
        match = re.search(rf"{section}:\s*\n\s*startAddress:\s*(0x[0-9a-fA-F]+)\s*\n\s*endAddress:\s*(0x[0-9a-fA-F]+)", content)
        if match is not None:
            values[label] = {"start": match.group(1), "end": match.group(2), "source": "ni710AE_io_2.yaml"}
    return values


def write_json_atomic(path: Path, payload: dict[str, JsonValue]) -> None:
    if path.exists() or path.is_symlink():
        raise InputError("invalid_output", f"output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def capture(fvp: Path, fvpconf: Path, schema: Path) -> dict[str, JsonValue]:
    input_fvp = fvp
    fvp = fvp.resolve()
    if not fvp.is_file() or fvp.is_symlink():
        raise InputError("missing_input", f"FVP must resolve to a regular file: {input_fvp}")
    fvp_sha256_before = sha256_file(fvp)
    fvpconf_sha256_before = sha256_file(fvpconf)
    contract_schema = load_json_object(schema, "invalid_schema")
    config = load_json_object(fvpconf, "malformed_input")
    parameters = string_map(config.get("parameters"), "fvpconf parameters")
    records: list[CommandRecord] = []
    output: dict[str, str] = {}
    for argument in COMMANDS:
        record, stdout = command(fvp, argument)
        records.append(record)
        output[argument] = stdout
    if (
        sha256_file(fvp) != fvp_sha256_before
        or sha256_file(fvpconf) != fvpconf_sha256_before
    ):
        raise InputError("stale_state", "FVP binary or configuration changed during capture")
    objects = model_objects(output["--list-instances"])
    defaults = model_parameters(output["--list-params"])
    if not all(item["present"] for item in objects.values()):
        raise InputError("model_objects_missing", "required PCIe4 model objects are not compiled")
    msix_default = defaults[f"{PCI_PREFIX}.pcie_rc.ahci0.endpoint.msix_support"]["default"]
    intx_default = defaults[f"{PCI_PREFIX}.pcie_rc.ahci0.endpoint.uses_interrupt"]["default"]
    if msix_default != "1":
        raise InputError("model_contract_unproven", "AHCI MSI-X is not enabled by the model default")
    if intx_default != "0":
        raise InputError("model_contract_unproven", "AHCI legacy INTx is not disabled by the model default")
    hierarchy = require_declared_value(parameters, f"{PCI_PREFIX}.hierarchy_file_name", "<default>")
    ats = require_declared_value(parameters, f"{PCI_PREFIX}.pcie_rc.ahci0.endpoint.ats_supported", "true")
    image_path = require_declared_value(parameters, f"{PCI_PREFIX}.pcie_rc.ahci0.ahci.image_path", "")
    its_count = require_declared_value(parameters, "css.gic_distributor.ITS-count", "1")
    ni = topology_file(fvp, "ni710AE_io_2.yaml")
    cmn = topology_file(fvp, "rd_asd_cmn_cyprus.yml")
    component_local = {
        "ecam": {"start": defaults[f"{PCI_PREFIX}.cfg_start"]["default"], "end": defaults[f"{PCI_PREFIX}.cfg_end"]["default"], "source": "FVP model defaults"},
        "mmio_low": {"start": defaults[f"{PCI_PREFIX}.mem0_start"]["default"], "end": defaults[f"{PCI_PREFIX}.mem0_end"]["default"], "source": "FVP model defaults"},
        "mmio_high": {"start": defaults[f"{PCI_PREFIX}.mem1_start"]["default"], "end": defaults[f"{PCI_PREFIX}.mem1_end"]["default"], "source": "FVP model defaults"},
    }
    ni_path = Path(str(ni["path"]))
    payload: dict[str, JsonValue] = {
        "format_version": 1,
        "captured_at_utc": timestamp(),
        "fvp": {"input_path": str(input_fvp), "realpath": str(fvp), "sha256": fvp_sha256_before, "version": output["--version"].strip(), "commands": [asdict(record) for record in records]},
        "model": {"model_present": all(item["present"] for item in objects.values()), "objects": objects, "defaults": defaults},
        "configuration": {"configuration_declared": True, "fvpconf": {"path": str(fvpconf), "sha256": fvpconf_sha256_before}, "declared": {"hierarchy": hierarchy, "ats_supported": ats == "true", "its_count": int(its_count), "baseline_image_path": image_path}},
        "interrupt_contract": {"msix_supported": msix_default == "1", "legacy_intx_supported": intx_default == "1"},
        "address_maps": {"component_local": component_local, "ap_visible": ap_visible_addresses(ni_path)},
        "topology": {"files": [ni, cmn]},
    }
    try:
        jsonschema.Draft202012Validator.check_schema(contract_schema)
        jsonschema.Draft202012Validator(contract_schema).validate(payload)
    except jsonschema.SchemaError as exc:
        raise InputError("invalid_schema", exc.message) from exc
    except jsonschema.ValidationError as exc:
        raise InputError("result_schema_error", exc.message) from exc
    return payload


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture the configured Apollo-FVP PCIe4 model contract.")
    parser.add_argument("--fvp", required=True, type=Path)
    parser.add_argument("--fvpconf", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        payload = capture(args.fvp, args.fvpconf, args.schema)
        write_json_atomic(args.output, payload)
    except InputError as exc:
        print(json.dumps({"reason": exc.reason, "detail": exc.detail}, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps({"status": "pass", "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
