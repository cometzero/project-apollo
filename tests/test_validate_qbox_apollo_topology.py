from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/validate_qbox_apollo_topology.py"
AP_MAP_SCRIPT = ROOT / "scripts/test/audit_qbox_apollo_ap_memory_map.py"
CONTRACT_DIR = (
    ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block"
)
CONFIG_SOURCE = CONTRACT_DIR / "config.lua"
ADDRESS_MAP_SOURCE = CONTRACT_DIR / "address_map.lua"
TOPOLOGY_SOURCE = CONTRACT_DIR / "topology.lua"
FABRIC_SOURCE = CONTRACT_DIR / "fabric.lua"
AP_SOURCE = CONTRACT_DIR / "ap_compute.lua"
RSE_SOURCE = CONTRACT_DIR / "rse.lua"
SYSTEM_MGMT_SOURCE = CONTRACT_DIR / "system_mgmt.lua"
SI_CL0_SOURCE = CONTRACT_DIR / "si_cl0.lua"
SI_CL1_SOURCE = CONTRACT_DIR / "si_cl1.lua"
SCP_FIRMWARE = ROOT / "hsoc-stack/components/system_mgmt/scp-firmware"
SI_CL0_FIRMWARE_CMAKE = (
    SCP_FIRMWARE / "product/automotive-rd/apollo-qvp/si0_ramfw/Firmware.cmake"
)
SI_CL0_TRANSPORT_CONFIG = (
    SCP_FIRMWARE
    / "product/automotive-rd/apollo-qvp/si0_ramfw/config_transport.c"
)
TRANSPORT_HEADER = SCP_FIRMWARE / "module/transport/include/mod_transport.h"
RSE_BL2_SCMI_COMMS = (
    ROOT
    / "hsoc-stack/components/system_mgmt/trusted-firmware-m/platform/ext/target"
    / "arm/rse/automotive_rd/apollo-qvp/bl2/scmi_comms.c"
)
RSE_BL2_BOOT_HAL = RSE_BL2_SCMI_COMMS.with_name("boot_hal_bl2.c")
CONTRACT_FILES = (
    "topology.lua",
    "address_map.lua",
    "transaction_routes.lua",
    "signal_routes.lua",
    "boot_control.lua",
    "software_contract.lua",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_validator(
    emit: Path,
    *,
    contract_dir: Path = CONTRACT_DIR,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--contract-dir",
            str(contract_dir),
            "--emit",
            str(emit),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def copy_contract(tmp_path: Path) -> Path:
    copied = tmp_path / "contract"
    copied.mkdir()
    for name in CONTRACT_FILES:
        shutil.copy2(CONTRACT_DIR / name, copied / name)
    return copied


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert text.count(old) == 1
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def error_ids(report: dict) -> set[str]:
    return {entry["id"] for entry in report["errors"]}


def test_contract_emits_all_route_evidence_and_artifact_hashes(tmp_path: Path) -> None:
    emit = tmp_path / "topology" / "topology.json"

    result = run_validator(emit)

    assert result.returncode == 0, result.stderr
    expected = {
        "topology.json",
        "address-routes.json",
        "transaction-routes.json",
        "irq-routes.json",
        "reset-routes.json",
        "boot-routes.json",
        "software-routes.json",
        "artifacts.json",
        "validation.json",
    }
    assert {path.name for path in emit.parent.iterdir()} == expected

    topology = load_json(emit)
    assert topology["schema_version"] == 1
    assert topology["machine"] == "apollo-qvp"
    assert {router["name"] for router in topology["routers"]} == {
        "system_router",
        "ap_router",
        "smd_router",
        "rse_router",
        "si_cl0_router",
        "si_cl1_router",
    }
    assert topology["validation"]["topology_frozen"] is True
    assert topology["validation"]["migration_phase"] == "A4_policy_routing"
    assert topology["validation"]["forbid_broad_passthrough"] is True
    assert topology["validation"]["compatibility_debt"] == []

    artifacts = load_json(emit.parent / "artifacts.json")
    local_conf = next(
        entry for entry in artifacts["artifacts"] if entry["name"] == "local_conf"
    )
    assert local_conf["exists"] is True
    assert len(local_conf["sha256"]) == 64
    assert artifacts["configuration"]["machine"] == "apollo-qvp"
    assert artifacts["configuration"]["rd_aspen_variant"] == "cfg2"
    assert artifacts["configuration"]["pc_cpus_count_default"] == 4

    validation = load_json(emit.parent / "validation.json")
    assert validation["status"] == "pass"
    assert validation["errors"] == []


def test_ap_memory_map_audit_accepts_ap_router_bindings(tmp_path: Path) -> None:
    output = tmp_path / "ap-map-audit.json"

    result = subprocess.run(
        [
            sys.executable,
            str(AP_MAP_SCRIPT),
            "--check",
            "coverage",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
    assert load_json(output)["passed"] is True


def test_contract_output_is_stable_for_same_checkout(tmp_path: Path) -> None:
    first = tmp_path / "first" / "topology.json"
    second = tmp_path / "second" / "topology.json"

    first_result = run_validator(first)
    second_result = run_validator(second)

    assert first_result.returncode == 0, first_result.stderr
    assert second_result.returncode == 0, second_result.stderr
    stable_files = (
        "topology.json",
        "address-routes.json",
        "transaction-routes.json",
        "irq-routes.json",
        "reset-routes.json",
        "boot-routes.json",
        "software-routes.json",
    )
    for name in stable_files:
        assert (first.parent / name).read_bytes() == (second.parent / name).read_bytes()


def test_validator_rejects_undocumented_overlap(tmp_path: Path) -> None:
    contract = copy_contract(tmp_path)
    replace_once(
        contract / "address_map.lua",
        'name = "ap_primary_uart"; base = 0x1A400000;',
        'name = "ap_primary_uart"; base = 0x1A410000;',
    )
    emit = tmp_path / "out" / "topology.json"

    result = run_validator(emit, contract_dir=contract)

    assert result.returncode == 1
    report = load_json(emit.parent / "validation.json")
    assert "address:overlap:ap:ap_primary_uart:ap_secure_uart" in error_ids(report)


def test_validator_rejects_nonadjacent_nested_overlap(tmp_path: Path) -> None:
    contract = copy_contract(tmp_path)
    replace_once(
        contract / "address_map.lua",
        '{ name = "ap_rse_mhu_mbx"; base = 0x406B0000; size = 0x00030000; view = "ap"; target = "host_ap_rse_mhu_mbx"; owner = "rse"; access = "secure_rw"; bridge = "ap_to_smd_atu_apu"; alias_of = "ap_to_smd_atu"; priority = 0; reason = "AP secure MHU has a dedicated target inside the programmed ATU aperture"; scope = cfg2; source = guide };',
        '{ name = "ap_rse_mhu_mbx"; base = 0x406B0000; size = 0x00030000; view = "ap"; target = "host_ap_rse_mhu_mbx"; owner = "rse"; access = "secure_rw"; bridge = "ap_to_smd_atu_apu"; scope = cfg2; source = guide };',
    )
    emit = tmp_path / "out" / "topology.json"

    result = run_validator(emit, contract_dir=contract)

    assert result.returncode == 1
    report = load_json(emit.parent / "validation.json")
    assert "address:overlap:ap:ap_to_smd_atu:ap_rse_mhu_mbx" in error_ids(report)


def test_validator_rejects_address_width_overflow(tmp_path: Path) -> None:
    contract = copy_contract(tmp_path)
    replace_once(
        contract / "topology.lua",
        'name = "system"; domain = "system"; width = 52;',
        'name = "system"; domain = "system"; width = 32;',
    )
    emit = tmp_path / "out" / "topology.json"

    result = run_validator(emit, contract_dir=contract)

    assert result.returncode == 1
    report = load_json(emit.parent / "validation.json")
    assert any(item.startswith("address:width:system:") for item in error_ids(report))


def test_validator_rejects_dangling_transaction_initiator(tmp_path: Path) -> None:
    contract = copy_contract(tmp_path)
    replace_once(
        contract / "transaction_routes.lua",
        'initiator = "gpex_dma";',
        'initiator = "missing_gpex_dma";',
    )
    emit = tmp_path / "out" / "topology.json"

    result = run_validator(emit, contract_dir=contract)

    assert result.returncode == 1
    report = load_json(emit.parent / "validation.json")
    assert "transaction:initiator:pcie_dma_to_smmu:missing_gpex_dma" in error_ids(report)


def test_runtime_wiring_has_no_broad_bridge_and_uses_policy_paths() -> None:
    fabric = FABRIC_SOURCE.read_text(encoding="utf-8")
    ap = AP_SOURCE.read_text(encoding="utf-8")
    system_mgmt = SYSTEM_MGMT_SOURCE.read_text(encoding="utf-8")
    si_cl0 = SI_CL0_SOURCE.read_text(encoding="utf-8")
    si_cl1 = SI_CL1_SOURCE.read_text(encoding="utf-8")

    assert "smd_router = {" in fabric
    assert "system_to_smd_nci = {" in fabric
    assert "ap_system_bridge" not in ap
    assert "si_cl0_system_bridge" not in si_cl0
    assert "si_cl1_system_bridge" not in si_cl1
    assert "si_cl0_atu_check_" not in si_cl0
    assert "host_si_atu.translation_socket" in si_cl0
    assert "host_smdexp2smd_atu.translation_socket" in si_cl0
    assert "tbu_lti00_socket" in ap
    assert 'bind = "&smd_router.initiator_socket"' in system_mgmt


def test_smd_sram_backing_covers_the_full_si_atu_region() -> None:
    config = CONFIG_SOURCE.read_text(encoding="utf-8")
    system_mgmt = SYSTEM_MGMT_SOURCE.read_text(encoding="utf-8")

    assert "HOST_SMD_SHARED_SRAM_SIZE = 0x00100000" in config
    assert "platform.host_smd_shared_sram = {" in system_mgmt
    assert "platform.host_smcf_smdexp_sram" not in system_mgmt


def test_si_cl0_mhu_local_views_use_directional_endpoint_pairs() -> None:
    system_mgmt = SYSTEM_MGMT_SOURCE.read_text(encoding="utf-8")
    si_cl0 = SI_CL0_SOURCE.read_text(encoding="utf-8")
    si_cl1 = SI_CL1_SOURCE.read_text(encoding="utf-8")

    assert "SI_CL0_MHU_LOCAL_ROUTES" not in si_cl0
    assert "physical = HOST_AP_SI_PFDI_MONITOR_MHU_MBX_PHYS_BASE" not in si_cl0
    assert "physical = HOST_AP_SI_PFDI_MONITOR_MHU_PBX_PHYS_BASE" not in si_cl0

    assert "platform.si_cl0_rse_mhu_pbx = {" in si_cl0
    assert 'pair = "si_cl0_to_rse"' in si_cl0
    assert "address = 0x38100000" in si_cl0
    assert "platform.si_cl0_rse_mhu_mbx = {" in si_cl0
    assert 'pair = "rse_to_si_cl0"' in si_cl0
    assert "address = 0x38140000" in si_cl0
    assert "platform.host_rse_si_mhu_pbx = {" in system_mgmt
    assert "platform.host_rse_si_mhu_mbx = {" in system_mgmt

    for name, frame, pair, address in (
        ("si_cl0_ap_ns_mhu_pbx", "pbx", "si_cl0_to_ap_ns", "0x38000000"),
        ("si_cl0_ap_ns_mhu_mbx", "mbx", "ap_to_si_cl0_ns", "0x38040000"),
        ("si_cl0_ap_scmi_mhu_pbx", "pbx", "si_cl0_to_ap_scmi", "0x38080000"),
        ("si_cl0_ap_scmi_mhu_mbx", "mbx", "ap_to_si_cl0_scmi", "0x380C0000"),
        (
            "si_cl0_ap_pfdi_monitor_mhu_pbx",
            "pbx",
            "si_cl0_to_ap_pfdi",
            "0x38380000",
        ),
        (
            "si_cl0_ap_pfdi_monitor_mhu_mbx",
            "mbx",
            "ap_to_si_cl0_pfdi",
            "0x383C0000",
        ),
    ):
        table = si_cl0.split(f"platform.{name} =", 1)[1]
        table = table.split("\n    platform.", 1)[0]
        assert f'frame = "{frame}"' in table
        assert f'pair = "{pair}"' in table
        assert f"address = {address}" in table
        assert 'protocol = "doorbell-bridge"' in table

    for name, live_pair in (
        ("host_ap_si_ns_scmi_mhu_pbx", "ap_to_si_cl0_ns"),
        ("host_ap_si_ns_scmi_mhu_mbx", "si_cl0_to_ap_ns"),
        ("host_ap_si_scmi_mhu_pbx", "ap_to_si_cl0_scmi"),
        ("host_ap_si_scmi_mhu_mbx", "si_cl0_to_ap_scmi"),
        ("host_ap_si_pfdi_monitor_mhu_pbx", "ap_to_si_cl0_pfdi"),
        ("host_ap_si_pfdi_monitor_mhu_mbx", "si_cl0_to_ap_pfdi"),
    ):
        table = system_mgmt.split(f"platform.{name} =", 1)[1]
        table = table.split("\n    platform.", 1)[0]
        assert f'"{live_pair}"' in table
        assert '"doorbell-bridge"' in table

    assert "platform.host_ap_si_pfdi_monitor_mhu_mbx =" in system_mgmt
    assert "platform.si_cl0_pfdi_mhu_pbx =" in si_cl0
    assert "platform.si_cl0_pfdi_mhu_mbx =" in si_cl0
    assert "platform.si_cl1_pfdi_reply_mhu_mbx =" in si_cl1

    for source, table_names in (
        (si_cl0, ("si_cl0_pfdi_mhu_pbx", "si_cl0_pfdi_mhu_mbx")),
        (si_cl1, ("si_cl1_pfdi_mhu_pbx", "si_cl1_pfdi_reply_mhu_mbx")),
    ):
        for table_name in table_names:
            table = source.split(f"platform.{table_name} =", 1)[1]
            table = table.split("\n    platform.", 1)[0]
            assert 'protocol = "doorbell-bridge"' in table
            assert 'protocol = "scmi"' not in table


def test_si_cl0_absolute_intids_are_converted_to_qbox_spi_indices() -> None:
    config = CONFIG_SOURCE.read_text(encoding="utf-8")
    si_cl0 = SI_CL0_SOURCE.read_text(encoding="utf-8")

    assert "local GIC_SPI_BASE_INTID = 32" in si_cl0
    for name, intid in (
        ("SI_CL0_AP_NS_MHU_SEND_INTID", 96),
        ("SI_CL0_AP_NS_MHU_RECV_INTID", 97),
        ("SI_CL0_AP_SCMI_MHU_SEND_INTID", 98),
        ("SI_CL0_AP_SCMI_MHU_RECV_INTID", 99),
        ("SI_CL0_AP_PFDI_MHU_SEND_INTID", 102),
        ("SI_CL0_AP_PFDI_MHU_RECV_INTID", 103),
    ):
        assert f"{name} = {intid}" in si_cl0
        assert f"{name} - GIC_SPI_BASE_INTID" in si_cl0

    assert "SI_CL0_RSE_MHU_INTID = 105" in si_cl0
    assert "SI_CL0_CL1_MHU_INTID = 107" in si_cl0
    assert "SI_CL0_UART_INTID = 40" in si_cl0
    assert "SI_CL0_FMU_CRITICAL_INTID = 128" in si_cl0
    assert "SI_CL0_FMU_NON_CRITICAL_INTID = 129" in si_cl0
    assert "SI_CL0_RSE_MHU_INTID - GIC_SPI_BASE_INTID" in si_cl0
    assert "SI_CL0_CL1_MHU_INTID - GIC_SPI_BASE_INTID" in si_cl0
    assert "SI_CL0_UART_INTID - GIC_SPI_BASE_INTID" in si_cl0
    assert "SI_CL0_FMU_CRITICAL_INTID - GIC_SPI_BASE_INTID" in si_cl0
    assert "SI_CL0_FMU_NON_CRITICAL_INTID - GIC_SPI_BASE_INTID" in si_cl0

    for name, irq in (
        ("AP_SI_NS_MHU_PBX_IRQ", 112),
        ("AP_SI_NS_MHU_MBX_IRQ", 113),
        ("AP_SI_SCMI_MHU_PBX_IRQ", 114),
        ("AP_SI_SCMI_MHU_MBX_IRQ", 115),
        ("AP_SI_PFDI_MHU_PBX_IRQ", 118),
        ("AP_SI_PFDI_MHU_MBX_IRQ", 119),
    ):
        assert f"{name} = {irq}" in config


def test_si_cl0_gic_view0_overlays_multiview_extensions_on_functional_alias() -> None:
    si_cl0 = SI_CL0_SOURCE.read_text(encoding="utf-8")
    multiview = si_cl0.split("platform.si_gic_multiview = {", 1)[1]
    multiview = multiview.split("-- CL0 CPU backend and SRAM", 1)[0]

    assert "view0_functional" in si_cl0
    assert "address = SI_CL0_GICD_VIEW0_BASE" in si_cl0
    assert "address = SI_CL0_GICR_VIEW0_BASES[1]" in si_cl0
    assert "view0_dist_cfgid = {" in si_cl0
    assert "view0_dist_iviewr = {" in si_cl0
    assert "view0_redist_0_pwrr = {" in si_cl0
    assert "view0_redist_0_viewr = {" in si_cl0
    assert "view0_redist_0_flushr = {" in si_cl0
    assert "view0_dist = {" not in multiview
    assert "for i=1,4 do" in multiview
    assert """dist_iface = {
            address = SI_CL0_GICD_VIEW1_BASE;
            size = 0x00010000;
            bind = "&si_cl0_router.initiator_socket";
            priority = 10;
            aliases = {""" in si_cl0
    assert """redist_iface_0 = {
            address = SI_CL0_GICR_VIEW1_BASE;
            size = SI_CL0_GICR_SIZE;
            bind = "&si_cl0_router.initiator_socket";
            priority = 10;
            aliases = {""" in si_cl0


def test_rse_and_si_cl0_keep_runtime_proven_execution_contracts() -> None:
    config = CONFIG_SOURCE.read_text(encoding="utf-8")
    topology = TOPOLOGY_SOURCE.read_text(encoding="utf-8")
    rse = RSE_SOURCE.read_text(encoding="utf-8")
    si_cl0 = SI_CL0_SOURCE.read_text(encoding="utf-8")
    si_cl1 = SI_CL1_SOURCE.read_text(encoding="utf-8")
    fabric = FABRIC_SOURCE.read_text(encoding="utf-8")

    assert 'QBOX_RDASPEN_RSE_TCG_MODE", "MULTI"' in config
    assert """rse_sync_policy = getenv_or(
    "QBOX_RDASPEN_RSE_SYNC_POLICY",
    "multithread-freerunning")""" in config
    assert rse.count("tcg_mode = rse_tcg_mode;") == 2
    assert rse.count("sync_policy = rse_sync_policy;") == 2
    assert 'QBOX_APOLLO_FULL_SI_CL0_TCG_MODE", "MULTI"' in si_cl0
    assert (
        'QBOX_APOLLO_FULL_SI_CL0_SYNC_POLICY", "multithread-quantum"'
        in si_cl0
    )
    assert (
        'QBOX_APOLLO_FULL_SI_CL0_PPU_ON_DELAY_NS", "0"'
        in si_cl0
    )
    assert "power_on_load_pulse_width_ns = 0" in si_cl0
    assert "power_on_load_to_reset_delay_ns = 0" in si_cl0
    assert "power_on_status_delay_ns = ctx.getenv_number_or(" in si_cl0
    assert (
        'QBOX_APOLLO_FULL_SI_CL0_PPU_ACCESS_LATENCY_NS", "100"'
        in si_cl0
    )
    assert "access_latency_ns = ctx.getenv_number_or(" in si_cl0
    si_cl1_cluster_ppu = si_cl1.split(
        "platform.host_si_cl1_clus_ppu = {", 1
    )[1].split("\n    }", 1)[0]
    assert "assert_power_on_load = apollo_live_cl1" in si_cl1_cluster_ppu
    assert "power_on_load_pulse_width_ns = 0" in si_cl1_cluster_ppu
    assert topology.count('sync_policy = "multithread-quantum"') == 2
    assert 'sync_policy = "multithread-unconstrained"' not in topology
    assert topology.count('sync_policy = "multithread-freerunning"') == 2
    assert 'sync_policy = "quantum"' not in topology
    assert topology.count('tcg_mode = "MULTI"') == 4


def test_ap_ppus_drive_primary_cold_boot_and_live_secondary_resets() -> None:
    config = CONFIG_SOURCE.read_text(encoding="utf-8")
    address_map = ADDRESS_MAP_SOURCE.read_text(encoding="utf-8")
    si_cl0 = SI_CL0_SOURCE.read_text(encoding="utf-8")
    system_mgmt = SYSTEM_MGMT_SOURCE.read_text(encoding="utf-8")

    reset_targets = config.split("function ap_system_reset_bind_targets()", 1)[1]
    reset_targets = reset_targets.split("\nend", 1)[0]
    assert '"&ap_bl2_reset_loader.reset"' in reset_targets
    assert '"&host_ap_bl2_header_sram.reset"' in reset_targets
    assert '"&host_ap_mhu_ns_shared_sram.reset"' not in reset_targets
    assert '"&ap_reset_gpio.reset_in"' in reset_targets
    assert (
        'name = "ap_mhu_ns_shared_sram"; base = 0x00180000; '
        'size = 0x00001000; view = "ap"; '
        'target = "host_ap_mhu_ns_shared_sram"; owner = "smd"; '
        'access = "rw"; backing = "ap-mhu-ns"; '
        'reset_policy = "preserve_on_ap_reset";'
        in address_map
    )

    ap = AP_SOURCE.read_text(encoding="utf-8")
    assert "platform.ap_cold_reset_fanout = enable_ap_cpus and {" in ap
    assert "reset_out = {bind = ap_system_reset_bind_targets()};" in ap

    ap_core_ppu = si_cl0.split(
        'platform["si_cl0_ap_cluster"..cluster.."_core"..core.."_ppu"] =',
        1,
    )[1]
    ap_core_ppu = ap_core_ppu.split("\n            }", 1)[0]
    assert "assert_power_on_load = enable_ap_cpus and" in ap_core_ppu
    assert "power_on_load_pulse_width_ns = 0" in ap_core_ppu
    assert "power_on_load_to_reset_delay_ns = 0" in ap_core_ppu
    assert 'power_on_load = enable_ap_cpus and cluster == 0 and' in ap_core_ppu
    assert '{bind = "&ap_cold_reset_fanout.reset_in"}' in ap_core_ppu
    assert "assert_power_on_reset = enable_ap_cpus and cluster == 0;" in ap_core_ppu
    assert 'power_on_reset = enable_ap_cpus and cluster == 0 and {' in ap_core_ppu
    assert 'bind = "&ap_cpu_"..core..".reset";' in ap_core_ppu

    synthetic_reset = system_mgmt.split(
        "if platform.host_ap_si_scmi_mhu_pbx ~= nil and", 1
    )[1].split("\n    end", 1)[0]
    assert "not ctx.apollo_live_cl0 then" in synthetic_reset


def test_si_cl0_preserves_a_valid_request_received_before_mhu_start() -> None:
    firmware = SI_CL0_FIRMWARE_CMAKE.read_text(encoding="utf-8")
    transport_config = SI_CL0_TRANSPORT_CONFIG.read_text(encoding="utf-8")
    transport_header = TRANSPORT_HEADER.read_text(encoding="utf-8")

    assert firmware.index('"scmi"') < firmware.index('"transport"')
    assert firmware.index('"scmi-power-domain"') < firmware.index('"transport"')
    assert firmware.index('"si0-platform"') < firmware.index('"transport"')
    for consumer in (
        '"scmi"',
        '"scmi-power-domain"',
        '"scmi-system-power"',
        '"si0-platform"',
        '"scmi-perf"',
        '"pfdi-monitor"',
        '"scmi-pfdi-monitor"',
        '"transport"',
    ):
        assert firmware.index(consumer) < firmware.index('"mhu3"')
    psci_channel = transport_config.split(
        "[SI0_CFGD_MOD_TRANSPORT_EIDX_PSCI]", 1
    )[1].split("#ifdef BUILD_HAS_SCMI_NOTIFICATIONS", 1)[0]
    assert ".notification_id = FWK_ID_NONE" in psci_channel
    assert ".source_id = FWK_ID_NONE" in psci_channel
    assert "MOD_TRANSPORT_POLICY_PRESERVE_PENDING_MAILBOX" in transport_header
    secure_policy = transport_config.split(
        "#define TRANSPORT_CH_SEC_MBX_INIT", 1
    )[1].split("\n\n", 1)[0]
    assert "MOD_TRANSPORT_POLICY_INIT_MAILBOX" in secure_policy
    assert "MOD_TRANSPORT_POLICY_SECURE" in secure_policy
    assert "MOD_TRANSPORT_POLICY_PRESERVE_PENDING_MAILBOX" in secure_policy
    for channel_macro, end_marker in (
        (
            "TRANSPORT_PFDI_MONITOR_AP(cluster, core)",
            "#if (PLATFORM_VARIANT == APOLLO_FVP_VARIANT_FVP)",
        ),
        (
            "TRANSPORT_PFDI_MONITOR_SI_CL1(core)",
            "#endif /* APOLLO_FVP_VARIANT_CFG1 */",
        ),
    ):
        channel = transport_config.split(channel_macro, 1)[1]
        channel = channel.split(end_marker, 1)[0]
        assert ".policies = TRANSPORT_CH_SEC_MBX_INIT" in channel


def test_rse_bl2_waits_for_delayed_si_cl0_scmi_response() -> None:
    comms = RSE_BL2_SCMI_COMMS.read_text(encoding="utf-8")
    boot_hal = RSE_BL2_BOOT_HAL.read_text(encoding="utf-8")

    assert "SCMI_TRANSPORT_POLL_ATTEMPTS" in comms
    wait_body = comms.split("scmi_comms_err_t transport_wait(void)", 1)[1]
    wait_body = wait_body.split("static scmi_comms_err_t transport_abort", 1)[0]
    assert "for (uint32_t attempt = 0;" in wait_body
    assert "scmi_hal_wait(SCMI_HAL_WAIT_TIME);" in wait_body
    assert "value & SI_MHU_COMMAND_MBX_FLAG" in wait_body
    assert "#define MAX_RETRIES_PROTOCOL_VER    30" in boot_hal


def test_ap_gic_view0_control_plane_and_view1_address_contract() -> None:
    config = CONFIG_SOURCE.read_text(encoding="utf-8")
    address_map = ADDRESS_MAP_SOURCE.read_text(encoding="utf-8")
    ap = AP_SOURCE.read_text(encoding="utf-8")

    assert "AP_GIC_VIEW0_DIST_BASE = 0x20000000" in config
    assert "AP_GIC_VIEW0_DIST_SIZE = 0x00080000" in config
    assert "AP_GIC_VIEW0_REDIST_BASE = 0x20080000" in config
    assert "AP_GIC_VIEW0_REDIST_SIZE = 0x00040000" in config
    assert "platform.ap_gic_multiview = {" in ap
    assert 'bind = "&ap_router.initiator_socket"' in ap
    assert "optee_secure_view" not in ap
    assert 'name = "ap_gic_dist"; base = 0x20800000' in address_map
    assert 'name = "ap_gic_redist"; base = 0x20880000' in address_map


def test_ap_gic_inactive_redistributor_tail_is_explicit_razwi() -> None:
    ap = AP_SOURCE.read_text(encoding="utf-8")

    assert "inactive_redists = {" in ap
    assert "AP_GIC_REDIST_BASE +" in ap
    assert "AP_GIC_ACTIVE_REDIST_REGIONS * AP_GIC_REDIST_SIZE" in ap
    assert "(AP_GIC_REDIST_REGIONS - AP_GIC_ACTIVE_REDIST_REGIONS) *" in ap
    assert 'bind = "&ap_router.initiator_socket"' in ap
