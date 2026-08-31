#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# ─── How to run ───
# python3 scripts/test/validate_apollo_pcie_its_runtime.py --help

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Final, NewType, TypedDict


PREFIX: Final = "APOLLO_IRQ|"
HASH_RE: Final = re.compile(r"[0-9a-f]{64}")
Virq = NewType("Virq", int)
JsonValue = str | int | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


class PhaseResult(TypedDict):
    before: list[int]
    after: list[int]
    delta: list[int]
    effective_cpu: int


@dataclass(frozen=True, slots=True)
class ContractError(Exception):
    reason: str

    def __str__(self) -> str:
        return self.reason


@dataclass(frozen=True, slots=True)
class Record:
    line: int
    fields: dict[str, str]


@dataclass(frozen=True, slots=True)
class PhaseSpec:
    name: str
    cpu: int
    target: str
    delta_reason: str


def parse_records(path: Path) -> tuple[list[Record], str]:
    raw = path.read_bytes()
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", raw.decode("utf-8", errors="replace")).replace("\r", "")
    records: list[Record] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.startswith(PREFIX):
            continue
        fields: dict[str, str] = {}
        for token in line[len(PREFIX):].split("|"):
            if "=" not in token:
                raise ContractError("malformed_input")
            key, value = token.split("=", 1)
            if not key or not value or key in fields:
                raise ContractError("malformed_input")
            fields[key] = value
        records.append(Record(line_number, fields))
    if not records:
        raise ContractError("malformed_input")
    return records, hashlib.sha256(raw).hexdigest()


def select(records: list[Record], event: str, phase: str | None = None) -> list[Record]:
    return [r for r in records if r.fields.get("event") == event and (phase is None or r.fields.get("phase") == phase)]


def one(records: list[Record], event: str, reason: str, phase: str | None = None) -> Record:
    found = select(records, event, phase)
    if len(found) != 1:
        raise ContractError(reason)
    return found[0]


def json_fields(fields: dict[str, str]) -> dict[str, JsonValue]:
    return {key: value for key, value in fields.items()}


def json_int_list(values: list[int]) -> list[JsonValue]:
    return [value for value in values]


def phase_json(phase: PhaseResult) -> dict[str, JsonValue]:
    return {
        "before": json_int_list(phase["before"]),
        "after": json_int_list(phase["after"]),
        "delta": json_int_list(phase["delta"]),
        "effective_cpu": phase["effective_cpu"],
    }


def number(value: str, reason: str) -> int:
    try:
        return int(value, 0)
    except ValueError as error:
        raise ContractError(reason) from error


def counts(records: list[Record], phase: str) -> list[int]:
    record = one(records, "count", "phase_missing", phase)
    values = [number(value, "count_format") for value in record.fields.get("values", "").split(",")]
    if len(values) < 2:
        raise ContractError("cpu_count")
    return values


def endpoint_check(endpoint: Record, platform: str, mode: str) -> None:
    fields = endpoint.fields
    if mode == "spi":
        devpath = fields.get("devpath", "")
        if fields.get("bdf") != "-" or not devpath.startswith("/sys/bus/platform/devices/"):
            raise ContractError("endpoint_kind")
        if devpath != "/sys/bus/platform/devices/30060000.virtio":
            raise ContractError("spi_endpoint_path")
        if fields.get("driver") != "virtio-mmio" or fields.get("compatible") != "virtio,mmio":
            raise ContractError("spi_endpoint_identity")
        return
    if not fields.get("devpath", "").endswith(fields.get("bdf", "!")):
        raise ContractError("endpoint_kind")
    if platform == "fvp":
        valid = (fields.get("bdf") == "0004:00:1f.0" and fields.get("vendor") == "0x13b5"
                 and fields.get("class", "").startswith("0x0106") and fields.get("driver") == "ahci")
    else:
        valid = (fields.get("bdf") == "0000:00:01.0" and fields.get("class", "").startswith("0x0200")
                 and fields.get("driver") == "virtio-pci" and fields.get("mac") == "52:54:00:12:34:56")
    if not valid:
        raise ContractError("endpoint_identity")


