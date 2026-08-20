from __future__ import annotations

import json
from pathlib import Path

import pytest

from apollo_validation.evidence import append_record, write_reports
from apollo_validation.profile_results import (
    AssertionStatus,
    ObservedAssertion,
    evaluate_profile,
    normalize_profile_run,
)
from apollo_validation.validation_matrix import load_validation_matrix


WORKSPACE = Path(__file__).resolve().parents[2]
MATRIX_PATH = WORKSPACE / "qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml"
REAL_PFDI_RESULT = (
    Path(__file__).parent / "fixtures/profile_results/pfdi-testresults.json"
)


def _profile(profile_id: str):
    matrix = load_validation_matrix(MATRIX_PATH)
    return next(profile for profile in matrix.profiles if profile.profile_id == profile_id)


def _assertion(
    assertion_id: str,
    status: AssertionStatus = "PASS",
) -> ObservedAssertion:
    return ObservedAssertion(
        assertion_id=assertion_id,
        status=status,
        coverage_kind="identical",
    )


def _profile_run(tmp_path: Path, profile_id: str, backend: str) -> Path:
    (tmp_path / "selection.json").write_text(
        json.dumps({"profile_name": profile_id}), encoding="utf-8"
    )
    (tmp_path / "manifest.json").write_text(
        json.dumps({"backend": backend, "test_profile": profile_id}),
        encoding="utf-8",
    )
    return tmp_path


def test_real_oeqa_result_normalizes_to_complete_pfdi_assertions(
    tmp_path: Path,
) -> None:
    # Given: the repository's captured OEQA testresults.json shape.
    run_dir = _profile_run(tmp_path, "pfdi", "fvp")
    append_record(
        run_dir / "commands.jsonl",
        {
            "name": "oeqa",
            "status": "pass",
            "artifacts": [{"kind": "oeqa_result", "path": str(REAL_PFDI_RESULT)}],
        },
    )

    # When: the named FVP profile is normalized.
    normalized = normalize_profile_run(run_dir, "pfdi", "fvp")

    # Then: stable matrix IDs, rather than OEQA method names, decide PASS.
    assert normalized.result.verdict == "PASS"
    assert normalized.counts.total == 7
    assert {item.assertion_id for item in normalized.result.assertions} == set(
        normalized.result.expected
    )


