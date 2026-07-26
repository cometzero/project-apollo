from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/debug/run_local_gdb.py"


def load_runner_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("run_local_gdb", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_build_remote_gdb_command() -> None:
    module = load_runner_module()
    component = module.DebugComponent(
        name="linux",
        domain="u_boot_linux",
        debugger="gdb-multiarch",
        elf=Path("/tmp/vmlinux"),
        gdb_script=Path("/tmp/linux.gdb"),
    )

    command = module.build_gdb_command(
        component,
        batch=True,
        remote="localhost:12341",
        breakpoints=("start_kernel",),
        resume=True,
    )

    assert command == [
        "gdb-multiarch",
        "-q",
        "--batch",
        "-x",
        "/tmp/linux.gdb",
        "-ex",
        "break start_kernel",
        "-ex",
        "target remote localhost:12341",
        "-ex",
        "continue",
    ]


def test_build_remote_command_waits_for_boot_marker_after_loading_symbols() -> None:
    module = load_runner_module()
    component = module.DebugComponent(
        name="linux",
        domain="u_boot_linux",
        debugger="gdb-multiarch",
        elf=Path("/tmp/vmlinux"),
        gdb_script=Path("/tmp/linux.gdb"),
    )

    command = module.build_gdb_command(
        component,
        remote="localhost:12343",
        wait_log_marker=(
            Path("/tmp/qbox-rse.log"),
            "SCP ready. Power domain protocol version",
            600.0,
        ),
        resume=True,
    )

    script_index = command.index("/tmp/linux.gdb")
    wait_index = next(
        index
        for index, value in enumerate(command)
        if value.startswith("shell ") and "--wait-log-marker-only" in value
    )
    remote_index = command.index("target remote localhost:12343")

    assert script_index < wait_index < remote_index
    assert "SCP ready. Power domain protocol version" in command[wait_index]


def test_build_host_attach_command() -> None:
    module = load_runner_module()
    component = module.DebugComponent(
        name="qbox-host",
        domain="qbox",
        debugger="gdb",
        elf=Path("/tmp/platforms-vp"),
        gdb_script=Path("/tmp/qbox-host.gdb"),
    )

    command = module.build_gdb_command(component, attach_pid=4242)

    assert command == [
        "gdb",
        "-q",
        "-x",
        "/tmp/qbox-host.gdb",
        "-p",
        "4242",
    ]


def test_build_host_remote_loads_symbols_before_connect() -> None:
    module = load_runner_module()
    component = module.DebugComponent(
        name="qbox-host",
        domain="qbox",
        debugger="gdb",
        elf=Path("/tmp/platforms-vp"),
        gdb_script=Path("/tmp/qbox-host.gdb"),
    )

    command = module.build_gdb_command(component, remote="localhost:12339")

    assert command.index("/tmp/qbox-host.gdb") < command.index(
        "target remote localhost:12339"
    )


def test_wait_for_remote_detects_listening_socket() -> None:
    import socket

    module = load_runner_module()
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]

        assert module.wait_for_remote(
            f"127.0.0.1:{port}", timeout=0.5, interval=0.01
        )


def test_wait_for_log_marker_detects_existing_marker(tmp_path: Path) -> None:
    module = load_runner_module()
    log = tmp_path / "secure.log"
    log.write_text("PFDI: OoR tests on core 3 succeeded.\n")

    assert module.wait_for_log_marker(
        log,
        "PFDI: OoR tests on core 3 succeeded.",
        timeout=0.1,
        interval=0.01,
    )

    result = subprocess.run(
        [
            str(SCRIPT),
            "--wait-log-marker-only",
            str(log),
            "PFDI: OoR tests on core 3 succeeded.",
            "--wait-seconds",
            "0.1",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Waiting for GDB attach marker" in result.stdout
    assert "GDB attach marker found" in result.stdout


def test_interrupt_keeps_debugger_process_alive(tmp_path: Path) -> None:
    fake_debugger = tmp_path / "fake-gdb"
    fake_debugger.write_text(
        "#!/usr/bin/env python3\n"
        "import signal\n"
        "signal.signal(signal.SIGINT, lambda *_: print('INT', flush=True))\n"
        "print('READY', flush=True)\n"
        "while True:\n"
        "    signal.pause()\n"
    )
    fake_debugger.chmod(0o755)
    gdb_script = tmp_path / "fake.gdb"
    gdb_script.write_text("")
    manifest = tmp_path / "symbols.json"
    manifest.write_text(
        json.dumps(
            {
                "components": {
                    "fake": {
                        "domain": "qbox",
                        "debugger": str(fake_debugger),
                        "elf": str(tmp_path / "fake.elf"),
                        "gdb_script": str(gdb_script),
                    }
                }
            }
        )
    )

    process = subprocess.Popen(
        [str(SCRIPT), "--manifest", str(manifest), "fake"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    assert process.stdout is not None
    assert process.stdout.readline() == "READY\n"

    os.killpg(process.pid, signal.SIGINT)
    try:
        process.wait(timeout=0.5)
    except subprocess.TimeoutExpired:
        is_alive = True
    else:
        is_alive = False
    finally:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            assert process.poll() is not None
        process.wait(timeout=1)

    assert is_alive
