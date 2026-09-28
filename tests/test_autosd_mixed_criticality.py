"""Host regressions: never mutate a running guest."""
import importlib.util
import json
from pathlib import Path
import sys

import pytest

SOURCE = Path(__file__).resolve().parents[1] / "autosd/customization/mixed-criticality-guest.py"
spec = importlib.util.spec_from_file_location("mixed_guest", SOURCE)
mixed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mixed)


def test_explicit_gate_required(tmp_path):
    with pytest.raises(SystemExit):
        mixed.main(["--out", str(tmp_path / "new")])
    assert not (tmp_path / "new").exists()


def test_runner_streams_and_checks(tmp_path, capsys):
    run = mixed.Runner(tmp_path)
    assert run.run(sys.executable, "-c", "print('guest evidence')") == "guest evidence"
    with pytest.raises(RuntimeError, match="Command failed"):
        run.run(sys.executable, "-c", "raise SystemExit(7)")
    run.log.close()
    assert "guest evidence" in capsys.readouterr().out
    assert "[exit=7]" in (tmp_path / "commands.log").read_text()


def test_runner_continuous_output_cannot_escape_deadline(tmp_path):
    run = mixed.Runner(tmp_path)
    with pytest.raises(RuntimeError, match="deadline"):
        run.run(sys.executable, "-c", "import os;\nwhile True: os.write(1,b'x'*4096)", timeout=.05)
    run.log.close()


def test_effective_memory_uses_ancestor_minimum():
    assert mixed.finite_memory({"limits": [{"memory.max": "max"}, {"memory.max": "1024"},
                                          {"memory.max": "2048"}]}) == 1024
    with pytest.raises(RuntimeError):
        mixed.finite_memory({"limits": [{"memory.max": "max"}]})


def test_heartbeat_requires_actual_progress():
    heartbeats = mixed.Heartbeats(123)
    heartbeats.samples = [{"heartbeat": 1, "age_seconds": .1, "monitor_monotonic": 1,
                          "monitor_age_seconds": .1}] * 4
    with pytest.raises(RuntimeError, match="did not advance"):
        heartbeats.metrics()
    heartbeats.samples = [{"heartbeat": n, "age_seconds": .1, "monitor_monotonic": n,
                          "monitor_age_seconds": .1} for n in range(4)]
    assert heartbeats.metrics()[1]["value"] == 3
    heartbeats.errors.append("fault")
    with pytest.raises(RuntimeError, match="fault"):
        heartbeats.metrics()


@pytest.mark.parametrize("state,stamp,valid", [("HEALTHY", 19, True), ("HEALTHY", 1, False),
                                               ("FAULT_LATCHED", 19, False), ("HEALTHY", 25, False)])
def test_monitor_synchronous_freshness(monkeypatch, state, stamp, valid):
    monkeypatch.setattr(mixed.Path, "read_text", lambda self: json.dumps({"state": state, "monotonic": stamp}))
    if valid:
        assert mixed.healthy_monitor(20)[1] == 1
    else:
        with pytest.raises(RuntimeError, match="unhealthy or stale"):
            mixed.healthy_monitor(20)


def test_monitor_stale_healthy_string_does_not_pass():
    heartbeats = mixed.Heartbeats(123)
    heartbeats.samples = [{"heartbeat": n, "age_seconds": .1, "monitor_monotonic": 1,
                          "monitor_age_seconds": n} for n in range(4)]
    with pytest.raises(RuntimeError, match="monitor timestamp did not advance"):
        heartbeats.metrics()


class FakeSampler:
    def __init__(self, pid):
        self.samples = [{"heartbeat": n} for n in range(4)]
        self.errors = []

    def start(self):
        pass

    def stop(self):
        pass

    def wait_for_monitor_update(self):
        pass

    def metrics(self):
        return [{"name": "adas_samples", "value": 4, "unit": "count"}]


