import pytest

from test_automation.checks.profiles import execute_profile

pytestmark = [pytest.mark.domain('si_cl1'), pytest.mark.category('safety'), pytest.mark.image("any")]


@pytest.mark.destructive
def test_cluster_pfdi_commands_and_scp_monitoring(platform_base_obj, record_property):
    execute_profile(platform_base_obj, 'pfdi-si-cl1', record_property)
