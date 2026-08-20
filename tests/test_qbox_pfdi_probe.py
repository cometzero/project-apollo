from __future__ import annotations

from pathlib import Path

import pytest

from scripts.run import run_qbox_apollo_fvp_full as full_runner


runtime = full_runner.runtime_engine


def pfdi_primary_log() -> str:
    lines = [
        "PFDI prerequisites OK",
        "Loading config V1.0: running 4 tasks every 60 ms",
        "libPFDI version: 1.0",
        "Stub firmware detected",
    ]
    for cpu in range(4):
        lines.extend(
            [
                f"CPU{cpu}: Firmware reports 41 available diagnostic tests",
                f"CPU{cpu}: Out of Reset (OoR) test OK",
                f"CPU{cpu}: PFDI Online (OnL) test (0 - 40) OK",
                f"CPU{cpu}: injected force error",
                f"CPU{cpu}: PFDI Online (OnL) test failed: "
                "Input/output error (errno=5)",
                f"pfdi_force_error_cpu{cpu}_rc:0",
            ]
        )
    lines.extend(
        [
            "pfdi_prerequisites_rc:0",
            "pfdi_service_rc:0",
            "pfdi_cli_rc:0",
            "pfdi_online_rc:0",
            "__QBOX_PFDI_PROBE_DONE__",
            "__QBOX_PROBE_DONE__",
        ]
    )
    return "\n".join(lines)


def pfdi_scp_log() -> str:
    lines: list[str] = []
    for cpu in range(4):
        lines.extend(
            [
                f"Started PFDI monitoring for AP cluster 0 core {cpu}",
                "[FMU] Critical fault received:",
                f"[SBISTC] SBISTC_EQ_FAIL_CORE{cpu} detected",
                f"[PFDI_MONITOR] Onl PFDI for AP cluster 0 core {cpu} "
                "failed, stopping PFDI monitoring",
            ]
        )
    return "\n".join(reversed(lines))


def test_pfdi_probe_commands_cover_same_bsp_contract() -> None:
    # Given/When: the fixed QBox PFDI command sequence is built.
    commands = runtime.pfdi_probe_commands()

    # Then: it covers prerequisites, service, CLI, online, and fault injection.
    joined = "\n".join(commands)
    assert "/dev/cpu/0/pfdi" in joined
    assert "pidof pfdi-sample-app" in joined
    assert "kill $pids" in joined
    assert "pfdi-cli --pfdi_info 0" in joined
    assert "pfdi-sample-app -ivc" in joined
    assert ">/run/pfdi-sample-app.log 2>&1 &" in joined
    assert "pfdi-cli --force_error 3 RUN ERROR" in joined
    assert commands[-1] == "echo __QBOX_PROBE_DONE__"


def test_pfdi_probe_accepts_reordered_scp_markers() -> None:
    # Given: all primary and SCP evidence in a non-FVP marker order.
    # When: the QBox PFDI probe result is evaluated.
    result = runtime.evaluate_pfdi_probe(pfdi_primary_log(), pfdi_scp_log())

    # Then: every CPU and fault-propagation contract passes without ordering.
    assert result["passed"] is True
    assert result["failed_checks"] == []


def test_pfdi_probe_fails_when_one_cpu_marker_is_missing() -> None:
    # Given: otherwise complete evidence without the CPU2 SBIST marker.
    scp = pfdi_scp_log().replace("[SBISTC] SBISTC_EQ_FAIL_CORE2 detected", "")

    # When: the QBox PFDI result is evaluated.
    result = runtime.evaluate_pfdi_probe(pfdi_primary_log(), scp)

    # Then: the missing CPU-specific propagation marker fails the probe.
    assert result["passed"] is False
    assert "cpu2_sbistc" in result["failed_checks"]


def test_pfdi_scp_console_prefers_full_system_si0_log(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Given: the child runner placeholder and the full-system SI0 console.
    si0_log = tmp_path / "si0.log"
    si0_log.write_text("real SI0 PFDI evidence\n", encoding="utf-8")
    monkeypatch.setenv("QBOX_APOLLO_FULL_SI_CL0_LOG", str(si0_log))

    # When/Then: PFDI evaluation reads the console that owns SCP firmware.
    assert runtime.pfdi_scp_console(tmp_path, {"scp": "placeholder"}) == (
        "real SI0 PFDI evidence\n"
    )
