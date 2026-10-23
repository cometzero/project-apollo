import pytest

from test_automation.checks.profiles import require_log_markers

pytestmark = [pytest.mark.domain("si_cl0"), pytest.mark.category("boot"), pytest.mark.image("any")]


def test_scp_boot_and_cmn_discovery(platform_base_obj):
    require_log_markers(platform_base_obj, "si_cl0", (
        "[SI0_PLATFORM] SCP started", "[FWK] Module initialization complete!",
        "CMN Discovery complete",
    ))
