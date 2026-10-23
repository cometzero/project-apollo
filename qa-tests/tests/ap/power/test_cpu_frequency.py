import pytest

from test_automation.checks.profiles import execute_profile

pytestmark = [pytest.mark.domain('ap'), pytest.mark.category('power'),
              pytest.mark.image("any"), pytest.mark.destructive]


def test_cpu_frequency_policy_governors_and_limits(platform_base_obj, record_property):
    execute_profile(platform_base_obj, 'cpufreq', record_property)
