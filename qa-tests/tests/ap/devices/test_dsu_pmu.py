import pytest

from test_automation.checks.bsp import DSU_COMMAND
from test_automation.checks.profiles import run_ap_command

pytestmark = [pytest.mark.image("any"), pytest.mark.domain("ap"), pytest.mark.category("devices")]


def test_dsu_pmu_events_under_memory_traffic(platform_base_obj):
    output = run_ap_command(platform_base_obj, DSU_COMMAND, timeout=500)
    assert "__QBOX_BSP_CORE_DSU_OK__" in output
