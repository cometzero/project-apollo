from __future__ import annotations

import os
from pathlib import Path
import pty
import select
import signal
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]
TMUX_SCRIPT = ROOT / "scripts/run/run_qbox_apollo_fvp_full_tmux.sh"


def read_until(
    proc: subprocess.Popen[bytes],
    needle: bytes,
    timeout_seconds: float,
) -> bytes:
    assert proc.stdout is not None
    deadline = time.monotonic() + timeout_seconds
    output = bytearray()
    fd = proc.stdout.fileno()

    while time.monotonic() < deadline:
        ready, _writable, _errors = select.select([fd], [], [], 0.05)
        if fd in ready:
            chunk = os.read(fd, 4096)
            if not chunk:
                break
            output.extend(chunk)
            if needle in output:
                return bytes(output)
        if proc.poll() is not None:
            break

    raise AssertionError(
        f"timed out waiting for {needle!r}; output was {bytes(output)!r}",
    )


def read_fd_once(fd: int, timeout_seconds: float) -> bytes:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        ready, _writable, _errors = select.select([fd], [], [], 0.05)
        if fd not in ready:
            continue
        chunk = os.read(fd, 4096)
        if chunk:
            return chunk

    return b""


def launch_primary_uart_console(
    tmp_path: Path,
) -> tuple[subprocess.Popen[bytes], Path]:
    log_path = tmp_path / "qbox-primary-console.log"
    fifo_path = tmp_path / "primary-uart-input.fifo"
    log_path.write_text("primary boot log\n", encoding="utf-8")
    os.mkfifo(fifo_path)

    proc = subprocess.Popen(
        [
            str(TMUX_SCRIPT),
            "--uart-console",
            "primary_console",
            "Primary Compute",
            str(log_path),
        ],
        cwd=ROOT,
        env={**os.environ, "OUT_DIR": str(tmp_path)},
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        read_until(proc, b"UART is interactive", 5.0)
    except Exception:
        terminate_process(proc)
        raise

    return proc, fifo_path


def launch_primary_uart_console_on_pty(
    tmp_path: Path,
) -> tuple[subprocess.Popen[bytes], Path, int]:
    log_path = tmp_path / "qbox-primary-console.log"
    fifo_path = tmp_path / "primary-uart-input.fifo"
    log_path.write_text("primary boot log\n", encoding="utf-8")
    os.mkfifo(fifo_path)
    master_fd, slave_fd = pty.openpty()
    proc = subprocess.Popen(
        [
            str(TMUX_SCRIPT),
            "--uart-console",
            "primary_console",
            "Primary Compute",
            str(log_path),
        ],
        cwd=ROOT,
        env={**os.environ, "OUT_DIR": str(tmp_path)},
        stdin=slave_fd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    os.close(slave_fd)
    try:
        read_until(proc, b"UART is interactive", 5.0)
    except Exception:
        os.close(master_fd)
        terminate_process(proc)
        raise

    return proc, fifo_path, master_fd


def terminate_process(proc: subprocess.Popen[bytes]) -> None:
    proc.terminate()
    try:
        proc.wait(timeout=2.0)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=2.0)


def test_uart_console_sends_guest_ctrl_c_when_sigint_received(
    tmp_path: Path,
) -> None:
    # Given: a UART console helper connected to the same FIFO shape QBox uses.
    proc, fifo_path = launch_primary_uart_console(tmp_path)
    fifo_fd = os.open(fifo_path, os.O_RDONLY | os.O_NONBLOCK)

    try:
        # When: tmux/user Ctrl+C is delivered as SIGINT to the pane process.
        proc.send_signal(signal.SIGINT)

        # Then: the console remains alive and forwards ETX to the guest FIFO.
        try:
            proc.wait(timeout=0.5)
        except subprocess.TimeoutExpired:
            pass
        else:
            assert False, f"UART console exited with {proc.returncode}"

        assert read_fd_once(fifo_fd, 5.0) == b"\x03"
    finally:
        os.close(fifo_fd)
        terminate_process(proc)


def test_uart_console_drops_terminal_cursor_position_reports(
    tmp_path: Path,
) -> None:
    proc, fifo_path = launch_primary_uart_console(tmp_path)
    fifo_fd = os.open(fifo_path, os.O_RDONLY | os.O_NONBLOCK)

    try:
        assert proc.stdin is not None
        proc.stdin.write(b"\x1b[33;98R\n^[[33;9R\n")
        proc.stdin.flush()

        assert read_fd_once(fifo_fd, 0.5) == b""
    finally:
        os.close(fifo_fd)
        terminate_process(proc)


def test_uart_console_strips_cursor_position_reports_around_input(
    tmp_path: Path,
) -> None:
    proc, fifo_path = launch_primary_uart_console(tmp_path)
    fifo_fd = os.open(fifo_path, os.O_RDONLY | os.O_NONBLOCK)

    try:
        assert proc.stdin is not None
        proc.stdin.write(b"\x1b[33;98Rroot^[[33;9R\n")
        proc.stdin.flush()

        assert read_fd_once(fifo_fd, 5.0) == b"root\n"
    finally:
        os.close(fifo_fd)
        terminate_process(proc)


def test_uart_console_preserves_empty_enter(
    tmp_path: Path,
) -> None:
    proc, fifo_path = launch_primary_uart_console(tmp_path)
    fifo_fd = os.open(fifo_path, os.O_RDONLY | os.O_NONBLOCK)

    try:
        assert proc.stdin is not None
        proc.stdin.write(b"\n")
        proc.stdin.flush()

        assert read_fd_once(fifo_fd, 5.0) == b"\n"
    finally:
        os.close(fifo_fd)
        terminate_process(proc)


def test_uart_console_disables_local_tty_echo(
    tmp_path: Path,
) -> None:
    proc, fifo_path, master_fd = launch_primary_uart_console_on_pty(tmp_path)
    fifo_fd = -1

    try:
        fifo_fd = os.open(fifo_path, os.O_RDONLY | os.O_NONBLOCK)

        os.write(master_fd, b"e")

        assert read_fd_once(fifo_fd, 5.0) == b"e"
        assert read_fd_once(master_fd, 0.5) == b""
    finally:
        if fifo_fd >= 0:
            os.close(fifo_fd)
        os.close(master_fd)
        terminate_process(proc)


def test_uart_console_filters_tty_cursor_position_response_bytes(
    tmp_path: Path,
) -> None:
    proc, fifo_path, master_fd = launch_primary_uart_console_on_pty(tmp_path)
    fifo_fd = -1

    try:
        fifo_fd = os.open(fifo_path, os.O_RDONLY | os.O_NONBLOCK)

        os.write(master_fd, b"\x1b[33;98R")

        assert read_fd_once(fifo_fd, 0.5) == b""

        os.write(master_fd, b"x")
        assert read_fd_once(fifo_fd, 5.0) == b"x"
        assert read_fd_once(master_fd, 0.5) == b""
    finally:
        if fifo_fd >= 0:
            os.close(fifo_fd)
        os.close(master_fd)
        terminate_process(proc)


def test_uart_console_forwards_tty_input_without_waiting_for_enter(
    tmp_path: Path,
) -> None:
    proc, fifo_path, master_fd = launch_primary_uart_console_on_pty(tmp_path)
    fifo_fd = -1

    try:
        fifo_fd = os.open(fifo_path, os.O_RDONLY | os.O_NONBLOCK)

        os.write(master_fd, b"r")

        assert read_fd_once(fifo_fd, 0.5) == b"r"
        assert read_fd_once(master_fd, 0.5) == b""
    finally:
        if fifo_fd >= 0:
            os.close(fifo_fd)
        os.close(master_fd)
        terminate_process(proc)
