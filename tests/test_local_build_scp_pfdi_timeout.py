import argparse
import re
from pathlib import Path
from typing import Final

from scripts.run import run_qbox_apollo_fvp_full as full_runner


ROOT: Final = Path(__file__).resolve().parents[1]
LOCAL_SCP_BUILD: Final = ROOT / "scripts/build/modules/build_scp.sh"
REFERENCE_YOCTO_SCP_BUILD: Final = (
    ROOT
    / "arm-zena-css/yocto/meta-zena-css-bsp/recipes-bsp/scp-firmware"
    / "scp-firmware-fvp-rd-aspen.inc"
)
QBOX_YOCTO_SCP_BUILD: Final = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-bsp/recipes-bsp/scp-firmware"
    / "scp-firmware-apollo-qvp.inc"
)
QBOX_MACHINE_CONFIG: Final = (
    ROOT / "hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-qvp.conf"
)
QBOX_PFDI_POLICY: Final = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/include"
    / "apollo-qvp-qbox-timing.inc"
)
LOCAL_BUILD_CONFIG: Final = ROOT / "scripts/build/local_build.conf"
FVP_PFDI_MONITOR: Final = (
    ROOT
    / "hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd"
    / "apollo-fvp/si0_ramfw/config_pfdi_monitor.c"
)
QVP_PFDI_MONITOR: Final = (
    ROOT
    / "hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd"
    / "apollo-qvp/si0_ramfw/config_pfdi_monitor.c"
)
PFDI_KCONFIG: Final = (
    ROOT
    / "arm-zena-css/components/safety_island/zephyr/src/subsys/pfdi/Kconfig"
)
PFDI_AGENT_CONFIG: Final = (
    ROOT
    / "arm-zena-css/components/safety_island/zephyr/src/drivers/pfdi_agent"
    / "pfdi_agent_scmi_cfg.h"
)
QBOX_FABRIC: Final = (
    ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/fabric.lua"
)


def qbox_pfdi_policy_value(name: str) -> int:
    source = QBOX_PFDI_POLICY.read_text(encoding="utf-8")
    match = re.search(rf'{name}\s*\?=\s*"(\d+)UL"', source)
    assert match is not None, name
    return int(match.group(1))


def source_macro_value(path: Path, name: str) -> int:
    source = path.read_text(encoding="utf-8")
    match = re.search(rf"#\s*define\s+{name}\s+(\d+)UL", source)
    assert match is not None, name
    return int(match.group(1))


def test_qbox_pfdi_timing_policy_is_centralized() -> None:
    # Given: the Apollo QVP machine policy and its local-build mirror.
    machine_source = QBOX_MACHINE_CONFIG.read_text(encoding="utf-8")
    policy_source = QBOX_PFDI_POLICY.read_text(encoding="utf-8")
    local_source = LOCAL_BUILD_CONFIG.read_text(encoding="utf-8")
    expected = {
        "SCP_PFDI_OOR_PERIOD_US": 10_000_000,
        "SCP_PFDI_BOOT_TIMEOUT_US": 180_000_000,
        "SCP_PFDI_ONLINE_TIMEOUT_US": 60_000_000,
        "SCP_SICL1_PFDI_OOR_PERIOD_US": 1_000_000,
        "SCP_SICL1_PFDI_BOOT_TIMEOUT_US": 10_000_000,
        "SCP_SICL1_PFDI_ONLINE_TIMEOUT_US": 500_000,
    }

    # When: every timing value and consumer is resolved.
    for name, value in expected.items():
        policy_assignment = f'{name} ?= "{value}UL"'
        local_assignment = f'{name}="${{{name}-{value}UL}}"'

        # Then: one machine include owns policy and local builds stay aligned.
        assert policy_assignment in policy_source
        assert local_assignment in local_source
        assert f"-D {name}=${{{name}}}" in QBOX_YOCTO_SCP_BUILD.read_text(
            encoding="utf-8"
        )
        assert f'-D{name}="${{{name}}}"' in LOCAL_SCP_BUILD.read_text(
            encoding="utf-8"
        )
    assert (
        "require conf/machine/include/apollo-qvp-qbox-timing.inc"
        in machine_source
    )


