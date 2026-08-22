from __future__ import annotations

from pathlib import Path
import re
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

from oeqa.controllers.fvp import OEFVPTargetState  # noqa: E402
from oeqa.controllers.hsocfvp import (  # noqa: E402
    HSOCSingleSessionFVPTarget,
    ROOT_SHELL_PROMPT_RE,
)
from oeqa.runtime.cases import test_60_linux_connectivity as connectivity  # noqa: E402


class FakeMatch:
    def __init__(self, status: int) -> None:
        self.status = status

    def group(self, index: int) -> bytes:
        assert index == 1
        return str(self.status).encode("ascii")


class FakeLogger:
    def info(self, message: str) -> None:
        assert message

    def debug(self, message: str, *values: object) -> None:
        assert message
        assert values


class FakeProductTarget(HSOCSingleSessionFVPTarget):
    def __init__(
        self, status: int = 0, output: bytes = b"serial output\r\n",
        serial_error: type[pexpect.ExceptionPexpect] | None = None,
    ) -> None:
        self.state = OEFVPTargetState.LINUX
        self.timeout = 10
        self._hsoc_linux_shell_ready = True
        self._hsoc_serial_command_lock = Lock()
        self._hsoc_serial_command_index = 0
        self.logger = FakeLogger()
        self.status = status
        self.output = output
        self.serial_error = serial_error
        self.sent: list[str] = []
        self.expected: list[tuple[object, int]] = []

    def transition(self, state: object, timeout: int = 600) -> None:
        assert state == OEFVPTargetState.LINUX
        assert timeout > 0

    def sendline(self, terminal: str, text: str) -> None:
        assert terminal == self.DEFAULT_CONSOLE
        self.sent.append(text)

    def expect(self, terminal: str, pattern: object, timeout: int) -> int:
        assert terminal == self.DEFAULT_CONSOLE
        self.expected.append((pattern, timeout))
        if self.serial_error is not None and len(self.expected) == 2:
            raise self.serial_error("serial failure")
        return 0

    def before(self, terminal: str) -> bytes:
        assert terminal == self.DEFAULT_CONSOLE
        return self.output

    def match(self, terminal: str) -> FakeMatch:
        assert terminal == self.DEFAULT_CONSOLE
        return FakeMatch(self.status)


class FakeConnectivityTarget:
    def __init__(
        self, readiness: list[tuple[int, str] | type[pexpect.ExceptionPexpect]],
        ssh_status: int = 0,
    ) -> None:
        self.ip = "192.0.2.10"
        self.server_ip = "192.0.2.1"
        self.readiness = readiness
        self.ssh_status = ssh_status
        self.commands: list[tuple[str, int]] = []
        self.boot_timeouts: list[int | None] = []
        self.linux_timeouts: list[int] = []
        self.diagnostics = {
            "ip -4 addr": (0, "inet 192.0.2.10/24 scope global ovsbr0"),
            "ip route": (0, "192.0.2.0/24 dev ovsbr0"),
            "networkctl --no-pager --full": (0, "ovsbr0 routable"),
        }

    def wait_for_linux(self, timeout: int) -> None:
        self.linux_timeouts.append(timeout)

    def run_serial(
        self, command: str, timeout: int,
        boot_timeout: int | None = None,
    ) -> tuple[int, str]:
        self.boot_timeouts.append(boot_timeout)
        self.commands.append((command, timeout))
        if command.startswith("ip -o -4 addr show"):
            result = self.readiness.pop(0) if self.readiness else (1, "not ready")
            if isinstance(result, type) and issubclass(result, pexpect.ExceptionPexpect):
                raise result("serial failure")
            return result
        return self.diagnostics[command]

    def run(self, command: str, timeout: int) -> tuple[int, str]:
        assert command == "uname -a"
        assert timeout == 30
        return self.ssh_status, "Linux apollo-fvp"


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


def _connectivity_case(target: FakeConnectivityTarget) -> connectivity.LinuxConnectivityTest:
    case = connectivity.LinuxConnectivityTest("test_ping")
    case.target = target
    case.td = {}
    return case


