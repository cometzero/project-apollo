#!/usr/bin/env python3
"""Validate Apollo full-system QBox map, IRQ, and ATU planning evidence."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
from typing import Any


CHECKS = {
    "memory": [
        ("map:ap", "doc/qbox-apollo-fvp-map-analysis.md", r"\| AP \|"),
        ("map:rse", "doc/qbox-apollo-fvp-map-analysis.md", r"\| RSE \|"),
        ("map:smd", "doc/qbox-apollo-fvp-map-analysis.md", r"\| SMD(?:/system-wide view| system-wide map)? \|"),
        ("map:si-cl0", "doc/qbox-apollo-fvp-map-analysis.md", r"\| Safety Island CL0 \|"),
        ("map:si-cl1", "doc/qbox-apollo-fvp-map-analysis.md", r"\| Safety Island CL1 \|"),
        ("platform:apollo-qvp-lua", "QBOX_PLATFORM_DIR/platforms/apollo/apollo-qvp.lua", r"hw-block/rse\.lua"),
        ("platform:apollo-qvp-config", "QBOX_PLATFORM_DIR/platforms/apollo/apollo-qvp.lua", r"hw-block/config\.lua"),
        ("platform:apollo-qvp-fabric", "QBOX_PLATFORM_DIR/platforms/apollo/apollo-qvp.lua", r"hw-block/fabric\.lua"),
        ("platform:config-block", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/config.lua", r"Apollo QVP shared config running"),
        ("platform:fabric-block", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/fabric.lua", r"function fabric\.create"),
        ("platform:smd-router", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/fabric.lua", r"smd_router\s*=\s*\{"),
        ("platform:system-to-smd-nci", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/fabric.lua", r"system_to_smd_nci\s*=\s*\{"),
        ("platform:apollo-qvp-system-mgmt", "QBOX_PLATFORM_DIR/platforms/apollo/apollo-qvp.lua", r"hw-block/system_mgmt\.lua"),
        ("platform:rse-topology-inline", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/rse.lua", r"Apollo RSE QBox skeleton config running"),
        ("platform:machine-contract", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/machine_contract.lua", r"function machine_contract\.load"),
        ("platform:transaction-route-contract", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/transaction_routes.lua", r"si_cl0_to_ap_hipc"),
        ("platform:system-mgmt-ownership", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/system_mgmt.lua", r"system_mgmt\.ownership"),
        ("platform:ap-compute-helper", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua", r"function ap_compute\.enable_ap_router"),
        ("platform:ap-atu-in-ap-view", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua", r"host_ap_atu\.translation_socket\.bind\s*=\s*[\r\n ]*\"&ap_router\.initiator_socket\""),
        ("platform:system-to-ap-flash", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua", r"platform\.system_to_ap_flash_bridge"),
        ("map:system-ap-flash", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/address_map.lua", r'name\s*=\s*"system_ap_flash"[^\n]*alias_of\s*=\s*"ap_flash"'),
        ("platform:ap-to-system-rse-carveout", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua", r"platform\.ap_to_system_rse_carveout_bridge"),
        ("map:ap-rse-carveout", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/address_map.lua", r'name\s*=\s*"ap_rse_carveout"[^\n]*backing\s*=\s*"ap-rse-carveout"'),
        ("platform:live-ap-rse-default", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/system_mgmt.lua", r'QBOX_RDASPEN_RSE_PS_PROXY",\s*false'),
        ("platform:ap-dram-in-ap-view", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua", r"bind_ap_socket\(platform\.host_ap_dram1,\s*\"target_socket\"\)"),
        ("platform:ap-gic-in-ap-view", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua", r"bind_ap_socket\(platform\.ap_gic,\s*\"dist_iface\"\)"),
        ("platform:ap-gpex-in-ap-view", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua", r"bind_ap_target\(platform\.ap_gpex_0\.ecam_iface\)"),
        ("platform:gpex-systemc-smmu-tbu", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua", r"ap_smmu_lti00\.upstream_socket"),
        ("platform:si-cl0-helper", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/si_cl0.lua", r"si_cl0\.enable"),
        ("platform:qvp-ap-router", "QBOX_PLATFORM_DIR/platforms/apollo/apollo-qvp.lua", r"ap_compute\.enable_ap_router"),
        ("platform:si-cl0-router", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/si_cl0.lua", r"platform\.si_cl0_router"),
        ("platform:si-cl0-atu-data-path", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/si_cl0.lua", r"host_si_atu\.translation_socket"),
        ("platform:smdexp-atu-data-path", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/si_cl0.lua", r"host_smdexp2smd_atu\.translation_socket"),
        ("platform:system-to-ap-shared", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/si_cl0.lua", r"platform\.system_to_ap_shared_bridge"),
        ("platform:system-to-ap-gic", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/si_cl0.lua", r"platform\.system_to_ap_gic_bridge"),
        ("platform:si-cl0-cl1-scmi-bridge", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/si_cl0.lua", r"platform\.si_cl0_to_si_cl1_scmi_bridge"),
        ("platform:si-cl1-helper", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/si_cl1.lua", r"si_cl1\.enable"),
        ("platform:si-cl1-router", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/si_cl1.lua", r"platform\.si_cl1_router"),
        ("platform:si-cl1-hipc-bridge", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/si_cl1.lua", r"platform\.si_cl1_hipc_bridge"),
        ("platform:ros-helper", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ros.lua", r"ros\.peripherals"),
        ("platform:ap-virtio-in-ros-view", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ros.lua", r"bind_ap_target\(virtio\.mem"),
        ("platform:ap-rtc-in-ros-view", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ros.lua", r"platform\.ap_rtc_0\.mem"),
        ("source:si0-mmap", "hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/include/si0_mmap.h", r"SI0_"),
    ],
    "irq": [
        ("irq:ledger", "doc/qbox-apollo-fvp-map-analysis.md", r"Interrupt Map"),
        ("irq:gic-multiview", "doc/qbox-apollo-fvp-full-system-design.md", r"Safety Island GIC Multiview Design"),
        ("irq:si0-header", "hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/include/si0_irq.h", r"IRQ"),
        ("irq:cl1-dts", "hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_fvp_safety_island_c1/apollo_fvp_safety_island_c1.dts", r"gic"),
        ("irq:multiview-task", "doc/qbox-apollo-fvp-full-system-tasks.md", r"QAP-FULL-029"),
        (
            "irq:ap-to-si-cl1-mhu-pair",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/system_mgmt.lua",
            r'pair\s*=\s*"apollo_ap_to_si_cl1"',
        ),
        (
            "irq:si-cl1-to-ap-mhu-pair",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/system_mgmt.lua",
            r'pair\s*=\s*"apollo_si_cl1_to_ap"',
        ),
        (
            "irq:si-cl1-real-doorbell-bridge",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/system_mgmt.lua",
            r'protocol\s*=\s*"doorbell-bridge"',
        ),
        (
            "timer:ap-refclk-ns-spi49",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/config.lua",
            r"AP_SYS_TIMER_IRQ_NS\s*=\s*49",
        ),
        (
            "timer:ap-refclk-secure-spi48",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/config.lua",
            r"AP_SYS_TIMER_IRQ_S\s*=\s*48",
        ),
        (
            "timer:rse-timer0-irq3",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/config.lua",
            r"RSE_TIMER0_IRQ\s*=\s*3",
        ),
        (
            "timer:rse-timer1-irq4",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/config.lua",
            r"RSE_TIMER1_IRQ\s*=\s*4",
        ),
        (
            "timer:rse-timer2-irq5",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/config.lua",
            r"RSE_TIMER2_IRQ\s*=\s*5",
        ),
        (
            "timer:rse-timer3-irq27",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/config.lua",
            r"RSE_TIMER3_IRQ\s*=\s*27",
        ),
        (
            "timer:rse-no-legacy-39-through-42",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/config.lua",
            r"NOT:RSE_TIMER[0-3]_IRQ\s*=\s*(?:39|40|41|42)",
        ),
    ],
    "timer": [
        (
            "timer:css-single-provider",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/system_mgmt.lua",
            r"platform\.css_system_counter\s*=\s*\{[\s\S]*?moduletype\s*=\s*\"arm_system_counter\"",
        ),
        (
            "timer:css-provider-frequency-contract",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/system_mgmt.lua",
            r"input_frequency_hz\s*=\s*125000000[\s\S]*?integer_increment\s*=\s*1[\s\S]*?reported_frequency_hz\s*=\s*125000000",
        ),
        (
            "timer:ap-cpu-mirror-publisher",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua",
            r"ap_cpu_counter_mirror_[\s\S]*?qemu_arm_counter_mirror[\s\S]*?&platform\.css_system_counter",
        ),
        (
            "timer:ap-mmio-mirror-publisher",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua",
            r"ap_timer_counter_mirror[\s\S]*?qemu_arm_mmio_counter_mirror[\s\S]*?&platform\.css_system_counter",
        ),
        (
            "timer:ap-cpu-native-counter",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua",
            r'local cpu\s*=\s*\{[\s\S]*?moduletype\s*=\s*"cpu_arm_cortexA720AE"',
        ),
        (
            "timer:ap-no-pull-counter-bridge",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua",
            r"NOT:qemu_arm_generic_timer_counter_bridge|counter_provider",
        ),
        (
            "timer:si0-css-mirror-publisher",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/si_cl0.lua",
            r"si_cl0_cpu_counter_mirror[\s\S]*?qemu_arm_counter_mirror[\s\S]*?&platform\.css_system_counter",
        ),
        (
            "timer:si1-css-mirror-publisher",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/si_cl1.lua",
            r"si_cl1_cpu_counter_mirror_[\s\S]*?qemu_arm_counter_mirror[\s\S]*?&platform\.css_system_counter",
        ),
        (
            "timer:smd-frontends-share-authority",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/system_mgmt.lua",
            r"host_css_counters_timers[\s\S]*?args\s*=\s*\{\"&platform\.css_system_counter\"\}[\s\S]*?host_css_counters_timers_read[\s\S]*?args\s*=\s*\{\"&platform\.css_system_counter\"\}",
        ),
        (
            "timer:rse-mirror-default-enabled",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/config.lua",
            r'QBOX_APOLLO_RSE_SMD_COUNTER_MIRROR",\s*true',
        ),
        (
            "timer:rse-local-mirror-selection",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/rse.lua",
            r'rse_smd_counter_mirror\s+and[\s\S]*?"qemu_sse_counter_mirror"[\s\S]*?&platform\.css_system_counter',
        ),
        (
            "timer:qemu-cpu-local-affine-state",
            "hsoc-stack/tools/qemu/target/arm/cpu.h",
            r"anchor_count[\s\S]*?generation[\s\S]*?\}\s*gt_counter_mirror",
        ),
        (
            "timer:qemu-cpu-hot-path-no-provider",
            "hsoc-stack/tools/qemu/target/arm/helper.c",
            r"NOT:counter_provider|counter_proxy|qemu_arm_generic_timer_counter_bridge",
        ),
    ],
    "atu": [
        ("atu:analysis", "doc/qbox-apollo-fvp-map-analysis.md", r"ATU|ATW"),
        ("atu:design", "doc/qbox-apollo-fvp-full-system-design.md", r"ATU|ATW"),
        ("atu:task", "doc/qbox-apollo-fvp-full-system-tasks.md", r"QAP-FULL-043"),
    ],
    "reset": [
        (
            "reset:hipc-shared-memory-preserved",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua",
            r"platform\.host_ap_bl2_header_sram\s*=\s*\{[\s\S]*?init_mem\s*=\s*false",
        ),
        (
            "reset:hipc-contract-preserved",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/address_map.lua",
            r'name\s*=\s*"ap_bl2_header_sram"[^\n]*reset_policy\s*=\s*"preserve_on_ap_reset"',
        ),
        (
            "reset:ap-cpu-count-default",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/config.lua",
            r'AP_NUM_CPUS\s*=\s*enable_ap_cpus\s+and\s+getenv_number_or\("QBOX_APOLLO_NUM_CPUS",\s*"4"\)',
        ),
        (
            "reset:ap-cpu-count-limit",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/config.lua",
            r"not\s+enable_ap_cpus\s+or\s+\(AP_NUM_CPUS\s*>=\s*1\s+and\s+AP_NUM_CPUS\s*<=\s*AP_MAX_CPUS\)",
        ),
        (
            "reset:ap-power-domain-count",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/system_mgmt.lua",
            r"power_domain_reset_count\s*=\s*AP_NUM_CPUS",
        ),
        (
            "reset:ap-ppu-cpu0-through-last",
            "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/si_cl0.lua",
            r'for\s+cluster=0,\(SI_CL0_AP_CLUSTER_COUNT\s*-\s*1\)\s+do[\s\S]*'
            r'for\s+core=0,\(SI_CL0_AP_CORE_PER_CLUSTER_COUNT\s*-\s*1\)\s+do[\s\S]*'
            r'power_on_reset\s*=\s*cpu_active\s+and\s+\{[\s\S]*'
            r'"&ap_cpu_"\.\.cpu_index\.\."\.reset"',
        ),
    ],
}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def qbox_platform_dir(root: Path) -> Path:
    value = os.environ.get("QBOX_PLATFORM_DIR")
    if value:
        return Path(value).expanduser().resolve()
    return root / "hsoc-stack/tools/qbox-platform"


def resolve_check_path(root: Path, rel_path: str) -> Path:
    prefix = "QBOX_PLATFORM_DIR/"
    if rel_path.startswith(prefix):
        return qbox_platform_dir(root) / rel_path.removeprefix(prefix)
    return root / rel_path


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def parse_checks(value: str) -> list[str]:
    checks = [part.strip() for part in value.split(",") if part.strip()]
    unknown = sorted(set(checks) - set(CHECKS))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown checks: {', '.join(unknown)}")
    return checks or sorted(CHECKS)


def run_check(root: Path, category: str, item: tuple[str, str, str]) -> dict[str, Any]:
    name, rel_path, pattern = item
    path = resolve_check_path(root, rel_path)
    text = read_text(path)
    forbidden = pattern.startswith("NOT:")
    effective_pattern = pattern.removeprefix("NOT:")
    matched = bool(text and re.search(effective_pattern, text, re.IGNORECASE | re.MULTILINE))
    return {
        "category": category,
        "name": name,
        "path": str(path),
        "pattern": pattern,
        "passed": not matched if forbidden else matched,
    }


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=parse_checks, default=sorted(CHECKS))
    parser.add_argument(
        "--out",
        "--output",
        dest="output",
        type=Path,
        default=root / "build/qbox-apollo-qvp/full-map-validation.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = workspace_root()
    selected = args.check if isinstance(args.check, list) else parse_checks(args.check)
    checks: list[dict[str, Any]] = []
    for category in selected:
        checks.extend(run_check(root, category, item) for item in CHECKS[category])
    passed = all(bool(check["passed"]) for check in checks)
    result = {
        "passed": passed,
        "qbox_platform_dir": str(qbox_platform_dir(root)),
        "selected": selected,
        "checks": checks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.output)
    if not passed:
        for check in checks:
            if not check["passed"]:
                print(f"FAIL {check['name']}: {check['path']} / {check['pattern']}", file=sys.stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
