from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
HSOCFVP = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/controllers/"
    / "hsocfvp.py"
)


class FakeTimeout(Exception):
    pass


class FakeLogger:
    def __getattr__(self, name):
        def log(*args, **kwargs):
            return None

        return log


class FakeTerminal:
    def __init__(self, *results):
        self.results = list(results)
        self.sends: list[bytes] = []
        self.timeouts: list[float | None] = []
        self.before = b""

    def send(self, payload: bytes) -> None:
        self.sends.append(payload)

    def expect(self, patterns, *args, timeout=None, **kwargs):
        self.timeouts.append(timeout)
        result = self.results.pop(0)
        if isinstance(result, tuple):
            result, self.before = result
        if result == "timeout":
            raise FakeTimeout()
        return result


def load_module(monkeypatch: pytest.MonkeyPatch):
    pexpect_module = ModuleType("pexpect")
    pexpect_module.TIMEOUT = FakeTimeout

    oeqa_module = ModuleType("oeqa")
    controllers_module = ModuleType("oeqa.controllers")
    fvp_module = ModuleType("oeqa.controllers.fvp")

    class OEFVPTarget:
        def transition(self, state, timeout=10 * 60):
            self.transition_calls.append((state, timeout))

        def __getattr__(self, name):
            def call_pexpect(*args, **kwargs):
                return None

            return call_pexpect

    class OEFVPTargetState:
        OFF = "off"
        ON = "on"

    fvp_module.OEFVPTarget = OEFVPTarget
    fvp_module.OEFVPTargetState = OEFVPTargetState

    monkeypatch.setitem(sys.modules, "pexpect", pexpect_module)
    monkeypatch.setitem(sys.modules, "oeqa", oeqa_module)
    monkeypatch.setitem(sys.modules, "oeqa.controllers", controllers_module)
    monkeypatch.setitem(sys.modules, "oeqa.controllers.fvp", fvp_module)

    spec = importlib.util.spec_from_file_location("hsocfvp_under_test", HSOCFVP)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def make_target(module, terminal: FakeTerminal):
    target = module.HSOCOEFVPTarget.__new__(module.HSOCOEFVPTarget)
    target.terminals = {"default": terminal}
    target.logger = FakeLogger()
    return target


def test_login_prompt_wait_sends_cr_and_retries_after_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(monkeypatch)
    terminal = FakeTerminal(("timeout", b"Reached target Login Prompts"), 0)
    target = make_target(module, terminal)

    result = target.expect("default", "login\\:", timeout=60)

    assert result == 0
    assert terminal.sends == [b"\r"]
    assert terminal.timeouts
    assert all(
        timeout <= module.LOGIN_PROMPT_NUDGE_INTERVAL_S
        for timeout in terminal.timeouts
    )


def test_login_prompt_wait_does_not_stop_uboot_autoboot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(monkeypatch)
    terminal = FakeTerminal(("timeout", b"Hit any key to stop autoboot"), 0)
    target = make_target(module, terminal)

    result = target.expect("default", "login\\:", timeout=60)

    assert result == 0
    assert terminal.sends == []


def test_non_login_timeout_is_not_retried(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(monkeypatch)
    terminal = FakeTerminal("timeout")
    target = make_target(module, terminal)

    with pytest.raises(FakeTimeout):
        target.expect("default", "booted", timeout=60)

    assert terminal.sends == []


def test_terminal_status_query_still_gets_answered(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_module(monkeypatch)
    terminal = FakeTerminal(1, 0)
    target = make_target(module, terminal)

    result = target.expect("default", "ready", timeout=60)

    assert result == 0
    assert terminal.sends == [module.TERMINAL_STATUS_RESPONSE]


def test_transition_on_resets_writable_flash_from_read_images(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    module = load_module(monkeypatch)
    deploy_dir = tmp_path / "deploy"
    writable_dir = tmp_path / "writable"
    deploy_dir.mkdir()
    writable_dir.mkdir()
    read_rse = deploy_dir / "rse-flash-image.img"
    read_ap = deploy_dir / "ap-flash-image.img"
    write_rse = writable_dir / "rse-flash-image.img"
    write_ap = writable_dir / "ap-flash-image.img"
    otp_image = deploy_dir / "rse-otp-image.img"
    read_rse.write_bytes(b"clean-rse")
    read_ap.write_bytes(b"clean-ap")
    otp_image.write_bytes(b"clean-otp")
    write_rse.write_bytes(b"dirty-rse")
    write_ap.write_bytes(b"dirty-ap")

    fvpconf = tmp_path / "image.fvpconf"
    fvpconf.write_text(
        json.dumps(
            {
                "parameters": {
                    "css.smb.rseil.rse_flashloader.fname": str(read_rse),
                    "css.smb.rseil.rse_flashloader.fnameWrite": str(write_rse),
                    "ros.flash_loader.fname": str(read_ap),
                    "ros.flash_loader.fnameWrite": str(write_ap),
                    "css.smb.rseil.rse.lcm_nvm.raw_image": str(otp_image),
                }
            }
        ),
        encoding="utf-8",
    )

    target = module.HSOCOEFVPTarget.__new__(module.HSOCOEFVPTarget)
    target.fvpconf = fvpconf
    target.logger = FakeLogger()
    target.transition_calls = []

    target.transition(module.OEFVPTargetState.ON, timeout=42)

    assert write_rse.read_bytes() == b"clean-rse"
    assert write_ap.read_bytes() == b"clean-ap"
    assert (writable_dir / "rse-otp-image.img").read_bytes() == b"clean-otp"
    runtime_fvpconf = json.loads(target.fvpconf.read_text(encoding="utf-8"))
    runtime_params = runtime_fvpconf["parameters"]
    assert runtime_params["css.smb.rseil.rse_flashloader.fname"] == str(read_rse)
    assert runtime_params["css.smb.rseil.rse_flashloader.fnameWrite"] == str(
        write_rse
    )
    assert runtime_params["ros.flash_loader.fname"] == str(read_ap)
    assert runtime_params["ros.flash_loader.fnameWrite"] == str(write_ap)
    assert runtime_params["css.smb.rseil.rse.lcm_nvm.raw_image"] == str(
        writable_dir / "rse-otp-image.img"
    )
    assert target.transition_calls == [(module.OEFVPTargetState.ON, 42)]
