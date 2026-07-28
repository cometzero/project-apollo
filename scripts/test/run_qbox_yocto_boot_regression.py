#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import signal
import shlex
import subprocess
import sys
import threading
import time
from types import FrameType
from typing import Any, NoReturn


ROOT = Path(__file__).resolve().parents[2]
SUPPORTED_MACHINES = ("apollo-fvp", "apollo-qvp")
DEFAULT_MACHINE = "apollo-qvp"
LOGIN_PROMPT_MARKERS = ("apollo-fvp login:", "apollo-qvp login:")
SCHEMA_VERSION = 1
DEFAULT_THRESHOLD = 0.20
DEFAULT_POLL_INTERVAL = 0.5
LIVE_TIMING_FILE = "qbox-live-line-timing.json"
EXPECTED_AP_CPU_TIMER_LINE = "arch_timer: cp15 timer running at 125.00MHz (phys)."
EXPECTED_AP_MMIO_TIMER_LINE = (
    "arch-timer-mmio 1a810000.timer: mmio timer running at 125.00MHz (phys)"
)
CURRENT_BASELINE_AP_MMIO_TIMER_LINE = (
    "arch-timer-mmio 1a810000.timer: mmio timer running at 19.20MHz (phys)"
)
AP_MMIO_TIMER_PREFIX = "arch-timer-mmio 1a810000.timer:"
TIMER_HEALTH_LOGS = {
    "qbox-primary-console.log",
    "qbox-platform.log",
    "qbox-rse.log",
    "qbox-scp.log",
    "qbox-safety-island-cl0.log",
}
TIMER_SHADOW_WARNING_RE = re.compile(
    r"css_counters_timers.*shadowed|refclk.*shadowed|syscntr.*shadowed",
    re.IGNORECASE,
)
TIMER_BAD_RE = re.compile(
    r"\b(?:timer|counter|syscntr|refclk|css_counters_timers)\b.*"
    r"\b(?:error|failed|failure|fatal|regression)\b|"
    r"\b(?:error|failed|failure|fatal|regression)\b.*"
    r"\b(?:timer|counter|syscntr|refclk|css_counters_timers)\b",
    re.IGNORECASE,
)
QBOX_PROCESS_PATTERNS = [
    "platforms-vp",
    "run_qbox_yocto.sh",
    "run_qbox_apollo_fvp_full.py",
]
IMAGE_OPTIONS = {
    "--rootfs",
    "--efi-capsule-disk",
    "--rse-rom",
    "--rse-flash",
    "--rse-otp",
    "--ap-flash",
    "--ap-dtb",
    "--si-cl0-image",
    "--si-cl1-image",
}

KNOWN_LOG_ORDER = [
    "qbox-runner.log",
    "qbox-platform.log",
    "qbox-rse.log",
    "qbox-secure-console.log",
    "qbox-safety-island-cl0.log",
    "qbox-safety-island-cl1.log",
    "qbox-primary-console.log",
]

DEFAULT_ERROR_REGEXES = [
    r"Kernel panic",
    r"Unable to mount root fs",
    r"No working init found",
    r"\bOops\b",
    r"Call trace:",
    r"Unhandled exception",
    r"Segmentation fault",
    r"\bFATAL\b",
    r"\[ERROR\]",
    r"\[ERR\]",
    r"<err>",
    r"\bE/[A-Z]+:",
    r"\bERROR:",
    r"Error while ",
]

LOG_STAGE_DEFS = [
    {
        "name": "si_cl0_gic_multiview_configured",
        "subsystem": "si_cl0",
        "label": "SI CL0 GIC multiview configured",
        "log": "qbox-safety-island-cl0.log",
        "marker": "GIC-multiview configured successfully",
    },
    {
        "name": "si_cl0_scp_started",
        "subsystem": "si_cl0",
        "label": "SI CL0 SCP started",
        "log": "qbox-safety-island-cl0.log",
        "marker": "[SI0_PLATFORM] SCP started",
    },
    {
        "name": "si_cl0_module_init_complete",
        "subsystem": "si_cl0",
        "label": "SI CL0 module init complete",
        "log": "qbox-safety-island-cl0.log",
        "marker": "[FWK] Module initialization complete!",
    },
    {
        "name": "si_cl1_cpu0_oor",
        "subsystem": "si_cl1",
        "label": "SI CL1 CPU0 out of reset",
        "log": "qbox-safety-island-cl1.log",
        "marker": "Out of Reset (OoR) completed on CPU: 0",
    },
    {
        "name": "si_cl1_zephyr_boot",
        "subsystem": "si_cl1",
        "label": "SI CL1 Zephyr boot",
        "log": "qbox-safety-island-cl1.log",
        "marker": "Booting Zephyr OS",
    },
    {
        "name": "si_cl1_pfdi_agent",
        "subsystem": "si_cl1",
        "label": "SI CL1 PFDI agent ready",
        "log": "qbox-safety-island-cl1.log",
        "marker": "PFDI Agent setup complete",
    },
    {
        "name": "si_cl1_pfdi_service",
        "subsystem": "si_cl1",
        "label": "SI CL1 PFDI service ready",
        "log": "qbox-safety-island-cl1.log",
        "marker": "PFDI service ready",
    },
    {
        "name": "si_cl1_network_configured",
        "subsystem": "si_cl1",
        "label": "SI CL1 network configured",
        "log": "qbox-safety-island-cl1.log",
        "marker": "si_net_init: Network interface configured",
    },
    {
        "name": "secure_bl2_console",
        "subsystem": "secure_console",
        "label": "Secure console BL2",
        "log": "qbox-secure-console.log",
        "marker": "NOTICE:  BL2:",
    },
    {
        "name": "secure_bl31_console",
        "subsystem": "secure_console",
        "label": "Secure console BL31",
        "log": "qbox-secure-console.log",
        "marker": "NOTICE:  BL31:",
    },
    {
        "name": "secure_optee_console",
        "subsystem": "secure_console",
        "label": "Secure console OP-TEE",
        "log": "qbox-secure-console.log",
        "marker": "OP-TEE version:",
    },
    {
        "name": "primary_uboot_console",
        "subsystem": "primary_console",
        "label": "Primary console U-Boot",
        "log": "qbox-primary-console.log",
        "marker": "U-Boot ",
    },
    {
        "name": "primary_linux_cpu_log",
        "subsystem": "primary_console",
        "label": "Primary console Linux CPU boot",
        "log": "qbox-primary-console.log",
        "marker": "Booting Linux on physical CPU",
    },
    {
        "name": "primary_login_prompt_log",
        "subsystem": "primary_console",
        "label": "Primary console login prompt",
        "log": "qbox-primary-console.log",
        "marker": LOGIN_PROMPT_MARKERS[0],
        "markers": list(LOGIN_PROMPT_MARKERS),
    },
]

