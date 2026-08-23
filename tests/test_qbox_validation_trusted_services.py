from __future__ import annotations

from dataclasses import replace

import pytest

from scripts.run.qbox_validation.registry import (
    canonical_matrix_path,
    resolve_profile,
)
from scripts.run.qbox_validation.result import evaluate_profile_result
from scripts.run.qbox_validation.types import Console, ConsoleSnapshot


EXPECTED = (
    "ts-psa-crypto-api-test",
    "ts-psa-ps-api-test",
    "ts-psa-its-api-test",
    "ts-psa-iat-api-test",
)


def _suite_output(name: str, tests: int, passed: int, skipped: int) -> str:
    return (
        f"__QBOX_TS_BEGIN__:{name}\n"
        f"TOTAL TESTS     : {tests}\n"
        f"TOTAL PASSED    : {passed}\n"
        "TOTAL SIM ERROR : 0\n"
        "TOTAL FAILED    : 0\n"
        f"TOTAL SKIPPED   : {skipped}\n"
        f"__QBOX_TS_RC__:{name}:0\n"
        f"__QBOX_TS_END__:{name}\n"
    )


def _outputs() -> tuple[str, ...]:
    return (
        _suite_output("crypto", 60, 57, 3),
        _suite_output("ps", 17, 11, 6),
        _suite_output("its", 10, 10, 0),
        _suite_output("iat", 1, 1, 0),
    )


def _result(
    outputs: tuple[str, ...],
    snapshot: ConsoleSnapshot | None = None,
) -> dict[str, str]:
    spec = resolve_profile("trusted-services", canonical_matrix_path())
    evaluated = evaluate_profile_result(
        spec,
        snapshot or ConsoleSnapshot(primary="root@apollo-qvp:~# "),
        outputs,
    )
    return {item["id"]: item["status"] for item in evaluated["assertions"]}


def test_trusted_services_profile_runs_all_four_psa_binaries() -> None:
    spec = resolve_profile("trusted-services", canonical_matrix_path())

    assert spec.coverage_kind == "identical"
    assert spec.required_consoles == frozenset({Console.PRIMARY})
    assert spec.expected_assertion_ids == EXPECTED
    assert len(spec.steps) == 4
    commands = "\n".join(step.command for step in spec.steps)
    for binary in (
        "psa-crypto-api-test",
        "psa-ps-api-test",
        "psa-its-api-test",
        "psa-iat-api-test",
    ):
        assert binary in commands


def test_trusted_services_evaluator_accepts_complete_psa_summaries() -> None:
    assert _result(_outputs()) == {item: "PASS" for item in EXPECTED}


@pytest.mark.parametrize(
    ("index", "old", "new", "assertion_id"),
    (
        (0, "TOTAL TESTS     : 60", "TOTAL TESTS     : 0", EXPECTED[0]),
        (1, "TOTAL FAILED    : 0", "TOTAL FAILED    : 1", EXPECTED[1]),
        (2, "TOTAL SKIPPED   : 0", "TOTAL SKIPPED   : 1", EXPECTED[2]),
        (3, "TOTAL PASSED    : 1", "TOTAL PASSED    : bad", EXPECTED[3]),
        (0, "TOTAL TESTS     : 60", "", EXPECTED[0]),
        (1, "TOTAL TESTS     : 17", "TOTAL TESTS     : 17\nTOTAL TESTS     : 17", EXPECTED[1]),
        (2, "__QBOX_TS_RC__:its:0", "__QBOX_TS_RC__:its:1", EXPECTED[2]),
        (3, "__QBOX_TS_END__:iat", "", EXPECTED[3]),
    ),
)
def test_trusted_services_evaluator_rejects_bad_suite_output(
    index: int,
    old: str,
    new: str,
    assertion_id: str,
) -> None:
    outputs = list(_outputs())
    outputs[index] = outputs[index].replace(old, new)

    assert _result(tuple(outputs))[assertion_id] == "FAIL"


def test_trusted_services_evaluator_rejects_partial_output_set() -> None:
    statuses = _result(_outputs()[:3])

    assert statuses["ts-psa-iat-api-test"] == "FAIL"
    assert tuple(statuses.values()).count("PASS") == 3


@pytest.mark.parametrize("marker", ("E/TC", "FF-A: error", "FF-A: failed"))
def test_trusted_services_evaluator_rejects_secure_console_error(
    marker: str,
) -> None:
    snapshot = ConsoleSnapshot(
        primary="root@apollo-qvp:~# ",
        secure=f"secure boot complete\n{marker}: injected failure\n",
    )

    assert all(status == "FAIL" for status in _result(_outputs(), snapshot).values())


def test_trusted_services_evaluator_ignores_expected_seproxy_negative_errors() -> None:
    snapshot = ConsoleSnapshot(
        primary="root@apollo-qvp:~# ",
        secure="E/SEPROXY: secure_storage_ipc_remove psa_call: -140\n",
    )

    assert _result(_outputs(), snapshot) == {item: "PASS" for item in EXPECTED}


def test_trusted_services_evaluator_rejects_misleading_boot_only_success() -> None:
    snapshot = replace(
        ConsoleSnapshot(),
        primary="Booting Linux\nReached target Multi-User System\nroot@apollo-qvp:~# ",
    )

    assert all(status != "PASS" for status in _result((), snapshot).values())
