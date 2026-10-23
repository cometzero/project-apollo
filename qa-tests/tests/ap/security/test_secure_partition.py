import pytest

from test_automation.checks.profiles import require_log_markers

pytestmark = [pytest.mark.image("any"), pytest.mark.domain("ap"), pytest.mark.category("security")]


def test_optee_and_secure_partitions(platform_base_obj):
    require_log_markers(platform_base_obj, "secure", (
        "Loading SP: SE Proxy", "Loading SP: SMM Gateway", "OP-TEE version:",
        "I/TC: Primary CPU switching to normal world boot",
    ))
