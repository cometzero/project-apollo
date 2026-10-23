import pytest

from test_automation.checks.profiles import execute_profile

pytestmark = [pytest.mark.domain("si_cl1"), pytest.mark.category("devices"), pytest.mark.image("any")]


def test_zephyr_kernel_version_command(platform_base_obj, record_property):
    execute_profile(platform_base_obj, "si-cl1", record_property)
