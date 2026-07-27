from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/debug/run_agent_qbox_debug.py"


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def executable(path: Path, body: str) -> Path:
    path.write_text("#!/usr/bin/env python3\n" + body, encoding="utf-8")
    path.chmod(0o755)
    return path


def write_fixture(tmp_path: Path, *, observed_pc: int) -> tuple[Path, Path, Path]:
    fake_gdb = executable(
        tmp_path / "fake-gdb",
        "from pathlib import Path\n"
        "import sys\n"
        f"Path({str(tmp_path / 'gdb.argv')!r}).write_text('\\n'.join(sys.argv[1:]))\n"
        "print('agent_debug_pc=0x%x' % " + str(observed_pc) + ")\n"
        "print('bl2_main at bl2_main.c:44')\n",
    )
    gdb_script = tmp_path / "tfa-bl2.gdb"
    gdb_script.write_text("set pagination off\n", encoding="utf-8")
    elf = tmp_path / "bl2.elf"
    elf.write_bytes(b"ELF")
    manifest = tmp_path / "symbols.json"
    manifest.write_text(
        json.dumps(
            {
                "components": {
                    "tfa-bl2": {
                        "name": "tfa-bl2",
                        "domain": "ap",
                        "debugger": str(fake_gdb),
                        "elf": str(elf),
                        "gdb_script": str(gdb_script),
                        "has_debug_info": True,
                        "remote": "127.0.0.1:1",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    runner = executable(
        tmp_path / "fake-runner",
        "from pathlib import Path\n"
        "import os\n"
        "import socket\n"
        "import subprocess\n"
        "import sys\n"
        "import time\n"
        "port = int(sys.argv[1])\n"
        "marker = Path(sys.argv[2])\n"
        "pid_file = Path(sys.argv[3])\n"
        "child = subprocess.Popen(\n"
        "    [sys.executable, '-c', 'import time; time.sleep(60)'],\n"
        "    start_new_session=True,\n"
        ")\n"
        "pid_file.write_text(f'{os.getpid()} {child.pid}')\n"
        f"marker.write_text('QBox GDB entry breakpoint reached: 0x{observed_pc:x}\\n')\n"
        "with socket.socket() as listener:\n"
        "    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\n"
        "    listener.bind(('127.0.0.1', port))\n"
        "    listener.listen()\n"
        "    while True:\n"
        "        time.sleep(0.1)\n",
    )
    return manifest, runner, fake_gdb


def process_is_gone(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    return False


def test_probe_records_pc_and_cleans_runner(tmp_path: Path) -> None:
    port = free_port()
    out_dir = tmp_path / "out"
    pid_file = tmp_path / "runner.pid"
    manifest, runner, _ = write_fixture(tmp_path, observed_pc=0x1000)

    result = subprocess.run(
        [
            str(SCRIPT),
            "--mode",
            "probe",
            "--target",
            "tf-a",
            "--component",
            "tfa-bl2",
            "--breakpoint",
            "bl2_main",
            "--expected-pc",
            "0x1000",
            "--endpoint",
            f"127.0.0.1:{port}",
            "--manifest",
            str(manifest),
            "--out-dir",
            str(out_dir),
            "--timeout",
            "2",
            "--wait-log",
            str(out_dir / "qbox-platform.log"),
            "--wait-marker",
            "QBox GDB entry breakpoint reached:",
            "--",
            str(runner),
            str(port),
            str(out_dir / "qbox-platform.log"),
            str(pid_file),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    decoded = json.loads((out_dir / "debug-result.json").read_text())
    assert decoded["backend"] == "qbox-gdb"
    assert decoded["status"] == "passed"
    assert decoded["breakpoint_hit"] is True
    assert decoded["expected_pc"] == "0x1000"
    assert decoded["observed_pc"] == "0x1000"
    assert decoded["cleanup_completed"] is True
    assert "bl2_main at bl2_main.c:44" in (out_dir / "gdb.log").read_text()
    gdb_argv = (tmp_path / "gdb.argv").read_text().splitlines()
    assert "continue" not in gdb_argv
    assert not any(value.startswith("target remote ") for value in gdb_argv)
    assert all(process_is_gone(int(pid)) for pid in pid_file.read_text().split())


def test_probe_reports_pc_mismatch(tmp_path: Path) -> None:
    port = free_port()
    out_dir = tmp_path / "out"
    pid_file = tmp_path / "runner.pid"
    manifest, runner, _ = write_fixture(tmp_path, observed_pc=0x2000)

    result = subprocess.run(
        [
            str(SCRIPT),
            "--mode",
            "probe",
            "--target",
            "tf-a",
            "--component",
            "tfa-bl2",
            "--breakpoint",
            "bl2_main",
            "--expected-pc",
            "0x1000",
            "--endpoint",
            f"127.0.0.1:{port}",
            "--manifest",
            str(manifest),
            "--out-dir",
            str(out_dir),
            "--timeout",
            "2",
            "--wait-log",
            str(out_dir / "qbox-platform.log"),
            "--wait-marker",
            "QBox GDB entry breakpoint reached:",
            "--",
            str(runner),
            str(port),
            str(out_dir / "qbox-platform.log"),
            str(pid_file),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 4
    decoded = json.loads((out_dir / "debug-result.json").read_text())
    assert decoded["status"] == "failed"
    assert decoded["breakpoint_hit"] is False
    assert decoded["observed_pc"] == "0x2000"
    assert decoded["cleanup_completed"] is True
    assert all(process_is_gone(int(pid)) for pid in pid_file.read_text().split())


def test_probe_gdb_is_the_first_tcp_client(tmp_path: Path) -> None:
    port = free_port()
    out_dir = tmp_path / "out"
    manifest, _runner, fake_gdb = write_fixture(tmp_path, observed_pc=0x1000)
    accepted = tmp_path / "accepted"
    runner = executable(
        tmp_path / "one-client-runner",
        "from pathlib import Path\n"
        "import socket\n"
        "import sys\n"
        "import time\n"
        "with socket.socket() as listener:\n"
        "    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\n"
        "    listener.bind(('127.0.0.1', int(sys.argv[1])))\n"
        "    listener.listen(1)\n"
        "    connection, _ = listener.accept()\n"
        "    connection.close()\n"
        "Path(sys.argv[2]).write_text('accepted')\n"
        "while True:\n"
        "    time.sleep(0.1)\n",
    )
    executable(
        fake_gdb,
        "import socket\n"
        "import sys\n"
        "endpoint = next(\n"
        "    arg.removeprefix('target remote ')\n"
        "    for arg in sys.argv\n"
        "    if arg.startswith('target remote ')\n"
        ")\n"
        "host, raw_port = endpoint.rsplit(':', 1)\n"
        "with socket.create_connection((host, int(raw_port)), timeout=0.2):\n"
        "    pass\n"
        "print('agent_debug_pc=0x1000')\n"
    )

    result = subprocess.run(
        [
            str(SCRIPT),
            "--mode",
            "probe",
            "--target",
            "tf-a",
            "--component",
            "tfa-bl2",
            "--breakpoint",
            "bl2_main",
            "--expected-pc",
            "0x1000",
            "--endpoint",
            f"127.0.0.1:{port}",
            "--manifest",
            str(manifest),
            "--out-dir",
            str(out_dir),
            "--timeout",
            "2",
            "--",
            str(runner),
            str(port),
            str(accepted),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    decoded = json.loads((out_dir / "debug-result.json").read_text())
    assert decoded["status"] == "passed"
    assert decoded["observed_pc"] == "0x1000"
    assert decoded["cleanup_completed"] is True
    assert accepted.read_text() == "accepted"


def test_runner_failure_is_not_reported_as_timeout(tmp_path: Path) -> None:
    port = free_port()
    out_dir = tmp_path / "out"
    manifest, _runner, _ = write_fixture(tmp_path, observed_pc=0x1000)
    failing_runner = executable(tmp_path / "failing-runner", "raise SystemExit(7)\n")

    result = subprocess.run(
        [
            str(SCRIPT),
            "--mode",
            "probe",
            "--target",
            "tf-a",
            "--component",
            "tfa-bl2",
            "--breakpoint",
            "bl2_main",
            "--expected-pc",
            "0x1000",
            "--endpoint",
            f"127.0.0.1:{port}",
            "--manifest",
            str(manifest),
            "--out-dir",
            str(out_dir),
            "--timeout",
            "2",
            "--",
            str(failing_runner),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 4
    decoded = json.loads((out_dir / "debug-result.json").read_text())
    assert decoded["status"] == "failed"
    assert decoded["timed_out"] is False
    assert decoded["runner_returncode"] == 7
    assert decoded["cleanup_completed"] is True


def test_server_ignores_stale_wait_marker(tmp_path: Path) -> None:
    port = free_port()
    out_dir = tmp_path / "out"
    marker = out_dir / "qbox-platform.log"
    marker.parent.mkdir(parents=True)
    marker.write_text("QBox GDB entry breakpoint reached: stale\n")
    pid_file = tmp_path / "runner.pid"
    manifest, _runner, _ = write_fixture(tmp_path, observed_pc=0x1000)
    runner = executable(
        tmp_path / "no-marker-runner",
        "from pathlib import Path\n"
        "import os\n"
        "import socket\n"
        "import sys\n"
        "import time\n"
        "port = int(sys.argv[1])\n"
        "Path(sys.argv[2]).write_text(str(os.getpid()))\n"
        "with socket.socket() as listener:\n"
        "    listener.bind(('127.0.0.1', port))\n"
        "    listener.listen()\n"
        "    while True:\n"
        "        time.sleep(0.1)\n",
    )

    result = subprocess.run(
        [
            str(SCRIPT),
            "--mode",
            "server",
            "--target",
            "tf-a",
            "--component",
            "tfa-bl2",
            "--breakpoint",
            "bl2_main",
            "--expected-pc",
            "0x1000",
            "--endpoint",
            f"127.0.0.1:{port}",
            "--manifest",
            str(manifest),
            "--out-dir",
            str(out_dir),
            "--timeout",
            "0.3",
            "--wait-log",
            str(marker),
            "--wait-marker",
            "QBox GDB entry breakpoint reached:",
            "--",
            str(runner),
            str(port),
            str(pid_file),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 3
    decoded = json.loads((out_dir / "debug-result.json").read_text())
    assert decoded["status"] == "timeout"
    assert decoded["breakpoint_hit"] is False
    assert decoded["cleanup_completed"] is True
    assert not (tmp_path / "gdb.argv").exists()


def test_interrupt_cleans_runner_tree(tmp_path: Path) -> None:
    port = free_port()
    out_dir = tmp_path / "out"
    pid_file = tmp_path / "runner.pid"
    manifest, runner, _ = write_fixture(tmp_path, observed_pc=0x1000)
    process = subprocess.Popen(
        [
            str(SCRIPT),
            "--mode",
            "probe",
            "--target",
            "tf-a",
            "--component",
            "tfa-bl2",
            "--breakpoint",
            "bl2_main",
            "--expected-pc",
            "0x1000",
            "--endpoint",
            f"127.0.0.1:{port}",
            "--manifest",
            str(manifest),
            "--out-dir",
            str(out_dir),
            "--timeout",
            "60",
            "--wait-log",
            str(out_dir / "qbox-platform.log"),
            "--wait-marker",
            "marker-that-will-not-match",
            "--",
            str(runner),
            str(port),
            str(out_dir / "qbox-platform.log"),
            str(pid_file),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    deadline = time.monotonic() + 2
    while not pid_file.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    assert pid_file.exists()

    process.send_signal(signal.SIGINT)
    process.communicate(timeout=5)

    assert process.returncode != 0
    assert all(process_is_gone(int(pid)) for pid in pid_file.read_text().split())
