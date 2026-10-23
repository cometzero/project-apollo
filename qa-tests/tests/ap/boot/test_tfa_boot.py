import pytest

from test_automation.checks.profiles import require_log_markers

pytestmark = [pytest.mark.domain("ap"), pytest.mark.category("boot"), pytest.mark.image("any")]


def test_tfa_boot_and_normal_world_handoff(platform_base_obj):
    require_log_markers(platform_base_obj, "secure", (
        "BL2: Booting BL31",
        "BL31: Initializing runtime services",
        "BL31: Preparing for EL3 exit to normal world",
    ))
