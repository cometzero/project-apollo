import pytest

from test_automation.checks.profiles import execute_profile

pytestmark = [pytest.mark.domain('ap'), pytest.mark.category('devices'), pytest.mark.image("product-only")]


@pytest.mark.destructive
def test_platform_devices_and_network_transport(platform_base_obj, record_property):
    execute_profile(platform_base_obj, 'platform-devices', record_property)
