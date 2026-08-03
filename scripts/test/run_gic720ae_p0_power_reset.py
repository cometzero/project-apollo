#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


SCENARIOS = ("pending-warm-reset", "cl1-cpu-power-cycle", "pwrr-timeout-negative")
CL1_MARKERS = ("Booting Zephyr", "PFDI Agent setup complete", "PFDI service ready", "RPMSG Endpoint: ATTACHED")
STATE_RE = re.compile(r"GIC720AE_POWER_STATE scenario=(?P<scenario>[^ ]+) pe=(?P<pe>[1-4]) phase=(?P<phase>[^ ]+) .*?observed_pending=(?P<pending>[01]) observed_active=(?P<active>[01]) raw_pwrr=0x(?P<pwrr>[0-9a-fA-F]{8}) raw_waker=0x(?P<waker>[0-9a-fA-F]{8}) raw_pending=0x(?P<raw_pending>[0-9a-fA-F]{8}) raw_active=0x(?P<raw_active>[0-9a-fA-F]{8}) error=(?P<error>-?\d+) timeout=(?P<timeout>[01])")
LIFECYCLE_RE = re.compile(r"GIC720AE_POWER_(?P<phase>START|READY|DONE) scenario=(?P<scenario>[^ ]+) pe=(?P<pe>[1-4]) pass=(?P<passed>[01])")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test-negative", type=Path)
    group.add_argument("--self-test-structured", type=Path)
    group.add_argument("--runner", type=Path)
    parser.add_argument("--si-single-gic", action="store_true")
    parser.add_argument("--cycles", type=int)
    parser.add_argument("--scenarios")
    parser.add_argument("--scp-power-profile-provenance", type=Path)
    parser.add_argument("--si-cl0-image", type=Path)
    parser.add_argument("--si-cl0-symbols", type=Path)
    parser.add_argument("--si-cl0-command")
    parser.add_argument("--si-cl1-image", type=Path)
    parser.add_argument("--record-artifact-hashes", action="store_true")
    parser.add_argument("--timeout", type=int)
    parser.add_argument("--out-dir", type=Path, required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def write_result(out_dir: Path, payload: dict[str, object]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "p0-power-reset-result.json").write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def validate_cycles(value: object) -> tuple[bool, str, int]:
    if not isinstance(value, dict) or not isinstance(value.get("cycles"), list):
        return False, "missing_state_transition", 0
    cycles = value["cycles"]
    if len(cycles) != 3:
        return False, "incomplete_cycle_count", 0
    for number, cycle in enumerate(cycles, start=1):
        if not isinstance(cycle, dict) or cycle.get("cycle") != number or not isinstance(cycle.get("scenarios"), list):
            return False, "missing_state_transition", 0
        records = cycle["scenarios"]
        if {item.get("scenario") for item in records if isinstance(item, dict)} != set(SCENARIOS):
            return False, "incomplete_scenarios", 0
        for item in records:
            if not isinstance(item, dict) or item.get("states") != ["before", "transition", "after"] or item.get("stale_irq") != 0 or item.get("timer_resumed") is not True or item.get("pfdi_rpmsg_recovered") is not True or item.get("timeout_errors") != 0:
                return False, "missing_state_transition", 0
    return True, "structured_power_reset_pass", 3


def runtime_inputs(args: argparse.Namespace) -> tuple[bool, str, dict[str, str]]:
    required = (args.scp_power_profile_provenance, args.si_cl0_image, args.si_cl0_symbols, args.si_cl1_image)
    if any(path is None or not path.is_file() for path in required):
        return False, "runtime_artifact_mismatch", {}
    if not args.si_single_gic or args.cycles != 3 or tuple((args.scenarios or "").split(",")) != SCENARIOS:
        return False, "invalid_runtime_plan", {}
    if args.timeout is None or args.timeout < 1 or not args.record_artifact_hashes:
        return False, "invalid_runtime_plan", {}
    if args.si_cl0_command is None or re.fullmatch(r"[ -~]{1,512}", args.si_cl0_command) is None:
        return False, "invalid_si_cl0_command", {}
    profile = read_json(args.scp_power_profile_provenance)
    outputs = profile.get("outputs")
    if profile.get("verdict") != "PASS" or not isinstance(outputs, list):
        return False, "stale_provenance", {}
    hashes = {"si_cl0_image": sha256(args.si_cl0_image), "si_cl0_symbols": sha256(args.si_cl0_symbols), "si_cl1_image": sha256(args.si_cl1_image), "provenance": sha256(args.scp_power_profile_provenance)}
    expected = {str(item.get("role")): str(item.get("sha256")) for item in outputs if isinstance(item, dict)}
    if expected.get("si0_ramfw.bin") != hashes["si_cl0_image"] or expected.get("apollo-qvp-si0-bl2.elf") != hashes["si_cl0_symbols"]:
        return False, "runtime_artifact_mismatch", hashes
    return True, "runtime_inputs_ready", hashes


def parse_states(log: str) -> list[dict[str, int | str]]:
    records: list[dict[str, int | str]] = []
    for match in STATE_RE.finditer(log):
        record: dict[str, int | str] = {key: int(value, 16) if key.startswith("raw_") or key in ("pwrr", "waker") else int(value) if key in ("pe", "pending", "active", "error", "timeout") else value for key, value in match.groupdict().items()}
        records.append(record)
    return records


def find_state(records: list[dict[str, int | str]], scenario: str, pe: int, phase: str) -> dict[str, int | str] | None:
    return next((record for record in records if record["scenario"] == scenario and record["pe"] == pe and record["phase"] == phase), None)


def state_observations(records: list[dict[str, int | str]], cl0_log: str) -> tuple[bool, str, dict[str, object]]:
    lifecycle = {
        (match["scenario"], int(match["pe"]), match["phase"])
        for match in LIFECYCLE_RE.finditer(cl0_log)
        if match["passed"] == "1"
    }
    required_lifecycle = {
        (scenario, pe, phase)
        for scenario in ("pwrr", "waker", "pending-warm-reset")
        for pe in range(1, 5)
        for phase in ("START", "READY", "DONE")
    }
    required_lifecycle.update(
        ("pwrr-timeout-negative", 1, phase)
        for phase in ("START", "READY", "DONE")
    )
    evidence: dict[str, object] = {
        "records": records,
        "lifecycle_markers": ["/".join((scenario, str(pe), phase)) for scenario, pe, phase in sorted(lifecycle)],
    }
    if not required_lifecycle.issubset(lifecycle):
        return False, "missing_scp_power_lifecycle", evidence
    if any(record["error"] != 0 or record["timeout"] != 0 for record in records):
        return False, "state_transition_error", evidence
    for pe in range(1, 5):
        pre = find_state(records, "pending-warm-reset", pe, "pre-reset")
        post = find_state(records, "pending-warm-reset", pe, "post-reset")
        off = find_state(records, "pwrr", pe, "off-observed")
        on = find_state(records, "pwrr", pe, "on-observed")
        sleep = find_state(records, "waker", pe, "sleep-observed")
        awake = find_state(records, "waker", pe, "awake-observed")
        if None in (pre, post, off, on, sleep, awake):
            return False, "missing_state_transition", evidence
        assert pre is not None and post is not None and off is not None and on is not None and sleep is not None and awake is not None
        if (pre["pending"] == 0 and pre["active"] == 0) or post["raw_pending"] != 0 or post["raw_active"] != 0 or post["error"] != 0 or post["timeout"] != 0:
            return False, "warm_reset_stale_irq_gate_failed", evidence
        if off["pwrr"] & 1 != 1 or on["pwrr"] & 1 != 0 or sleep["waker"] & 6 != 6 or awake["waker"] & 6 != 0:
            return False, "pwrr_waker_gate_failed", evidence
        if any(record["error"] != 0 or record["timeout"] != 0 for record in (off, on, sleep, awake)):
            return False, "pwrr_waker_timeout", evidence
    if "GIC720AE_POWER_NEGATIVE scenario=pwrr-timeout-negative verdict=PASS expected=FWK_E_TIMEOUT" not in cl0_log:
        return False, "missing_timeout_negative_evidence", evidence
    return True, "state_transitions_pass", evidence


def cycle_evidence(cycle: int, cycle_dir: Path) -> tuple[bool, str, dict[str, object]]:
    child = cycle_dir / "result.json"
    cl0 = cycle_dir / "qbox-safety-island-cl0.log"
    cl1 = cycle_dir / "qbox-safety-island-cl1.log"
    timer = cycle_dir / "timer-snapshot.json"
    if not all(path.is_file() for path in (child, cl0, cl1, timer)):
        return False, "missing_runtime_evidence", {"cycle": cycle}
    result = read_json(child)
    cl0_log = cl0.read_text(encoding="utf-8", errors="replace")
    cl1_log = cl1.read_text(encoding="utf-8", errors="replace")
    timer_result = read_json(timer)
    transport = result.get("si_cl0_command_transport")
    commands = transport.get("commands") if isinstance(transport, dict) else []
    transport_passed = isinstance(commands, list) and len(commands) == 1 and all(isinstance(item, dict) and item.get("transport_returncode") == 0 and item.get("bytes_sent", 0) > 0 for item in commands)
    state_ok, state_reason, states = state_observations(parse_states(cl0_log), cl0_log)
    markers_ok = all(marker in cl1_log for marker in CL1_MARKERS) and not any(marker in cl1_log for marker in ("E_PARAM", "FWK_E_TIMEOUT", "PFDI timeout", "ERROR"))
    timer_ok = timer_result.get("status") == "pass" and isinstance(timer_result.get("samples"), list) and len(timer_result["samples"]) >= 2
    receipt: dict[str, object] = {"cycle": cycle, "runner_result": str(child.resolve()), "runner_returncode": result.get("child_returncode"), "child_result_sha256": sha256(child), "si0_log_sha256": sha256(cl0), "cl1_log_sha256": sha256(cl1), "timer_snapshot_sha256": sha256(timer), "command_transport": transport, "state_observations": states, "cl1_markers": {marker: marker in cl1_log for marker in CL1_MARKERS}}
    if result.get("passed") is not True or result.get("verdict") != "pass":
        return False, "runner_not_passed", receipt
    if not transport_passed:
        return False, "command_transport_failed", receipt
    if not timer_ok:
        return False, "timer_probe_failed", receipt
    if not markers_ok:
        return False, "cl1_recovery_gate_failed", receipt
    return (state_ok, state_reason, receipt)


def run_runtime(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
    inputs_ok, reason, hashes = runtime_inputs(args)
    payload: dict[str, object] = {"format_version": 2, "qualification": "NOT_QUALIFIED", "verdict": "FAIL", "reason": reason, "required_scenarios": list(SCENARIOS), "cycles_verified": 0, "artifact_hashes": hashes, "cycles": []}
    if not inputs_ok:
        return 1, payload
    if args.runner is None or not args.runner.is_file():
        payload["reason"] = "runner_not_found"
        return 1, payload
    child_hashes: set[str] = set()
    for cycle in range(1, 4):
        cycle_dir = args.out_dir / f"cycle-{cycle}"
        cycle_dir.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, str(args.runner), "--si-single-gic", "--timer-probe", "--si-cl0-command", args.si_cl0_command, "--si-cl0-image", str(args.si_cl0_image), "--si-cl1-image", str(args.si_cl1_image), "--skip-build", "--timeout", str(args.timeout), "--out-dir", str(cycle_dir)]
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        (cycle_dir / "orchestrator-child.stdout.log").write_text(completed.stdout, encoding="utf-8")
        (cycle_dir / "orchestrator-child.stderr.log").write_text(completed.stderr, encoding="utf-8")
        ok, cycle_reason, receipt = cycle_evidence(cycle, cycle_dir)
        receipt["runner_command"] = command
        receipt["runner_process_returncode"] = completed.returncode
        payload["cycles"].append(receipt)
        child_hash = receipt.get("child_result_sha256")
        if isinstance(child_hash, str) and child_hash in child_hashes:
            ok, cycle_reason = False, "duplicate_child_result"
        if isinstance(child_hash, str):
            child_hashes.add(child_hash)
        if completed.returncode != 0 or not ok:
            payload["reason"] = cycle_reason
            return 1, payload
    payload.update({"verdict": "PASS", "qualification": "RUNTIME_QUALIFIED", "reason": "three_independent_real_runtime_cycles", "cycles_verified": 3})
    return 0, payload


def main() -> int:
    args = parse_args()
    if args.runner is not None:
        rc, payload = run_runtime(args)
        write_result(args.out_dir, payload)
        return rc
    source = args.self_test_negative or args.self_test_structured
    assert source is not None
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        value = None
    passed, reason, cycles = validate_cycles(value)
    synthetic = args.self_test_structured is not None
    payload = {"format_version": 1, "verdict": "PASS" if passed else "FAIL", "reason": reason, "qualification": "SYNTHETIC_ONLY" if synthetic else "NOT_QUALIFIED", "cycles_verified": cycles, "required_scenarios": list(SCENARIOS)}
    write_result(args.out_dir, payload)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
