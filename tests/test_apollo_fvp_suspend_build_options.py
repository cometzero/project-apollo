"""Exercise the real firmware's opt-in experiment configuration guards."""
from pathlib import Path
import shutil
import subprocess

import pytest


FIRMWARE = (Path(__file__).resolve().parents[1] /
            'hsoc-stack/components/system_mgmt/scp-firmware/product/'
            'automotive-rd/apollo-fvp/si0_ramfw/Firmware.cmake')


@pytest.mark.parametrize('isolate,delay,accepted', [
    ('OFF', '0', True),
    ('ON', '0', True),
    ('ON', '5000000', True),
    ('OFF', '5000000', False),
    ('ON', '-1', False),
    ('ON', 'invalid', False),
    ('ON', '60000001', False),
])
def test_experimental_build_guards(isolate, delay, accepted):
    cmake = shutil.which('cmake')
    if cmake is None:
        pytest.skip('cmake unavailable')
    result = subprocess.run([
        cmake, f'-DSCP_APOLLO_FVP_ISOLATE_CL1={isolate}',
        f'-DAPOLLO_FVP_TEST_SUSPEND_WAKE_US={delay}', '-P', str(FIRMWARE),
    ], capture_output=True, text=True, timeout=20)
    assert (result.returncode == 0) == accepted, result.stderr


@pytest.mark.parametrize('retained', ['ON', 'OFF'])
def test_retention_option_is_explicit(retained):
    result = subprocess.run([
        'cmake', '-DSCP_APOLLO_FVP_ISOLATE_CL1=ON',
        '-DAPOLLO_FVP_TEST_SUSPEND_WAKE_US=5000000',
        f'-DAPOLLO_FVP_AP_SRAM_RETAINED={retained}', '-P', str(FIRMWARE),
    ], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    source = FIRMWARE.with_name('config_scmi_perf.c').read_text()
    assert '.fast_channel_memory_retained = APOLLO_FVP_AP_SRAM_RETAINED' in source
    definitions = FIRMWARE.with_name('CMakeLists.txt').read_text()
    assert 'APOLLO_FVP_AP_SRAM_RETAINED=$<BOOL:${APOLLO_FVP_AP_SRAM_RETAINED}>' in definitions
