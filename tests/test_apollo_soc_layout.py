"""Exercise the Apollo SoC/VP/Board composition and its failure contracts."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import shutil

import pytest


ROOT = Path(__file__).resolve().parents[1]
APOLLO = ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo"
SPEC = importlib.util.spec_from_file_location(
    "apollo_soc_layout_descriptor", ROOT / "scripts/test/apollo_lua_descriptor.py"
)
assert SPEC and SPEC.loader
DESCRIPTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DESCRIPTOR)
LINUX_ENV = {
    "QBOX_LINUX_BOOT_STUB": "/test/boot.bin",
    "QBOX_LINUX_KERNEL": "/test/Image",
    "QBOX_LINUX_DTB": "/test/apollo.dtb",
}


@pytest.fixture
def sources():
    if not any(shutil.which(name) for name in ("lua5.4", "lua5.3", "lua", "luajit")):
        pytest.skip("Lua interpreter unavailable")
    return DESCRIPTOR.read_sources(APOLLO)


def evaluate_contract(sources, body, *, environment=None):
    return DESCRIPTOR.evaluate_modules(
        {**sources, "contract.lua": body},
        entrypoint="contract.lua", environment=environment,
    )


@pytest.mark.parametrize("entry", ["apollo-qvp-saturn-v.lua", "apollo-qvp-linux.lua"])
def test_composition_exports_only_platform(sources, entry):
    evaluate_contract(sources, f'''
local before = {{}}
for key, value in pairs(_G) do before[key] = value end
dofile("./{entry}")
for key, value in pairs(_G) do
    assert(key == "platform" or before[key] == value, "global changed: " .. key)
end
for key, value in pairs(before) do
    assert(_G[key] == value, "global removed or changed: " .. key)
end
''', environment=LINUX_ENV)


def test_options_are_private_and_preserve_false(sources):
    evaluate_contract(sources, '''
local options = dofile("./vp/options.lua")
local first = options.create("./")
local second = options.create("./")
assert(first.options ~= second.options)
assert(first.options.host_memory_dmi == false)
assert(first.options.rse_smd_counter_mirror == false)
first.options.host_sram_shared_memory = true
assert(first.options.host_sram_shared_memory_enabled("") == true)
assert(second.options.host_sram_shared_memory_enabled("") == false)
platform = {}
''', environment={
        "QBOX_RDASPEN_HOST_MEMORY_DMI": "false",
        "QBOX_APOLLO_RSE_SMD_COUNTER_MIRROR": "false",
        "QBOX_RDASPEN_HOST_SRAM_SHARED_MEMORY": "false",
    })


def test_existing_hardware_object_is_rejected(sources):
    with pytest.raises(DESCRIPTOR.DescriptorError, match="duplicate Apollo object"):
        evaluate_contract(sources, '''
local ctx = dofile("./vp/options.lua").create("./")
platform = {host_ap_shared_sram = {moduletype = "sentinel"}}
dofile("./soc/hw-block/ap_compute/memory.lua").define(ctx, platform)
''')


SOC_STANDALONE = '''
local load = dofile
dofile = function(path)
    assert(path:match("^%%./soc/"), "SoC loaded an external layer: " .. path)
    return load(path)
end
os.getenv = function() error("SoC requested environment") end
assert(io == nil, "host file API must be unavailable")
local soc = dofile("./soc/apollo.lua")
local config = soc.default_config()
%s
platform = soc.create(config)
assert(platform.ap_gic.num_cpus == config.options.AP_NUM_CPUS)
for i = 0, config.options.AP_NUM_CPUS - 1 do
    assert(platform["ap_cpu_" .. i].moduletype == "cpu_arm_cortexA720AE")
end
assert(platform["ap_cpu_" .. config.options.AP_NUM_CPUS] == nil)
assert(platform.rse_cpu_pass.cpu_0.moduletype == "ApolloRseCPU")
assert(platform.si_cl0_cpu_0.moduletype == "cpu_arm_cortexR82")
assert(platform.si_cl1_cpu_3.moduletype == "cpu_arm_cortexR82")
assert(platform.si_cl0_gic.num_cpus == 1)
assert(platform.si_cl1_gic.num_cpus == 4)
for _, name in ipairs({"rse_itcm", "rse_dtcm", "host_ap_shared_sram",
                       "si_cl0_sram", "si_cl1_sram"}) do
    assert(platform[name].moduletype == "gs_memory", name)
end
assert(platform.rse_boot_flash.moduletype == "strata_flash_j3")
assert(platform.host_ap_rse_mhu_pbx.protocol == "doorbell-bridge")
assert(platform.host_ap_si_scmi_mhu_pbx.system_reset.bind ~= nil)
assert(platform.ap_bl2_reset_loader == nil and platform.si_cl0_loader == nil)
assert(platform.board_i2c0 == nil)
%s
-- Socket names can be implicit C++ model children, but their owning Lua
-- object must exist. Descend through explicit Container boundaries as well.
local function reference(target, scope)
    local parts = {}
    for part in target:sub(2):gmatch("[^.]+") do parts[#parts + 1] = part end
    local owner, index = scope, 1
    if parts[1] == "platform" then owner, index = platform, 2 end
    assert(owner[parts[index]], "missing SoC reference: " .. target)
    owner = owner[parts[index]]
    index = index + 1
    while type(owner) == "table" and owner.moduletype == "Container" and
          index < #parts do
        assert(owner[parts[index]], "missing SoC container child: " .. target)
        owner = owner[parts[index]]
        index = index + 1
    end
end
local function scan(value, scope)
    if type(value) == "string" and value:sub(1, 1) == "&" then
        for target in value:gmatch("[^;]+") do reference(target, scope) end
    elseif type(value) == "table" then
        assert(value.moduletype ~= "loader", "SoC contains a host loader")
        for key, child in pairs(value) do
            local child_scope = scope
            if value.moduletype == "Container" and type(child) == "table" and
               child.moduletype then child_scope = value end
            scan(child, child_scope)
        end
    end
end
scan(platform, platform)
'''


@pytest.mark.parametrize("cpus", [16, 4])
def test_soc_constructs_without_host_services(sources, cpus):
    configure = "" if cpus == 16 else (
        f"config.options.AP_NUM_CPUS = {cpus}; config.options.AP_GIC_NUM_CPUS = {cpus}"
    )
    evaluate_contract(sources, SOC_STANDALONE % (configure, ""))


@pytest.mark.parametrize("backend", ["systemc-strata", "qemu-cfi-local"])
def test_soc_local_backends_resolve_without_vp(sources, backend):
    configure = (
        'config.options.rse_local_boot_flash = true; '
        'config.options.rse_local_crypto = true; '
        'config.options.cc3xx_backend = "qemu-native"; '
        f'config.options.rse_flash_backend = "{backend}"'
    )
    body = SOC_STANDALONE.replace(
        'assert(platform.rse_boot_flash.moduletype == "strata_flash_j3")',
        'assert(platform.rse_cpu_pass.remote_main_router and platform.rse_boot_flash == nil)',
    )
    evaluate_contract(sources, body % (configure, ""))


@pytest.mark.parametrize(("target", "message"), [
    ("&missing.reset", "missing SoC reference"),
    ("&rse_cpu_pass.missing.reset", "missing SoC container child"),
])
def test_soc_reference_check_detects_dangling_reset(sources, target, message):
    mutation = f'platform.host_ap_si_scmi_mhu_pbx.system_reset.bind = "{target}"'
    with pytest.raises(DESCRIPTOR.DescriptorError, match=message):
        evaluate_contract(sources, SOC_STANDALONE % ("", mutation))


@pytest.mark.parametrize(("mutation", "message"), [
    ("config.options.enable_ap_cpus = false; config.options.AP_NUM_CPUS = 0; "
     "config.options.AP_GIC_NUM_CPUS = 1", "complete Apollo SoC requires AP CPUs"),
    ("config.options.AP_NUM_CPUS = 17", "Apollo AP CPU count"),
    ("config.options.AP_NUM_CPUS = 1.5", "Apollo AP CPU count"),
    ("config.options.AP_GIC_NUM_CPUS = 4", "Apollo GIC CPU count"),
    ('config.options.rse_flash_backend = "qemu-cfi-local"', "requires RSE local boot flash"),
    ('config.options.smmu_backend = "invalid"', "unsupported SMMU backend"),
])
def test_invalid_standalone_soc_configuration(sources, mutation, message):
    with pytest.raises(DESCRIPTOR.DescriptorError, match=message):
        evaluate_contract(sources, SOC_STANDALONE % (mutation, ""))


def test_soc_sources_exclude_host_policy(sources):
    for path, source in sources.items():
        if not path.startswith("soc/"):
            continue
        assert not re.search(r"\bgetenv\w*\b|vp/|board/|\bio\.open\b", source), path
        assert not re.search(
            r'moduletype\s*=\s*"(?:loader|char_backend_\w+)"', source
        ), path
        assert not re.search(
            r"\b(?:bin_file|backing_file|blkdev_str|map_file|trace_file|"
            r"trace_pc_file|stats_file|otp_image)\s*=", source
        ), path


@pytest.mark.parametrize("proxy", [False, True])
def test_system_mgmt_mailbox_modes_and_runtime_inputs(sources, proxy):
    evaluate_contract(sources, '''
dofile("./apollo-qvp-saturn-v.lua")
local proxy = os.getenv("QBOX_RDASPEN_RSE_PS_PROXY") == "true"
local pbx = platform.host_ap_rse_mhu_pbx
local mbx = platform.host_ap_rse_mhu_mbx
assert(pbx.protocol == (proxy and "rse-ps-proxy" or "doorbell-bridge"))
assert(mbx.protocol == pbx.protocol)
assert(pbx.pair == (proxy and "ap_rse_ps_proxy" or "ap_s_to_rse"))
assert(mbx.pair == (proxy and "ap_rse_ps_proxy" or "rse_to_ap_s"))
assert(mbx.doorbell_commit_on_notify == not proxy)
for _, name in ipairs({"host_si_atu", "host_ap_atu", "host_smdexp2smd_atu"}) do
    assert(platform[name].trace_address_min == 4096)
    assert(platform[name].trace_address_max == 8192)
end
-- Saturn-V pulls GPIO0/1 high while retaining the other input bits.
assert(platform.host_smd_gpio.init_inputs == 167)
assert(platform.host_smd_gpio.irq.bind == "&ap_gic.spi_in_193")
assert(platform.host_smd_gpio_cold_reset.args[1] == "&platform.host_smd_gpio")
assert(platform.host_ap_rse_mailbox.moduletype == "gs_memory")
assert(platform.host_ap_rse_mailbox.target_socket.address == 0x0FFFE0000)
assert(platform.host_ap_rse_mailbox.dmi_allow == false)
''', environment={
        "QBOX_RDASPEN_RSE_PS_PROXY": str(proxy).lower(),
        "QBOX_RDASPEN_ATU_TRACE_ADDRESS_MIN": "4096",
        "QBOX_RDASPEN_ATU_TRACE_ADDRESS_MAX": "8192",
        "QBOX_APOLLO_SMD_GPIO_INIT_INPUTS": "165",
    })


def test_si_cl0_protected_view_and_power_reset_order(sources):
    evaluate_contract(sources, '''
dofile("./apollo-qvp-saturn-v.lua")
assert(platform.si_cl0_cpu_0.mem.bind ==
       "&si_cl0_ni710ae_primary_nci.protected_target_socket")
local gic = platform.si_cl0_gic
assert(gic.dist_iface.address == 0x30100000)
assert(gic.dist_iface.aliases.view0_functional.address == 0x30000000)
assert(gic.dist_iface.priority == 10)
assert(platform.si_gic_multiview.view0_dist_iviewr.priority == 0)
assert(platform.si_gic_multiview.view0_redist_1.priority == 20)
local cl0 = platform.host_si_cl0_core0_ppu
assert(cl0.power_on_load.bind == "&si_cl0_loader.reset")
assert(cl0.power_on_reset.bind == "&si_cl0_cpu_0.reset")
local ap = platform.si_cl0_ap_cluster0_core0_ppu
assert(ap.power_on_load.bind == "&host_reset_ctrl.ap_power_reset")
assert(ap.power_on_load_pulse_width_ns == 1)
assert(ap.power_on_load_to_reset_delay_ns == 1)
assert(ap.power_on_reset.bind == "&ap_cpu_0.reset")
assert(platform.si_cl0_smcf_smd_mgi.moduletype == "host_smcf_mgi")
assert(platform.si_cl0_smcf_ap_cluster_mgi_3.group_id == 4)
''')


def test_si_cl1_gic_hipc_and_ordered_reset(sources):
    evaluate_contract(sources, '''
dofile("./apollo-qvp-saturn-v.lua")
local gic = platform.si_cl1_gic
assert(gic.num_cpus == 4 and gic.num_spi == 128)
for i = 0, 3 do
    assert(gic["redist_iface_" .. i].address == 0x30260000 + i * 0x20000)
    assert(gic["redist_iface_" .. i].size == 0x20000)
    assert(platform["si_cl1_cpu_" .. i].mp_affinity == 0x10000 + i * 0x100)
    assert(platform["si_cl1_cpu_" .. i].irq_timer_phys_out.bind ==
           "&si_cl1_gic.ppi_in_cpu_" .. i .. "_20")
end
local bridge = platform.si_cl1_hipc_bridge
assert(bridge.target_socket.address == 0xE0130000)
assert(bridge.target_socket.size == 0x80000)
assert(bridge.mapped_base_addr == 0x100000)
assert(bridge.initiator_socket.bind == "&ap_router.target_socket")
local positions = {}
local order = 0
for target in platform.apollo_system_reset_fanout.reset_out.bind:gmatch("[^;]+") do
    assert(positions[target] == nil, "duplicate reset: " .. target)
    order = order + 1
    positions[target] = order
end
assert(positions["&si_cl1_core3_ppu.reset"] < positions["&si_cl0_uart.reset"])
assert(positions["&si_cl1_uart.reset"] < positions["&si_gic_multiview.reset"])
assert(positions["&si_gic_multiview.reset"] < positions["&si_cl0_qemu_inst.reset"])
assert(positions["&si_cl0_qemu_inst.reset"] < positions["&si_cl1_qemu_inst.reset"])
assert(positions["&si_cl1_qemu_inst.reset"] < positions["&ap_rgic2lgic_messreg.reset"])
''')


@pytest.mark.parametrize("vm_width", [18, 21])
@pytest.mark.parametrize("backend", ["qemu-cfi-local", "systemc-strata"])
@pytest.mark.parametrize("mirror", ["true", "false"])
def test_rse_memory_and_reset_domains(sources, vm_width, backend, mirror):
    evaluate_contract(sources, '''
dofile("./apollo-qvp-saturn-v.lua")
local cpu = platform.rse_cpu_pass
assert(cpu.rse_nvic_cold_reset.args[1] == "&cpu_0.cpu.nvic")
assert(platform.rse_nvic_cold_reset == nil)
local rss = platform.rse_sys_rss_reset_fanout.reset_out.bind
local aon = platform.rse_aon_reset_fanout.reset_out.bind
assert(rss:find("&rse_cpu_pass.rse_timer_2.reset", 1, true))
assert(not rss:find("rse_timer_3", 1, true))
assert(aon:find("&rse_cpu_pass.rse_timer_3.reset", 1, true))
assert(not aon:find("rse_timer_2", 1, true))
assert((rss:find("rse_pflash_cold_reset", 1, true) ~= nil) ==
       (cpu.rse_pflash_cold_reset ~= nil))
assert((aon:find("rse_local_system_counter", 1, true) ~= nil) ==
       (cpu.rse_local_system_counter ~= nil))
local size = 2 ^ tonumber(os.getenv("QBOX_RDASPEN_RSE_VMADDRWIDTH"))
assert(platform.rse_vm0.target_socket.size == size)
assert(platform.rse_vm1.target_socket.size == size)
assert(platform.rse_vm1.target_socket.address == 0x31000000 + size)
''', environment={
        "QBOX_RDASPEN_RSE_VMADDRWIDTH": str(vm_width),
        "QBOX_RDASPEN_RSE_FLASH_BACKEND": backend,
        "QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH": "true",
        "QBOX_APOLLO_RSE_SMD_COUNTER_MIRROR": mirror,
    })


@pytest.mark.parametrize("cpus", [1, 4, 16])
@pytest.mark.parametrize("backend", ["systemc-mmu720ae", "qemu-arm-smmuv3"])
def test_ap_interrupt_geometry_and_dma_routing(sources, cpus, backend):
    evaluate_contract(sources, '''
dofile("./apollo-qvp-saturn-v.lua")
local count = tonumber(os.getenv("QBOX_APOLLO_NUM_CPUS"))
local gic = platform.ap_gic
assert(gic.num_cpus == count)
for i = 0, count - 1 do
    local window = gic["redist_iface_" .. i]
    assert(window.address == 0x20880000 + i * 0x40000)
    assert(window.bind == "&ap_router.initiator_socket")
    assert(platform["ap_cpu_" .. i].mem.bind == "&ap_router.target_socket")
end
assert(gic["redist_iface_" .. count] == nil)
assert(platform.ap_gic_multiview.view0_redist_15 ~= nil)
assert((platform.ap_gic_multiview.inactive_redists ~= nil) == (count < 16))
if os.getenv("QBOX_RDASPEN_SMMU_BACKEND") == "systemc-mmu720ae" then
    assert(platform.ap_gpex_0.bus_master.bind == "&ap_smmu_lti00.upstream_socket")
    assert(platform.ap_smmu_lti00.downstream_socket.bind == "&ap_router.target_socket")
else
    assert(platform.ap_gpex_0.bus_master.bind == "&ap_router.target_socket")
    assert(platform.ap_smmu_0.args[2] == "&platform.ap_gpex_0")
end
assert(platform.host_ap_flash.target_socket.bind == "&ap_router.initiator_socket")
assert(platform.ap_bl2_reset_loader.initiator_socket.bind == "&ap_router.target_socket")
''', environment={
        "QBOX_APOLLO_NUM_CPUS": str(cpus),
        "QBOX_RDASPEN_SMMU_BACKEND": backend,
    })


@pytest.mark.parametrize(("module", "ports", "message"), [
    ("pca9539", "{}", "Saturn-V requires AP I2C0"),
    ("pca9539", "{ap_dw_i2c_0 = {}}", "Saturn-V requires SMD GPIO"),
    ("tps6594", "{}", "Saturn-V PMIC requires the SI host I2C extension"),
    ("tps6594", "{si_cl0_dw_i2c_0 = {}}", "Saturn-V PMIC requires the SI host GPIO extension"),
])
def test_board_requires_declared_soc_ports(sources, module, ports, message):
    with pytest.raises(DESCRIPTOR.DescriptorError, match=re.escape(message)):
        evaluate_contract(sources, f'''
platform = {ports}
dofile("./board/hw-block/{module}.lua").connect(platform)
''')


@pytest.mark.parametrize(("module", "ports"), [
    ("pca9539", "{ap_dw_i2c_0 = {}, ap_dw_i2c_0_eeprom = {}, host_smd_gpio = {}}"),
    ("tps6594", "{si_cl0_dw_i2c_0 = {}, si_cl0_pmic_gpio = {}}"),
])
def test_board_population_cannot_be_defined_twice(sources, module, ports):
    with pytest.raises(DESCRIPTOR.DescriptorError, match="duplicate"):
        evaluate_contract(sources, f'''
platform = {ports}
local board = dofile("./board/hw-block/{module}.lua")
board.connect(platform)
board.connect(platform)
''')


def test_source_relative_includes_from_foreign_directory(sources, monkeypatch, tmp_path):
    # No module exists in this cwd. Both the entry and includes are relocated in
    # the evaluator's allowlist to expose accidental cwd-relative dofile calls.
    monkeypatch.chdir(tmp_path)
    prefix = "relocated/platforms/apollo/"
    result = DESCRIPTOR.evaluate_modules(
        {prefix + name: text for name, text in sources.items()},
        entrypoint=prefix + "apollo-qvp-saturn-v.lua",
    )
    executed = result["executed"]
    assert "./" + prefix + "soc/hw-block/ap_compute/cpu.lua" in executed
    assert "./" + prefix + "board/hw-block/pca9539.lua" in executed
    assert all(name.startswith("./" + prefix) for name in executed)


@pytest.mark.parametrize(("environment", "message"), [
    ({"QBOX_RDASPEN_SMMU_BACKEND": "invalid"}, "QBOX_RDASPEN_SMMU_BACKEND must be"),
    ({"QBOX_RDASPEN_CC3XX_BACKEND": "invalid"}, "QBOX_RDASPEN_CC3XX_BACKEND must be"),
    ({"QBOX_RDASPEN_RSE_FLASH_BACKEND": "invalid"}, "QBOX_RDASPEN_RSE_FLASH_BACKEND must be"),
    ({"QBOX_APOLLO_NUM_CPUS": "1.5"}, "QBOX_APOLLO_NUM_CPUS must be an integer in 1..16"),
    ({"QBOX_APOLLO_NUM_CPUS": "17"}, "QBOX_APOLLO_NUM_CPUS must be an integer in 1..16"),
    ({"QBOX_APOLLO_NUM_CPUS": "invalid"}, "QBOX_APOLLO_NUM_CPUS must be numeric"),
    ({"QBOX_APOLLO_MONITOR_PORT": "65536"}, "QBOX_APOLLO_MONITOR_PORT must be an integer"),
    ({"QBOX_APOLLO_RUNTIME_INJECTION": "true"}, "QBOX_APOLLO_RUNTIME_INJECTION requires QBOX_APOLLO_MONITOR"),
    ({"QBOX_APOLLO_NVME_IMAGE": "relative.img"}, "QBOX_APOLLO_NVME_IMAGE must be an absolute image path"),
])
def test_invalid_configuration_fails_before_elaboration(sources, environment, message):
    with pytest.raises(DESCRIPTOR.DescriptorError, match=re.escape(message)):
        DESCRIPTOR.evaluate_modules(
            sources, entrypoint="apollo-qvp-saturn-v.lua", environment=environment,
        )


@pytest.mark.parametrize(("address", "model", "message"), [
    ("0x48", "dw_i2c_eeprom", "I2C address collision"),
    ("0x4a", "dw_i2c_eeprom", "I2C address collision"),
    ("0x7e", "tps6594", "invalid I2C address range"),
    ("1.5", "dw_i2c_eeprom", "invalid I2C address range"),
])
def test_board_i2c_aliases_and_address_ranges(sources, address, model, message):
    with pytest.raises(DESCRIPTOR.DescriptorError, match=message):
        evaluate_contract(sources, f'''
platform = {{
    bus = {{moduletype = "i2c_bus"}},
    pmic = {{moduletype = "tps6594", address = 0x48,
             i2c_socket = {{bind = "&bus.initiator_socket"}}}},
    candidate = {{moduletype = "{model}", address = {address},
                  i2c_socket = {{bind = "&bus.initiator_socket"}}}},
}}
dofile("./board/hw-block/validate.lua").i2c_bus(platform, "bus")
''')


def test_i2c_addresses_are_scoped_to_each_bus(sources):
    evaluate_contract(sources, '''
platform = {
    first_bus = {moduletype = "i2c_bus"},
    second_bus = {moduletype = "i2c_bus"},
    first = {moduletype = "dw_i2c_eeprom", address = 0x50,
             i2c_socket = {bind = "&first_bus.initiator_socket"}},
    second = {moduletype = "dw_i2c_eeprom", address = 0x50,
              i2c_socket = {bind = "&second_bus.initiator_socket"}},
}
local validator = dofile("./board/hw-block/validate.lua")
validator.i2c_bus(platform, "first_bus")
validator.i2c_bus(platform, "second_bus")
''')


def test_full_composition_runs_board_address_validation(sources):
    source = sources["board/hw-block/pca9539.lua"]
    assert "address = 0x74" in source
    sources["board/hw-block/pca9539.lua"] = source.replace(
        "address = 0x74", "address = 0x50", 1
    )
    with pytest.raises(DESCRIPTOR.DescriptorError, match="I2C address collision on board_i2c0"):
        DESCRIPTOR.evaluate_modules(sources, entrypoint="apollo-qvp-saturn-v.lua")


SI_IRQ_CONTRACT = '''
dofile("./apollo-qvp-saturn-v.lua")
local expected = {
    {"si_cl0_timer_cntbase", "irq", 0, 34},
    {"si_cl0_watchdog", "ws0", 0, 37},
    {"si_cl0_uart", "irq", 0, 40},
    {"si_cl1_uart", "irq", 1, 39},
    {"si_cl0_vmcu_uart", "irq", 0, 41},
    {"si_cl0_vmcu_gpio", "irq", 0, 42},
    {"si_cl0_vmcu_spi", "irq", 0, 43},
    {"si_cl1_hipc_mhu_pbx", "irq", 1, 72},
    {"si_cl1_hipc_mhu_mbx", "irq", 1, 73},
    {"si_cl1_pfdi_mhu_pbx", "irq", 1, 82},
    {"si_cl0_ap_ns_mhu_pbx", "irq", 0, 96},
    {"si_cl0_ap_ns_mhu_mbx", "irq", 0, 97},
    {"si_cl0_ap_scmi_mhu_pbx", "irq", 0, 98},
    {"si_cl0_ap_scmi_mhu_mbx", "irq", 0, 99},
    {"si_cl0_ap_pfdi_monitor_mhu_pbx", "irq", 0, 102},
    {"si_cl0_ap_pfdi_monitor_mhu_mbx", "irq", 0, 103},
    {"si_cl0_rse_mhu_mbx", "irq", 0, 105},
    {"si_cl0_pfdi_mhu_mbx", "irq", 0, 107},
    {"si_cl0_fmu", "critical_irq", 0, 128},
    {"si_cl0_fmu", "non_critical_irq", 0, 129},
}
for cluster = 0, 3 do
    table.insert(expected, {"si_cl0_ap_ras_cluster" .. cluster, "cluster_irq", 0, 325 + 2 * cluster})
    local prefix = "si_cl0_ap_cluster" .. cluster
    table.insert(expected, {prefix .. "_ppu", "irq", 0, 260 + 5 * cluster})
    for core = 0, 3 do
        table.insert(expected, {prefix .. "_core" .. core .. "_ppu", "irq", 0, 261 + 5 * cluster + core})
    end
end
local owners = {}
for _, route in ipairs(expected) do
    local controller = "si_cl" .. route[3] .. "_gic"
    local index = route[4] - 32
    assert(index >= 0 and index < platform[controller].num_spi)
    local target = "&" .. controller .. ".spi_in_" .. index
    assert(not owners[target], "duplicate SI SPI: " .. target)
    owners[target] = true
    assert(platform[route[1]][route[2]].bind == target, "SI IRQ mismatch: " .. route[1])
end
local watchdog = platform.ap_ns_watchdog_ws1_fanout.signal_out.bind
assert(watchdog == "&ap_gic.spi_in_51;&si_cl0_gic.spi_in_289")
assert(not owners["&si_cl0_gic.spi_in_289"])
owners["&si_cl0_gic.spi_in_289"] = true
-- Check every actual SI SPI binding, including fanout entries.
local seen = {}
local function scan(value)
    if type(value) ~= "table" then return end
    for key, child in pairs(value) do
        if key == "bind" and type(child) == "string" then
            for target in child:gmatch("[^;]+") do
                if target:match("^&si_cl[01]_gic%.spi_in_%d+$") then
                    assert(owners[target], "unexpected SI SPI: " .. target)
                    assert(not seen[target], "duplicate SI binding: " .. target)
                    seen[target] = true
                end
            end
        elseif type(child) == "table" then scan(child) end
    end
end
scan(platform)
for target in pairs(owners) do assert(seen[target], "missing SI SPI: " .. target) end
local ppis = {sec = 29, phys = 20, virt = 27, hyp = 19}
for cluster = 0, 1 do
    for cpu = 0, (cluster == 0 and 0 or 3) do
        local device = platform["si_cl" .. cluster .. "_cpu_" .. cpu]
        for timer, intid in pairs(ppis) do
            assert(device["irq_timer_" .. timer .. "_out"].bind ==
                   "&si_cl" .. cluster .. "_gic.ppi_in_cpu_" .. cpu .. "_" .. intid)
        end
    end
end
'''


@pytest.mark.parametrize("external_vmcu", [False, True])
def test_si_irq_connections(sources, external_vmcu):
    environment = {}
    if external_vmcu:
        environment = {
            "QBOX_APOLLO_VMCU_SAFETY_ENDPOINT": "127.0.0.1:44002",
            "QBOX_APOLLO_VMCU_GPIO_ENDPOINT": "127.0.0.1:44003",
        }
    evaluate_contract(sources, SI_IRQ_CONTRACT, environment=environment)


@pytest.mark.parametrize(("device", "target"), [
    ("si_cl1_uart", "&si_cl1_gic.spi_in_8"),
    ("si_cl1_uart", "&si_cl0_gic.spi_in_7"),
    ("si_cl0_vmcu_spi", "&si_cl0_gic.spi_in_12"),
    ("si_cl0_vmcu_spi", "&si_cl1_gic.spi_in_11"),
])
def test_si_irq_contract_rejects_wrong_index_or_owner(sources, device, target):
    mutation = f'platform.{device}.irq.bind = "{target}"\n'
    body = SI_IRQ_CONTRACT.replace('local expected = {', mutation + 'local expected = {', 1)
    with pytest.raises(DESCRIPTOR.DescriptorError, match=f"SI IRQ mismatch: {device}"):
        evaluate_contract(sources, body)


def test_si_irq_contract_rejects_duplicate_binding(sources):
    mutation = 'platform.unexpected_irq = {bind = "&si_cl1_gic.spi_in_7"}\n'
    body = SI_IRQ_CONTRACT.replace('local expected = {', mutation + 'local expected = {', 1)
    with pytest.raises(DESCRIPTOR.DescriptorError, match="duplicate SI binding"):
        evaluate_contract(sources, body)
