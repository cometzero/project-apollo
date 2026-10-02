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
local hw = dofile("./soc/hw-block/ap_compute/map.lua").create(ctx.options)
platform = {host_ap_shared_sram = {moduletype = "sentinel"}}
dofile("./soc/hw-block/ap_compute/memory.lua").define(ctx, platform, hw)
''')


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
