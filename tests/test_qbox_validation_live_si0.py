from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import sys

import pytest

from scripts.run import run_qbox_apollo_fvp_full as full_runner


evaluation_types = importlib.import_module("qbox_validation.types")


def fake_si0_profile_child(out_dir: Path) -> list[str]:
    script = """
import json
import os
from pathlib import Path

fifo = os.environ["QBOX_APOLLO_FULL_SI_CL0_UART_READ_FILE"]
log = Path(os.environ["SI0_PROFILE_LOG"])
log.write_text("[FWK] Module initialization complete!\\n", encoding="utf-8")
commands = []
with open(fifo, "rb", buffering=0) as stream:
    for name, total in (("ssu", 1), ("fmu", 20)):
        payload = b""
        while not payload.endswith(b"\\x04"):
            payload += stream.read(1)
        commands.append(payload.hex())
        with log.open("a", encoding="utf-8") as output:
            output.write(
                f"[INTEGRATION_TEST] Start: {name}\\n"
                f"{total} Tests 0 Failures 0 Ignored\\n"
                "OK\\n"
                f"[INTEGRATION_TEST] End: {name}\\n"
            )
Path(os.environ["SI0_PROFILE_RECEIPT"]).write_text(
    json.dumps(commands), encoding="utf-8"
)
"""
    return [sys.executable, "-c", script]


def test_outer_si0_launch_executes_registry_state_machine(tmp_path: Path) -> None:
    # Given: the canonical SI0 profile with a real child/FIFO and fake log seam.
    args = full_runner.parse_args(
        [
            "--validation-profile",
            "safety-diagnostics-tests",
            "--out-dir",
            str(tmp_path),
        ]
    )
    receipt_path = tmp_path / "child-receipt.json"
    environment = os.environ.copy()
    environment["SI0_PROFILE_LOG"] = str(
        tmp_path / "qbox-safety-island-cl0.log"
    )
    environment["SI0_PROFILE_RECEIPT"] = str(receipt_path)

    # When: the production outer-child transport runs the selected profile.
    returncode = full_runner.run_child_with_si_cl0_transport(
        args,
        fake_si0_profile_child(tmp_path),
        environment,
    )

    # Then: registry evaluation and managed cleanup are recorded on the run.
    receipt = args.si_cl0_command_transport
    profile_result = receipt["validation_profile_result"]
    assert returncode == 0
    assert profile_result["verdict"] == "PASS"
    assert receipt["profile_cleanup"] == {
        "passed": True,
        "detail": "no_resources",
    }
    assert receipt["fifo_cleaned"] is True
    assert not (tmp_path / "si-cl0-uart-input.fifo").exists()
    assert len(json.loads(receipt_path.read_text())) == 2
    assert full_runner.validation_profile_evidence(args, None) == profile_result


def test_outer_si0_evaluator_error_serializes_blocked_result(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    # Given: a live safety profile whose evaluator raises after real FIFO work.
    args = full_runner.parse_args(
        [
            "--validation-profile",
            "safety-diagnostics-tests",
            "--out-dir",
            str(tmp_path),
        ]
    )
    receipt_path = tmp_path / "error-child-receipt.json"
    environment = os.environ.copy()
    environment["SI0_PROFILE_LOG"] = str(
        tmp_path / "qbox-safety-island-cl0.log"
    )
    environment["SI0_PROFILE_RECEIPT"] = str(receipt_path)

    evaluator_type = type(
        full_runner.resolve_profile(
            "safety-diagnostics-tests",
            full_runner.workspace_root()
            / "qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml",
        ).evaluator
    )

    def raise_evaluator(evaluator, snapshot, outputs):
        raise evaluation_types.EvaluationError("evaluator_error")

    monkeypatch.setattr(evaluator_type, "evaluate", raise_evaluator)

    # When: outer runtime and canonical result writing consume that failure.
    child_returncode = full_runner.run_child_with_si_cl0_transport(
        args,
        fake_si0_profile_child(tmp_path),
        environment,
    )
    monkeypatch.setattr(full_runner, "si_gate_blocker", lambda *values: None)
    result_returncode = full_runner.write_result(
        args,
        {},
        command=[],
        child_status={"passed": True},
        child_returncode=child_returncode,
        blocker=None,
        check_only=False,
    )

    # Then: schema-shaped BLOCKED assertions and evaluator blocker are stable.
    receipt = args.si_cl0_command_transport
    profile_result = receipt["validation_profile_result"]
    written = json.loads((tmp_path / "result.json").read_text())
    assert child_returncode != 0
    assert result_returncode != 0
    assert receipt["profile_cleanup"] == {
        "passed": True,
        "detail": "no_resources",
    }
    assert profile_result["verdict"] == "BLOCKED"
    assert profile_result["expected"] == [
        "safety-island-fmu",
        "safety-island-ssu",
    ]
    assert all(item["status"] == "BLOCKED" for item in profile_result["assertions"])
    assert written["passed"] is False
    assert written["blocker"] == "evaluator_error"
    assert written["safety_diagnostics_probe"]["passed"] is False
