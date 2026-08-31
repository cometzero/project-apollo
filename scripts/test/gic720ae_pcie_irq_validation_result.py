from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import gic720ae_pcie_irq_validation_contract as contract
    import gic720ae_pcie_irq_validation_provenance as provenance
    import gic720ae_pcie_irq_validation_workflow as workflow
except ModuleNotFoundError:
    from scripts.test import gic720ae_pcie_irq_validation_contract as contract
    from scripts.test import gic720ae_pcie_irq_validation_provenance as provenance
    from scripts.test import gic720ae_pcie_irq_validation_workflow as workflow


@dataclass(frozen=True, slots=True)
class ResultInputs:
    config: contract.RunConfig
    closure_path: Path
    completed: set[str]
    failed: str | None
    reason: str
    qbox_started: bool
    children: dict[str, contract.JsonValue]
    ap_memory_map_audit: contract.JsonObject
    task9: contract.JsonObject
    task10: contract.JsonObject
    cleanup: contract.JsonObject


def phase_records(inputs: ResultInputs) -> list[contract.JsonValue]:
    records: list[contract.JsonValue] = []
    for phase in workflow.PHASES:
        status = "PASS" if phase in inputs.completed else "NOT_RUN"
        if phase == inputs.failed:
            status = "FAIL"
        records.append({"name": phase, "status": status})
    return records


def child_binding(result: contract.ChildResult) -> contract.JsonObject:
    return {
        "command": list(result.command),
        "returncode": result.returncode,
        "log": workflow.file_binding(result.log),
    }


def qbox_binding(inputs: ResultInputs) -> contract.JsonObject:
    return {
        "started": inputs.qbox_started,
        "build": "PASS" if "qbox_build" in inputs.completed else "FAIL",
        "binary": provenance.binary_identity(inputs.config.qbox_binary),
    }


def build(inputs: ResultInputs) -> contract.JsonObject:
    passed = inputs.failed is None
    return {
        "schema_version": 1,
        "overall": "PASS" if passed else "FAIL",
        "reason": "ok" if passed else inputs.reason,
        "fvp": {
            "reference_gate": "PASS",
            "qualification": "UNSUPPORTED",
            "started": False,
            "gate_sha256": contract.GATE_SHA256,
        },
        "provenance": {
            "status": "PASS",
            "path": str(inputs.closure_path.resolve()),
            "sha256": contract.digest(inputs.closure_path),
        },
        "qbox": qbox_binding(inputs),
        "ap_memory_map_audit": inputs.ap_memory_map_audit,
        "task9": inputs.task9,
        "task10": inputs.task10,
        "children": inputs.children,
        "cleanup": inputs.cleanup,
        "phases": phase_records(inputs),
        "timeout_seconds": inputs.config.timeout,
    }
