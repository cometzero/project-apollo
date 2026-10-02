"""Semantic equivalents of the Apollo map/IRQ/ATU/reset Lua checks."""
from __future__ import annotations

from pathlib import Path
import re

try:
    from apollo_lua_descriptor import evaluated_platform, evaluate_modules, plain_descriptor, read_sources, DescriptorError
except ModuleNotFoundError:
    from scripts.test.apollo_lua_descriptor import evaluated_platform, evaluate_modules, plain_descriptor, read_sources, DescriptorError


def contracts(source_root: Path) -> dict[str, bool]:
    p, locations = evaluated_platform(source_root)
    sources = read_sources(source_root)

    def value(path):
        obj = p
        for key in path.split("."):
            if not isinstance(obj, dict):
                return None
            obj = obj.get(int(key) if key.isdecimal() else key)
        return obj

    def eq(path, expected):
        return value(path) == expected

    def exists(name, module):
        return eq(name + ".moduletype", module)

    def bind(name, port, target):
        return eq(name + "." + port + ".bind", target)

    def ap_bound(name, port):
        return bind(name, port, "&ap_router.initiator_socket")

    def bridge(name, base, size, source, target):
        return (exists(name, "addrtr") and eq(name + ".target_socket.address", base)
                and eq(name + ".target_socket.size", size)
                and bind(name, "target_socket", "&" + source + ".initiator_socket")
                and bind(name, "initiator_socket", "&" + target + ".target_socket")
                and eq(name + ".target_socket.relative_addresses", False))

    def mirror(name, module):
        return exists(name, module) and eq(name + ".args.2", "&platform.css_system_counter")

    cpus = sum(isinstance(obj, dict) and obj.get("moduletype") == "cpu_arm_cortexA720AE"
               for obj in p.values())
    checks = {
        "platform:apollo-qvp-lua": exists("rse_cpu_pass.cpu_0", "ApolloRseCPU"),
        "platform:apollo-qvp-config": "vp/options.lua" in sources,
        "platform:apollo-qvp-fabric": exists("system_router", "router"),
        "platform:config-block": "vp/options/environment.lua" in sources,
        "platform:config-no-hardware-map-constants": not any(
            re.search(r"(?m)^\s*(?:local\s+)?[A-Z][A-Z0-9_]*(?:BASE|SIZE|IRQ|OFFSET|ADDRESS|STRIDE|CHANNELS|REGIONS)(?:_[A-Z0-9]+)*\s*=", text)
            for name, text in sources.items() if name.startswith("vp/options/")),
        "platform:ap-map-locals": eq("ap_timer_mem.irq.1.bind", "&ap_gic.spi_in_49"),
        "platform:rse-map-locals": eq("rse_cpu_pass.rse_timer_0.irq.bind", "&cpu_0.cpu.nvic.irq_in_3"),
        "platform:system-mgmt-map-locals": bind("host_ap_si_ns_scmi_mhu_pbx", "irq", "&ap_gic.spi_in_112"),
        "platform:fabric-block": exists("system_router", "router"),
        "platform:smd-router": exists("smd_router", "router"),
        "platform:system-to-smd-nci": bridge("system_to_smd_nci", 0x2000000000000, 0x1000000000000, "system_router", "smd_router"),
        "platform:apollo-qvp-system-mgmt": exists("host_reset_ctrl", "zena_reset_ctrl"),
        "platform:rse-topology-inline": exists("rse_cpu_pass.cpu_0", "ApolloRseCPU"),
        "gpio:rse-pl061-pair": all(exists("rse_gpio_" + str(i), "qemu_pl061") for i in range(2)),
        "gpio:rse-ppcexp0-policy": all(eq(f"rse_gpio_{i}_ppc.ppc_register_offset", 0x10)
                                          and eq(f"rse_gpio_{i}_ppc.policy_mask", 1 << i) for i in range(2)),
        "gpio:smd-physical-target": eq("host_smd_gpio.mem.address", 0x20000D0310000)
                                    and bind("host_smd_gpio", "mem", "&smd_router.initiator_socket"),
        "gpio:smd-no-direct-ap-logical-target": value("host_smd_gpio.mem.address") != 0x40750000,
        "platform:direct-config": "vp/options.lua" in sources and "soc/apollo.lua" in sources,
        "platform:system-mgmt-ownership": locations.get("platform.host_ap_atu", {}).get("path", "").startswith("./soc/hw-block/system_mgmt/"),
        "platform:ap-compute-helper": exists("ap_router", "router"),
        "platform:ap-atu-in-ap-view": ap_bound("host_ap_atu", "translation_socket")
                                      and eq("host_ap_atu.translation_socket.relative_addresses", False),
        "platform:system-to-ap-flash": bridge("system_to_ap_flash_bridge", 0x38000000, 0x08000000, "system_router", "ap_router"),
        "platform:ap-to-system-rse-carveout": bridge("ap_to_system_rse_carveout_bridge", 0xFFFE0000, 0x20000, "ap_router", "system_router"),
        "platform:live-ap-rse-default": eq("host_ap_rse_mhu_pbx.protocol", "doorbell-bridge")
                                       and eq("host_ap_rse_mhu_mbx.protocol", "doorbell-bridge"),
        "platform:ap-dram-in-ap-view": ap_bound("host_ap_dram1", "target_socket"),
        "platform:ap-gic-in-ap-view": ap_bound("ap_gic", "dist_iface"),
        "platform:ap-gpex-in-ap-view": ap_bound("ap_gpex_0", "ecam_iface"),
        "platform:gpex-systemc-smmu-tbu": bind("ap_gpex_0", "bus_master", "&ap_smmu_lti00.upstream_socket")
                                         and exists("ap_smmu_lti00", "smmuv3_tbu"),
        "platform:si-cl0-helper": exists("si_cl0_cpu_0", "cpu_arm_cortexR82"),
        "platform:qvp-ap-router": exists("ap_router", "router"),
        "platform:si-cl0-router": exists("si_cl0_router", "router"),
        "platform:si-cl0-atu-data-path": bind("host_si_atu", "translation_socket", "&si_cl0_router.initiator_socket")
                                         and bind("host_si_atu", "initiator_socket", "&system_router.target_socket")
                                         and eq("host_si_atu.translation_socket.relative_addresses", False),
        "platform:smdexp-atu-data-path": bind("host_smdexp2smd_atu", "translation_socket", "&si_cl0_router.initiator_socket")
                                         and bind("host_smdexp2smd_atu", "initiator_socket", "&system_router.target_socket")
                                         and eq("host_smdexp2smd_atu.translation_socket.relative_addresses", False),
        "platform:system-to-ap-shared": bridge("system_to_ap_shared_bridge", 0, 0x200000, "system_router", "ap_router"),
        "platform:system-to-ap-gic": bridge("system_to_ap_gic_bridge", 0x20000000, 0x08000000, "system_router", "ap_router"),
        "platform:si-cl0-cl1-scmi-bridge": bridge("si_cl0_to_si_cl1_scmi_bridge", 0x48000000, 0x1000, "si_cl0_router", "si_cl1_router"),
        "platform:si-cl1-helper": all(exists(f"si_cl1_cpu_{i}", "cpu_arm_cortexR82") for i in range(4)),
        "platform:si-cl1-router": exists("si_cl1_router", "router"),
        "platform:si-cl1-hipc-bridge": bridge("si_cl1_hipc_bridge", 0xE0130000, 0x80000, "si_cl1_router", "ap_router")
                                      and eq("si_cl1_hipc_bridge.mapped_base_addr", 0x100000),
        "platform:ros-helper": exists("ap_dw_i2c_0", "dw_apb_i2c") and exists("ap_rtc_0", "pl031"),
        "platform:ap-virtio-in-ros-view": all(ap_bound(f"ap_virtioblk_{i}", "mem") for i in range(4)),
        "platform:ap-rtc-in-ros-view": ap_bound("ap_rtc_0", "mem"),
        "irq:ap-to-si-cl1-mhu-pair": eq("host_ap_si_cl1_mhu_pbx.pair", "apollo_ap_to_si_cl1"),
        "irq:si-cl1-to-ap-mhu-pair": eq("host_ap_si_cl1_mhu_mbx.pair", "apollo_si_cl1_to_ap"),
        "irq:si-cl1-real-doorbell-bridge": all(eq(f"host_ap_si_cl1_mhu_{frame}.protocol", "doorbell-bridge") for frame in ("pbx", "mbx")),
        "timer:ap-refclk-ns-spi49": eq("ap_timer_mem.irq.1.bind", "&ap_gic.spi_in_49"),
        "timer:ap-refclk-secure-spi48": eq("ap_timer_mem.irq.2.bind", "&ap_gic.spi_in_48"),
        "timer:rse-no-legacy-39-through-42": all(value(f"rse_cpu_pass.rse_timer_{i}.irq.bind") not in
                                                {f"&cpu_0.cpu.nvic.irq_in_{irq}" for irq in range(39,43)} for i in range(4)),
        "gpio:rse-combined-irq34": bind("rse_gpio_irq_or", "signal_out", "&rse_cpu_pass.target_signal_socket_34"),
        "gpio:smd-ap-spi193": bind("host_smd_gpio", "irq", "&ap_gic.spi_in_193"),
        "timer:css-single-provider": exists("css_system_counter", "arm_system_counter") and
            sum(isinstance(obj, dict) and obj.get("moduletype") == "arm_system_counter" for obj in p.values()) == 1,
        "timer:css-provider-frequency-contract": eq("css_system_counter.input_frequency_hz", 125000000)
                                                and eq("css_system_counter.reported_frequency_hz", 125000000),
        "timer:ap-cpu-mirror-publisher": all(mirror(f"ap_cpu_counter_mirror_{i}", "qemu_arm_counter_mirror") for i in range(cpus)),
        "timer:ap-mmio-mirror-publisher": mirror("ap_timer_counter_mirror", "qemu_arm_mmio_counter_mirror"),
        "timer:ap-cpu-native-counter": cpus > 0 and all(eq(f"ap_cpu_{i}.cntfrq_hz", 125000000) for i in range(cpus)),
        "timer:ap-no-pull-counter-bridge": all(obj.get("moduletype") != "qemu_arm_generic_timer_counter_bridge"
                                              and "counter_provider" not in obj for obj in p.values() if isinstance(obj, dict)),
        "timer:si0-css-mirror-publisher": mirror("si_cl0_cpu_counter_mirror", "qemu_arm_counter_mirror"),
        "timer:si1-css-mirror-publisher": all(mirror(f"si_cl1_cpu_counter_mirror_{i}", "qemu_arm_counter_mirror") for i in range(4)),
        "timer:smd-frontends-share-authority": all(eq(name + ".args.1", "&platform.css_system_counter")
                                                   for name in ("host_css_counters_timers", "host_css_counters_timers_read", "host_css_counters_timers_sync")),
        "timer:rse-mirror-default-enabled": exists("rse_cpu_pass.rse_lsc_counter", "qemu_sse_counter_mirror"),
        "timer:rse-local-mirror-selection": exists("rse_cpu_pass.rse_lsc_counter", "qemu_sse_counter_mirror")
                                            and eq("rse_cpu_pass.rse_lsc_counter.args.3", "&platform.css_system_counter"),
        "reset:hipc-shared-memory-preserved": eq("host_ap_bl2_header_sram.init_mem", False),
        "reset:ap-cpu-count-default": cpus == 4,
        "reset:ap-power-domain-count": eq("host_ap_si_scmi_mhu_pbx.power_domain_reset_count", cpus),
        "reset:ap-ppu-cpu0-through-last": all(
            bind(f"si_cl0_ap_cluster{i // 4}_core{i % 4}_ppu", "power_on_reset", f"&ap_cpu_{i}.reset")
            if i < cpus else value(f"si_cl0_ap_cluster{i // 4}_core{i % 4}_ppu.power_on_reset") is None
            for i in range(16)),
    }
    checks["map:system-ap-flash"] = checks["platform:system-to-ap-flash"]
    checks["map:ap-rse-carveout"] = checks["platform:ap-to-system-rse-carveout"]
    for i, irq in enumerate((3, 4, 5, 27)):
        checks[f"timer:rse-timer{i}-irq{irq}"] = eq(f"rse_cpu_pass.rse_timer_{i}.irq.bind", f"&cpu_0.cpu.nvic.irq_in_{irq}")
    entry = "apollo-qvp-saturn-v.lua"
    monitor = plain_descriptor(evaluate_modules(sources, entrypoint=entry,
        environment={"QBOX_APOLLO_MONITOR": "true"})["descriptor"])
    checks["platform:conditional-monitor"] = ("qbox_monitor" not in p and
        monitor.get("qbox_monitor", {}).get("moduletype") == "monitor" and
        monitor.get("qbox_monitor", {}).get("server_port") == 18080)
    rejected = []
    for count in ("0", "17"):
        try:
            evaluate_modules(sources, entrypoint=entry, environment={"QBOX_APOLLO_NUM_CPUS": count})
        except DescriptorError as exc:
            rejected.append("QBOX_APOLLO_NUM_CPUS" in str(exc))
        else:
            rejected.append(False)
    checks["reset:ap-cpu-count-limit"] = all(rejected)
    return checks
