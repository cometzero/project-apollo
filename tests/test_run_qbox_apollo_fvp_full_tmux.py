from __future__ import annotations

import os
from pathlib import Path
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


def test_uart_console_sends_guest_ctrl_c_when_sigint_received(
    tmp_path: Path,
) -> None:
    # Given: a UART console helper connected to the same FIFO shape QBox uses.
    log_path = tmp_path / "qbox-primary-console.log"
    fifo_path = tmp_path / "primary-uart-input.fifo"
    input_capture = tmp_path / "primary-input.bin"
    log_path.write_text("primary boot log\n", encoding="utf-8")
    os.mkfifo(fifo_path)

    fifo_reader = subprocess.Popen(
        [
            "python3",
            "-c",
            (
                "from pathlib import Path\n"
                "import sys\n"
                "data = Path(sys.argv[1]).open('rb').read(1)\n"
                "Path(sys.argv[2]).write_bytes(data)\n"
            ),
            str(fifo_path),
            str(input_capture),
        ],
        stderr=subprocess.PIPE,
    )
    try:
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

            # When: tmux/user Ctrl+C is delivered as SIGINT to the pane process.
            proc.send_signal(signal.SIGINT)

            # Then: the console remains alive and forwards ETX to the guest FIFO.
            try:
                proc.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                pass
            else:
                assert False, f"UART console exited with {proc.returncode}"

            fifo_reader.wait(timeout=5.0)
            assert input_capture.read_bytes() == b"\x03"
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2.0)
    finally:
        fifo_reader.terminate()
        try:
            fifo_reader.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            fifo_reader.kill()
            fifo_reader.wait(timeout=2.0)
