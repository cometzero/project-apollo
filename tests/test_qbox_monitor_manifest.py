"""Exercise monitor ownership against real local sockets, without a VM."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/run"))
import qbox_monitor_manifest as monitor


def test_listener_owner_and_collision(tmp_path):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen()
        port = sock.getsockname()[1]
        plan = monitor.monitor_plan(True, port, tmp_path)
        with pytest.raises(OSError):
            monitor.preflight(plan)
        assert monitor.listener_owner(port, os.getpid())["pid"] == os.getpid()
        with pytest.raises(RuntimeError, match="not owned"):
            monitor.listener_owner(port, 99999999)
        monitor.update_runtime(plan, os.getpid(), "test-run")
        state = json.loads(Path(plan["runtime_manifest"]).read_text())
        assert state["status"] == "READY"
        assert state["run_id"] == "test-run"
        assert state["start_ticks"] == monitor.process_identity(os.getpid())[1]


def test_unbound_endpoint_is_starting(tmp_path):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        plan = monitor.monitor_plan(True, port, tmp_path)
        monitor.update_runtime(plan, os.getpid(), "pending")
        assert json.loads(Path(plan["runtime_manifest"]).read_text())["status"] == "STARTING"


def test_qmp_private_paths_and_domain_biflows(tmp_path):
    plan = {"qmp_enabled": True, "monitor": monitor.monitor_plan(True, 18080, tmp_path, full=True),
            "environment": {}}
    monitor.prepare_qmp(plan)
    directory = Path(plan["environment"]["QBOX_APOLLO_QMP_DIR"])
    try:
        assert directory.stat().st_mode & 0o777 == 0o700
        assert len({d["qmp_socket"] for d in plan["monitor"]["domains"]}) == 4
        assert plan["monitor"]["domains"][1]["qmp_biflow"] == "platform.si_cl0_qmp.qmp_socket.qmp_socket_router"
        assert plan["monitor"]["domains"][0]["qmp_biflow"] == "platform.rse_cpu_pass.rse_qmp.qmp_socket.qmp_socket_router"
        assert all(len(d["qmp_socket"]) < 108 for d in plan["monitor"]["domains"])
    finally:
        directory.rmdir()


def test_rse_qmp_is_constructed_before_nested_devices():
    root = Path(__file__).resolve().parents[1]
    script = root / "hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-qmp.lua"
    lua = '''
local platform = {rse_cpu_pass={qemu_inst_mgr={}, qemu_inst={}}}
dofile(arg[1])(platform, true)
local rse = platform.rse_cpu_pass
assert(platform.rse_qmp == nil)
assert(rse.rse_qmp.args[1] == "&qemu_inst")
assert(rse.qemu_inst_mgr.construction_priority < rse.qemu_inst.construction_priority)
assert(rse.qemu_inst.construction_priority < rse.rse_qmp.construction_priority)
assert(rse.rse_qmp.construction_priority < 0)
assert(platform.ap_qmp.args[1] == "&platform.ap_qemu_inst")
assert(platform.si_cl0_qmp.args[1] == "&platform.si_cl0_qemu_inst")
assert(platform.si_cl1_qmp.args[1] == "&platform.si_cl1_qemu_inst")
'''
    subprocess.run(["lua", "-", str(script)], input=lua, text=True, check=True,
                   env={**os.environ, "QBOX_APOLLO_QMP_DIR": "/tmp/qbox-qmp-test"})


def test_ap_only_profile_constructs_shared_metadata_without_si_domains():
    root = Path(__file__).resolve().parents[1]
    script = root / "hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-linux.lua"
    lua = '''
dofile(arg[1])
assert(platform.ap_cpu_0 ~= nil)
assert(platform.si_cl0_qemu_inst == nil)
assert(platform.si_cl1_qemu_inst == nil)
assert(platform.ap_ns_watchdog_ws1_fanout == nil)
assert(platform.ap_watchdog_0.ws1.bind == "&ap_gic.spi_in_51")
assert(platform.qbox_monitor.runtime_mutation == false)
assert(platform.ap_qmp.args[1] == "&platform.ap_qemu_inst")
'''
    subprocess.run(["lua", "-", str(script)], input=lua, text=True, check=True,
                   env={**os.environ, "QBOX_RDASPEN_ENABLE_AP_CPUS": "true",
                        "QBOX_LINUX_BOOT_STUB": "/tmp/unused", "QBOX_LINUX_KERNEL": "/tmp/unused",
                        "QBOX_LINUX_DTB": "/tmp/unused", "QBOX_LINUX_INITRD": "",
                        "QBOX_APOLLO_MONITOR": "true", "QBOX_APOLLO_RUNTIME_INJECTION": "false",
                        "QBOX_APOLLO_QMP_DIR": "/tmp/qbox-qmp-test"})


@pytest.mark.parametrize("port", [0, -1, 65536])
def test_invalid_ports(port, tmp_path):
    with pytest.raises(ValueError):
        monitor.monitor_plan(True, port, tmp_path)
def test_qmp_module_is_in_provider_required_targets():
    root = Path(__file__).resolve().parents[1]
    source = (root / 'hsoc-stack/tools/qbox-platform/CMakeLists.txt').read_text()
    targets = source.split('set(QBOX_APOLLO_REQUIRED_TARGETS', 1)[1].split(')', 1)[0].split()
    assert 'qmp' in targets
