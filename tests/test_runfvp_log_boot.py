from __future__ import annotations

import importlib.util
import io
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
