"""Compile the Apollo PSCI OFF arming hook; this is not runtime evidence."""

import ctypes
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCP = ROOT / "hsoc-stack/components/system_mgmt/scp-firmware"


@pytest.fixture(scope="module")
def prepare(tmp_path_factory):
    compiler = shutil.which("gcc")
    if compiler is None:
        pytest.skip("host compiler unavailable")
    source = (SCP / "product/automotive-rd/apollo-qvp/si0_ramfw/config_scmi_power_domain.c").read_text()
    function = source[source.index("int scmi_pd_prepare_async_response("):]
    unit = """#include <stdint.h>
typedef unsigned int fwk_id_t;
#define FWK_SUCCESS 0
#define SI0_SCMI_AGENT_IDX_PSCI 2
#define MOD_PD_LEVEL_0 0
#define MOD_PD_STATE_OFF 0
#define MOD_PD_COMPOSITE_STATE(l, s3, s2, s1, s0) \\
    (((l) << 16) | ((s3) << 12) | ((s2) << 8) | ((s1) << 4) | (s0))
static unsigned int calls, last_core;
static int prepare_status;
unsigned int platform_get_core_count(void) { return 4; }
unsigned int fwk_id_get_element_idx(fwk_id_t id) { return id; }
int si0_prepare_core_off(unsigned int core) {
    calls++; last_core = core; return prepare_status;
}
void reset(int status) { calls = 0; last_core = 99; prepare_status = status; }
unsigned int get_calls(void) { return calls; }
unsigned int get_core(void) { return last_core; }
""" + function
    output = tmp_path_factory.mktemp("qvp-core-off") / "prepare.so"
    subprocess.run(
        [compiler, "-shared", "-fPIC", "-Werror", "-x", "c", "-o", str(output), "-"],
        input=unit, text=True, capture_output=True, check=True, timeout=20,
    )
    library = ctypes.CDLL(str(output))
    library.scmi_pd_prepare_async_response.argtypes = [ctypes.c_uint32, ctypes.c_uint, ctypes.c_uint]
    library.scmi_pd_prepare_async_response.restype = ctypes.c_int
    return library


@pytest.mark.parametrize("state,agent,core,armed", [
    (0, 2, 0, True), (0, 2, 3, True),
    (1, 2, 0, False),  # CPU ON
    (2, 2, 0, False),  # CPU suspend
    (0x10000, 2, 0, False),  # Cluster OFF
    (0x20000, 2, 0, False),  # System OFF
    (0, 1, 0, False),  # RSE
    (0, 3, 0, False),  # PFDI
    (0, 4, 0, False),  # OSPM
    (0, 2, 4, False),  # First non-AP-core domain
])
def test_only_secure_psci_ap_core_off_is_armed(prepare, state, agent, core, armed):
    prepare.reset(0)
    assert prepare.scmi_pd_prepare_async_response(state, agent, core) == 0
    assert prepare.get_calls() == int(armed)
    if armed:
        assert prepare.get_core() == core


def test_prepare_failure_reaches_scmi_response(prepare):
    prepare.reset(-7)
    assert prepare.scmi_pd_prepare_async_response(0, 2, 1) == -7
    assert prepare.get_calls() == 1
