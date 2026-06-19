#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any


FORBIDDEN_QBOX_PATHS = [
    "tools/qbox/platforms/apollo",
    "tools/qbox/platforms/fvp-rd-aspen",
    "tools/qbox/platforms/fvp-rd-aspen-rse",
    "tools/qbox/qemu-components/cc3xx_native",
]

OVERLAY_ONLY_SYSTEMC_COMPONENTS = [
    "cc3xx",
    "dma350",
    "gicx00_multiview",
    "host_cmn_cyprus",
    "host_gtimer",
    "host_ni710ae_nci",
    "host_ppu",
    "host_smcf_mgi",
    "host_system_pll",
    "mhu320ae",
    "mhuv3_rproc_stub",
    "mhuv3_stub",
    "mmu720ae",
    "ras_ffh_stub",
    "reset_fanout",
    "rse_atu",
    "rse_integrity_checker",
    "rse_kmu",
    "rse_lcm",
    "rse_protection_ctrl",
    "rse_sam",
    "rse_sysctrl",
    "strata_flash_j3",
    "zena_fmu",
    "zena_ssu",
]

OVERLAY_ONLY_TEST_COMPONENTS = [
    "cc3xx",
    "dma350",
    "gicx00_multiview",
    "host_cmn_cyprus",
    "host_gtimer",
    "host_ni710ae_nci",
    "host_ppu",
    "host_smcf_mgi",
    "host_system_pll",
    "mhu320ae",
    "mhuv3_stub",
    "mmu720ae",
    "reset_fanout",
    "rse_atu",
    "rse_integrity_checker",
    "rse_kmu",
    "rse_lcm",
    "rse_protection_ctrl",
    "rse_sam",
    "rse_sysctrl",
    "strata_flash_j3",
    "zena_fmu",
    "zena_ssu",
]

ACTIVE_TEXT_PATTERNS = [
    re.compile(r"tools/qbox/platforms/(?:apollo|fvp-rd-aspen|fvp-rd-aspen-rse)"),
    re.compile(r"qbox\s*/\s*[\"']platforms/(?:apollo|fvp-rd-aspen|fvp-rd-aspen-rse)[\"']"),
    re.compile(r"tools/qbox/(?:systemc-components/cc3xx|qemu-components/cc3xx_native)"),
    re.compile(r"systemc-components/cc3xx/include"),
]

ACTIVE_TEXT_PATHS = [
    "AGENTS.md",
    "README.md",
    "scripts",
]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def collect_path_violations(root: Path) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    candidates = list(FORBIDDEN_QBOX_PATHS)
    candidates.extend(
        f"tools/qbox/systemc-components/{component}"
        for component in OVERLAY_ONLY_SYSTEMC_COMPONENTS
    )
    candidates.extend(
        f"tools/qbox/tests/components/{component}"
        for component in OVERLAY_ONLY_TEST_COMPONENTS
    )
    for rel_path in candidates:
        path = root / rel_path
        if path.exists():
            violations.append({"kind": "path", "path": rel_path})
    return violations


def iter_active_text_files(root: Path) -> list[Path]:
    self_path = Path(__file__).resolve()
    files: list[Path] = []
    for rel_path in ACTIVE_TEXT_PATHS:
        path = root / rel_path
        if path.is_file():
            if path.resolve() != self_path:
                files.append(path)
        elif path.is_dir():
            files.extend(
                child
                for child in path.rglob("*")
                if child.is_file()
                and child.resolve() != self_path
                and child.suffix in {".md", ".py", ".sh"}
            )
    return files


def collect_text_violations(root: Path) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for path in iter_active_text_files(root):
        rel_path = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern in ACTIVE_TEXT_PATTERNS:
                if pattern.search(line):
                    violations.append(
                        {
                            "kind": "text",
                            "path": rel_path,
                            "line": line_no,
                            "pattern": pattern.pattern,
                            "text": line.strip(),
                        }
                    )
    return violations


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit that Apollo/RD-Aspen overlay code is not left in QBox core."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="print machine-readable JSON instead of a human report",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = workspace_root()
    violations = collect_path_violations(root) + collect_text_violations(root)
    result = {
        "passed": not violations,
        "violations": violations,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif violations:
        for violation in violations:
            if violation["kind"] == "path":
                print(f"FAIL path: {violation['path']}", file=sys.stderr)
            else:
                print(
                    "FAIL text: "
                    f"{violation['path']}:{violation['line']}: "
                    f"{violation['text']}",
                    file=sys.stderr,
                )
    else:
        print("QBox core boundary audit passed")
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
