"""Compile the actual SCMI perf PM handler; no FVP retention claim."""

import ctypes
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCP = ROOT / "hsoc-stack/components/system_mgmt/scp-firmware"


@pytest.fixture(scope="module")
def handler(tmp_path_factory):
    gcc = shutil.which("gcc")
    if not gcc:
        pytest.skip("host compiler unavailable")
    source = (SCP / "module/scmi_perf/src/mod_scmi_perf.c").read_text()
    begin = source.index("static int scmi_perf_process_notification(")
    end = source.index("\n#endif", begin)
    unit = r'''
#include <stdbool.h>
#include <stddef.h>
#define FWK_SUCCESS 0
#define FWK_E_PARAM -1
#define MOD_PD_STATE_ON 1
#define FWK_LOG_INFO(...) ((void)0)
typedef unsigned fwk_id_t;
struct fwk_event { fwk_id_t id, source_id; unsigned params[4]; };
struct mod_scmi_perf_config {
    fwk_id_t (*fast_channel_power_domain_id)(void);
    bool fast_channel_memory_retained;
};
struct mod_pd_power_state_pre_transition_notification_params {
    unsigned current_state, target_state;
};
struct mod_pd_power_state_pre_transition_notification_resp_params { int status; };
struct mod_pd_power_state_transition_notification_params { unsigned state; };
static const fwk_id_t mod_pd_notification_id_power_state_pre_transition = 10;
static const fwk_id_t mod_pd_notification_id_power_state_transition = 11;
static struct { const struct mod_scmi_perf_config *config; } scmi_perf_ctx;
static bool paused;
static void perf_fch_set_paused(bool p) { paused = p; }
static bool perf_fch_is_paused(void) { return paused; }
static bool fwk_id_is_equal(fwk_id_t a, fwk_id_t b) { return a == b; }
static fwk_id_t owner(void) { return 5; }
'''
    unit += source[begin:end]
    unit += r'''
int run(unsigned kind, unsigned state, bool initial, bool retained, unsigned src) {
    struct mod_scmi_perf_config config = { owner, retained };
    struct fwk_event event = {kind, src, {0}}, response = {0};
    scmi_perf_ctx.config = &config; paused = initial;
    if (kind == 10) { event.params[0] = 1; event.params[1] = state; }
    else event.params[0] = state;
    response.params[0] = 99;
    int status = scmi_perf_process_notification(&event, &response);
    if (status) return status;
    if (kind == 10 && response.params[0] != 0) return -99;
    return paused;
}
'''
    folder = tmp_path_factory.mktemp("scmi-perf-power")
    src = folder / "handler.c"
    src.write_text(unit)
    library = folder / "handler.so"
    subprocess.run([gcc, "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                    str(src), "-o", str(library)], check=True)
    function = ctypes.CDLL(str(library)).run
    function.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_bool,
                         ctypes.c_bool, ctypes.c_uint]
    function.restype = ctypes.c_int
    return function


@pytest.mark.parametrize("kind,state,initial,retained,src,expected", [
    (10, 0, False, False, 5, 1),  # OFF: quiesce before successful ACK
    (10, 6, False, False, 5, 1),  # SLEEP0: same memory accessibility contract
    (10, 1, True, True, 5, 1),    # ON request alone cannot resume accesses
    (11, 0, True, True, 5, 1),    # actual OFF report remains paused
    (11, 1, True, False, 5, 1),   # SRAM loss: no premature resume
    (11, 1, True, True, 5, 0),    # ON + retained/valid memory permits resume
    (11, 1, False, False, 5, 0),  # cold ON leaves existing polling intact
    (10, 0, False, False, 6, -1), # unrelated domain cannot alter state
    (12, 0, False, False, 5, -1), # unrelated notification rejected
])
def test_notification_contract(handler, kind, state, initial, retained, src, expected):
    assert handler(kind, state, initial, retained, src) == expected