def chain_check(records: list[Record], mode: str, endpoint: Record) -> tuple[Virq, list[dict[str, str]]]:
    event = "msi_irq" if mode == "msix" else "line_irq"
    irq_record = one(records, event, "irq_owner_missing")
    virq = Virq(number(irq_record.fields.get("virq", ""), "irq_format"))
    if mode == "msix" and irq_record.fields.get("owner") != f"{endpoint.fields['devpath']}/msi_irqs/{virq}":
        raise ContractError("irq_owner")
    if mode != "msix" and irq_record.fields.get("owner") != endpoint.fields["devpath"]:
        raise ContractError("irq_owner")
    chain = [r for r in select(records, "chain") if r.fields.get("virq") == str(virq)]
    indexes = [number(r.fields.get("index", ""), "chain_order") for r in chain]
    if len(indexes) != len(set(indexes)):
        raise ContractError("chain_duplicate")
    if not chain:
        raise ContractError("chain_missing")
    if mode == "msix":
        chips = [r.fields.get("chip") for r in chain]
        domains = [r.fields.get("domain") for r in chain]
        if indexes != [0, 1, 2] or chips != ["PCI-MSIX", "ITS-MSI", "GICv3"]:
            raise ContractError("chain_order")
        if domains != [f"PCI-MSIX-{endpoint.fields['bdf']}", "ITS-MSI", "GICv3"]:
            raise ContractError("chain_domain_identity")
        parents = [number(chain[i].fields.get("hwirq", ""), "chain_hwirq") for i in (1, 2)]
        if min(parents) < 8192 or parents[0] != parents[1]:
            raise ContractError("lpi_hwirq_range")
    elif mode == "intx":
        if indexes != [0] or chain[0].fields.get("chip") != "GICv3" or chain[0].fields.get("domain") != "GICv3" or number(chain[0].fields.get("hwirq", ""), "intx_hwirq") != 333:
            raise ContractError("intx_hwirq")
    else:
        if indexes != [0] or chain[0].fields.get("chip") != "GICv3" or chain[0].fields.get("domain") != "GICv3" or number(chain[0].fields.get("hwirq", ""), "spi_hwirq") != 293:
            raise ContractError("spi_hwirq")
    return virq, [dict(r.fields) for r in chain]


def phase_check(records: list[Record], spec: PhaseSpec) -> PhaseResult:
    if spec.name != "offline":
        affinity = one(records, "affinity", "affinity_missing", spec.name)
        if affinity.fields.get("rc") != "0" or affinity.fields.get("requested") != str(spec.cpu) or affinity.fields.get("effective") != str(spec.cpu):
            raise ContractError("affinity_effective")
    workload = one(records, "workload", "workload_missing", spec.name)
    if workload.fields.get("target") != spec.target:
        raise ContractError("workload_target")
    if workload.fields.get("rc") != "0":
        raise ContractError("workload_rc")
    before, after = counts(records, f"{spec.name}-before"), counts(records, f"{spec.name}-after")
    if len(before) != len(after) or spec.cpu >= len(before):
        raise ContractError("cpu_count")
    delta = [end - start for start, end in zip(before, after, strict=True)]
    if delta[spec.cpu] <= 0 or any(value != 0 for index, value in enumerate(delta) if index != spec.cpu):
        raise ContractError(spec.delta_reason)
    return {"before": before, "after": after, "delta": delta, "effective_cpu": spec.cpu}