LOG_PREFS = {
    "rse": ["qbox-rse.log", "qbox-runner.log"],
    "ap_firmware": ["qbox-rse.log", "qbox-secure-console.log", "qbox-primary-console.log"],
    "primary_console": ["qbox-primary-console.log"],
    "primary": ["qbox-primary-console.log"],
    "secure_console": ["qbox-secure-console.log"],
    "si_cl0": ["qbox-safety-island-cl0.log"],
    "si_cl1": ["qbox-safety-island-cl1.log"],
}

ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
LINUX_TS_RE = re.compile(r"\[\s*(?P<seconds>\d+\.\d+)\]")
ZEPHYR_TS_RE = re.compile(
    r"\[(?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})"
    r"\.(?P<millis>\d{3}),(?P<micros>\d{3})\]"
)


class RegressionFailure(RuntimeError):
    pass


def result_root_for_machine(machine: str) -> Path:
    return ROOT / f"build/qbox-{machine}"


def baseline_for_machine(machine: str) -> Path:
    return result_root_for_machine(machine) / "run_qbox_yocto_baseline.json"


def raise_keyboard_interrupt(_signum: int, _frame: FrameType | None) -> NoReturn:
    raise KeyboardInterrupt


def install_signal_handlers() -> None:
    signal.signal(signal.SIGTERM, raise_keyboard_interrupt)


def clean_line(line: str) -> str:
    return ANSI_RE.sub("", line).replace("\r", "")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_elapsed_from_line(line: str, line_number: int) -> float | None:
    zephyr = ZEPHYR_TS_RE.search(line)
    if zephyr:
        return (
            int(zephyr.group("hours")) * 3600
            + int(zephyr.group("minutes")) * 60
            + int(zephyr.group("seconds"))
            + int(zephyr.group("millis")) / 1000
            + int(zephyr.group("micros")) / 1_000_000
        )
    linux = LINUX_TS_RE.search(line)
    if linux:
        return float(linux.group("seconds"))
    if line_number == 1:
        return 0.0
    return None


def resolve_logged_path(result_dir: Path, value: str) -> Path:
    path = Path(value)
    if path.exists():
        return path
    fallback = result_dir / path.name
    return fallback


def load_result_files(result_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    result_json = result_dir / "result.json"
    child_json = result_dir / "rd-aspen-result.json"
    result = read_json(result_json) if result_json.exists() else {}

    child_ref = result.get("child_result")
    if isinstance(child_ref, str):
        candidate = Path(child_ref)
        if not candidate.exists():
            candidate = result_dir / candidate.name
        if candidate.exists():
            child_json = candidate

    child = read_json(child_json) if child_json.exists() else {}
    if not result and not child:
        raise RegressionFailure(f"no result JSON found under {result_dir}")
    return result, child


def result_json_ready(result_dir: Path) -> bool:
    for path in (result_dir / "result.json", result_dir / "rd-aspen-result.json"):
        if not path.exists():
            continue
        try:
            read_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        return True
    return False


def last_lines(path: Path, count: int) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-count:]


def complete_log_lines(text: str) -> list[str]:
    lines = text.splitlines()
    if text and not text.endswith(("\n", "\r")):
        return lines[:-1]
    return lines


def split_complete_and_partial_log_lines(text: str) -> tuple[list[str], tuple[int, str] | None]:
    lines = text.splitlines()
    if text and not text.endswith(("\n", "\r")) and lines:
        return lines[:-1], (len(lines), lines[-1])
    return lines, None


def run_status(result_dir: Path) -> str | None:
    path = result_dir / "qbox-run.status"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8", errors="replace").strip() or None


def wait_for_run_result(result_dir: Path, *, wait_timeout: float, poll_interval: float) -> None:
    deadline = time.monotonic() + wait_timeout
    while time.monotonic() <= deadline:
        if result_json_ready(result_dir):
            return
        status = run_status(result_dir)
        if (result_dir / ".qbox-run.done").exists() and status not in (None, "0", "running"):
            details = [
                f"runner status: {status}",
                f"result dir: {result_dir}",
                "qbox-runner.log tail:",
                *[f"  {line}" for line in last_lines(result_dir / "qbox-runner.log", 40)],
            ]
            raise RegressionFailure(
                "run_qbox_yocto.sh finished before writing result JSON:\n"
                + "\n".join(details)
            )
        time.sleep(poll_interval)

    details = [
        f"wait_timeout_s: {wait_timeout:.1f}",
        f"runner status: {run_status(result_dir) or 'unknown'}",
        f"result dir: {result_dir}",
        "qbox-runner.log tail:",
        *[f"  {line}" for line in last_lines(result_dir / "qbox-runner.log", 40)],
    ]
    raise RegressionFailure("timed out waiting for result JSON:\n" + "\n".join(details))


def log_paths_from_results(result_dir: Path, result: dict[str, Any], child: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    seen: set[Path] = set()

    def add(path: Path) -> None:
        resolved = path.resolve() if path.exists() else path
        if resolved not in seen and path.exists() and path.is_file():
            seen.add(resolved)
            paths.append(path)

    for item in (result, child):
        console_logs = item.get("console_logs")
        if isinstance(console_logs, dict):
            for value in console_logs.values():
                if isinstance(value, str):
                    add(resolve_logged_path(result_dir, value))
        platform_log = item.get("platform_stdout_log")
        if isinstance(platform_log, str):
            add(resolve_logged_path(result_dir, platform_log))

    for name in KNOWN_LOG_ORDER:
        add(result_dir / name)
    for path in sorted(result_dir.glob("*.log")):
        add(path)
    return paths


def load_logs(result_dir: Path, result: dict[str, Any], child: dict[str, Any]) -> list[dict[str, Any]]:
    logs = []
    for path in log_paths_from_results(result_dir, result, child):
        text = path.read_text(encoding="utf-8", errors="replace")
        logs.append(
            {
                "path": path,
                "name": path.name,
                "text": text,
                "lines": text.splitlines(),
            }
        )
    return logs


def infer_subsystem(name: str) -> str:
    if name.startswith("rse_"):
        return "rse"
    if name.startswith("primary_"):
        return "primary_console"
    if name.startswith("secure_"):
        return "secure_console"
    if name.startswith("measured_boot"):
        return "ap_firmware"
    return "qbox"


def preferred_logs(logs: list[dict[str, Any]], subsystem: str) -> list[dict[str, Any]]:
    preferred_names = LOG_PREFS.get(subsystem, [])
    preferred = [log for name in preferred_names for log in logs if log["name"] == name]
    rest = [log for log in logs if log not in preferred]
    return preferred + rest


def marker_candidates(name: str, marker: str | None) -> list[str]:
    if name == "primary_login_prompt" or marker in LOGIN_PROMPT_MARKERS:
        return list(LOGIN_PROMPT_MARKERS)
    return [marker] if marker else []


def find_marker(
    logs: list[dict[str, Any]], markers: list[str], subsystem: str
) -> dict[str, Any] | None:
    if not markers:
        return None
    for log in preferred_logs(logs, subsystem):
        for index, line in enumerate(log["lines"], start=1):
            clean = clean_line(line)
            for marker in markers:
                if marker in clean:
                    return {
                        "log": str(log["path"]),
                        "log_name": log["name"],
                        "line_number": index,
                        "line": clean,
                        "marker": marker,
                        "elapsed_s": parse_elapsed_from_line(line, index),
                    }
    return None


def normalize_elapsed(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value), 6)
    except (TypeError, ValueError):
        return None


