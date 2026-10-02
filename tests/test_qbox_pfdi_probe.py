from __future__ import annotations

from pathlib import Path

import pytest

from scripts.run import run_qbox_apollo_fvp_full as full_runner
from scripts.run.qbox_pfdi_probe import evaluate_pfdi_probe, pfdi_probe_commands


runtime = full_runner.runtime_engine


def pfdi_primary_log(interval_ms: int = 600) -> str:
    lines = [
        "PFDI prerequisites OK",
        f"pfdi_interval_ms:{interval_ms}",
        f"Loading config V1.0: running 4 tasks every {interval_ms} ms",
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
    commands = pfdi_probe_commands()

    # Then: it covers prerequisites, service, CLI, online, and fault injection.
    joined = "\n".join(commands)
    assert "/dev/cpu/0/pfdi" in joined
    assert "pidof pfdi-sample-app" in joined
    assert "od -An -tu8 -j16 -N8 /etc/pfdi/pfdi_test_config_0.pack" in joined
    assert "printf 'pfdi_interval_ms:%s\\n'" in joined
    assert "every $interval_ms ms" in joined
    assert "kill $pids" in joined
    assert "pfdi-cli --pfdi_info 0" in joined
    assert "pfdi-sample-app -ivc" in joined
    assert ">/run/pfdi-sample-app.log 2>&1 &" in joined
    assert "pfdi-cli --force_error 3 RUN ERROR" in joined
    assert commands[-1] == "echo __QBOX_PROBE_DONE__"


def test_pfdi_probe_accepts_reordered_scp_markers() -> None:
    # Given: all primary and SCP evidence in a non-FVP marker order.
    # When: the QBox PFDI probe result is evaluated.
    result = evaluate_pfdi_probe(pfdi_primary_log(), pfdi_scp_log())

    # Then: every CPU and fault-propagation contract passes without ordering.
    assert result["passed"] is True
    assert result["failed_checks"] == []


@pytest.mark.parametrize("interval_ms", [60, 600, 900])
def test_pfdi_probe_uses_configured_interval(interval_ms: int) -> None:
    commands = pfdi_probe_commands(expected_interval_ms=interval_ms)
    assert f'test "$interval_ms" -eq {interval_ms}' in "\n".join(commands)
    result = evaluate_pfdi_probe(
        pfdi_primary_log(interval_ms), pfdi_scp_log(),
        expected_interval_ms=interval_ms,
    )
    assert result["passed"] is True


@pytest.mark.parametrize("interval_ms", [60, 600, 900])
def test_pfdi_probe_defaults_to_installed_pack_interval(interval_ms: int) -> None:
    result = evaluate_pfdi_probe(pfdi_primary_log(interval_ms), pfdi_scp_log())
    assert result["passed"] is True


def test_pfdi_probe_rejects_policy_interval_mismatch() -> None:
    result = evaluate_pfdi_probe(
        pfdi_primary_log(60), pfdi_scp_log(), expected_interval_ms=600,
    )
    assert result["passed"] is False
    assert "service" in result["failed_checks"]


def test_pfdi_probe_rejects_pack_and_active_log_mismatch() -> None:
    primary = pfdi_primary_log().replace("pfdi_interval_ms:600", "pfdi_interval_ms:900")
    result = evaluate_pfdi_probe(primary, pfdi_scp_log())
    assert result["passed"] is False
    assert "service" in result["failed_checks"]


@pytest.mark.parametrize("marker", [
    "", "pfdi_interval_ms:", "pfdi_interval_ms:invalid", "pfdi_interval_ms:0",
    "pfdi_interval_ms:-1", "pfdi_interval_ms:600 trailing", "pfdi_interval_ms:4294967296",
    "pfdi_interval_ms:600\npfdi_interval_ms:900",
    "pfdi_interval_ms:600\npfdi_interval_ms:invalid",
    "echo pfdi_interval_ms:600",
])
def test_pfdi_probe_rejects_invalid_pack_interval_evidence(marker: str) -> None:
    primary = pfdi_primary_log().replace("pfdi_interval_ms:600", marker)
    result = evaluate_pfdi_probe(primary, pfdi_scp_log())
    assert result["passed"] is False
    assert "service" in result["failed_checks"]


@pytest.mark.parametrize("interval_ms", [0, -1, 4294967296])
def test_pfdi_probe_rejects_unsupported_intervals(interval_ms: int) -> None:
    with pytest.raises(ValueError, match="1..4294967295"):
        pfdi_probe_commands(expected_interval_ms=interval_ms)
    with pytest.raises(ValueError, match="1..4294967295"):
        evaluate_pfdi_probe("", "", expected_interval_ms=interval_ms)


def test_pfdi_probe_fails_when_one_cpu_marker_is_missing() -> None:
    # Given: otherwise complete evidence without the CPU2 SBIST marker.
    scp = pfdi_scp_log().replace("[SBISTC] SBISTC_EQ_FAIL_CORE2 detected", "")

    # When: the QBox PFDI result is evaluated.
    result = evaluate_pfdi_probe(pfdi_primary_log(), scp)

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