def test_product_run_serial_uses_fresh_token_frames() -> None:
    # Given: a running product console containing any stale shell prompt.
    target = FakeProductTarget(status=7)

    # When: a bounded serial command is executed through the product target.
    status, output = target.run_serial("ip -4 addr", timeout=9)

    # Then: fresh begin/end tokens frame output, status, and final prompt.
    assert status == 7
    assert output == "serial output"
    assert len(target.sent) == 1
    assert "__OEQA_PRODUCT_BEGIN_00000001__" in target.sent[0]
    assert "__OEQA_PRODUCT_END_00000001__" in target.sent[0]
    assert len(target.expected) == 3
    assert target.expected[0] == (re.escape("__OEQA_PRODUCT_BEGIN_00000001__"), 9)
    assert isinstance(target.expected[1][0], re.Pattern)
    assert target.expected[2] == (ROOT_SHELL_PROMPT_RE, 9)


@pytest.mark.parametrize("serial_error", [pexpect.TIMEOUT, pexpect.EOF])
def test_product_run_serial_propagates_bounded_serial_errors(
    serial_error: type[pexpect.ExceptionPexpect],
) -> None:
    # Given: the console cannot produce the command completion token.
    target = FakeProductTarget(serial_error=serial_error)

    # When/Then: the exact serial error remains visible to the caller.
    with pytest.raises(serial_error):
        target.run_serial("ip route", timeout=4)
    assert all(timeout == 4 for _pattern, timeout in target.expected)


def test_product_run_serial_rejects_multiline_command_before_send() -> None:
    # Given: a command that could escape the serial token wrapper.
    target = FakeProductTarget()

    # When/Then: the controller rejects it without touching the console.
    with pytest.raises(ValueError, match="single-line"):
        target.run_serial("ip addr\nprintf injected", timeout=4)
    assert target.sent == []


