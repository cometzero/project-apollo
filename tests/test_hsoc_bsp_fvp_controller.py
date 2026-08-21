from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from threading import Lock

import pytest


ROOT = Path(__file__).resolve().parents[1]
for module_path in (
    ROOT / "qa-tests",
    ROOT / "hsoc-stack/yocto/meta-hsoc-auto-solutions/lib",
    ROOT / "layers/meta-arm/meta-arm/lib",
    ROOT / "layers/poky/meta/lib",
):
    sys.path.insert(0, str(module_path))

from oeqa.controllers.fvp import OEFVPTargetState  # noqa: E402
from apollo_validation.root_cli import parse_root_args  # noqa: E402
from apollo_validation.selection import (  # noqa: E402
    prepare_selection,
    selected_test_environment,
)
from oeqa.controllers.hsocfvp import (  # noqa: E402
    HSOCBSPFVPTarget,
    HSOCSingleSessionFVPTarget,
)


class FakeMatch:
    def group(self, index: int) -> bytes:
        assert index == 1
        return b"7"


class FakeLogger:
    def info(self, message: str) -> None:
        assert message

    def debug(self, message: str, *values: str | Path) -> None:
        assert message
        assert values


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


SI_CL1_UART = "css.smb.si.cluster1_pl011_uart.uart_enable"
FVP_USER_NETWORKING = "ros.virtio_net.hostbridge.userNetworking"
FVP_INTERFACE_NAME = "ros.virtio_net.hostbridge.interfaceName"
PROFILE_ENV = "APOLLO_VALIDATION_FVP_CONFIG"


def _runtime_target(tmp_path: Path) -> tuple[HSOCBSPFVPTarget, Path]:
    deploy = tmp_path / "deploy"
    deploy.mkdir()
    source_image = deploy / "flash.bin"
    source_image.write_bytes(b"source flash")
    source = deploy / "image.fvpconf"
    source.write_text(
        json.dumps(
            {
                "parameters": {
                    SI_CL1_UART: "0",
                    "ros.flash_loader.fname": str(source_image),
                    "ros.flash_loader.fnameWrite": str(source_image),
                }
            }
        ),
        encoding="utf-8",
    )
    target = HSOCBSPFVPTarget.__new__(HSOCBSPFVPTarget)
    target.fvpconf = source
    target.bootlog = str(tmp_path / "run/logs/default.log")
    target.logger = FakeLogger()
    return target, source


def _product_runtime_target(
    tmp_path: Path,
) -> tuple[HSOCSingleSessionFVPTarget, Path]:
    deploy = tmp_path / "deploy"
    deploy.mkdir()
    source_image = deploy / "flash.bin"
    source_image.write_bytes(b"source flash")
    source = deploy / "image.fvpconf"
    source.write_text(
        json.dumps(
            {
                "parameters": {
                    FVP_USER_NETWORKING: "1",
                    "ros.flash_loader.fname": str(source_image),
                    "ros.flash_loader.fnameWrite": str(source_image),
                }
            }
        ),
        encoding="utf-8",
    )
    target = HSOCSingleSessionFVPTarget.__new__(HSOCSingleSessionFVPTarget)
    target.fvpconf = source
    target.bootlog = str(tmp_path / "run/logs/default.log")
    target.logger = FakeLogger()
    return target, source


