"""Execute real retention C and ON-report gate on the host, not a mock hash."""
import ctypes
from pathlib import Path
import shutil
import subprocess

import pytest

SCP = Path(__file__).resolve().parents[1] / 'hsoc-stack/components/system_mgmt/scp-firmware'
CONFIG = SCP / 'product/automotive-rd/apollo-fvp/si0_ramfw/config_system_power.c'
MODULE = SCP / 'module/system_power/src/mod_system_power.c'


def extract_function(source, name):
    start = source.index('static int '+name+'(')
    brace = source.index('{', start)
    depth, end = 1, brace+1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


PREFIX = '''
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <inttypes.h>
#define FWK_SUCCESS 0
#define FWK_E_STATE -2
#define FWK_E_DATA -3
#define FWK_LOG_INFO(...) ((void)0)
#define FWK_LOG_ERR(...) ((void)0)
#define FWK_ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
'''


def compile_c(text, tmp_path):
    cc = shutil.which('gcc')
    if not cc:
        pytest.skip('gcc unavailable')
    output = tmp_path/'native.so'
    subprocess.run([cc,'-shared','-fPIC','-Werror','-x','c','-o',str(output),'-'],
                   input=text,text=True,capture_output=True,check=True,timeout=20)
    return ctypes.CDLL(str(output))


@pytest.fixture
def retention(tmp_path):
    source = CONFIG.read_text()
    actual = source[source.index('static uint64_t ap_sram_fingerprint('):]
    actual = actual[:actual.index('#endif')]
    unit = PREFIX + '''
static uint8_t secure[1048576], nonsecure[1048576];
#define SI0_ATW6_AP_PERIPHERAL_SRAM_BASE ((uintptr_t)secure)
#define SI0_ATW7_AP_PERIPHERAL_NS_SRAM_BASE ((uintptr_t)nonsecure)
#define SI0_ATW6_AP_PERIPHERAL_SRAM_SIZE sizeof(secure)
#define SI0_ATW7_AP_PERIPHERAL_NS_SRAM_SIZE sizeof(nonsecure)
''' + actual + '''
int check(bool before){return ap_sram_retention_check(before);}
void mutate(unsigned region,unsigned offset){(region?nonsecure:secure)[offset]^=0x5a;}
uint64_t fingerprint(const uint8_t*p,size_t n){return ap_sram_fingerprint((uintptr_t)p,n);}
'''
    lib = compile_c(unit, tmp_path)
    lib.fingerprint.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
    lib.fingerprint.restype = ctypes.c_uint64
    return lib


def test_standard_fnv1a_vectors(retention):
    assert retention.fingerprint(b'', 0) == 0xcbf29ce484222325
    assert retention.fingerprint(b'a', 1) == 0xaf63dc4c8601ec8c
    assert retention.fingerprint(b'foobar', 6) == 0x85944171f73967e8


def test_requires_baseline_and_consumes_it(retention):
    assert retention.check(False) == -2
    assert retention.check(True) == 0
    assert retention.check(False) == 0
    assert retention.check(False) == -2


@pytest.mark.parametrize('region,offset', [(0,0),(0,1048575),(1,0),(1,1048575)])
def test_covers_first_and_last_byte_of_both_full_regions(retention, region, offset):
    assert retention.check(True) == 0
    retention.mutate(region, offset)
    assert retention.check(False) == -3
    assert retention.check(False) == -2
    # A new cycle records the changed bytes; no SRAM restoration occurred.
    assert retention.check(True) == 0
    assert retention.check(False) == 0


@pytest.fixture
def report_gate(tmp_path):
    actual = extract_function(MODULE.read_text(), 'system_power_report_power_state_transition')
    unit = PREFIX + '''
typedef unsigned fwk_id_t;
#define MOD_PD_STATE_ON 1
static unsigned actual_state=1, trace;
static int callback_result;
static int get_state(fwk_id_t id,unsigned*s){*s=actual_state;return 0;}
static int callback(bool before){trace=trace*10+1;return callback_result;}
static int report(fwk_id_t id,unsigned state){trace=trace*10+2;return 0;}
struct cfg{int(*test_retention_check)(bool);};
struct devcfg{fwk_id_t sys_ppu_id;};
struct api{int(*get_state)(fwk_id_t,unsigned*);};
struct input{int(*report_power_state_transition)(fwk_id_t,unsigned);};
struct system_power_dev_ctx{struct devcfg*config;struct api*sys_ppu_api;};
static struct cfg cfg={callback};static struct devcfg dc;static struct api api={get_state};
static struct system_power_dev_ctx device={&dc,&api};static struct input input={report};
static struct {unsigned dev_count,requested_state,state;bool test_retention_pending,test_retention_off_verified;
struct cfg*config;struct system_power_dev_ctx*dev_ctx_table;struct input*pd_driver_input_api;fwk_id_t mod_pd_system_id;} system_power_ctx;
''' + actual + '''
int run(bool pending,bool off_verified,unsigned actual,int failure){
system_power_ctx.dev_count=1;system_power_ctx.requested_state=1;system_power_ctx.state=0;
system_power_ctx.test_retention_pending=pending;system_power_ctx.test_retention_off_verified=off_verified;
system_power_ctx.config=&cfg;system_power_ctx.dev_ctx_table=&device;system_power_ctx.pd_driver_input_api=&input;
actual_state=actual;callback_result=failure;trace=0;return system_power_report_power_state_transition(0,1);}
unsigned get_trace(void){return trace;}
'''
    return compile_c(unit, tmp_path)


def test_retention_check_precedes_on_report(report_gate):
    assert report_gate.run(True, True, 1, 0) == 0
    assert report_gate.get_trace() == 12


@pytest.mark.parametrize('off_verified,actual,failure,expected_trace',
                         [(False,1,0,0),(True,0,0,0),(True,1,-3,1)])
def test_invalid_or_mismatched_retention_never_reports_on(report_gate, off_verified, actual, failure, expected_trace):
    assert report_gate.run(True, off_verified, actual, failure) != 0
    assert report_gate.get_trace() == expected_trace


def test_default_no_retention_hook_path_unchanged(report_gate):
    assert report_gate.run(False, False, 1, 0) == 0
    assert report_gate.get_trace() == 2


def test_capture_is_before_power_off_and_after_last_core_lookup():
    source = extract_function(MODULE.read_text(), 'test_suspend_power_off')
    assert source.index('get_last_core_pd_id') < source.index('test_retention_check(true)')
    assert source.index('sys_ppu_api->get_state(') < source.index('actual_state != MOD_PD_STATE_ON')
    assert source.index('actual_state != MOD_PD_STATE_ON') < source.index('test_retention_check(true)')
    assert source.index('test_retention_check(true)') < source.index('set_system_power_state(')
    assert source.index('MOD_PD_STATE_ON : MOD_PD_STATE_OFF') < source.index('test_retention_off_verified = true')
    assert '#if APOLLO_FVP_TEST_SUSPEND_WAKE_US > 0 && APOLLO_FVP_AP_SRAM_RETAINED' in CONFIG.read_text()
