from __future__ import annotations

from pathlib import Path
import sys
from threading import Lock

import pexpect
import pytest


ROOT = Path(__file__).resolve().parents[1]
for module_path in (
    ROOT / "hsoc-stack/yocto/meta-hsoc-auto-solutions/lib",
    ROOT / "layers/meta-arm/meta-arm/lib",
    ROOT / "layers/poky/meta/lib",
):
    sys.path.insert(0, str(module_path))

from oeqa.controllers import hsocfvp as hsocfvp_controller  # noqa: E402
from oeqa.controllers.fvp import OEFVPTargetState  # noqa: E402
from oeqa.controllers.hsocfvp import (  # noqa: E402
    FVPSerialBootError,
    HSOCSingleSessionFVPTarget,
)
from oeqa.runtime.cases import test_60_linux_connectivity as connectivity  # noqa: E402


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


class FakeMatch:
    def group(self, index: int) -> bytes:
        assert index == 1
        return b"0"


class FakeLogger:
    def info(self, message: str) -> None:
        assert message

    def debug(self, message: str, *values: object) -> None:
        assert message
        assert values


class DelayedBootProductTarget(HSOCSingleSessionFVPTarget):
    def __init__(self, clock: FakeClock, boot_delay: int) -> None:
        self.state = OEFVPTargetState.ON
        self.timeout = 10
        self._hsoc_linux_shell_ready = False
        self._hsoc_serial_command_lock = Lock()
        self._hsoc_serial_command_index = 0
        self.logger = FakeLogger()
        self.clock = clock
        self.boot_delay = boot_delay
        self.transition_timeouts: list[int] = []
        self.boot_attempts = 0
        self.sent: list[str] = []
        self.expected_timeouts: list[float] = []

    def transition(self, state: object, timeout: int = 600) -> None:
        assert state == OEFVPTargetState.LINUX
        self.transition_timeouts.append(timeout)
        if self.state == OEFVPTargetState.LINUX:
            return
        self.boot_attempts += 1
        if timeout < self.boot_delay:
            self.clock.sleep(timeout)
            raise RuntimeError("Failed to start FVP.")
        self.clock.sleep(self.boot_delay)
        self.state = OEFVPTargetState.LINUX
        self._hsoc_linux_shell_ready = True

    def sendline(self, terminal: str, text: str) -> None:
        assert terminal == self.DEFAULT_CONSOLE
        self.sent.append(text)

    def expect(self, terminal: str, pattern: object, timeout: float) -> int:
        assert terminal == self.DEFAULT_CONSOLE
        assert pattern
        self.expected_timeouts.append(timeout)
        return 0

    def before(self, terminal: str) -> bytes:
        assert terminal == self.DEFAULT_CONSOLE
        return b"serial output\r\n"

    def match(self, terminal: str) -> FakeMatch:
        assert terminal == self.DEFAULT_CONSOLE
        return FakeMatch()


def test_product_run_serial_separates_boot_and_probe_budgets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: Linux login needs 30 seconds, beyond the 15-second probe budget.
    clock = FakeClock()
    target = DelayedBootProductTarget(clock, boot_delay=30)
    monkeypatch.setattr(hsocfvp_controller.time, "monotonic", clock.monotonic)

    # When: readiness supplies its full 120-second remaining deadline.
    status, output = target.run_serial(
        "ip -4 addr",
        timeout=15,
        boot_timeout=120,
    )

    # Then: boot gets 120 seconds, the serial probe remains bounded to 15.
    assert (status, output) == (0, "serial output")
    assert target.transition_timeouts == [120]
    assert target.expected_timeouts == [15, 15, 15]
    target.run_serial("ip route", timeout=15, boot_timeout=90)
    assert target.boot_attempts == 1
    assert target.transition_timeouts == [120, 90]


def test_product_run_serial_fails_at_absolute_boot_deadline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: Linux login cannot complete inside the remaining 120 seconds.
    clock = FakeClock()
    target = DelayedBootProductTarget(clock, boot_delay=121)
    monkeypatch.setattr(hsocfvp_controller.time, "monotonic", clock.monotonic)

    # When/Then: one boot attempt consumes the deadline and fails without send.
    with pytest.raises(FVPSerialBootError, match="Failed to start FVP"):
        target.run_serial("ip -4 addr", timeout=15, boot_timeout=120)
    assert target.boot_attempts == 1
    assert target.transition_timeouts == [120]
    assert target.state == OEFVPTargetState.ON
    assert target.sent == []


class EOFBootProductTarget(DelayedBootProductTarget):
    def transition(self, state: object, timeout: int = 600) -> None:
        assert state == OEFVPTargetState.LINUX
        assert timeout == 120
        self.boot_attempts += 1
        raise pexpect.EOF("boot console closed")


def test_product_run_serial_reports_boot_console_eof_once() -> None:
    # Given: the FVP console closes before Linux login.
    target = EOFBootProductTarget(FakeClock(), boot_delay=0)

    # When/Then: typed boot failure is raised without retry or FVP reset.
    with pytest.raises(FVPSerialBootError, match="boot console closed"):
        target.run_serial("ip -4 addr", timeout=15, boot_timeout=120)
    assert target.boot_attempts == 1
    assert target.state == OEFVPTargetState.ON
    assert target.sent == []


class BootFailureConnectivityTarget:
    ip = "192.0.2.10"
    server_ip = "192.0.2.1"

    def run_serial(
        self,
        command: str,
        timeout: int,
        boot_timeout: int | None = None,
    ) -> tuple[int, str]:
        raise FVPSerialBootError(
            "Failed to start FVP.",
            "Run /init as init process",
        )

    def run(self, command: str, timeout: int) -> tuple[int, str]:
        raise AssertionError("SSH must not run before Linux login")


def test_guest_network_boot_failure_reports_console_not_retry() -> None:
    # Given: Linux login fails while the console still shows init progress.
    case = connectivity.LinuxConnectivityTest("test_ping")
    case.target = BootFailureConnectivityTarget()

    # When/Then: readiness fails once with the captured console tail.
    with pytest.raises(AssertionError) as failure:
        case._wait_for_guest_network()
    message = str(failure.value)
    assert "network diagnostics unavailable before shell login" in message
    assert "Run /init as init process" in message
