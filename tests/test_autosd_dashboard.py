"""Dashboard safety boundaries and evidence contracts; no real VM required."""
import importlib.util
import base64
import json
from pathlib import Path
import threading
import urllib.error
import urllib.request

import pytest

PATH = Path(__file__).resolve().parents[1] / "scripts/autosd_dashboard/server.py"
spec = importlib.util.spec_from_file_location("autosd_dashboard_server", PATH)
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


@pytest.fixture
def app(tmp_path):
    return server.Dashboard(tmp_path)


def test_default_read_only(app):
    state = app.state()
    assert not state["capabilities"]["execution_enabled"]
    assert not any(item["enabled"] for item in state["catalog"])
    assert not any(item["enabled"] for item in state["system_controls"])
    assert state["monitoring"]["status"] == "OFFLINE"
    assert state["evidence"] == []
    with pytest.raises(ValueError, match="disabled"):
        app.start("boot")


def test_backend_default_and_validation(tmp_path):
    app = server.Dashboard(tmp_path)
    assert app.state()["vm"]["backend"] == "qemu"
    assert app.state()["capabilities"]["platform"] == "QEMU TCG"
    assert app.boot_timeout == 240
    with pytest.raises(ValueError, match="Unsupported backend"):
        server.Dashboard(tmp_path, backend="qbox; rm -rf")


@pytest.mark.parametrize("backend", ["qemu", "qbox", "qbox-full"])
def test_boot_backend_argv(tmp_path, backend):
    app = server.Dashboard(tmp_path, Path("manifest with spaces"), Path("disk with spaces"),
                           2255, True, backend=backend)
    argv = app.boot_command(tmp_path)
    assert argv[0] == str(server.ROOT / ("run_qbox_autosd.sh" if backend == "qbox-full" else "run_" + backend + "_linux.sh"))
    assert argv[argv.index("--autosd") + 1] == "manifest with spaces"
    assert argv[argv.index("--rootfs") + 1] == "disk with spaces"
    assert "--headless" in argv
    if backend != "qemu":
        assert argv[-2:] == ["--ssh-port", "2255"]
        assert "--netdev" not in argv  # launcher constructs fixed loopback forwarding
    else:
        assert argv[-2:] == ["--netdev", "user,id=net0,hostfwd=tcp:127.0.0.1:2255-:22"]


@pytest.mark.parametrize("action", ["pause", "resume", "reboot"])
def test_qbox_unqualified_controls_rejected(tmp_path, monkeypatch, action):
    app = server.Dashboard(tmp_path, Path("manifest"), Path("disk"), allow=True, backend="qbox")
    monkeypatch.setattr(app, "running", lambda: True)
    state = app.state()
    control = next(c for c in state["system_controls"] if c["action"] == action)
    assert not control["enabled"]
    assert "not qualified" in control["unsupported_reason"]
    assert state["capabilities"]["platform"] == "QBox AP direct"
    assert app.boot_timeout == 600
    with pytest.raises(ValueError, match="not qualified"):
        app.start(action, confirmed=True)
    assert app.jobs == []
    assert app.feature_session is None


@pytest.mark.parametrize("action", ["rt", "rt-r02", "timerlat", "osnoise"])
@pytest.mark.parametrize("backend,platform", [("qemu", "tcg"), ("qbox", "qbox"), ("qbox-full", "qbox")])
def test_rt_platform_tracks_backend(tmp_path, action, backend, platform):
    app = server.Dashboard(tmp_path, backend=backend)
    args = app.guest_command({"action": action, "id": "a" * 32, "evidence_path": str(tmp_path)})
    command = args[args.index("--command") + 1]
    assert "--platform " + platform + " " in command
    assert "--threshold-us 5000" in command


def test_qbox_boot_job_tags_backend_and_bounded_deadline(tmp_path, monkeypatch):
    app = server.Dashboard(tmp_path, Path("manifest"), Path("disk"), 0, True, backend="qbox")
    monkeypatch.setattr(server.threading.Thread, "start", lambda _: None)
    monkeypatch.setattr(server.time, "monotonic", lambda: 10)
    job = app.start("boot")
    assert job["backend"] == "qbox"
    assert app.boot_deadline == 610
    assert "QBox AP direct" in app.state()["catalog"][0]["description"]
    assert all("TCG" not in row["description"] for row in app.state()["catalog"])


@pytest.mark.parametrize("action,timeout", [("health", 360), ("rt", 600), ("rt-r06", 600),
                                           ("timerlat", 360), ("osnoise", 360),
                                           ("automotive", 1500), ("automotive-s04", 600),
                                           ("shutdown", 240)])
def test_qbox_host_operation_timeout(tmp_path, action, timeout):
    app = server.Dashboard(tmp_path, backend="qbox")
    assert app.operation_timeout(action) == timeout
    argv = app.guest_command({"id": "a" * 32, "action": action, "evidence_path": str(tmp_path)})
    assert argv[argv.index("--timeout") + 1] == str(timeout)
    assert server.Dashboard(tmp_path).operation_timeout(action) == server.guest_timeout(action)


