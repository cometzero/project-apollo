from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import sys
from typing import TextIO

import pytest


ROOT = Path(__file__).resolve().parents[1]
for module_path in (
    ROOT / "hsoc-stack/yocto/meta-hsoc-bsp/lib",
    ROOT / "layers/poky/meta/lib",
):
    sys.path.insert(0, str(module_path))

from oeqa.runtime.cases.test_21_bsp_smcf import SmcfBspTest  # noqa: E402
from oeqa.runtime.cases.test_31_bsp_si_pfdi_monitor import (  # noqa: E402
    LogTerminal,
    SiPfdiMonitorBspTest,
)


setattr(SmcfBspTest, "__test__", False)
setattr(SiPfdiMonitorBspTest, "__test__", False)


class FakeTerminal:
    def __init__(self, logfile: Path) -> None:
        self.logfile: TextIO = logfile.open("a+", encoding="utf-8")

    def close(self) -> None:
        self.logfile.close()


class ScriptedTarget:
    def __init__(self, expected: list[str], logfile: Path | None = None) -> None:
        self.expected = expected
        self.transitions: list[str] = []
        self.controls: list[tuple[str, str]] = []
        self.lines: list[tuple[str, str]] = []
        self._fake_terminals: list[FakeTerminal] = []
        terminals: dict[str, LogTerminal] = {}
        if logfile is not None:
            fake_terminal = FakeTerminal(logfile)
            self._fake_terminals.append(fake_terminal)
            terminals["scp"] = fake_terminal
        self.terminals: Mapping[str, LogTerminal] = terminals

    def transition(self, state: str) -> None:
        self.transitions.append(state)

    def sendcontrol(self, terminal: str, control: str) -> None:
        self.controls.append((terminal, control))

    def sendline(self, terminal: str, line: str = "") -> None:
        self.lines.append((terminal, line))

    def expect(self, terminal: str, pattern: str, timeout: int) -> int:
        del terminal, timeout
        if not self.expected:
            raise AssertionError(f"unexpected pattern: {pattern}")
        expected = self.expected.pop(0)
        if expected != pattern:
            raise AssertionError(f"expected {expected}, got {pattern}")
        return 0

    def close(self) -> None:
        for terminal in self._fake_terminals:
            terminal.close()


def _smcf_run_markers() -> list[str]:
    return [
        r"\[CLI_DEBUGGER_MODULE\]\s+Entering CLI",
        r">",
        r"\[CLI_DEBUGGER_MODULE\]\s+Exiting CLI",
        r"\[INTEGRATION_TEST\]\s+Start:\s*smcf",
        r"(?P<tests>[1-9]\d*)\s+Tests\s+0\s+Failures\s+0\s+Ignored",
        r"\bOK\b",
        r"\[INTEGRATION_TEST\]\s+End:\s*smcf",
    ]


def _smcf_case(target: ScriptedTarget, method: str) -> SmcfBspTest:
    case = SmcfBspTest(method)
    case.target = target
    case.setUp()
    return case


def test_smcf_requires_four_distinct_completed_cli_runs() -> None:
    # Given: an SCP console containing four distinct complete executions.
    target = ScriptedTarget(_smcf_run_markers() * 4)
    case = _smcf_case(target, "test_02_execute_smcf_test")

    # When: the functional execution and the three stability executions run.
    case.test_02_execute_smcf_test()
    case.test_03_run_smcf_3x()

    # Then: each execution has independent CLI entry/exit and completion markers.
    assert not target.expected
    assert target.controls == [("scp", "e"), ("scp", "d")] * 4
    assert target.lines == [("scp", "test smcf")] * 4


@pytest.mark.parametrize(
    "marker_index",
    [3, 4, 5, 6],
    ids=["missing-start", "zero-failed-ignored-summary", "missing-ok", "missing-end"],
)
def test_smcf_rejects_incomplete_or_invalid_execution(marker_index: int) -> None:
    # Given: one command whose expected marker is absent or semantically invalid.
    expected = _smcf_run_markers()
    expected.pop(marker_index)
    target = ScriptedTarget(expected)

    # When/Then: the execution cannot be accepted from an incomplete transcript.
    with pytest.raises(AssertionError):
        _smcf_case(target, "test_02_execute_smcf_test").test_02_execute_smcf_test()


def test_smcf_rejects_reused_single_execution_for_stability() -> None:
    # Given: only one complete run that a stale cursor could otherwise reuse.
    target = ScriptedTarget(_smcf_run_markers())

    # When/Then: the three-run stability gate requires three additional executions.
    with pytest.raises(AssertionError):
        _smcf_case(target, "test_03_run_smcf_3x").test_03_run_smcf_3x()


