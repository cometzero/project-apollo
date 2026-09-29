"""Check manifest portability and fault detection without a privileged host."""
import importlib.util
import json
from pathlib import Path
import shutil
import signal
import subprocess
import time

import pytest

LAYER = Path(__file__).resolve().parents[1] / "autosd/customization"


def test_demo_runner_preserves_failure_and_bounds_commands(tmp_path):
    demo = load("customization_demo", LAYER / "demo-guest.py")
    assert demo.run_case("pass", "echo evidence", tmp_path, 5)["status"] == "PASS"
    failure = demo.run_case("fail", "false; echo unreachable", tmp_path, 5)
    assert failure["status"] == "FAIL"
    assert "unreachable" not in (tmp_path / "fail.log").read_text()
    assert demo.run_case("timeout", "sleep 5", tmp_path, .1)["returncode"] == 124


def test_demo_stops_after_first_failure(tmp_path, monkeypatch):
    demo = load("customization_demo_failfast", LAYER / "demo-guest.py")
    output = tmp_path / "evidence"
    monkeypatch.setattr("sys.argv", ["demo-guest.py", "--allow-disruptive-demo", "--out", str(output)])
    monkeypatch.setattr(demo, "CASES", [("first", "exit 7"), ("must-not-run", "true")])
    assert demo.main() == 1
    results = json.loads((output / "results.json").read_text())
    assert len(results) == 1 and results[0]["returncode"] == 7
    assert not (output / "must-not-run.log").exists()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bundle_is_valid_and_portable(tmp_path):
    compiler = shutil.which("aarch64-linux-gnu-gcc")
    if not compiler:
        pytest.skip("AArch64 compiler unavailable")
    module = load("customization_prepare", LAYER / "prepare.py")
    output = tmp_path / "bundle"
    manifest = module.prepare(output, compiler)
    assert "auth" not in manifest
    assert "image" not in manifest  # No unconditional boot-success override.
    assert manifest["qm"]["memory_limit"]["max"] == "1G"
    root_files = {item["path"]: item for item in manifest["content"]["add_files"]}
    assert "/usr/libexec/apollo/watchdog-guest.py" not in root_files
    network = root_files["/etc/modules-load.d/apollo-container-network.conf"]["text"]
    assert [line for line in network.splitlines() if line and not line.startswith("#")] == ["br_netfilter"]
    for content in (manifest["content"], manifest["qm"]["content"]):
        for item in content["add_files"]:
            if "source_path" in item:
                assert (output / item["source_path"]).is_file()
    assert (output / "payload/Containerfile").read_text().startswith("FROM scratch")


def test_watchdog_bundle_is_explicit_root_only_and_inactive(tmp_path):
    compiler = shutil.which("aarch64-linux-gnu-gcc")
    if not compiler:
        pytest.skip("AArch64 compiler unavailable")
    module = load("customization_watchdog_prepare", LAYER / "prepare.py")
    output = tmp_path / "bundle"
    manifest = module.prepare(output, compiler, watchdog_tools=True)
    runtime = json.loads((output / "runtime-files.json").read_text())
    source = (LAYER.parents[1] / "scripts/autosd_demo/watchdog_guest.py").read_text()
    destination = "/usr/libexec/apollo/watchdog-guest.py"
    root_files = {item["path"]: item for item in manifest["content"]["add_files"]}
    assert root_files[destination]["text"] == source
    assert (output / "watchdog-guest.py").read_text() == source
    # The private installer consumes the same inline-text manifest entries.
    assert runtime["content"]["add_files"] == manifest["content"]["add_files"]
    assert destination not in {item["path"] for item in manifest["qm"]["content"]["add_files"]}
    assert not any("watchdog" in name for name in manifest["content"]["systemd"]["enabled_services"])
    assert not any(item["path"].startswith("/etc/systemd/system.conf.d/")
                   for item in manifest["content"]["add_files"])
    assert "scripts/autosd_demo/watchdog_guest.py" in json.loads((output / "provenance.json").read_text())


def test_patched_runtime_overlay_covers_root_and_qm(tmp_path):
    compiler = shutil.which("aarch64-linux-gnu-gcc")
    if not compiler:
        pytest.skip("AArch64 compiler unavailable")
    module = load("customization_runtime_prepare", LAYER / "prepare.py")
    binary = tmp_path / "runtime"
    subprocess.run([compiler, "-static", str(LAYER / "apps/workload.c"), "-o", str(binary)], check=True)
    output = tmp_path / "bundle"
    manifest = module.prepare(output, compiler, crun_binary=binary)
    for content in (manifest["content"], manifest["qm"]["content"]):
        runtime = next(item for item in content["add_files"] if item["path"] == "/usr/bin/crun")
        assert runtime["source_path"] == "./payload/crun"
        assert {"path": "/usr/bin/crun", "mode": "0755"} in content["chmod_files"]
    assert "crun_sha256" in json.loads((output / "provenance.json").read_text())


