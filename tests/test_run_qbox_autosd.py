"""Private full-system AutoSD launch contracts; no firmware execution."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/run"))
import run_qbox_autosd as runner


@pytest.fixture
def inputs(tmp_path, monkeypatch):
    deploy = tmp_path / "deploy"
    deploy.mkdir()
    for name in ("nexios-bsp-initramfs-a.efi", "ukibootaa64.efi", "slot_a.addon.efi",
                 "slot_b.addon.efi", "efi-capsule-update-disk-image-apollo-qvp.img"):
        (deploy / name).write_bytes(b"fixture")
    disk, initrd = tmp_path / "source.wic", tmp_path / "initrd.img"
    disk.write_bytes(b"disk")
    initrd.write_bytes(b"initrd")
    manifest = tmp_path / "regular.json"
    manifest.write_text(json.dumps({"mode": "regular", "rootfs": str(disk),
                                    "initrd": str(initrd), "bootargs": "console=ttyAMA0 root=LABEL=root"}))
    monkeypatch.setattr(runner, "inspect_uki", lambda path: {"kernel_sha256": "test"})
    monkeypatch.setattr(runner, "inspect_disk", lambda path: {"bootctl": {"state": "valid"}})
    return runner.parser().parse_args(["--autosd", str(manifest), "--deploy-dir", str(deploy),
                                       "--out-dir", str(tmp_path / "run"), "--ssh-port", "2245", "--headless"])


def test_plan_full_chain_loopback_and_no_writes(inputs):
    plan = runner.make_plan(inputs)
    assert not inputs.out_dir.exists()
    assert "--foreground-runtime" in plan["command"]
    assert "--no-persistent-rse-state" in plan["command"]
    assert "--multi-session" in plan["command"]
    assert "--headless" in plan["command"]
    assert plan["command"][0].endswith("run_qbox_yocto.sh")
    assert plan["environment"]["QBOX_APOLLO_NETDEV"] == "type=user,hostfwd=tcp:127.0.0.1:2245-:22"
    assert "systemd.default_device_timeout_sec=180s" in plan["bootargs"]
    assert "efi=runtime" in plan["bootargs"]
    assert "apollo.fullsystem=1" in plan["bootargs"]
    assert Path(plan["rootfs"]) != Path(plan["source_rootfs"])


def test_monitor_plan_and_injection_are_explicit(inputs, monkeypatch):
    monkeypatch.setenv("QBOX_APOLLO_MONITOR_BIND_ADDRESS", "0.0.0.0")
    monkeypatch.setenv("QBOX_APOLLO_RUNTIME_INJECTION", "true")
    plan = runner.make_plan(inputs)
    assert plan["environment"]["QBOX_APOLLO_RUNTIME_INJECTION"] == "false"
    assert not plan["monitor"]["enabled"]
    inputs.monitor_port = 18123
    inputs.runtime_injection = True
    plan = runner.make_plan(inputs)
    assert plan["environment"]["QBOX_APOLLO_MONITOR_BIND_ADDRESS"] == "127.0.0.1"
    assert plan["environment"]["QBOX_APOLLO_RUNTIME_INJECTION"] == "true"
    assert plan["command"][1:4] == ["--monitor", "--monitor-port", "18123"]
    assert [len(d["cpu_object_paths"]) for d in plan["monitor"]["domains"]] == [1, 1, 4, 4]


def test_no_arguments_use_prepared_manifest(inputs):
    build = inputs.autosd.parent / "build"
    manifest = build / "autosd/demo-minimal-qm-prepared/regular.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(inputs.autosd.read_text())
    inputs.build_dir, inputs.autosd = build, None
    plan = runner.make_plan(inputs)
    assert plan["autosd"] == str(manifest)
    assert plan["input_selection"] == "manifest rootfs"
    inputs.rootfs = Path(plan["source_rootfs"])
    assert runner.make_plan(inputs)["input_selection"] == "explicit --rootfs"


def test_missing_default_manifest_is_actionable(tmp_path):
    args = runner.parser().parse_args(["--build-dir", str(tmp_path)])
    with pytest.raises(ValueError, match="prepare the image or use --autosd"):
        runner.make_plan(args)


@pytest.mark.parametrize("diagnostic", [False, True])
def test_rt_boot_profile_preserves_optional_diagnostic_baseline(inputs, diagnostic):
    data = json.loads(inputs.autosd.read_text())
    debug = "slub_debug=FPZ rcupdate.rcu_expedited=1 rcupdate.rcu_normal_after_boot=0"
    data["bootargs"] += " " + debug + " cpuidle.off=1"
    inputs.autosd.write_text(json.dumps(data))
    inputs.diagnostic_boot = diagnostic
    plan = runner.make_plan(inputs)
    for word in debug.split():
        assert (word in plan["bootargs"].split()) is diagnostic
    assert "cpuidle.off=1" in plan["bootargs"].split()
    assert plan["boot_profile"] == ("diagnostic" if diagnostic else "normal-rt")


def test_native_reboot_observation_is_explicit_not_qualification(inputs):
    assert runner.make_plan(inputs)["observe_native_reboot"] is False
    inputs.observe_native_reboot = True
    assert runner.make_plan(inputs)["observe_native_reboot"] is True


def test_reset_trace_receipt_records_cli_and_environment(inputs, monkeypatch):
    monkeypatch.delenv("QBOX_APOLLO_RESET_TRACE", raising=False)
    assert runner.make_plan(inputs)["environment"]["QBOX_APOLLO_RESET_TRACE"] == "0"
    monkeypatch.setenv("QBOX_APOLLO_RESET_TRACE", "1")
    assert runner.make_plan(inputs)["environment"]["QBOX_APOLLO_RESET_TRACE"] == "1"
    monkeypatch.setenv("QBOX_APOLLO_RESET_TRACE", "0")
    inputs.reset_trace = True
    assert runner.make_plan(inputs)["environment"]["QBOX_APOLLO_RESET_TRACE"] == "1"


@pytest.mark.parametrize("invalid", [None, "active", "failed", "other-manifest", "provision", "symlink"])
def test_default_disk_requires_complete_matching_receipts(tmp_path, invalid):
    manifest = tmp_path / "regular.json"
    folder = tmp_path / "autosd/dashboard/session/job/vm"
    folder.mkdir(parents=True)
    (folder / "launch.json").write_text(json.dumps({"backend": "qbox-full", "autosd": str(manifest)}))
    result = {"status": "POWERED_OFF", "passed": True, "poweroff_observed": True,
              "domains": {"status": "PASS"}}
    (folder / "result.json").write_text(json.dumps(result))
    (folder / "modules.json").write_text('{"status":"PASS"}')
    disk = folder / "rootfs.wic"
    disk.touch()
    if invalid == "active":
        (folder / "result.json").unlink()
    elif invalid == "failed":
        result["domains"]["status"] = "FAIL"
        (folder / "result.json").write_text(json.dumps(result))
    elif invalid == "other-manifest":
        manifest = tmp_path / "other.json"
    elif invalid == "provision":
        (folder / "modules.json").write_text('{"status":"FAIL"}')
    elif invalid == "symlink":
        disk.unlink()
        disk.symlink_to(folder / "modules.json")
    assert runner.default_rootfs(tmp_path, manifest) == (disk if invalid is None else None)


@pytest.mark.parametrize("port", [22, -1, 65536])
def test_invalid_port(inputs, port):
    inputs.ssh_port = port
    with pytest.raises(ValueError, match="ssh-port"):
        runner.make_plan(inputs)


def test_existing_output_refused(inputs):
    inputs.out_dir.mkdir()
    (inputs.out_dir / "rootfs.wic").write_bytes(b"keep")
    with pytest.raises(ValueError, match="never overwrite"):
        runner.make_plan(inputs)


def test_slot_override_refused(inputs):
    data = json.loads(inputs.autosd.read_text())
    data["bootargs"] += " androidboot.slot_suffix=_a"
    inputs.autosd.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="must select"):
        runner.make_plan(inputs)


@pytest.mark.parametrize("error", [
    "Assertion failed in ap_watchdog_isr",
    "AP watchdog recovery enqueue failed: -1",
    "RSE recovery not completed: -7",
    "AP watchdog WS1 remains pending after reset",
    "Watchdog rearm FAILED after 10 attempts: -7",
    "Watchdog rearm enqueue failed: -1",
    "Watchdog rearm readback failed; IRQ mask failed: -1",
    "Error! SCP-RSE handshake failed",
])
def test_watchdog_recovery_failure_is_not_hidden_by_old_boot_markers(tmp_path, error):
    runtime = tmp_path / "full-system"
    runtime.mkdir()
    for domain, (_, filename) in runner.LOGS.items():
        (runtime / filename).write_text("\n".join(runner.MARKERS[domain]))
    (runtime / "qbox-secure-console.log").write_text(
        "NOTICE:  BL2:\nNOTICE:  BL31:\nOP-TEE version:")
    with (runtime / "qbox-safety-island-cl0.log").open("a") as log:
        log.write("\n" + error)
    result = runner.domain_status(tmp_path)
    assert result["status"] == "FAIL"
    assert next(row for row in result["domains"] if row["id"] == "si-cl0")["errors"]


def test_all_domains_required_not_login_only(tmp_path):
    runtime = tmp_path / "full-system"
    runtime.mkdir()
    (runtime / "qbox-primary-console.log").write_text("U-Boot\nLinux version\nlogin:")
    assert runner.domain_status(tmp_path)["status"] == "WAITING"
    for domain, (_, filename) in runner.LOGS.items():
        (runtime / filename).write_text("\n".join(runner.MARKERS[domain]))
    assert runner.domain_status(tmp_path)["status"] == "WAITING"
    (runtime / "qbox-secure-console.log").write_text("NOTICE:  BL2:\nNOTICE:  BL31:\nOP-TEE version:")
    assert runner.domain_status(tmp_path)["status"] == "PASS"
    with (runtime / "qbox-primary-console.log").open("a") as f:
        f.write("\nKernel panic")
    assert runner.domain_status(tmp_path)["status"] == "FAIL"


@pytest.mark.parametrize("message,status,code", [
    ("[ 100.1] reboot: Power down\n", "POWERED_OFF", 0),
    ("[ 100.1] reboot: Restarting system\n", "TIMEOUT", 124),
    ("echo reboot: Power down\n", "TIMEOUT", 124),
])
def test_supervisor_shutdown_is_observed_not_inferred(tmp_path, message, status, code):
    (tmp_path / "linux-uart.log").write_text(message)
    plan = {"out_dir": str(tmp_path), "environment": {}, "timeout": .1,
            "command": [sys.executable, "-c", "import time; time.sleep(30)"]}
    assert runner.supervise(plan) == code
    result = json.loads((tmp_path / "result.json").read_text())
    assert result["status"] == status
    assert result["poweroff_observed"] == (code == 0)


def test_unexpected_successful_child_exit_is_failure(tmp_path):
    plan = {"out_dir": str(tmp_path), "environment": {}, "timeout": 5,
            "command": [sys.executable, "-c", "pass"]}
    assert runner.supervise(plan) == 1
    assert json.loads((tmp_path / "result.json").read_text())["status"] == "UNEXPECTED_EXIT"


def test_canonical_runner_preserves_explicit_netdev():
    source = (ROOT / "run_qbox_yocto.sh").read_text()
    assert 'NETDEV="${QBOX_APOLLO_NETDEV:-type=user,hostfwd=tcp::${SSH_PORT_VALUE}-:22}"' in source


def test_foreground_runtime_option_is_opt_in():
    source = (ROOT / "scripts/run/run_qbox_apollo_fvp_full.py").read_text()
    assert 'getattr(args, "foreground_runtime", False)' in source
    assert "proc.send_signal(signal.SIGINT)" in source


def test_cleanup_failure_cannot_report_poweroff_pass(tmp_path, monkeypatch):
    (tmp_path / "linux-uart.log").write_text("reboot: Power down\n")
    def failed_cleanup(proc):
        proc.terminate()
        proc.wait(timeout=5)
        raise RuntimeError("cleanup failure")
    monkeypatch.setattr(runner, "stop_owned", failed_cleanup)
    plan = {"out_dir": str(tmp_path), "environment": {}, "timeout": 5,
            "command": [sys.executable, "-c", "import time; time.sleep(30)"]}
    with pytest.raises(RuntimeError):
        runner.supervise(plan)
    result = json.loads((tmp_path / "result.json").read_text())
    assert result["status"] == "CLEANUP_FAILED"
    assert result["passed"] is False


def test_foreground_sigterm_waits_for_owned_runtime_cleanup(tmp_path):
    child = """
