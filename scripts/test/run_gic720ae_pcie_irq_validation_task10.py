#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["jsonschema>=4.0"]
# ///
# ─── How to run ───
# python3 scripts/test/run_gic720ae_pcie_irq_validation_task10.py --help

from __future__ import annotations

import argparse
from pathlib import Path

try:
    import compare_apollo_pcie_its_runtime as comparator
except ModuleNotFoundError:
    from scripts.test import compare_apollo_pcie_its_runtime as comparator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Task 10 on a Task 11 closure.")
    parser.add_argument("--fvp-reference-gate", required=True, type=Path)
    parser.add_argument("--qbox-profile-manifest", required=True, type=Path)
    parser.add_argument("--qbox-run-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return comparator.compare(
        args.fvp_reference_gate,
        args.qbox_profile_manifest,
        args.qbox_run_root,
        args.output,
    )


if __name__ == "__main__":
    raise SystemExit(main())
