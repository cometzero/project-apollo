"""Exercise the board composition without starting QBox."""
from pathlib import Path
import subprocess


def test_board_wiring():
    root = Path(__file__).resolve().parents[1]
    subprocess.run(["lua", "-"], cwd=root, check=True, input=r'''
local board = dofile("hsoc-stack/tools/qbox-platform/platforms/apollo/board/pca9539.lua")
local empty = {}
board.connect(empty)
assert(next(empty) == nil)
local p = {
    ap_dw_i2c_0 = {}, ap_dw_i2c_0_eeprom = {},
    host_smd_gpio = {pullups = 0x80, init_inputs = 0x40},
}
board.connect(p)
assert(p.ap_dw_i2c_0.i2c_socket.bind == "&board_i2c0.target_socket")
assert(p.ap_dw_i2c_0_eeprom.i2c_socket.bind == "&board_i2c0.initiator_socket")
assert(p.board_pca9539.i2c_socket.bind == "&board_i2c0.initiator_socket")
assert(p.board_pca9539.address == 0x74)
assert(p.ap_dw_i2c_0_eeprom.write_cycle == "5 ms")
assert(p.host_smd_gpio.gpio_out_0.bind == "&board_pca9539.reset_n")
assert(p.board_pca9539.int_n.bind == "&host_smd_gpio.gpio_in_1")
assert(p.host_smd_gpio.pullups == 0x83 and p.host_smd_gpio.init_inputs == 0x43)
assert(p.board_pca9539.gpio_out_0.bind == "&board_pca9539.gpio_in_1")
assert(p.board_pca9539.gpio_out_8.bind == "&board_pca9539.gpio_in_9")

local pmic = dofile("hsoc-stack/tools/qbox-platform/platforms/apollo/board/tps6594.lua")
local absent = {}
pmic.connect(absent)
assert(next(absent) == nil)
p.si_cl0_router = {}
p.si_cl0_dw_i2c_0 = {}
p.si_cl0_pmic_gpio = {pullups = 1, init_inputs = 1}
pmic.connect(p)
assert(p.board_tps6594.address == 0x48)
assert(p.board_tps6594.i2c_socket.bind == "&board_si_i2c0.initiator_socket")
assert(p.board_tps6594.int_n.bind == "&si_cl0_pmic_gpio.gpio_in_0")
assert(p.board_tps6594.gpio_out_0.bind == "&board_tps6594.gpio_in_1")
assert(p.board_tps6594.gpio_out_8.bind == "&board_tps6594.gpio_in_9")
assert(p.host_smd_gpio.pullups == 0x83 and p.host_smd_gpio.init_inputs == 0x43)
assert(p.si_cl0_pmic_gpio.pullups == 1 and p.si_cl0_pmic_gpio.init_inputs == 1)
assert(p.si_cl0_dw_i2c_0.i2c_socket.bind == "&board_si_i2c0.target_socket")
local used = {[0x74] = true}
for index, address in ipairs({0x48}) do
    local name = "board_tps6594" .. (index == 1 and "" or "_" .. (index - 1))
    local device = p[name]
    assert(device.address == address)
    assert(device.i2c_socket.bind == "&board_si_i2c0.initiator_socket")
    assert(device.int_n.bind == "&si_cl0_pmic_gpio.gpio_in_" .. (index - 1))
    assert(device.gpio_out_0.bind == "&" .. name .. ".gpio_in_1")
    assert(device.gpio_out_8.bind == "&" .. name .. ".gpio_in_9")
    for alias = address, address + 4 do
        assert(not used[alias])
        used[alias] = true
    end
end
for index = 1, 3 do
    assert(p["board_tps6594_" .. index] == nil)
end
local pmic_count = 0
for _, device in pairs(p) do
    if device.moduletype == "tps6594" then
        pmic_count = pmic_count + 1
    end
end
assert(pmic_count == 1)
for index = 1, 2 do
    local device = p["ap_dw_i2c_0_eeprom_" .. index]
    assert(device.address == 0x50 + index)
    assert(not used[device.address])
    used[device.address] = true
    assert(device.write_cycle == "5 ms")
    assert(device.size == 256 and device.address_width == 8 and device.page_size == 8)
    assert(device.i2c_socket.bind == "&board_i2c0.initiator_socket")
end
''', text=True)
