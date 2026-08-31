from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import time
from typing import Final

try:
    import gic720ae_pcie_irq_validation_ap_map as ap_map
    import qbox_apollo_pcie_irq_task9 as task9
    import qbox_apollo_pcie_irq_task9_cleanup as task9_cleanup
    from qbox_apollo_pcie_irq_task9_result import ModeResult
except ModuleNotFoundError:
    from scripts.test import gic720ae_pcie_irq_validation_ap_map as ap_map
    from scripts.test import qbox_apollo_pcie_irq_task9 as task9
    from scripts.test import qbox_apollo_pcie_irq_task9_cleanup as task9_cleanup
    from scripts.test.qbox_apollo_pcie_irq_task9_result import ModeResult


GUEST: Final = task9.ROOT / "scripts/test/apollo_qbox_pcie_irq_task9_guest.sh"
PAIR_VALIDATOR: Final = (
    task9.ROOT / "scripts/test/validate_qbox_apollo_pcie_irq_runtime.py"
)
SPI_VALIDATOR: Final = task9.ROOT / "scripts/test/validate_qbox_apollo_pcie_irq_spi.py"
COVERAGE_AUDIT: Final = (
    task9.ROOT / "scripts/test/audit_qbox_apollo_fvp_full_coverage.py"
)
EVIDENCE_ROOT: Final = task9.ROOT / ".omo/evidence/apollo-gic-its/task-9"


@dataclass(frozen=True, slots=True)
class ValidatorInputs:
    run_root: Path
    pins: task9.PinClosure
    profile: Path
    ap_map_artifact: ap_map.ApMapArtifact


def terminate_process_group(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=10)


def wait_and_inject(
    process: subprocess.Popen[bytes],
    out_dir: Path,
    guest: bytes,
    arguments: tuple[str, str, str],
) -> None:
    deadline = time.monotonic() + 840
    fifo = out_dir / "primary-uart-input.fifo"
    primary = out_dir / "qbox-primary-console.log"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise task9.Task9Error("runner_exited_before_injection")
        if fifo.exists() and stat.S_ISFIFO(fifo.stat().st_mode) and primary.exists():
            text = primary.read_text(encoding="utf-8", errors="replace")
            if "nexios-bsp#" in text:
                task9.inject_fifo_paused(process.pid, fifo, guest, arguments)
                return
        time.sleep(0.05)
    raise task9.Task9Error("guest_injection_timeout")


def validate_runner_result(path: Path, expected: task9.ModeInput) -> None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise task9.Task9Error("runner_result") from error
    if not isinstance(payload, dict):
        raise task9.Task9Error("runner_result")
    gates = payload.get("completion_gates")
    artifacts = payload.get("input_artifacts")
    if not isinstance(gates, dict) or not isinstance(artifacts, dict):
        raise task9.Task9Error("runner_result")
    rootfs = artifacts.get("rootfs")
    if not isinstance(rootfs, dict) or not isinstance(rootfs.get("path"), str):
        raise task9.Task9Error("runner_rootfs")
    if (
        payload.get("passed") is not True
        or payload.get("verdict") != "pass"
        or payload.get("child_returncode") != 0
        or gates != {"G0": "pass", "G1": "pass", "G2": "pass"}
    ):
        raise task9.Task9Error("runner_result")
    actual = Path(rootfs["path"])
    if (
        actual.resolve() != expected.disk.resolve()
        or task9.sha256(actual) != expected.disk_sha256
    ):
        raise task9.Task9Error("runner_rootfs_sha256")


