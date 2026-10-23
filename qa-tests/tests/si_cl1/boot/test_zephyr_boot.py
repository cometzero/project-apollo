import pytest

from test_automation.checks.profiles import require_log_markers
from scripts.run.qbox_validation.reuse_bsp import si1_boot_complete

pytestmark = [pytest.mark.domain("si_cl1"), pytest.mark.category("boot"), pytest.mark.image("any")]


def test_zephyr_boot_and_secondary_cpus(platform_base_obj):
    text = require_log_markers(platform_base_obj, "si_cl1", ("Booting Zephyr OS build", "uart:~$"))
    assert si1_boot_complete(text), "si_cl1: secondary CPU boot records missing or invalid"
