"""Host-compile the actual Apollo policy, isolating framework logging/config."""

import ctypes
from pathlib import Path
import re
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCP = ROOT / "hsoc-stack/components/system_mgmt/scp-firmware"


@pytest.fixture(scope="module")
def policy(tmp_path_factory):
    compiler = shutil.which("gcc")
    if compiler is None:
        pytest.skip("host compiler unavailable")
    header = (SCP / "module/scmi_system_power/include/mod_scmi_system_power.h").read_text()
    policy_enum = re.search(
        r"enum mod_scmi_sys_power_policy_status\s*\{.*?\};", header, re.S
    ).group()
    source = (SCP / "product/automotive-rd/apollo-fvp/si0_ramfw/config_scmi_system_power.c").read_text()
    function = source[source.index("int scmi_sys_power_state_set_policy("):]
    unit = (
        '#include <stdint.h>\n#include <stdbool.h>\n'
        '#include <internal/scmi_system_power.h>\n'
        'typedef unsigned int fwk_id_t;\n#define FWK_SUCCESS 0\n'
        + policy_enum + '\n' + function
    )
    output = tmp_path_factory.mktemp("apollo-policy") / "policy.so"
    subprocess.run(
        [compiler, "-shared", "-fPIC", "-Werror", "-x", "c",
         f"-I{SCP / 'module/scmi_system_power/include'}", "-o", str(output), "-"],
        input=unit, text=True, capture_output=True, check=True, timeout=20,
    )
    library = ctypes.CDLL(str(output))
    function = library.scmi_sys_power_state_set_policy
    function.argtypes = [ctypes.POINTER(ctypes.c_int),
                         ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint,
                         ctypes.c_bool]
    function.restype = ctypes.c_int
    return function


@pytest.mark.parametrize("state,graceful,execute", [
    (4, True, True),   # PSCI suspend must reach the power-domain handler.
    (4, False, True),
    (2, True, True),   # Existing warm-reset path is unchanged.
    (0, True, False),  # Existing graceful shutdown is unchanged.
    (1, True, False),
    (0, False, True),
    (1, False, True),
])
def test_apollo_system_power_policy(policy, state, graceful, execute):
    result = ctypes.c_int(-1)
    requested = ctypes.c_uint32(state)
    assert policy(ctypes.byref(result), ctypes.byref(requested), 0, graceful) == 0
    # The real header defines SKIP=0 and EXECUTE=1.
    assert result.value == int(execute)
    assert requested.value == state
