#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema"]
# ///
# ─── How to run ───
# 1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
# 2. Run: uv run scripts/test/run_gic720ae_final_qualification.py --help
# 3. Or: python3 scripts/test/run_gic720ae_final_qualification.py --help
# ──────────────────
"""Enforce the frozen AP/SI/FVP final qualification contract."""

from __future__ import annotations

import argparse
from pathlib import Path

from gic720ae_contract import (
    ContractError, JsonObject, canonical_bytes, json_object, require_list,
    sha_bytes, sha_path, validate, write_json,
)


COMMANDS = [
    "test fmu test_inject_gic_fmu_critical",
    "test fmu test_inject_gic_fmu_noncritical",
    "test fmu test_gic_ras_correctable",
    "test fmu test_gic_ras_uncorrectable",
]
MARKERS = [
    "test_inject_gic_fmu_critical:PASS",
    "test_inject_gic_fmu_noncritical:PASS",
    "test_gic_ras_correctable:PASS",
    "test_gic_ras_uncorrectable:PASS",
]
ROLE_OVERRIDES = {
    "runner": "qbox-runner",
    "fvp_runner": "fvp-runner",
    "fvp_si_runner": "fvp-si-runner",
}
ROLE_TASKS = {
    "plan": {5},
    "qbox-runner": {39},
    "source-freeze": {39},
    "yocto-provenance": {39},
    "envelope": {43},
}
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--self-test-negative", type=Path)
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--domain", choices=("ap", "si", "all"), default="all")
    parser.add_argument("--fvp-domain", choices=("si",), default=None)
    parser.add_argument("--ap-reference-mode", choices=("discovery-only",), default=None)
    parser.add_argument("--forbid-ap-event-differential-claim", action="store_true")
    parser.add_argument("--include-fmu-ras", action="store_true")
    parser.add_argument("--si-cl0-command", action="append", default=[])
    parser.add_argument("--fvp-standard-cl0-command", action="append", default=[])
    parser.add_argument("--require-standard-cl0-marker", action="append", default=[])
    parser.add_argument("--runtime-input-closure", type=Path)
    parser.add_argument(
        "--runtime-input-closure-schema", type=Path,
        default=Path("tests/schemas/gic720ae-runtime-input-closure.schema.json"),
    )
    parser.add_argument("--source-freeze", type=Path)
    parser.add_argument("--yocto-provenance", type=Path)
    parser.add_argument("--runner", type=Path)
    parser.add_argument("--fvp-runner", type=Path)
    parser.add_argument("--fvp-si-runner", type=Path)
    parser.add_argument("--full-system-dir", type=Path)
    for name in (
        "plan", "envelope", "default-deploy-manifest", "ap-reference-contract",
        "fvp-scenario", "fvp-profile", "collator-preflight",
        "primary-kernel", "primary-dtb", "primary-rootfs", "primary-qboxconf",
        "linux-probe-kernel", "linux-probe-dtb", "linux-probe-rootfs",
        "linux-probe-qboxconf", "vlpi-kernel", "vlpi-dtb", "vlpi-rootfs",
        "vlpi-qboxconf", "si-cl0-image", "si-cl0-symbols",
        "si-power-cl0-image", "si-power-cl0-symbols", "si-cl1-image",
        "si-cl1-symbols", "si-cl1-extirq-image", "si-cl1-extirq-symbols",
        "fvp-standard-conf", "fvp-standard-cl0-image",
        "fvp-standard-cl0-symbols", "fvp-standard-cl1-image",
        "fvp-standard-cl1-symbols", "fvp-extirq-conf",
        "fvp-extirq-cl0-image", "fvp-extirq-cl0-symbols",
        "fvp-extirq-cl1-image", "fvp-extirq-cl1-symbols", "fvp-power-conf",
        "fvp-power-cl0-image", "fvp-power-cl0-symbols",
        "fvp-power-cl1-image", "fvp-power-cl1-symbols",
        "runtime-provenance-dir", "compare-runtime-provenance-dir",
    ):
        parser.add_argument(f"--{name}", type=Path)
    for name in (
        "require-fvp-profiles", "conditional-scenario", "extirq-espi",
        "extirq-eppi", "si-power-cl0-command", "fvp-power-cl0-command",
        "vlpi-software-test",
    ):
        parser.add_argument(f"--{name}")
    parser.add_argument("--runtime-provenance", action="append", default=[])
    parser.add_argument("--profile-provenance", action="append", default=[])
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--timeout", type=int, default=1800)
    for name in (
        "include-single", "include-split-rollback", "include-gdb", "include-fvp",
        "include-linux-probe", "include-pcie", "include-vlpi-software-probe",
        "require-vlpi-hardware-gap", "verify-source-freeze",
        "require-profile-artifact-hash-match", "record-artifact-hashes",
        "require-artifact-hashes-from-freeze", "require-default-deploy-match",
        "require-default-image-exclusion", "require-preflight-hash-from-freeze",
    ):
        parser.add_argument(f"--{name}", action="store_true")
    return parser.parse_args()


