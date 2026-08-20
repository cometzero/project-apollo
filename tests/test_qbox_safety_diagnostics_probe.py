from __future__ import annotations

import json
from pathlib import Path

from scripts.run import run_qbox_apollo_fvp_full as full_runner
from qbox_safety_diagnostics_probe import (
    evaluate_safety_diagnostics,
    safety_diagnostics_commands,
)


def diagnostic_log(
    name: str,
    *,
    total: int,
    failures: int = 0,
    ignored: int = 0,
) -> str:
    status = "OK" if failures == 0 and ignored == 0 else "FAIL"
    return "\n".join(
        [
            f"[INTEGRATION_TEST] Start: {name}",
            f"{name}.c:10:test_{name}:"
            f"{'PASS' if status == 'OK' else 'FAIL'}",
            f"{total} Tests {failures} Failures {ignored} Ignored",
            status,
            f"[INTEGRATION_TEST] End: {name}",
        ]
    )


def test_safety_diagnostics_commands_match_fvp_order() -> None:
    # Given/When: the fixed QBox Safety Island diagnostic sequence is built.
    commands = safety_diagnostics_commands()

    # Then: SSU completes before the larger FMU integration suite starts.
    assert commands == ["test ssu", "test fmu"]


def test_safety_diagnostics_accepts_complete_console() -> None:
    # Given: complete zero-failure SSU and FMU Unity output.
    console = "\n".join(
        [
            diagnostic_log("ssu", total=1),
            diagnostic_log("fmu", total=20),
        ]
    )

    # When: the cross-suite diagnostics result is evaluated.
    result = evaluate_safety_diagnostics(console)

    # Then: both FVP-equivalent suites and the aggregate verdict pass.
    assert result["passed"] is True
    assert result["failed_checks"] == []
    assert result["diagnostics"]["ssu"]["passed"] == 1
    assert result["diagnostics"]["fmu"]["passed"] == 20


def test_safety_diagnostics_rejects_ignored_case() -> None:
    # Given: SSU passes while the FMU suite reports an ignored case.
    console = "\n".join(
        [
            diagnostic_log("ssu", total=1),
            diagnostic_log("fmu", total=20, ignored=1),
        ]
    )

    # When: the diagnostics result is evaluated.
    result = evaluate_safety_diagnostics(console)

    # Then: the aggregate result retains the failing FMU boundary.
    assert result["passed"] is False
    assert result["failed_checks"] == ["fmu"]


def test_full_runner_expands_safety_diagnostics_probe() -> None:
    # Given/When: the full-system runner parses the diagnostics selector.
    args = full_runner.parse_args(["--safety-diagnostics-probe"])

    # Then: the selector owns the exact SI0 command sequence.
    assert args.safety_diagnostics_probe is True
    assert args.si_cl0_command == ["test ssu", "test fmu"]


def test_full_runner_rejects_failed_safety_diagnostics(
    tmp_path: Path,
) -> None:
    # Given: a boot-success result whose SI0 log contains an FMU failure.
    args = full_runner.parse_args(
        [
            "--out-dir",
            str(tmp_path),
            "--safety-diagnostics-probe",
        ]
    )
    (tmp_path / "qbox-safety-island-cl0.log").write_text(
        "\n".join(
            [
                diagnostic_log("ssu", total=1),
                diagnostic_log("fmu", total=20, failures=1),
            ]
        ),
        encoding="utf-8",
    )

    # When: the canonical full-system result is written.
    returncode = full_runner.write_result(
        args,
        {},
        command=[],
        child_status={"passed": True},
        child_returncode=0,
        blocker=None,
        check_only=False,
    )

    # Then: diagnostics failure overrides the child boot verdict.
    result = json.loads((tmp_path / "result.json").read_text())
    assert returncode == 1
    assert result["passed"] is False
    assert result["blocker"] == "safety_diagnostics_failed:fmu"
