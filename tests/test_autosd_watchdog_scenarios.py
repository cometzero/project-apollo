"""No hardware access: watchdog orchestration evidence and authorization contracts."""
import importlib.util
import io
import json
from pathlib import Path
import sys
import threading
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/autosd_dashboard"))
import watchdog_scenarios as wd

spec = importlib.util.spec_from_file_location("watchdog_dashboard_server", ROOT / "scripts/autosd_dashboard/server.py")
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


def test_ordered_trace_requires_rearm():
    platform = "\n".join("platform.ap_watchdog_0 ws0=%s ws1=%s sc_time=%s ns" % row
                         for row in ((1, 0, 10), (1, 1, 20), (0, 0, 23)))
    si0 = "AP watchdog IRQ 321 snapshot: enabled=1 pending=0 recovery=0\nWatchdog rearm attempt=1 before=0 after=0 status=0"
    assert wd.trace_evidence(platform, si0)["status"] == "PASS"
    assert wd.trace_evidence(platform, "")["status"] == "FAIL"
    assert wd.trace_evidence("\n".join(reversed(platform.splitlines())), si0)["status"] == "FAIL"
    assert wd.trace_evidence(platform.replace("ap_watchdog_0", "ap_watchdog_1"), si0)["status"] == "FAIL"


def test_fresh_offsets_and_truncation(tmp_path):
    path = tmp_path / "trace"
    path.write_text("old evidence\n")
    offset = path.stat().st_size
    with path.open("a") as stream:
        stream.write("fresh\n")
    assert wd.read_since(path, offset) == "fresh\n"
    path.write_text("short")
    with pytest.raises(RuntimeError, match="truncated"):
        wd.read_since(path, offset)


@pytest.mark.parametrize("backend", ["qemu", "qbox"])
def test_hardware_expiry_rejected_outside_full(tmp_path, backend):
    app = server.Dashboard(tmp_path, "manifest", "disk", allow=True, backend=backend)
    with pytest.raises(ValueError, match="only on QBox full"):
        app.start("watchdog-wd04", confirmed=True)
    child = next(c for p in app.state()["catalog"] for c in p["children"] if c["code"] == "WD04")
    assert not child["enabled"] and child["unsupported_reason"]


def test_expiry_requires_confirmation(tmp_path):
    app = server.Dashboard(tmp_path, "manifest", "disk", allow=True, backend="qbox-full")
    with pytest.raises(ValueError, match="confirm"):
        app.start("watchdog-wd04")


def test_safe_group_never_expires(tmp_path, monkeypatch):
    commands = []
    def guest(app, directory, log, command, uploads=(), downloads=(), timeout=180):
        directory.mkdir()
        (directory / "scenario.json").write_text('{"status":"PASS"}')
        (directory / "events.jsonl").write_text('{"event":"keepalive","timeleft_s":20}\n')
        commands.append(command)
        return 0
    monkeypatch.setattr(wd, "run_command", guest)
    app = SimpleNamespace(persist=lambda job: None)
    job = {"action": "watchdog", "id": "a" * 32, "evidence_path": str(tmp_path)}
    result = wd.run(app, job, io.BytesIO())
    assert result["status"] == "PASS"
    assert [r["id"] for r in result["scenarios"]] == ["WD01", "WD02", "WD03"]
    assert not any("expiry" in command or "acknowledge-reset" in command for command in commands)
    assert "--duration 30" in commands[1]
    assert "--timeout 20" in commands[1]


def test_missing_evidence_cannot_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(wd, "run_command", lambda *a, **kw: 0)
    result = wd.run(SimpleNamespace(persist=lambda j: None),
                    {"action": "watchdog-wd01", "id": "b", "evidence_path": str(tmp_path)}, io.BytesIO())
    assert result["status"] == "FAIL"


def test_mixed_fixed_cases_and_archives(tmp_path):
    app = server.Dashboard(tmp_path, backend="qbox-full")
    for case in ("mc01", "mc02", "mc03"):
        action = "mixed-criticality-" + case
        argv = app.guest_command({"id": "abc", "action": action, "evidence_path": str(tmp_path)})
        command = argv[argv.index("--command") + 1]
        assert "--case " + case.upper() in command
        assert "--allow-disruptive-demo" in command
        assert "/results.json:scenarios.json" in " ".join(argv)
        assert "evidence.tar.gz" in str(argv)
        assert action in server.MEASUREMENT_ACTIONS