@pytest.mark.parametrize(
    ("profile_id", "methods"),
    [
        (
            "bsp-core",
            (
                "test_10_bsp_core.BSPCoreTest.test_firmware_boot_chain",
                "test_10_bsp_core.BSPCoreTest.test_linux_topology_and_devices",
                "test_10_bsp_core.BSPCoreTest.test_safety_island_cl1",
            ),
        ),
        (
            "si-cl1",
            ("test_10_bsp_core.BSPCoreTest.test_safety_island_cl1",),
        ),
        (
            "smcf",
            (
                "test_21_bsp_smcf.SmcfBspTest.test_01_smcf_client_start",
                "test_21_bsp_smcf.SmcfBspTest.test_02_execute_smcf_test",
                "test_21_bsp_smcf.SmcfBspTest.test_03_run_smcf_3x",
                "test_21_bsp_smcf.SmcfBspTest.test_04_smcf_client_sensor_monitor",
            ),
        ),
        (
            "cpuidle",
            (
                "test_31_bsp_cpuidle.BspCpuIdleTest.test_ensure_interface",
                "test_31_bsp_cpuidle.BspCpuIdleTest.test_cpuidle_c_states",
                "test_31_bsp_cpuidle.BspCpuIdleTest.test_default_status",
                "test_31_bsp_cpuidle.BspCpuIdleTest.test_disable_state",
                "test_31_bsp_cpuidle.BspCpuIdleTest.test_residency_latency",
                "test_31_bsp_cpuidle.BspCpuIdleTest.test_governors",
                "test_31_bsp_cpuidle.BspCpuIdleTest.test_governor_switching",
                "test_31_bsp_cpuidle.BspCpuIdleTest.test_invalid_governor",
            ),
        ),
    ],
)
def test_bsp_profile_oeqa_methods_normalize_each_assertion_once(
    tmp_path: Path,
    profile_id: str,
    methods: tuple[str, ...],
) -> None:
    # Given: passing real-shaped OEQA result entries for the selected profile.
    run_dir = _profile_run(tmp_path, profile_id, "fvp")
    result_path = run_dir / "oeqa/testresults.json"
    result_path.parent.mkdir(parents=True)
    result_path.write_text(
        json.dumps(
            {
                "runtime": {
                    "result": {
                        method: {"status": "PASSED"} for method in methods
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    append_record(
        run_dir / "commands.jsonl",
        {
            "name": "oeqa",
            "status": "pass",
            "artifacts": [{"kind": "oeqa_result", "path": str(result_path)}],
        },
    )

    # When: the public profile result is normalized.
    normalized = normalize_profile_run(run_dir, profile_id, "fvp")

    # Then: every expected assertion appears once with no blocker or skip.
    assert normalized.result.verdict == "PASS"
    assert normalized.counts.failed == 0
    assert normalized.counts.blocked == 0
    assert normalized.counts.skipped == 0
    assert normalized.counts.passed == len(normalized.result.expected)
    assert len({item.assertion_id for item in normalized.result.assertions}) == len(
        normalized.result.expected
    )


@pytest.mark.parametrize(
    ("observed", "verdict", "reason"),
    [
        ((), "BLOCKED", "blocked_profile_zero_assertions"),
        ((_assertion("pfdi-systemd-service", "SKIPPED"),), "BLOCKED", "blocked_profile_all_skipped"),
        ((_assertion("pfdi-systemd-service", "FAIL"),), "FAIL", "failed_profile_assertions"),
        ((_assertion("pfdi-systemd-service", "BLOCKED"),), "BLOCKED", "blocked_profile_assertions"),
    ],
)
def test_incomplete_assertion_status_never_passes(
    observed: tuple[ObservedAssertion, ...],
    verdict: str,
    reason: str,
) -> None:
    # Given: a named profile with an incomplete or unsuccessful observation set.
    # When: the assertion-complete verdict is evaluated.
    normalized = evaluate_profile(_profile("pfdi"), "qbox", observed)

    # Then: it has a stable non-PASS verdict and blocker reason.
    assert normalized.result.verdict == verdict
    assert reason in normalized.reasons


def test_missing_duplicate_and_unexpected_assertions_never_pass() -> None:
    # Given: duplicate and out-of-contract IDs with required assertions missing.
    observed = (
        _assertion("pfdi-systemd-service"),
        _assertion("pfdi-systemd-service"),
        _assertion("not-in-contract"),
    )

    # When: the named profile is evaluated.
    normalized = evaluate_profile(_profile("pfdi"), "qbox", observed)

    # Then: all three integrity failures are reported and PASS is impossible.
    assert normalized.result.verdict == "FAIL"
    assert set(normalized.reasons) >= {
        "duplicate_profile_assertion_ids",
        "unexpected_profile_assertion_ids",
        "missing_profile_assertions",
    }


def test_one_skipped_prerequisite_blocks_an_otherwise_complete_profile() -> None:
    # Given: every expected assertion, with one prerequisite skipped.
    profile = _profile("pfdi")
    observed = tuple(
        _assertion(assertion_id, "SKIPPED" if index == 0 else "PASS")
        for index, assertion_id in enumerate(profile.qbox_assertions)
    )

    # When: the complete set is evaluated.
    normalized = evaluate_profile(profile, "fvp", observed)

    # Then: one skip blocks the profile even though all IDs are present.
    assert normalized.result.verdict == "BLOCKED"
    assert "blocked_profile_assertions_skipped" in normalized.reasons


def test_boot_only_named_profile_writes_normalized_blocked_artifact(
    tmp_path: Path,
) -> None:
    # Given: successful context and boot commands but no assertions.
    run_dir = _profile_run(tmp_path, "pfdi", "qbox")
    append_record(run_dir / "commands.jsonl", {"name": "context", "status": "pass"})
    append_record(run_dir / "commands.jsonl", {"name": "qbox-boot", "status": "pass"})

    # When: the public reporting surface summarizes the run.
    summary, exit_code = write_reports(run_dir)

    # Then: misleading command success cannot produce a named-profile PASS.
    assert exit_code != 0
    assert summary["status"] == "BLOCKED"
    assert summary["counts"]["total"] == 7
    assert (run_dir / "profile-result.json").is_file()
    assert summary["profile_result"]["verdict"] == "BLOCKED"


def test_qbox_assertion_shaped_fixture_can_pass_named_profile(tmp_path: Path) -> None:
    # Given: an already-normalized QBox assertion fixture for every expected ID.
    profile = _profile("pfdi")
    run_dir = _profile_run(tmp_path, profile.profile_id, "qbox")
    fixture_path = run_dir / "qbox/result.json"
    fixture_path.parent.mkdir(parents=True)
    fixture_path.write_text(
        json.dumps(
            {
                "version": 1,
                "profile_id": profile.profile_id,
                "backend": "qbox",
                "verdict": "PASS",
                "expected": list(profile.qbox_assertions),
                "assertions": [
                    {
                        "id": assertion_id,
                        "status": "PASS",
                        "coverage_kind": profile.coverage_kind,
                    }
                    for assertion_id in profile.qbox_assertions
                ],
            }
        ),
        encoding="utf-8",
    )
    append_record(
        run_dir / "commands.jsonl",
        {
            "name": "qbox-boot",
            "status": "pass",
            "artifacts": [{"kind": "qbox_result", "path": str(fixture_path)}],
        },
    )

    # When: reporting consumes the QBox fixture without adding probe logic.
    summary, exit_code = write_reports(run_dir)

    # Then: the required assertions alone produce PASS and non-zero counts.
    assert exit_code == 0
    assert summary["status"] == "PASS"
    assert summary["counts"] == {
        "passed": 7,
        "failed": 0,
        "blocked": 0,
        "skipped": 0,
        "total": 7,
    }


@pytest.mark.parametrize("payload", ["{", '{"assertions":[{"id":"x","status":"MAYBE"}]}'])
def test_malformed_qbox_result_is_blocked_stably(
    tmp_path: Path,
    payload: str,
) -> None:
    # Given: malformed JSON or an invalid assertion status at the input boundary.
    run_dir = _profile_run(tmp_path, "pfdi", "qbox")
    result_path = run_dir / "qbox/result.json"
    result_path.parent.mkdir(parents=True)
    result_path.write_text(payload, encoding="utf-8")
    append_record(
        run_dir / "commands.jsonl",
        {
            "name": "qbox-boot",
            "status": "pass",
            "artifacts": [{"kind": "qbox_result", "path": str(result_path)}],
        },
    )

    # When: reporting parses the untrusted fixture.
    summary, exit_code = write_reports(run_dir)

    # Then: it returns a stable blocker with schema-shaped missing assertions.
    assert exit_code == 2
    assert summary["status"] == "BLOCKED"
    assert {item["reason"] for item in summary["blockers"]} >= {
        "blocked_invalid_profile_result"
    }


def test_stale_pass_assertions_cannot_hide_current_interruption(tmp_path: Path) -> None:
    # Given: complete stale assertions beside a current interrupted command.
    profile = _profile("pfdi")
    run_dir = _profile_run(tmp_path, profile.profile_id, "qbox")
    result_path = run_dir / "qbox/result.json"
    result_path.parent.mkdir(parents=True)
    result_path.write_text(
        json.dumps(
            {
                "assertions": [
                    {
                        "id": assertion_id,
                        "status": "PASS",
                        "coverage_kind": profile.coverage_kind,
                    }
                    for assertion_id in profile.qbox_assertions
                ]
            }
        ),
        encoding="utf-8",
    )
    append_record(
        run_dir / "commands.jsonl",
        {
            "name": "interrupt",
            "status": "blocked",
            "required": True,
            "artifacts": [{"kind": "qbox_result", "path": str(result_path)}],
        },
    )

    # When: the current run is summarized.
    summary, exit_code = write_reports(run_dir)

    # Then: stale success cannot override cancel or interruption state.
    assert exit_code == 2
    assert summary["profile_result"]["verdict"] == "BLOCKED"
    assert {item["reason"] for item in summary["blockers"]} >= {
        "blocked_required_profile_command"
    }