def test_cgroup_patch_preserves_selinux_other_filesystems():
    patch = (LAYER / "runtime/crun-cgroup-mount-label.patch").read_text()
    assert 'strcmp (type, "cgroup") == 0 || strcmp (type, "cgroup2") == 0' in patch
    assert "+    return LABEL_NONE;" in patch
    assert 'strcmp (type, "mqueue") == 0' in patch


def test_real_workload_detects_missing_stale_and_corrupt_heartbeat(tmp_path):
    cc = shutil.which("cc")
    if not cc:
        pytest.skip("C compiler unavailable")
    binary, heartbeat = tmp_path / "workload", tmp_path / "heartbeat"
    subprocess.run([cc, "-O2", "-Wall", "-Wextra", "-Werror", str(LAYER / "apps/workload.c"),
                    "-o", str(binary)], check=True)

    def healthy():
        return subprocess.run([str(binary), "health", str(heartbeat)]).returncode == 0

    assert not healthy()
    process = subprocess.Popen([str(binary), "run", str(heartbeat)])
    try:
        deadline = time.monotonic() + 5
        while not heartbeat.exists() and time.monotonic() < deadline:
            time.sleep(.02)
        assert healthy()
        process.send_signal(signal.SIGSTOP)
        time.sleep(1.1)
        assert not healthy()
        heartbeat.write_text("invalid\n")
        assert not healthy()
    finally:
        process.kill()
        process.wait()


@pytest.mark.parametrize("signum", [signal.SIGTERM, signal.SIGINT])
def test_workload_handles_shutdown_signal_cleanly(tmp_path, signum):
    cc = shutil.which("cc")
    if not cc:
        pytest.skip("C compiler unavailable")
    binary, heartbeat = tmp_path / "workload", tmp_path / "heartbeat"
    subprocess.run([cc, "-O2", "-Wall", "-Wextra", "-Werror",
                    str(LAYER / "apps/workload.c"), "-o", str(binary)], check=True)
    process = subprocess.Popen([str(binary), "run", str(heartbeat)])
    try:
        deadline = time.monotonic() + 5
        while not heartbeat.exists() and time.monotonic() < deadline:
            time.sleep(.02)
        assert heartbeat.exists()
        process.send_signal(signum)
        assert process.wait(timeout=2) == 0
    finally:
        if process.poll() is None:
            process.kill()
        process.wait()


def test_rt_profile_is_explicit_and_preserves_qm_restrictions(tmp_path):
    compiler = shutil.which("aarch64-linux-gnu-gcc")
    if not compiler:
        pytest.skip("AArch64 compiler unavailable")
    module = load("customization_rt_prepare", LAYER / "prepare.py")
    output = tmp_path / "rt-bundle"
    manifest = module.prepare(output, compiler, rt_tools=True)
    provenance = json.loads((output / "provenance.json").read_text())
    import hashlib
    assert provenance["latency_probe_sha256"] == hashlib.sha256(
        (output / "payload/latency-probe").read_bytes()).hexdigest()
    assert "realtime-tests" in manifest["content"]["rpms"]
    assert "rtla" in manifest["content"]["rpms"]
    assert manifest["qm"]["content"]["rpms"] == ["podman", "bluechi-agent", "stress-ng"]
    assert "auth" not in manifest and "image" not in manifest
    assert "rt-experiment" not in str(manifest["content"]["systemd"])
    for content in (manifest["content"], manifest["qm"]["content"]):
        probe = [f for f in content["add_files"] if f["path"].endswith("/latency-probe")][0]
        assert (output / probe["source_path"]).is_file()
    assert (output / "rt-trace.py").is_file()


def test_monitor_latches_fault_and_stops_only_adas(tmp_path, monkeypatch):
    # Restarting the monitor must not independently restart the stopped ADAS.
    unit = (LAYER / "root/apollo-safety-monitor.service").read_text()
    assert "Wants=apollo-adas" not in unit and "Requires=apollo-adas" not in unit
    monitor = load("scenario_monitor", LAYER / "root/safety-monitor.py")
    monitor.STATE = tmp_path / "state.json"
    health = iter([True, False, True, False, False, False])
    monkeypatch.setattr(monitor, "probe", lambda: next(health))
    monkeypatch.setattr(monitor.time, "sleep", lambda _: None)
    commands = []
    monkeypatch.setattr(monitor.subprocess, "run", lambda command, **kwargs: commands.append(command))
    monitor.main()
    assert json.loads(monitor.STATE.read_text())["state"] == "FAULT_LATCHED"
    assert commands == [["systemctl", "stop", "apollo-adas.service"]]
    with pytest.raises(SystemExit, match="Operator"):
        monitor.main()


def test_probe_timeout_is_unhealthy(monkeypatch):
    monitor = load("scenario_monitor_timeout", LAYER / "root/safety-monitor.py")
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], 2)
    monkeypatch.setattr(monitor.subprocess, "run", timeout)
    assert not monitor.probe()
