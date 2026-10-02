from __future__ import annotations

import re
from typing import Final, TypedDict


PFDI_CPU_COUNT: Final = 4
PFDI_MAX_INTERVAL_MS: Final = (1 << 32) - 1
PFDI_PROBE_DONE_MARKER: Final = "__QBOX_PFDI_PROBE_DONE__"
QBOX_PROBE_DONE_MARKER: Final = "__QBOX_PROBE_DONE__"


class PFDICpuResult(TypedDict):
    count: bool
    oor: bool
    online: bool
    force_error: bool
    online_failure: bool
    monitor_started: bool
    sbistc: bool
    monitor_failure: bool


class PFDIProbeResult(TypedDict):
    passed: bool
    done_marker: bool
    return_codes: dict[str, int]
    fmu_fault_count: int
    cpu_results: dict[str, PFDICpuResult]
    failed_checks: list[str]


def _force_error_command(cpu: int) -> str:
    failure = (
        f"CPU{cpu}: PFDI Online (OnL) test failed: "
        "Input/output error (errno=5)"
    )
    return (
        f"rc=0; pfdi-cli --force_error {cpu} RUN ERROR || rc=1; "
        "attempt=0; "
        f"until grep -Fq '{failure}' /run/pfdi-sample-app.log; do "
        "attempt=$((attempt + 1)); "
        "if [ \"$attempt\" -ge 180 ]; then rc=1; break; fi; "
        "sleep 1; done; "
        f"grep -F '{failure}' /run/pfdi-sample-app.log || true; "
        f"echo pfdi_force_error_cpu{cpu}_rc:$rc"
    )


def pfdi_probe_commands(expected_interval_ms: int | None = None) -> list[str]:
    if expected_interval_ms is not None and not 1 <= expected_interval_ms <= PFDI_MAX_INTERVAL_MS:
        raise ValueError("PFDI interval must be in 1..4294967295 ms")
    interval_check = (
        f'test "$interval_ms" -eq {expected_interval_ms} || rc=1; '
        if expected_interval_ms is not None else ""
    )
    cpu_devices = " ".join(f"/dev/cpu/{cpu}/pfdi" for cpu in range(PFDI_CPU_COUNT))
    cli_commands = [
        "rc=0",
        "pfdi-cli --info || rc=1",
        "pfdi-cli --pfdi_info 0 || rc=1",
    ]
    for cpu in range(PFDI_CPU_COUNT):
        cli_commands.extend(
            [
                f"pfdi-cli --count {cpu} || rc=1",
                f"pfdi-cli --result {cpu} || rc=1",
            ]
        )
    cli_commands.append("echo pfdi_cli_rc:$rc")
    commands = [
        (
            "rc=0; "
            f"for path in {cpu_devices}; do test -c \"$path\" || rc=1; done; "
            "test -x /usr/bin/pfdi-cli || rc=1; "
            "test -x /usr/bin/pfdi-sample-app || rc=1; "
            "test -r /etc/pfdi/pfdi_test_config_0.pack || rc=1; "
            "printf 'PFDI prerequisites OK\\n'; "
            "echo pfdi_prerequisites_rc:$rc"
        ),
        (
            "pidof pfdi-sample-app; rc=$?; "
            # The pack stores a little-endian uint64 after its 16-byte version.
            # The guest is little-endian; the app timer accepts unsigned int ms.
            "interval_ms=$(od -An -tu8 -j16 -N8 "
            "/etc/pfdi/pfdi_test_config_0.pack | tr -d '[:space:]'); "
            "case \"$interval_ms\" in ''|*[!0-9]*) rc=1;; "
            "*) test \"$interval_ms\" -ge 1 "
            f"&& test \"$interval_ms\" -le {PFDI_MAX_INTERVAL_MS} || rc=1;; esac; "
            "printf 'pfdi_interval_ms:%s\\n' \"$interval_ms\"; "
            f"{interval_check}"
            'grep -F "Loading config V1.0: running 4 tasks every $interval_ms ms" '
            "/run/pfdi-sample-app.log || rc=1; "
            "echo pfdi_service_rc:$rc"
        ),
        "; ".join(cli_commands),
        (
            "rc=0; pids=$(pidof pfdi-sample-app) || rc=1; "
            "test -n \"$pids\" && kill $pids || rc=1; "
            "attempt=0; while pidof pfdi-sample-app >/dev/null; do "
            "attempt=$((attempt + 1)); "
            "if [ \"$attempt\" -ge 30 ]; then rc=1; break; fi; "
            "sleep 1; done; "
            "pfdi-sample-app -ivc /etc/pfdi/pfdi_test_config_0.pack "
            "-m single || rc=1; "
            "pfdi-sample-app -ivc /etc/pfdi/pfdi_test_config_0.pack "
            ">/run/pfdi-sample-app.log 2>&1 & "
            "attempt=0; until pidof pfdi-sample-app >/dev/null; do "
            "attempt=$((attempt + 1)); "
            "if [ \"$attempt\" -ge 30 ]; then rc=1; break; fi; "
            "sleep 1; done; "
            "echo pfdi_online_rc:$rc"
        ),
    ]
    commands.extend(_force_error_command(cpu) for cpu in range(PFDI_CPU_COUNT))
    commands.extend(
        [
            f"echo {PFDI_PROBE_DONE_MARKER}",
            f"echo {QBOX_PROBE_DONE_MARKER}",
        ]
    )
    return commands


