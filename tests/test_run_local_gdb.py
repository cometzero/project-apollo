from __future__ import annotations

import importlib.util
from pathlib import Path
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
    )

    assert command == [
        "gdb-multiarch",
        "-q",
        "--batch",
        "-x",
        "/tmp/linux.gdb",
        "-ex",
        "target remote localhost:12341",
        "-ex",
        "break start_kernel",
    ]


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
