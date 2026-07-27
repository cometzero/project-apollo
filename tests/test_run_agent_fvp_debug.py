from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/debug/run_agent_fvp_debug.py"


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def executable(path: Path, body: str) -> Path:
    path.write_text("#!/usr/bin/env python3\n" + body, encoding="utf-8")
    path.chmod(0o755)
    return path


def process_is_gone(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    return False


def test_probe_uses_iris_then_collects_gdb_snapshot(tmp_path: Path) -> None:
    port = free_port()
    out_dir = tmp_path / "out"
    pid_file = tmp_path / "runner.pid"
    invocation_log = tmp_path / "invocations.log"
    runner = executable(
        tmp_path / "fake-runner",
        "import os\n"
        "from pathlib import Path\n"
        "import socket\n"
        "import sys\n"
        "import time\n"
        "port = int(sys.argv[1])\n"
        "Path(sys.argv[2]).write_text(str(os.getpid()))\n"
        "with socket.socket() as listener:\n"
        "    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\n"
        "    listener.bind(('127.0.0.1', port))\n"
        "    listener.listen()\n"
        "    while True:\n"
        "        time.sleep(0.1)\n",
    )
    iris_helper = executable(
        tmp_path / "fake-iris",
        "from pathlib import Path\n"
        f"Path({str(invocation_log)!r}).write_text('iris ' + ' '.join(__import__('sys').argv[1:]) + '\\n')\n"
        "print('breakpoint_hit component=tfa-bl2 symbol=bl2_main address=0x1000 target=cpu0 id=1')\n",
    )
    cornea = executable(
        tmp_path / "fake-cornea",
        "from pathlib import Path\n"
        "import sys\n"
        f"path = Path({str(invocation_log)!r})\n"
        "path.write_text(path.read_text() + 'cornea ' + ' '.join(sys.argv[1:]) + '\\n')\n",
    )
    fake_gdb = executable(
        tmp_path / "fake-gdb",
        "print('agent_debug_pc=0x1000')\n"
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
                    }
                }
            }
        ),
        encoding="utf-8",
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
            "--iris-instance",
            "component.cpu0",
            "--iris-port",
            str(port),
            "--manifest",
            str(manifest),
            "--cornea",
            str(cornea),
            "--iris-helper",
            str(iris_helper),
            "--out-dir",
            str(out_dir),
            "--timeout",
            "2",
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

    assert result.returncode == 0, result.stderr
    decoded = json.loads((out_dir / "debug-result.json").read_text())
    assert decoded["backend"] == "fvp-iris"
    assert decoded["status"] == "passed"
    assert decoded["breakpoint_hit"] is True
    assert decoded["observed_pc"] == "0x1000"
    assert decoded["cleanup_completed"] is True
    assert "breakpoint_hit component=tfa-bl2" in (
        out_dir / "iris-probe.log"
    ).read_text()
    assert "bl2_main at bl2_main.c:44" in (out_dir / "gdb.log").read_text()
    invocations = invocation_log.read_text().splitlines()
    assert invocations[0].startswith("iris --port")
    assert "register-read component.cpu0 PC" in invocations[1]
    assert process_is_gone(int(pid_file.read_text()))
