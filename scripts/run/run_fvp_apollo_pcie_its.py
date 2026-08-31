#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))

from fvp_apollo_pcie_its_output import parse_output_dir
from fvp_apollo_pcie_its_profile import RunError, VerifiedProfile, atomic_write, configuration_applied, failure_result, load_json, require_record, sha256_file, verify_profile
from fvp_apollo_pcie_its_runtime import extract_base64_between, normalize_live_fdt, pcie_stall_state, require_runtime_pass, run, stop_process_group, verify_live_dt


WORKSPACE = Path(__file__).resolve().parents[2]

__all__ = [
    "RunError", "VerifiedProfile", "atomic_write", "configuration_applied",
    "extract_base64_between", "failure_result", "load_json", "normalize_live_fdt",
    "pcie_stall_state", "require_record", "require_runtime_pass", "run",
    "sha256_file", "stop_process_group", "verify_live_dt", "verify_profile",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=int, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        output_dir = parse_output_dir(args.out_dir, WORKSPACE)
    except RunError as error:
        print(error, file=sys.stderr)
        return 2
    with output_dir:
        profile_sha = ""
        try:
            if args.timeout <= 0 or args.timeout > 900:
                raise RunError("invalid_timeout")
            verified = verify_profile(args.profile_dir, expected_profile_sha=None)
            profile_sha = verified.profile_sha256
            result = run(verified, output_dir, args.timeout)
        except RunError as error:
            result = failure_result(
                error.reason, profile_sha, output_dir, {"error": error.detail}
            )
        print(output_dir.path / "result.json")
        return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
