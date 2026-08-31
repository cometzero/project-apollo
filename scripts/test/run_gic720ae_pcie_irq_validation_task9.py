#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.0"]
# ///
# ─── How to run ───
# python3 scripts/test/run_gic720ae_pcie_irq_validation_task9.py --help

from __future__ import annotations

import argparse
from pathlib import Path
import signal
import sys

try:
    import gic720ae_pcie_irq_validation_ap_map as ap_map
    import gic720ae_pcie_irq_validation_contract as contract
    import qbox_apollo_pcie_irq_task9 as task9
    import qbox_apollo_pcie_irq_task9_cleanup as cleanup
    import qbox_apollo_pcie_irq_task9_process as process
    import qbox_apollo_pcie_irq_task9_result as result
except ModuleNotFoundError:
    from scripts.test import gic720ae_pcie_irq_validation_ap_map as ap_map
    from scripts.test import gic720ae_pcie_irq_validation_contract as contract
    from scripts.test import qbox_apollo_pcie_irq_task9 as task9
    from scripts.test import qbox_apollo_pcie_irq_task9_cleanup as cleanup
    from scripts.test import qbox_apollo_pcie_irq_task9_process as process
    from scripts.test import qbox_apollo_pcie_irq_task9_result as result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Task 9 in a Task 11 closure.")
    parser.add_argument("--fvp-reference-gate", required=True, type=Path)
    parser.add_argument("--qbox-profile-manifest", required=True, type=Path)
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--ap-map-audit", required=True, type=Path)
    parser.add_argument("--ap-map-audit-sha256", required=True)
    parser.add_argument("--ap-map-audit-size", required=True, type=int)
    return parser.parse_args()


def clean_run_root(run_root: Path) -> None:
    for mode in ("msix", "intx"):
        out_dir = run_root / mode
        if not out_dir.is_dir():
            continue
        cleanup.terminate_task_owned(out_dir)
        task9.cleanup_uart_fifo(out_dir)


def main() -> int:
    args = parse_args()
    for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
        signal.signal(signum, task9.signal_handler)
    run_root = args.run_root.resolve()
    try:
        pins = task9.pin_closure(
            args.fvp_reference_gate.resolve(), args.qbox_profile_manifest.resolve()
        )
        audit = ap_map.task11_artifact(
            run_root.parent,
            args.ap_map_audit,
            ap_map.ExpectedDigest(args.ap_map_audit_sha256, args.ap_map_audit_size),
        )
        run_root.mkdir(parents=True, exist_ok=False)
        msix = process.run_mode(run_root, "msix", pins.msix, pins)
        intx = process.run_mode(run_root, "intx", pins.intx, pins)
        process.run_validators(
            process.ValidatorInputs(
                run_root, pins, args.qbox_profile_manifest.resolve(), audit
            )
        )
        residual = process.residual_processes(run_root)
        if residual:
            raise task9.Task9Error("process_cleanup")
        result.write_qualification(run_root, pins, msix, intx)
        print(run_root / "qualification.json")
        return 0
    except task9.Task9Signal as error:
        print(f"interrupted:{error.signum}", file=sys.stderr)
        return 128 + error.signum
    except (
        contract.ValidationError,
        task9.Task9Error,
        cleanup.CleanupError,
        OSError,
    ) as error:
        print(error, file=sys.stderr)
        return 1
    finally:
        clean_run_root(run_root)


if __name__ == "__main__":
    raise SystemExit(main())