def validate(records: list[Record], platform: str, mode: str, digest: str) -> dict[str, JsonValue]:
    contract = one(records, "contract", "contract_missing")
    if any(r.fields.get("v") != "1" for r in records):
        raise ContractError("contract_version")
    if contract.fields.get("input_sha256") != digest or not HASH_RE.fullmatch(digest):
        raise ContractError("input_hash")
    if contract.fields.get("platform") != platform or contract.fields.get("mode") != mode:
        raise ContractError("platform_contract")
    expected_action = "disk-io" if platform == "fvp" else ("net-io" if mode != "spi" else "control")
    if contract.fields.get("action") != expected_action:
        raise ContractError("action_contract")
    endpoint = one(records, "endpoint", "endpoint_missing")
    endpoint_check(endpoint, platform, mode)
    virq, chain = chain_check(records, mode, endpoint)
    target = endpoint.fields.get("target", "")
    phases: dict[str, PhaseResult] = {"cpu0": phase_check(records, PhaseSpec("cpu0", 0, target, "cpu0_delta")),
                                      "cpu1": phase_check(records, PhaseSpec("cpu1", 1, target, "cpu1_delta"))}
    offline = one(records, "hotplug", "hotplug_offline", "cpu1-offline")
    if offline.fields.get("rc") != "0" or offline.fields.get("online") != "0" or offline.fields.get("effective") != "0":
        raise ContractError("hotplug_offline")
    phases["offline"] = phase_check(records, PhaseSpec("offline", 0, target, "offline_delta"))
    online = one(records, "hotplug", "hotplug_online", "cpu1-online")
    if online.fields.get("rc") != "0" or online.fields.get("online") != "1":
        raise ContractError("hotplug_online")
    phases["replay"] = phase_check(records, PhaseSpec("replay", 1, target, "replay_delta"))
    cleanup = one(records, "cleanup", "cleanup_missing")
    if cleanup.fields.get("rc") != "0" or cleanup.fields.get("affinity_restored") != "1" or cleanup.fields.get("cpu1_restored") != "1":
        raise ContractError("cleanup_failed")
    final = one(records, "final", "final_missing")
    if final.fields.get("status") != "complete" or final.fields.get("input_sha256") != digest:
        raise ContractError("final_invalid")
    irq_line = one(records, "msi_irq" if mode == "msix" else "line_irq", "irq_owner_missing").line
    chain_lines = [record.line for record in select(records, "chain") if record.fields.get("virq") == str(virq)]
    phase_lines = [
        one(records, "affinity", "affinity_missing", "cpu0").line,
        one(records, "count", "phase_missing", "cpu0-before").line,
        one(records, "workload", "workload_missing", "cpu0").line,
        one(records, "count", "phase_missing", "cpu0-after").line,
        one(records, "affinity", "affinity_missing", "cpu1").line,
        one(records, "count", "phase_missing", "cpu1-before").line,
        one(records, "workload", "workload_missing", "cpu1").line,
        one(records, "count", "phase_missing", "cpu1-after").line,
        offline.line,
        one(records, "count", "phase_missing", "offline-before").line,
        one(records, "workload", "workload_missing", "offline").line,
        one(records, "count", "phase_missing", "offline-after").line,
        online.line,
        one(records, "affinity", "affinity_missing", "replay").line,
        one(records, "count", "phase_missing", "replay-before").line,
        one(records, "workload", "workload_missing", "replay").line,
        one(records, "count", "phase_missing", "replay-after").line,
    ]
    ordered_lines = [contract.line, endpoint.line, irq_line, *chain_lines, *phase_lines, cleanup.line, final.line]
    if ordered_lines != sorted(ordered_lines) or len(ordered_lines) != len(set(ordered_lines)):
        raise ContractError("event_order")
    chain_json: list[JsonValue] = [json_fields(item) for item in chain]
    phases_json: dict[str, JsonValue] = {name: phase_json(phase) for name, phase in phases.items()}
    return {"status": "pass", "reason": "ok", "platform": platform, "mode": mode, "action": expected_action,
            "input_sha256": digest, "endpoint": json_fields(endpoint.fields), "virq": int(virq),
            "chain": chain_json, "cpu_count": len(phases["cpu0"]["before"]), "phases": phases_json,
            "cleanup": json_fields(cleanup.fields)}


def atomic_write(path: Path, payload: dict[str, JsonValue]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
        temporary = Path(stream.name)
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate endpoint-bound Apollo IRQ evidence")
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--input-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source_hash = ""
    platform = args.platform if args.platform in ("fvp", "qbox") else "invalid"
    mode = args.mode if args.mode in ("msix", "intx", "spi") else "invalid"
    digest_valid = HASH_RE.fullmatch(args.input_sha256) is not None
    normalized_digest = args.input_sha256 if digest_valid else hashlib.sha256(args.input_sha256.encode()).hexdigest()
    try:
        if platform == "invalid" or mode == "invalid":
            raise ContractError("platform_contract")
        records, source_hash = parse_records(args.log)
        payload = validate(records, platform, mode, args.input_sha256)
        payload["source_log_sha256"] = source_hash
        payload["schema_version"] = 1
        payload["input_sha256_valid"] = True
    except (ContractError, OSError) as error:
        reason = error.reason if isinstance(error, ContractError) else "input_io"
        payload = {"schema_version": 1, "status": "fail", "reason": reason, "platform": platform,
                   "mode": mode, "input_sha256": normalized_digest, "input_sha256_valid": digest_valid,
                   "source_log_sha256": source_hash}
    atomic_write(args.output, payload)
    print(args.output)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
