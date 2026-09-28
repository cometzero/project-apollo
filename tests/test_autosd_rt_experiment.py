"""Keep measurement validity, injected detections and latency qualification separate."""
import importlib.util
from contextlib import contextmanager
import json
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rt_experiment", ROOT / "autosd/customization/rt/experiment.py")
rt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt)


def test_cyclictest_zero_exit_requires_real_samples(tmp_path):
    path = tmp_path / "cyclic.json"
    assert rt.cyclic_result({"returncode": 0}, path, 1000)["status"] == "FAIL"
    path.write_text(json.dumps({"thread": {"0": {"cycles": 0, "min": 0, "max": 0}}}))
    assert rt.cyclic_result({"returncode": 0}, path, 1000)["status"] == "FAIL"
    path.write_text(json.dumps({"thread": {"0": {"cycles": 10, "min": 10, "max": 1500}}}))
    result = rt.cyclic_result({"returncode": 0}, path, 1000)
    assert result["status"] == "PASS" and result["latency_status"] == "EXCEEDED"
    assert rt.cyclic_result({"returncode": 1}, path, 1000)["status"] == "FAIL"


def test_measurement_is_not_a_budget_pass():
    value = {"completed": True, "count": 10, "threshold_exceedances": 2}
    assert rt.classify({"returncode": 0}, value) == "EXCEEDED"
    value.update(synthetic=True)
    assert rt.classify({"returncode": 0}, value, synthetic=True) == "DETECTION_PASS"
    assert rt.classify({"returncode": 1}, value) == "ERROR"
    assert rt.classify({"returncode": 0}, {}) == "ERROR"
    value.update(threshold_exceedances=0)
    assert rt.classify({"returncode": 0}, value, synthetic=True) == "ERROR"
    assert rt.classify({"returncode": 0}, value) == "WITHIN_OBSERVED_THRESHOLD"


def test_platform_observation_defaults_are_not_universal_budget():
    assert rt.default_threshold("tcg") == 5000
    assert rt.default_threshold("hardware") == 1000
    assert rt.default_threshold("qbox") == 1000


def test_baseline_and_synthetic_do_not_fail_rt_observation():
    report = {"cases": [{"evaluation_role": "baseline", "latency_status": "EXCEEDED"}]}
    assert rt.aggregate_latency(report) == "BASELINE_OBSERVATION"
    report["cases"].append({"evaluation_role": "detection", "latency_status": "DETECTION_PASS"})
    report["cases"].append({"evaluation_role": "rt_observation", "latency_status": "WITHIN_OBSERVED_THRESHOLD"})
    assert rt.aggregate_latency(report) == "WITHIN_OBSERVED_THRESHOLD"
    report["cases"][-1]["latency_status"] = "EXCEEDED"
    assert rt.aggregate_latency(report) == "EXCEEDED"
    report["cases"] = []
    report["cyclictest"] = {"latency_status": "EXCEEDED"}
    assert rt.aggregate_latency(report) == "EXCEEDED"


def test_command_bounds_and_missing_binary():
    assert rt.command(["no-such-apollo-rt-command"])["returncode"] == 127
    assert rt.command(["sleep", "5"], timeout=.01)["returncode"] == 124


def test_fifo_requests_mlock_and_exclusive_output(tmp_path):
    args = SimpleNamespace(probe=Path("/probe"), cpu=1, duration=2, period_us=1000,
                           threshold_us=100, out=tmp_path)
    argv = rt.probe_command(args, "case", 50)
    assert "--mlock" in argv
    assert argv[argv.index("--output") + 1] == str(tmp_path / "case.json")
    assert "--mlock" not in rt.probe_command(args, "case", 0)


def test_empty_probe_result_is_an_error(tmp_path, monkeypatch):
    args = SimpleNamespace(probe=Path("/probe"), cpu=1, duration=2, period_us=1000,
                           threshold_us=100, out=tmp_path)
    (tmp_path / "setup-failed.json").touch()
    monkeypatch.setattr(rt, "command", lambda *a, **kw: {"returncode": 1, "output": "mlock failed"})
    assert rt.run_probe(args, "setup-failed", 50)["latency_status"] == "ERROR"


def test_cleanup_attempts_all_owned_units_after_failure(tmp_path, monkeypatch):
    args = SimpleNamespace(probe=Path("/probe"), cpu=1, qm_cpus=[2, 3], duration=1, out=tmp_path)
    stopped = []
    active_calls = 0
    def fake(argv, **kwargs):
        nonlocal active_calls
        if "stop" in argv:
            stopped.append(argv[-1])
        output = ""
        if "is-active" in argv:
            active_calls += 1
            output = "active" if active_calls <= 3 else "inactive"
        return {"returncode": 0, "output": output, "command": argv}
    monkeypatch.setattr(rt, "command", fake)
    with pytest.raises(RuntimeError, match="cleanup not confirmed"):
        with rt.loads(args, qm=True):
            raise RuntimeError("measurement failed")
    assert len(stopped) == 2 and len(set(stopped)) == 2


