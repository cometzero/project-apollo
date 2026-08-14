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
QBOX_PFDI_MONITOR: Final = (
    ROOT
    / "hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd"
    / "apollo-qvp/si0_ramfw/config_pfdi_monitor.c"
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
    for build_path in (LOCAL_SCP_BUILD, QBOX_YOCTO_SCP_BUILD):
        build_source = build_path.read_text(encoding="utf-8")
        for timeout_name in (
            "SCP_PFDI_ONLINE_TIMEOUT_US",
            "SCP_SICL1_PFDI_ONLINE_TIMEOUT_US",
        ):
            timeout_match = re.search(
                rf"{timeout_name}=(\d+)UL",
                build_source,
            )
            assert timeout_match is not None
            watchdog_timeout_us = int(timeout_match.group(1))
            assert watchdog_timeout_us >= 5 * qbox_request_budget_us, build_path

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
    # Given: the QVP-specific AP out-of-reset watchdog.
    monitor_source = QBOX_PFDI_MONITOR.read_text(encoding="utf-8")
    timeout_match = re.search(
        r"#define OOR_PFDI_PERIOD_US\s+(\d+)UL",
        monitor_source,
    )
    assert timeout_match is not None

    # When: the timeout is compared with the full-system boot budget.
    oor_timeout_us = int(timeout_match.group(1))

    # Then: secondary cores are not diagnosed before the QVP boot deadline.
    assert oor_timeout_us >= 10_000_000