def add_stage(
    stages: list[dict[str, Any]],
    seen_names: set[str],
    *,
    name: str,
    subsystem: str,
    label: str,
    marker: str | None,
    elapsed_s: float | None,
    source: str,
    logs: list[dict[str, Any]],
    optional: bool = False,
    markers: list[str] | None = None,
) -> None:
    if name in seen_names:
        return
    marker_list = markers if markers is not None else marker_candidates(name, marker)
    hit = find_marker(logs, marker_list, subsystem)
    if elapsed_s is None and hit is not None:
        elapsed_s = normalize_elapsed(hit.get("elapsed_s"))
    if hit is not None and str(hit.get("line") or "").startswith("\x00"):
        elapsed_s = None
    stages.append(
        {
            "name": name,
            "subsystem": subsystem,
            "label": label,
            "marker": marker,
            "markers": marker_list,
            "observed_marker": hit.get("marker") if hit else None,
            "seen": hit is not None or elapsed_s is not None,
            "optional": optional,
            "elapsed_s": normalize_elapsed(elapsed_s),
            "source": source,
            "log": hit.get("log") if hit else None,
            "line_number": hit.get("line_number") if hit else None,
            "line": hit.get("line") if hit else None,
        }
    )
    seen_names.add(name)


def profile_from_results(result: dict[str, Any], child: dict[str, Any]) -> dict[str, Any]:
    for item in (result, child):
        profile = item.get("rse_boot_timing_profile")
        if isinstance(profile, dict) and isinstance(profile.get("markers"), list):
            return profile
    return {}


def progress_hits_from_results(result: dict[str, Any], child: dict[str, Any]) -> dict[str, dict[str, Any]]:
    for item in (child, result):
        hits = item.get("progress_marker_first_hits")
        if isinstance(hits, dict):
            return {str(key): value for key, value in hits.items() if isinstance(value, dict)}
    return {}


