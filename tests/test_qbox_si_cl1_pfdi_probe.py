from __future__ import annotations

from scripts.run import run_qbox_apollo_fvp_full as full_runner
from qbox_si_cl1_pfdi_probe import (
    advance_si_cl1_pfdi_probe,
    evaluate_si_cl1_pfdi_records,
    new_si_cl1_pfdi_state,
    si_cl1_pfdi_checks,
)


runtime = full_runner.runtime_engine


def test_si_cl1_pfdi_checks_cover_complete_fvp_contract() -> None:
    # Given/When: the fixed QBox SI CL1 PFDI command sequence is built.
    checks = si_cl1_pfdi_checks()

    # Then: all 119 FVP shell operations and CPU domains are represented.
    assert len(checks) == 119
    commands = [check.command for check in checks]
    assert "pfdi get-status 0" in commands
    assert "pfdi run 3 1 1 2" in commands
    assert "pfdi set-status 2 0" in commands
    assert "pfdi force-error 3 1" in commands
    assert commands.count("pfdi run 0") == 10
    assert commands[-1] == "pfdi info 0"


def test_si_cl1_pfdi_evaluator_requires_every_check() -> None:
    # Given: one matching record per complete SI CL1 PFDI check.
    checks = si_cl1_pfdi_checks()
    outputs = ["\n".join(check.pattern_examples) for check in checks]

    # When: all records are evaluated.
    result = evaluate_si_cl1_pfdi_records(checks, outputs)

    # Then: every CPU has the normalized FVP observation contract.
    assert result["passed"] is True
    assert result["checks_total"] == 119
    assert result["checks_passed"] == 119
    assert result["failed_checks"] == []
    assert all(
        all(value for key, value in cpu.items() if key != "cpu")
        for cpu in result["cpus"]
    )
    assert result["firmware_info_seen"] is True


def test_si_cl1_pfdi_evaluator_reports_missing_pattern() -> None:
    # Given: the complete sequence with one empty command result.
    checks = si_cl1_pfdi_checks()
    outputs = ["\n".join(check.pattern_examples) for check in checks]
    outputs[0] = ""

    # When: command results are evaluated.
    result = evaluate_si_cl1_pfdi_records(checks, outputs)

    # Then: the exact failed check remains visible.
    assert result["passed"] is False
    assert result["failed_checks"] == [checks[0].name]


def test_si_cl1_pfdi_probe_accepts_redrawn_zephyr_prompt() -> None:
    # Given: the adjacent prompts emitted after asynchronous Zephyr logs.
    state = new_si_cl1_pfdi_state()

    # When: the live console is advanced.
    command = advance_si_cl1_pfdi_probe(state, "booted\nuart:~$ uart:~$ ")

    # Then: the first SI CL1 command is ready for FIFO delivery.
    assert command == "pfdi get-status 0\n"
    assert state["command_index"] == 1
