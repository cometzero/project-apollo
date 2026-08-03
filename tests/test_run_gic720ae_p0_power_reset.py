from __future__ import annotations

import json
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/test/run_gic720ae_p0_power_reset.py"
MARKER_ONLY = ROOT / "tests/fixtures/gic720ae/p0-power-marker-only.json"
SPEC = importlib.util.spec_from_file_location("p0_power_reset", RUNNER)
assert SPEC is not None and SPEC.loader is not None
P0_POWER_RESET = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = P0_POWER_RESET
SPEC.loader.exec_module(P0_POWER_RESET)


def run_validator(tmp_path: Path, fixture: Path) -> tuple[subprocess.CompletedProcess[str], Path]:
    out_dir = tmp_path / "result"
    result = subprocess.run(
        [sys.executable, str(RUNNER), "--self-test-negative", str(fixture), "--out-dir", str(out_dir)],
        cwd=ROOT, check=False, capture_output=True, text=True,
    )
    return result, out_dir / "p0-power-reset-result.json"


def complete_state_log(include_lifecycle: bool) -> str:
    records: list[str] = []
    for pe in range(1, 5):
        records.extend([
            f"GIC720AE_POWER_STATE scenario=pending-warm-reset pe={pe} phase=pre-reset observed_pending=1 observed_active=1 raw_pwrr=0x00000000 raw_waker=0x00000000 raw_pending=0x00000001 raw_active=0x00000001 error=0 timeout=0",
            f"GIC720AE_POWER_STATE scenario=pending-warm-reset pe={pe} phase=post-reset observed_pending=1 observed_active=1 raw_pwrr=0x00000000 raw_waker=0x00000000 raw_pending=0x00000000 raw_active=0x00000000 error=0 timeout=0",
            f"GIC720AE_POWER_STATE scenario=pwrr pe={pe} phase=off-observed observed_pending=0 observed_active=0 raw_pwrr=0x00000001 raw_waker=0x00000000 raw_pending=0x00000000 raw_active=0x00000000 error=0 timeout=0",
            f"GIC720AE_POWER_STATE scenario=pwrr pe={pe} phase=on-observed observed_pending=0 observed_active=0 raw_pwrr=0x00000000 raw_waker=0x00000000 raw_pending=0x00000000 raw_active=0x00000000 error=0 timeout=0",
            f"GIC720AE_POWER_STATE scenario=waker pe={pe} phase=sleep-observed observed_pending=0 observed_active=0 raw_pwrr=0x00000000 raw_waker=0x00000006 raw_pending=0x00000000 raw_active=0x00000000 error=0 timeout=0",
            f"GIC720AE_POWER_STATE scenario=waker pe={pe} phase=awake-observed observed_pending=0 observed_active=0 raw_pwrr=0x00000000 raw_waker=0x00000000 raw_pending=0x00000000 raw_active=0x00000000 error=0 timeout=0",
        ])
    if include_lifecycle:
        records.extend(
            f"GIC720AE_POWER_{phase} scenario={scenario} pe={pe} pass=1"
            for scenario in ("pwrr", "waker", "pending-warm-reset")
            for pe in range(1, 5)
            for phase in ("START", "READY", "DONE")
        )
        records.extend(
            f"GIC720AE_POWER_{phase} scenario=pwrr-timeout-negative pe=1 pass=1"
            for phase in ("START", "READY", "DONE")
        )
    records.append(
        "GIC720AE_POWER_NEGATIVE scenario=pwrr-timeout-negative verdict=PASS expected=FWK_E_TIMEOUT"
    )
    return "\n".join(records)


def test_marker_only_evidence_is_not_power_reset_qualification(tmp_path: Path) -> None:
    # Given: the fixture contains the expected human-readable power markers only.
    # When: the negative parser surface evaluates it.
    result, output = run_validator(tmp_path, MARKER_ONLY)

    # Then: marker strings cannot replace per-cycle state transitions.
    assert result.returncode != 0
    assert json.loads(output.read_text(encoding="utf-8"))["reason"] == "missing_state_transition"


def test_state_transitions_require_scp_lifecycle_for_every_scenario() -> None:
    # Given: all raw register transitions and the expected timeout-negative result.
    log = complete_state_log(include_lifecycle=False)

    # When: runtime states are accepted without SCP START/READY/DONE markers.
    passed, reason, _ = P0_POWER_RESET.state_observations(
        P0_POWER_RESET.parse_states(log), log,
    )

    # Then: the production lifecycle remains a mandatory independent gate.
    assert passed is False
    assert reason == "missing_scp_power_lifecycle"


def test_state_transitions_accept_complete_scp_lifecycle() -> None:
    passed, reason, _ = P0_POWER_RESET.state_observations(
        P0_POWER_RESET.parse_states(complete_state_log(include_lifecycle=True)),
        complete_state_log(include_lifecycle=True),
    )

    assert passed is True
    assert reason == "state_transitions_pass"