def test_backend_switch_preserves_disk_and_history_but_resets_current_state(app):
    app.rootfs = Path("preserved-runtime.wic")
    app.jobs = [{"id": "old", "backend": "qbox", "status": "PASS"}]
    app.backend = "qbox"
    app.feature_session = app.log_session = app.vm_job = "old"
    app.feature_boot = {"status": "PASS"}
    app.feature_health = {"status": "PASS"}
    app.history = [{"cpus": [1]}]
    app.monitoring = {"cpus": [1]}
    app.service_log_cache[("old", "root")] = (0, {"text": "old"})
    result = app.select_backend("qbox-full")
    assert result["backend"] == "qbox-full"
    assert app.boot_timeout == 900
    assert app.rootfs == Path("preserved-runtime.wic")
    assert app.jobs[0]["backend"] == "qbox"
    assert app.feature_session is app.log_session is app.vm_job is None
    assert app.feature_boot is app.feature_health is None
    assert app.history == [] and app.monitoring["cpus"] == []
    assert app.service_log_cache == {}
    state = app.state()
    assert state["backend_selection_enabled"]
    assert [row["id"] for row in state["backends"]] == ["qemu", "qbox", "qbox-full"]
    assert state["capabilities"]["platform"] == "QBox full system"


@pytest.mark.parametrize("busy", ["vm", "job", "health"])
def test_backend_switch_rejects_busy_state(app, monkeypatch, busy):
    monkeypatch.setattr(app, "running", lambda: busy == "vm")
    app.active = "active" if busy == "job" else None
    app.auto_health_pending = busy == "health"
    with pytest.raises(ValueError, match="Power off"):
        app.select_backend("qbox-full")
    assert app.backend == "qemu"
    assert not app.state()["backend_selection_enabled"]


@pytest.mark.parametrize("action", ["pause", "resume"])
def test_qbox_full_controls_unqualified(app, action):
    app.select_backend("qbox-full")
    assert "not qualified" in app.unsupported_control(action)
    with pytest.raises(ValueError, match="not qualified"):
        app.start(action, confirmed=True)


def test_full_native_reboot_is_supported_but_not_pause(app):
    app.select_backend("qbox-full")
    assert app.unsupported_control("reboot") is None
    assert app.shutdown_wait_timeout() == 180
    assert "QBox Pause/Resume/Reboot" not in app.state()["capabilities"]["unsupported"]
    app.select_backend("qbox")
    assert app.unsupported_control("reboot")
    assert app.shutdown_wait_timeout() == 60


@pytest.mark.parametrize("new_id,epoch,provision,status,expected", [
    ("old", 2, 2, "PASS", False),
    ("new", 1, 1, "PASS", False),
    ("new", 2, 1, "PASS", False),
    ("new", 2, 2, "RUNNING", False),
    ("new", 2, 2, "PASS", True),
])
def test_full_reboot_requires_new_boot_and_current_provision(full_app, tmp_path, new_id, epoch, provision, status, expected):
    rows = [{"id": name, "status": "PASS", "boot_epoch": epoch} for name in server.FULL_DOMAINS]
    (tmp_path / "vm/domains.json").write_text(json.dumps({"status": "PASS", "domains": rows,
        "provision": {"status": status, "boot_epoch": provision}}))
    before = {"status": "ONLINE", "boot_id": "old"}
    after = {"status": "ONLINE", "boot_id": new_id}
    previous = {"domains": [{"id": "ap", "boot_epoch": 1}]}
    assert full_app.reboot_verified(before, after, previous) is expected


def test_reboot_background_sample_cannot_complete_feature(full_app):
    full_app.jobs.append({"id": "reboot", "action": "reboot"})
    full_app.active = "reboot"
    full_app.advance_features("boot", {"status": "ONLINE", "boot_id": "unverified"})
    assert full_app.feature_boot["status"] == "RUNNING"


@pytest.fixture
def full_app(tmp_path, monkeypatch):
    app = server.Dashboard(tmp_path, Path("manifest"), Path("disk"), allow=True, backend="qbox-full")
    (tmp_path / "vm").mkdir()
    app.jobs = [{"id": "boot", "evidence_path": str(tmp_path), "backend": "qbox-full"}]
    app.vm_job = app.feature_session = app.log_session = "boot"
    app.feature_boot = {"status": "RUNNING"}
    app.feature_health = {"status": "QUEUED"}
    app.auto_health_pending = True
    monkeypatch.setattr(app, "running", lambda: True)
    monkeypatch.setattr(server.threading.Thread, "start", lambda _: None)
    return app


@pytest.mark.parametrize("mode", ["missing", "incomplete", "waiting", "fail", "pass"])
def test_full_boot_requires_all_domain_markers_and_ssh(full_app, tmp_path, mode):
    app = full_app
    rows = [{"id": name, "status": "PASS"} for name in server.FULL_DOMAINS]
    if mode == "incomplete":
        rows.pop()
    elif mode in ("waiting", "fail"):
        rows[1]["status"] = mode.upper()
    if mode != "missing":
        (tmp_path / "vm/domains.json").write_text(json.dumps({"status": "PASS", "domains": rows}))
    app.active = "hold-auto-health"
    app.advance_features("boot", {"status": "ONLINE", "boot_id": "guest-id"})
    expected = "PASS" if mode == "pass" else "FAIL" if mode == "fail" else "RUNNING"
    assert app.feature_boot["status"] == expected
    assert len(app.state()["domain_boot"]["domains"]) == 4