import pathlib, sys, time
p = pathlib.Path(sys.argv[1])
try:
    (p / 'ready').touch()
    while True: time.sleep(.1)
except KeyboardInterrupt:
    (p / 'cleaned').touch()
"""
    parent = """
import argparse, importlib.util, pathlib, sys
spec = importlib.util.spec_from_file_location('full_lifecycle', sys.argv[1])
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)
p = pathlib.Path(sys.argv[2])
m.child_command = lambda *_: [sys.executable, '-c', sys.argv[3], str(p)]
m.clear_run_outputs = lambda *_: None
m.full_system_child_environment = lambda *_: {}
args = argparse.Namespace(out_dir=p, qbox_build_dir=p, timer_probe=False,
    build_only=False, live_trace=False, si_cl0_command=None,
    keep_running_after_pass=True, foreground_runtime=True, timeout=5)
rc, _ = m.run_child(args, {'si_cl0_image':p, 'si_cl1_image':p})
sys.exit(rc)
"""
    proc = subprocess.Popen([sys.executable, "-c", parent,
                             str(ROOT / "scripts/run/run_qbox_apollo_fvp_full.py"),
                             str(tmp_path), child], start_new_session=True)
    try:
        deadline = time.monotonic() + 5
        while not (tmp_path / "ready").exists():
            assert proc.poll() is None
            assert time.monotonic() < deadline
            time.sleep(.02)
        assert proc.poll() is None  # foreground parent has not detached
        proc.terminate()
        assert proc.wait(timeout=5) == 0
        assert (tmp_path / "cleaned").exists()
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)


@pytest.mark.parametrize("provision_status", ["PASS", "FAIL"])
def test_domain_gate_requires_module_provision(tmp_path, monkeypatch, provision_status):
    runtime = tmp_path / "full-system"
    runtime.mkdir()
    for domain, (alias, filename) in runner.LOGS.items():
        (runtime / filename).write_text("\n".join(runner.MARKERS[domain]))
        (tmp_path / alias).symlink_to(Path("full-system") / filename)
    (runtime / "qbox-secure-console.log").write_text("NOTICE:  BL2:\nNOTICE:  BL31:\nOP-TEE version:")
    calls = []
    def provision(port, build, out):
        calls.append((port, build, out))
        return {"status": provision_status}
    monkeypatch.setitem(sys.modules, "autosd_fullsystem_modules", SimpleNamespace(provision=provision))
    plan = {"out_dir": str(tmp_path), "environment": {}, "timeout": .6,
            "ssh_port": 2244, "build_dir": str(tmp_path / "build"),
            "command": [sys.executable, "-c", "import time; time.sleep(30)"]}
    assert runner.supervise(plan) == 124
    assert len(calls) == 1
    domains = json.loads((tmp_path / "domains.json").read_text())
    assert domains["status"] == provision_status
    assert domains["provision"]["status"] == provision_status


def test_new_boot_cannot_reuse_historical_markers_or_errors(tmp_path):
    runtime = tmp_path / "full-system"
    runtime.mkdir()
    for domain, (_, filename) in runner.LOGS.items():
        (runtime / filename).write_text("\n".join(runner.MARKERS[domain]))
    secure = runtime / "qbox-secure-console.log"
    secure.write_text("NOTICE:  BL2:\nNOTICE:  BL31:\nOP-TEE version:\nPANIC\nNOTICE:  BL2:\n")
    state = runner.domain_status(tmp_path)
    ap = state["domains"][-1]
    assert ap["boot_epoch"] == 2
    assert ap["status"] == "WAITING"
    assert not ap["markers"]["login:"]
    assert not ap["errors"]
    uart = runtime / "qbox-primary-console.log"
    with uart.open("a") as f:
        f.write("\nKernel panic\nU-Boot\n")
    ap = runner.domain_status(tmp_path)["domains"][-1]
    assert ap["status"] == "WAITING" and not ap["errors"]
    with uart.open("a") as f:
        f.write("\n" + "\n".join(runner.MARKERS["ap"][1:]))
    with secure.open("a") as f:
        f.write("NOTICE:  BL31:\nOP-TEE version:\n")
    assert runner.domain_status(tmp_path)["status"] == "PASS"
    # AP-only watchdog reboot leaves the other live firmware epochs intact.
    assert [d["boot_epoch"] for d in runner.domain_status(tmp_path)["domains"]] == [1, 1, 1, 2]


def test_reboot_request_withdraws_old_login(tmp_path):
    runtime = tmp_path / "full-system"
    runtime.mkdir()
    (runtime / "qbox-primary-console.log").write_text(
        "\n".join(runner.MARKERS["ap"]) + "\nreboot: Restarting system\n")
    ap = runner.domain_status(tmp_path)["domains"][-1]
    assert not ap["markers"]["login:"]
    assert ap["status"] == "WAITING"


@pytest.mark.parametrize("domain,start", [
    ("rse", "Starting TF-M BL1_1"),
    ("si-cl0", "[ 0.000000]  ___  ___ ___      __ _"),
    ("si-cl1", "Out of Reset (OoR) completed on CPU: 0"),
])
def test_each_firmware_epoch_discards_old_pass_and_failure(tmp_path, domain, start):
    runtime = tmp_path / "full-system"
    runtime.mkdir()
    text = start + "\n" + "\n".join(runner.MARKERS[domain])
    text += "\n" + runner.FAIL_MARKERS[domain][0] + "\n" + start + "\n"
    (runtime / runner.LOGS[domain][1]).write_text(text)
    row = next(d for d in runner.domain_status(tmp_path)["domains"] if d["id"] == domain)
    assert row["status"] == "WAITING"
    assert not row["errors"]


def test_bl2_build_and_handoff_messages_are_not_boot_epochs(tmp_path):
    runtime = tmp_path / "full-system"
    runtime.mkdir()
    (runtime / "qbox-secure-console.log").write_text(
        "NOTICE:  BL2: v2.14\nNOTICE:  BL2: Built : yesterday\nNOTICE:  BL2: Booting BL31\n")
    assert runner.domain_status(tmp_path)["domains"][-1]["boot_epoch"] == 1


def test_provision_serializes_and_discards_obsolete_epoch(tmp_path, monkeypatch):
    import threading
    entered, release = threading.Event(), threading.Event()
    calls = []
    def provision(port, build, out):
        calls.append(out)
        entered.set()
        assert release.wait(3)
        return {"status": "PASS"}
    monkeypatch.setitem(sys.modules, "autosd_fullsystem_modules", SimpleNamespace(provision=provision))
    p = runner.EpochProvisioner({"ssh_port": 2244, "build_dir": str(tmp_path)}, tmp_path)
    assert p.update(1, True)["status"] == "RUNNING"
    assert entered.wait(1)
    assert p.update(2, False)["status"] == "WAITING"
    assert p.update(2, True)["status"] == "WAITING"
    assert len(calls) == 1
    release.set()
    p.thread.join(2)
    assert p.update(2, False) == {"status": "WAITING", "boot_epoch": 2}
    assert p.update(2, True)["status"] == "RUNNING"
    p.thread.join(2)
    assert p.update(2, True) == {"status": "PASS", "boot_epoch": 2}
    p.update(2, True)
    assert len(calls) == 2
    assert calls[0] != calls[1]
    assert json.loads((tmp_path / "modules.json").read_text())["boot_epoch"] == 2


def test_default_uses_canonical_tmux_and_generated_directory(inputs):
    inputs.headless = False
    inputs.out_dir = None
    plan = runner.make_plan(inputs)
    assert "--headless" not in plan["command"]
    assert "--no-attach" in plan["command"]  # observer starts before interactive attach
    assert "--session" in plan["command"]
    assert plan["session"].startswith("autosd-full-")
    assert Path(plan["out_dir"]).name.startswith("autosd-full-")
    assert plan["no_attach"] is False
    assert not Path(plan["out_dir"]).exists()


def test_tmux_options_and_headless_rejection(inputs):
    inputs.no_attach = True
    with pytest.raises(ValueError, match="tmux option"):
        runner.make_plan(inputs)
    inputs.headless = False
    inputs.session = "autosd-custom"
    plan = runner.make_plan(inputs)
    assert plan["session"] == "autosd-custom"
    assert plan["no_attach"] is True
    inputs.session = "foreign:0"
    with pytest.raises(ValueError, match="session"):
        runner.make_plan(inputs)


@pytest.mark.parametrize("headless", [False, True])
def test_preflight_refuses_existing_full_system(tmp_path, headless):
    proc = tmp_path / "123"
    proc.mkdir()
    (proc / "cmdline").write_bytes(b"python\0/x/run_qbox_apollo_fvp_full.py\0--runtime-child\0")
    (proc / "environ").write_bytes(b"QBOX_SESSION_OUT_DIR=/existing/vm\0")
    with pytest.raises(ValueError, match="Power off"):
        runner.runtime_preflight({"session": "new", "headless": headless}, tmp_path)


def test_headless_preflight_does_not_require_tmux(tmp_path, monkeypatch):
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: pytest.fail("must not invoke tmux"))
    runner.runtime_preflight({"headless": True}, tmp_path)


def test_tmux_detached_launcher_return_does_not_end_supervisor(tmp_path, monkeypatch):
    plan = {"out_dir": str(tmp_path), "environment": {}, "command": ["canonical"],
            "session": "owned", "no_attach": True}
    calls = []
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: calls.append(a))
    observer = SimpleNamespace(pid=1234, poll=lambda: None)
    def spawn(*args, **kwargs):
        runner.write_json(tmp_path / "supervisor.json", {"status": "RUNNING"})
        assert kwargs["start_new_session"] is True
        assert "--supervise-tmux" in args[0]
        return observer
    monkeypatch.setattr(runner.subprocess, "Popen", spawn)
    assert runner.start_tmux(plan) == 0
    assert len(calls) == 1


def test_tmux_runtime_pidfd_targets_only_validated_runtime(tmp_path):
    runtime = tmp_path / "full-system"
    runtime.mkdir()
    env = dict(os.environ, QBOX_SESSION_OUT_DIR=str(runtime))
    # Extra argv identifies the canonical path without executing firmware.
    proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)",
                             str(ROOT / "scripts/run/run_qbox_apollo_fvp_full.py")], env=env)
    (runtime / "qbox-run.pid").write_text(str(proc.pid))
    handle = None
    try:
        handle = runner.TmuxRuntime(tmp_path)
        assert handle.poll() is None
        handle.terminate()
        handle.wait(timeout=5)
        assert handle.poll() is not None
    finally:
        if handle is not None:
            handle.close()
        if proc.poll() is None:
            proc.kill()
        proc.wait(timeout=5)


def test_foreign_tmux_session_never_cleaned(monkeypatch, tmp_path):
    calls = []
    def run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout="foreign\n")
    monkeypatch.setattr(runner.subprocess, "run", run)
    runner.cleanup_created_tmux({"out_dir": str(tmp_path), "session": "foreign"})
    assert len(calls) == 1
    assert "--stop-session" not in calls[0]


def test_canonical_start_failure_requests_scoped_cleanup(monkeypatch, tmp_path):
    plan = {"out_dir": str(tmp_path), "environment": {}, "command": ["canonical"],
            "session": "owned", "no_attach": True}
    cleaned = []
    def fail(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "canonical")
    monkeypatch.setattr(runner.subprocess, "run", fail)
    monkeypatch.setattr(runner, "cleanup_created_tmux", lambda value: cleaned.append(value))
    with pytest.raises(subprocess.CalledProcessError):
        runner.start_tmux(plan)
    assert cleaned == [plan]


def test_attach_failure_keeps_created_session_and_observer(monkeypatch, tmp_path):
    plan = {"out_dir": str(tmp_path), "environment": {}, "command": ["canonical"],
            "session": "owned", "no_attach": False}
    runner.write_json(tmp_path / "supervisor.json", {"status": "RUNNING"})
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **k: None)
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *a, **k: SimpleNamespace(pid=1234))
    monkeypatch.setattr(runner.subprocess, "call", lambda *a, **k: 1)
    cleaned = []
    monkeypatch.setattr(runner, "cleanup_created_tmux", lambda value: cleaned.append(value))
    assert runner.start_tmux(plan) == 1
    assert cleaned == []


@pytest.mark.parametrize("interval", [None, 2.])
def test_stats_enable_monitor_and_qmp(inputs, interval):
    inputs.stats = interval is None
    inputs.stats_interval = interval
    plan = runner.make_plan(inputs)
    assert plan["monitor"]["enabled"]
    assert plan["qmp_enabled"]
    assert "--monitor" in plan["command"]
    assert "--stats-interval" in plan["command"]
