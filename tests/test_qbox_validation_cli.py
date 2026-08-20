from __future__ import annotations

import pytest

from scripts.run import run_qbox_apollo_fvp_full as full_runner
from scripts.run.qbox_validation.result import evaluate_profile_result
from scripts.run.qbox_validation.registry import (
    canonical_matrix_path,
    resolve_profile,
)
from scripts.run.qbox_validation.types import ConsoleSnapshot


@pytest.mark.parametrize(
    ("profile_id", "legacy_flag"),
    (
        ("pfdi", "--pfdi-probe"),
        ("pfdi-si-cl1", "--pfdi-si-cl1-probe"),
        ("ras_cpu", "--ras-cpu-probe"),
        ("safety-diagnostics-tests", "--safety-diagnostics-probe"),
    ),
)
def test_canonical_profile_preserves_legacy_child_adapter(
    profile_id: str,
    legacy_flag: str,
) -> None:
    # Given: a canonical repository-owned profile selection.
    args = full_runner.parse_args(["--validation-profile", profile_id])
    artifacts = full_runner.resolved_artifacts(args)

    # When: the private runtime-child command is constructed.
    command = full_runner.child_command(args, artifacts)

    # Then: canonical metadata and the existing behavior adapter are both kept.
    if profile_id != "safety-diagnostics-tests":
        assert command[command.index("--validation-profile") + 1] == profile_id
        assert legacy_flag in command
    else:
        assert "--validation-profile" not in command
        assert args.si_cl0_command == ["test ssu", "test fmu"]


@pytest.mark.parametrize(
    ("legacy_flag", "profile_id"),
    (
        ("--pfdi-probe", "pfdi"),
        ("--pfdi-si-cl1-probe", "pfdi-si-cl1"),
        ("--ras-cpu-probe", "ras_cpu"),
        ("--safety-diagnostics-probe", "safety-diagnostics-tests"),
    ),
)
def test_legacy_adapter_selects_same_canonical_profile(
    legacy_flag: str,
    profile_id: str,
) -> None:
    # Given: one of the original public probe flags.
    # When: arguments are parsed through the registry adapter.
    args = full_runner.parse_args([legacy_flag])

    # Then: results use the canonical profile ID without changing behavior.
    assert args.validation_profile == profile_id


def test_unknown_profile_and_conflicting_adapter_reject_before_runtime(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Given: invalid selections at the CLI trust boundary.
    # When/Then: both exit through argparse before artifact or process work.
    with pytest.raises(SystemExit) as unknown:
        full_runner.parse_args(["--validation-profile", "unknown"])
    assert unknown.value.code == 2
    assert "unknown_validation_profile:unknown" in capsys.readouterr().err

    with pytest.raises(SystemExit) as conflict:
        full_runner.parse_args(
            ["--validation-profile", "pfdi", "--ras-cpu-probe"]
        )
    assert conflict.value.code == 2
    assert "conflicting_validation_profile_adapters" in capsys.readouterr().err


def test_safety_diagnostics_normalizes_to_task1_result_schema() -> None:
    # Given: complete non-empty SI0 Unity diagnostics output.
    spec = resolve_profile(
        "safety-diagnostics-tests",
        canonical_matrix_path(),
    )
    console = "\n".join(
        (
            "[INTEGRATION_TEST] Start: ssu",
            "1 Tests 0 Failures 0 Ignored",
            "OK",
            "[INTEGRATION_TEST] End: ssu",
            "[INTEGRATION_TEST] Start: fmu",
            "20 Tests 0 Failures 0 Ignored",
            "OK",
            "[INTEGRATION_TEST] End: fmu",
        )
    )

    # When: evaluator output is normalized by the registry engine.
    result = evaluate_profile_result(spec, ConsoleSnapshot(si0=console))

    # Then: exact Task 1 IDs produce a non-empty PASS result.
    assert result == {
        "version": 1,
        "profile_id": "safety-diagnostics-tests",
        "backend": "qbox",
        "verdict": "PASS",
        "expected": ["safety-island-fmu", "safety-island-ssu"],
        "assertions": [
            {
                "id": "safety-island-fmu",
                "status": "PASS",
                "coverage_kind": "identical",
            },
            {
                "id": "safety-island-ssu",
                "status": "PASS",
                "coverage_kind": "identical",
            },
        ],
    }


def test_help_surface_mentions_validation_profile(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Given: the canonical full-system parser.
    with pytest.raises(SystemExit) as completed:
        full_runner.parse_args(["--help"])
    help_text = capsys.readouterr().out

    # When/Then: users can discover the registry selection flag.
    assert completed.value.code == 0
    assert "--validation-profile NAME" in help_text


def test_runtime_child_rejects_outer_owned_si0_profile(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Given: an SI0-only profile incorrectly sent to the inner runtime child.
    # When: runtime-child preflight parses the selection.
    with pytest.raises(SystemExit) as completed:
        full_runner.runtime_engine.parse_args(
            ["--validation-profile", "safety-diagnostics-tests"]
        )

    # Then: it rejects the unbound console before process launch.
    assert completed.value.code == 2
    assert "unbound_console:si0" in capsys.readouterr().err
