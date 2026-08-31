#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.0"]
# ///
# ─── How to run ───
# python3 scripts/test/run_qbox_apollo_pcie_irq_task9.py --help

from __future__ import annotations

import argparse
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
import re
import signal
import sys
from typing import Final

try:
    import gic720ae_pcie_irq_validation_ap_map as ap_map
    import gic720ae_pcie_irq_validation_contract as contract
    import qbox_apollo_pcie_irq_task9 as task9
    import qbox_apollo_pcie_irq_task9_process as task9_process
    import qbox_apollo_pcie_irq_task9_result as task9_result
except ModuleNotFoundError:
    from scripts.test import gic720ae_pcie_irq_validation_ap_map as ap_map
    from scripts.test import gic720ae_pcie_irq_validation_contract as contract
    from scripts.test import qbox_apollo_pcie_irq_task9 as task9
    from scripts.test import qbox_apollo_pcie_irq_task9_process as task9_process
    from scripts.test import qbox_apollo_pcie_irq_task9_result as task9_result


class RunRootLayout(StrEnum):
    DIRECT = "direct"
    VERIFIER = "verifier"


@dataclass(frozen=True, slots=True)
class RunRootPolicy:
    path: Path
    layout: RunRootLayout
    run_id: str


DIRECT_RUN_ID_RE: Final = re.compile(r"run-\d{8}T\d{6}Z")
VERIFIER_RUN_ID_RE: Final = re.compile(r"fresh-run-\d{8}T\d{6}Z")
DEFAULT_AP_MAP_AUDIT: Final = (
    task9.ROOT / "build/qbox-apollo-qvp/ap-map-9-1-1/ap-map-audit.json"
)


def parse_run_root(raw: Path) -> RunRootPolicy:
    if ".." in raw.parts:
        raise task9.Task9Error("run_root")
    candidate = Path.cwd() / raw if not raw.is_absolute() else raw
    evidence_root = task9_process.EVIDENCE_ROOT.absolute()
    try:
        relative = candidate.relative_to(evidence_root)
    except ValueError as error:
        raise task9.Task9Error("run_root") from error
    if not relative.parts or len(relative.parts) > 2:
        raise task9.Task9Error("run_root")

    current = evidence_root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise task9.Task9Error("run_root_symlink")

    resolved = candidate.resolve()
    workspace = task9.ROOT.resolve()
    try:
        resolved.relative_to(workspace)
        resolved.relative_to(evidence_root.resolve())
    except ValueError as error:
        raise task9.Task9Error("run_root") from error

    if len(relative.parts) == 1 and DIRECT_RUN_ID_RE.fullmatch(relative.name):
        layout = RunRootLayout.DIRECT
        run_id = relative.name.removeprefix("run-")
    elif (
        len(relative.parts) == 2
        and relative.parts[0] == "verifier"
        and VERIFIER_RUN_ID_RE.fullmatch(relative.name)
    ):
        layout = RunRootLayout.VERIFIER
        run_id = relative.name.removeprefix("fresh-run-")
    else:
        raise task9.Task9Error("run_root")

    if not candidate.parent.is_dir():
        raise task9.Task9Error("run_root")
    if any((candidate / mode).exists() for mode in ("msix", "intx")):
        raise task9.Task9Error("stale_run_root")
    return RunRootPolicy(resolved, layout, run_id)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Qualify Apollo QBox PCI MSI-X, INTx, and virtio-mmio IRQs."
    )
    parser.add_argument("--fvp-reference-gate", required=True, type=Path)
    parser.add_argument("--profile-manifest", required=True, type=Path)
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--ap-map-audit", type=Path, default=DEFAULT_AP_MAP_AUDIT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
        signal.signal(signum, task9.signal_handler)
    try:
        pins = task9.pin_closure(args.fvp_reference_gate, args.profile_manifest)
        run_policy = parse_run_root(args.run_root)
        run_root = run_policy.path
        audit = ap_map.load(args.ap_map_audit, task9.ROOT, "task9_ap_map")
        run_root.mkdir(parents=True, exist_ok=True)
        msix = task9_process.run_mode(run_root, "msix", pins.msix, pins)
        intx = task9_process.run_mode(run_root, "intx", pins.intx, pins)
        task9_process.run_validators(
            task9_process.ValidatorInputs(
                run_root, pins, args.profile_manifest.resolve(), audit
            )
        )
        residual = task9_process.residual_processes(run_root)
        if residual:
            raise task9.Task9Error("process_cleanup")
        task9_result.write_qualification(run_root, pins, msix, intx)
        print(run_root)
        return 0
    except task9.Task9Signal as error:
        print(f"interrupted:{error.signum}", file=sys.stderr)
        return 128 + error.signum
    except (contract.ValidationError, task9.Task9Error, OSError) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
