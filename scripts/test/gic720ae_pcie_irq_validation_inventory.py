from __future__ import annotations

from typing import Final

SOURCE_PATHS: Final = (
    "scripts/test/run_gic720ae_pcie_irq_validation.py",
    "scripts/test/run_gic720ae_pcie_irq_validation_task9.py",
    "scripts/test/run_gic720ae_pcie_irq_validation_task10.py",
    "scripts/test/gic720ae_pcie_irq_validation_ap_map.py",
    "scripts/test/gic720ae_pcie_irq_validation_contract.py",
    "scripts/test/gic720ae_pcie_irq_validation_execution.py",
    "scripts/test/gic720ae_pcie_irq_validation_inventory.py",
    "scripts/test/gic720ae_pcie_irq_validation_negative.py",
    "scripts/test/gic720ae_pcie_irq_validation_provenance.py",
    "scripts/test/gic720ae_pcie_irq_validation_repository.py",
    "scripts/test/gic720ae_pcie_irq_validation_result.py",
    "scripts/test/gic720ae_pcie_irq_validation_workflow.py",
    "scripts/test/audit_qbox_apollo_ap_memory_map.py",
    "scripts/test/run_qbox_apollo_pcie_irq_task9.py",
    "scripts/test/qbox_apollo_pcie_irq_task9.py",
    "scripts/test/qbox_apollo_pcie_irq_task9_validate.py",
    "scripts/test/qbox_apollo_pcie_irq_task9_process.py",
    "scripts/test/qbox_apollo_pcie_irq_task9_result.py",
    "scripts/test/qbox_apollo_pcie_irq_task9_cleanup.py",
    "scripts/test/apollo_pcie_its_boundary_contract.py",
    "scripts/test/apollo_pcie_its_boundary_io.py",
    "scripts/test/apollo_pcie_its_comparator_qbox.py",
    "scripts/test/compare_apollo_pcie_its_runtime.py",
    "tests/schemas/apollo-pcie-its-boundary-comparison.schema.json",
    "tests/schemas/gic720ae-pcie-irq-validation-provenance.schema.json",
    "tests/schemas/gic720ae-pcie-irq-validation-result.schema.json",
    "tests/test_run_gic720ae_pcie_irq_validation.py",
    "tests/test_gic720ae_pcie_irq_validation_ap_map.py",
    "tests/test_gic720ae_pcie_irq_validation_ap_map_runlocal.py",
    "tests/test_gic720ae_pcie_irq_validation_interrupt.py",
    "tests/test_gic720ae_pcie_irq_validation_provenance.py",
    "tests/test_qbox_apollo_pcie_irq_task9_ap_map.py",
)
REPOSITORIES: Final = {
    "superproject": (
        ".",
        (
            "yocto_build.sh",
            "run_qbox_yocto.sh",
            "scripts/build",
            "scripts/run",
            "scripts/test",
            "tests",
        ),
    ),
    "linux": (
        "hsoc-stack/components/primary_compute/linux",
        (
            "arch/arm64/boot/dts/arm/apollo-fvp.dts",
            "arch/arm64/boot/dts/arm/apollo-fvp.dtsi",
            "arch/arm64/boot/dts/arm/apollo-qvp.dts",
            "arch/arm64/boot/dts/arm/apollo-qvp.dtsi",
        ),
    ),
    "trusted_firmware_a": (
        "hsoc-stack/components/primary_compute/trusted-firmware-a",
        (
            "fdts/apollo_fvp_fvp.dts",
            "fdts/apollo_fvp.dtsi",
            "fdts/apollo_fvp-defs.dtsi",
            "fdts/apollo_qvp_fvp.dts",
            "fdts/apollo_qvp.dtsi",
            "fdts/apollo_qvp-defs.dtsi",
        ),
    ),
    "scp_firmware": (
        "hsoc-stack/components/system_mgmt/scp-firmware",
        (
            "product/automotive-rd/module/pcie_setup",
            "product/automotive-rd/module/pcie_discovery",
            "product/automotive-rd/interface",
            "product/automotive-rd/apollo-fvp/si0_ramfw/config_cmn_cyprus.c",
            "product/automotive-rd/apollo-fvp/si0_ramfw/test",
            "product/test/check_automotive_rd_pcie_module_paths.cmake",
        ),
    ),
    "meta_hsoc_bsp": (
        "hsoc-stack/yocto/meta-hsoc-bsp",
        (
            "recipes-kernel/linux",
            "recipes-devtools/qbox/qbox-apollo-qvp-native.bb",
            "conf/machine/apollo-qvp.conf",
        ),
    ),
    "qbox_platform": (
        "hsoc-stack/tools/qbox-platform",
        (
            "platforms/apollo",
            "systemc-components/gic720ae_power_bridge",
            "systemc-components/gic720ae_messreg",
            "systemc-components/gicx00_multiview",
            "tests/components/gic720ae_power_reset",
            "tests/components/gic720ae_messreg",
            "tests/components/gicx00_multiview",
        ),
    ),
    "qbox_core": (
        "hsoc-stack/tools/qbox",
        (
            "qemu-components/pci",
            "qemu-components/irq-ctrl/arm_gicv3",
            "qemu-components/irq-ctrl/arm_gicv3_its",
            "qemu-components/common",
            "CMakeLists.txt",
        ),
    ),
    "qemu": (
        "hsoc-stack/tools/qemu",
        (
            "hw/intc",
            "hw/pci",
            "hw/pci-host",
            "include/hw/intc",
            "include/hw/pci",
            "tests/qtest/arm-gicv3-baseline-test.c",
            "tests/qtest/arm-gicv4-1-direct-lpi-test.c",
        ),
    ),
}
