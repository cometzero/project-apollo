"""Bounded host checks for test-only wake logic; not FVP power qualification."""

import ctypes
from pathlib import Path
import re
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCP = ROOT / "hsoc-stack/components/system_mgmt/scp-firmware"


def function(source, name):
    start = source.index("static ", source.index(name) - 20)
    brace = source.index("{", start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]


@pytest.fixture(scope="module")
def backend(tmp_path_factory):
    gcc = shutil.which("gcc")
    if gcc is None:
        pytest.skip("host compiler unavailable")
    source = (SCP / "module/system_power/src/mod_system_power.c").read_text()
    ppu = (SCP / "product/automotive-rd/apollo-fvp/si0_ramfw/config_ppu_v1.c").read_text()
    alarm = re.search(
        r"suspend_poll_alarm_id = FWK_ID_SUB_ELEMENT\(\s*[^,]+,\s*[^,]+,\s*([^;]+)\);",
        ppu,
    ).group(1)
    # Framework APIs are isolated; the two algorithm bodies are verbatim source.
    unit = r'''
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "si0_cfgd_timer.h"
#define FWK_SUCCESS 0
#define FWK_E_SUPPORT -1
#define FWK_E_STATE -2
#define MOD_PD_STATE_OFF 0
#define MOD_PD_STATE_ON 1
#define MOD_SYSTEM_POWER_POWER_STATE_SLEEP0 6
#define MOD_SYSTEM_POWER_SOC_WAKEUP_STATE 0x2111
#define MOD_TIMER_ALARM_TYPE_ONCE 0
#define FWK_LOG_INFO(...) ((void)0)
#define FWK_LOG_ERR(...) ((void)0)
typedef unsigned fwk_id_t;
static int mode, armed, wakes, changes;
struct ppu_api { int (*get_state)(fwk_id_t, unsigned *); };
struct alarm_api { int (*start)(fwk_id_t, uint32_t, int, void (*)(uintptr_t), uintptr_t); };
struct pd_api { int (*set_state)(fwk_id_t, bool, unsigned); };
struct input_api { int (*get_last_core_pd_id)(fwk_id_t *); };
struct config { fwk_id_t test_wake_alarm_id; uint32_t test_wake_delay_us;
    bool test_keep_systop_on; int (*test_children_off_check)(void);
    int (*test_retention_check)(bool); };
struct dev_config { fwk_id_t sys_ppu_id; };
struct system_power_dev_ctx { struct dev_config *config; struct ppu_api *sys_ppu_api; };
static struct {
    bool test_wake_armed;
    bool test_retention_pending, test_retention_off_verified;
    struct pd_api *pd_restricted_api;
    struct input_api *pd_driver_input_api;
    fwk_id_t last_core_pd_id;
    struct alarm_api *test_wake_alarm;
    struct config *config;
    unsigned dev_count;
    struct system_power_dev_ctx *dev_ctx_table;
} system_power_ctx;
static int set_system_power_state(unsigned s) { changes++; return mode == 3 ? -3 : 0; }
static int get_state(fwk_id_t id, unsigned *state) { *state = mode == 1 || mode == 7 || mode == 8 || mode == 10 ? 1 : 0; return mode == 2 ? -3 : 0; }
static int children_off(void) { return mode == 8 ? -3 : 0; }
static int forbidden_fingerprint(bool off) { return -99; }
static int last_core(fwk_id_t *id) { *id = 42; return 0; }
static int start(fwk_id_t id, uint32_t delay, int type, void (*cb)(uintptr_t), uintptr_t p)
{ armed++; return mode == 4 ? -3 : 0; }
static int wake(fwk_id_t id, bool response, unsigned state)
{ if (id != 42 || state != MOD_SYSTEM_POWER_SOC_WAKEUP_STATE) return -99; wakes++; return 0; }
'''
    unit += function(source, "test_suspend_wake_callback") + "\n"
    unit += function(source, "test_suspend_power_off") + "\n"
    platform_source = (SCP / "product/automotive-rd/apollo-fvp/si0_ramfw/config_system_power.c").read_text()
    unit += r'''
static uint32_t ppu_registers[2][64];
#define SI0_ATW1_CLUSTER_UTILITY_BASE ((uintptr_t)ppu_registers)
#define SI0_CLUSTER_UTILITY_SIZE sizeof(ppu_registers[0])
#define SI0_CLUSTER_UTILITY_CLUSTER_PPU_OFFSET 0
#define SI0_CLUSTER_UTILITY_CORE_PPU0_OFFSET 32
#define SI0_CLUSTER_UTILITY_CORE_PPU_OFFSET 32
static unsigned platform_get_cluster_count(void) { return 2; }
static unsigned platform_get_core_per_cluster_count(unsigned c) { return c + 1; }
'''
    unit += function(platform_source, "ap_children_off_check") + "\n"
    unit += r'''
int check_children(unsigned failure) {
    memset(ppu_registers, 0, sizeof(ppu_registers));
    if (failure == 1) ppu_registers[0][2] = 8;
    if (failure == 2) ppu_registers[1][2] = 8;
    if (failure == 3) ppu_registers[0][10] = 8;
    if (failure == 4) ppu_registers[1][10] = 8;
    if (failure == 5) ppu_registers[1][18] = 8;
    return ap_children_off_check();
}
'''
    unit += r'''
int run(int requested_mode) {
    struct ppu_api pp = {get_state}; struct alarm_api al = {start};
    struct pd_api pd = {wake}; struct input_api in = {last_core};
    struct config cf = {1, 5000000}; struct dev_config dc = {9};
    struct system_power_dev_ctx dev = {&dc, &pp};
    memset(&system_power_ctx, 0, sizeof(system_power_ctx));
    mode = requested_mode; armed = wakes = changes = 0;
    if (mode >= 7) {
        cf.test_keep_systop_on = true;
        cf.test_children_off_check = mode == 10 ? NULL : children_off;
        cf.test_retention_check = forbidden_fingerprint;
    }
    system_power_ctx.pd_restricted_api = &pd;
    system_power_ctx.pd_driver_input_api = &in;
    system_power_ctx.test_wake_alarm = mode == 6 ? NULL : &al;
    system_power_ctx.config = &cf; system_power_ctx.dev_count = 1;
    system_power_ctx.dev_ctx_table = &dev;
    int rc = test_suspend_power_off();
    test_suspend_wake_callback(0);
    test_suspend_wake_callback(0); /* stale delivery must not duplicate wake */
    return (rc == 0 ? 1000 : 0) + changes * 100 + armed * 10 + wakes;
}
'''
    unit += f"unsigned alarm_for_core(unsigned core_element_count) {{return {alarm};}}\n"
    unit += "unsigned wake_alarm(void) {return SI0_CFGD_TEST_AP_SUSPEND_WAKE_ALARM_IDX;}\n"
    out = tmp_path_factory.mktemp("suspend-backend") / "backend.so"
    subprocess.run([gcc, "-shared", "-fPIC", "-Werror", "-x", "c",
        "-DAPOLLO_FVP_TEST_SUSPEND_WAKE_US=5000000",
        f"-I{SCP / 'product/automotive-rd/apollo-fvp/si0_ramfw/include'}",
        "-o", str(out), "-"], input=unit, text=True, capture_output=True,
        check=True, timeout=20)
    return ctypes.CDLL(str(out))


@pytest.mark.parametrize("mode,expected", [
    (0, 1111),  # Verified OFF -> one alarm -> one wake.
    (1, 100),   # PPU still ON: no alarm or wake.
    (2, 100),   # Readback error: no alarm or wake.
    (3, 100),   # OFF request failure: no alarm or wake.
    (4, 110),   # Failed alarm arm: no synthetic wake.
    (6, 0),     # Missing timer backend: no OFF request.
    (7, 1111),  # KEEP mode: actual SYS0 ON, all children OFF; no fingerprint.
    (8, 0),     # Child not OFF: no request, timer, or synthetic wake.
    (9, 100),   # KEEP mode must reject physical SYS0 OFF.
    (10, 0),    # Missing mandatory child verification callback.
])
def test_actual_off_gates_wake(backend, mode, expected):
    assert backend.run(mode) == expected


@pytest.mark.parametrize("failure", range(6))
def test_every_present_child_requires_physical_off(backend, failure):
    assert backend.check_children(failure) == (0 if failure == 0 else -2)


def test_every_ap_core_has_unique_poll_alarm(backend):
    alarms = [backend.alarm_for_core(core) for core in range(16)]
    assert len(set(alarms)) == 16
    assert backend.wake_alarm() not in alarms