class FakeRunner:
    def __init__(self, fail_load=False):
        self.calls = []
        self.fail_load = fail_load
        self.inspect_count = 0

    def qm(self, *args, **kwargs):
        self.calls.append(args)
        if args[0] == "systemd-run" and self.fail_load:
            raise RuntimeError("load submission timeout")
        if args[:2] == ("systemctl", "show"):
            if "ControlGroup" in args:
                return "/system.slice/test.service"
            return "1000000"
        if args[0] == "cat":
            return "2-3"
        if args[:2] == ("systemctl", "is-active"):
            return "inactive"
        if args[:2] == ("podman", "inspect"):
            self.inspect_count += 1
            return ("a" if self.inspect_count == 1 else "b") * 64
        return ""


@pytest.fixture
def mock_guest(monkeypatch):
    monkeypatch.setattr(mixed, "placement", lambda run: {"adas": {"pid": 123}})
    monkeypatch.setattr(mixed, "Heartbeats", FakeSampler)
    monkeypatch.setattr(mixed.time, "sleep", lambda seconds: None)


def test_mc01_persists_observations(mock_guest, tmp_path):
    result = mixed.scenario("MC01", FakeRunner(), tmp_path)
    assert result["status"] == "PASS"
    saved = json.loads((tmp_path / "MC01.json").read_text())
    assert len(saved["observations"]["heartbeat_samples"]) == 4


@pytest.mark.parametrize("fail", [False, True])
def test_load_cleanup_even_ambiguous_submission(mock_guest, tmp_path, fail):
    run = FakeRunner(fail_load=fail)
    result = mixed.scenario("MC02", run, tmp_path)
    assert result["status"] == ("FAIL" if fail else "PASS")
    submission = next(call for call in run.calls if call[0] == "systemd-run")
    unit = submission[2]
    assert unit.startswith("apollo-mc-load-")
    assert ("systemctl", "stop", unit) in run.calls
    assert "--property=RuntimeMaxSec=30" in submission
    assert result["observations"]["load_cleanup"] == "PASS"


def test_qm_replacement_keeps_adas_samples_and_restores_service(mock_guest, tmp_path):
    run = FakeRunner()
    result = mixed.scenario("MC03", run, tmp_path)
    assert result["status"] == "PASS"
    assert result["observations"]["old_container_id"] != result["observations"]["new_container_id"]
    assert ("systemctl", "start", "apollo-qm-container") in run.calls
    assert result["observations"]["qm_cleanup"] == "PASS"


def test_precondition_failure_never_mutates(monkeypatch, tmp_path):
    def fail(run):
        raise RuntimeError("unhealthy precondition")
    monkeypatch.setattr(mixed, "placement", fail)
    run = FakeRunner()
    result = mixed.scenario("MC03", run, tmp_path)
    assert result["status"] == "FAIL" and not run.calls
    assert (tmp_path / "MC03.json").exists()


def test_adas_restart_fails(monkeypatch, mock_guest, tmp_path):
    values = iter([{"adas": {"pid": 1}}, {"adas": {"pid": 2}}])
    monkeypatch.setattr(mixed, "placement", lambda run: next(values))
    result = mixed.scenario("MC01", FakeRunner(), tmp_path)
    assert result["status"] == "FAIL"
    assert "ADAS restarted" in result["reason"]


def test_failed_owned_load_is_reset_only_by_uuid(mock_guest, tmp_path):
    class FailedLoad(FakeRunner):
        def qm(self, *args, **kwargs):
            value = super().qm(*args, **kwargs)
            return "failed" if args[:2] == ("systemctl", "is-active") else value
    run = FailedLoad()
    result = mixed.scenario("MC02", run, tmp_path)
    resets = [call for call in run.calls if call[:2] == ("systemctl", "reset-failed")]
    assert len(resets) == 1 and resets[0][2].startswith("apollo-mc-load-")
    assert result["observations"]["load_cleanup"] == "PASS"
