from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUALIFIER = ROOT / "scripts/test/run_qbox_apollo_pcie_irq_task9.py"
PROFILE = (
    ROOT / ".omo/evidence/apollo-gic-its/task-8/remediation-3/profile/manifest.json"
)
GATE = (
    ROOT
    / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current"
    / "fvp-reference-gate-current.json"
)
TASK9_MODULE = ROOT / "scripts/test/qbox_apollo_pcie_irq_task9.py"
PROCESS_MODULE = ROOT / "scripts/test/qbox_apollo_pcie_irq_task9_process.py"
CLEANUP_MODULE = ROOT / "scripts/test/qbox_apollo_pcie_irq_task9_cleanup.py"
GUEST = ROOT / "scripts/test/apollo_qbox_pcie_irq_task9_guest.sh"


def load_task9_module():
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location("task9_runtime", TASK9_MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_process_module():
    sys.path.insert(0, str(ROOT / "scripts/test"))
    spec = importlib.util.spec_from_file_location("task9_process", PROCESS_MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_cleanup_module():
    spec = importlib.util.spec_from_file_location("task9_cleanup", CLEANUP_MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_cli_fails_before_qbox_when_reference_gate_is_copied(
    tmp_path: Path,
) -> None:
    copied_gate = tmp_path / "copied-gate.json"
    copied_gate.write_bytes(GATE.read_bytes())
    run_root = tmp_path / "run"

    result = subprocess.run(
        [
            sys.executable,
            str(QUALIFIER),
            "--fvp-reference-gate",
            str(copied_gate),
            "--profile-manifest",
            str(PROFILE),
            "--run-root",
            str(run_root),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "fvp_reference_gate_path" in result.stderr
    assert not (run_root / "msix").exists()
    assert not (run_root / "intx").exists()


def test_fifo_injection_crosses_a_real_shell_process_boundary(
    tmp_path: Path,
) -> None:
    task9 = load_task9_module()
    fifo = tmp_path / "input.fifo"
    fifo.parent.mkdir(parents=True, exist_ok=True)
    fifo.touch()
    fifo.unlink()
    subprocess.run(["mkfifo", str(fifo)], check=True)
    output = tmp_path / "observed.txt"
    consumer = subprocess.Popen(
        [
            "/bin/sh",
            "-c",
            'IFS= read -r command < "$1"; eval "$command"',
            "task9-consumer",
            str(fifo),
        ],
        cwd=ROOT,
    )
    guest = b'#!/bin/sh\nprintf %s "$1" > "$2"\n'

    task9.inject_fifo(fifo, guest, ("process-boundary", str(output)))
    assert consumer.wait(timeout=5) == 0
    assert output.read_text(encoding="utf-8") == "process-boundary"


def test_chunked_fifo_injection_crosses_a_real_shell_process_boundary(
    tmp_path: Path,
) -> None:
    task9 = load_task9_module()
    fifo = tmp_path / "stream.fifo"
    subprocess.run(["mkfifo", str(fifo)], check=True)
    output = tmp_path / "stream-observed.txt"
    holding = os.open(fifo, os.O_RDWR | os.O_NONBLOCK)
    reader = os.open(fifo, os.O_RDONLY)
    consumer = subprocess.Popen(["/bin/sh"], stdin=reader, cwd=ROOT)
    os.close(reader)
    guest = b'#!/bin/sh\nprintf %s "$1" > "$2"\n'
    task9.inject_fifo_stream(fifo, guest, ("chunked-boundary", str(output)))
    os.close(holding)
    assert consumer.wait(timeout=5) == 0
    assert output.read_text(encoding="utf-8") == "chunked-boundary"


def test_real_guest_payload_fits_one_atomic_fifo_write() -> None:
    task9 = load_task9_module()
    commands = task9.injection_commands(
        GUEST.read_bytes(),
        ("msix", "9" * 64, "8" * 64),
    )
    assert max(map(len, commands)) <= 4096
    assert all(command.endswith(b"\n") for command in commands)


def test_canonical_mode_command_preserves_requested_runner_contract(
    tmp_path: Path,
) -> None:
    task9 = load_task9_module()
    rootfs = tmp_path / "msix.img"
    out_dir = tmp_path / "msix"
    command = task9.canonical_command("msix", rootfs, out_dir)
    assert command == [
        "./run_qbox_yocto.sh",
        "--headless",
        "--keep-running-after-pass",
        "--timeout",
        "900",
        "--rootfs",
        str(rootfs),
        "--rootfs-bootargs-profile",
        "none",
        "--out-dir",
        str(out_dir),
    ]


def test_raw_intx_gate_requires_empty_msi_irqs(tmp_path: Path) -> None:
    task9 = load_task9_module()
    log = tmp_path / "intx.log"
    log.write_text(
        "APOLLO_IRQ|v=1|event=msi_state|count=1|path=/sys/bus/pci/devices/0000:00:01.0/msi_irqs\n",
        encoding="utf-8",
    )
    try:
        task9.validate_mode_extras(log, "intx", "8" * 64)
    except task9.Task9Error as error:
        assert str(error) == "intx_msi_irqs"
    else:
        raise AssertionError("non-empty INTx msi_irqs accepted")


def test_embedded_probe_rejects_stale_timeout_contract(tmp_path: Path) -> None:
    task9 = load_task9_module()
    log = tmp_path / "msix.log"
    log.write_text(
        "\n".join(
            [
                "APOLLO_IRQ|v=1|event=msi_state|count=1|path=/sys/bus/pci/devices/0000:00:01.0/msi_irqs",
                "APOLLO_IRQ|v=1|event=embedded_probe|path=/usr/bin/apollo-pcie-its-guest|sha256="
                + "8" * 64
                + "|busybox_timeout_rc=0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    try:
        task9.validate_mode_extras(log, "msix", "8" * 64)
    except task9.Task9Error as error:
        assert str(error) == "embedded_probe"
    else:
        raise AssertionError("stale timeout contract accepted")


def test_signal_handler_converts_term_into_cleanup_unwind() -> None:
    task9 = load_task9_module()
    try:
        task9.signal_handler(15, None)
    except task9.Task9Signal as error:
        assert error.signum == 15
    else:
        raise AssertionError("TERM did not unwind through cleanup")


def test_interrupted_mode_cleanup_removes_uart_fifo(tmp_path: Path) -> None:
    task9 = load_task9_module()
    out_dir = tmp_path / "msix"
    out_dir.mkdir()
    fifo = out_dir / "primary-uart-input.fifo"
    subprocess.run(["mkfifo", str(fifo)], check=True)
    task9.cleanup_uart_fifo(out_dir)
    assert not fifo.exists()


def test_cleanup_terminates_escaped_descendant_with_run_root_fd(
    tmp_path: Path,
) -> None:
    task9_cleanup = load_cleanup_module()
    out_dir = tmp_path / "msix"
    out_dir.mkdir()
    owned = out_dir / "qbox-platform.log"
    owned.write_bytes(b"task9")
    descendant = subprocess.Popen(
        [
            "/bin/bash",
            "-c",
            'exec 9<"$1"; echo ready; exec -a platforms-vp tail -f /dev/null',
            "task9-qbox-descendant",
            str(owned),
        ],
        start_new_session=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    assert descendant.stdout is not None
    assert descendant.stdout.readline() == "ready\n"
    assert descendant.pid in task9_cleanup.task_owned_processes(out_dir)
    task9_cleanup.terminate_task_owned(out_dir)
    assert descendant.wait(timeout=5) != 0
    assert task9_cleanup.task_owned_processes(out_dir) == []


def test_cleanup_ignores_unrelated_fd_holder_under_run_root(
    tmp_path: Path,
) -> None:
    task9_cleanup = load_cleanup_module()
    out_dir = tmp_path / "msix"
    out_dir.mkdir()
    owned = out_dir / "owned.raw"
    owned.write_bytes(b"task9")
    unrelated = subprocess.Popen(
        [
            "/bin/bash",
            "-c",
            'exec 9<"$1"; echo ready; exec -a unrelated-holder tail -f /dev/null',
            "unrelated-holder",
            str(owned),
        ],
        start_new_session=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    assert unrelated.stdout is not None
    try:
        assert unrelated.stdout.readline() == "ready\n"
        assert unrelated.pid not in task9_cleanup.task_owned_processes(out_dir)
        task9_cleanup.terminate_task_owned(out_dir)
        assert unrelated.poll() is None
    finally:
        if unrelated.poll() is None:
            unrelated.terminate()
            try:
                unrelated.wait(timeout=5)
            except subprocess.TimeoutExpired:
                unrelated.kill()
                unrelated.wait(timeout=5)
