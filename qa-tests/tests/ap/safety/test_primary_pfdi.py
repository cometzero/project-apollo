import pytest

from test_automation.checks.profiles import execute_profile

pytestmark = [pytest.mark.domain('ap'), pytest.mark.category('safety'), pytest.mark.image("any")]


@pytest.mark.destructive
def test_primary_pfdi_diagnostics_and_fault_propagation(platform_base_obj, record_property):
    execute_profile(platform_base_obj, 'pfdi', record_property)