def _return_codes(primary: str) -> dict[str, int]:
    return {
        match.group(1): int(match.group(2))
        for match in re.finditer(r"\b(pfdi_[A-Za-z0-9_]+_rc):(\d+)\b", primary)
    }


def _pack_interval_ms(primary: str) -> int | None:
    values = re.findall(r"^pfdi_interval_ms:([^\r\n]*)\r?$", primary, re.MULTILINE)
    if not values or any(re.fullmatch(r"[0-9]{1,10}", value) is None for value in values):
        return None
    intervals = {int(value) for value in values}
    if len(intervals) != 1:
        return None
    interval = intervals.pop()
    return interval if 1 <= interval <= PFDI_MAX_INTERVAL_MS else None


def evaluate_pfdi_probe(
    primary: str, scp: str, expected_interval_ms: int | None = None
) -> PFDIProbeResult:
    if expected_interval_ms is not None and not 1 <= expected_interval_ms <= PFDI_MAX_INTERVAL_MS:
        raise ValueError("PFDI interval must be in 1..4294967295 ms")
    return_codes = _return_codes(primary)
    interval_ms = _pack_interval_ms(primary)
    failed_checks: list[str] = []
    global_checks = {
        "done_marker": PFDI_PROBE_DONE_MARKER in primary,
        "prerequisites": (
            return_codes.get("pfdi_prerequisites_rc") == 0
            and "PFDI prerequisites OK" in primary
        ),
        "service": (
            return_codes.get("pfdi_service_rc") == 0
            and interval_ms is not None
            and (expected_interval_ms is None or interval_ms == expected_interval_ms)
            and f"Loading config V1.0: running 4 tasks every {interval_ms} ms" in primary
        ),
        "cli": (
            return_codes.get("pfdi_cli_rc") == 0
            and "libPFDI version: 1.0" in primary
            and re.search(
                r"Stub firmware detected|PFDI firmware version", primary
            )
            is not None
        ),
        "online": return_codes.get("pfdi_online_rc") == 0,
    }
    failed_checks.extend(name for name, passed in global_checks.items() if not passed)

    cpu_results: dict[str, PFDICpuResult] = {}
    for cpu in range(PFDI_CPU_COUNT):
        result: PFDICpuResult = {
            "count": (
                f"CPU{cpu}: Firmware reports 41 available diagnostic tests" in primary
            ),
            "oor": f"CPU{cpu}: Out of Reset (OoR) test OK" in primary,
            "online": f"CPU{cpu}: PFDI Online (OnL) test (0 - 40) OK" in primary,
            "force_error": (
                f"CPU{cpu}: injected force error" in primary
                and return_codes.get(f"pfdi_force_error_cpu{cpu}_rc") == 0
            ),
            "online_failure": (
                f"CPU{cpu}: PFDI Online (OnL) test failed: "
                "Input/output error (errno=5)" in primary
            ),
            "monitor_started": (
                f"Started PFDI monitoring for AP cluster 0 core {cpu}" in scp
            ),
            "sbistc": f"[SBISTC] SBISTC_EQ_FAIL_CORE{cpu} detected" in scp,
            "monitor_failure": (
                f"[PFDI_MONITOR] Onl PFDI for AP cluster 0 core {cpu} "
                "failed, stopping PFDI monitoring" in scp
            ),
        }
        cpu_results[str(cpu)] = result
        failed_checks.extend(
            f"cpu{cpu}_{name}" for name, passed in result.items() if not passed
        )

    fmu_fault_count = len(
        re.findall(r"\[FMU\] (?:Non-critical|Critical) fault received:", scp)
    )
    if fmu_fault_count < PFDI_CPU_COUNT:
        failed_checks.append("fmu_fault_count")
    return {
        "passed": not failed_checks,
        "done_marker": global_checks["done_marker"],
        "return_codes": return_codes,
        "fmu_fault_count": fmu_fault_count,
        "cpu_results": cpu_results,
        "failed_checks": failed_checks,
    }
