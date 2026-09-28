"""Monitor scenario opt-in, lifecycle, and evidence routing boundaries."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

PATH = Path(__file__).resolve().parents[1] / "scripts/autosd_dashboard/server.py"
spec = importlib.util.spec_from_file_location("monitor_dashboard_server", PATH)
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


@pytest.mark.parametrize("backend", ["qemu", "qbox", "qbox-full"])
def test_launch_diagnostics_are_opt_in(tmp_path, backend):
    app = server.Dashboard(tmp_path, Path("manifest"), Path("disk"), backend=backend)
    assert "--qmp" not in app.boot_command(tmp_path)
    assert "--runtime-injection" not in app.boot_command(tmp_path)
    app.qbox_diagnostics, app.runtime_injection = True, True
    command = app.boot_command(tmp_path)
    assert ("--qmp" in command) == (backend != "qemu")
    assert ("--runtime-injection" in command) == (backend == "qbox-full")


@pytest.mark.parametrize("backend,opt_in", [("qemu", True), ("qbox", True), ("qbox-full", False)])
def test_start_and_catalog_reject_without_full_opt_in(tmp_path, monkeypatch, backend, opt_in):
    app = server.Dashboard(tmp_path, Path("manifest"), Path("disk"), allow=True,
                           backend=backend, runtime_injection=opt_in)
    monkeypatch.setattr(app, "running", lambda: True)
    monkeypatch.setattr(app, "domain_boot", lambda: {"status": "PASS"})
    item = next(row for row in app.state()["catalog"] if row["action"] == "monitor-mhu")
    assert not item["enabled"]
    assert item["unsupported_reason"]
    with pytest.raises(ValueError, match="requires QBox full"):
        app.start("monitor-mhu", confirmed=True)


def test_disruptive_confirmation_required(tmp_path):
    app = server.Dashboard(tmp_path, Path("manifest"), Path("disk"), allow=True,
                           backend="qbox-full", runtime_injection=True)
    with pytest.raises(ValueError, match="confirm_disruptive"):
        app.start("monitor-mhu")
    assert "monitor-mhu" in app.simulator_barriers


@pytest.mark.parametrize("status,recovered", [("UNKNOWN", False), ("UNCONFIRMED", True), ("PASS", True)])
def test_scenario_status_and_boot_lifecycle(tmp_path, monkeypatch, status, recovered):
    import monitor_scenarios
    app = server.Dashboard(tmp_path, Path("manifest"), Path("disk"), allow=True,
                           backend="qbox-full", runtime_injection=True)
    job = {"id": "a" * 32, "action": "monitor-mhu", "evidence_path": str(tmp_path),
           "feature_session": "test", "status": "RUNNING"}
    app.jobs, app.active, app.feature_session = [job], job["id"], "test"
    result = {"status": status, "after_boot_id": "new" if recovered else None,
              "recovery_required": not recovered}
    monkeypatch.setattr(monitor_scenarios, "run", lambda *args: result)
    transitions = []
    monkeypatch.setattr(app, "boot_ready", lambda *args: transitions.append(("ready", args)))
    monkeypatch.setattr(app, "boot_failed", lambda *args: transitions.append(("failed", args)))
    app.execute(job)
    assert job["status"] == status
    assert transitions[0][0] == ("ready" if recovered else "failed")
    assert app.active is None


def test_root_scenario_artifact(tmp_path):
    app = server.Dashboard(tmp_path)
    app.jobs = [{"id": "test", "action": "monitor-mhu", "evidence_path": str(tmp_path)}]
    result = tmp_path / "scenarios.json"
    result.write_text(json.dumps({"status": "UNCONFIRMED"}))
    assert app.artifact("test", "scenarios.json") == result


def test_pause_qualification_is_scoped_to_current_run(tmp_path):
    app = server.Dashboard(tmp_path, backend="qbox-full")
    assert app.unsupported_control("pause")
    app.vm_job = "old"
    app.qbox_pause_run = "old"
    assert app.unsupported_control("pause") is None
    app.vm_job = "new"
    assert app.unsupported_control("pause")
    assert "monitor-qualify" in app.simulator_barriers


@pytest.mark.parametrize("enabled", [False, True])
def test_qmp_http_opt_in_gate(tmp_path, enabled):
    app = server.Dashboard(tmp_path, qbox_diagnostics=enabled)
    calls, replies = [], []
    app.simulator.diagnostics = lambda domain, command: calls.append((domain, command)) or {"status": "PASS"}
    handler = SimpleNamespace(path="/api/simulator/qmp?domain=si-cl1&command=query-status",
                              server=SimpleNamespace(app=app), safe_request=lambda: True,
                              send=lambda code, data: replies.append((code, data)))
    server.Handler.do_GET(handler)
    assert replies[0][0] == (200 if enabled else 503)
    assert calls == ([("si-cl1", "query-status")] if enabled else [])


def test_unknown_control_allows_only_explicit_owned_recovery(tmp_path, monkeypatch):
    import qbox_control
    app = server.Dashboard(tmp_path, backend="qbox-full")
    app.vm_job, app.qbox_pause_run = "run", "run"
    app.simulator.collector = SimpleNamespace(run_id="run")
    monkeypatch.setattr(app, "running", lambda: True)
    calls = []
    def control(collector, action):
        calls.append(action)
        return {"status": "UNKNOWN" if action == "pause" else "PASS"}
    monkeypatch.setattr(qbox_control, "control", control)
    import io
    assert app.control_monitor("pause", io.BytesIO())["status"] == "UNKNOWN"
    assert app.vm_paused
    assert app.qbox_pause_run is None
    assert app.qbox_pause_unknown_run == "run"
    assert app.unsupported_control("resume") is None
    assert app.unsupported_control("pause")
    assert calls == ["pause"]
    assert app.control_monitor("resume", io.BytesIO())["status"] == "PASS"
    assert not app.vm_paused
    assert app.qbox_pause_unknown_run is None
    assert app.qbox_pause_run is None
    assert app.unsupported_control("pause")
    assert calls == ["pause", "resume"]


def test_unknown_recovery_cannot_control_another_run(tmp_path, monkeypatch):
    app = server.Dashboard(tmp_path, backend="qbox-full")
    app.vm_job, app.qbox_pause_unknown_run = "new", "old"
    assert app.unsupported_control("resume")
    app.qbox_pause_unknown_run = "new"
    app.simulator.collector = SimpleNamespace(run_id="old")
    monkeypatch.setattr(app, "running", lambda: True)
    import io
    with pytest.raises(ValueError, match="Current owned"):
        app.control_monitor("resume", io.BytesIO())


def test_qualification_artifact(tmp_path):
    app = server.Dashboard(tmp_path)
    app.jobs = [{"id": "test", "action": "monitor-qualify", "evidence_path": str(tmp_path)}]
    path = tmp_path / "qualification.json"
    path.write_text('{"status":"UNKNOWN"}')
    assert app.artifact("test", "qualification.json") == path


def test_unknown_qualification_exposes_recovery_resume(tmp_path, monkeypatch):
    import qbox_control
    app = server.Dashboard(tmp_path, backend="qbox-full")
    app.vm_job = "run"
    job = {"id": "b" * 32, "action": "monitor-qualify", "evidence_path": str(tmp_path),
           "status": "RUNNING"}
    app.jobs, app.active = [job], job["id"]
    monkeypatch.setattr(qbox_control, "run", lambda *args: {"status": "UNKNOWN", "pause_state_unknown": True})
    app.execute(job)
    assert job["status"] == "UNKNOWN"
    assert app.vm_paused
    assert app.qbox_pause_unknown_run == "run"
    assert app.unsupported_control("resume") is None
