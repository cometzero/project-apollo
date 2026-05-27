#!/usr/bin/env python3
"""Audit QBox RD-Aspen coverage against the generated FVP device tree."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def has_all(text: str, patterns: list[str]) -> bool:
    return all(re.search(pattern, text, re.IGNORECASE | re.MULTILINE) for pattern in patterns)


def config_value(text: str, symbol: str) -> str | None:
    match = re.search(rf"^{re.escape(symbol)}=([ym])$", text, re.MULTILINE)
    if match:
        return match.group(1)
    if re.search(rf"^# {re.escape(symbol)} is not set$", text, re.MULTILINE):
        return "n"
    return None


RSE_FIDELITY_LABELS = {
    "host_si_scr",
    "mhuv3",
    "rse_atu",
    "rse_boot_media",
    "rse_cc3xx",
    "rse_cortex_m55_boot",
    "rse_dma350",
    "rse_integrity_checker",
    "rse_kmu",
    "rse_lcm",
    "rse_nsacfg",
    "rse_oriented_ap_boot",
    "rse_sacfg",
    "rse_scp_endpoint",
    "rse_sysctrl",
}

FIDELITY_DEBT_LABELS = {
    "not-modeled",
    "partial-model",
    "static-map-only",
    "temporary-stub",
}


BLOCKS: list[dict[str, object]] = [
    {
        "name": "cpu_cortex_a720ae_4cpu",
        "driver": "arm64 SMP/PSCI",
        "reference": [
            r"CPU0:cpu@0",
            r"CPU3:cpu@300",
            r"compatible = \"arm,cortex-a720ae\"",
        ],
        "qbox_dts": [r"CPU0: cpu@0", r"CPU3: cpu@300"],
        "qbox_lua": [r"ARM_NUM_CPUS\s*=\s*4", r"cpu_arm_cortexA720AE"],
        "runtime": [r"smp: Brought up 1 node, 4 CPUs", r"CPU3: Booted secondary"],
        "status": "implemented_runtime_pass",
    },
    {
        "name": "dram_banks",
        "driver": "memblock",
        "reference": [r"0x00000000 0x80000000", r"0x00000200 0x00000000"],
        "qbox_dts": [r"0x0 0x80000000 0x0 0x7f000000", r"0x00000200 0x00000000"],
        "qbox_lua": [r"address\s*=\s*INITIAL_DDR_SPACE", r"address\s*=\s*0x20000000000"],
        "runtime": [r"Memory: .* available"],
        "status": "implemented_runtime_pass",
    },
    {
        "name": "armv8_generic_timer_ppi",
        "driver": "arch_timer",
        "reference": [r"compatible = \"arm,armv8-timer\"", r"<1 13 8>", r"<1 14 8>"],
        "qbox_dts": [r"compatible = \"arm,armv8-timer\"", r"<1 13 8>", r"<1 14 8>"],
        "qbox_lua": [r"ARCH_TIMER_NS_EL1_IRQ", r"irq_timer_phys_out"],
        "runtime": [r"arch_timer"],
        "status": "implemented_runtime_pass",
    },
    {
        "name": "gicv3_and_redistributors",
        "driver": "irq-gic-v3",
        "reference": [r"interrupt-controller@20800000", r"#redistributor-regions = <16>"],
        "qbox_dts": [r"interrupt-controller@20800000", r"#redistributor-regions = <16>"],
        "qbox_lua": [r"GIC_REDIST_REGIONS\s*=\s*16", r"GIC_ACTIVE_REDIST_REGIONS\s*=\s*ARM_NUM_CPUS"],
        "runtime": [r"GICv3: 512 SPIs implemented", r"CPU3: found redistributor 300"],
        "status": "implemented_runtime_pass",
    },
    {
        "name": "gicv3_its",
        "driver": "irq-gic-v3-its",
        "reference": [r"msi-controller@20840000", r"compatible = \"arm,gic-v3-its\""],
        "qbox_dts": [r"msi-controller@20840000", r"compatible = \"arm,gic-v3-its\""],
        "qbox_lua": [r"moduletype = \"arm_gicv3_its\"", r"address = 0x20840000"],
        "runtime": [r"ITS \[mem 0x20840000-0x2087ffff\]", r"ITS@0x0000000020840000"],
        "status": "implemented_runtime_pass",
    },
    {
        "name": "pl011_uart",
        "driver": "amba-pl011",
        "reference": [r"serial@1a400000", r"interrupts = <0 52 4>"],
        "qbox_dts": [r"serial@1a400000", r"interrupts = <0 52 4>"],
        "qbox_lua": [r"pl011_uart_0", r"spi_in_52"],
        "runtime": [r"1a400000\.serial: ttyAMA0", r"AMBA PL011 UART driver"],
        "runtime_result_driver_patterns": ["pl011_uart"],
        "status": "implemented_runtime_pass",
    },
    {
        "name": "sbsa_watchdog",
        "driver": "sbsa-gwdt",
        "reference": [r"watchdog@1a420000", r"interrupts = <0 50 4>"],
        "qbox_dts": [r"watchdog@1a420000", r"interrupts = <0 50 4>"],
        "qbox_lua": [r"watchdog_0", r"spi_in_50"],
        "runtime": [r"sbsa-gwdt 1a420000\.watchdog"],
        "status": "implemented_runtime_pass",
    },
    {
        "name": "pl031_rtc",
        "driver": "rtc-pl031",
        "reference": [r"rtc@300d0000", r"interrupts = <0 268 4>"],
        "qbox_dts": [r"rtc@300d0000", r"interrupts = <0 268 4>"],
        "qbox_lua": [r"rtc_0", r"spi_in_268"],
        "runtime": [r"rtc-pl031 300d0000\.rtc"],
        "status": "implemented_runtime_pass",
    },
    {
        "name": "virtio_mmio_block",
        "driver": "virtio_blk",
        "reference": [r"virtio-block@30020000", r"interrupts = <0 257 4>", r"virtio-block@30050000"],
        "qbox_dts": [r"virtio-block@30020000", r"interrupts = <0 257 4>", r"virtio-block@30050000"],
        "qbox_lua": [r"virtioblk_0", r"spi_in_257", r"virtioblk_3", r"spi_in_260"],
        "runtime": [r"virtio_blk virtio[0-9]+", r"\[vda\]", r"\[vdd\]"],
        "runtime_result_driver_patterns": ["virtio"],
        "status": "implemented_runtime_pass",
    },
    {
        "name": "virtio_mmio_net",
        "driver": "virtio_net",
        "reference": [r"virtio-net@30060000", r"interrupts = <0 261 4>"],
        "qbox_dts": [r"virtio-net@30060000", r"interrupts = <0 261 4>"],
        "qbox_lua": [r"virtionet0_0", r"spi_in_261"],
        "runtime": [r"30060000\.virtio-net", r"\beth0:"],
        "runtime_result_driver_patterns": ["virtio"],
        "status": "implemented_runtime_pass",
    },
    {
        "name": "virtio_mmio_rng",
        "driver": "virtio_rng",
        "reference": [r"virtio-rng@30080000", r"interrupts = <0 263 4>"],
        "qbox_dts": [r"virtio-rng@30080000", r"interrupts = <0 263 4>"],
        "qbox_lua": [r"virtiorng_0", r"spi_in_263"],
        "runtime": [r"30080000\.virtio-rng"],
        "runtime_result_driver_patterns": ["virtio"],
        "status": "implemented_runtime_pass",
    },
    {
        "name": "sram_scmi_shmem",
        "driver": "mmio-sram/scmi-shmem",
        "reference": [r"sram@180000", r"arm,scmi-shmem"],
        "qbox_dts": [r"sram@180000", r"arm,scmi-shmem"],
        "qbox_lua": [r"sram_0", r"address = 0x00180000"],
        "runtime": [],
        "status": "static_map_only",
    },
    {
        "name": "si_remoteproc_reserved_memory",
        "driver": "reserved-memory",
        "reference": [
            r"si_cl1_rproc_rsctbl",
            r"&si_cl1_rproc_rsctbl \{ status = \"okay\"; \};",
            r"&si_cl1_vdev0buffer \{ status = \"okay\"; \};",
        ],
        "qbox_dts": [
            r"rsctbl@100000",
            r"status = \"okay\";",
            r"vdev0buffer@160000",
        ],
        "qbox_lua": [
            r"si_cl1_rproc_rsctbl_0",
            r"si_cl1_vdev0buffer_0",
        ],
        "runtime": [],
        "status": "static_map_only",
    },
    {
        "name": "armv7_timer_mem",
        "driver": "timer-of",
        "reference": [r"timer@1a810000", r"arm,armv7-timer-mem", r"interrupts = <0 49 4>"],
        "qbox_dts": [r"timer@1a810000"],
        "qbox_lua": [r"timer_mem_0", r"1a810000", r"1a830000", r"spi_in_49"],
        "runtime": [r"arch_timer_mmio: mmio timer running|arch_mem_timer|1a810000\.timer"],
        "status": "implemented_runtime_pass",
    },
    {
        "name": "dsu_pmu",
        "driver": "arm_dsu_pmu",
        "reference": [r"dsu-pmu-0", r"arm,dsu-pmu", r"interrupts = <0 216 1>"],
        "qbox_dts": [r"dsu-pmu-0"],
        "qbox_lua": [r"dsu_pmu_irq_0", r"spi_in_216"],
        "runtime": [r"arm_dsu_0|dsu-pmu-0"],
        "runtime_result_driver_patterns": ["dsu_pmu"],
        "kernel_config": ["CONFIG_ARM_DSU_PMU"],
        "status": "implemented_runtime_pass",
    },
    {
        "name": "ras_ffh",
        "driver": "ras",
        "reference": [r"ras-ffh@ffa00000", r"arm,ras-ffh", r"interrupts = <0 57 1>"],
        "qbox_dts": [r"ras-ffh@ffa00000", r"status-block-size = <0x00010000>"],
        "qbox_lua": [r"ras_ffh_0", r"spi_in_57"],
        "runtime": [r"Registered estatus provider|ffa00000\.ras-ffh"],
        "kernel_config": ["CONFIG_RAS", "CONFIG_RAS_ESTATUS_DT"],
        "status": "implemented_runtime_pass",
    },
    {
        "name": "smmu_v3",
        "driver": "arm-smmu-v3",
        "reference": [r"iommu@1c0000000", r"arm,smmu-v3", r"interrupts = <0 65 1>"],
        "qbox_dts": [r"iommu@1c0000000"],
        "qbox_lua": [r"1c0000000"],
        "runtime": [r"arm-smmu-v3|iommu@1c0000000|1c0000000\.iommu"],
        "runtime_result_driver_patterns": ["smmu_v3"],
        "kernel_config": ["CONFIG_ARM_SMMU_V3"],
        "status": "implemented_runtime_pass",
    },
    {
        "name": "mhuv3_scmi_transport",
        "driver": "arm_mhuv3/scmi",
        "reference": [r"mhu@40020000", r"mhu@40050000", r"arm,scmi", r"interrupts = <0 112 4>", r"interrupts = <0 113 4>"],
        "qbox_dts": [r"mhu@40020000", r"mhu@40050000", r"arm,scmi"],
        "qbox_lua": [r"mhuv3_db_tx_0", r"mhuv3_db_rx_0", r"spi_in_112", r"spi_in_113"],
        "runtime": [r"arm-mhuv3-mailbox|40020000\.mhu|40050000\.mhu", r"SCMI Protocol v"],
        "kernel_config": ["CONFIG_ARM_MHU_V3", "CONFIG_ARM_SCMI_PROTOCOL", "CONFIG_ARM_SCMI_TRANSPORT_MAILBOX"],
        "status": "implemented_runtime_pass",
    },
    {
        "name": "si_remoteproc_rpmsg",
        "driver": "si-rproc/rpmsg",
        "reference": [r"si_remoteproc", r"arm,si-rproc", r"&si_remoteproc \{ status = \"okay\"; \};"],
        "qbox_dts": [r"si_remoteproc", r"arm,si-rproc"],
        "qbox_lua": [r"400b0000", r"400e0000", r"spi_in_120", r"spi_in_121"],
        "runtime": [
            r"remoteproc remoteproc0: si-cl1 is available",
            r"remote processor si-cl1 is now attached|remoteproc_state:si-cl1:attached",
            r"rproc-virtio .*registered virtio",
            r"virtio_rpmsg_bus .*rpmsg host is online",
            r"rpmsg_net_modprobe_rc:0|rpmsg_net",
        ],
        "runtime_result_driver_patterns": ["arm_si_rproc", "rpmsg"],
        "kernel_config": ["CONFIG_REMOTEPROC", "CONFIG_RPMSG", "CONFIG_RPMSG_VIRTIO"],
        "status": "implemented_runtime_pass",
    },
]


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def runtime_result_driver_patterns_present(
    block: dict[str, object],
    runtime_result: dict[str, object],
) -> bool | None:
    pattern_keys = list(block.get("runtime_result_driver_patterns", []))
    if not pattern_keys:
        return None

    post_login_probe = runtime_result.get("post_login_probe", {})
    if not isinstance(post_login_probe, dict):
        return False

    driver_patterns = post_login_probe.get("driver_patterns", {})
    if not isinstance(driver_patterns, dict):
        return False

    return all(bool(driver_patterns.get(key)) for key in pattern_keys)


def block_result(
    block: dict[str, object],
    texts: dict[str, str],
    runtime_result: dict[str, object],
) -> dict[str, object]:
    reference_patterns = list(block.get("reference", []))
    qbox_dts_patterns = list(block.get("qbox_dts", []))
    qbox_lua_patterns = list(block.get("qbox_lua", []))
    runtime_patterns = list(block.get("runtime", []))
    kernel_symbols = list(block.get("kernel_config", []))

    status = str(block["status"])
    runtime_log_present = (
        has_all(texts["runtime"], runtime_patterns) if runtime_patterns else None
    )
    runtime_result_present = runtime_result_driver_patterns_present(
        block, runtime_result
    )
    if runtime_log_present is None:
        runtime_present = runtime_result_present
    elif runtime_result_present is None:
        runtime_present = runtime_log_present
    else:
        runtime_present = runtime_log_present or runtime_result_present

    result: dict[str, object] = {
        "name": block["name"],
        "driver": block["driver"],
        "status": status,
        "reference_present": has_all(texts["reference"], reference_patterns),
        "qbox_dts_present": has_all(texts["qbox_dts"], qbox_dts_patterns),
        "qbox_lua_present": has_all(texts["qbox_lua"], qbox_lua_patterns),
        "runtime_present": runtime_present,
        "runtime_log_present": runtime_log_present,
        "runtime_result_present": runtime_result_present,
        "kernel_config": {
            symbol: config_value(texts["kernel_config"], symbol) for symbol in kernel_symbols
        },
    }

    if status == "implemented_runtime_pass":
        result["passed"] = all(
            bool(result[key])
            for key in ["reference_present", "qbox_dts_present", "qbox_lua_present", "runtime_present"]
        )
    elif status == "static_map_only":
        result["passed"] = all(
            bool(result[key])
            for key in ["reference_present", "qbox_dts_present", "qbox_lua_present"]
        )
    else:
        result["passed"] = False
        result["blocker"] = (
            "Reference DT and kernel config expose this block, but QBox does not "
            "instantiate a matching device/interrupt and the runtime log has no "
            "successful driver probe."
        )
    return result


def rse_fidelity_audit(runtime_result: dict[str, object]) -> dict[str, object]:
    if runtime_result.get("boot_mode") != "rse-oriented":
        return {
            "present": False,
            "passed": True,
            "reason": "runtime_result_is_not_rse_oriented",
        }

    raw_labels = runtime_result.get("fidelity_labels", {})
    labels = raw_labels if isinstance(raw_labels, dict) else {}
    missing = sorted(RSE_FIDELITY_LABELS - set(labels))
    unexpected = sorted(set(labels) - RSE_FIDELITY_LABELS)
    debt = {
        key: value
        for key, value in sorted(labels.items())
        if value in FIDELITY_DEBT_LABELS
    }

    marker_hits = runtime_result.get("marker_hits", {})
    marker_groups: dict[str, bool] = {}
    if isinstance(marker_hits, dict):
        for group, hits in marker_hits.items():
            if isinstance(hits, dict):
                marker_groups[group] = all(bool(value) for value in hits.values())

    scp_service_model = runtime_result.get("scp_service_model", {})
    live_scp_cpu_gdb = None
    if isinstance(scp_service_model, dict):
        live_scp_cpu_gdb = scp_service_model.get("live_scp_cpu_gdb")

    return {
        "present": True,
        "passed": not missing,
        "expected_labels": sorted(RSE_FIDELITY_LABELS),
        "labels": labels,
        "missing_labels": missing,
        "unexpected_labels": unexpected,
        "debt_labels": debt,
        "marker_groups": marker_groups,
        "live_scp_cpu_gdb": live_scp_cpu_gdb,
    }


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    parser = argparse.ArgumentParser(
        description="Audit full RD-Aspen FVP DT coverage in the QBox platform."
    )
    parser.add_argument(
        "--qbox-conf",
        type=Path,
        default=root / "tools/qbox/platforms/fvp-rd-aspen/conf.lua",
    )
    parser.add_argument(
        "--qbox-dts",
        type=Path,
        default=root / "tools/qbox/platforms/fvp-rd-aspen/fvp-rd-aspen-primary-compute.dts",
    )
    parser.add_argument(
        "--reference-dts",
        type=Path,
        default=root
        / "build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/trusted-firmware-a/"
        / "2.14.0+git/build/rdaspen/debug/fdts/rdaspen_fvp.pre.dts",
    )
    parser.add_argument(
        "--kernel-config",
        type=Path,
        default=root
        / "build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/linux-yocto-rt/"
        / "6.18.5+git/linux-fvp_rd_aspen-preempt-rt-build/.config",
    )
    parser.add_argument(
        "--runtime-result",
        type=Path,
        default=root
        / "build/qbox-fvp-rd-aspen/20260518-212803-exact-maxcpus4-postprobe/result.json",
    )
    parser.add_argument(
        "--runtime-log",
        type=Path,
        default=root
        / "build/qbox-fvp-rd-aspen/20260518-212803-exact-maxcpus4-postprobe/qbox-fvp-rd-aspen.log",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "build/qbox-fvp-rd-aspen/coverage-audit.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runtime_result = read_json(args.runtime_result)
    texts = {
        "reference": read_text(args.reference_dts),
        "qbox_dts": read_text(args.qbox_dts),
        "qbox_lua": read_text(args.qbox_conf),
        "runtime": read_text(args.runtime_log),
        "kernel_config": read_text(args.kernel_config),
    }
    blocks = [block_result(block, texts, runtime_result) for block in BLOCKS]
    implemented = [block for block in blocks if block["status"] != "not_emulated"]
    missing = [block for block in blocks if block["status"] == "not_emulated"]
    rse_audit = rse_fidelity_audit(runtime_result)
    result = {
        "full_coverage_passed": not missing and all(bool(block["passed"]) for block in blocks),
        "implemented_blocks_passed": all(bool(block["passed"]) for block in implemented),
        "rse_fidelity_labels_passed": rse_audit["passed"],
        "paths": {
            "qbox_conf": str(args.qbox_conf.resolve()),
            "qbox_dts": str(args.qbox_dts.resolve()),
            "reference_dts": str(args.reference_dts.resolve()),
            "kernel_config": str(args.kernel_config.resolve()),
            "runtime_result": str(args.runtime_result.resolve()),
            "runtime_log": str(args.runtime_log.resolve()),
        },
        "counts": {
            "blocks": len(blocks),
            "implemented_or_static": len(implemented),
            "not_emulated": len(missing),
            "implemented_failed": sum(1 for block in implemented if not block["passed"]),
        },
        "blocks": blocks,
        "rse_fidelity_audit": rse_audit,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0 if result["implemented_blocks_passed"] and result["rse_fidelity_labels_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