def test_qvp_pfdi_source_defaults_match_fvp() -> None:
    # Given: the FVP and Apollo QVP PFDI monitor source defaults.
    macro_pairs = (
        ("OOR_PFDI_PERIOD_US", "OOR_PFDI_PERIOD_US"),
        ("BOOT_TIMEOUT_US", "PFDI_BOOT_TIMEOUT_US"),
        ("SICL1_OOR_PFDI_PERIOD_US", "SICL1_OOR_PFDI_PERIOD_US"),
        ("SICL1_BOOT_TIMEOUT_US", "SICL1_BOOT_TIMEOUT_US"),
    )

    # When/Then: every QVP fallback preserves its FVP-derived value.
    for fvp_name, qvp_name in macro_pairs:
        assert source_macro_value(FVP_PFDI_MONITOR, fvp_name) == source_macro_value(
            QVP_PFDI_MONITOR,
            qvp_name,
        )


def test_qbox_pfdi_watchdogs_have_full_system_margin() -> None:
    # Given: the heartbeat period and the SI0 watchdogs used by full-system builds.
    period_source = PFDI_KCONFIG.read_text(encoding="utf-8")
    agent_source = PFDI_AGENT_CONFIG.read_text(encoding="utf-8")
    fabric_source = QBOX_FABRIC.read_text(encoding="utf-8")
    period_match = re.search(
        r"config PFDI_MGMT_PERIOD_MS\s+.*?default\s+(\d+)",
        period_source,
        flags=re.DOTALL,
    )
    response_match = re.search(
        r"PFDI_AGENT_RESP_TIMEOUT_MS\s+(\d+)U",
        agent_source,
    )
    quantum_match = re.search(
        r"SYSTEMC_QUANTUM_NS\s*=\s*(\d+)",
        fabric_source,
    )
    assert period_match is not None
    assert response_match is not None
    assert quantum_match is not None

    # When: the complete QBox request path is budgeted in microseconds.
    heartbeat_period_us = int(period_match.group(1)) * 1_000
    response_timeout_us = int(response_match.group(1)) * 1_000
    systemc_quantum_us = int(quantum_match.group(1)) // 1_000
    qbox_request_budget_us = (
        heartbeat_period_us + response_timeout_us + systemc_quantum_us
    )

    # Then: five complete request windows fit before a QBox watchdog deadline.
    for timeout_name in (
        "SCP_PFDI_ONLINE_TIMEOUT_US",
        "SCP_SICL1_PFDI_ONLINE_TIMEOUT_US",
    ):
        watchdog_timeout_us = qbox_pfdi_policy_value(timeout_name)
        assert watchdog_timeout_us >= 5 * qbox_request_budget_us

    reference_source = REFERENCE_YOCTO_SCP_BUILD.read_text(encoding="utf-8")
    reference_match = re.search(
        r"SCP_SICL1_PFDI_ONLINE_TIMEOUT_US=(\d+)UL",
        reference_source,
    )
    assert reference_match is not None
    assert int(reference_match.group(1)) == heartbeat_period_us


def test_full_system_gate_detects_si0_pfdi_watchdog_timeout(
    tmp_path: Path,
) -> None:
    # Given: SI0 reports a PFDI watchdog expiry while SI1 remains healthy.
    (tmp_path / full_runner.CONSOLE_LOGS["si_cl0"]).write_text(
        "[PFDI_MONITOR] Error! PFDI monitor timeout for AP cluster 0 core 0\n",
        encoding="utf-8",
    )
    (tmp_path / full_runner.CONSOLE_LOGS["si_cl1"]).write_text(
        "PFDI service ready\n",
        encoding="utf-8",
    )
    args = argparse.Namespace(out_dir=tmp_path)

    # When: the canonical full-system runner classifies Safety Island errors.
    error_hits = full_runner.si_error_hits(args)

    # Then: the SI0 watchdog expiry blocks a false-positive boot pass.
    assert error_hits["pfdi_monitor_timeout"]


def test_qbox_ap_secondary_cores_have_time_to_report_out_of_reset() -> None:
    # Given: the local and Yocto Apollo QVP SCP build configurations.
    policy = qbox_pfdi_policy_value("SCP_PFDI_OOR_PERIOD_US")

    # When/Then: secondary cores retain the established ten-second deadline.
    assert policy >= 10_000_000


def test_qbox_ap_pfdi_watchdogs_cover_product_crypto() -> None:
    # Given: the QVP-only AP PFDI watchdog configuration.
    boot_policy = qbox_pfdi_policy_value("SCP_PFDI_BOOT_TIMEOUT_US")
    online_policy = qbox_pfdi_policy_value("SCP_PFDI_ONLINE_TIMEOUT_US")

    # When/Then: product login and long secure calls fit without masking a
    # permanently missing heartbeat.
    assert boot_policy >= 180_000_000
    assert online_policy >= 60_000_000