def test_full_domain_pass_without_ssh_does_not_complete_boot(full_app, tmp_path):
    (tmp_path / "vm/domains.json").write_text(json.dumps({"status": "PASS", "domains": [
        {"id": name, "status": "PASS"} for name in server.FULL_DOMAINS]}))
    full_app.advance_features("boot", None)
    assert full_app.feature_boot["status"] == "RUNNING"


def test_full_failed_domains_block_manual_scenarios(full_app):
    full_app.auto_health_pending = False
    with pytest.raises(ValueError, match="domain boot verification"):
        full_app.start("automotive-s01")


def test_full_domain_log_sources_bounded_and_whitelisted(full_app, tmp_path):
    (tmp_path / "vm/si-cl0-uart.log").write_text("SCP firmware boot\n")
    assert full_app.guest_log("si-cl0")["text"] == "SCP firmware boot\n"
    assert full_app.guest_log("si-cl0")["log_session"] == "boot"
    assert {"rse", "si-cl0", "si-cl1"} <= {row["id"] for row in full_app.state()["guest_log_sources"]}
    with pytest.raises(ValueError, match="Unknown"):
        full_app.guest_log("../../etc/passwd")
    full_app.backend = "qbox"
    with pytest.raises(ValueError, match="Unknown"):
        full_app.guest_log("si-cl0")


@pytest.fixture
def lifecycle_app(app, monkeypatch):
    app.allow, app.manifest, app.rootfs, app.ssh_port = True, Path("manifest"), Path("rootfs"), 0
    monkeypatch.setattr(server.threading.Thread, "start", lambda _: None)
    return app


@pytest.mark.parametrize("action", ["boot", "shutdown", "reboot"])
def test_feature_epoch_resets_on_accepted_control(lifecycle_app, monkeypatch, action):
    app = lifecycle_app
    monkeypatch.setattr(app, "running", lambda: action != "boot")
    app.feature_session = "old"
    app.jobs.append({"id": "old", "action": "automotive-s04", "status": "PASS", "feature_session": "old"})
    job = app.start(action, confirmed=True)
    state = app.state()
    assert state["feature_session"] == job["id"] == job["feature_session"]
    assert state["jobs"][0]["status"] == "PASS"  # retained as history
    if action == "shutdown":
        assert state["feature_boot"] is state["feature_health"] is None
        assert not app.auto_health_pending
    else:
        assert state["feature_boot"]["status"] == "RUNNING"
        assert state["feature_health"]["status"] == "QUEUED"


def test_boot_fresh_sample_schedules_health_once(lifecycle_app, monkeypatch):
    app = lifecycle_app
    boot = app.start("boot")
    monkeypatch.setattr(app, "running", lambda: True)
    app.active = None  # launcher ownership established
    app.monitoring = {"status": "ONLINE", "boot_id": "stale"}
    app.advance_features(boot["id"])
    assert app.feature_boot["status"] == "RUNNING"
    app.advance_features("old-epoch", {"status": "ONLINE", "boot_id": "old"})
    assert len(app.jobs) == 1
    with pytest.raises(ValueError, match="Automatic boot health"):
        app.start("automotive-s01")
    app.advance_features(boot["id"], {"status": "ONLINE", "boot_id": "fresh"})
    assert app.feature_boot["status"] == "PASS"
    health = app.jobs[-1]
    assert health["action"] == "health" and health["automatic"]
    assert health["feature_session"] == boot["id"]
    assert app.active == health["id"]
    app.advance_features(boot["id"], {"status": "ONLINE", "boot_id": "fresh"})
    assert len(app.jobs) == 2


def test_shutdown_cancels_pending_health(lifecycle_app, monkeypatch):
    app = lifecycle_app
    boot = app.start("boot")
    app.active = None
    monkeypatch.setattr(app, "running", lambda: True)
    app.start("shutdown", confirmed=True)
    app.advance_features(boot["id"], {"status": "ONLINE", "boot_id": "stale"})
    assert not app.auto_health_pending
    assert app.feature_boot is None
    assert all(job["action"] != "health" for job in app.jobs)


def test_rejected_control_preserves_feature_epoch(lifecycle_app, monkeypatch):
    app = lifecycle_app
    app.feature_session = "old"
    monkeypatch.setattr(app, "running", lambda: True)
    with pytest.raises(ValueError, match="confirm"):
        app.start("reboot")
    assert app.feature_session == "old"


def test_boot_exit_before_autohealth_cancels_queue(lifecycle_app, monkeypatch):
    from types import SimpleNamespace
    app = lifecycle_app
    started = app.start("boot")
    def exited():
        app.boot_ready(started["id"], "ready")
        return 1
    monkeypatch.setattr(server.subprocess, "Popen", lambda *a, **k: SimpleNamespace(wait=exited))
    app.execute(app.jobs[-1])
    assert app.feature_boot["status"] == "PASS"  # historical readiness was observed
    assert app.feature_health["status"] == "BLOCKED"
    assert not app.auto_health_pending


def test_boot_readiness_timeout_blocks_health(lifecycle_app, monkeypatch):
    app = lifecycle_app
    boot = app.start("boot")
    app.boot_deadline = -1
    app.advance_features(boot["id"])
    assert app.feature_boot["status"] == "TIMEOUT"
    assert app.feature_health["status"] == "BLOCKED"
    assert not app.auto_health_pending


