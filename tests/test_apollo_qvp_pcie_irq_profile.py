from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
QBOX_VIRTIO_NET = (
    ROOT
    / "hsoc-stack/tools/qbox/qemu-components/pci/virtio_net_pci/include/virtio_net_pci.h"
)
QBOX_PLATFORM = ROOT / "hsoc-stack/tools/qbox-platform"
AP_COMPUTE = QBOX_PLATFORM / "platforms/apollo/hw-block/ap_compute.lua"
PRIMARY_COMPUTE = (
    QBOX_PLATFORM / "platforms/apollo/hw-block/primary_compute.lua"
)
SIGNAL_ROUTES = QBOX_PLATFORM / "platforms/apollo/hw-block/signal_routes.lua"
OVERLAY = (
    QBOX_PLATFORM
    / "platforms/apollo/test-profile/apollo-qvp-pcie-irq-overlay.dtso"
)
GUEST_TEST = (
    QBOX_PLATFORM / "platforms/apollo/test-profile/apollo-qvp-pcie-irq-test.sh"
)
QBOX_PLATFORM_CMAKE = QBOX_PLATFORM / "CMakeLists.txt"
PREPARE = ROOT / "scripts/test/prepare_qbox_apollo_pcie_irq_profile.py"
VALIDATE = ROOT / "scripts/test/validate_qbox_apollo_pcie_irq_runtime.py"
DIRECT_RUNNER = ROOT / "scripts/run/run_qbox_apollo_fvp_linux.py"


def load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_virtio_net_pci_supports_stable_pci_slot() -> None:
    text = QBOX_VIRTIO_NET.read_text(encoding="utf-8")

    assert 'cci::cci_param<std::string> p_addr;' in text
    assert 'p_addr("addr", ""' in text
    assert 'm_dev.set_prop_str("addr", p_addr.get_value().c_str())' in text


def test_apollo_test_endpoint_is_opt_in_and_has_fixed_identity() -> None:
    text = AP_COMPUTE.read_text(encoding="utf-8")

    assert 'QBOX_APOLLO_PCIE_IRQ_TEST' in text
    assert 'platform.ap_pcie_irq_test_endpoint' in text
    assert 'moduletype = "virtio_net_pci"' in text
    assert 'addr = "01.0"' in text
    assert 'mac = "52:54:00:12:34:56"' in text
    assert 'netdev_str = "type=user"' in text
    assert 'gicv4_1_cte_size = 8' in text


def test_apollo_build_contract_includes_test_endpoint_module() -> None:
    text = QBOX_PLATFORM_CMAKE.read_text(encoding="utf-8")

    assert "\n    virtio_net_pci\n" in text


def test_primary_compute_direct_profile_uses_same_pcie_path() -> None:
    text = PRIMARY_COMPUTE.read_text(encoding="utf-8")
    runner = DIRECT_RUNNER.read_text(encoding="utf-8")

    assert 'QBOX_APOLLO_PCIE_IRQ_TEST' in text
    assert 'moduletype = "qemu_gpex"' in text
    assert 'bind = "&smmu_lti00.upstream_socket"' in text
    assert 'moduletype = "smmuv3"' in text
    assert 'moduletype = "smmuv3_tbu"' in text
    assert 'topology_id = 0x40' in text
    assert 'gicv4_1_cte_size = 8' in text
    assert 'moduletype = "virtio_net_pci"' in text
    assert 'addr = "01.0"' in text
    assert '"qemu_gpex"' in runner
    assert '"smmuv3"' in runner
    assert '"virtio_net_pci"' in runner


def test_overlay_describes_gpex_smmu_and_its_contract() -> None:
    text = OVERLAY.read_text(encoding="utf-8")

    assert 'target-path = "/soc/interrupt-controller@20800000/msi-controller@20840000"' in text
    assert 'pcie_irq_its: __overlay__' in text
    assert 'compatible = "arm,smmu-v3"' in text
    assert 'reg = <0x1 0xc0000000 0x0 0x20000>' in text
    assert 'compatible = "pci-host-ecam-generic"' in text
    assert 'reg = <0x0 0x43b50000 0x0 0x10000000>' in text
    assert 'iommu-map = <0x8 &pcie_irq_smmu 0x40 0x1>' in text
    assert 'iommu-map-mask = <0xffff>' in text
    assert 'msi-map = <0x0 &pcie_irq_its 0x0 0x10000>' in text
    assert '0x0 0x0 0x0 0x12d 0x4' in text


