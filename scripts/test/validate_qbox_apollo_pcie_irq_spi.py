#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# ─── How to run ───
# python3 scripts/test/validate_qbox_apollo_pcie_irq_spi.py --help

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


PREFIX: Final = "APOLLO_SPI|"
HASH_RE: Final = re.compile(r"[0-9a-f]{64}")
JsonValue = str | int | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


@dataclass(frozen=True, slots=True)
class SpiError(Exception):
    reason: str

    def __str__(self) -> str:
        return self.reason


@dataclass(frozen=True, slots=True)
class Record:
    line: int
    fields: dict[str, str]


def parse_records(path: Path) -> tuple[list[Record], str]:
    raw = path.read_bytes()
    clean = (
        re.sub(rb"\x1b\[[0-?]*[ -/]*[@-~]", b"", raw)
        .decode("utf-8", errors="replace")
        .replace("\r", "")
    )
    records: list[Record] = []
    for line_number, line in enumerate(clean.splitlines(), 1):
        if not line.startswith(PREFIX):
            continue
        fields: dict[str, str] = {}
        for token in line[len(PREFIX) :].split("|"):
            if "=" not in token:
                raise SpiError("malformed_input")
            key, value = token.split("=", 1)
            if not key or not value or key in fields:
                raise SpiError("malformed_input")
            fields[key] = value
        records.append(Record(line_number, fields))
    if not records:
        raise SpiError("malformed_input")
    return records, hashlib.sha256(raw).hexdigest()


def one(records: list[Record], event: str, phase: str | None = None) -> Record:
    matches = [
        record
        for record in records
        if record.fields.get("event") == event
        and (phase is None or record.fields.get("phase") == phase)
    ]
    if len(matches) != 1:
        raise SpiError(event + "_missing")
    return matches[0]


def number(value: str, reason: str) -> int:
    try:
        return int(value, 0)
    except ValueError as error:
        raise SpiError(reason) from error


def counts(records: list[Record], phase: str) -> list[int]:
    values = one(records, "count", phase).fields.get("values", "")
    parsed = [number(value, "count_format") for value in values.split(",")]
    if len(parsed) < 2:
        raise SpiError("cpu_count")
    return parsed


def delta(before: list[int], after: list[int], reason: str) -> list[int]:
    if len(before) != len(after):
        raise SpiError("cpu_count")
    values = [end - start for start, end in zip(before, after, strict=True)]
    if any(value < 0 for value in values):
        raise SpiError(reason)
    return values


def validate(records: list[Record], digest: str) -> dict[str, JsonValue]:
    if not HASH_RE.fullmatch(digest):
        raise SpiError("input_hash")
    if any(record.fields.get("v") != "1" for record in records):
        raise SpiError("contract_version")
    contract = one(records, "contract")
    if (
        contract.fields.get("input_sha256") != digest
        or contract.fields.get("platform") != "qbox"
        or contract.fields.get("mode") != "spi"
    ):
        raise SpiError("contract")
    endpoint = one(records, "endpoint")
    expected_endpoint = {
        "bdf": "-",
        "driver": "virtio-mmio",
        "compatible": "virtio,mmio",
        "devpath": "/sys/bus/platform/devices/30060000.virtio",
    }
    if any(
        endpoint.fields.get(key) != value for key, value in expected_endpoint.items()
    ):
        raise SpiError("spi_endpoint")
    target = endpoint.fields.get("target", "")
    if not target:
        raise SpiError("spi_endpoint")
    pci_vector = one(records, "pci_vector")
    pci_virq = number(pci_vector.fields.get("virq", ""), "pci_vector")
    expected_owner = f"/sys/bus/pci/devices/0000:00:01.0/msi_irqs/{pci_virq}"
    if pci_vector.fields.get("owner") != expected_owner:
        raise SpiError("pci_vector")
    line_irq = one(records, "line_irq")
    spi_virq = number(line_irq.fields.get("virq", ""), "spi_irq")
    if line_irq.fields.get("owner") != expected_endpoint["devpath"]:
        raise SpiError("spi_irq")
    chain = one(records, "chain")
    if (
        chain.fields.get("virq") != str(spi_virq)
        or chain.fields.get("index") != "0"
        or chain.fields.get("domain") != "GICv3"
        or chain.fields.get("chip") != "GICv3"
        or number(chain.fields.get("hwirq", ""), "spi_hwirq") != 293
    ):
        raise SpiError("spi_hwirq")
    workload = one(records, "workload", "isolated")
    if workload.fields.get("target") != target or workload.fields.get("rc") != "0":
        raise SpiError("workload")
    spi_before = counts(records, "spi-before")
    pci_before = counts(records, "pci-before")
    spi_after = counts(records, "spi-after")
    pci_after = counts(records, "pci-after")
    spi_delta = delta(spi_before, spi_after, "spi_delta")
    pci_delta = delta(pci_before, pci_after, "pci_vector_delta")
    if spi_delta[0] <= 0 or any(value != 0 for value in spi_delta[1:]):
        raise SpiError("spi_delta")
    if any(pci_delta):
        raise SpiError("pci_vector_delta")
    cleanup = one(records, "cleanup")
    if (
        cleanup.fields.get("affinity_restored") != "1"
        or cleanup.fields.get("rc") != "0"
    ):
        raise SpiError("cleanup")
    final = one(records, "final")
    if (
        final.fields.get("status") != "complete"
        or final.fields.get("input_sha256") != digest
    ):
        raise SpiError("final")
    ordered = [
        contract.line,
        endpoint.line,
        pci_vector.line,
        line_irq.line,
        chain.line,
        one(records, "count", "spi-before").line,
        one(records, "count", "pci-before").line,
        workload.line,
        one(records, "count", "spi-after").line,
        one(records, "count", "pci-after").line,
        cleanup.line,
        final.line,
    ]
    if ordered != sorted(ordered) or len(ordered) != len(set(ordered)):
        raise SpiError("event_order")
    spi_before_json: list[JsonValue] = list(spi_before)
    spi_after_json: list[JsonValue] = list(spi_after)
    spi_delta_json: list[JsonValue] = list(spi_delta)
    pci_before_json: list[JsonValue] = list(pci_before)
    pci_after_json: list[JsonValue] = list(pci_after)
    pci_delta_json: list[JsonValue] = list(pci_delta)
    payload: dict[str, JsonValue] = {
        "schema_version": 1,
        "status": "pass",
        "reason": "ok",
        "input_sha256": digest,
        "endpoint": dict(endpoint.fields),
        "pci_vector": dict(pci_vector.fields),
        "spi_virq": spi_virq,
        "chain": [dict(chain.fields)],
        "spi_before": spi_before_json,
        "spi_after": spi_after_json,
        "spi_delta": spi_delta_json,
        "pci_vector_before": pci_before_json,
        "pci_vector_after": pci_after_json,
        "pci_vector_delta": pci_delta_json,
        "cleanup": dict(cleanup.fields),
    }
    return payload


def atomic_write(path: Path, payload: dict[str, JsonValue]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
        temporary = Path(stream.name)
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate isolated Apollo QBox virtio-mmio SPI evidence."
    )
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--input-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source_hash = ""
    try:
        records, source_hash = parse_records(args.log)
        payload = validate(records, args.input_sha256)
        payload["source_log_sha256"] = source_hash
    except (OSError, SpiError) as error:
        payload = {
            "schema_version": 1,
            "status": "fail",
            "reason": error.reason if isinstance(error, SpiError) else "input_io",
            "input_sha256": args.input_sha256,
            "source_log_sha256": source_hash,
        }
    atomic_write(args.output, payload)
    print(args.output)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
