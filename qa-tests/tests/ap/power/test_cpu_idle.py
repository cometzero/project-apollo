import pytest

from test_automation.checks.profiles import execute_profile

pytestmark = [pytest.mark.domain('ap'), pytest.mark.category('power'),
              pytest.mark.image("any"), pytest.mark.destructive]


def test_cpu_idle_states_governors_and_residency(platform_base_obj, record_property):
    execute_profile(platform_base_obj, 'cpuidle', record_property)