def test_signal_contract_records_test_profile_ids() -> None:
    text = SIGNAL_ROUTES.read_text(encoding="utf-8")

    assert 'pcie_irq_test = {' in text
    assert 'bdf = "0000:00:01.0"' in text
    assert 'device_id = 0x0008' in text
    assert 'stream_id = 0x0040' in text
    assert 'event_id_base = 0' in text
    assert 'its_translator = 0x20850040' in text
    assert 'legacy_intx_spi = 301' in text


def test_guest_test_emits_bounded_runtime_evidence() -> None:
    text = GUEST_TEST.read_text(encoding="utf-8")

    assert "__QBOX_PCIE_IRQ_TEST_BEGIN__" in text
    assert "__QBOX_PCIE_IRQ_BEFORE__" in text
    assert "__QBOX_PCIE_IRQ_AFTER__" in text
    assert "__QBOX_PCIE_IRQ_TEST_DONE__" in text
    assert "udhcpc" in text
    assert "smp_affinity" in text


def test_profile_helper_adds_intx_bootarg_once() -> None:
    module = load_script("prepare_qbox_apollo_pcie_irq_profile", PREPARE)

    patched = module.append_bootarg(
        'setenv bootargs "console=ttyAMA0 maxcpus=4"\nbooti\n',
        "pci=nomsi",
    )

    assert patched.count("pci=nomsi") == 1
    assert module.append_bootarg(patched, "pci=nomsi") == patched


def test_runtime_validator_accepts_cpu0_lpi_and_intx_increments(tmp_path: Path) -> None:
    module = load_script("validate_qbox_apollo_pcie_irq_runtime", VALIDATE)
    msix = tmp_path / "msix.log"
    intx = tmp_path / "intx.log"
    msix.write_text(
        "\n".join(
            (
                "__QBOX_PCIE_IRQ_TEST_BEGIN__:msix",
                "__QBOX_PCIE_BDF__:0000:00:01.0",
                "__QBOX_PCIE_IFACE__:eth0",
                "__QBOX_PCIE_MSIX__:MSI-X: Enable+ Count=4",
                "__QBOX_PCIE_IRQ_BEFORE__",
                "8192: 1 0 0 0 ITS-MSI 8 Edge virtio0-input.0",
                "__QBOX_PCIE_IRQ_BEFORE_END__",
                "__QBOX_PCIE_IRQ_AFTER__",
                "8192: 4 0 0 0 ITS-MSI 8 Edge virtio0-input.0",
                "__QBOX_PCIE_IRQ_AFTER_END__",
                "__QBOX_PCIE_IRQ_TEST_DONE__:msix",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    intx.write_text(
        "\n".join(
            (
                "__QBOX_PCIE_IRQ_TEST_BEGIN__:intx",
                "__QBOX_PCIE_BDF__:0000:00:01.0",
                "__QBOX_PCIE_IFACE__:eth0",
                "__QBOX_PCIE_CMDLINE__:console=ttyAMA0 pci=nomsi",
                "__QBOX_PCIE_IRQ_BEFORE__",
                "45: 2 0 0 0 GICv3 333 Level virtio0",
                "__QBOX_PCIE_IRQ_BEFORE_END__",
                "__QBOX_PCIE_IRQ_AFTER__",
                "45: 5 0 0 0 GICv3 333 Level virtio0",
                "__QBOX_PCIE_IRQ_AFTER_END__",
                "__QBOX_PCIE_IRQ_TEST_DONE__:intx",
            )
        )
        + "\n",
        encoding="utf-8",
    )

    result = module.validate_pair(msix, intx)

    assert result["status"] == "pass"
    assert result["msix"]["cpu0_delta"] == 3
    assert result["intx"]["cpu0_delta"] == 3
    assert result["identity"]["device_id"] == 0x0008