@pytest.mark.parametrize("selection", [f"R{i:02d}" for i in range(1, 6)])
def test_selected_rt_case_has_no_implicit_measurements(tmp_path, monkeypatch, selection, capsys):
    args = SimpleNamespace(case=selection, priority=50, threshold_us=1000, external_tools=True)
    calls, load_calls = [], []
    def probe(args, case, priority, inject=0):
        calls.append((case, priority, inject))
        return {"id": case, "latency_status": "WITHIN_OBSERVED_THRESHOLD"}
    @contextmanager
    def load(args, qm):
        load_calls.append(qm)
        yield
    monkeypatch.setattr(rt, "run_probe", probe)
    monkeypatch.setattr(rt, "loads", load)
    report = {"cases": []}
    rt.run_cases(args, report)
    assert len(calls) == 1 and calls[0][0].startswith(selection + "-")
    assert calls[0][1] == (0 if selection == "R01" else 50)
    assert load_calls == ([True] if selection == "R03" else [False] if selection == "R04" else [])
    assert "cyclictest" not in report
    events = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [event["event"] for event in events] == ["case-start", "case-complete"]


def test_r06_forces_only_cyclictest(tmp_path, monkeypatch):
    args = SimpleNamespace(case="R06", priority=50, threshold_us=1000, external_tools=False,
                           cpu=1, duration=1, period_us=1000, out=tmp_path)
    calls = []
    def command(argv, timeout):
        calls.append(argv)
        (tmp_path / "cyclictest.json").write_text(json.dumps({"thread": {"0": {"cycles": 10, "min": 1, "max": 10}}}))
        return {"returncode": 0}
    monkeypatch.setattr(rt.shutil, "which", lambda name: "/bin/" + name)
    monkeypatch.setattr(rt, "command", command)
    monkeypatch.setattr(rt, "run_probe", lambda *a: pytest.fail("R06 must not execute other cases"))
    report = {"cases": []}
    rt.run_cases(args, report)
    assert report["cases"] == [] and report["cyclictest"]["status"] == "PASS"
    assert len(calls) == 1 and calls[0][0] == "cyclictest" and "-m" in calls[0]


def test_default_full_rt_order_is_preserved(monkeypatch):
    args = SimpleNamespace(case="all", priority=50, threshold_us=1000, external_tools=False)
    calls = []
    def probe(args, case, priority, inject=0):
        calls.append(case)
        return {"id": case, "latency_status": "WITHIN_OBSERVED_THRESHOLD"}
    @contextmanager
    def load(args, qm):
        yield
    monkeypatch.setattr(rt, "run_probe", probe)
    monkeypatch.setattr(rt, "loads", load)
    report = {"cases": []}
    rt.run_cases(args, report)
    assert calls == ["R01-other", "R02-fifo", "R03-qm-load", "R04-shared-cpu", "R05-injected"]
    assert "cyclictest" not in report


def test_r06_main_needs_no_probe_and_checks_health_twice(tmp_path, monkeypatch):
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", ["rt", "--allow-private-guest", "--platform", "tcg",
        "--case", "R06", "--probe", str(tmp_path / "missing-probe"), "--out", str(out)])
    monkeypatch.setattr(rt.os, "geteuid", lambda: 0)
    monkeypatch.setattr(rt.platform, "machine", lambda: "aarch64")
    monkeypatch.setattr(rt.os, "sched_getaffinity", lambda pid: {0, 1, 2, 3})
    monkeypatch.setattr(rt, "read", lambda path: "Automotive" if path == "/etc/os-release" else "1")
    monkeypatch.setattr(rt, "snapshot", lambda: {})
    monkeypatch.setattr(rt.signal, "signal", lambda *a: None)
    commands = []
    def command(argv, **kwargs):
        commands.append(argv)
        return {"returncode": 0}
    def run_cases(args, report):
        assert args.case == "R06"
        report["cyclictest"] = {"status": "PASS", "latency_status": "WITHIN_OBSERVED_THRESHOLD"}
    monkeypatch.setattr(rt, "command", command)
    monkeypatch.setattr(rt, "run_cases", run_cases)
    assert rt.main() == 0
    report = json.loads((out / "results.json").read_text())
    assert "probe_sha256" not in report
    assert len(commands) == 2 and all(argv[0] == "bash" for argv in commands)
