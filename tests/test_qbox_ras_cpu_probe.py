from __future__ import annotations

import os

from scripts.run import run_qbox_apollo_fvp_full as full_runner
from qbox_ras_cpu_probe import evaluate_ras_cpu_probe, ras_cpu_probe_commands


runtime = full_runner.runtime_engine


def ras_primary_log() -> str:
    return "\n".join(
        [
            "ras_prerequisites_rc:0",
            "CorrectableCpuError UncorrectableFatalCpuError DeferredCpuError",
            "ras_list_rc:0",
            "Unknown error type: InvalidErrorType",
            "ras_invalid_rc:0",
            "ErrorName is one of: CorrectableCpuError UncorrectableFatalCpuError DeferredCpuError",
            "ras_usage_rc:0",
            "event severity: corrected",
            "processor context not corrupted",
            "the error has been corrected",
            "Context info structure 0",
            "Context info structure 1",
            "ras_correctable_rc:0",
            "event severity: recoverable",
            "the error has not been corrected",
            "ras_deferred_rc:0",
            "ras_repeat_rc:0",
            "ras_combined_rc:0",
            "rasdaemon: ras:arm_event event enabled",
            "ras_journal_rc:0",
            "ras_uncorrectable_rc:0",
            "__QBOX_RAS_CPU_PROBE_DONE__",
            "__QBOX_PROBE_DONE__",
        ]
    )


def test_ras_cpu_probe_commands_cover_fvp_contract() -> None:
    # Given/When: the fixed QBox RAS CPU sequence is built.
    commands = ras_cpu_probe_commands()

    # Then: product prerequisites and every FVP error class are covered.
    joined = "\n".join(commands)
    assert "ts-ras-inject --list" in joined
    assert "CorrectableCpuError" in joined
    assert "DeferredCpuError" in joined
    assert "UncorrectableFatalCpuError" in joined
    assert "journalctl -u rasdaemon.service" in joined
    assert "seq 1 10" in joined
    assert commands[-1] == "echo __QBOX_PROBE_DONE__"


def test_ras_cpu_probe_accepts_complete_cross_console_evidence() -> None:
    # Given: Linux, TF-A, and SCP evidence for the complete profile.
    secure = "\n".join(["CPU RAS: Interrupt Received"] * 14)
    scp = "\n".join(
        [
            "Faulty CPU Identified",
            "Fault Type = Uncontainable Error",
            "Setting SSU FSM to: ERRC",
        ]
    )

    # When: the QBox RAS result is evaluated.
    result = evaluate_ras_cpu_probe(ras_primary_log(), secure, scp)

    # Then: every FVP contract and the aggregate verdict pass.
    assert result["passed"] is True
    assert result["failed_checks"] == []
    assert result["tfa_interrupt_count"] == 14


def test_ras_cpu_probe_rejects_missing_scp_fault() -> None:
    # Given: complete Linux/TF-A evidence without SI0 uncontainable handling.
    secure = "\n".join(["CPU RAS: Interrupt Received"] * 14)

    # When: the cross-console result is evaluated.
    result = evaluate_ras_cpu_probe(ras_primary_log(), secure, "")

    # Then: the missing SCP fault remains explicit.
    assert result["passed"] is False
    assert "scp_faulty_cpu" in result["failed_checks"]


def test_qbox_product_probe_answers_only_getty_terminal_query(tmp_path) -> None:
    # Given: a product-image probe and an early U-Boot terminal query.
    args = runtime.parse_args(
        ["--out-dir", str(tmp_path), "--ras-cpu-probe"]
    )
    state = runtime.make_probe_state(args)
    read_fd, write_fd = os.pipe()
    os.set_blocking(read_fd, False)
    try:
        # When: the console has not reached the Linux login stage.
        runtime.drive_post_login_probe(
            args,
            {"primary_console": "\x1b[6n"},
            state,
            write_fd,
        )

        # Then: U-Boot receives no input, while the later getty query does.
        try:
            early_response = os.read(read_fd, 64)
        except BlockingIOError:
            early_response = b""
        assert early_response == b""
        runtime.drive_post_login_probe(
            args,
            {
                "primary_console":
                    f"\x1b[6n\n{args.primary_login_prompt}\n\x1b[6n"
            },
            state,
            write_fd,
        )
        getty_input = os.read(read_fd, 64)
        assert getty_input.startswith(b"\x1b[32766;32766R")
        assert getty_input.count(b"\x1b[32766;32766R") == 1
        assert state["terminal_status_responses"] == 2
    finally:
        os.close(read_fd)
        os.close(write_fd)
