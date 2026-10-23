import pytest

from test_automation.checks.profiles import require_log_markers

pytestmark = [pytest.mark.domain("rse"), pytest.mark.category("boot"), pytest.mark.image("any")]


def test_rse_normal_boot_and_ap_power_on(platform_base_obj):
    require_log_markers(platform_base_obj, "rse", (
        "Starting TF-M BL1_1", "Starting TF-M BL1_2", "Init SCMI comm to SCP succeeded",
        "RSE to SCP SCMI power on AP succeeded", "Jumping to the first image slot",
        "Booting TF-M",
    ))


def test_rse_measured_boot(platform_base_obj):
    require_log_markers(platform_base_obj, "rse", (
        "MeasuredBoot: Extending measurement for sw_type: BL2",
        "MeasuredBoot: Extending measurement for sw_type: BL_33",
    ))
