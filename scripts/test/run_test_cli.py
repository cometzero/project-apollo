#!/usr/bin/env python3

from __future__ import annotations

import sys


USAGE = "\n".join(
    (
        "Usage: ./run_test.sh [options]",
        "",
        "Run the Apollo FVP validation wrapper and save logs under build/tests/<stamp>.",
        "Default behavior: inspect the active Apollo Yocto config, then run",
        "the selected validation category. The default category is basic.",
        "",
        "Options:",
        "  --build-dir PATH          Yocto build directory (default: build)",
        "  --machine NAME            Yocto machine (default: apollo-fvp)",
        "  --image NAME              Image recipe/name (default: nexios-image)",
        "  --out-dir PATH            Run output directory (default: build/tests/<stamp>)",
        "  --stamp STAMP             Run stamp (default: date +%Y%m%d-%H%M%S)",
        "  --category CATEGORY       Select category for run/list; default: basic",
        "                            choices: basic, functional, power, extended, stress",
        "  --list                    List all suites, or selected category only",
        "  --dry-run                 Plan and summarize without runtime execution",
        "  --preflight-only          Run runtime prerequisite preflight only",
        "  --skip-runtime            Skip required runtime lanes",
        "  --include-qbox-runtime    Request QBox runtime lanes in later todos",
        "  --timeout-oeqa SECONDS    OEQA timeout for later runtime lanes",
        "  --timeout-fvp SECONDS     FVP timeout for the basic boot lane",
        "  -h, --help                Show this help",
        "",
        "Final result lines:",
        "  RESULT: PASS|FAIL|BLOCKED",
        "  SUMMARY: build/tests/<stamp>/summary.json",
        "",
        "Result paths:",
        "  manifest.json, suite.json, commands.jsonl, summary.json",
        "  and per-lane logs are written under build/tests/<stamp>.",
        "  build/tests/latest points at the most recent run directory.",
        "",
        "Exclusions:",
        "  Xen, DomU, virtualization-image, and test_40_virtualization style",
        "  lanes are excluded for the active baremetal Apollo FVP configuration.",
        "",
        "Exit codes:",
        "  0 PASS; 1 FAIL; 2 BLOCKED",
        "  64 command-line usage error; 70 internal runner error",
        "",
        "Common unblock steps:",
        "  Missing FVP executable: confirm the selected .fvpconf fvp-bindir/exe",
        "  exists or install the Arm FVP package for FVP_Zena_CSS_Cfg2.",
        "  Missing Crypto plugin: confirm Crypto.so exists next to the selected",
        "  FVP plugin path referenced by .fvpconf.",
        "  port collision: free 127.0.0.1:2222 or wait for the holder of",
        "  build/tests/.run_test.lock to finish.",
    )
)


def main() -> int:
    print(USAGE, end="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
