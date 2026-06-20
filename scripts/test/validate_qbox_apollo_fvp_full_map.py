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
        ("platform:apollo-pc-entrypoint", "QBOX_PLATFORM_DIR/platforms/apollo/apollo-pc.lua", r"hw-block/primary_compute\.lua"),
        ("platform:pc-block", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/primary_compute.lua", r"Apollo FVP QBox config running"),
        ("platform:apollo-si-cl1-entrypoint", "QBOX_PLATFORM_DIR/platforms/apollo/apollo-si-cl1.lua", r"hw-block/si_cl1_isolated\.lua"),
        ("platform:si-cl1-isolated-block", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/si_cl1_isolated.lua", r"Apollo FVP Safety Island CL1 isolated"),
        ("platform:apollo-qvp-lua", "QBOX_PLATFORM_DIR/platforms/apollo/apollo-qvp.lua", r"hw-block/rse\.lua"),
        ("platform:apollo-qvp-config", "QBOX_PLATFORM_DIR/platforms/apollo/apollo-qvp.lua", r"hw-block/config\.lua"),
        ("platform:apollo-qvp-fabric", "QBOX_PLATFORM_DIR/platforms/apollo/apollo-qvp.lua", r"hw-block/fabric\.lua"),
        ("platform:config-block", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/config.lua", r"Apollo QVP shared config running"),
        ("platform:fabric-block", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/fabric.lua", r"function fabric\.create"),
        ("platform:apollo-qvp-system-mgmt", "QBOX_PLATFORM_DIR/platforms/apollo/apollo-qvp.lua", r"hw-block/system_mgmt\.lua"),
        ("platform:rse-topology-inline", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/rse.lua", r"Apollo RSE QBox skeleton config running"),
        ("platform:system-mgmt-helper", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/system_mgmt.lua", r"system_mgmt\.add_ap_logical_mhu_aliases"),
        ("platform:system-mgmt-live-cl0-integration", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/system_mgmt.lua", r"system_mgmt\.prepare_live_cl0_integration"),
        ("platform:system-mgmt-ownership", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/system_mgmt.lua", r"system_mgmt\.ownership"),
        ("platform:ap-compute-helper", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua", r"ap_view_router"),
        ("platform:ap-atu-in-ap-view", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua", r"host_ap_atu\.translation_socket\.bind\s*=\s*[\r\n ]*\"&ap_view_router\.initiator_socket\""),
        ("platform:ap-dram-in-ap-view", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua", r"bind_ap_socket\(platform\.host_ap_dram1,\s*\"target_socket\"\)"),
        ("platform:ap-gic-in-ap-view", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua", r"bind_ap_socket\(platform\.ap_gic,\s*\"dist_iface\"\)"),
        ("platform:ap-gpex-in-ap-view", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ap_compute.lua", r"bind_ap_target\(platform\.ap_gpex_0\.ecam_iface\)"),
        ("platform:si-cl0-helper", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/si_cl0.lua", r"si_cl0\.enable"),
        ("platform:qvp-live-cl0-system-mgmt", "QBOX_PLATFORM_DIR/platforms/apollo/apollo-qvp.lua", r"system_mgmt\.prepare_live_cl0_integration"),
        ("platform:si-cl1-helper", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/si_cl1.lua", r"si_cl1\.enable"),
        ("platform:ros-helper", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ros.lua", r"ros\.peripherals"),
        ("platform:ap-virtio-in-ros-view", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ros.lua", r"bind_ap_target\(virtio\.mem"),
        ("platform:ap-rtc-in-ros-view", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/ros.lua", r"platform\.ap_rtc_0\.mem"),
        ("platform:ap-rse-mhu-pbx-logical", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/system_mgmt.lua", r"AP_RSE_SECURE_MHU_PBX_LOGICAL_BASE\s*=\s*0x40680000"),
        ("platform:ap-rse-mhu-mbx-logical", "QBOX_PLATFORM_DIR/platforms/apollo/hw-block/system_mgmt.lua", r"AP_RSE_SECURE_MHU_MBX_LOGICAL_BASE\s*=\s*0x406B0000"),
        ("source:si0-mmap", "hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/include/si0_mmap.h", r"SI0_"),
    ],
    "irq": [
        ("irq:ledger", "doc/qbox-apollo-fvp-map-analysis.md", r"Interrupt Map"),
        ("irq:gic-multiview", "doc/qbox-apollo-fvp-full-system-design.md", r"Safety Island GIC Multiview Design"),
        ("irq:si0-header", "hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/include/si0_irq.h", r"IRQ"),
        ("irq:cl1-dts", "hsoc-stack/components/system_mgmt/zephyrproject/safety_island/boards/arm/fvp_rd_aspen_safety_island/fvp_rd_aspen_safety_island_c1.dts", r"gic"),
        ("irq:multiview-task", "doc/qbox-apollo-fvp-full-system-tasks.md", r"QAP-FULL-029"),
    ],
    "atu": [
        ("atu:analysis", "doc/qbox-apollo-fvp-map-analysis.md", r"ATU|ATW"),
        ("atu:design", "doc/qbox-apollo-fvp-full-system-design.md", r"ATU|ATW"),
        ("atu:task", "doc/qbox-apollo-fvp-full-system-tasks.md", r"QAP-FULL-043"),
    ],
}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def qbox_platform_dir(root: Path) -> Path:
    value = os.environ.get("QBOX_PLATFORM_DIR")
    if value:
        return Path(value).expanduser().resolve()
    return root / "tools/qbox-platform"


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
    return {
        "category": category,
        "name": name,
        "path": str(path),
        "pattern": pattern,
        "passed": bool(text and re.search(pattern, text, re.IGNORECASE | re.MULTILINE)),
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
        default=root / "build/qbox-apollo-fvp/full-map-validation.json",
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
