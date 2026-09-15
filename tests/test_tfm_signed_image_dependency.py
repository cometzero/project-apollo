"""Verify that the signing dependency rebuilds after a raw image changes."""
from pathlib import Path
import re
import shutil
import subprocess

import pytest


def test_raw_image_change_rebuilds_signed_output(tmp_path):
    if not all(shutil.which(tool) for tool in ('cmake', 'ninja', 'cc')):
        pytest.skip('CMake, Ninja and C compiler required')
    source = (Path(__file__).resolve().parents[1] /
              'hsoc-stack/components/system_mgmt/trusted-firmware-m/'
              'bl2/ext/mcuboot/CMakeLists.txt').read_text()
    block = re.search(r'set\(wrapper_depends\s+(.*?)\n    \)', source, re.S).group(1)
    dependency = next(line.strip() for line in block.splitlines()
                      if 'DEPENDS $<TARGET_FILE_DIR:tfm_s>/tfm_s.bin' in line)
    # Use the actual dependency in a tiny native incremental-build fixture.
    (tmp_path / 'CMakeLists.txt').write_text('''
cmake_minimum_required(VERSION 3.20)
project(signing_dependency C)
add_executable(tfm_s main.c)
add_custom_command(OUTPUT ${CMAKE_BINARY_DIR}/tfm_s.bin
  COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/payload ${CMAKE_BINARY_DIR}/tfm_s.bin
  DEPENDS ${CMAKE_SOURCE_DIR}/payload)
add_custom_target(tfm_s_bin DEPENDS ${CMAKE_BINARY_DIR}/tfm_s.bin)
add_custom_target(signing_layout_s)
add_custom_command(OUTPUT signed.bin
  COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_BINARY_DIR}/tfm_s.bin signed.bin
  DEPENDS tfm_s_bin signing_layout_s
  ''' + dependency + ''')
add_custom_target(signed ALL DEPENDS signed.bin)
''')
    (tmp_path / 'main.c').write_text('int main(void) { return 0; }\n')
    payload = tmp_path / 'payload'
    payload.write_text('old firmware')
    build = tmp_path / 'build'
    subprocess.run(['cmake', '-G', 'Ninja', '-S', str(tmp_path), '-B', str(build)],
                   check=True, capture_output=True, timeout=30)
    command = ['cmake', '--build', str(build)]
    subprocess.run(command, check=True, capture_output=True, timeout=30)
    assert (build / 'signed.bin').read_text() == 'old firmware'
    payload.write_text('new firmware with suspend handler')
    subprocess.run(command, check=True, capture_output=True, timeout=30)
    assert (build / 'signed.bin').read_text() == payload.read_text()
