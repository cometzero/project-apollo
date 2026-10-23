import pytest

from test_automation.checks.profiles import require_log_markers

pytestmark = [pytest.mark.domain("ap"), pytest.mark.category("boot"), pytest.mark.image("any")]


def test_uboot_boot_and_efi_handoff(platform_base_obj):
    require_log_markers(platform_base_obj, "ap", (
        "U-Boot ", "Hit any key to stop autoboot:", "efi: EFI v", "by Das U-Boot",
    ))
