import pytest

from test_automation.checks.profiles import execute_profile

pytestmark = [pytest.mark.domain('ap'), pytest.mark.category('safety'), pytest.mark.image("product-only")]


@pytest.mark.destructive
def test_cpu_ras_injection_and_rasdaemon(platform_base_obj, record_property):
    execute_profile(platform_base_obj, 'ras_cpu', record_property)
