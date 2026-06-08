#!/usr/bin/env python3
"""Validate the QBox RD-Aspen memory map and interrupt wiring."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


MEMORY_REGIONS = {
    "dram0": (0x80000000, 0x7F000000),
    "dram1": (0x20000000000, 0x80000000),
    "sram": (0x00180000, 0x1000),
    "si_cl1_rproc_rsctbl": (0x00100000, 0x20000),
    "si_cl1_vdev0vring0": (0x00120000, 0x20000),
    "si_cl1_vdev0vring1": (0x00140000, 0x20000),
    "si_cl1_vdev0buffer": (0x00160000, 0x20000),
    "ras_buffer": (0xFFA00000, 0x100000),
}

DEVICE_REGIONS = {
    "gicd": (0x20800000, 0x10000),
    "gic_its": (0x20840000, 0x40000),
    "pl011_uart": (0x1A400000, 0x10000),
    "sbsa_gwdt_refresh": (0x1A420000, 0x10000),
    "sbsa_gwdt_control": (0x1A430000, 0x10000),
    "armv7_timer_mem": (0x1A810000, 0x10000),
    "smmu_v3": (0x1C0000000, 0x8000000),
    "si_cl1_mhu_tx": (0x400B0000, 0x30000),
    "si_cl1_mhu_rx": (0x400E0000, 0x30000),
    "virtio_blk0": (0x30020000, 0x10000),
    "virtio_blk1": (0x30030000, 0x10000),
    "virtio_blk2": (0x30040000, 0x10000),
    "virtio_blk3": (0x30050000, 0x10000),
    "virtio_net": (0x30060000, 0x10000),
    "virtio_rng": (0x30080000, 0x10000),
    "rtc_pl031": (0x300D0000, 0x10000),
}

GIC_REDISTS = [(0x20880000 + index * 0x40000, 0x40000) for index in range(16)]

INTERRUPTS = {
    "arch_timer_secure_el1": ("ppi", 13),
    "arch_timer_nonsecure_el1": ("ppi", 14),
    "arch_timer_virtual": ("ppi", 11),
    "arch_timer_nonsecure_el2": ("ppi", 10),
    "arch_timer_virtual_el2": ("ppi", 12),
    "gic_maintenance": ("ppi", 25),
    "pmu": ("ppi", 23),
    "pl011_uart": ("spi", 52),
    "sbsa_gwdt": ("spi", 50),
    "ras_ffh": ("spi", 57),
    "armv7_timer_mem": ("spi", 49),
    "smmu_v3": ("spi", 65),
    "mhuv3_db_tx": ("spi", 112),
    "mhuv3_db_rx": ("spi", 113),
    "si_cl1_mhu_tx": ("spi", 120),
    "si_cl1_mhu_rx": ("spi", 121),
    "dsu_pmu": ("spi", 216),
    "virtio_blk0": ("spi", 257),
    "virtio_blk1": ("spi", 258),
    "virtio_blk2": ("spi", 259),
    "virtio_blk3": ("spi", 260),
    "virtio_net": ("spi", 261),
    "virtio_rng": ("spi", 263),
    "rtc_pl031": ("spi", 268),
}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def strip_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def check_regex(name: str, text: str, pattern: str) -> dict[str, object]:
    matched = re.search(pattern, text, re.IGNORECASE | re.DOTALL) is not None
    return {"name": name, "passed": matched, "pattern": pattern}


def lua_hex_pattern(value: int) -> str:
    return rf"0x0*{value:x}"


def lua_region_pattern(module: str, address: int, size: int) -> str:
    address_pattern = lua_hex_pattern(address)
    if address == 0x80000000:
        address_pattern = rf"(?:INITIAL_DDR_SPACE|{address_pattern})"
    return (
        rf"{re.escape(module)}\s*=\s*\{{.*?"
        rf"address\s*=\s*{address_pattern}\s*[,;].*?"
        rf"size\s*=\s*{lua_hex_pattern(size)}\s*[,;]"
    )


def dts_cell_pattern(value: int) -> str:
    if value == 0:
        return r"\(?\s*(?:0x0+|0)\s*\)?"
    return rf"\(?\s*0x0*{value:x}\s*\)?"


def dts_reg_pattern(address: int, size: int) -> str:
    high = address >> 32
    low = address & 0xFFFFFFFF
    size_high = size >> 32
    size_low = size & 0xFFFFFFFF
    return (
        rf"{dts_cell_pattern(high)}\s+{dts_cell_pattern(low)}\s+"
        rf"{dts_cell_pattern(size_high)}\s+{dts_cell_pattern(size_low)}"
    )


def dts_interrupt_pattern(kind: str, number: int) -> str:
    irq_type = "0" if kind == "spi" else "1"
    return rf"{irq_type}\s+{number}\s+[148]"


def reference_pattern(address: int, size: int) -> str:
    return dts_reg_pattern(address, size)


def validate_qbox_lua(lua_path: Path) -> list[dict[str, object]]:
    text = lua_path.read_text(encoding="utf-8", errors="replace")
    checks: list[dict[str, object]] = []
    module_names = {
        "dram0": "ram_0",
        "dram1": "ram_1",
        "sram": "sram_0",
        "si_cl1_rproc_rsctbl": "si_cl1_rproc_rsctbl_0",
        "si_cl1_vdev0vring0": "si_cl1_vdev0vring0_0",
        "si_cl1_vdev0vring1": "si_cl1_vdev0vring1_0",
        "si_cl1_vdev0buffer": "si_cl1_vdev0buffer_0",
        "ras_buffer": "ras_buffer_0",
        "gicd": "dist_iface",
        "gic_its": "its_0",
        "pl011_uart": "pl011_uart_0",
        "sbsa_gwdt_refresh": "refresh_mem",
        "sbsa_gwdt_control": "control_mem",
        "armv7_timer_mem": "timer_mem_0",
        "si_cl1_mhu_tx": "mhuv3_si_rproc_tx_0",
        "si_cl1_mhu_rx": "mhuv3_si_rproc_rx_0",
        "virtio_blk0": "virtioblk_0",
        "virtio_blk1": "virtioblk_1",
        "virtio_blk2": "virtioblk_2",
        "virtio_blk3": "virtioblk_3",
        "virtio_net": "virtionet0_0",
        "virtio_rng": "virtiorng_0",
        "rtc_pl031": "rtc_0",
    }

    for name, region in {**MEMORY_REGIONS, **DEVICE_REGIONS}.items():
        if name not in module_names:
            continue
        checks.append(
            check_regex(
                f"lua:{name}:reg",
                text,
                lua_region_pattern(module_names[name], *region),
            )
        )

    checks.append(
        check_regex("lua:gic:redist-base", text, r"GIC_REDIST_BASE\s*=\s*0x20880000")
    )
    checks.append(
        check_regex("lua:gic:redist-size", text, r"GIC_REDIST_SIZE\s*=\s*0x40000")
    )
    checks.append(
        check_regex("lua:gic:redist-regions", text, r"GIC_REDIST_REGIONS\s*=\s*16")
    )
    checks.append(
        check_regex("lua:cpu:active-count", text, r"ARM_NUM_CPUS\s*=\s*4")
    )
    checks.append(
        check_regex(
            "lua:gic:active-redist-regions",
            text,
            r"GIC_ACTIVE_REDIST_REGIONS\s*=\s*ARM_NUM_CPUS",
        )
    )
    checks.append(
        check_regex("lua:gic:reserved-redist-windows", text, r"gicr_reserved_")
    )
    checks.append(
        check_regex(
            "lua:armv7_timer_mem:frame0-reg",
            text,
            lua_region_pattern("mem_view", 0x1A830000, 0x10000),
        )
    )
    checks.append(
        check_regex(
            "lua:smmu_v3:reg",
            text,
            r"smmu0_component.*?address\s*=\s*0x0*1c0000000\s*[,;].*?"
            r"size\s*=\s*0x0*8000000\s*[,;]",
        )
    )
    checks.append(
        check_regex(
            "lua:smmu_v3:backend-selector",
            text,
            r"QBOX_RDASPEN_SMMU_BACKEND",
        )
    )
    checks.append(
        check_regex("lua:smmu_v3:qemu-module", text, r"moduletype\s*=\s*\"arm_smmuv3\"")
    )
    checks.append(
        check_regex("lua:smmu_v3:systemc-module", text, r"moduletype\s*=\s*\"mmu720ae\"")
    )
    checks.append(
        check_regex(
            "lua:smmu_v3:gpex-parent",
            text,
            r"args\s*=\s*\{\s*\"&platform\.qemu_inst\"\s*,\s*\"&platform\.gpex_0\"\s*\}",
        )
    )
    checks.append(check_regex("lua:smmu_v3:stage", text, r"stage\s*=\s*\"1\""))
    checks.append(check_regex("lua:ras_ffh:module", text, r"ras_ffh_0\s*=\s*\{"))
    checks.append(check_regex("lua:dsu_pmu:module", text, r"dsu_pmu_irq_0\s*=\s*\{"))
    checks.append(
        check_regex(
            "lua:mhuv3_db_tx:reg",
            text,
            lua_region_pattern("mhuv3_db_tx_0", 0x40020000, 0x30000),
        )
    )
    checks.append(
        check_regex(
            "lua:mhuv3_db_rx:reg",
            text,
            lua_region_pattern("mhuv3_db_rx_0", 0x40050000, 0x30000),
        )
    )
    checks.append(
        check_regex(
            "lua:si_cl1_mhu_tx:reg",
            text,
            lua_region_pattern("mhuv3_si_rproc_tx_0", 0x400B0000, 0x30000),
        )
    )
    checks.append(
        check_regex(
            "lua:si_cl1_mhu_rx:reg",
            text,
            lua_region_pattern("mhuv3_si_rproc_rx_0", 0x400E0000, 0x30000),
        )
    )

    for name, (kind, number) in INTERRUPTS.items():
        if name.startswith("arch_timer"):
            binding = {
                "arch_timer_secure_el1": "ARCH_TIMER_S_EL1_IRQ",
                "arch_timer_nonsecure_el1": "ARCH_TIMER_NS_EL1_IRQ",
                "arch_timer_virtual": "ARCH_TIMER_VIRT_IRQ",
                "arch_timer_nonsecure_el2": "ARCH_TIMER_NS_EL2_IRQ",
            }.get(name)
            if binding:
                checks.append(check_regex(f"lua:{name}:irq", text, binding))
            continue
        if kind == "ppi":
            checks.append(check_regex(f"lua:{name}:irq", text, rf"ppi_in_cpu_.*_{number}"))
        else:
            checks.append(
                check_regex(f"lua:{name}:irq", text, rf"spi_in_{number}\b")
            )
    return checks


def validate_qbox_dts(dts_path: Path) -> list[dict[str, object]]:
    text = strip_ws(dts_path.read_text(encoding="utf-8", errors="replace"))
    checks: list[dict[str, object]] = []

    for name, (address, size) in {**MEMORY_REGIONS, **DEVICE_REGIONS}.items():
        checks.append(
            check_regex(f"dts:{name}:reg", text, dts_reg_pattern(address, size))
        )

    for index, (address, size) in enumerate(GIC_REDISTS):
        checks.append(
            check_regex(
                f"dts:gic:redist{index}:reg",
                text,
                dts_reg_pattern(address, size),
            )
        )

    checks.append(
        check_regex(
            "dts:armv7_timer_mem:frame0-reg",
            text,
            r"frame@20000\s*\{.*?reg\s*=\s*<\s*0x20000\s+0x10000\s*>",
        )
    )
    checks.append(
        check_regex(
            "dts:ras_ffh:node",
            text,
            r"ras-ffh@ffa00000\s*\{.*?compatible\s*=\s*\"arm,ras-ffh\".*?"
            r"reg\s*=\s*<\s*"
            + dts_reg_pattern(0xFFA00000, 0x100000)
            + r"\s*>.*?status-block-size\s*=\s*<\s*0x0*10000\s*>.*?"
            r"memory-region\s*=\s*<\s*&ras_buffer\s*>",
        )
    )
    checks.append(
        check_regex(
            "dts:dsu_pmu:node",
            text,
            r"dsu-pmu-0\s*\{.*?compatible\s*=\s*\"arm,dsu-pmu\".*?"
            r"cpus\s*=\s*<\s*&CPU0\s*>,\s*<\s*&CPU1\s*>,\s*<\s*&CPU2\s*>,\s*<\s*&CPU3\s*>",
        )
    )
    checks.append(
        check_regex(
            "dts:mhuv3_db_tx:node",
            text,
            r"mhu@40020000\s*\{.*?compatible\s*=\s*\"arm,mhuv3\".*?"
            r"reg\s*=\s*<\s*"
            + dts_reg_pattern(0x40020000, 0x30000)
            + r"\s*>.*?#mbox-cells\s*=\s*<\s*3\s*>",
        )
    )
    checks.append(
        check_regex(
            "dts:mhuv3_db_rx:node",
            text,
            r"mhu@40050000\s*\{.*?compatible\s*=\s*\"arm,mhuv3\".*?"
            r"reg\s*=\s*<\s*"
            + dts_reg_pattern(0x40050000, 0x30000)
            + r"\s*>.*?#mbox-cells\s*=\s*<\s*3\s*>",
        )
    )
    checks.append(
        check_regex(
            "dts:scmi:node",
            text,
            r"scmi\s*\{.*?compatible\s*=\s*\"arm,scmi\".*?mboxes\s*=\s*<\s*&mbox_db_tx\s+0\s+0\s+0\s*>.*?shmem\s*=\s*<\s*&scmi_shmem_tx\s*>,\s*<\s*&scmi_shmem_rx\s*>",
        )
    )
    checks.append(
        check_regex(
            "dts:si_remoteproc:node",
            text,
            r"si_remoteproc\s*\{.*?compatible\s*=\s*\"arm,si-rproc\".*?"
            r"si-cl1\s*\{.*?compatible\s*=\s*\"arm,si-channel\".*?"
            r"mboxes\s*=\s*<\s*&si_cl1_mbox_rproc_rx\s+0\s+0\s+0\s*>.*?"
            r"mbox-names\s*=\s*\"vq0_rx\"",
        )
    )

    checks.append(
        check_regex(
            "dts:gic:redist-regions",
            text,
            r"#redistributor-regions\s*=\s*<\s*16\s*>",
        )
    )

    for name, (kind, number) in INTERRUPTS.items():
        if name in {"gic_maintenance", "pmu"}:
            continue
        checks.append(
            check_regex(
                f"dts:{name}:irq",
                text,
                dts_interrupt_pattern(kind, number),
            )
        )
    return checks


def validate_reference(reference_path: Path) -> list[dict[str, object]]:
    if not reference_path.exists():
        return [
            {
                "name": "reference:available",
                "passed": False,
                "pattern": str(reference_path),
            }
        ]

    text = strip_ws(reference_path.read_text(encoding="utf-8", errors="replace"))
    checks: list[dict[str, object]] = [
        {"name": "reference:available", "passed": True, "pattern": str(reference_path)}
    ]
    for name, (address, size) in {**MEMORY_REGIONS, **DEVICE_REGIONS}.items():
        checks.append(
            check_regex(
                f"reference:{name}:reg",
                text,
                reference_pattern(address, size),
            )
        )
    for index, (address, size) in enumerate(GIC_REDISTS):
        checks.append(
            check_regex(
                f"reference:gic:redist{index}:reg",
                text,
                reference_pattern(address, size),
            )
        )
    checks.append(
        check_regex(
            "reference:armv7_timer_mem:frame0-reg",
            text,
            r"frame@20000\s*\{.*?reg\s*=\s*<\s*0x20000\s+0x10000\s*>",
        )
    )
    checks.append(
        check_regex(
            "reference:ras_ffh:node",
            text,
            r"ras-ffh@ffa00000\s*\{.*?compatible\s*=\s*\"arm,ras-ffh\".*?"
            r"reg\s*=\s*<\s*"
            + dts_reg_pattern(0xFFA00000, 0x100000)
            + r"\s*>.*?status-block-size\s*=\s*<\s*0x0*10000\s*>.*?"
            r"memory-region\s*=\s*<\s*&ras_buffer\s*>",
        )
    )
    checks.append(
        check_regex(
            "reference:dsu_pmu:node",
            text,
            r"dsu-pmu-0\s*\{.*?compatible\s*=\s*\"arm,dsu-pmu\".*?"
            r"cpus\s*=\s*<\s*&CPU0\s*>,\s*<\s*&CPU1\s*>,\s*<\s*&CPU2\s*>,\s*<\s*&CPU3\s*>",
        )
    )
    checks.append(
        check_regex(
            "reference:mhuv3_db_tx:node",
            text,
            r"mbox_db_tx:\s*mhu@40020000\s*\{.*?compatible\s*=\s*\"arm,mhuv3\".*?"
            r"reg\s*=\s*<\s*"
            + dts_reg_pattern(0x40020000, 0x30000)
            + r"\s*>.*?#mbox-cells\s*=\s*<\s*3\s*>",
        )
    )
    checks.append(
        check_regex(
            "reference:mhuv3_db_rx:node",
            text,
            r"mbox_db_rx:\s*mhu@40050000\s*\{.*?compatible\s*=\s*\"arm,mhuv3\".*?"
            r"reg\s*=\s*<\s*0x0\s*\(\(0x40020000\)\s*\+\s*\(0x30000\)\)\s*0x0\s*\(0x30000\)\s*>.*?#mbox-cells\s*=\s*<\s*3\s*>",
        )
    )
    checks.append(
        check_regex(
            "reference:scmi:node",
            text,
            r"scmi\s*\{.*?compatible\s*=\s*\"arm,scmi\".*?mboxes\s*=\s*<\s*&mbox_db_tx\s+0\s+0\s+0\s+&mbox_db_rx\s+0\s+0\s+0\s+&mbox_db_rx\s+0\s+0\s+2\s*>.*?shmem\s*=\s*<\s*&scmi_shmem_tx\s+&scmi_shmem_rx\s*>",
        )
    )
    checks.append(
        check_regex(
            "reference:si_remoteproc:node",
            text,
            r"si_remoteproc:\s*si_remoteproc\s*\{.*?compatible\s*=\s*\"arm,si-rproc\".*?"
            r"si_cl1:\s*si-cl1\s*\{.*?compatible\s*=\s*\"arm,si-channel\".*?"
            r"mboxes\s*=\s*<\s*&si_cl1_mbox_rproc_rx\s+0\s+0\s+0\s*>\s*,\s*"
            r"<\s*&si_cl1_mbox_rproc_rx\s+0\s+0\s+1",
        )
    )
    for name, (kind, number) in INTERRUPTS.items():
        if name in {"gic_maintenance", "pmu"}:
            continue
        checks.append(
            check_regex(
                f"reference:{name}:irq",
                text,
                dts_interrupt_pattern(kind, number),
            )
        )
    return checks


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    parser = argparse.ArgumentParser(
        description="Validate QBox RD-Aspen map/interrupts against the FVP DT."
    )
    parser.add_argument(
        "--qbox-conf",
        type=Path,
        default=root / "tools/qbox/platforms/fvp-rd-aspen/conf.lua",
    )
    parser.add_argument(
        "--qbox-dts",
        type=Path,
        default=root
        / "tools/qbox/platforms/fvp-rd-aspen/fvp-rd-aspen-primary-compute.dts",
    )
    parser.add_argument(
        "--reference-dts",
        type=Path,
        default=root
        / "build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-a/"
        / "2.14.0+git/build/rdaspen/debug/fdts/rdaspen_fvp.pre.dts",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "build/qbox-fvp-rd-aspen/map-validation.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checks: list[dict[str, object]] = []
    for path, label in [
        (args.qbox_conf, "QBox Lua"),
        (args.qbox_dts, "QBox DTS"),
    ]:
        if not path.exists():
            checks.append({"name": f"{label}:available", "passed": False, "pattern": str(path)})
        else:
            checks.append({"name": f"{label}:available", "passed": True, "pattern": str(path)})

    if args.qbox_conf.exists():
        checks.extend(validate_qbox_lua(args.qbox_conf))
    if args.qbox_dts.exists():
        checks.extend(validate_qbox_dts(args.qbox_dts))
    checks.extend(validate_reference(args.reference_dts))

    passed = all(bool(check["passed"]) for check in checks)
    result = {
        "passed": passed,
        "qbox_conf": str(args.qbox_conf.resolve()),
        "qbox_dts": str(args.qbox_dts.resolve()),
        "reference_dts": str(args.reference_dts.resolve()),
        "checks": checks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.output)
    if not passed:
        for check in checks:
            if not check["passed"]:
                print(f"FAIL {check['name']}: {check['pattern']}", file=sys.stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