def test_reboot_epoch_waits_for_new_boot_id_before_health(lifecycle_app, tmp_path, monkeypatch):
    import sys
    from types import SimpleNamespace
    app = lifecycle_app
    monkeypatch.setattr(app, "running", lambda: True)
    samples = iter([{"status": "ONLINE", "boot_id": "old"},
                    {"status": "ONLINE", "boot_id": "old"},
                    {"status": "ONLINE", "boot_id": "new"}])
    monkeypatch.setitem(sys.modules, "telemetry", SimpleNamespace(collect=lambda _: next(samples)))
    monkeypatch.setattr(server.subprocess, "Popen", lambda *a, **k: SimpleNamespace(wait=lambda **k: 0))
    monkeypatch.setattr(server.time, "sleep", lambda _: None)
    app.vm_job = "original"
    app.jobs.append({"id": "original", "evidence_path": str(tmp_path / "original")})
    started = app.start("reboot", confirmed=True)
    assert app.feature_boot["status"] == "RUNNING"
    app.execute(app.jobs[-1])
    assert app.feature_boot["status"] == "PASS"
    assert app.feature_boot["result"]["boot_id"] == "new"
    app.advance_features(started["id"])
    assert app.jobs[-1]["action"] == "health"
    assert app.jobs[-1]["automatic"]


def test_failed_reboot_blocks_automatic_health(lifecycle_app, monkeypatch):
    import sys
    from types import SimpleNamespace
    app = lifecycle_app
    monkeypatch.setattr(app, "running", lambda: True)
    monkeypatch.setitem(sys.modules, "telemetry", SimpleNamespace(collect=lambda _: {"status": "UNAVAILABLE"}))
    app.start("reboot", confirmed=True)
    app.execute(app.jobs[-1])
    assert app.feature_boot["status"] == "FAIL"
    assert app.feature_health["status"] == "BLOCKED"
    assert not app.auto_health_pending


def test_automatic_health_wait_is_bounded_but_manual_is_single_check(app):
    job = {"id": "test", "action": "health", "evidence_path": "/tmp/test"}
    argv = app.guest_command(job)
    assert "deadline=" not in argv[argv.index("--command") + 1]
    argv = app.guest_command(dict(job, automatic=True))
    command = argv[argv.index("--command") + 1]
    assert "SECONDS+180" in command and "exit 1" in command and "sleep 5" in command


def test_system_control_state_gates(app, monkeypatch):
    app.allow, app.manifest, app.rootfs = True, Path("manifest"), Path("rootfs")
    monkeypatch.setattr(app, "running", lambda: True)
    controls = {c["action"]: c["enabled"] for c in app.state()["system_controls"]}
    assert controls == dict(boot=False, shutdown=True, reboot=True, pause=True, resume=False)
    with pytest.raises(ValueError, match="confirm"):
        app.start("pause")
    with pytest.raises(ValueError, match="not paused"):
        app.start("resume")
    app.vm_paused = True
    controls = {c["action"]: c["enabled"] for c in app.state()["system_controls"]}
    assert controls == dict(boot=False, shutdown=False, reboot=False, pause=False, resume=True)
    assert not any(c["enabled"] for c in app.state()["catalog"])
    for action in ("health", "shutdown", "reboot", "pause"):
        with pytest.raises(ValueError, match="paused"):
            app.start(action, confirmed=True)
    app.active = "busy"
    assert not any(c["enabled"] for c in app.state()["system_controls"])


@pytest.mark.parametrize("action,status", [("pause", "paused"), ("resume", "running")])
def test_system_monitor_confirmation(app, tmp_path, monkeypatch, action, status):
    import io
    vm = tmp_path / "owned/vm"
    vm.mkdir(parents=True)
    (vm / "qemu-monitor.in").touch()
    (vm / "qemu-monitor.log").write_text("old VM status: paused\n")
    app.jobs = [{"id": "boot", "evidence_path": str(vm.parent)}]
    app.vm_job = "boot"
    monkeypatch.setattr(app, "running", lambda: True)
    def response(_):
        with (vm / "qemu-monitor.log").open("a") as stream:
            stream.write("VM status: " + status + "\n")
    monkeypatch.setattr(server.time, "sleep", response)
    result = app.control_monitor(action, io.BytesIO())
    assert result["qemu_status"] == status
    assert app.vm_paused == (action == "pause")
    assert (vm / "qemu-monitor.in").read_text() == ("stop" if action == "pause" else "cont") + "\ninfo status\n"


def test_reboot_command_is_guest_os_reboot(app):
    argv = app.guest_command({"action": "reboot", "id": "reboot", "evidence_path": "/tmp/example"})
    assert argv[argv.index("--command") + 1] == "systemctl reboot --no-block"