def test_smcf_sensor_requires_documented_value_format(tmp_path: Path) -> None:
    # Given: an SCP transcript with a sensor header but no hexadecimal value.
    logfile = tmp_path / "smcf-missing-sensor.log"
    logfile.write_text(
        "[SMCF_CLIENT] Values for MGI MGI_SMD_SMCF_MGI MLI 0 (Sensor)\n",
        encoding="utf-8",
    )
    target = ScriptedTarget([], logfile)

    # When/Then: a header alone cannot establish sensor-value correctness.
    with pytest.raises(AssertionError):
        _smcf_case(target, "test_04_smcf_client_sensor_monitor").test_04_smcf_client_sensor_monitor()
    target.close()


def _si_log(cpus: int, error: str = "") -> str:
    lines: list[str] = ["[SI0_PLATFORM] SCP started"]
    for cpu in range(cpus):
        lines.extend(
            [
                f"[PFDI_MONITOR] Started PFDI monitoring for SI cluster 1 core {cpu}",
                f"[PFDI_MONITOR] SI cluster 1 core {cpu} has been turned on, switching on PFDI monitoring",
            ]
        )
    return "\n".join([*lines, error])


def _si_case(target: ScriptedTarget, cpu_count: str) -> SiPfdiMonitorBspTest:
    case = SiPfdiMonitorBspTest("test_si_pfdi_monitoring")
    case.target = target
    case.td = {"SI_CL1_CPUS_COUNT": cpu_count}
    case.setUp()
    return case


def test_si_pfdi_requires_each_configured_cluster_core_tuple(tmp_path: Path) -> None:
    # Given: a fresh SCP log containing the full two-marker sequence per core.
    logfile = tmp_path / "scp.log"
    logfile.write_text(_si_log(2), encoding="utf-8")
    target = ScriptedTarget([], logfile)

    # When: the BSP-native SI monitor case runs.
    _si_case(target, "2").test_si_pfdi_monitoring()
    target.close()

    # Then: every configured tuple is independently verified from the live log.
    assert target.transitions == ["on", "off"]


@pytest.mark.parametrize(
    "log, cpu_count",
    [
        (_si_log(1), "2"),
        (_si_log(1) + "\n[PFDI_MONITOR] Started PFDI monitoring for SI cluster 1 core 0", "1"),
        (_si_log(1, "[PFDI_MONITOR] Error! PFDI monitor timeout for SI cluster 1 core 0"), "1"),
        (_si_log(1, "[PFDI_MONITOR] failed to start monitoring"), "1"),
    ],
    ids=["missing-core", "duplicate-core", "timeout", "failure"],
)
def test_si_pfdi_rejects_incomplete_or_failed_monitoring(
    tmp_path: Path,
    log: str,
    cpu_count: str,
) -> None:
    # Given: a malformed, duplicate, timed-out, or failed SCP monitor transcript.
    logfile = tmp_path / "scp.log"
    logfile.write_text(log, encoding="utf-8")
    target = ScriptedTarget([], logfile)
    case = _si_case(target, cpu_count)
    case.timeout = 0

    # When/Then: no stale or partial log can satisfy the configured monitor gate.
    with pytest.raises(AssertionError):
        case.test_si_pfdi_monitoring()
    target.close()


def test_si_pfdi_rejects_stale_markers_before_current_scp_anchor(
    tmp_path: Path,
) -> None:
    # Given: a complete old monitor segment followed by a current empty SCP boot.
    logfile = tmp_path / "scp.log"
    logfile.write_text(
        _si_log(1) + "\n[SI0_PLATFORM] SCP started\n",
        encoding="utf-8",
    )
    target = ScriptedTarget([], logfile)
    case = _si_case(target, "1")
    case.timeout = 0

    # When/Then: stale markers cannot satisfy the current-process monitor gate.
    with pytest.raises(AssertionError):
        case.test_si_pfdi_monitoring()
    target.close()


def test_si_pfdi_rejects_malformed_configured_cpu_count(tmp_path: Path) -> None:
    # Given: a non-numeric testdata CPU count at the profile boundary.
    logfile = tmp_path / "scp.log"
    logfile.write_text(_si_log(1), encoding="utf-8")
    target = ScriptedTarget([], logfile)

    # When/Then: malformed counts cannot silently reduce tuple coverage.
    with pytest.raises(AssertionError, match="SI_CL1_CPUS_COUNT"):
        _si_case(target, "invalid").test_si_pfdi_monitoring()
    target.close()
