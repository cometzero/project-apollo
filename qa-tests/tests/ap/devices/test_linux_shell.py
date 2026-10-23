import pytest

from test_automation.checks.profiles import run_ap_command

pytestmark = [pytest.mark.domain("ap"), pytest.mark.category("devices"), pytest.mark.image("any")]


def test_linux_uart_executes_guest_command(platform_base_obj):
    output = run_ap_command(platform_base_obj, "echo __QBOX_BSP_CORE_PROBE_START__; uname -s")
    assert "__QBOX_BSP_CORE_PROBE_START__" in output
    assert "Linux" in output.splitlines()
