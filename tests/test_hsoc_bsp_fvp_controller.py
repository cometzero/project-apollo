from __future__ import annotations

from pathlib import Path
import sys
from threading import Lock


ROOT = Path(__file__).resolve().parents[1]
for module_path in (
    ROOT / "hsoc-stack/yocto/meta-hsoc-auto-solutions/lib",
    ROOT / "layers/meta-arm/meta-arm/lib",
    ROOT / "layers/poky/meta/lib",
):
    sys.path.insert(0, str(module_path))

from oeqa.controllers.fvp import OEFVPTargetState  # noqa: E402
from oeqa.controllers.hsocfvp import HSOCBSPFVPTarget  # noqa: E402


class FakeMatch:
    def group(self, index: int) -> bytes:
        assert index == 1
        return b"7"


class FakeLogger:
    def info(self, message: str) -> None:
        assert message


class FakeBspTarget(HSOCBSPFVPTarget):
    def __init__(self) -> None:
        self.state = OEFVPTargetState.LINUX
        self.timeout = 10
        self._hsoc_bsp_command_lock = Lock()
        self._hsoc_bsp_command_index = 0
        self.logger = FakeLogger()
        self.sent: list[str] = []
        self.expected: list[str] = []

    def sendline(self, terminal: str, text: str) -> None:
        assert terminal == self.DEFAULT_CONSOLE
        self.sent.append(text)

    def expect(self, terminal: str, pattern, timeout: int) -> int:
        assert terminal == self.DEFAULT_CONSOLE
        assert timeout == 5
        self.expected.append(str(pattern))
        return 0

    def before(self, terminal: str) -> bytes:
        assert terminal == self.DEFAULT_CONSOLE
        return b"payload output\r\n"

    def match(self, terminal: str) -> FakeMatch:
        assert terminal == self.DEFAULT_CONSOLE
        return FakeMatch()


def test_bsp_target_runs_command_over_primary_console() -> None:
    # Given: an already booted BSP serial target.
    target = FakeBspTarget()

    # When: OEQA runs a command through its target API.
    status, output = target.run("pfdi-cli --info", timeout=5)

    # Then: exit status and output come from unique serial markers.
    assert status == 7
    assert output == "payload output"
    assert len(target.sent) == 1
    assert "pfdi-cli --info" in target.sent[0]
    assert "__OEQA_BSP_BEGIN_00000001__" in target.sent[0]
    assert len(target.expected) == 3


def test_bsp_target_keeps_linux_session_for_on_transition() -> None:
    # Given: a BSP FVP session that already reached its shell.
    target = FakeBspTarget()

    # When: a console-only OEQA test requests the ON state.
    target.transition(OEFVPTargetState.ON)

    # Then: the running BSP session remains available without a reboot.
    assert target.state == OEFVPTargetState.LINUX
