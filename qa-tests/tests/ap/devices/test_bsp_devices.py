import pytest

from test_automation.checks.bsp import DEVICES_COMMAND
from test_automation.checks.profiles import run_ap_command

pytestmark = [pytest.mark.image("any"), pytest.mark.domain("ap"), pytest.mark.category("devices")]


def test_rtc_watchdog_and_rng_interfaces(platform_base_obj):
    output = run_ap_command(platform_base_obj, DEVICES_COMMAND)
    assert "__QBOX_BSP_CORE_DEVICES_OK__" in output