def extract_stages(result: dict[str, Any], child: dict[str, Any], logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stages: list[dict[str, Any]] = []
    seen_names: set[str] = set()

    for marker in profile_from_results(result, child).get("markers", []):
        if not isinstance(marker, dict):
            continue
        name = str(marker.get("name") or "")
        if not name:
            continue
        subsystem = infer_subsystem(name)
        add_stage(
            stages,
            seen_names,
            name=name,
            subsystem=subsystem,
            label=str(marker.get("label") or name),
            marker=marker.get("marker") if isinstance(marker.get("marker"), str) else None,
            elapsed_s=normalize_elapsed(marker.get("elapsed_s")),
            source="rse_boot_timing_profile",
            logs=logs,
            markers=marker_candidates(
                name,
                marker.get("marker") if isinstance(marker.get("marker"), str) else None,
            ),
        )

    progress_hits = progress_hits_from_results(result, child)
    for name, hit in sorted(
        progress_hits.items(),
        key=lambda item: normalize_elapsed(item[1].get("elapsed_s")) or 0.0,
    ):
        add_stage(
            stages,
            seen_names,
            name=name,
            subsystem=infer_subsystem(name),
            label=name,
            marker=hit.get("marker") if isinstance(hit.get("marker"), str) else None,
            elapsed_s=normalize_elapsed(hit.get("elapsed_s")),
            source="progress_marker_first_hits",
            logs=logs,
            markers=marker_candidates(
                name,
                hit.get("marker") if isinstance(hit.get("marker"), str) else None,
            ),
        )

    for stage_def in LOG_STAGE_DEFS:
        log = next((item for item in logs if item["name"] == stage_def["log"]), None)
        stage_logs = [log] if log else logs
        add_stage(
            stages,
            seen_names,
            name=str(stage_def["name"]),
            subsystem=str(stage_def["subsystem"]),
            label=str(stage_def["label"]),
            marker=str(stage_def["marker"]),
            elapsed_s=None,
            source="console_log",
            logs=stage_logs,
            optional=bool(stage_def.get("optional")),
            markers=stage_def.get("markers") if isinstance(stage_def.get("markers"), list) else None,
        )

    return stages


def result_status_failures(result: dict[str, Any], child: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if result and result.get("passed") is False:
        failures.append(f"result.json passed=false blocker={result.get('blocker')!r}")
    if child and child.get("passed") is False:
        failures.append(f"rd-aspen-result.json passed=false blocker={child.get('blocker')!r}")

    for label, item in (("result.json", result), ("rd-aspen-result.json", child)):
        fail_patterns = item.get("fail_patterns")
        if isinstance(fail_patterns, dict):
            hits = [pattern for pattern, hit in fail_patterns.items() if hit]
            if hits:
                failures.append(f"{label} fail_patterns hit: {', '.join(hits)}")
    return failures


def compile_regexes(patterns: list[str]) -> list[tuple[str, re.Pattern[str]]]:
    return [(pattern, re.compile(pattern, re.IGNORECASE)) for pattern in patterns]


def ignored_line(line: str, ignore_regexes: list[tuple[str, re.Pattern[str]]]) -> bool:
    return any(regex.search(line) for _pattern, regex in ignore_regexes)


def scan_error_logs(
    logs: list[dict[str, Any]],
    error_regexes: list[str],
    ignore_regexes: list[str],
) -> list[dict[str, Any]]:
    compiled_errors = compile_regexes(error_regexes)
    compiled_ignores = compile_regexes(ignore_regexes)
    matches: list[dict[str, Any]] = []
    for log in logs:
        for index, raw_line in enumerate(log["lines"], start=1):
            line = clean_line(raw_line)
            if ignored_line(line, compiled_ignores):
                continue
            for pattern, regex in compiled_errors:
                if regex.search(line):
                    matches.append(
                        {
                            "pattern": pattern,
                            "log": str(log["path"]),
                            "log_name": log["name"],
                            "line_number": index,
                            "line": line,
                        }
                    )
                    break
    return matches


def log_line_record(log: dict[str, Any], line_number: int, line: str) -> dict[str, Any]:
    return {
        "log": str(log["path"]),
        "log_name": log["name"],
        "line_number": line_number,
        "line": line,
    }


def find_log_line(
    logs: list[dict[str, Any]], expected: str, *, log_name: str | None = None
) -> dict[str, Any] | None:
    for log in logs:
        if log_name is not None and log["name"] != log_name:
            continue
        for index, raw_line in enumerate(log["lines"], start=1):
            line = clean_line(raw_line)
            if expected in line:
                return log_line_record(log, index, line)
    return None


def find_prefixed_log_lines(
    logs: list[dict[str, Any]], prefix: str, *, log_name: str | None = None
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for log in logs:
        if log_name is not None and log["name"] != log_name:
            continue
        for index, raw_line in enumerate(log["lines"], start=1):
            line = clean_line(raw_line)
            if prefix in line:
                matches.append(log_line_record(log, index, line))
    return matches


def scan_timer_health_logs(logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for log in logs:
        if log["name"] not in TIMER_HEALTH_LOGS:
            continue
        for index, raw_line in enumerate(log["lines"], start=1):
            line = clean_line(raw_line)
            if TIMER_SHADOW_WARNING_RE.search(line):
                match = log_line_record(log, index, line)
                match["check"] = "timer_window_shadow_warning"
                matches.append(match)
                continue
            if TIMER_BAD_RE.search(line):
                match = log_line_record(log, index, line)
                match["check"] = "timer_related_error"
                matches.append(match)
    return matches


def extract_timer_topology(logs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ap_cpu_timer": find_log_line(
            logs,
            EXPECTED_AP_CPU_TIMER_LINE,
            log_name="qbox-primary-console.log",
        ),
        "ap_mmio_timer_expected": find_log_line(
            logs,
            EXPECTED_AP_MMIO_TIMER_LINE,
            log_name="qbox-primary-console.log",
        ),
        "ap_mmio_timer_current_baseline": find_log_line(
            logs,
            CURRENT_BASELINE_AP_MMIO_TIMER_LINE,
            log_name="qbox-primary-console.log",
        ),
        "ap_mmio_timer_lines": find_prefixed_log_lines(
            logs,
            AP_MMIO_TIMER_PREFIX,
            log_name="qbox-primary-console.log",
        ),
        "timer_health_matches": scan_timer_health_logs(logs),
    }


def timer_topology_location(hit: dict[str, Any] | None) -> tuple[str | None, int | None]:
    if hit is None:
        return None, None
    log = hit.get("log") if isinstance(hit.get("log"), str) else None
    line_number = hit.get("line_number") if isinstance(hit.get("line_number"), int) else None
    return log, line_number


def require_timer_topology(
    snapshot: dict[str, Any], *, context: int, allow_current_baseline: bool
) -> dict[str, Any]:
    timer = snapshot["timer_topology"]
    cpu_hit = timer.get("ap_cpu_timer")
    if not isinstance(cpu_hit, dict):
        raise RegressionFailure(
            "AP CPU timer line missing or changed:\n"
            f"  expected: {EXPECTED_AP_CPU_TIMER_LINE}"
        )

    mmio_hit = timer.get("ap_mmio_timer_expected")
    current_baseline_hit = timer.get("ap_mmio_timer_current_baseline")
    baseline_allowed = allow_current_baseline and isinstance(current_baseline_hit, dict)
    if not isinstance(mmio_hit, dict) and not baseline_allowed:
        observed = timer.get("ap_mmio_timer_lines")
        observed_items = observed if isinstance(observed, list) else []
        observed_lines = [
            f"  observed: {item.get('line')}"
            for item in observed_items
            if isinstance(item, dict)
        ]
        details = [
            "AP MMIO timer mismatch:",
            f"  expected: {EXPECTED_AP_MMIO_TIMER_LINE}",
            f"  known old baseline: {CURRENT_BASELINE_AP_MMIO_TIMER_LINE}",
            "  use --allow-current-timer-baseline only for explicit baseline characterization",
            *observed_lines,
        ]
        first_observed = next(
            (item for item in observed_items if isinstance(item, dict)),
            None,
        )
        log, line_number = timer_topology_location(first_observed)
        fail_with_log_context(
            "timer topology regression detected",
            log=log,
            line_number=line_number,
            context=context,
            details=details,
        )

    timer_health_matches = timer.get("timer_health_matches")
    if isinstance(timer_health_matches, list) and timer_health_matches:
        match = next((item for item in timer_health_matches if isinstance(item, dict)), None)
        if match is not None:
            log, line_number = timer_topology_location(match)
            fail_with_log_context(
                "timer topology regression detected",
                log=log,
                line_number=line_number,
                context=context,
                details=[
                    f"check: {match.get('check')}",
                    f"line: {match.get('line')}",
                    "timer-related platform shadow warnings are not allowlisted",
                ],
            )

    return {
        "ap_cpu_timer": str(cpu_hit.get("line")),
        "ap_mmio_timer": (
            str(mmio_hit.get("line"))
            if isinstance(mmio_hit, dict)
            else str(current_baseline_hit.get("line"))
        ),
        "allowed_current_timer_baseline": baseline_allowed,
        "timer_health_match_count": len(timer_health_matches)
        if isinstance(timer_health_matches, list)
        else 0,
    }


def build_snapshot(
    result_dir: Path,
    *,
    threshold: float,
    error_regexes: list[str],
    ignore_error_regexes: list[str],
) -> dict[str, Any]:
    result, child = load_result_files(result_dir)
    logs = load_logs(result_dir, result, child)
    stages = extract_stages(result, child, logs)
    apply_live_line_timings(result_dir, stages)
    return {
        "schema_version": SCHEMA_VERSION,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "result_dir": str(result_dir.resolve()),
        "threshold": threshold,
        "error_regexes": error_regexes,
        "ignore_error_regexes": ignore_error_regexes,
        "result_status_failures": result_status_failures(result, child),
        "error_matches": scan_error_logs(logs, error_regexes, ignore_error_regexes),
        "timer_topology": extract_timer_topology(logs),
        "logs": [
            {
                "name": log["name"],
                "path": str(log["path"]),
                "bytes": len(log["text"].encode("utf-8", errors="replace")),
            }
            for log in logs
        ],
        "stages": stages,
    }


def context_lines(path: Path, line_number: int | None, context: int) -> list[str]:
    if line_number is None or not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(1, line_number - context)
    end = min(len(lines), line_number + context)
    return [f"{idx}: {clean_line(lines[idx - 1])}" for idx in range(start, end + 1)]


def fail_with_log_context(
    title: str,
    *,
    log: str | None,
    line_number: int | None,
    context: int,
    details: list[str],
) -> NoReturn:
    lines = [title, *details]
    if log and line_number:
        lines.append(f"context: {log}:{line_number}")
        lines.extend(f"  {line}" for line in context_lines(Path(log), line_number, context))
    raise RegressionFailure("\n".join(lines))


def print_stage_pass(
    *,
    stage_name: str,
    label: str,
    baseline_elapsed: float,
    current_elapsed: float,
    allowed_elapsed: float,
    threshold: float,
    log: str | None,
    line_number: int | None,
) -> None:
    location = f"{log}:{line_number}" if log and line_number else "unknown"
    print(
        "PASS boot stage: "
        f"{stage_name} ({label}) "
        f"baseline_elapsed_s={baseline_elapsed:.3f} "
        f"current_elapsed_s={current_elapsed:.3f} "
        f"allowed_elapsed_s={allowed_elapsed:.3f} "
        f"threshold=+{threshold * 100:.1f}% "
        f"context={location}",
        flush=True,
    )


def require_clean_baseline(
    snapshot: dict[str, Any], *, fail_on_baseline_errors: bool, context: int
) -> None:
    if snapshot["result_status_failures"]:
        raise RegressionFailure(
            "baseline result is not passing:\n"
            + "\n".join(f"  {failure}" for failure in snapshot["result_status_failures"])
        )
    missing = [
        stage
        for stage in snapshot["stages"]
        if not stage.get("seen") and not stage.get("optional")
    ]
    if missing:
        stage = missing[0]
        raise RegressionFailure(
            "baseline is missing required boot stage:\n"
            f"  {stage['name']} ({stage['label']}) marker={stage.get('marker')!r}"
        )
    if snapshot["error_matches"] and fail_on_baseline_errors:
        match = snapshot["error_matches"][0]
        fail_with_log_context(
            "baseline contains an error log match",
            log=match.get("log"),
            line_number=match.get("line_number"),
            context=context,
            details=[
                f"pattern: {match.get('pattern')}",
                f"line: {match.get('line')}",
            ],
        )
    if not any(stage.get("elapsed_s") and stage.get("elapsed_s") > 0 for stage in snapshot["stages"]):
        raise RegressionFailure("baseline has no timed boot stages")


def error_fingerprint(match: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(match.get("log_name") or Path(str(match.get("log") or "")).name),
        str(match.get("pattern") or ""),
        str(match.get("line") or ""),
    )


def realtime_log_paths(result_dir: Path) -> list[Path]:
    paths: list[Path] = []
    seen: set[Path] = set()
    for path in [*(result_dir / name for name in KNOWN_LOG_ORDER), *sorted(result_dir.glob("*.log"))]:
        if path in seen:
            continue
        seen.add(path)
        paths.append(path)
    return paths


def realtime_stage_log_allowed(stage: dict[str, Any], path: Path) -> bool:
    subsystem = str(stage.get("subsystem") or "")
    preferred = [name for name in LOG_PREFS.get(subsystem, []) if name != "qbox-runner.log"]
    if preferred:
        return path.name in preferred
    log = stage.get("log")
    if isinstance(log, str):
        return path.name == Path(log).name
    return path.name != "qbox-runner.log"


def live_line_timing_key(path: Path, line_number: int) -> str:
    return f"{path.resolve(strict=False)}:{line_number}"


def load_live_line_timings(result_dir: Path) -> dict[str, float]:
    path = result_dir / LIVE_TIMING_FILE
    if not path.exists():
        return {}
    try:
        raw = read_json(path)
    except (OSError, json.JSONDecodeError):
        return {}
    timings = raw.get("line_elapsed_s")
    if not isinstance(timings, dict):
        return {}
    parsed: dict[str, float] = {}
    for key, value in timings.items():
        elapsed = normalize_elapsed(value)
        if isinstance(key, str) and elapsed is not None:
            parsed[key] = elapsed
    return parsed


def apply_live_line_timings(result_dir: Path, stages: list[dict[str, Any]]) -> None:
    timings = load_live_line_timings(result_dir)
    if not timings:
        return
    for stage in stages:
        log = stage.get("log")
        line_number = stage.get("line_number")
        line = stage.get("line")
        if not isinstance(log, str) or not isinstance(line_number, int) or not isinstance(line, str):
            continue
        if line.startswith("\x00"):
            continue
        if parse_elapsed_from_line(line, line_number) is not None:
            continue
        elapsed = timings.get(live_line_timing_key(Path(log), line_number))
        if elapsed is not None:
            stage["elapsed_s"] = elapsed
            stage["source"] = f"{stage.get('source')}+live_line_timing"


class RealtimeLineTimingRecorder:
    def __init__(self, *, result_dir: Path) -> None:
        self.result_dir = result_dir
        self.line_counts: dict[Path, int] = {}
        self.line_elapsed_s: dict[str, float] = {}
        self.partial_lines: dict[str, str] = {}
        self.start_time = time.monotonic()

    def poll(self) -> None:
        for path in realtime_log_paths(self.result_dir):
            if not path.exists() or not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            lines, partial = split_complete_and_partial_log_lines(text)
            start = self.line_counts.get(path, 0)
            if len(lines) < start:
                start = 0
            elapsed = round(time.monotonic() - self.start_time, 6)
            for index, _raw_line in enumerate(lines[start:], start=start + 1):
                self.line_elapsed_s.setdefault(live_line_timing_key(path, index), elapsed)
            self.line_counts[path] = len(lines)
            if partial is not None:
                line_number, raw_line = partial
                key = live_line_timing_key(path, line_number)
                if self.partial_lines.get(key) != raw_line:
                    self.partial_lines[key] = raw_line
                    self.line_elapsed_s[key] = elapsed

    def write(self) -> None:
        if not self.line_elapsed_s:
            return
        write_json(
            self.result_dir / LIVE_TIMING_FILE,
            {
                "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "line_elapsed_s": self.line_elapsed_s,
            },
        )


class RealtimeLogMonitor:
    def __init__(
        self,
        *,
        baseline: dict[str, Any],
        result_dir: Path,
        threshold: float,
        error_regexes: list[str],
        ignore_regexes: list[str],
        context: int,
        allow_current_timer_baseline: bool,
    ) -> None:
        self.baseline_errors = {
            error_fingerprint(match) for match in baseline.get("error_matches", [])
        }
        self.result_dir = result_dir
        self.threshold = threshold
        self.error_regexes = compile_regexes(error_regexes)
        self.ignore_regexes = compile_regexes(ignore_regexes)
        self.context = context
        self.allow_current_timer_baseline = allow_current_timer_baseline
        self.line_counts: dict[Path, int] = {}
        self.start_time = time.monotonic()
        self.stage_seen: set[str] = set()
        self.stages = [
            stage
            for stage in baseline.get("stages", [])
            if stage_marker_candidates(stage)
            and (normalize_elapsed(stage.get("elapsed_s")) or 0.0) > 0.0
            and not stage.get("optional")
        ]

    def poll(self) -> None:
        for path in realtime_log_paths(self.result_dir):
            if not path.exists() or not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            lines, partial = split_complete_and_partial_log_lines(text)
            start = self.line_counts.get(path, 0)
            if len(lines) < start:
                start = 0
            for index, raw_line in enumerate(lines[start:], start=start + 1):
                self.check_line(path, index, raw_line, complete=True)
            self.line_counts[path] = len(lines)
            if partial is not None:
                line_number, raw_line = partial
                self.check_line(path, line_number, raw_line, complete=False)
        self.check_overdue_stages()

    def stage_context_location(self, stage: dict[str, Any]) -> tuple[str | None, int | None]:
        candidate_names: list[str] = []
        subsystem = str(stage.get("subsystem") or "")
        candidate_names.extend(LOG_PREFS.get(subsystem, []))
        log = stage.get("log")
        if isinstance(log, str):
            candidate_names.append(Path(log).name)
        for path in [self.result_dir / name for name in candidate_names]:
            if not path.exists() or not path.is_file():
                continue
            lines = complete_log_lines(path.read_text(encoding="utf-8", errors="replace"))
            return str(path), len(lines) if lines else None
        return None, None

    def check_overdue_stages(self) -> None:
        current_elapsed = time.monotonic() - self.start_time
        for stage in self.stages:
            name = str(stage.get("name") or "")
            if not name or name in self.stage_seen:
                continue
            if "+live_line_timing" not in str(stage.get("source") or ""):
                continue
            baseline_elapsed = normalize_elapsed(stage.get("elapsed_s"))
            if baseline_elapsed is None or baseline_elapsed <= 0:
                continue
            allowed = baseline_elapsed * (1.0 + self.threshold)
            if current_elapsed <= allowed:
                continue
            log, line_number = self.stage_context_location(stage)
            fail_with_log_context(
                "boot stage overdue in current run",
                log=log,
                line_number=line_number,
                context=self.context,
                details=[
                    f"stage: {name} ({stage.get('label')})",
                    f"marker: {stage.get('marker')!r}",
                    f"baseline_elapsed_s: {baseline_elapsed:.3f}",
                    f"current_elapsed_s: {current_elapsed:.3f}",
                    f"allowed_elapsed_s: {allowed:.3f}",
                    f"threshold: +{self.threshold * 100:.1f}%",
                ],
            )

    def check_line(
        self, path: Path, line_number: int, raw_line: str, *, complete: bool = True
    ) -> None:
        line = clean_line(raw_line)
        self.check_timer_topology_line(path, line_number, line)
        if complete and not ignored_line(line, self.ignore_regexes):
            for pattern, regex in self.error_regexes:
                if not regex.search(line):
                    continue
                match = {
                    "pattern": pattern,
                    "log": str(path),
                    "log_name": path.name,
                    "line_number": line_number,
                    "line": line,
                }
                if error_fingerprint(match) not in self.baseline_errors:
                    fail_with_log_context(
                        "error log regression detected",
                        log=str(path),
                        line_number=line_number,
                        context=self.context,
                        details=[f"pattern: {pattern}", f"line: {line}"],
                    )
                break

        for stage in self.stages:
            name = str(stage.get("name") or "")
            markers = stage_marker_candidates(stage)
            if not name or name in self.stage_seen or not markers:
                continue
            if not realtime_stage_log_allowed(stage, path):
                continue
            observed_marker = next((marker for marker in markers if marker in line), None)
            if observed_marker is None:
                continue
            stage["observed_marker"] = observed_marker
            self.stage_seen.add(name)
            baseline_elapsed = normalize_elapsed(stage.get("elapsed_s"))
            if baseline_elapsed is None or baseline_elapsed <= 0:
                continue
            current_elapsed = parse_elapsed_from_line(raw_line, line_number)
            if current_elapsed is None:
                current_elapsed = time.monotonic() - self.start_time
            allowed = baseline_elapsed * (1.0 + self.threshold)
            if current_elapsed > allowed:
                fail_with_log_context(
                    "boot timing regression detected",
                    log=str(path),
                    line_number=line_number,
                    context=self.context,
                    details=[
                        f"stage: {name} ({stage.get('label')})",
                        f"baseline_elapsed_s: {baseline_elapsed:.3f}",
                        f"current_elapsed_s: {current_elapsed:.3f}",
                        f"allowed_elapsed_s: {allowed:.3f}",
                        f"threshold: +{self.threshold * 100:.1f}%",
                    ],
                )
            print_stage_pass(
                stage_name=name,
                label=str(stage.get("label")),
                baseline_elapsed=baseline_elapsed,
                current_elapsed=current_elapsed,
                allowed_elapsed=allowed,
                threshold=self.threshold,
                log=str(path),
                line_number=line_number,
            )

    def check_timer_topology_line(self, path: Path, line_number: int, line: str) -> None:
        if path.name not in TIMER_HEALTH_LOGS:
            return
        if TIMER_SHADOW_WARNING_RE.search(line):
            fail_with_log_context(
                "timer topology regression detected",
                log=str(path),
                line_number=line_number,
                context=self.context,
                details=[
                    "check: timer_window_shadow_warning",
                    f"line: {line}",
                    "timer-related platform shadow warnings are not allowlisted",
                ],
            )
        if TIMER_BAD_RE.search(line):
            fail_with_log_context(
                "timer topology regression detected",
                log=str(path),
                line_number=line_number,
                context=self.context,
                details=[
                    "check: timer_related_error",
                    f"line: {line}",
                ],
            )
        if path.name != "qbox-primary-console.log" or AP_MMIO_TIMER_PREFIX not in line:
            return
        if EXPECTED_AP_MMIO_TIMER_LINE in line:
            return
        if self.allow_current_timer_baseline and CURRENT_BASELINE_AP_MMIO_TIMER_LINE in line:
            return
        fail_with_log_context(
            "timer topology regression detected",
            log=str(path),
            line_number=line_number,
            context=self.context,
            details=[
                "AP MMIO timer mismatch:",
                f"  expected: {EXPECTED_AP_MMIO_TIMER_LINE}",
                f"  known old baseline: {CURRENT_BASELINE_AP_MMIO_TIMER_LINE}",
                f"  observed: {line}",
                "  use --allow-current-timer-baseline only for explicit baseline characterization",
            ],
        )


def compare_snapshot(
    baseline: dict[str, Any],
    current: dict[str, Any],
    *,
    threshold: float,
    context: int,
    emit_passes: bool,
) -> dict[str, Any]:
    baseline_errors = {
        error_fingerprint(match) for match in baseline.get("error_matches", [])
    }
    unknown_errors = [
        match
        for match in current["error_matches"]
        if error_fingerprint(match) not in baseline_errors
    ]
    if unknown_errors:
        match = unknown_errors[0]
        fail_with_log_context(
            "error log regression detected",
            log=match.get("log"),
            line_number=match.get("line_number"),
            context=context,
            details=[
                f"pattern: {match.get('pattern')}",
                f"line: {match.get('line')}",
            ],
        )
    if current["result_status_failures"]:
        raise RegressionFailure(
            "QBox Yocto boot result failed:\n"
            + "\n".join(f"  {failure}" for failure in current["result_status_failures"])
        )

    current_by_name = {stage["name"]: stage for stage in current["stages"]}
    checked = 0
    skipped_removed = 0
    for baseline_stage in baseline.get("stages", []):
        if baseline_stage.get("optional"):
            continue
        name = baseline_stage.get("name")
        current_stage = current_by_name.get(name)
        if not current_stage:
            skipped_removed += 1
            continue
        if not current_stage.get("seen"):
            raise RegressionFailure(
                "boot stage missing in current run:\n"
                f"  {name} ({baseline_stage.get('label')}) marker={baseline_stage.get('marker')!r}"
            )

        baseline_elapsed = normalize_elapsed(baseline_stage.get("elapsed_s"))
        if baseline_elapsed is None or baseline_elapsed <= 0:
            continue
        current_elapsed = normalize_elapsed(current_stage.get("elapsed_s"))
        if current_elapsed is None:
            fail_with_log_context(
                "boot stage timing missing in current run",
                log=current_stage.get("log"),
                line_number=current_stage.get("line_number"),
                context=context,
                details=[
                    f"stage: {name} ({baseline_stage.get('label')})",
                    f"baseline_elapsed_s: {baseline_elapsed:.3f}",
                ],
            )

        checked += 1
        allowed = baseline_elapsed * (1.0 + threshold)
        if current_elapsed > allowed:
            fail_with_log_context(
                "boot timing regression detected",
                log=current_stage.get("log"),
                line_number=current_stage.get("line_number"),
                context=context,
                details=[
                    f"stage: {name} ({baseline_stage.get('label')})",
                    f"baseline_elapsed_s: {baseline_elapsed:.3f}",
                    f"current_elapsed_s: {current_elapsed:.3f}",
                    f"allowed_elapsed_s: {allowed:.3f}",
                    f"threshold: +{threshold * 100:.1f}%",
                ],
            )
        if emit_passes:
            print_stage_pass(
                stage_name=str(name),
                label=str(baseline_stage.get("label")),
                baseline_elapsed=baseline_elapsed,
                current_elapsed=current_elapsed,
                allowed_elapsed=allowed,
                threshold=threshold,
                log=current_stage.get("log")
                if isinstance(current_stage.get("log"), str)
                else None,
                line_number=current_stage.get("line_number")
                if isinstance(current_stage.get("line_number"), int)
                else None,
            )

    return {
        "passed": True,
        "checked_timed_stages": checked,
        "baseline_stage_count": len(baseline.get("stages", [])),
        "current_stage_count": len(current.get("stages", [])),
        "skipped_removed_stage_count": skipped_removed,
        "baseline_error_match_count": len(baseline_errors),
        "current_error_match_count": len(current.get("error_matches", [])),
        "threshold": threshold,
    }


def stage_marker_candidates(stage: dict[str, Any]) -> list[str]:
    markers = stage.get("markers")
    if isinstance(markers, list):
        return [marker for marker in markers if isinstance(marker, str)]
    marker = stage.get("marker")
    return [marker] if isinstance(marker, str) else []


def latest_result_dir(root: Path) -> Path | None:
    candidates = []
    for path in root.iterdir() if root.exists() else []:
        if path.is_dir() and ((path / "result.json").exists() or (path / "rd-aspen-result.json").exists()):
            candidates.append(path)
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def process_cmdline(pid: int) -> str:
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return ""
    return raw.replace(b"\0", b" ").decode("utf-8", errors="replace").strip()


def is_qbox_process(pid: int) -> bool:
    cmdline = process_cmdline(pid)
    return any(pattern in cmdline for pattern in QBOX_PROCESS_PATTERNS)


def process_open_paths(pid: int) -> set[Path]:
    fd_dir = Path(f"/proc/{pid}/fd")
    paths: set[Path] = set()
    try:
        fds = list(fd_dir.iterdir())
    except OSError:
        return paths
    for fd in fds:
        try:
            target = fd.resolve(strict=True)
        except OSError:
            continue
        paths.add(target)
    return paths


def qbox_pids_holding_paths(paths: list[Path]) -> dict[int, list[Path]]:
    wanted = {path.resolve(strict=True) for path in paths if path.exists()}
    holders: dict[int, list[Path]] = {}
    if not wanted:
        return holders
    for proc_dir in Path("/proc").iterdir():
        if not proc_dir.name.isdigit():
            continue
        pid = int(proc_dir.name)
        if pid == os.getpid() or not is_qbox_process(pid):
            continue
        opened = process_open_paths(pid)
        hits = sorted(wanted.intersection(opened))
        if hits:
            holders[pid] = hits
    return holders


def terminate_process_groups_for_pids(pids: list[int], *, label: str) -> None:
    pgids: set[int] = set()
    for pid in pids:
        try:
            pgid = os.getpgid(pid)
        except ProcessLookupError:
            continue
        if pgid == os.getpgrp():
            continue
        pgids.add(pgid)
    if not pgids:
        return
    print(
        f"{label}: terminating QBox process groups: "
        + ", ".join(str(pgid) for pgid in sorted(pgids)),
        flush=True,
    )
    for pgid in sorted(pgids):
        try:
            os.killpg(pgid, signal.SIGTERM)
        except ProcessLookupError:
            continue
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if not any(pid_exists(pid) for pid in pids):
            return
        time.sleep(0.2)
    for pgid in sorted(pgids):
        try:
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            continue


def headless_runner_command(
    args: argparse.Namespace,
    runner_args: list[str],
    out_dir: Path,
    *,
    dry_run: bool = False,
) -> list[str]:
    command = [
        str(args.runner),
        "--headless",
        "--machine",
        str(args.machine),
        "--out-dir",
        str(out_dir),
        "--timeout",
        str(args.timeout),
        "--exit-after-pass",
    ]
    if dry_run:
        command.append("--dry-run")
    command.extend(remove_runner_machine_arg(runner_args))
    return command


def remove_runner_machine_arg(runner_args: list[str]) -> list[str]:
    cleaned: list[str] = []
    index = 0
    while index < len(runner_args):
        if runner_args[index] == "--machine" and index + 1 < len(runner_args):
            index += 2
            continue
        cleaned.append(runner_args[index])
        index += 1
    return cleaned


def dry_run_headless_command(
    args: argparse.Namespace,
    runner_args: list[str],
    out_dir: Path,
) -> list[str]:
    command = headless_runner_command(args, runner_args, out_dir, dry_run=True)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if completed.returncode != 0:
        raise RegressionFailure(
            "failed to resolve headless QBox command:\n" + completed.stdout
        )
    marker = "Headless QBox runner command:"
    if marker not in completed.stdout:
        raise RegressionFailure(
            "headless dry-run output did not contain the runner command:\n"
            + completed.stdout
        )
    command_text = completed.stdout.split(marker, 1)[1].strip()
    return shlex.split(command_text)


def image_paths_from_command(command: list[str]) -> list[Path]:
    paths: list[Path] = []
    index = 0
    while index < len(command):
        option = command[index]
        if option in IMAGE_OPTIONS and index + 1 < len(command):
            path = Path(command[index + 1])
            if not path.is_absolute():
                path = ROOT / path
            paths.append(path.resolve(strict=False))
            index += 2
            continue
        index += 1
    return paths


def cleanup_qbox_processes_holding_images(image_paths: list[Path], *, label: str) -> None:
    holders = qbox_pids_holding_paths(image_paths)
    if not holders:
        return
    for pid, paths in sorted(holders.items()):
        print(
            f"{label}: QBox pid "
            f"{pid} holds image(s): "
            + ", ".join(str(path) for path in paths),
            flush=True,
        )
    terminate_process_groups_for_pids(list(holders), label=label)
    remaining = qbox_pids_holding_paths(image_paths)
    if remaining:
        details = []
        for pid, paths in sorted(remaining.items()):
            details.append(f"  pid {pid}: " + ", ".join(str(path) for path in paths))
        raise RegressionFailure(
            f"QBox image locks remain after {label}:\n" + "\n".join(details)
        )


def terminate_process_group(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=10)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    proc.wait(timeout=10)


def copy_process_output(pipe: Any, runner_log: Path) -> None:
    with runner_log.open("a", encoding="utf-8", errors="replace") as log:
        for line in pipe:
            log.write(line)
            log.flush()
            print(line, end="", flush=True)


def run_qbox_yocto(
    args: argparse.Namespace,
    runner_args: list[str],
    *,
    baseline: dict[str, Any] | None,
    error_regexes: list[str],
    ignore_error_regexes: list[str],
) -> tuple[Path, int]:
    out_dir = args.out_dir
    if out_dir is None:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        out_dir = result_root_for_machine(args.machine) / f"regression-{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    resolved_command = dry_run_headless_command(args, runner_args, out_dir)
    image_paths = image_paths_from_command(resolved_command)
    cleanup_qbox_processes_holding_images(image_paths, label="pre-run cleanup")

    command = headless_runner_command(args, runner_args, out_dir)
    print("running:", " ".join(command), flush=True)
    runner_log = out_dir / "qbox-runner.log"
    runner_log.write_text("running: " + " ".join(command) + "\n", encoding="utf-8")
    monitor = (
        RealtimeLogMonitor(
            baseline=baseline,
            result_dir=out_dir,
            threshold=args.threshold,
            error_regexes=error_regexes,
            ignore_regexes=ignore_error_regexes,
            context=args.context_lines,
            allow_current_timer_baseline=args.allow_current_timer_baseline,
        )
        if baseline is not None
        else None
    )
    line_timing_recorder = RealtimeLineTimingRecorder(result_dir=out_dir)
    proc = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        start_new_session=True,
    )
    assert proc.stdout is not None
    output_thread = threading.Thread(
        target=copy_process_output,
        args=(proc.stdout, runner_log),
        daemon=True,
    )
    output_thread.start()
    try:
        while proc.poll() is None:
            if monitor is not None:
                monitor.poll()
            if line_timing_recorder is not None:
                line_timing_recorder.poll()
            time.sleep(args.poll_interval)
        if monitor is not None:
            monitor.poll()
        if line_timing_recorder is not None:
            line_timing_recorder.poll()
    except RegressionFailure:
        terminate_process_group(proc)
        output_thread.join(timeout=5)
        raise
    finally:
        terminate_process_group(proc)
        output_thread.join(timeout=5)
        if line_timing_recorder is not None:
            line_timing_recorder.write()
        pending_exception = sys.exc_info()[0]
        try:
            cleanup_qbox_processes_holding_images(image_paths, label="post-run cleanup")
        except RegressionFailure as exc:
            if pending_exception is None:
                raise
            print(str(exc), file=sys.stderr)
    return out_dir, int(proc.returncode or 0)


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description=(
            "Record a run_qbox_yocto.sh boot baseline or compare a later run "
            "against it with fail-fast timing and error-log checks."
        )
    )
    parser.add_argument("--machine", choices=SUPPORTED_MACHINES, default=DEFAULT_MACHINE)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--result-dir", type=Path)
    parser.add_argument("--latest-result-root", type=Path)
    parser.add_argument("--record-baseline", action="store_true")
    parser.add_argument("--fail-on-baseline-errors", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--runner", type=Path, default=ROOT / "run_qbox_yocto.sh")
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--result-wait-timeout", type=float)
    parser.add_argument("--poll-interval", type=float, default=DEFAULT_POLL_INTERVAL)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--context-lines", type=int, default=3)
    parser.add_argument("--error-regex", action="append")
    parser.add_argument("--ignore-error-regex", action="append", default=[])
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument(
        "--allow-current-timer-baseline",
        action="store_true",
        help=(
            "Allow the known pre-fix Apollo AP MMIO timer baseline "
            "(`arch-timer-mmio 1a810000.timer` at 19.20MHz) for explicit "
            "baseline characterization only; timer-window shadow warnings and "
            "timer-related errors still fail."
        ),
    )
    parser.add_argument("runner_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    runner_args = list(args.runner_args)
    if runner_args and runner_args[0] == "--":
        runner_args = runner_args[1:]
    if args.baseline is None:
        args.baseline = baseline_for_machine(args.machine)
    if args.latest_result_root is None:
        args.latest_result_root = result_root_for_machine(args.machine)
    return args, runner_args


def main() -> int:
    install_signal_handlers()
    args, runner_args = parse_args()
    error_regexes = args.error_regex or DEFAULT_ERROR_REGEXES
    ignore_error_regexes = args.ignore_error_regex

    try:
        run_returncode: int | None = None
        baseline: dict[str, Any] | None = None
        if not args.record_baseline:
            if not args.baseline.exists():
                raise RegressionFailure(
                    f"baseline not found: {args.baseline}; "
                    "create it with --record-baseline first"
                )
            baseline = read_json(args.baseline)
            if baseline.get("schema_version") != SCHEMA_VERSION:
                raise RegressionFailure(
                    f"unsupported baseline schema: {baseline.get('schema_version')}"
                )

        if args.run:
            result_dir, run_returncode = run_qbox_yocto(
                args,
                runner_args,
                baseline=baseline,
                error_regexes=error_regexes,
                ignore_error_regexes=ignore_error_regexes,
            )
        elif args.result_dir:
            result_dir = args.result_dir
        else:
            latest = latest_result_dir(args.latest_result_root)
            if latest is None:
                raise RegressionFailure(
                    "no --result-dir was provided and no latest result directory was found"
                )
            result_dir = latest

        if args.run and not result_json_ready(result_dir):
            if run_returncode not in (None, 0):
                raise RegressionFailure(
                    "headless runner exited before writing result JSON:\n"
                    f"  status: {run_returncode}\n"
                    f"  result dir: {result_dir}\n"
                    "  qbox-runner.log tail:\n"
                    + "\n".join(
                        f"    {line}" for line in last_lines(result_dir / "qbox-runner.log", 40)
                    )
                )
            wait_timeout = (
                args.result_wait_timeout
                if args.result_wait_timeout is not None
                else float(args.timeout + 60 if args.timeout > 0 else 3600)
            )
            wait_for_run_result(
                result_dir,
                wait_timeout=wait_timeout,
                poll_interval=args.poll_interval,
            )

        snapshot = build_snapshot(
            result_dir,
            threshold=args.threshold,
            error_regexes=error_regexes,
            ignore_error_regexes=ignore_error_regexes,
        )

        if args.record_baseline:
            timer_summary = require_timer_topology(
                snapshot,
                context=args.context_lines,
                allow_current_baseline=args.allow_current_timer_baseline,
            )
            require_clean_baseline(
                snapshot,
                fail_on_baseline_errors=args.fail_on_baseline_errors,
                context=args.context_lines,
            )
            write_json(args.baseline, snapshot)
            print(f"recorded baseline: {args.baseline}")
            print(f"source result dir: {result_dir}")
            print(f"stages: {len(snapshot['stages'])}")
            print(f"known error matches: {len(snapshot['error_matches'])}")
            print(f"timer topology: {json.dumps(timer_summary, sort_keys=True)}")
            return 0

        if baseline is None:
            baseline = read_json(args.baseline)

        timer_summary = require_timer_topology(
            snapshot,
            context=args.context_lines,
            allow_current_baseline=args.allow_current_timer_baseline,
        )
        summary = compare_snapshot(
            baseline,
            snapshot,
            threshold=args.threshold,
            context=args.context_lines,
            emit_passes=not args.run,
        )
        summary["result_dir"] = str(result_dir)
        summary["baseline"] = str(args.baseline)
        summary["timer_topology"] = timer_summary
        if args.summary_out:
            write_json(args.summary_out, summary)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except RegressionFailure as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("interrupted; terminated QBox runner process group", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