def test_guest_network_readiness_allows_delayed_dhcp(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: the guest is initially unconfigured, then becomes fully reachable.
    target = FakeConnectivityTarget([(1, "no address"), (0, "ready")])
    case = _connectivity_case(target)
    clock = FakeClock()
    monkeypatch.setattr(connectivity.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(connectivity, "sleep", clock.sleep)

    # When: the connectivity prerequisite waits for the guest network.
    case._wait_for_guest_network()

    # Then: it retries and returns only after address, route, and ping succeed.
    readiness = [command for command, _timeout in target.commands]
    assert len(readiness) == 2
    assert all("192.0.2.10" in command for command in readiness)
    assert all("ip route get 192.0.2.1" in command for command in readiness)
    assert all("ping -c 1" in command for command in readiness)
    assert target.linux_timeouts == [connectivity.DEFAULT_LINUX_BOOT_TIMEOUT_SECONDS]
    assert all(timeout is None for timeout in target.boot_timeouts)
    assert all(timeout <= connectivity.SERIAL_COMMAND_TIMEOUT_SECONDS for _, timeout in target.commands)


def test_guest_network_readiness_timeout_reports_exact_diagnostics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: the guest never acquires the expected reachable network state.
    target = FakeConnectivityTarget(
        [(1, "no route"), (1, "1 packets transmitted, 0 received")]
    )
    case = _connectivity_case(target)
    clock = FakeClock()
    monkeypatch.setattr(connectivity, "NETWORK_READY_TIMEOUT_SECONDS", 2)
    monkeypatch.setattr(connectivity, "NETWORK_READY_POLL_SECONDS", 1)
    monkeypatch.setattr(connectivity.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(connectivity, "sleep", clock.sleep)

    # When/Then: timeout fails and includes every required guest diagnostic.
    with pytest.raises(AssertionError) as failure:
        case._wait_for_guest_network()
    message = str(failure.value)
    assert "Guest network readiness timeout" in message
    assert "1 packets transmitted, 0 received" in message
    assert "$ ip -4 addr" in message
    assert "inet 192.0.2.10/24 scope global ovsbr0" in message
    assert "$ ip route" in message
    assert "192.0.2.0/24 dev ovsbr0" in message
    assert "$ networkctl --no-pager --full" in message
    assert "ovsbr0 routable" in message


def test_guest_network_readiness_rejects_wrong_expected_ip(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: the guest never reports the selected target address.
    target = FakeConnectivityTarget([(1, "address mismatch")])
    target.ip = "192.0.2.11"
    case = _connectivity_case(target)
    clock = FakeClock()
    monkeypatch.setattr(connectivity, "NETWORK_READY_TIMEOUT_SECONDS", 1)
    monkeypatch.setattr(connectivity, "NETWORK_READY_POLL_SECONDS", 1)
    monkeypatch.setattr(connectivity.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(connectivity, "sleep", clock.sleep)

    # When/Then: the valid but wrong address fails instead of passing loosely.
    with pytest.raises(AssertionError, match="target 192.0.2.11"):
        case._wait_for_guest_network()
    assert "inet 192.0.2.11/" in target.commands[0][0]


def test_guest_network_serial_error_never_passes_silently(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: readiness commands encounter serial timeout and EOF failures.
    target = FakeConnectivityTarget([pexpect.TIMEOUT, pexpect.EOF])
    case = _connectivity_case(target)
    clock = FakeClock()
    monkeypatch.setattr(connectivity, "NETWORK_READY_TIMEOUT_SECONDS", 2)
    monkeypatch.setattr(connectivity, "NETWORK_READY_POLL_SECONDS", 1)
    monkeypatch.setattr(connectivity.time, "monotonic", clock.monotonic)
    monkeypatch.setattr(connectivity, "sleep", clock.sleep)

    # When/Then: the final failure names the serial cause and diagnostics.
    with pytest.raises(AssertionError) as failure:
        case._wait_for_guest_network()
    message = str(failure.value)
    assert "EOF" in message
    assert "$ ip -4 addr" in message


class FakeHostPing:
    def communicate(self) -> tuple[bytes, None]:
        return b"host ping ok\n", None

    def poll(self) -> int:
        return 0


def test_host_ping_remains_five_and_uses_argv_not_shell(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: guest readiness is immediate and each host ping succeeds.
    target = FakeConnectivityTarget([(0, "ready")])
    case = _connectivity_case(target)
    observed: list[list[str]] = []

    def fake_popen(argv: list[str], stdout: int) -> FakeHostPing:
        assert stdout == connectivity.PIPE
        observed.append(argv)
        return FakeHostPing()

    monkeypatch.setattr(connectivity, "Popen", fake_popen)

    # When: the strict connectivity case executes.
    case.test_ping()

    # Then: exactly five host ping processes use non-shell argv.
    assert observed == [["ping", "-c", "1", "192.0.2.10"]] * 5


def test_ssh_failure_uses_target_serial_diagnostics() -> None:
    # Given: SSH returns an unexpected status after network readiness passed.
    target = FakeConnectivityTarget([(0, "ready")], ssh_status=1)
    case = _connectivity_case(target)

    # When/Then: the failure includes diagnostics from the target serial API.
    with pytest.raises(AssertionError) as failure:
        case.test_ssh()
    assert "uname failed" in str(failure.value)
    assert [command for command, _timeout in target.commands] == list(
        connectivity.NETWORK_DIAGNOSTIC_COMMANDS
    )


@pytest.mark.parametrize("field", ["ip", "server_ip"])
def test_connectivity_rejects_untrusted_address_before_command(
    field: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: an address field contains shell command syntax.
    target = FakeConnectivityTarget([(0, "ready")])
    setattr(target, field, "192.0.2.10; injected")
    case = _connectivity_case(target)
    monkeypatch.setattr(
        connectivity,
        "Popen",
        lambda *_args, **_kwargs: pytest.fail("host command executed"),
    )

    # When/Then: validation fails before serial or host command execution.
    with pytest.raises(AssertionError, match="valid IPv4"):
        case.test_ping()
    assert target.commands == []
