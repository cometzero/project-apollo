from __future__ import annotations

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
FVP_SCP_CONFIG = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/scp-firmware"
    / "scp-firmware-apollo-fvp.inc"
)
FVP_PFDI_CONFIG = (
    ROOT
    / "hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd"
    / "apollo-fvp/si0_ramfw/config_pfdi_monitor.c"
)


def _effective_online_timeout(machine: str) -> int:
    command = (
        "set +u; source layers/poky/oe-init-build-env build >/dev/null; "
        "set -u; "
        f"MACHINE={machine} bitbake -e scp-firmware"
    )
    result = subprocess.run(
        ["bash", "-lc", command],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=300,
    )
    match = re.search(r'^EXTRA_OECMAKE="(.*)"$', result.stdout, re.MULTILINE)
    assert match is not None
    values = re.findall(
        r"-D SCP_SICL1_PFDI_ONLINE_TIMEOUT_US=(\d+)UL",
        match.group(1),
    )
    assert values
    return int(values[-1])


def test_fvp_and_qvp_resolve_the_si_pfdi_online_timeout() -> None:
    # Given: the active FVP and QVP SCP recipe environments.
    # When: each effective CMake command is resolved by BitBake.
    fvp_timeout = _effective_online_timeout("apollo-fvp")
    qvp_timeout = _effective_online_timeout("apollo-qvp")

    # Then: both use the bounded 500ms SI CL1 PFDI online watchdog.
    assert fvp_timeout == 500_000
    assert qvp_timeout == 500_000


def test_fvp_source_keeps_the_ten_second_si_pfdi_boot_timeout() -> None:
    # Given: the project-owned FVP monitor configuration source.
    source = FVP_PFDI_CONFIG.read_text(encoding="utf-8")

    # When/Then: the online policy does not change the established boot budget.
    assert re.search(r"SICL1_BOOT_TIMEOUT_US\s+10000000UL", source)


def test_fvp_recipe_owns_the_online_timeout_override() -> None:
    # Given: the project-owned FVP SCP recipe include.
    source = FVP_SCP_CONFIG.read_text(encoding="utf-8")

    # When/Then: FVP explicitly replaces the external 60ms watchdog setting.
    assert 'SCP_SICL1_PFDI_ONLINE_TIMEOUT_US = "500000UL"' in source
