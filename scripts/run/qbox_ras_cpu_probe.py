from __future__ import annotations

import re
from typing import Final, TypedDict


RAS_PROBE_DONE_MARKER: Final = "__QBOX_RAS_CPU_PROBE_DONE__"
QBOX_PROBE_DONE_MARKER: Final = "__QBOX_PROBE_DONE__"
RAS_ERROR_NAMES: Final = (
    "CorrectableCpuError",
    "UncorrectableFatalCpuError",
    "DeferredCpuError",
)


class RASCpuChecks(TypedDict):
    prerequisites: bool
    list: bool
    invalid: bool
    usage: bool
    correctable: bool
    deferred: bool
    repeat: bool
    combined: bool
    journal: bool
    uncorrectable: bool
    scp_faulty_cpu: bool
    scp_uncontainable: bool
    scp_ssu_errc: bool


class RASCpuProbeResult(TypedDict):
    passed: bool
    done_marker: bool
    return_codes: dict[str, int]
    tfa_interrupt_count: int
    checks: RASCpuChecks
    failed_checks: list[str]


def _ras_event_command(error_name: str, severity: str) -> str:
    correction = (
        "grep -qi 'the error has been corrected' <<<\"$DM\" || rc=1; "
        if severity == "corrected"
        else "grep -qi 'the error has not been corrected' <<<\"$DM\" || rc=1; "
    )
    key = error_name.removesuffix("CpuError").lower()
    return (
        "rc=0; dmesg -c >/dev/null 2>&1; "
        f"ts-ras-inject {error_name} || rc=1; sleep 3; "
        "DM=$(dmesg); printf '%s\n' \"$DM\"; "
        f"grep -qi 'event severity: {severity}' <<<\"$DM\" || rc=1; "
        "grep -qi 'processor context not corrupted' <<<\"$DM\" || rc=1; "
        + correction
        + "grep -q 'Context info structure 0' <<<\"$DM\" || rc=1; "
        "grep -q 'Context info structure 1' <<<\"$DM\" || rc=1; "
        f"echo ras_{key}_rc:$rc"
    )


def _repeat_command() -> str:
    return (
        "rc=0; prev=0; echo __QBOX_RAS_REPEAT_START__; "
        "echo 0 > /proc/sys/kernel/printk_ratelimit || true; "
        "echo 0 > /proc/sys/kernel/printk_ratelimit_burst || true; "
        "for i in $(seq 1 10); do dmesg -c >/dev/null 2>&1; "
        "ts-ras-inject CorrectableCpuError || rc=1; sleep 11; "
        "DM=$(dmesg); printf '%s\n' \"$DM\"; "
        "ID=$(printf '%s\n' \"$DM\" | sed -nE "
        "'s/.*[{]([0-9]+)[}][[]Hardware Error[]]: "
        "event severity: corrected.*/\\1/p' | tail -n 1); "
        "grep -qi 'processor context not corrupted' <<<\"$DM\" || rc=1; "
        "grep -qi 'the error has been corrected' <<<\"$DM\" || rc=1; "
        "grep -q 'Context info structure 0' <<<\"$DM\" || rc=1; "
        "grep -q 'Context info structure 1' <<<\"$DM\" || rc=1; "
        "if [ -z \"$ID\" ]; then rc=1; "
        "elif [ \"$prev\" -ne 0 ] && [ \"$ID\" -ne $((prev+1)) ]; "
        "then rc=1; fi; prev=${ID:-$prev}; done; "
        "echo __QBOX_RAS_REPEAT_DONE__; echo ras_repeat_rc:$rc"
    )


def _combined_command() -> str:
    return (
        "rc=0; dmesg -c >/dev/null 2>&1; "
        "ts-ras-inject CorrectableCpuError || rc=1; sleep 3; "
        "ts-ras-inject DeferredCpuError || rc=1; sleep 3; "
        "DM=$(dmesg); printf '%s\n' \"$DM\"; "
        "grep -qi 'event severity: corrected' <<<\"$DM\" || rc=1; "
        "grep -qi 'event severity: recoverable' <<<\"$DM\" || rc=1; "
        "echo ras_combined_rc:$rc"
    )


