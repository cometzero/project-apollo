#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.0"]
# ///
# ─── How to run ───
# python3 scripts/test/run_gic720ae_pcie_irq_validation.py --help

from __future__ import annotations

import argparse
import json
import signal
import sys
from pathlib import Path
from types import FrameType
from typing import Final

try:
    import gic720ae_pcie_irq_validation_contract as contract
    import gic720ae_pcie_irq_validation_execution as execution
    import gic720ae_pcie_irq_validation_negative as negative
    import gic720ae_pcie_irq_validation_provenance as provenance
    import gic720ae_pcie_irq_validation_workflow as workflow
    import qbox_apollo_pcie_irq_task9 as task9
except ModuleNotFoundError:
    from scripts.test import gic720ae_pcie_irq_validation_contract as contract
    from scripts.test import gic720ae_pcie_irq_validation_execution as execution
    from scripts.test import gic720ae_pcie_irq_validation_negative as negative
    from scripts.test import gic720ae_pcie_irq_validation_provenance as provenance
    from scripts.test import gic720ae_pcie_irq_validation_workflow as workflow
    from scripts.test import qbox_apollo_pcie_irq_task9 as task9


DEFAULT_GATE: Final = (
    contract.ROOT
    / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current/fvp-reference-gate-current.json"
)
DEFAULT_PROFILE: Final = (
    contract.ROOT
    / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current/canonical-profile-v4/manifest.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run FVP-boundary-first Apollo PCIe IRQ validation."
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--build-only", action="store_true")
    modes.add_argument("--self-test-negative", action="store_true")
    parser.add_argument("--fvp-reference-gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--qbox-profile-manifest", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--run-root", type=Path)
    parser.add_argument("--emit-profile-provenance", type=Path)
    parser.add_argument("--frozen-provenance", type=Path)
    parser.add_argument("--qbox-binary", type=Path, default=contract.QBOX_BINARY)
    parser.add_argument("--timeout", type=int, default=1800)
    return parser.parse_args()


def signal_handler(signum: int, _frame: FrameType | None) -> None:
    raise contract.ValidationError(f"interrupted:{signum}")


def config_from_args(args: argparse.Namespace) -> contract.RunConfig:
    if args.timeout < 1:
        raise contract.ValidationError("timeout")
    if args.self_test_negative:
        run_root = (
            contract.ROOT / ".omo/evidence/apollo-gic-its/task-11/self-test-unused"
        )
    elif args.build_only:
        if args.emit_profile_provenance is None:
            raise contract.ValidationError("build_only_provenance_output")
        run_root = contract.validate_output_path(args.emit_profile_provenance).parent
    else:
        if args.run_root is None:
            raise contract.ValidationError("run_root_required")
        run_root = args.run_root.absolute()
    return contract.RunConfig(
        args.fvp_reference_gate.resolve(),
        args.qbox_profile_manifest.resolve(),
        run_root,
        contract.validate_output_path(args.emit_profile_provenance)
        if args.emit_profile_provenance is not None
        else None,
        args.frozen_provenance.resolve()
        if args.frozen_provenance is not None
        else None,
        args.timeout,
        args.qbox_binary.absolute(),
    )


def preflight(config: contract.RunConfig) -> contract.JsonObject:
    contract.validate_gate(config.gate)
    contract.profile_bindings(config.profile)
    task9.pin_closure(config.gate, config.profile)
    closure = provenance.build(config)
    if config.frozen_provenance is not None:
        provenance.compare_frozen(
            closure, config.frozen_provenance, config.run_root
        )
    return closure


def main() -> int:
    args = parse_args()
    try:
        config = config_from_args(args)
        if args.self_test_negative:
            payload = negative.run(config)
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0 if payload["status"] == "PASS" else 1
        closure = preflight(config)
        if args.dry_run:
            for line in workflow.display_plan(config):
                print(line)
            return 0
        if not args.build_only:
            run_root = contract.validate_run_root(config.run_root)
            config = contract.RunConfig(
                config.gate,
                config.profile,
                run_root,
                config.provenance_output,
                config.frozen_provenance,
                config.timeout,
                config.qbox_binary,
            )
        for signum in (
            signal.SIGHUP,
            signal.SIGINT,
            signal.SIGTERM,
            signal.SIGALRM,
        ):
            signal.signal(signum, signal_handler)
        signal.alarm(config.timeout)
        try:
            if args.build_only:
                return execution.build_only(config, closure)
            return execution.execute(config, closure)
        finally:
            signal.alarm(0)
    except (contract.ValidationError, task9.Task9Error, OSError) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