def test_reboot_requires_new_boot_id(app, tmp_path, monkeypatch):
    import sys
    from types import SimpleNamespace
    samples = iter([{"status": "ONLINE", "boot_id": "old"},
                    {"status": "ONLINE", "boot_id": "old"},
                    {"status": "ONLINE", "boot_id": "new"}])
    monkeypatch.setitem(sys.modules, "telemetry", SimpleNamespace(collect=lambda _: next(samples)))
    monkeypatch.setattr(app, "running", lambda: True)
    monkeypatch.setattr(server.subprocess, "Popen", lambda *a, **k: SimpleNamespace(wait=lambda **k: 0))
    monkeypatch.setattr(server.time, "sleep", lambda _: None)
    app.vm_job = "boot"
    app.jobs = [{"id": "boot", "evidence_path": str(tmp_path / "boot")}]
    job = {"id": "test", "action": "reboot", "evidence_path": str(tmp_path), "result": None}
    app.execute(job)
    assert job["status"] == "PASS"
    assert job["result"]["before_boot_id"] == "old"
    assert job["result"]["after_boot_id"] == "new"
    assert "Waiting for a new" in (tmp_path / "console.log").read_text()
    assert app.log_session == "test"
    assert job["log_session"] == "test"


def test_guest_log_is_current_uart_not_selected_job(app, tmp_path):
    vm = tmp_path / "boot/vm"
    vm.mkdir(parents=True)
    (vm / "linux-uart.log").write_bytes(b"old boot\nnew boot\n")
    app.jobs = [{"id": "boot", "evidence_path": str(vm.parent)}]
    app.vm_job = "boot"
    app.log_session = "reboot"
    app.guest_log_offset = len(b"old boot\n")
    assert app.guest_log() == {"text": "new boot\n", "truncated": False, "log_session": "reboot"}
    (vm / "linux-uart.log").write_bytes(b"x" * (300 * 1024))
    result = app.guest_log()
    assert len(result["text"]) == 256 * 1024 and result["truncated"]


def test_guest_log_no_owned_boot(app):
    assert app.guest_log()["log_session"] is None


def test_boot_reserves_new_uart_owner_before_thread_starts(app, tmp_path, monkeypatch):
    old = tmp_path / "old/vm"
    old.mkdir(parents=True)
    (old / "linux-uart.log").write_text("old UART must not leak")
    app.jobs = [{"id": "old", "evidence_path": str(old.parent)}]
    app.vm_job, app.log_session = "old", "old"
    app.allow, app.manifest, app.rootfs, app.ssh_port = True, Path("manifest"), Path("rootfs"), 0
    monkeypatch.setattr(server.threading.Thread, "start", lambda _: None)
    job = app.start("boot")
    assert app.vm_job == app.log_session == job["id"]
    result = app.guest_log()
    assert result["log_session"] == job["id"]
    assert "old UART" not in result["text"]


def test_reboot_unavailable_guest_does_not_issue_command(app, tmp_path, monkeypatch):
    import sys
    from types import SimpleNamespace
    monkeypatch.setitem(sys.modules, "telemetry", SimpleNamespace(collect=lambda _: {"status": "UNAVAILABLE"}))
    monkeypatch.setattr(server.subprocess, "Popen", lambda *a, **k: pytest.fail("must not reboot"))
    job = {"id": "test", "action": "reboot", "evidence_path": str(tmp_path)}
    app.execute(job)
    assert job["status"] == "FAIL"
    assert "reboot not issued" in job["error"]


def test_allowlist_and_disruptive_confirmation(app):
    app.allow, app.manifest, app.rootfs = True, Path("manifest"), Path("rootfs")
    with pytest.raises(ValueError, match="Unknown action"):
        app.start("rm -rf /")
    with pytest.raises(ValueError, match="confirm"):
        app.start("automotive")
    with pytest.raises(ValueError, match="No owned"):
        app.start("health")


def test_evidence_only_known_files_and_no_symlinks(tmp_path):
    good = tmp_path / "rt-experiment-verified"
    good.mkdir()
    (good / "results.json").write_text('{"measurement_status":"FAIL"}')
    (good / "private.json").write_text('{"secret":true}')
    (good / "trace-result.json").symlink_to(good / "private.json")
    rows = server.evidence(tmp_path)
    assert len(rows) == 1
    assert rows[0]["result"]["measurement_status"] == "FAIL"
    assert rows[0]["modified_at"]


@pytest.mark.parametrize("action", ["health", "automotive", "rt", "timerlat", "osnoise", "shutdown"])
def test_guest_commands_fixed_and_bounded(app, action):
    args = app.guest_command({"id": "abc123", "action": action, "evidence_path": "/tmp/test"})
    assert "--timeout" in args
    assert args[args.index("--port") + 1] == "2244"
    command = args[args.index("--command") + 1]
    if action in ("rt", "timerlat", "osnoise"):
        assert "--upload" in args
        assert "--duration 5" in command
        assert "--allow-private-guest" in command
    if action == "automotive":
        assert "--allow-disruptive-demo" in command
    if action != "health" and action != "shutdown":
        assert "evidence.tar.gz" in " ".join(args)


def test_log_cannot_escape_job_allowlist(app):
    with pytest.raises(KeyError):
        app.log("../../etc/passwd")


@pytest.fixture
def http(app):
    instance = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    instance.app = app
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    yield instance
    instance.shutdown()
    instance.server_close()
    thread.join(2)


def request(http, path="/api/state", body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"http://127.0.0.1:{http.server_port}" + path,
        data=data, headers=headers or {})
    return urllib.request.urlopen(req)


def test_api_state(http):
    with request(http) as response:
        state = json.load(response)
        assert state["csrf_token"]
        assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_guest_log_api(http):
    with request(http, "/api/guest/log") as response:
        payload = json.load(response)
        assert "text" in payload and payload["log_session"] is None


