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

TEST_403_RE = re.compile(
    r"TEST:\s*403\s*\|\s*DESCRIPTION:\s*Insufficient space check\s*\|\s*UT:\s*(?P<ut>ITS|PS)"
)
NEXT_TEST_RE = re.compile(r"\s*TEST:\s+\d+\s*\|")
CHECK_RE = re.compile(r"\[Check\s+(?P<check>\d+)\]")
UID_SPACE_RE = re.compile(
    r"UID\s+(?P<uid>\d+)\s+set failed due to insufficient space"
)
TEST_RESULT_RE = re.compile(r"TEST RESULT:\s*(?P<result>PASSED|FAILED)")
SECTION_END_RE = re.compile(
    r"(^root@|__FVP_|__QBOX_|(?:fvp_)?secure_psa_(?:its|ps)_api_test_rc:)"
)

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


def is_meaningful_log_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("====="):
        return False
    if set(stripped) == {"*"}:
        return False
    return True


def parse_storage_test_403(text: str) -> dict[str, object]:
    normalized = normalize(text)
    lines = normalized.splitlines()
    sections: list[dict[str, object]] = []
    index = 0
    while index < len(lines):
        match = TEST_403_RE.search(lines[index])
        if not match:
            index += 1
            continue

        ut = match.group("ut")
        section_lines = [lines[index]]
        end = index + 1
        while end < len(lines):
            if lines[end].startswith("====="):
                break
            if NEXT_TEST_RE.match(lines[end]):
                break
            if SECTION_END_RE.search(lines[end]):
                break
            section_lines.append(lines[end])
            end += 1

        checks_seen = sorted(
            {
                int(check.group("check"))
                for line in section_lines
                for check in CHECK_RE.finditer(line)
            }
        )
        insufficient_space_uids = [
            int(uid.group("uid"))
            for line in section_lines
            for uid in UID_SPACE_RE.finditer(line)
        ]
        results = [
            result.group("result")
            for line in section_lines
            for result in TEST_RESULT_RE.finditer(line)
        ]
        meaningful = [
            line.strip() for line in section_lines if is_meaningful_log_line(line)
        ]
        section = {
            "ut": ut,
            "started": True,
            "checks_seen": checks_seen,
            "insufficient_space_uids": insufficient_space_uids,
            "insufficient_space_uid": insufficient_space_uids[-1]
            if insufficient_space_uids
            else None,
            "remove_all_registered_uids_count": sum(
                "Remove all registered UIDs" in line for line in section_lines
            ),
            "result": results[-1] if results else None,
            "completed": "PASSED" in results,
            "last_observed_line": meaningful[-1] if meaningful else None,
        }
        sections.append(section)
        index = end

    by_ut: dict[str, dict[str, object] | None] = {"ITS": None, "PS": None}
    for section in sections:
        by_ut[str(section["ut"])] = section
    return {
        "sections": sections,
        "by_ut": by_ut,
        "section_count": len(sections),
        "completed_uts": [
            ut for ut, section in by_ut.items() if section and section["completed"]
        ],
    }


def storage_stage(section: dict[str, object] | None) -> str:
    if not section:
        return "not_started"
    if section.get("completed"):
        return "completed"
    uid = section.get("insufficient_space_uid")
    if section.get("remove_all_registered_uids_count"):
        return f"cleanup_after_uid_{uid}"
    if uid is not None:
        return f"insufficient_space_uid_{uid}"
    checks_seen = section.get("checks_seen")
    if isinstance(checks_seen, list) and checks_seen:
        return f"check_{checks_seen[-1]}"
    return "started"


def missing_storage_steps(
    ut: str,
    fvp_section: dict[str, object] | None,
    qbox_section: dict[str, object] | None,
) -> list[str]:
    if not fvp_section:
        return []
    if not qbox_section:
        return [f"{ut}:test_403_started"]

    missing: list[str] = []
    fvp_checks = set(fvp_section.get("checks_seen", []))
    qbox_checks = set(qbox_section.get("checks_seen", []))
    for check in sorted(fvp_checks - qbox_checks):
        missing.append(f"{ut}:check_{check}")

    fvp_uid_count = len(fvp_section.get("insufficient_space_uids", []))
    qbox_uid_count = len(qbox_section.get("insufficient_space_uids", []))
    for index in range(qbox_uid_count + 1, fvp_uid_count + 1):
        missing.append(f"{ut}:insufficient_space_uid_event_{index}")

    fvp_cleanup_count = int(fvp_section.get("remove_all_registered_uids_count", 0))
    qbox_cleanup_count = int(qbox_section.get("remove_all_registered_uids_count", 0))
    for index in range(qbox_cleanup_count + 1, fvp_cleanup_count + 1):
        missing.append(f"{ut}:remove_all_registered_uids_event_{index}")

    if fvp_section.get("completed") and not qbox_section.get("completed"):
        missing.append(f"{ut}:test_403_completed")
    return missing


def compare_storage_test_403(fvp_text: str, qbox_text: str) -> dict[str, object]:
    fvp = parse_storage_test_403(fvp_text)
    qbox = parse_storage_test_403(qbox_text)
    missing_in_qbox: list[str] = []
    missing_steps: dict[str, list[str]] = {}
    stage_delta: dict[str, dict[str, str]] = {}

    fvp_by_ut = fvp["by_ut"]
    qbox_by_ut = qbox["by_ut"]
    assert isinstance(fvp_by_ut, dict)
    assert isinstance(qbox_by_ut, dict)

    for ut in ("ITS", "PS"):
        fvp_section = fvp_by_ut.get(ut)
        qbox_section = qbox_by_ut.get(ut)
        stage_delta[ut] = {
            "fvp": storage_stage(fvp_section),
            "qbox": storage_stage(qbox_section),
        }
        missing_steps[ut] = missing_storage_steps(ut, fvp_section, qbox_section)
        missing_in_qbox.extend(missing_steps[ut])

    return {
        "passed": not missing_in_qbox,
        "fvp": fvp,
        "qbox": qbox,
        "stage_delta": stage_delta,
        "missing_steps": missing_steps,
        "missing_in_qbox_from_fvp": missing_in_qbox,
    }


def compare(
    fvp_text: str, qbox_text: str, require_secure_storage: bool = False
) -> dict[str, object]:
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
    boot_passed = (
        not any(missing_in_qbox.values())
        and not any(required_missing.values())
        and linux_ok
        and qbox_order_ok
    )
    storage_test_403 = compare_storage_test_403(fvp_text, qbox_text)
    passed = boot_passed and (
        not require_secure_storage or bool(storage_test_403["passed"])
    )
    return {
        "passed": passed,
        "boot_passed": boot_passed,
        "fvp_marker_hits": fvp_hits,
        "qbox_marker_hits": qbox_hits,
        "missing_in_qbox_from_fvp": missing_in_qbox,
        "required_missing_in_qbox": required_missing,
        "linux_ok": linux_ok,
        "qbox_ordered_marker_positions": qbox_positions,
        "qbox_order_ok": qbox_order_ok,
        "secure_storage_required": require_secure_storage,
        "storage_test_403": storage_test_403,
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
    parser.add_argument(
        "--require-secure-storage",
        action="store_true",
        help="Fail when FVP completes ITS/PS test 403 but QBox does not.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = compare(
        read_text(args.fvp),
        read_text(args.qbox),
        require_secure_storage=args.require_secure_storage,
    )
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
