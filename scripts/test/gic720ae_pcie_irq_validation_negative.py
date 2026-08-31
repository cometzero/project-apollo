from __future__ import annotations

import copy
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, assert_never

try:
    import apollo_pcie_its_boundary_contract as boundary_contract
    import gic720ae_pcie_irq_validation_contract as contract
    import gic720ae_pcie_irq_validation_provenance as provenance
except ModuleNotFoundError:
    from scripts.test import apollo_pcie_its_boundary_contract as boundary_contract
    from scripts.test import gic720ae_pcie_irq_validation_contract as contract
    from scripts.test import gic720ae_pcie_irq_validation_provenance as provenance


@dataclass(frozen=True, slots=True)
class NegativeOutcome:
    name: str
    status: str


NegativeAction = Literal[
    "load", "gate", "profile", "provenance", "child", "comparison", "result"
]


def expect_failure(name: str, action: NegativeAction, path: Path) -> NegativeOutcome:
    try:
        match action:
            case "load":
                contract.load_object(path, name)
            case "gate":
                contract.validate_gate(path)
            case "profile":
                contract.profile_bindings(path)
            case "provenance":
                payload = contract.load_object(path, name)
                contract.validate_schema(
                    payload, contract.PROVENANCE_SCHEMA, "provenance_schema"
                )
            case "child":
                payload = contract.load_object(path, name)
                result = base_result()
                result["children"] = {"candidate": payload}
                contract.validate_schema(
                    result, contract.RESULT_SCHEMA, "result_child_schema"
                )
            case "comparison":
                payload = contract.load_object(path, name)
                contract.validate_schema(
                    payload,
                    contract.ROOT
                    / "tests/schemas/apollo-pcie-its-boundary-comparison.schema.json",
                    "comparison_schema",
                )
            case "result":
                payload = contract.load_object(path, name)
                contract.validate_schema(
                    payload, contract.RESULT_SCHEMA, "result_schema"
                )
            case unreachable:
                assert_never(unreachable)
    except contract.ValidationError:
        return NegativeOutcome(name, "PASS")
    return NegativeOutcome(name, "FAIL")


def write_json(path: Path, value: contract.JsonValue) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def shape_matrix(
    root: Path,
    name: str,
    action: NegativeAction,
    valid: contract.JsonObject,
) -> list[NegativeOutcome]:
    outcomes: list[NegativeOutcome] = []
    for variant, value in (
        ("scalar", 7),
        ("array", []),
        ("malformed", "{"),
    ):
        path = root / f"{name}-{variant}.json"
        if variant == "malformed":
            path.write_text(str(value), encoding="utf-8")
        else:
            write_json(path, value)
        outcomes.append(expect_failure(f"{name}_{variant}", action, path))
    wrong_version = copy.deepcopy(valid)
    wrong_version["schema_version"] = 999
    version_path = root / f"{name}-wrong_version.json"
    write_json(version_path, wrong_version)
    outcomes.append(expect_failure(f"{name}_wrong_version", action, version_path))
    outcomes.append(
        expect_failure(f"{name}_missing", action, root / f"{name}-missing.json")
    )
    return outcomes


def base_result() -> contract.JsonObject:
    phases: list[contract.JsonValue] = [
        {"name": name, "status": "NOT_RUN"}
        for name in (
            "parse_hash_inputs",
            "validate_fvp_gate",
            "provenance_preflight",
            "qbox_build",
            "task9_qualification",
            "task10_comparison",
            "cleanup_audit",
            "atomic_final_result",
        )
    ]
    return {
        "schema_version": 1,
        "overall": "FAIL",
        "reason": "negative_fixture",
        "fvp": {
            "reference_gate": "PASS",
            "qualification": "UNSUPPORTED",
            "started": False,
            "gate_sha256": contract.GATE_SHA256,
        },
        "provenance": {"status": "PASS", "path": "/tmp/p", "sha256": "0" * 64},
        "qbox": {
            "started": False,
            "build": "FAIL",
            "binary": {"status": "MISSING", "path": "/missing/platforms-vp"},
        },
        "task9": {"status": "NOT_RUN", "artifacts": {}},
        "task10": {"status": "NOT_RUN"},
        "children": {},
        "cleanup": {"status": "PASS", "residual_pids": [], "receipts": {}},
        "phases": phases,
        "timeout_seconds": 1,
    }


