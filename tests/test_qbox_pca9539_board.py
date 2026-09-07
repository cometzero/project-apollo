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
assert(p.host_smd_gpio.gpio_out_0.bind == "&board_pca9539.reset_n")
assert(p.board_pca9539.int_n.bind == "&host_smd_gpio.gpio_in_1")
assert(p.host_smd_gpio.pullups == 0x83 and p.host_smd_gpio.init_inputs == 0x43)
assert(p.board_pca9539.gpio_out_0.bind == "&board_pca9539.gpio_in_1")
assert(p.board_pca9539.gpio_out_8.bind == "&board_pca9539.gpio_in_9")
''', text=True)
