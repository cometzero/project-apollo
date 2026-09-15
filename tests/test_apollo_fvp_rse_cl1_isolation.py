"""Host-execute the actual RSE image-selection hook in both configurations."""
import ctypes
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
TFM = ROOT / 'hsoc-stack/components/system_mgmt/trusted-firmware-m'
SOURCE = TFM / 'platform/ext/target/arm/rse/automotive_rd/apollo-fvp/bl2/boot_hal_bl2.c'


@pytest.fixture(params=[0, 1])
def selection(request, tmp_path):
    cc = shutil.which('gcc')
    if not cc:
        pytest.skip('host gcc unavailable')
    source = SOURCE.read_text()
    actual = source[source.index('bool boot_platform_should_load_image('):]
    unit = '''
#include <stdint.h>
#include <stdbool.h>
#define RSE_FIRMWARE_NON_SECURE_ID 1
#define RSE_FIRMWARE_SI_CL0_ID 3
#define RSE_FIRMWARE_SI_CL1_ID 4
#define RSE_FIRMWARE_COUNT 5
#define BOOT_LOG_INF(...) ((void)0)
#define BOOT_LOG_ERR(...) ((void)0)
#define BOOT_LOG_WRN(...) ((void)0)
static int preparation_error;
static unsigned prepares, presence_checks;
static bool present=true;
static int boot_platform_si_pre_load(void){prepares++;return preparation_error;}
static bool check_si_cl1_is_present(void){presence_checks++;return present;}
void reset(int error,bool exists){prepares=0;presence_checks=0;preparation_error=error;present=exists;}
unsigned preparations(void){return prepares;}
unsigned checks(void){return presence_checks;}
''' + actual
    output = tmp_path / 'selection.so'
    subprocess.run([cc, '-shared', '-fPIC', '-Werror', '-x', 'c',
                    f'-DAPOLLO_FVP_ISOLATE_CL1={request.param}', '-o', str(output), '-'],
                   input=unit, text=True, capture_output=True, check=True, timeout=20)
    lib = ctypes.CDLL(str(output))
    lib.boot_platform_should_load_image.restype = ctypes.c_bool
    return request.param, lib


def test_cl1_preserves_shared_si_initialization(selection):
    isolated, lib = selection
    lib.reset(0, True)
    assert lib.boot_platform_should_load_image(4) == (not isolated)
    assert lib.preparations() == 1
    assert lib.checks() == (not isolated)


def test_shared_initialization_failure_still_skips(selection):
    _, lib = selection
    lib.reset(1, True)
    assert not lib.boot_platform_should_load_image(4)
    assert lib.preparations() == 1
    assert lib.checks() == 0


def test_other_image_selection_unchanged(selection):
    _, lib = selection
    for image, expected in [(0, True), (1, False), (2, True), (3, True), (5, False)]:
        lib.reset(0, True)
        assert lib.boot_platform_should_load_image(image) == expected
        assert lib.preparations() == 0


def test_generic_loader_checks_selection_before_preload():
    source = (TFM / 'bl2/ext/mcuboot/bl2_main.c').read_text()
    selection = source.index('if (!boot_platform_should_load_image(image_id))')
    preload = source.index('err = boot_platform_pre_load(image_id)', selection)
    assert 'continue;' in source[selection:preload]