def test_service_log_api_rejects_unknown_source(http):
    with pytest.raises(urllib.error.HTTPError) as error:
        request(http, "/api/guest/log?source=arbitrary-shell")
    assert error.value.code == 400


def test_service_log_cache_gates_and_epoch(app, monkeypatch):
    app.log_session = "boot1"
    monkeypatch.setattr(app, "running", lambda: True)
    monkeypatch.setattr(server.threading.Thread, "start", lambda _: None)
    assert app.service_log("root")["status"] == "WAITING"
    assert app.service_log_inflight
    calls = []
    monkeypatch.setattr(server, "collect_service_logs", lambda port, source: calls.append(source) or {"text": "guest root journal", "status": "OK"})
    app.fetch_service_log(("boot1", "root"))
    assert app.service_log("root")["text"] == "guest root journal"
    assert calls == ["root"]
    app.vm_paused = True
    assert app.service_log("root")["status"] == "PAUSED"
    app.fetch_service_log(("boot1", "qm"))
    assert calls == ["root"]
    app.vm_paused = False
    app.log_session = "boot2"
    app.fetch_service_log(("boot1", "root"))
    assert calls == ["root"]
    app.active = "measure"
    app.jobs = [{"id": "measure", "action": "rt-r02"}]
    assert app.service_log("root")["status"] == "DEFERRED"
    assert "guest root journal" not in app.service_log("root")["text"]


def test_lan_auth_and_origin(http):
    host = '192.168.0.13:' + str(http.server_port)
    http.allowed_hosts = {host, '127.0.0.1:' + str(http.server_port)}
    auth = 'Basic ' + base64.b64encode(b'autosd:test-password-not-a-real-secret').decode()
    http.authorization = auth
    for path in ('/', '/api/state', '/api/jobs/test/log'):
        with pytest.raises(urllib.error.HTTPError) as error:
            request(http, path, headers={'Host': host})
        assert error.value.code == 401
        assert error.value.headers['WWW-Authenticate'].startswith('Basic ')
    for address in http.allowed_hosts:
        with request(http, headers={'Host': address, 'Authorization': auth, 'Origin': 'http://' + address}) as response:
            assert json.load(response)['csrf_token']
    with pytest.raises(urllib.error.HTTPError) as error:
        request(http, headers={'Host': host, 'Authorization': auth, 'Origin': 'http://attacker.example'})
    assert error.value.code == 403
    with pytest.raises(urllib.error.HTTPError) as error:
        request(http, '/api/jobs', {'action': 'boot'}, {'Host': host, 'Authorization': auth,
                                                     'Content-Type': 'application/json'})
    assert error.value.code == 403  # Authentication does not replace CSRF.


def test_explicit_lan_without_login_keeps_origin_and_csrf(http):
    host = '192.168.0.13:' + str(http.server_port)
    http.allowed_hosts = {host, '127.0.0.1:' + str(http.server_port)}
    http.authorization = None
    for address in http.allowed_hosts:
        with request(http, headers={'Host': address, 'Origin': 'http://' + address}) as response:
            assert json.load(response)['csrf_token']
    with pytest.raises(urllib.error.HTTPError) as error:
        request(http, headers={'Host': host, 'Origin': 'http://attacker.example'})
    assert error.value.code == 403
    with pytest.raises(urllib.error.HTTPError) as error:
        request(http, '/api/jobs', {'action': 'boot'}, {'Host': host, 'Content-Type': 'application/json'})
    assert error.value.code == 403


def test_password_file_private_stable_and_no_symlink(tmp_path):
    path = tmp_path / 'access.password'
    password = server.access_password(path)
    assert len(password) >= 20
    assert path.stat().st_mode & 0o777 == 0o600
    assert server.access_password(path) == password
    link = tmp_path / 'link'
    link.symlink_to(path)
    with pytest.raises(OSError):
        server.access_password(link)
    path.chmod(0o644)
    with pytest.raises(ValueError, match='0600'):
        server.access_password(path)


@pytest.mark.parametrize("headers", [{"Host": "attacker.example"},
    {"Origin": "https://attacker.example"}, {"Sec-Fetch-Site": "cross-site"}])
def test_dns_rebinding_and_cross_origin_rejected(http, headers):
    with pytest.raises(urllib.error.HTTPError) as error:
        request(http, headers=headers)
    assert error.value.code == 403


def test_post_csrf_required(http):
    with pytest.raises(urllib.error.HTTPError) as error:
        request(http, "/api/jobs", {"action": "boot"}, {"Content-Type": "application/json"})
    assert error.value.code == 403


def test_backend_http_selection(http):
    with request(http, "/api/backend", {"backend": "qbox-full"},
                 {"Content-Type": "application/json", "X-CSRF-Token": http.app.token}) as response:
        assert response.status == 200
        assert json.load(response)["backend"] == "qbox-full"


@pytest.mark.parametrize("body", [{"backend": "shell"}, {"backend": []},
                                  {"backend": "qbox", "command": "anything"}, {}])
def test_backend_http_strict_payload(http, body):
    with pytest.raises(urllib.error.HTTPError) as error:
        request(http, "/api/backend", body,
                {"Content-Type": "application/json", "X-CSRF-Token": http.app.token})
    assert error.value.code == 400
    assert http.app.backend == "qemu"