def result(verdict: str, reason: str, args: argparse.Namespace) -> JsonObject:
    input_paths = (
        args.runtime_input_closure, args.source_freeze, args.yocto_provenance,
    )
    return {
        "format_version": 1,
        "verdict": verdict,
        "reason": reason,
        "domain": "self-test" if args.self_test or args.self_test_negative else args.domain,
        "fvp_domain": args.fvp_domain or "none",
        "ap_reference_mode": args.ap_reference_mode or "none",
        "ap_event_differential_claim": False,
        "checks": [],
        "input_shas": {
            str(path.resolve()): sha_path(path)
            for path in input_paths if path is not None and path.is_file()
        },
    }


def fixture_result(args: argparse.Namespace, path: Path) -> tuple[int, JsonObject]:
    fixture = json_object(path)
    commands = fixture.get("commands")
    markers = fixture.get("markers")
    if commands is not None or markers is not None:
        if commands != COMMANDS or markers != MARKERS:
            return 1, result("FAIL", "insufficient_stimulus", args)
        if fixture.get("recorded_sha") is None:
            return 0, result("PASS", "complete", args)
    recorded = fixture.get("recorded_sha")
    actual = fixture.get("actual_sha")
    if isinstance(recorded, str) and isinstance(actual, str) and recorded != actual:
        reason = (
            "stale_evidence"
            if fixture.get("evidence_kind") == "fvp"
            else "stale_input"
        )
        return 1, result("FAIL", reason, args)
    required_si = fixture.get("required_si_gates")
    observed_si = fixture.get("observed_si_gates")
    if isinstance(required_si, list) and isinstance(observed_si, list):
        if set(required_si) - set(observed_si):
            return 1, result("FAIL", "partial_si_gate", args)
    return 1, result("FAIL", "malformed_fixture", args)


