import pytest

from test_automation.checks.profiles import require_log_markers

pytestmark = [pytest.mark.domain("ap"), pytest.mark.category("boot"), pytest.mark.image("any")]


def test_linux_boot_and_userspace_handoff(platform_base_obj):
    require_log_markers(platform_base_obj, "ap", (
        "Booting Linux on physical CPU", "Linux version ", " as init process",
    ))