def test_synthetic_structured_three_cycle_surface_is_explicitly_not_runtime(tmp_path: Path) -> None:
    # Given: every required scenario carries three concrete state transitions.
    fixture = tmp_path / "structured.json"
    scenarios = ["pending-warm-reset", "cl1-cpu-power-cycle", "pwrr-timeout-negative"]
    fixture.write_text(json.dumps({
        "cycles": [
            {"cycle": cycle, "scenarios": [
                {"scenario": scenario, "states": ["before", "transition", "after"], "stale_irq": 0,
                 "timer_resumed": True, "pfdi_rpmsg_recovered": True, "timeout_errors": 0}
                for scenario in scenarios
            ]}
            for cycle in (1, 2, 3)
        ]
    }), encoding="utf-8")
    out_dir = tmp_path / "valid"

    # When: the parser is asked to evaluate synthetic structured evidence.
    result = subprocess.run(
        [sys.executable, str(RUNNER), "--self-test-structured", str(fixture), "--out-dir", str(out_dir)],
        cwd=ROOT, check=False, capture_output=True, text=True,
    )

    # Then: its parser succeeds but refuses to label it runtime qualification.
    assert result.returncode == 0, result.stderr
    payload = json.loads((out_dir / "p0-power-reset-result.json").read_text(encoding="utf-8"))
    assert payload["verdict"] == "PASS"
    assert payload["qualification"] == "SYNTHETIC_ONLY"
    assert payload["cycles_verified"] == 3


def test_runtime_mode_requires_independent_runner_records(tmp_path: Path) -> None:
    # Given: nominal artifacts but no canonical child result or UART observations.
    provenance = tmp_path / "provenance.json"
    si0 = tmp_path / "si0.bin"
    elf = tmp_path / "si0.elf"
    si1 = tmp_path / "si1.bin"
    for path in (si0, elf, si1):
        path.write_bytes(b"artifact")
    provenance.write_text(json.dumps({
        "verdict": "PASS",
        "outputs": [
            {"role": "si0_ramfw.bin", "path": str(si0), "sha256": ""},
            {"role": "apollo-qvp-si0-bl2.elf", "path": str(elf), "sha256": ""},
        ],
        "provenance": {"owners": {"hsoc-stack/components/system_mgmt/scp-firmware": "current"}},
    }), encoding="utf-8")
    out_dir = tmp_path / "runtime"

    # When: runtime qualification is requested without a runnable child runner.
    result = subprocess.run(
        [
            sys.executable, str(RUNNER), "--runner", str(tmp_path / "missing-runner"),
            "--si-single-gic", "--cycles", "3",
            "--scenarios", "pending-warm-reset,cl1-cpu-power-cycle,pwrr-timeout-negative",
            "--scp-power-profile-provenance", str(provenance),
            "--si-cl0-image", str(si0), "--si-cl0-symbols", str(elf),
            "--si-cl0-command", "test gic_power", "--si-cl1-image", str(si1),
            "--record-artifact-hashes", "--timeout", "1", "--out-dir", str(out_dir),
        ], cwd=ROOT, check=False, capture_output=True, text=True,
    )

    # Then: marker-free transport cannot be promoted to a runtime pass.
    assert result.returncode != 0
    payload = json.loads((out_dir / "p0-power-reset-result.json").read_text(encoding="utf-8"))
    assert payload["qualification"] == "NOT_QUALIFIED"
    assert payload["reason"] in {"runner_not_found", "runtime_artifact_mismatch"}


def test_runtime_child_failure_writes_a_cycle_receipt(tmp_path: Path) -> None:
    # Given: a valid profile and a runner that exits before producing artifacts.
    provenance = tmp_path / "provenance.json"
    si0 = tmp_path / "si0.bin"
    elf = tmp_path / "si0.elf"
    si1 = tmp_path / "si1.bin"
    for path in (si0, elf, si1):
        path.write_bytes(b"artifact")
    provenance.write_text(json.dumps({
        "verdict": "PASS",
        "outputs": [
            {"role": "si0_ramfw.bin", "path": str(si0), "sha256": hashlib.sha256(si0.read_bytes()).hexdigest()},
            {"role": "apollo-qvp-si0-bl2.elf", "path": str(elf), "sha256": hashlib.sha256(elf.read_bytes()).hexdigest()},
        ],
    }), encoding="utf-8")
    fake_runner = tmp_path / "failing-runner.py"
    fake_runner.write_text("import sys\nraise SystemExit(9)\n", encoding="utf-8")
    out_dir = tmp_path / "runtime"

    # When: the first independent child aborts before creating its own output.
    result = subprocess.run(
        [
            sys.executable, str(RUNNER), "--runner", str(fake_runner),
            "--si-single-gic", "--cycles", "3",
            "--scenarios", "pending-warm-reset,cl1-cpu-power-cycle,pwrr-timeout-negative",
            "--scp-power-profile-provenance", str(provenance),
            "--si-cl0-image", str(si0), "--si-cl0-symbols", str(elf),
            "--si-cl0-command", "test gic_power", "--si-cl1-image", str(si1),
            "--record-artifact-hashes", "--timeout", "1", "--out-dir", str(out_dir),
        ], cwd=ROOT, check=False, capture_output=True, text=True,
    )

    # Then: the validator records the child failure without a traceback.
    assert result.returncode != 0
    assert (out_dir / "cycle-1" / "orchestrator-child.stdout.log").is_file()
    payload = json.loads((out_dir / "p0-power-reset-result.json").read_text(encoding="utf-8"))
    assert payload["reason"] == "missing_runtime_evidence"
