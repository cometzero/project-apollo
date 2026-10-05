from __future__ import annotations

import importlib
from dataclasses import replace
import json
import os
from pathlib import Path
import sys
import time

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
    assert receipt["completion_gate"]["released"] is True
    assert receipt["completion_gate"]["cleaned"] is True
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
    assert receipt["completion_gate"]["released"] is False
    assert receipt["completion_gate"]["cleaned"] is True


def fake_smcf_child() -> list[str]:
    # AP becomes ready before the first delayed sensor reading. The fake
    # runtime, like production, exits on readiness unless its gate is pending.
    script = r'''
import json
import os
from pathlib import Path
import sys
import time

log = Path(os.environ["SI0_PROFILE_LOG"])
receipt = Path(os.environ["SI0_PROFILE_RECEIPT"])
gate = None
if "--required-pass-marker" in sys.argv:
    index = sys.argv.index("--required-pass-marker")
    gate, marker = Path(sys.argv[index + 1]), sys.argv[index + 2]
log.write_text("[SI0_PLATFORM] SCP started\n"
               "[FWK] Module initialization complete!\n"
               "[SMCF_CLIENT] start data_sampling for MGI[0]\n")
fd = os.open(os.environ["QBOX_APOLLO_FULL_SI_CL0_UART_READ_FILE"],
             os.O_RDONLY | os.O_NONBLOCK)
commands = []
samples = 0
pending = b""
sample_at = None
deadline = time.monotonic() + 5
try:
    while time.monotonic() < deadline:
        now = time.monotonic()
        try:
            pending += os.read(fd, 512)
        except BlockingIOError:
            pass
        if pending.endswith(b"\x04"):
            commands.append(pending.hex())
            pending = b""
            with log.open("a") as stream:
                stream.write("[INTEGRATION_TEST] Start: smcf\n"
                             "1 Tests 0 Failures 0 Ignored\nOK\n"
                             "[INTEGRATION_TEST] End: smcf\n")
            if len(commands) % 2:
                sample_at = now + 0.1
        if commands and (gate is None or marker in gate.read_text()):
            receipt.write_text(json.dumps({"commands": commands,
                "samples": samples, "normal_exit": True}))
            sys.exit(0)
        if (sample_at is not None and now >= sample_at
                and os.environ.get("SI0_NO_SENSOR") != "1"):
            with log.open("a") as stream:
                stream.write("[SMCF_CLIENT] Values for MGI TEMP MLI 1 (Sensor)\n"
                             "[SMCF_CLIENT] Value[0] data = 0x1a\n")
            samples += 1
            sample_at = None
        time.sleep(0.005)
    sys.exit(124)
finally:
    os.close(fd)
'''
    return [sys.executable, "-c", script]


@pytest.mark.parametrize("sensor_available", [True, False])
def test_outer_smcf_gate_waits_past_ap_ready_and_cleans_on_timeout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, sensor_available: bool,
) -> None:
    args = full_runner.parse_args([
        "--validation-profile", "smcf", "--out-dir", str(tmp_path),
    ])
    if not sensor_available:
        real_resolve = full_runner.resolve_profile

        def short_profile(*values):
            spec = real_resolve(*values)
            return replace(spec, steps=tuple(
                replace(step, timeout_s=0.5) for step in spec.steps
            ))

        monkeypatch.setattr(full_runner, "resolve_profile", short_profile)
    receipt_path = tmp_path / "smcf-child.json"
    environment = {
        **os.environ,
        "SI0_PROFILE_LOG": str(tmp_path / "qbox-safety-island-cl0.log"),
        "SI0_PROFILE_RECEIPT": str(receipt_path),
        "SI0_NO_SENSOR": "0" if sensor_available else "1",
    }
    started = time.monotonic()
    returncode = full_runner.run_child_with_si_cl0_transport(
        args, fake_smcf_child(), environment,
    )
    receipt = args.si_cl0_command_transport
    gate = receipt["completion_gate"]
    assert gate["cleaned"] is True
    assert not Path(gate["path"]).exists()
    assert receipt["fifo_cleaned"] is True
    if sensor_available:
        child_receipt = json.loads(receipt_path.read_text())
        assert returncode == 0 and child_receipt["normal_exit"] is True
        assert len(child_receipt["commands"]) == 4
        assert child_receipt["samples"] == 2
        assert receipt["validation_profile_result"]["verdict"] == "PASS"
        assert gate["released"] is True
    else:
        assert returncode == 124
        assert receipt["profile_blocker"] == "command_timeout:0:si0"
        assert receipt["validation_profile_result"]["verdict"] == "BLOCKED"
        assert receipt["child_returncode"] is not None
        assert gate["released"] is False
        assert not receipt_path.exists()
        assert time.monotonic() - started < 3
