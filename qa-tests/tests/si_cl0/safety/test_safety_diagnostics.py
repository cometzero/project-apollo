import pytest

from test_automation.checks.profiles import execute_profile

pytestmark = [pytest.mark.domain('si_cl0'), pytest.mark.category('safety'), pytest.mark.image("any")]


@pytest.mark.destructive
def test_fmu_and_ssu_integration_diagnostics(platform_base_obj, record_property):
    execute_profile(platform_base_obj, 'safety-diagnostics-tests', record_property)
