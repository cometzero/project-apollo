import pytest

from scripts.run.qbox_validation.reuse_bsp import BSP_HOTPLUG_PROBE
from test_automation.checks.bsp import TOPOLOGY_COMMAND
from test_automation.checks.profiles import run_ap_command

pytestmark = [pytest.mark.image("any"), pytest.mark.domain("ap"), pytest.mark.category("devices")]


def test_four_cpu_topology_and_shared_cache(platform_base_obj):
    output = run_ap_command(platform_base_obj, TOPOLOGY_COMMAND)
    assert "__QBOX_BSP_CORE_TOPOLOGY_OK__" in output


@pytest.mark.destructive
def test_secondary_cpu_hotplug_and_restore(platform_base_obj):
    # A failed hotplug must not leave the session used by later tests offline.
    output = run_ap_command(platform_base_obj, f"( set -e; {BSP_HOTPLUG_PROBE} )", timeout=500)
    assert "__QBOX_BSP_CORE_HOTPLUG_RESTORED__" in output