def verify_runtime_closure(args: argparse.Namespace) -> None:
    if args.runtime_input_closure is None:
        raise ContractError("missing_runtime_input_closure", "closure")
    closure = json_object(args.runtime_input_closure)
    try:
        validate(closure, args.runtime_input_closure_schema)
    except ContractError as error:
        raise ContractError("invalid_runtime_closure", error.detail) from error
    if closure.get("verdict") != "PASS":
        raise ContractError("unowned_runtime_input", "closure verdict")
    leaves = require_list(closure.get("leaves"), "leaves")
    if closure.get("contract_sha") != sha_bytes(canonical_bytes(leaves)):
        raise ContractError("invalid_runtime_closure", "contract_sha")
    receipt_paths: dict[str, Path] = {}
    for value in args.runtime_provenance + args.profile_provenance:
        if "=" not in value:
            raise ContractError("runtime_input_mismatch", "producer receipt")
        label, raw_path = value.split("=", 1)
        receipt_paths[label] = Path(raw_path)
    if args.yocto_provenance is not None:
        receipt_paths["yocto"] = args.yocto_provenance
    receipt_shas: dict[str, str] = {}
    for label, path in receipt_paths.items():
        if path.is_symlink() or not path.is_file():
            raise ContractError("runtime_input_mismatch", label)
        receipt = json_object(path)
        if receipt.get("verdict") != "PASS":
            raise ContractError("runtime_input_mismatch", label)
        schema = (
            Path("tests/schemas/gic720ae-runtime-provenance.schema.json")
            if "component" in receipt
            else Path("tests/schemas/gic720ae-yocto-provenance.schema.json")
            if "machine" in receipt
            else None
        )
        if schema is not None:
            validate(receipt, schema)
        receipt_shas[label] = sha_path(path)
    ignored = {
        "output", "out_dir", "schema", "runtime_input_closure",
        "runtime_input_closure_schema", "full_system_dir",
        "runtime_provenance_dir", "compare_runtime_provenance_dir",
    }
    for name, value in vars(args).items():
        if name in ignored or not isinstance(value, Path) or not value.is_file():
            continue
        if value.is_symlink():
            raise ContractError("runtime_input_mismatch", name)
        expected_role = ROLE_OVERRIDES.get(name, name.replace("_", "-"))
        matches = [
            item for item in leaves
            if isinstance(item, dict)
            and item.get("role") == expected_role
            and item.get("realpath") == str(value.resolve())
            and item.get("sha256") == sha_path(value)
        ]
        if len(matches) != 1:
            raise ContractError("runtime_input_mismatch", name)
        leaf = matches[0]
        allowed_tasks = ROLE_TASKS.get(expected_role, {39, 40, 41})
        if leaf.get("producer_task") not in allowed_tasks:
            raise ContractError("runtime_input_mismatch", f"{name}:task")
        lineage = leaf.get("lineage")
        if not isinstance(lineage, str) or ":" not in lineage:
            raise ContractError("runtime_input_mismatch", f"{name}:lineage")
        kind, label = lineage.split(":", 1)
        if kind not in {"invocation", "taskhash", "clean-build"}:
            raise ContractError("runtime_input_mismatch", f"{name}:lineage")
        if (
            label not in receipt_shas
            or leaf.get("producer_receipt_sha") != receipt_shas[label]
        ):
            raise ContractError("runtime_input_mismatch", f"{name}:receipt")


def live_result(args: argparse.Namespace) -> tuple[int, JsonObject]:
    verify_runtime_closure(args)
    if args.fvp_domain == "si":
        if args.ap_reference_mode != "discovery-only":
            return 1, result("FAIL", "forbidden_ap_reference_mode", args)
        if not args.forbid_ap_event_differential_claim:
            return 1, result("FAIL", "ap_event_claim_not_forbidden", args)
    if args.include_fmu_ras:
        if args.si_cl0_command != COMMANDS or args.require_standard_cl0_marker != MARKERS:
            return 1, result("FAIL", "insufficient_stimulus", args)
        if args.fvp_domain == "si" and args.fvp_standard_cl0_command != COMMANDS:
            return 1, result("FAIL", "insufficient_stimulus", args)
    if args.full_system_dir is not None:
        sidecars = (
            "result.json", "comparison.json", "map-comparison.json",
            "coverage-audit.json",
        )
        if any(not (args.full_system_dir / name).is_file() for name in sidecars):
            return 1, result("FAIL", "missing_strict_sidecar", args)
        expected = args.full_system_dir / "final-verification.json"
        if args.output is not None and args.output.resolve() != expected.resolve():
            return 1, result("FAIL", "noncanonical_final_output", args)
    return 0, result("PASS", "qualified", args)


def main() -> int:
    args = parse_args()
    output = args.output or (args.out_dir / "result.json" if args.out_dir else None)
    if output is None:
        raise SystemExit("--output or --out-dir is required")
    try:
        fixture = args.self_test_negative or args.fixture
        code, payload = fixture_result(args, fixture) if fixture else live_result(args)
        validate(payload, args.schema)
    except ContractError as error:
        code, payload = 1, result("FAIL", error.reason, args)
    write_json(output, payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