def test_backend_http_csrf_required(http):
    with pytest.raises(urllib.error.HTTPError) as error:
        request(http, "/api/backend", {"backend": "qbox"}, {"Content-Type": "application/json"})
    assert error.value.code == 403


@pytest.mark.parametrize("action", ["reboot", "pause", "resume"])
def test_qbox_http_rejects_unqualified_controls(http, monkeypatch, action):
    http.app.backend = "qbox"
    http.app.allow, http.app.manifest, http.app.rootfs = True, Path("manifest"), Path("disk")
    monkeypatch.setattr(http.app, "running", lambda: True)
    with pytest.raises(urllib.error.HTTPError) as error:
        request(http, "/api/jobs", {"action": action, "confirm_disruptive": True},
                {"Content-Type": "application/json", "X-CSRF-Token": http.app.token})
    assert error.value.code == 400
    assert "not qualified" in json.load(error.value)["error"]
    assert not http.app.jobs


def test_post_cannot_inject_arbitrary_command(http):
    with pytest.raises(urllib.error.HTTPError) as error:
        request(http, "/api/jobs", {"action": "health", "command": "anything"},
            {"Content-Type": "application/json", "X-CSRF-Token": http.app.token})
    assert error.value.code == 400


def test_static_path_traversal_rejected(http):
    with pytest.raises(urllib.error.HTTPError) as error:
        request(http, "/../../etc/passwd")
    assert error.value.code == 404


def test_log_tail_bounded(app, tmp_path):
    (tmp_path / "console.log").write_bytes(b"x" * 300000)
    app.jobs.append({"id": "known", "evidence_path": str(tmp_path)})
    result = app.log("known")
    assert result["truncated"]
    assert len(result["text"]) == 256 * 1024


def test_artifact_allowlist_and_symlinks(app, tmp_path):
    guest = tmp_path / "guest"
    guest.mkdir()
    (guest / "results.json").write_text("{}")
    (guest / "scenarios.json").symlink_to(guest / "results.json")
    app.jobs.append({"id": "known", "evidence_path": str(tmp_path)})
    assert app.artifact("known", "results.json") == guest / "results.json"
    with pytest.raises(KeyError):
        app.artifact("known", "../../etc/passwd")
    with pytest.raises(KeyError):
        app.artifact("known", "scenarios.json")


def test_persisted_running_jobs_never_adopted(tmp_path):
    identifier = "a" * 32
    directory = tmp_path / "dashboard/session" / identifier
    directory.mkdir(parents=True)
    (directory / "job.json").write_text(json.dumps({"id": identifier, "action": "boot",
        "status": "RUNNING", "evidence_path": "/untrusted/path"}))
    app = server.Dashboard(tmp_path)
    assert app.jobs[0]["status"] == "ORPHANED_NOT_MANAGED"
    assert app.jobs[0]["evidence_path"] == str(directory)
    assert not app.running()
    assert not app.state()["vm"]["owned"]


def test_artifact_http_download(http, tmp_path):
    directory = tmp_path / "artifact"
    directory.mkdir()
    (directory / "job.json").write_text('{"status":"FAIL"}')
    http.app.jobs.append({"id": "known", "evidence_path": str(directory)})
    with request(http, "/api/jobs/known/artifacts/job.json") as response:
        assert json.load(response)["status"] == "FAIL"
        assert response.headers["Content-Disposition"].startswith("attachment")


def test_restart_restores_bounded_telemetry_as_offline(tmp_path):
    directory = tmp_path / "dashboard/session"
    directory.mkdir(parents=True)
    rows = [{"status": "ONLINE", "collected_at": f"sample-{i}",
             "cpus": [{"id": "cpu0", "utilization_pct": i % 100}],
             "subsystems": [{"id": "qm", "status": "active"}]} for i in range(150)]
    (directory / "telemetry.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\ninvalid\n")
    app = server.Dashboard(tmp_path)
    assert len(app.history) == 120
    assert app.history[0]["collected_at"] == "sample-30"
    assert app.monitoring["collected_at"] == "sample-149"
    assert app.monitoring["status"] == "OFFLINE"
    assert app.monitoring["historical"] is True
    assert app.monitoring["cpus"][0]["utilization_pct"] == 49
    assert not app.state()["vm"]["owned"]


def test_history_skips_symlink_and_oversized_input(tmp_path):
    directory = tmp_path / "dashboard/session"
    directory.mkdir(parents=True)
    target = tmp_path / "sample.jsonl"
    target.write_text('{"status":"ONLINE","collected_at":"old","cpus":[],"subsystems":[]}\n')
    (directory / "telemetry.jsonl").symlink_to(target)
    assert server.telemetry_history(tmp_path) == []
    (directory / "telemetry.jsonl").unlink()
    with (directory / "telemetry.jsonl").open("wb") as stream:
        stream.truncate(256 * 1024 * 1024 + 1)
    assert server.telemetry_history(tmp_path) == []


def test_history_rejects_parent_symlink_outside_base(tmp_path):
    base = tmp_path / "base"
    (base / "dashboard").mkdir(parents=True)
    external = tmp_path / "external"
    external.mkdir()
    (external / "telemetry.jsonl").write_text('{"collected_at":"old","cpus":[],"subsystems":[]}\n')
    (base / "dashboard/session").symlink_to(external, target_is_directory=True)
    assert server.telemetry_history(base) == []


