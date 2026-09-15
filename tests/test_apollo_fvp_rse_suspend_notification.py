"""Compile the actual RSE notification handler with host side-effect stubs.

This tests notification semantics, not firmware integration or power-off.
"""
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SCMI = ROOT / (
    "hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target/"
    "arm/rse/automotive_rd/apollo-fvp/scmi"
)


def test_suspend_notification_keeps_aon_state(tmp_path):
    source = (SCMI / "scmi_hal.c").read_text()
    # The final function is isolated to avoid mocking the unrelated MHU driver.
    handler = source.split("int32_t scmi_hal_sys_power_state(", 1)[1]
    handler = "int32_t scmi_hal_sys_power_state(" + handler.rsplit("#endif", 1)[0]
    harness = r'''
#include <assert.h>
#include <stdint.h>
typedef int scmi_comms_err_t;
#include "scmi_protocol.h"
#include "scmi_system_power.h"
#define SCMI_LOG_INF(...) ((void)0)
#define SCMI_LOG_NOT(...) ((void)0)
#define SCMI_LOG_ERR(...) ((void)0)
#define SCMI_COMMS_SUCCESS 0
#define TFM_PLAT_SWSYN_DEFAULT 0
static unsigned waits, resets, loads, inits, ready;
static void __WFI(void) { ++waits; assert(0); }
static void tfm_hal_system_reset(int type) { (void)type; ++resets; }
static void rse_load_ap_bl2_image(void) { ++loads; }
static int scmi_hal_shared_memory_init(void) { ++inits; return 0; }
static int scmi_hal_notify_warm_reset_ready(void) { ++ready; return 0; }
'''
    checks = r'''
int main(void) {
    for (uint32_t flags = 0; flags <= 1; ++flags) {
        assert(scmi_hal_sys_power_state(0, flags, SCMI_SYS_POWER_STATE_SUSPEND)
               == SCMI_STATUS_SUCCESS);
        assert(waits == 0 && resets == 0 && loads == 0 && inits == 0 && ready == 0);
    }
    assert(scmi_hal_sys_power_state(0, 2, SCMI_SYS_POWER_STATE_SUSPEND)
           == SCMI_STATUS_INVALID_PARAMETERS);
    assert(scmi_hal_sys_power_state(0, 0, SCMI_SYS_POWER_STATE_POWER_UP)
           == SCMI_STATUS_NOT_SUPPORTED);
    assert(scmi_hal_sys_power_state(0, 0, UINT32_MAX)
           == SCMI_STATUS_NOT_SUPPORTED);
    assert(scmi_hal_sys_power_state(0, 0, SCMI_SYS_POWER_STATE_WARM_RESET) == 0);
    assert(loads == 1 && inits == 1 && ready == 1 && resets == 0);
    assert(scmi_hal_sys_power_state(0, 0, SCMI_SYS_POWER_STATE_COLD_RESET) == 0);
    assert(resets == 1 && waits == 0);
    return 0;
}
'''
    unit = tmp_path / "notification.c"
    unit.write_text(harness + handler + checks)
    executable = tmp_path / "notification"
    subprocess.run([
        "cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
        "-Wno-unused-parameter", "-I", str(SCMI), str(unit), "-o", str(executable),
    ], check=True)
    subprocess.run([str(executable)], check=True, timeout=5)
