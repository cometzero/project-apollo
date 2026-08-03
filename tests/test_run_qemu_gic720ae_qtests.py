from __future__ import annotations

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/build/run_qemu_gic720ae_qtests.sh"


def test_list_reports_supported_qtest_deterministically() -> None:
    # Given: the repository-local QEMU GIC qtest runner.
    command = [str(RUNNER), "--list"]

    # When: its supported tests are listed twice.
    first = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    second = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: both invocations return the same ordered candidate set.
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert first.stdout == (
            "arm-gicv3-baseline\n"
            "arm-gicv3-ext-range-cpuif\n"
            "arm-gicv3-ext-range-gpio-delivery\n"
            "arm-gicv3-eppi\n"
            "arm-gicv3-espi\n"
            "arm-gicv3-ext-range-gpio-abi\n"
            "arm-gicv3-ext-range-vmstate\n"
            "arm-gicv4-1-vpendbaser\n"
            "arm-gicv4-1-its-vpe\n"
            "arm-gicv4-1-direct-lpi\n"
        )
    assert second.stdout == first.stdout


def test_unsupported_qtest_exits_two_with_candidate_list() -> None:
    # Given: a test name outside the runner's allowlist.
    unsupported = "arm-gicv3-unknown"

    # When: the runner is asked to execute it.
    result = subprocess.run(
        [str(RUNNER), "--test", unsupported],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: input parsing fails with exit 2 and the valid candidates.
    assert result.returncode == 2
    assert "arm-gicv3-baseline" in result.stderr
    assert "arm-gicv4-1-vpendbaser" in result.stderr
    assert "arm-gicv4-1-its-vpe" in result.stderr


def test_repeated_selector_is_rejected_with_actionable_diagnostic() -> None:
    result = subprocess.run(
        [str(RUNNER), "--test", "arm-gicv3-baseline", "--test", "arm-gicv3-baseline"],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 2
    assert "duplicate test: arm-gicv3-baseline" in result.stderr


def test_missing_test_name_is_rejected() -> None:
    result = subprocess.run(
        [str(RUNNER), "--test"],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 2
    assert "missing test name after --test" in result.stderr


def test_no_test_selector_is_rejected() -> None:
    # Given: the runner with no selection arguments.
    command = [str(RUNNER)]

    # When: it is invoked without --test.
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: it fails closed instead of selecting an implicit qtest set.
    assert result.returncode == 2
    assert "Usage:" in result.stderr


def test_test_name_is_not_evaluated_as_shell_code(tmp_path: Path) -> None:
    # Given: an unsupported name containing shell command syntax.
    marker = tmp_path / "injected"
    unsupported = f"$(touch {marker})"

    # When: the name crosses the runner's CLI boundary.
    result = subprocess.run(
        [str(RUNNER), "--test", unsupported],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Then: it is rejected as data and no command is executed.
    assert result.returncode == 2
    assert not marker.exists()