def run_mode(
    run_root: Path,
    mode: str,
    expected: task9.ModeInput,
    pins: task9.PinClosure,
) -> ModeResult:
    out_dir = run_root / mode
    out_dir.mkdir()
    command = task9.canonical_command(
        mode, expected.disk.relative_to(task9.ROOT), out_dir
    )
    environment = os.environ.copy()
    environment["QBOX_APOLLO_NUM_CPUS"] = "4"
    environment["QBOX_APOLLO_PCIE_IRQ_TEST"] = "true"
    environment["QBOX_RDASPEN_NETDEV"] = "type=user"
    process: subprocess.Popen[bytes] | None = None
    with (run_root / f"{mode}-runner-host.log").open("wb") as stream:
        try:
            process = subprocess.Popen(
                command,
                cwd=task9.ROOT,
                env=environment,
                stdout=stream,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            pid = process.pid
            pgid = pid
            task9_cleanup.write_registry(out_dir, pid, pgid)
            wait_and_inject(
                process,
                out_dir,
                GUEST.read_bytes(),
                (mode, expected.input_sha256, pins.guest_probe_sha256),
            )
            runner_rc = process.wait(timeout=900)
        finally:
            if process is not None:
                terminate_process_group(process)
            task9_cleanup.terminate_task_owned(out_dir)
            task9.cleanup_uart_fifo(out_dir)
            if process is not None:
                task9_cleanup.write_cleanup(out_dir, process.pid, process.pid)
    if runner_rc != 0:
        raise task9.Task9Error(f"runner_rc:{mode}:{runner_rc}")
    primary = out_dir / "qbox-primary-console.log"
    if "__APOLLO_TASK9_RC__0" not in primary.read_text(
        encoding="utf-8", errors="replace"
    ):
        raise task9.Task9Error(f"guest_rc:{mode}")
    validate_runner_result(out_dir / "result.json", expected)
    task9.validate_mode_extras(primary, mode, pins.guest_probe_sha256)
    fifo_cleaned = not (out_dir / "primary-uart-input.fifo").exists()
    if not fifo_cleaned:
        raise task9.Task9Error(f"fifo_cleanup:{mode}")
    return ModeResult(
        command,
        pid,
        pgid,
        task9.sha256(expected.disk),
        task9.sha256(primary),
        task9.sha256(out_dir / "result.json"),
    )


def run_checked(command: list[str], log: Path) -> None:
    result = subprocess.run(
        command,
        cwd=task9.ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise task9.Task9Error(
            f"validator_rc:{Path(command[1]).name}:{result.returncode}"
        )


def run_validators(inputs: ValidatorInputs) -> None:
    run_root = inputs.run_root
    pins = inputs.pins
    profile = inputs.profile
    ap_map.require_current(
        inputs.ap_map_artifact,
        inputs.ap_map_artifact.path.parent,
        "task9_ap_map",
    )
    msix_log = run_root / "msix/qbox-primary-console.log"
    intx_log = run_root / "intx/qbox-primary-console.log"
    run_checked(
        [
            sys.executable,
            str(PAIR_VALIDATOR.relative_to(task9.ROOT)),
            "--profile-manifest",
            str(profile.relative_to(task9.ROOT)),
            "--msix-log",
            str(msix_log),
            "--intx-log",
            str(intx_log),
            "--output",
            str(run_root / "pcie-runtime-validation.json"),
        ],
        run_root / "pcie-runtime-validator.log",
    )
    run_checked(
        [
            sys.executable,
            str(SPI_VALIDATOR.relative_to(task9.ROOT)),
            "--log",
            str(msix_log),
            "--input-sha256",
            pins.msix.input_sha256,
            "--output",
            str(run_root / "spi-runtime-validation.json"),
        ],
        run_root / "spi-runtime-validator.log",
    )
    for mode in ("msix", "intx"):
        run_checked(
            [
                sys.executable,
                str(COVERAGE_AUDIT.relative_to(task9.ROOT)),
                "--result-json",
                str(run_root / mode / "result.json"),
                "--ap-map-audit",
                str(inputs.ap_map_artifact.path),
                "--output",
                str(run_root / f"{mode}-coverage-audit.json"),
            ],
            run_root / f"{mode}-coverage-audit.log",
        )
        ap_map.validate_coverage(
            run_root / f"{mode}-coverage-audit.json", inputs.ap_map_artifact
        )


def residual_processes(run_root: Path) -> list[int]:
    needle = str(run_root).encode()
    current_uid = os.getuid()
    matches: list[int] = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit() or int(entry.name) == os.getpid():
            continue
        try:
            if (
                entry.stat().st_uid == current_uid
                and needle in (entry / "cmdline").read_bytes()
            ):
                matches.append(int(entry.name))
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
    return matches
