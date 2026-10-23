import pytest

from test_automation.checks.profiles import require_log_markers

pytestmark = [pytest.mark.domain("ap"), pytest.mark.category("boot"), pytest.mark.image("any")]


def test_optee_primary_and_secondary_cpu_boot(platform_base_obj):
    require_log_markers(platform_base_obj, "secure", (
        "I/TC: OP-TEE version:",
        "I/TC: Primary CPU switching to normal world boot",
        *(f"I/TC: Secondary CPU {cpu} switching to normal world boot" for cpu in range(1, 4)),
    ))