def test_platform_profile_config_reaches_product_runtime_fvpconf(
    tmp_path: Path,
) -> None:
    # Given: the selected platform profile and its immutable deployed config.
    options = parse_root_args(
        ["--fvp", "--headless", "--test-profile", "platform-devices"]
    )
    selection, _resolved = prepare_selection(ROOT, options)
    assert selection is not None
    target, source = _product_runtime_target(tmp_path)
    source_bytes = source.read_bytes()

    # When: the product controller prepares the selected runtime config.
    with selected_test_environment(selection):
        target._reset_writable_flash()

    # Then: the private copy uses TAP networking and records both parameters.
    assert source.read_bytes() == source_bytes
    runtime = json.loads(target.fvpconf.read_text(encoding="utf-8"))
    assert runtime["parameters"][FVP_USER_NETWORKING] == "0"
    assert runtime["parameters"][FVP_INTERFACE_NAME] == "apollo-fvp-tap0"
    receipt = json.loads(
        (target.fvpconf.parent / "fvp-config-application.json").read_text(
            encoding="utf-8"
        )
    )
    assert receipt["applied_fvp_config"] == {
        FVP_INTERFACE_NAME: "apollo-fvp-tap0",
        FVP_USER_NETWORKING: "0",
    }
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    assert receipt["source_sha256"] == source_hash
    assert receipt["source_after_sha256"] == source_hash


def test_profile_config_uses_private_runtime_fvpconf(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: a selected profile map and an immutable deployed FVP config.
    target, source = _runtime_target(tmp_path)
    source_bytes = source.read_bytes()
    monkeypatch.setenv(PROFILE_ENV, json.dumps({SI_CL1_UART: "1"}))

    # When: the controller prepares writable runtime state.
    target._reset_writable_flash()

    # Then: only the private runtime copy carries the selected UART override.
    assert source.read_bytes() == source_bytes
    assert target.fvpconf != source
    runtime = json.loads(target.fvpconf.read_text(encoding="utf-8"))
    assert runtime["parameters"][SI_CL1_UART] == "1"
    receipt = target.fvpconf.parent / "fvp-config-application.json"
    evidence = json.loads(receipt.read_text(encoding="utf-8"))
    assert evidence["applied_fvp_config"] == {SI_CL1_UART: "1"}
    assert evidence["source_sha256"] == hashlib.sha256(source_bytes).hexdigest()


def test_default_controller_preserves_deployed_uart_value(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: no selected profile FVP config.
    target, source = _runtime_target(tmp_path)
    monkeypatch.delenv(PROFILE_ENV, raising=False)

    # When: normal writable runtime state is prepared.
    target._reset_writable_flash()

    # Then: the default UART value remains zero and no profile receipt exists.
    assert source.read_bytes()
    runtime = json.loads(target.fvpconf.read_text(encoding="utf-8"))
    assert runtime["parameters"][SI_CL1_UART] == "0"
    assert not (target.fvpconf.parent / "fvp-config-application.json").exists()


@pytest.mark.parametrize(
    "payload",
    [
        {"unknown.parameter": "1"},
        {SI_CL1_UART: ["1"]},
        {SI_CL1_UART: '1\"\\nINJECT = "1'},
        {FVP_USER_NETWORKING: "1"},
        {FVP_INTERFACE_NAME: "tap0; injected"},
    ],
)
def test_controller_rejects_malformed_profile_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    payload: object,
) -> None:
    # Given: malformed data at the controller environment boundary.
    target, _source = _runtime_target(tmp_path)
    monkeypatch.setenv(PROFILE_ENV, json.dumps(payload))

    # When/Then: the controller rejects it before creating a runtime config.
    with pytest.raises(ValueError, match="FVP config"):
        target._reset_writable_flash()


def test_profile_runtime_reset_restarts_from_immutable_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: a prior private runtime copy was externally changed after one run.
    target, source = _runtime_target(tmp_path)
    source_bytes = source.read_bytes()
    monkeypatch.setenv(PROFILE_ENV, json.dumps({SI_CL1_UART: "1"}))
    target._reset_writable_flash()
    target.fvpconf.write_text(
        json.dumps({"parameters": {SI_CL1_UART: "stale"}}),
        encoding="utf-8",
    )

    # When: the controller resets for another transition.
    target._reset_writable_flash()

    # Then: it reapplies the selected map from the immutable deployed source.
    runtime = json.loads(target.fvpconf.read_text(encoding="utf-8"))
    assert runtime["parameters"][SI_CL1_UART] == "1"
    assert source.read_bytes() == source_bytes
