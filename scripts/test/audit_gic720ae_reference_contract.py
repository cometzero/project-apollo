#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import stat
import sys
from typing import Final, TypedDict

import jsonschema


ROOT: Final = Path(__file__).resolve().parents[2]
PARAMETER: Final = re.compile(r"^([A-Za-z0-9_.-]+)=([^\s#]*)")
SHA256: Final = re.compile(r"^[0-9a-f]{64}$")


class InputError(RuntimeError):
    def __init__(self, reason: str, detail: str) -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(detail)


class Row(TypedDict):
    name: str
    classification: str
    expected: str | int
    observed: str | int | None
    passed: bool
    detail: str


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def provenance_digest(executable: dict[str, object], descriptor_exec_path: str, commands: list[object]) -> str:
    value = {"executable": executable, "descriptor_exec_path": descriptor_exec_path, "commands": commands}
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def write_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path, reason: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise InputError(reason, f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise InputError(reason, f"JSON object required: {path}")
    return value


def parse_parameters(text: str) -> dict[str, str]:
    values = {match.group(1): match.group(2) for line in text.splitlines() if (match := PARAMETER.match(line))}
    if not values:
        raise InputError("invalid_introspection", "introspection contains no parameter assignments")
    return values


def integer(parameters: dict[str, str], key: str) -> int | None:
    raw = parameters.get(key)
    if raw is None:
        return None
    try:
        return int(raw, 0)
    except ValueError:
        return None


def row(name: str, classification: str, expected: str | int, observed: str | int | None, detail: str) -> Row:
    return {"name": name, "classification": classification, "expected": expected, "observed": observed, "passed": observed == expected, "detail": detail}


def regular_bytes(path: Path) -> bytes:
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise InputError("invalid_introspection_receipt", f"receipt artifact is missing: {path}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise InputError("invalid_introspection_receipt", f"receipt artifact is not a regular file: {path}")
    return path.read_bytes()


def valid_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def verify_command(command: object, argument: str, receipt_dir: Path, executable: str, descriptor_exec_path: str) -> None:
    if not isinstance(command, dict):
        raise InputError("invalid_introspection_receipt", "receipt command is not an object")
    argv = command.get("argv")
    exec_argv = command.get("exec_argv")
    env = command.get("env")
    if not isinstance(argv, list) or len(argv) != 2 or not all(isinstance(item, str) for item in argv) or argv != [executable, argument]:
        raise InputError("invalid_introspection_receipt", f"receipt argv is invalid for {argument}")
    if not isinstance(exec_argv, list) or len(exec_argv) != 2 or not all(isinstance(item, str) for item in exec_argv) or exec_argv != [descriptor_exec_path, argument]:
        raise InputError("invalid_introspection_receipt", f"receipt exec argv is invalid for {argument}")
    if command.get("cwd") != str(ROOT):
        raise InputError("invalid_introspection_receipt", f"receipt cwd is invalid for {argument}")
    if not isinstance(env, dict) or set(env) != {"LC_ALL", "LANG", "PATH"} or env.get("LC_ALL") != "C" or env.get("LANG") != "C" or not isinstance(env.get("PATH"), str):
        raise InputError("invalid_introspection_receipt", f"receipt env allowlist is invalid for {argument}")
    started = valid_timestamp(command.get("started_at_utc"))
    ended = valid_timestamp(command.get("ended_at_utc"))
    if started is None or ended is None or ended < started:
        raise InputError("invalid_introspection_receipt", f"receipt timestamps are invalid for {argument}")
    if command.get("exit_code") != 0:
        raise InputError("invalid_introspection_receipt", f"receipt exit code is invalid for {argument}")
    name = argument.removeprefix("--")
    for stream in ("stdout", "stderr"):
        path_key = f"{stream}_path"
        hash_key = f"{stream}_sha256"
        if command.get(path_key) != f"{name}.{stream}" or not isinstance(command.get(hash_key), str) or SHA256.fullmatch(command[hash_key]) is None:
            raise InputError("invalid_introspection_receipt", f"receipt {stream} provenance is invalid for {argument}")
        if digest(regular_bytes(receipt_dir / command[path_key])) != command[hash_key]:
            raise InputError("invalid_introspection_receipt", f"receipt {stream} hash drifted for {argument}")


def verify_receipt(receipt_path: Path, introspection: bytes) -> dict[str, object]:
    receipt = load_json(receipt_path, "invalid_introspection_receipt")
    schema = load_json(ROOT / "tests/schemas/gic720ae-fvp-introspection.schema.json", "invalid_schema")
    try:
        jsonschema.validate(receipt, schema)
    except jsonschema.ValidationError as exc:
        raise InputError("invalid_introspection_receipt", f"receipt schema validation failed: {exc.message}") from exc
    commands = receipt.get("commands")
    executable = receipt.get("executable")
    descriptor_exec_path = receipt.get("descriptor_exec_path")
    summary = receipt.get("introspection")
    if not isinstance(commands, list) or not isinstance(executable, dict) or not isinstance(descriptor_exec_path, str) or not re.fullmatch(r"/proc/self/fd/[0-9]+", descriptor_exec_path) or not isinstance(summary, dict):
        raise InputError("invalid_introspection_receipt", "receipt lacks executable, commands, or introspection object")
    if valid_timestamp(receipt.get("captured_at_utc")) is None:
        raise InputError("invalid_introspection_receipt", "receipt capture timestamp is invalid")
    expected = ["--version", "--list-instances", "--list-params"]
    if len(commands) != len(expected):
        raise InputError("invalid_introspection_receipt", "receipt command count is invalid")
    if not isinstance(executable.get("realpath"), str):
        raise InputError("invalid_introspection_receipt", "receipt executable path is invalid")
    for command, argument in zip(commands, expected, strict=True):
        verify_command(command, argument, receipt_path.parent, executable["realpath"], descriptor_exec_path)
    if not isinstance(executable.get("input_path"), str) or not isinstance(executable.get("realpath"), str) or not isinstance(executable.get("sha256"), str) or SHA256.fullmatch(executable["sha256"]) is None or not isinstance(receipt.get("version"), str) or not receipt["version"].strip():
        raise InputError("invalid_introspection_receipt", "receipt has no fixed executable identity or version")
    executable_path = Path(executable["realpath"])
    if executable_path != Path(executable["input_path"]).resolve() or digest(regular_bytes(executable_path)) != executable["sha256"]:
        raise InputError("invalid_introspection_receipt", "receipt executable identity drifted")
    if not isinstance(receipt.get("provenance_sha256"), str) or SHA256.fullmatch(receipt["provenance_sha256"]) is None or receipt["provenance_sha256"] != provenance_digest(executable, descriptor_exec_path, commands):
        raise InputError("invalid_introspection_receipt", "receipt command provenance drifted")
    version_command = commands[0]
    if not isinstance(version_command, dict) or receipt["version"] != regular_bytes(receipt_path.parent / "version.stdout").decode("utf-8", errors="replace"):
        raise InputError("invalid_introspection_receipt", "receipt version output drifted")
    if summary.get("path") != "fvp-gic-introspection.txt" or summary.get("bytes") != len(introspection) or summary.get("sha256") != digest(introspection):
        raise InputError("invalid_introspection_receipt", "introspection SHA does not match receipt")
    return receipt


def audit(parameters: dict[str, str], contract: dict[str, object]) -> list[Row]:
    expected = contract.get("expected")
    collator = contract.get("collator")
    if not isinstance(expected, dict) or not isinstance(collator, dict):
        raise InputError("invalid_contract", "contract lacks expected or collator sections")
    ap = expected.get("ap")
    si = expected.get("si")
    inactive = expected.get("inactive")
    if not isinstance(ap, dict) or not isinstance(si, dict) or not isinstance(inactive, dict):
        raise InputError("invalid_contract", "contract expected sections are malformed")
    ap_prefix = "css.gic_distributor."
    si_prefix = "css.smb.si.gic."
    ap_spi_blocks = integer(parameters, ap_prefix + "SPI-blocks")
    si_spi_blocks = integer(parameters, si_prefix + "SPI-blocks")
    affinities = parameters.get(si_prefix + "CPU-affinities")
    si_pe = None if affinities is None else len([item for item in affinities.split(",") if item])
    rows = [
        row("AP SPI", "active", int(ap["spi_blocks"]) * 32, None if ap_spi_blocks is None else ap_spi_blocks * 32, "SPI blocks times 32"),
        row("AP PPI", "active", int(ap["ppi"]), integer(parameters, ap_prefix + "PPI-count"), "PPI-count"),
        row("AP EPPI", "active", int(ap["eppi"]), integer(parameters, ap_prefix + "extended-ppi-count"), "extended-ppi-count"),
        row("AP ITS", "active", int(ap["its"]), integer(parameters, ap_prefix + "ITS-count"), "ITS-count"),
        row("AP IIDR", "active", int(ap["iidr"]), integer(parameters, ap_prefix + "IIDR"), "IIDR"),
        row("AP views", "active", int(ap["views"]), integer(parameters, ap_prefix + "enable-multiple-views-feature"), "multiple views"),
        row("SI SPI", "active", int(si["standard_spi_blocks"]) * 32, None if si_spi_blocks is None else min(si_spi_blocks, int(si["standard_spi_blocks"])) * 32, "standard SPI portion of combined blocks"),
        row("SI ESPI", "active", (int(si["spi_blocks"]) - int(si["standard_spi_blocks"])) * 32, None if si_spi_blocks is None else max(si_spi_blocks - int(si["standard_spi_blocks"]), 0) * 32, "remaining combined SPI blocks are ESPI"),
        row("SI PPI", "active", int(si["ppi"]), integer(parameters, si_prefix + "PPI-count"), "PPI-count"),
        row("SI EPPI", "active", int(si["eppi"]), integer(parameters, si_prefix + "extended-ppi-count"), "extended-ppi-count"),
        row("SI PE", "active", int(si["pe"]), si_pe, "CPU-affinities entries"),
        row("SI IIDR", "active", int(si["iidr"]), integer(parameters, si_prefix + "IIDR"), "IIDR"),
        row("A4S", "inactive", int(inactive["a4s"]), integer(parameters, "css.cmn.enable_a4s"), "CMN A4S routing"),
        row("Fast Models consolidators AP", "inactive", str(inactive["consolidators"]), parameters.get(ap_prefix + "consolidators"), "Fast Models parameter only"),
        row("Fast Models consolidators SI", "inactive", str(inactive["consolidators"]), parameters.get(si_prefix + "consolidators"), "Fast Models parameter only"),
        row("wake outputs AP", "inactive", int(inactive["wake"]), integer(parameters, ap_prefix + "add-output-cpu-wake-request-signal-from-redistributor"), "redistributor wake output"),
        row("wake outputs SI", "inactive", int(inactive["wake"]), integer(parameters, si_prefix + "add-output-cpu-wake-request-signal-from-redistributor"), "redistributor wake output"),
        row("NMI AP", "inactive", int(inactive["nmi"]), integer(parameters, ap_prefix + "has_nmi"), "NMI parameter"),
        row("NMI SI", "inactive", int(inactive["nmi"]), integer(parameters, si_prefix + "has_nmi"), "NMI parameter"),
        row("invalidate AP", "inactive", int(inactive["invalidate"]), integer(parameters, ap_prefix + "GICR-invalidate-registers-implemented"), "redistributor invalidate block"),
        row("invalidate SI", "inactive", int(inactive["invalidate"]), integer(parameters, si_prefix + "GICR-invalidate-registers-implemented"), "redistributor invalidate block"),
        row("SPI Collator", str(collator["classification"]), str(collator["status"]), str(collator["status"]), "No active message path is inferred before Task 33 controlled preflight."),
    ]
    return rows


def self_test_parameters(path: Path) -> dict[str, str]:
    fixture = load_json(path, "invalid_negative_fixture")
    raw = fixture.get("parameters")
    if not isinstance(raw, dict) or not all(isinstance(key, str) and isinstance(value, str) for key, value in raw.items()):
        raise InputError("invalid_negative_fixture", "negative fixture parameters must be strings")
    baseline = {
        "css.gic_distributor.SPI-blocks": "30", "css.gic_distributor.PPI-count": "16", "css.gic_distributor.extended-ppi-count": "0", "css.gic_distributor.ITS-count": "1", "css.gic_distributor.IIDR": "117445691", "css.gic_distributor.enable-multiple-views-feature": "1", "css.gic_distributor.consolidators": "", "css.gic_distributor.add-output-cpu-wake-request-signal-from-redistributor": "0", "css.gic_distributor.has_nmi": "0", "css.gic_distributor.GICR-invalidate-registers-implemented": "0", "css.smb.si.gic.SPI-blocks": "62", "css.smb.si.gic.PPI-count": "16", "css.smb.si.gic.extended-ppi-count": "64", "css.smb.si.gic.CPU-affinities": "0.0.0.0,0.1.0.0,0.1.1.0,0.1.2.0,0.1.3.0", "css.smb.si.gic.IIDR": "117445691", "css.smb.si.gic.enable-multiple-views-feature": "1", "css.smb.si.gic.consolidators": "", "css.smb.si.gic.add-output-cpu-wake-request-signal-from-redistributor": "0", "css.smb.si.gic.has_nmi": "0", "css.smb.si.gic.GICR-invalidate-registers-implemented": "0", "css.cmn.enable_a4s": "0",
    }
    return {**baseline, **raw}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the Apollo cfg2 GIC-720AE reference contract.")
    parser.add_argument("--introspection", type=Path)
    parser.add_argument("--introspection-receipt", type=Path)
    parser.add_argument("--self-test-negative", type=Path)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        contract = load_json(args.contract, "invalid_contract")
        if args.self_test_negative is not None:
            parameters = self_test_parameters(args.self_test_negative)
        elif args.introspection is not None and args.introspection_receipt is not None:
            introspection = args.introspection.read_bytes()
            verify_receipt(args.introspection_receipt, introspection)
            parameters = parse_parameters(introspection.decode("utf-8", errors="strict"))
        else:
            raise InputError("invalid_arguments", "provide introspection plus receipt, or --self-test-negative")
        rows = audit(parameters, contract)
        reason = "reference_contract_pass" if all(item["passed"] for item in rows) else "reference_contract_drift"
        report: dict[str, object] = {"format_version": 1, "reason": reason, "rows": rows}
        schema = load_json(ROOT / "tests/schemas/gic720ae-reference-contract.schema.json", "invalid_schema")
        jsonschema.validate(report, schema)
        write_json(args.output, report)
        print(json.dumps({"reason": reason, "output": str(args.output)}, sort_keys=True))
        return 0 if reason == "reference_contract_pass" else 1
    except (InputError, UnicodeDecodeError, jsonschema.ValidationError) as exc:
        reason = exc.reason if isinstance(exc, InputError) else "invalid_input"
        report = {"format_version": 1, "reason": reason, "detail": str(exc)}
        write_json(args.output, report)
        print(json.dumps(report, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
