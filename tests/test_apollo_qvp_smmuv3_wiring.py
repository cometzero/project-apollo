from pathlib import Path
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[1]
HW_BLOCK: Final = (
    ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block"
)
CONFIG: Final = HW_BLOCK / "config.lua"
AP_COMPUTE: Final = HW_BLOCK / "ap_compute.lua"
ROUTES: Final = HW_BLOCK / "transaction_routes.lua"
SIGNALS: Final = HW_BLOCK / "signal_routes.lua"
QBOX_PLATFORM_CMAKE: Final = ROOT / "hsoc-stack/tools/qbox-platform/CMakeLists.txt"


def test_systemc_mmu720_profile_uses_reusable_smmuv3_core() -> None:
    text = CONFIG.read_text(encoding="utf-8")

    assert 'moduletype = "smmuv3"' in text
    assert "pamax = 48" in text
    assert "sidsize = 8" in text
    assert "iidr = 0x720AE000" in text
    assert 'target_socket = {' in text
    assert 'dma = {bind = "&system_router.target_socket"}' in text
    assert 'local event_irq_target = "&ap_gic.spi_in_65"' in text
    assert "irq_eventq = {bind = event_irq_target}" in text


def test_gpex_lti00_uses_one_smmuv3_tbu_with_stream_id_0x40() -> None:
    text = AP_COMPUTE.read_text(encoding="utf-8")

    assert 'platform.ap_smmu_lti00 = enable_ap_cpus and' in text
    assert 'moduletype = "smmuv3_tbu"' in text
    assert 'args = {"&platform.ap_smmu_0"}' in text
    assert "topology_id = 0x40" in text
    assert 'bind = "&ap_smmu_lti00.upstream_socket"' in text
    downstream = text.split(
        "platform.ap_smmu_lti00.downstream_socket = {", maxsplit=1
    )[1].split("}", maxsplit=1)[0]
    assert 'bind = "&ap_router.target_socket"' in downstream


def test_active_route_and_build_contract_include_reusable_smmuv3() -> None:
    routes = ROUTES.read_text(encoding="utf-8")
    signals = SIGNALS.read_text(encoding="utf-8")
    cmake = QBOX_PLATFORM_CMAKE.read_text(encoding="utf-8")

    assert '"ap_smmu_lti00.upstream_socket"' in routes
    assert 'source = "ap_smmu_0.irq_eventq"' in signals
    assert "\n    smmuv3\n" in cmake
