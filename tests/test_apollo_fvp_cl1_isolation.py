"""Host-execute the actual CL1 boot/PFDI start functions with framework stubs."""
import ctypes
from pathlib import Path
import shutil
import subprocess

import pytest

BASE = Path(__file__).resolve().parents[1] / 'hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp'


def function(source, name):
    start = source.index('static int ' + name + '(')
    brace = source.index('{', start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


@pytest.fixture(scope='module')
def native(tmp_path_factory):
    cc = shutil.which('gcc')
    if not cc:
        pytest.skip('host gcc unavailable')
    common = '''
#include <stdint.h>
#include <stdbool.h>
typedef unsigned fwk_id_t;
#define FWK_SUCCESS 0
#define FWK_E_PARAM -1
#define FWK_E_STATE -2
#define MOD_PD_STATE_OFF 0
#define MOD_PD_CS_STATE_MASK 15U
#define FWK_ID_TYPE_ELEMENT 1
#define FWK_ID_TYPE_MODULE 0
#define MOD_NAME "test"
#define FWK_LOG_INFO(...) ((void)0)
#define FWK_LOG_ERR(...) ((void)0)
#define FWK_LOG_DEBUG(...) ((void)0)
#define FWK_MODULE_IDX_POWER_DOMAIN 0
#define FWK_ID_ELEMENT(m,i) (i)
#define MOD_PD_COMPOSITE_STATE(...) 1
#define MOD_TIMER_ALARM_TYPE_ONCE 0
static bool fwk_id_is_type(fwk_id_t id,unsigned t){return t==1;}
static unsigned fwk_id_get_element_idx(fwk_id_t id){return 0;}
static unsigned platform_get_core_count(void){return 16;}
static unsigned platform_get_cluster_count(void){return 4;}
static unsigned calls;
'''
    boot = common + '''
struct cfg { struct {unsigned id,num_cores,core_offset;} cluster_layout; bool skip_boot; };
struct api {int (*set_state)(fwk_id_t,bool,uint32_t);int (*get_state)(fwk_id_t,unsigned*);int (*get_domain_parent_id)(fwk_id_t,fwk_id_t*);};
struct safety_island_cluster_ctx {const struct cfg *config;const struct api *pd_restricted_api;};
static struct {struct safety_island_cluster_ctx *safety_island_ctx_table;} ctx;
static unsigned last_id,last_state,reported_state;
static int set_state(fwk_id_t i,bool b,uint32_t s){calls++;last_id=i;last_state=s;return 0;}
static int get_state(fwk_id_t i,unsigned*s){*s=reported_state;return 0;}
static int get_parent(fwk_id_t i,fwk_id_t*p){*p=25;return 0;}
''' + function((BASE/'module/safety_island_platform/src/mod_safety_island_platform.c').read_text(), 'init_si_cluster_cores') + '''
unsigned test_boot(bool skip){struct cfg c={{0,4,1},skip};struct api a={set_state,get_state,get_parent};
struct safety_island_cluster_ctx x={&c,&a};ctx.safety_island_ctx_table=&x;calls=0;
return init_si_cluster_cores(1)==0?calls:999;}
unsigned request_id(void){return last_id;} unsigned request_state(void){return last_state;}
void core_state(unsigned s){reported_state=s;}
'''
    pfdi = common + '''
struct mod_pfdi_monitor_core_config {unsigned alarm_id,pd_source_id,oor_pfdi_period_us;bool start_suspended;};
struct alarm {int (*start)(unsigned,unsigned,unsigned,void*,uintptr_t);};
struct pfdi_monitor_core_context {const struct mod_pfdi_monitor_core_config *core_cfg;const struct alarm *alarm_api;};
static struct {unsigned core_count;struct pfdi_monitor_core_context *core_ctx_table;} ctx;
static unsigned pd_transition_notification_id, subscriptions;
static void *pfdi_monitor_timeout;
static int fwk_notification_subscribe(unsigned a,unsigned b,unsigned c){subscriptions++;return 0;}
static int start_alarm(unsigned a,unsigned b,unsigned c,void*d,uintptr_t e){calls++;return 0;}
''' + function((BASE/'module/pfdi_monitor/src/mod_pfdi_monitor.c').read_text(), 'pfdi_monitor_start') + '''
unsigned test_pfdi(bool skip){struct mod_pfdi_monitor_core_config c={0,0,1,skip};
struct alarm a={start_alarm};struct pfdi_monitor_core_context x={&c,&a};
ctx.core_count=1;ctx.core_ctx_table=&x;calls=0;subscriptions=0;
return pfdi_monitor_start(1)==0?subscriptions*10+calls:999;}
'''
    libs = []
    for name, text in [('boot', boot), ('pfdi', pfdi)]:
        output = tmp_path_factory.mktemp('cl1-isolation') / (name+'.so')
        subprocess.run([cc,'-shared','-fPIC','-Werror','-x','c','-o',str(output),'-'],
                       input=text,text=True,capture_output=True,check=True,timeout=20)
        libs.append(ctypes.CDLL(str(output)))
    return libs


def test_boot_default_starts_all_cores(native):
    assert native[0].test_boot(False) == 4


def test_boot_isolation_requests_only_parent_off(native):
    assert native[0].test_boot(True) == 1
    assert native[0].request_id() == 25
    assert native[0].request_state() == 0


def test_boot_isolation_rejects_active_core(native):
    native[0].core_state(1)
    assert native[0].test_boot(True) == 999
    native[0].core_state(0)


def test_boot_isolation_allows_off_core_with_on_parent(native):
    native[0].core_state(0x10010)
    assert native[0].test_boot(True) == 1
    assert native[0].request_state() == 0
    native[0].core_state(0)


def test_pfdi_default_subscribes_and_starts_alarm(native):
    assert native[1].test_pfdi(False) == 11


def test_pfdi_isolated_still_subscribes_without_alarm(native):
    assert native[1].test_pfdi(True) == 10
