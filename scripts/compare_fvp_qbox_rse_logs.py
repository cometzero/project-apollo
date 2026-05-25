#!/usr/bin/env python3
"""Compare deterministic RD-Aspen RSE markers between FVP and QBox logs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


MARKER_GROUPS = {
    "rse_boot": [
        "Starting TF-M BL1_1",
        "Jumping to the first image slot",
    ],
    "rse_scp_handoff": [
        "Init SCMI comm to SCP succeeded",
        "RSE to SCP SCMI power on AP succeeded",
        "SCMI Comms subscribed to power state notifications",
    ],
    "measured_boot": [
        "BL1_2",
        "BL2",
        "SI_CL0",
        "AP_BL2",
        "RT_0",
        "SECURE_RT_EL3",
        "SECURE_RT_EL1_SPMD",
        "BL_33",
    ],
    "linux_boot": [
        "fvp-rd-aspen login:",
        "root@fvp-rd-aspen",
        "apollo-fvp login:",
        "root@apollo-fvp",
    ],
}

ORDERED_MARKERS = [
    "Starting TF-M BL1_1",
    "Init SCMI comm to SCP succeeded",
    "RSE to SCP SCMI power on AP succeeded",
    "Jumping to the first image slot",
    "SCMI Comms subscribed to power state notifications",
]

NORMALIZERS = [
    (re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\a]*(?:\a|\x1b\\)"), ""),
    (re.compile(r"\b\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\b"), "<timestamp>"),
    (re.compile(r"\b20\d{6}-\d{6}\b"), "<run-id>"),
    (re.compile(r"\bport \d+\b", re.IGNORECASE), "port <port>"),
    (re.compile(r"\blocalhost:\d+\b"), "localhost:<port>"),
    (re.compile(r"/(?:build|home|tmp|var|run)/[^\s'\"]+"), "<path>"),
    (re.compile(r"writable-images/[^\s'\"]+"), "writable-images/<image>"),
]

EXCLUDED_DIRECTORY_FILES = {
    "summary.txt",
    "comparison.txt",
}


def read_text(path: Path) -> str:
    if path.is_file():
        return path.read_text(encoding="utf-8", errors="replace")
    if not path.exists():
        return ""
    parts: list[str] = []
    for child in sorted(path.rglob("*")):
        if (
            child.is_file()
            and child.name not in EXCLUDED_DIRECTORY_FILES
            and child.suffix.lower() == ".log"
        ):
            parts.append(f"\n===== {child} =====\n")
            parts.append(child.read_text(encoding="utf-8", errors="replace"))
    return "".join(parts)


def normalize(text: str) -> str:
    out = text.replace("\r", "")
    for pattern, repl in NORMALIZERS:
        out = pattern.sub(repl, out)
    return out


def marker_hits(text: str) -> dict[str, dict[str, bool]]:
    return {
        group: {marker: marker in text for marker in markers}
        for group, markers in MARKER_GROUPS.items()
    }


def ordered_positions(text: str) -> dict[str, int | None]:
    return {
        marker: (index if (index := text.find(marker)) >= 0 else None)
        for marker in ORDERED_MARKERS
    }


def order_ok(positions: dict[str, int | None]) -> bool:
    seen = [pos for pos in positions.values() if pos is not None]
    return seen == sorted(seen)


def compare(fvp_text: str, qbox_text: str) -> dict[str, object]:
    fvp = normalize(fvp_text)
    qbox = normalize(qbox_text)
    fvp_hits = marker_hits(fvp)
    qbox_hits = marker_hits(qbox)
    missing_in_qbox = {
        group: [
            marker
            for marker, hit in fvp_hits[group].items()
            if hit and not qbox_hits[group].get(marker, False)
        ]
        for group in MARKER_GROUPS
    }
    required_missing = {
        group: [marker for marker, hit in hits.items() if not hit]
        for group, hits in qbox_hits.items()
        if group != "linux_boot"
    }
    linux_ok = any(qbox_hits["linux_boot"].values())
    qbox_positions = ordered_positions(qbox)
    qbox_order_ok = order_ok(qbox_positions)
    passed = (
        not any(missing_in_qbox.values())
        and not any(required_missing.values())
        and linux_ok
        and qbox_order_ok
    )
    return {
        "passed": passed,
        "fvp_marker_hits": fvp_hits,
        "qbox_marker_hits": qbox_hits,
        "missing_in_qbox_from_fvp": missing_in_qbox,
        "required_missing_in_qbox": required_missing,
        "linux_ok": linux_ok,
        "qbox_ordered_marker_positions": qbox_positions,
        "qbox_order_ok": qbox_order_ok,
        "normalized_fvp_bytes": len(fvp.encode("utf-8", errors="replace")),
        "normalized_qbox_bytes": len(qbox.encode("utf-8", errors="replace")),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare deterministic RSE boot markers between FVP and QBox logs."
    )
    parser.add_argument("--fvp", type=Path, required=True, help="FVP log file or run directory")
    parser.add_argument("--qbox", type=Path, required=True, help="QBox log file or run directory")
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = compare(read_text(args.fvp), read_text(args.qbox))
    result["fvp"] = str(args.fvp.resolve())
    result["qbox"] = str(args.qbox.resolve())
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
