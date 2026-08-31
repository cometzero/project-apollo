from __future__ import annotations

import os
from pathlib import Path
import signal
import sys
from types import FrameType

import pytest

from scripts.test import gic720ae_pcie_irq_validation_contract as contract
from scripts.test import gic720ae_pcie_irq_validation_workflow as workflow


def assert_reaped(registry: Path, expected_reason: str) -> None:
    receipt = contract.load_object(registry, "test_process_registry")
    pid = receipt.get("pid")
    assert isinstance(pid, int)
    assert receipt["status"] == "TERMINATED"
    assert receipt["reason"] == expected_reason
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)


def test_timed_out_child_is_reaped_and_registry_records_termination(
    tmp_path: Path,
) -> None:
    # Given: a registered child that cannot complete inside its bounded timeout.
    registry = tmp_path / "audit-process.json"
    log = tmp_path / "audit.log"

    # When: the shared child boundary reaches its timeout.
    with pytest.raises(contract.ValidationError, match="child_timeout"):
        workflow.run_child(
            (sys.executable, "-c", "import time; time.sleep(60)"),
            log,
            1,
            registry,
        )

    # Then: the process group is gone and the registry cannot imply it is live.
    assert_reaped(registry, "timeout")


@pytest.mark.parametrize("attempt", (1, 2))
def test_interrupted_child_is_reaped_on_repeated_attempts(
    tmp_path: Path,
    attempt: int,
) -> None:
    # Given: the CLI's typed interruption seam is armed during a live child.
    registry = tmp_path / f"interrupt-{attempt}.json"
    log = tmp_path / f"interrupt-{attempt}.log"

    def interrupt(_signum: int, _frame: FrameType | None) -> None:
        raise contract.ValidationError(f"interrupted:{attempt}")

    previous = signal.signal(signal.SIGALRM, interrupt)
    signal.setitimer(signal.ITIMER_REAL, 0.1)
    try:
        # When: one supported alarm interruption reaches the child boundary.
        with pytest.raises(contract.ValidationError, match="interrupted"):
            workflow.run_child(
                (sys.executable, "-c", "import time; time.sleep(60)"),
                log,
                10,
                registry,
            )
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)

    # Then: each independent interruption leaves a terminated receipt.
    assert_reaped(registry, "interrupted")


def test_child_boundary_recovers_after_interruption(tmp_path: Path) -> None:
    # Given: a clean registry after prior interruption scenarios.
    registry = tmp_path / "recovery.json"
    log = tmp_path / "recovery.log"

    # When: a new child completes normally through the same boundary.
    result = workflow.run_child(
        (sys.executable, "-c", "raise SystemExit(0)"), log, 10, registry
    )

    # Then: recovery is unambiguously EXITED and successful.
    receipt = contract.load_object(registry, "test_recovery_registry")
    assert result.returncode == 0
    assert receipt["status"] == "EXITED"
    assert receipt["returncode"] == 0