def test_full_boot_enables_reset_trace(tmp_path):
    app = server.Dashboard(tmp_path, backend="qbox-full")
    assert "--reset-trace" in app.boot_command(tmp_path)


def test_expiry_owns_feature_readiness(tmp_path):
    app = server.Dashboard(tmp_path)
    app.feature_session = "new"
    app.auto_health_pending = True
    app.active = "expiry"
    app.jobs = [{"id": "expiry", "action": "watchdog-wd04"}]
    app.feature_boot = {"status": "RUNNING"}
    app.advance_features("new", {"status": "ONLINE", "boot_id": "old"})
    assert app.feature_boot["status"] == "RUNNING"


@pytest.mark.parametrize("broken", [None, "trace", "process", "si_epoch", "health", "same_boot"])
def test_expiry_needs_independent_recovery_evidence(tmp_path, monkeypatch, broken):
    vm = tmp_path / "boot/vm"
    (vm / "full-system").mkdir(parents=True)
    (vm / "launch.json").write_text('{"environment":{"QBOX_APOLLO_RESET_TRACE":"1"}}')
    (vm / "linux-uart.log").write_text("old console")
    platform = vm / "full-system/qbox-platform.log"
    si = vm / "si-cl0-uart.log"
    platform.write_text("old trace\n")
    si.write_text("old firmware\n")
    domain = lambda epoch, si_epoch=1: {"status": "PASS", "domains": [
        {"id": name, "boot_epoch": epoch if name == "ap" else si_epoch}
        for name in ("rse", "si-cl0", "si-cl1", "ap")]}
    states = [domain(1), domain(2, 2 if broken == "si_epoch" else 1)]
    snapshots = iter([{"status": "ONLINE", "boot_id": "old"},
                      {"status": "ONLINE", "boot_id": "old" if broken == "same_boot" else "new"}])
    monkeypatch.setattr(wd, "boot_snapshot", lambda *a: next(snapshots))
    process = iter([{"123": {"starttime": "1"}}, {"123": {"starttime": "2" if broken == "process" else "1"}}])
    monkeypatch.setattr(wd, "descendants", lambda pid: next(process))
    app = SimpleNamespace(backend="qbox-full", ssh_port=2244, vm_job="boot", boot_timeout=10,
                          jobs=[{"id": "boot", "evidence_path": str(tmp_path / "boot")}],
                          domain_boot=lambda: states.pop(0), vm_process=SimpleNamespace(pid=123),
                          persist=lambda job: None, lock=threading.RLock(), monitoring={})
    app.running = lambda: True
    app.reboot_verified = lambda before, after, domains: after.get("boot_id") != before["boot_id"]
    # One recovery poll, then deadline. Same boot must remain a failure.
    stamps = iter([0, 1, 20])
    monkeypatch.setattr(wd.time, "monotonic", lambda: next(stamps))
    monkeypatch.setattr(wd.time, "sleep", lambda seconds: None)
    def command(app, directory, log, command, uploads=(), downloads=(), timeout=180):
        if "expiry" in command:
            if broken != "trace":
                with platform.open("a") as stream:
                    stream.write("platform.ap_watchdog_0 ws0=1 ws1=0 sc_time=10 ns\n"
                                 "platform.ap_watchdog_0 ws0=1 ws1=1 sc_time=20 ns\n"
                                 "platform.ap_watchdog_0 ws0=0 ws1=0 sc_time=23 ns\n")
            with si.open("a") as stream:
                stream.write("AP watchdog IRQ 321 snapshot: enabled=1 pending=0 recovery=0\n"
                             "Watchdog rearm attempt=1 before=0 after=0 status=0\n")
            return 124  # This alone must never qualify a hardware reset.
        return 1 if directory.name == "recovery" and broken == "health" else 0
    monkeypatch.setattr(wd, "run_command", command)
    out = tmp_path / "case"
    out.mkdir()
    result = wd.expiry(app, {"id": "new"}, io.BytesIO(), out, "/var/tmp/private")
    assert result["status"] == ("PASS" if broken is None else "FAIL")
    assert result["expiry_ssh_returncode"] == 124
    assert "old trace" not in (out / "watchdog-trace.log").read_text()


def test_watchdog_artifact_route(tmp_path):
    app = server.Dashboard(tmp_path)
    (tmp_path / "scenarios.json").write_text('{}')
    app.jobs = [{"id": "owned", "action": "watchdog-wd01", "evidence_path": str(tmp_path)}]
    assert app.artifact("owned", "scenarios.json") == tmp_path / "scenarios.json"