def test_shutdown_preserves_real_sample_without_new_timestamp(app):
    sample = {"status": "ONLINE", "collected_at": "original", "cpus": [{"id": "cpu1", "utilization_pct": 42}], "subsystems": []}
    app.monitoring = sample
    app.mark_offline()
    assert app.monitoring == dict(sample, status="OFFLINE", historical=True)
    app.history = [sample]
    app.monitoring = {"status": "UNAVAILABLE", "cpus": []}
    app.mark_offline()
    assert app.monitoring["collected_at"] == "original"
    assert app.monitoring["cpus"] == sample["cpus"]


def test_child_catalog_enablement_and_confirmation(app, monkeypatch):
    children = {child["action"]: child for parent in app.state()["catalog"]
                for child in parent["children"]}
    assert len(children) == 19
    assert not any(child["enabled"] for child in children.values())
    app.allow, app.manifest, app.rootfs = True, Path("manifest"), Path("rootfs")
    monkeypatch.setattr(app, "running", lambda: True)
    assert all(child["enabled"] for parent in app.state()["catalog"] for child in parent["children"]
               if child["action"] != "watchdog-wd04")
    assert children["automotive-s01"]["disruptive"] is False
    for index in range(2, 7):
        action = f"automotive-s{index:02}"
        assert children[action]["disruptive"] is True
        with pytest.raises(ValueError, match="confirm"):
            app.start(action)
    app.active = "other-job"
    assert not any(child["enabled"] for parent in app.state()["catalog"] for child in parent["children"])
    with pytest.raises(ValueError, match="Another"):
        app.start("automotive-s01")
    with pytest.raises(ValueError, match="Another"):
        app.start("rt-r01")


@pytest.mark.parametrize("action", sorted(a for a, row in server.CHILD_ACTIONS.items()
                                          if row[0] in ("automotive", "rt")))
def test_child_command_is_fixed_bounded_and_archived(app, action):
    parent, case, *_ = server.CHILD_ACTIONS[action]
    args = app.guest_command({"id": "abc123", "action": action, "evidence_path": "/tmp/test"})
    command = args[args.index("--command") + 1]
    assert " --case " + case in command
    assert args[args.index("--timeout") + 1] == ("360" if parent == "automotive" else "240")
    assert "--upload" in args and "evidence.tar.gz" in " ".join(args)
    assert "rc=$?" in command and "exit $rc" in command
    if parent == "rt":
        assert "--threshold-us 5000" in command
        assert action in server.MEASUREMENT_ACTIONS
        assert "--duration 5" in command
    else:
        assert action not in server.MEASUREMENT_ACTIONS
        assert "--allow-disruptive-demo" in command


@pytest.mark.parametrize("action", ["rt", "timerlat", "osnoise"])
def test_measurement_dashboard_uses_explicit_tcg_observation_limit(app, action):
    args = app.guest_command({"id": "abc123", "action": action, "evidence_path": "/tmp/test"})
    assert "--threshold-us 5000" in args[args.index("--command") + 1]


@pytest.mark.parametrize("action", ["rt-r07", "automotive-s00", "rt-r01;id", "automotive-s01 --case S04"])
def test_child_unknown_and_injection_rejected(app, action):
    with pytest.raises(ValueError, match="Unknown"):
        app.start(action)
    with pytest.raises(ValueError, match="Unknown"):
        app.guest_command({"id": "abc123", "action": action, "evidence_path": "/tmp/test"})


@pytest.mark.parametrize("action,returncode,status", [
    ("rt-r01", 2, "EXCEEDED"), ("rt-r06", 0, "PASS"),
    ("rt-r03", 1, "FAIL"), ("rt-r06", 77, "UNSUPPORTED"),
    ("automotive-s04", 2, "FAIL"), ("automotive-s06", 124, "TIMEOUT"),
])
def test_child_execution_status_and_telemetry_barrier(app, tmp_path, monkeypatch, action, returncode, status):
    class Barrier:
        held = False

        def __enter__(self):
            self.held = True

        def __exit__(self, *args):
            self.held = False

    barrier = Barrier()
    app.telemetry_lock = barrier

    class Process:
        def wait(self, timeout=None):
            assert barrier.held == (action in server.MEASUREMENT_ACTIONS)
            assert timeout == server.guest_timeout(action) + 50
            return returncode

    monkeypatch.setattr(server.subprocess, "Popen", lambda *args, **kwargs: Process())
    job = {"id": "abc123", "action": action, "evidence_path": str(tmp_path), "result": None}
    app.active = job["id"]
    app.execute(job)
    assert job["status"] == status
    assert app.active is None and not barrier.held


def test_child_missing_prerequisite_is_blocked_not_pass(app, tmp_path, monkeypatch):
    class Process:
        def wait(self, timeout=None):
            return 1

    monkeypatch.setattr(server.subprocess, "Popen", lambda *args, **kwargs: Process())
    guest = tmp_path / "guest"
    guest.mkdir()
    (guest / "scenarios.json").write_text(json.dumps([
        {"id": "S06-operator-recovery", "status": "BLOCKED", "reason": "No latch"}]))
    job = {"id": "abc123", "action": "automotive-s06", "evidence_path": str(tmp_path), "result": None}
    app.execute(job)
    assert job["status"] == "BLOCKED"
    assert job["returncode"] == 1