def base_comparison() -> contract.JsonObject:
    versions: dict[str, contract.JsonValue] = {
        "contract_collection_entry_size": 2,
        "fvp_gate_schema_version": 1,
        "pcie_runtime_schema_version": 2,
        "profile_schema_version": 2,
        "qualification_schema_version": 1,
        "run_id": "negative-fixture",
        "spi_runtime_schema_version": 1,
    }
    bindings: contract.JsonObject = {
        name: versions.get(name, "0" * 64)
        for name in boundary_contract.BINDINGS
    }
    rows: contract.JsonObject = {}
    for row in boundary_contract.ROWS:
        refs: list[contract.JsonValue] = [ref for ref in sorted(row.refs)]
        entry: contract.JsonObject = {
            "id": row.key,
            "scope": row.scope,
            "status": "UNSUPPORTED" if row.scope == "FVP" else "PASS",
            "detail": row.detail,
            "bindings": refs,
        }
        rows[row.key] = entry
    return {
        "schema_version": 1,
        "status": "PASS",
        "reason": "ok",
        "fvp_qualification": "UNSUPPORTED",
        "device_equivalence": "NOT_COMPARABLE",
        "bindings": bindings,
        "rows": rows,
    }


def frozen_byte_matrix(
    root: Path, closure: contract.JsonObject
) -> list[NegativeOutcome]:
    canonical = provenance.canonical_bytes(closure)
    reordered = {key: closure[key] for key in reversed(tuple(closure))}
    variants = (
        ("appended_newline", canonical + b"\n"),
        ("leading_space", b" " + canonical),
        ("trailing_spaces", canonical.rstrip(b"\n") + b"  \n"),
        ("reordered_keys", (json.dumps(reordered, indent=2) + "\n").encode()),
    )
    outcomes: list[NegativeOutcome] = []
    for name, content in variants:
        path = root / f"frozen-{name}.json"
        path.write_bytes(content)
        try:
            provenance.compare_frozen(closure, path, root)
        except contract.ValidationError:
            outcomes.append(NegativeOutcome(f"frozen_{name}", "PASS"))
        else:
            outcomes.append(NegativeOutcome(f"frozen_{name}", "FAIL"))
    return outcomes


def run(config: contract.RunConfig) -> contract.JsonObject:
    closure = provenance.build(config)
    outcomes: list[NegativeOutcome] = []
    with tempfile.TemporaryDirectory(prefix="apollo-t11-negative-") as raw_root:
        root = Path(raw_root)
        gate = contract.load_object(config.gate, "gate")
        profile = contract.load_object(config.profile, "profile")
        child: contract.JsonObject = {
            "command": ["true"],
            "returncode": 0,
            "log": {
                "path": str(config.gate),
                "sha256": contract.GATE_SHA256,
                "size": config.gate.stat().st_size,
            },
        }
        comparison = base_comparison()
        cases: tuple[tuple[str, NegativeAction, contract.JsonObject], ...] = (
            ("gate", "gate", gate),
            ("profile", "profile", profile),
            ("provenance", "provenance", closure),
            ("child", "child", child),
            ("comparison", "comparison", comparison),
            ("result", "result", base_result()),
        )
        for name, action, valid in cases:
            outcomes.extend(shape_matrix(root, name, action, valid))
        outcomes.extend(frozen_byte_matrix(root, closure))

        comparison = copy.deepcopy(comparison)
        rows = contract.object_value(comparison.get("rows"), "comparison_rows")
        rows.pop("qbox_msix_its_lpi")
        comparison_path = root / "missing-physical-lpi.json"
        write_json(comparison_path, comparison)
        outcomes.append(
            expect_failure(
                "comparison_missing_physical_lpi", "comparison", comparison_path
            )
        )

        bad_result = base_result()
        bad_result["overall"] = "PASS"
        result_path = root / "misleading-result.json"
        write_json(result_path, bad_result)
        outcomes.append(expect_failure("result_misleading_pass", "result", result_path))
    matrix: list[contract.JsonValue] = [
        {"name": outcome.name, "status": outcome.status} for outcome in outcomes
    ]
    passed = all(outcome.status == "PASS" for outcome in outcomes)
    return {
        "schema_version": 1,
        "status": "PASS" if passed else "FAIL",
        "fvp_started": False,
        "qbox_started": False,
        "prompt_injection": "N/A:no_instruction_surface",
        "matrix": matrix,
    }