def ras_cpu_probe_commands() -> list[str]:
    return [
        (
            "rc=0; test -x /usr/bin/ts-ras-inject || rc=1; "
            "systemctl is-active --quiet rasdaemon.service || rc=1; "
            "test \"$(nproc)\" -eq 4 || rc=1; "
            "echo ras_prerequisites_rc:$rc"
        ),
        "ts-ras-inject --list; echo ras_list_rc:$?",
        (
            "ts-ras-inject InvalidErrorType || true; "
            "echo ras_invalid_rc:0"
        ),
        "ts-ras-inject || true; echo ras_usage_rc:0",
        _ras_event_command("CorrectableCpuError", "corrected"),
        _ras_event_command("DeferredCpuError", "recoverable"),
        _repeat_command(),
        _combined_command(),
        (
            "rc=0; J=$(journalctl -u rasdaemon.service --no-pager); "
            "printf '%s\n' \"$J\"; "
            "grep -q 'rasdaemon: ras:arm_event event enabled' <<<\"$J\" || rc=1; "
            "grep -q 'affinity: -1' <<<\"$J\" && rc=1; "
            "echo ras_journal_rc:$rc"
        ),
        (
            "rc=0; dmesg -c >/dev/null 2>&1; "
            "ts-ras-inject UncorrectableFatalCpuError || rc=1; "
            "echo ras_uncorrectable_rc:$rc"
        ),
        f"echo {RAS_PROBE_DONE_MARKER}",
        f"echo {QBOX_PROBE_DONE_MARKER}",
    ]


def _return_codes(primary: str) -> dict[str, int]:
    return {
        match.group(1): int(match.group(2))
        for match in re.finditer(r"\b(ras_[a-z_]+_rc):(\d+)\b", primary)
    }


def evaluate_ras_cpu_probe(
    primary: str,
    secure: str,
    scp: str,
) -> RASCpuProbeResult:
    return_codes = _return_codes(primary)
    tfa_interrupt_count = secure.count("CPU RAS: Interrupt Received")
    checks: RASCpuChecks = {
        "prerequisites": return_codes.get("ras_prerequisites_rc") == 0,
        "list": (
            return_codes.get("ras_list_rc") == 0
            and " ".join(RAS_ERROR_NAMES) in primary
        ),
        "invalid": (
            return_codes.get("ras_invalid_rc") == 0
            and "Unknown error type: InvalidErrorType" in primary
        ),
        "usage": (
            return_codes.get("ras_usage_rc") == 0
            and f"ErrorName is one of: {' '.join(RAS_ERROR_NAMES)}" in primary
        ),
        "correctable": return_codes.get("ras_correctable_rc") == 0,
        "deferred": return_codes.get("ras_deferred_rc") == 0,
        "repeat": return_codes.get("ras_repeat_rc") == 0,
        "combined": return_codes.get("ras_combined_rc") == 0,
        "journal": return_codes.get("ras_journal_rc") == 0,
        "uncorrectable": return_codes.get("ras_uncorrectable_rc") == 0,
        "scp_faulty_cpu": "Faulty CPU Identified" in scp,
        "scp_uncontainable": "Fault Type = Uncontainable Error" in scp,
        "scp_ssu_errc": "Setting SSU FSM to: ERRC" in scp,
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    if tfa_interrupt_count < 14:
        failed_checks.append("tfa_interrupt_count")
    done_marker = RAS_PROBE_DONE_MARKER in primary
    if not done_marker:
        failed_checks.append("done_marker")
    return {
        "passed": not failed_checks,
        "done_marker": done_marker,
        "return_codes": return_codes,
        "tfa_interrupt_count": tfa_interrupt_count,
        "checks": checks,
        "failed_checks": failed_checks,
    }
