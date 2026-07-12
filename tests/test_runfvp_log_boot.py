from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
import threading


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run/runfvp_log_boot.py"


def load_module():
    spec = importlib.util.spec_from_file_location("runfvp_log_boot", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeProcess:
    def __init__(self, text: str) -> None:
        self.stdout = io.StringIO(text)
        self.stdin = io.StringIO()


def test_console_capture_ignores_uboot_terminal_status_query() -> None:
    module = load_module()
    capture = module.ConsoleCapture(
        term="terminal_ns_uart0",
        port=5004,
        log_path=Path("unused.log"),
        marker_hits={},
        marker_lock=threading.Lock(),
        start_time=0.0,
    )
    proc = FakeProcess("\x1b[6n\n")
    capture.proc = proc
    capture._file = io.StringIO()

    capture._reader()

    assert proc.stdin.getvalue() == ""


def test_console_capture_answers_login_terminal_status_query() -> None:
    module = load_module()
    capture = module.ConsoleCapture(
        term="terminal_ns_uart0",
        port=5004,
        log_path=Path("unused.log"),
        marker_hits={},
        marker_lock=threading.Lock(),
        start_time=0.0,
    )
    proc = FakeProcess("Reached target Login Prompts\n\x1b[6n\n")
    capture.proc = proc
    capture._file = io.StringIO()

    capture._reader()

    assert proc.stdin.getvalue() == "\x1b[32766;32766R"


def test_copy_writable_flash_uses_read_image_when_write_path_is_missing(
    tmp_path: Path,
) -> None:
    module = load_module()
    deploy_dir = tmp_path / "deploy"
    read_image = deploy_dir / "rse-flash-image.img"
    missing_write_image = tmp_path / "fvp-writable/rse-flash-image.img"
    deploy_dir.mkdir()
    read_image.write_bytes(b"clean-read-flash")

    args = module.copy_writable_flash(
        {
            "parameters": {
                "css.rse.flash_loader.fname": str(read_image),
                "css.rse.flash_loader.fnameWrite": str(missing_write_image),
            }
        },
        tmp_path / "out",
    )

    writable = tmp_path / "out/writable-images/rse-flash-image.img"
    assert writable.read_bytes() == b"clean-read-flash"
    assert args == [
        "--parameter",
        f"css.rse.flash_loader.fnameWrite={writable}",
    ]


def test_copy_writable_flash_copies_rse_otp_nvm_image(tmp_path: Path) -> None:
    module = load_module()
    deploy_dir = tmp_path / "deploy"
    otp_image = deploy_dir / "rse-otp-image.img"
    deploy_dir.mkdir()
    otp_image.write_bytes(b"clean-otp")

    args = module.copy_writable_flash(
        {
            "parameters": {
                "css.smb.rseil.rse.lcm_nvm.raw_image": str(otp_image),
            }
        },
        tmp_path / "out",
    )

    writable = tmp_path / "out/writable-images/rse-otp-image.img"
    assert writable.read_bytes() == b"clean-otp"
    assert args == [
        "--parameter",
        f"css.smb.rseil.rse.lcm_nvm.raw_image={writable}",
    ]


def test_primary_console_accepts_systemd_multi_user_as_boot_ready() -> None:
    module = load_module()

    status = module.check_console(
        "terminal_ns_uart0",
        "\n".join(
            [
                "U-Boot 2024.01",
                "Booting Linux on physical CPU 0x0000000000 [0x410fd490]",
                "Linux version 6.12.0",
                "Reached target \x1b[0;1;39mMulti-User System\x1b[0m.",
            ]
        ),
    )

    assert status["passed"]


def test_empty_terminal_configuration_cannot_pass_boot() -> None:
    module = load_module()

    status = module.build_status(set(), {}, {}, "all")

    assert not status["passed"]
    assert status["missing_required_patterns"]


def test_default_fvpconf_skips_incomplete_stable_config(tmp_path: Path) -> None:
    module = load_module()
    deploy = tmp_path / "build/tmp_baremetal/deploy/images/apollo-fvp"
    deploy.mkdir(parents=True)
    stable = deploy / "nexios-image-apollo-fvp.fvpconf"
    valid = deploy / "nexios-image-apollo-fvp-20260712000000.fvpconf"
    stable.write_text(json.dumps({"terminals": {}}), encoding="utf-8")
    valid.write_text(
        json.dumps(
            {
                "terminals": {
                    f"css.{terminal}": terminal
                    for terminal in module.CHECKS
                }
            }
        ),
        encoding="utf-8",
    )

    selected = module.resolve_default_fvpconf(tmp_path, "apollo-fvp", "all")

    assert selected == valid


def test_runtime_configuration_rejects_small_wic(tmp_path: Path) -> None:
    module = load_module()
    wic = tmp_path / "nexios-image-apollo-fvp.wic"
    wic.write_text("not a disk image\n", encoding="utf-8")

    errors = module.runtime_configuration_errors(
        {"parameters": {"ros.virtio_block0.image_path": str(wic)}}
    )

    assert len(errors) == 1
    assert "implausibly small" in errors[0]
