#!/usr/bin/env python3
"""Validate Apollo full-system QBox map, IRQ, and ATU planning evidence."""
# noqa: SIZE_OK — the declarative CHECKS table is intentionally kept together.

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
from typing import Any


try:
    from apollo_lua_contracts import contracts
    from apollo_lua_descriptor import DescriptorError
except ModuleNotFoundError:
    from scripts.test.apollo_lua_contracts import contracts
    from scripts.test.apollo_lua_descriptor import DescriptorError


CHECKS = {'memory': [('map:ap', 'doc/qbox-apollo-fvp-map-analysis.md', '\\| AP \\|'),
            ('map:rse', 'doc/qbox-apollo-fvp-map-analysis.md', '\\| RSE \\|'),
            ('map:smd',
             'doc/qbox-apollo-fvp-map-analysis.md',
             '\\| SMD(?:/system-wide view| system-wide map)? \\|'),
            ('map:si-cl0', 'doc/qbox-apollo-fvp-map-analysis.md', '\\| Safety Island CL0 \\|'),
            ('map:si-cl1', 'doc/qbox-apollo-fvp-map-analysis.md', '\\| Safety Island CL1 \\|'),
            ('platform:apollo-qvp-lua', 'APOLLO_DESCRIPTOR', 'platform:apollo-qvp-lua'),
            ('platform:apollo-qvp-config', 'APOLLO_DESCRIPTOR', 'platform:apollo-qvp-config'),
            ('platform:apollo-qvp-fabric', 'APOLLO_DESCRIPTOR', 'platform:apollo-qvp-fabric'),
            ('platform:config-block', 'APOLLO_DESCRIPTOR', 'platform:config-block'),
            ('platform:config-no-hardware-map-constants',
             'APOLLO_DESCRIPTOR',
             'platform:config-no-hardware-map-constants'),
            ('platform:ap-map-locals', 'APOLLO_DESCRIPTOR', 'platform:ap-map-locals'),
            ('platform:rse-map-locals', 'APOLLO_DESCRIPTOR', 'platform:rse-map-locals'),
            ('platform:system-mgmt-map-locals', 'APOLLO_DESCRIPTOR', 'platform:system-mgmt-map-locals'),
            ('platform:fabric-block', 'APOLLO_DESCRIPTOR', 'platform:fabric-block'),
            ('platform:smd-router', 'APOLLO_DESCRIPTOR', 'platform:smd-router'),
            ('platform:system-to-smd-nci', 'APOLLO_DESCRIPTOR', 'platform:system-to-smd-nci'),
            ('platform:apollo-qvp-system-mgmt', 'APOLLO_DESCRIPTOR', 'platform:apollo-qvp-system-mgmt'),
            ('platform:conditional-monitor', 'APOLLO_DESCRIPTOR', 'platform:conditional-monitor'),
            ('build:apollo-monitor-target',
             'QBOX_PLATFORM_DIR/CMakeLists.txt',
             'QBOX_APOLLO_REQUIRED_TARGETS[\\s\\S]*?\\n\\s*monitor\\s*\\n'),
            ('build:apollo-qemu-pl061-target',
             'QBOX_PLATFORM_DIR/CMakeLists.txt',
             'QBOX_APOLLO_REQUIRED_TARGETS[\\s\\S]*?\\n\\s*qemu_pl061\\s*\\n'),
            ('gpio:qemu-pl061-wrapper',
             'hsoc-stack/tools/qbox/qemu-components/gpio/qemu_pl061/include/qemu_pl061.h',
             'QemuDevice\\(name, inst, "pl061"\\)[\\s\\S]*?gpio_in[\\s\\S]*?gpio_out'),
            ('monitor:nonblocking-external-scripts',
             'hsoc-stack/tools/qbox/systemc-components/monitor/static/monitor.html',
             '<script\\s+async[^>]*src=\\"https://cdn\\.jsdelivr\\.net/npm/@xterm/xterm@5\\.5\\.0/lib/xterm\\.min\\.js\\"'),
            ('monitor:offline-terminal-fallback',
             'hsoc-stack/tools/qbox/systemc-components/monitor/static/monitor.html',
             'function createTerminalFallback\\(\\)[\\s\\S]*?function initializeTerminal\\(\\)'),
            ('monitor:startup-not-window-load-blocked',
             'hsoc-stack/tools/qbox/systemc-components/monitor/static/monitor.html',
             "fetchObjects\\(\\);\\s*\\n\\s*window\\.addEventListener\\('resize'"),
            ('platform:rse-topology-inline', 'APOLLO_DESCRIPTOR', 'platform:rse-topology-inline'),
            ('gpio:rse-pl061-pair', 'APOLLO_DESCRIPTOR', 'gpio:rse-pl061-pair'),
            ('gpio:rse-ppcexp0-policy', 'APOLLO_DESCRIPTOR', 'gpio:rse-ppcexp0-policy'),
            ('gpio:smd-physical-target', 'APOLLO_DESCRIPTOR', 'gpio:smd-physical-target'),
            ('gpio:smd-no-direct-ap-logical-target',
             'APOLLO_DESCRIPTOR',
             'gpio:smd-no-direct-ap-logical-target'),
            ('platform:direct-config', 'APOLLO_DESCRIPTOR', 'platform:direct-config'),
            ('platform:system-mgmt-ownership', 'APOLLO_DESCRIPTOR', 'platform:system-mgmt-ownership'),
            ('platform:ap-compute-helper', 'APOLLO_DESCRIPTOR', 'platform:ap-compute-helper'),
            ('platform:ap-atu-in-ap-view', 'APOLLO_DESCRIPTOR', 'platform:ap-atu-in-ap-view'),
            ('platform:system-to-ap-flash', 'APOLLO_DESCRIPTOR', 'platform:system-to-ap-flash'),
            ('map:system-ap-flash', 'APOLLO_DESCRIPTOR', 'map:system-ap-flash'),
            ('platform:ap-to-system-rse-carveout',
             'APOLLO_DESCRIPTOR',
             'platform:ap-to-system-rse-carveout'),
            ('map:ap-rse-carveout', 'APOLLO_DESCRIPTOR', 'map:ap-rse-carveout'),
            ('platform:live-ap-rse-default', 'APOLLO_DESCRIPTOR', 'platform:live-ap-rse-default'),
            ('platform:ap-dram-in-ap-view', 'APOLLO_DESCRIPTOR', 'platform:ap-dram-in-ap-view'),
            ('platform:ap-gic-in-ap-view', 'APOLLO_DESCRIPTOR', 'platform:ap-gic-in-ap-view'),
            ('platform:ap-gpex-in-ap-view', 'APOLLO_DESCRIPTOR', 'platform:ap-gpex-in-ap-view'),
            ('platform:gpex-systemc-smmu-tbu', 'APOLLO_DESCRIPTOR', 'platform:gpex-systemc-smmu-tbu'),
            ('platform:si-cl0-helper', 'APOLLO_DESCRIPTOR', 'platform:si-cl0-helper'),
            ('platform:qvp-ap-router', 'APOLLO_DESCRIPTOR', 'platform:qvp-ap-router'),
            ('platform:si-cl0-router', 'APOLLO_DESCRIPTOR', 'platform:si-cl0-router'),
            ('platform:si-cl0-atu-data-path', 'APOLLO_DESCRIPTOR', 'platform:si-cl0-atu-data-path'),
            ('platform:smdexp-atu-data-path', 'APOLLO_DESCRIPTOR', 'platform:smdexp-atu-data-path'),
            ('platform:system-to-ap-shared', 'APOLLO_DESCRIPTOR', 'platform:system-to-ap-shared'),
            ('platform:system-to-ap-gic', 'APOLLO_DESCRIPTOR', 'platform:system-to-ap-gic'),
            ('platform:si-cl0-cl1-scmi-bridge', 'APOLLO_DESCRIPTOR', 'platform:si-cl0-cl1-scmi-bridge'),
            ('platform:si-cl1-helper', 'APOLLO_DESCRIPTOR', 'platform:si-cl1-helper'),
            ('platform:si-cl1-router', 'APOLLO_DESCRIPTOR', 'platform:si-cl1-router'),
            ('platform:si-cl1-hipc-bridge', 'APOLLO_DESCRIPTOR', 'platform:si-cl1-hipc-bridge'),
            ('platform:ros-helper', 'APOLLO_DESCRIPTOR', 'platform:ros-helper'),
            ('platform:ap-virtio-in-ros-view', 'APOLLO_DESCRIPTOR', 'platform:ap-virtio-in-ros-view'),
            ('platform:ap-rtc-in-ros-view', 'APOLLO_DESCRIPTOR', 'platform:ap-rtc-in-ros-view'),
            ('source:si0-mmap',
             'hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/include/si0_mmap.h',
             'SI0_')],
 'irq': [('irq:ledger', 'doc/qbox-apollo-fvp-map-analysis.md', 'Interrupt Map'),
         ('irq:gic-multiview',
          'doc/qbox-apollo-fvp-full-system-design.md',
          'Safety Island GIC Multiview Design'),
         ('irq:si0-header',
          'hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/include/si0_irq.h',
          'IRQ'),
         ('irq:cl1-dts',
          'hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src/boards/hsoc/apollo_fvp_safety_island_c1/apollo_fvp_safety_island_c1.dts',
          'gic'),
         ('irq:multiview-task', 'doc/qbox-apollo-fvp-full-system-tasks.md', 'QAP-FULL-029'),
         ('irq:ap-to-si-cl1-mhu-pair', 'APOLLO_DESCRIPTOR', 'irq:ap-to-si-cl1-mhu-pair'),
         ('irq:si-cl1-to-ap-mhu-pair', 'APOLLO_DESCRIPTOR', 'irq:si-cl1-to-ap-mhu-pair'),
         ('irq:si-cl1-real-doorbell-bridge', 'APOLLO_DESCRIPTOR', 'irq:si-cl1-real-doorbell-bridge'),
         ('timer:ap-refclk-ns-spi49', 'APOLLO_DESCRIPTOR', 'timer:ap-refclk-ns-spi49'),
         ('timer:ap-refclk-secure-spi48', 'APOLLO_DESCRIPTOR', 'timer:ap-refclk-secure-spi48'),
         ('timer:rse-timer0-irq3', 'APOLLO_DESCRIPTOR', 'timer:rse-timer0-irq3'),
         ('timer:rse-timer1-irq4', 'APOLLO_DESCRIPTOR', 'timer:rse-timer1-irq4'),
         ('timer:rse-timer2-irq5', 'APOLLO_DESCRIPTOR', 'timer:rse-timer2-irq5'),
         ('timer:rse-timer3-irq27', 'APOLLO_DESCRIPTOR', 'timer:rse-timer3-irq27'),
         ('timer:rse-no-legacy-39-through-42', 'APOLLO_DESCRIPTOR', 'timer:rse-no-legacy-39-through-42'),
         ('gpio:rse-combined-irq34', 'APOLLO_DESCRIPTOR', 'gpio:rse-combined-irq34'),
         ('gpio:smd-ap-spi193', 'APOLLO_DESCRIPTOR', 'gpio:smd-ap-spi193')],
 'timer': [('timer:css-single-provider', 'APOLLO_DESCRIPTOR', 'timer:css-single-provider'),
           ('timer:css-provider-frequency-contract',
            'APOLLO_DESCRIPTOR',
            'timer:css-provider-frequency-contract'),
           ('timer:ap-cpu-mirror-publisher', 'APOLLO_DESCRIPTOR', 'timer:ap-cpu-mirror-publisher'),
           ('timer:ap-mmio-mirror-publisher', 'APOLLO_DESCRIPTOR', 'timer:ap-mmio-mirror-publisher'),
           ('timer:ap-cpu-native-counter', 'APOLLO_DESCRIPTOR', 'timer:ap-cpu-native-counter'),
           ('timer:ap-no-pull-counter-bridge', 'APOLLO_DESCRIPTOR', 'timer:ap-no-pull-counter-bridge'),
           ('timer:si0-css-mirror-publisher', 'APOLLO_DESCRIPTOR', 'timer:si0-css-mirror-publisher'),
           ('timer:si1-css-mirror-publisher', 'APOLLO_DESCRIPTOR', 'timer:si1-css-mirror-publisher'),
           ('timer:smd-frontends-share-authority',
            'APOLLO_DESCRIPTOR',
            'timer:smd-frontends-share-authority'),
           ('timer:rse-mirror-default-enabled', 'APOLLO_DESCRIPTOR', 'timer:rse-mirror-default-enabled'),
           ('timer:rse-local-mirror-selection', 'APOLLO_DESCRIPTOR', 'timer:rse-local-mirror-selection'),
           ('timer:qemu-cpu-local-affine-state',
            'hsoc-stack/tools/qemu/target/arm/cpu.h',
            'anchor_count[\\s\\S]*?generation[\\s\\S]*?\\}\\s*gt_counter_mirror'),
           ('timer:qemu-cpu-hot-path-no-provider',
            'hsoc-stack/tools/qemu/target/arm/helper.c',
            'NOT:counter_provider|counter_proxy|qemu_arm_generic_timer_counter_bridge')],
 'atu': [('atu:analysis', 'doc/qbox-apollo-fvp-map-analysis.md', 'ATU|ATW'),
         ('atu:design', 'doc/qbox-apollo-fvp-full-system-design.md', 'ATU|ATW'),
         ('atu:task', 'doc/qbox-apollo-fvp-full-system-tasks.md', 'QAP-FULL-043')],
 'reset': [('reset:hipc-shared-memory-preserved',
            'APOLLO_DESCRIPTOR',
            'reset:hipc-shared-memory-preserved'),
           ('reset:ap-cpu-count-default', 'APOLLO_DESCRIPTOR', 'reset:ap-cpu-count-default'),
           ('reset:ap-cpu-count-limit', 'APOLLO_DESCRIPTOR', 'reset:ap-cpu-count-limit'),
           ('reset:ap-power-domain-count', 'APOLLO_DESCRIPTOR', 'reset:ap-power-domain-count'),
           ('reset:ap-ppu-cpu0-through-last', 'APOLLO_DESCRIPTOR', 'reset:ap-ppu-cpu0-through-last')]}

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


def run_check(root: Path, category: str, item: tuple[str, str, str],
              semantic: dict[str, bool] | None = None) -> dict[str, Any]:
    name, rel_path, pattern = item
    if rel_path == "APOLLO_DESCRIPTOR":
        path = qbox_platform_dir(root) / "platforms/apollo/apollo-qvp-saturn-v.lua"
        try:
            evaluated = semantic if semantic is not None else contracts(path.parent)
            return {"category": category, "name": name, "path": str(path),
                    "pattern": "evaluated descriptor contract", "passed": evaluated.get(name, False)}
        except (DescriptorError, OSError) as exc:
            return {"category": category, "name": name, "path": str(path),
                    "passed": False, "error": str(exc)}
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
    try:
        semantic = contracts(qbox_platform_dir(root) / "platforms/apollo")
    except (DescriptorError, OSError) as exc:
        semantic = {}
        checks.append({"name": "descriptor:evaluation", "category": "memory",
                       "passed": False, "error": str(exc)})
    for category in selected:
        checks.extend(run_check(root, category, item, semantic) for item in CHECKS[category])
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
                detail = check.get("error") or f"{check.get('path', '')} / {check.get('pattern', '')}"
                print(f"FAIL {check['name']}: {detail}", file=sys.stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
