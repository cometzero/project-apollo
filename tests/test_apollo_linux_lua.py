"""Check executable Lua composition without loading native modules or firmware."""

import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("cpus", [1, 4, 16])
@pytest.mark.parametrize("disk", ["", "/private/rootfs.wic"])
def test_linux_profile_has_only_ap_cpus_and_resolved_bindings(cpus, disk):
    lua = shutil.which("lua")
    if not lua:
        pytest.skip("Lua interpreter unavailable")
    env = {
        **os.environ,
        "QBOX_RDASPEN_ENABLE_AP_CPUS": "true",
        "QBOX_APOLLO_NUM_CPUS": str(cpus),
        "QBOX_APOLLO_RUNTIME_INJECTION": "false",
        "QBOX_RDASPEN_ROOTFS": disk,
        "QBOX_LINUX_BOOT_STUB": "/private/boot.bin",
        "QBOX_LINUX_KERNEL": "/private/Image",
        "QBOX_LINUX_DTB": "/private/linux.dtb",
    }
    check = r'''
dofile("hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-linux.lua")
local cpus = 0
for name, obj in pairs(platform) do
    if type(obj) == "table" and obj.moduletype == "cpu_arm_cortexA720AE" then
        cpus = cpus + 1
        assert(name:match("^ap_cpu_%d+$"))
        assert(obj.rvbar == 0x80000000 and not obj.start_in_reset)
        assert(obj.psci_conduit == "smc")
    end
end
assert(cpus == tonumber(os.getenv("QBOX_APOLLO_NUM_CPUS")))
assert(not platform.qemu_inst and not platform.si_cl0_qemu_inst)
assert(not platform.si_cl1_qemu_inst and not platform.ap_bl2_reset_loader)
assert((platform.ap_virtioblk_0 ~= nil) == (os.getenv("QBOX_RDASPEN_ROOTFS") ~= ""))
assert(not platform.ap_virtioblk_1)
assert(platform.linux_si_stub.moduletype == "apollo_si_stub")
assert(platform.linux_si_stub.target_socket.address == 0x400b0000)
assert(platform.linux_si_stub.target_socket.size == 0x60000)
assert(platform.linux_si_stub.irq_pbx.bind == "&ap_gic.spi_in_120")
assert(platform.linux_si_stub.irq_mbx.bind == "&ap_gic.spi_in_121")
assert(not platform.linux_si_cl1_pbx and not platform.linux_si_cl1_mbx)
local function walk(t)
    for k, v in pairs(t) do
        if type(v) == "table" then walk(v)
        elseif type(v) == "string" and (k == "bind" or type(k) == "number") then
            for name in v:gmatch("&([%w_]+)%.") do
                assert(name == "platform" or platform[name], "dangling binding: "..v)
            end
        end
    end
end
walk(platform)
'''
    result = subprocess.run(
        [lua, "-"], input=check, text=True, capture_output=True, cwd=ROOT, env=env
    )
    assert result.returncode == 0, result.stdout + result.stderr
