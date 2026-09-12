"""Validate PCIe profile selection without starting QEMU or changing images."""

import importlib
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
LUA = ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua"


@pytest.mark.parametrize("mode,loopback,valid", [
    ("none", False, True), ("port2", False, True),
    ("none", True, True), ("port2", True, False),
    ("port3", False, False), ("both", False, False),
])
def test_pcie_topology(mode, loopback, valid):
    lua = shutil.which("lua")
    if lua is None:
        pytest.skip("Lua interpreter unavailable")
    env = os.environ.copy()
    env.update({
        "QBOX_RDASPEN_ENABLE_AP_CPUS": "true",
        "QBOX_APOLLO_PCIE_IRQ_TEST": "false",
        "QBOX_APOLLO_PCIE_TEST_ENDPOINTS": "false",
        "QBOX_APOLLO_PCIE_BIFURCATION": mode,
        "QBOX_APOLLO_PCIE_EP_LOOPBACK": str(loopback).lower(),
        "QBOX_APOLLO_NVME_IMAGE": "",
    })
    script = """
dofile(arg[1])
assert(platform.ap_pcie_epc.regs.address == 0x30300000)
assert(platform.ap_pcie_epc.outbound.size == 0x400000)
assert(platform.ap_pcie_root_port_1.x_width == '4')
assert(platform.ap_pcie_root_port_4.x_width == '2')
assert(platform.ap_pcie_root_port_6 == nil)
if os.getenv('QBOX_APOLLO_PCIE_EP_LOOPBACK') == 'true' then
    assert(platform.ap_pcie_root_port_2 == nil)
    assert(platform.ap_pcie_test_ep.args[2] == '&platform.ap_pcie_root_port_1')
    assert(platform.ap_pcie_test_ep.args[3] == '&platform.ap_pcie_epc')
else
    assert(platform.ap_pcie_root_port_2.x_width == '4')
    assert(platform.ap_pcie_test_ep == nil)
end
if os.getenv('QBOX_APOLLO_PCIE_BIFURCATION') == 'port2' then
    assert(platform.ap_pcie_root_port_3.x_width == '1')
    assert(platform.ap_pcie_root_port_5.x_width == '1')
else
    assert(platform.ap_pcie_root_port_3.x_width == '2')
    assert(platform.ap_pcie_root_port_5 == nil)
end
"""
    result = subprocess.run([lua, "-", str(LUA)], input=script, env=env,
                            cwd=ROOT, text=True, capture_output=True, timeout=10)
    assert (result.returncode == 0) == valid, result.stderr
    if not valid:
        assert "bifurcation" in result.stderr.lower() or "profiles" in result.stderr


def test_ep_loopback_environment_is_recorded(monkeypatch, tmp_path):
    sys.path.insert(0, str(ROOT))
    runner = importlib.import_module("scripts.run.run_qbox_apollo_fvp_full")
    monkeypatch.setenv("QBOX_APOLLO_PCIE_EP_LOOPBACK", "true")
    args = runner.parse_args(["--out-dir", str(tmp_path)])
    assert runner.full_system_child_environment(args)["QBOX_APOLLO_PCIE_EP_LOOPBACK"] == "true"


@pytest.mark.parametrize("image,nic,valid", [
    ("/tmp/test-nvme.raw", False, True),
    ("relative.raw", False, False),
    ("/tmp/test-nvme.raw", True, False),
])
def test_nvme_uses_fixed_x2_port(image, nic, valid):
    lua = shutil.which("lua")
    if lua is None:
        pytest.skip("Lua interpreter unavailable")
    env = os.environ.copy()
    env.update({
        "QBOX_RDASPEN_ENABLE_AP_CPUS": "true",
        "QBOX_APOLLO_PCIE_IRQ_TEST": "false",
        "QBOX_APOLLO_PCIE_TEST_ENDPOINTS": str(nic).lower(),
        "QBOX_APOLLO_PCIE_BIFURCATION": "port2",
        "QBOX_APOLLO_PCIE_EP_LOOPBACK": "false",
        "QBOX_APOLLO_NVME_IMAGE": image,
        "QBOX_APOLLO_NVME_SERIAL": "test-serial",
    })
    script = """
dofile(arg[1])
assert(platform.ap_nvme_0.moduletype == 'nvme')
assert(platform.ap_nvme_0.args[2] == '&platform.ap_pcie_root_port_4')
assert(platform.ap_nvme_0.image_path == '/tmp/test-nvme.raw')
assert(platform.ap_nvme_0.serial == 'test-serial')
assert(platform.ap_nvme_0.x_speed == '32')
assert(platform.ap_nvme_0.x_width == '2')
assert(platform.ap_pcie_root_port_4.x_width == '2')
assert(platform.ap_pcie_root_port_3.x_width == '1')
"""
    result = subprocess.run([lua, "-", str(LUA)], input=script, env=env,
                            cwd=ROOT, text=True, capture_output=True, timeout=10)
    assert (result.returncode == 0) == valid, result.stderr
    if not valid:
        assert "NVME" in result.stderr or "NVMe" in result.stderr
