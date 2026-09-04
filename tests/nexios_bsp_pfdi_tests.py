from __future__ import annotations

from nexios_bsp_workflow_support import ROOT


def test_bsp_image_uses_minimal_pfdi_runtime_package() -> None:
    # Given: long-running Apollo boots require the PFDI periodic test service.
    auto_layer = ROOT / "hsoc-stack/yocto/meta-hsoc-auto-solutions"
    image = (
        auto_layer / "recipes-core/images/nexios-bsp-initramfs.bb"
    ).read_text(encoding="utf-8")
    split = (
        auto_layer
        / "dynamic-layers/meta-ewaol/recipes-demos/pfdi/"
        "platform-fault-detection.bbappend"
    ).read_text(encoding="utf-8")
    # When: the BSP package set and upstream PFDI package split are inspected.
    # Then: the C runtime is included without the Python demo dependencies.
    assert "pfdi-bsp-app" in image
    assert 'RDEPENDS:pfdi-bsp-app = "libpfdi"' in split
    assert "${bindir}/pfdi-cli" in split
    assert "${bindir}/pfdi-sample-app" in split
    assert "${sysconfdir}/pfdi/*.pack" in split


def test_qvp_pfdi_agent_enables_tx_completion_irq() -> None:
    common = (
        ROOT
        / "hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/"
        "zephyr-demos-cl1-apollo-common.inc"
    ).read_text(encoding="utf-8")
    module = (
        ROOT
        / "hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/zephyr-kernel/"
        "files/pfdi-tx-irq/pfdi_agent_tx_irq.c"
    ).read_text(encoding="utf-8")

    assert 'SRC_URI:append:apollo-qvp = " file://pfdi-tx-irq"' in common
    assert 'PFDI_TX_IRQ_MODULE = "${UNPACKDIR}/pfdi-tx-irq"' in common
    assert "mbox_set_enabled_dt(&channels[channel], true)" in module
    assert "SYS_INIT(pfdi_tx_irq_init, APPLICATION," in module


def test_bsp_init_starts_and_checks_pfdi_service() -> None:
    # Given: probing /dev/cpu/*/pfdi alone does not feed the SI PFDI monitor.
    scripts = (
        ROOT
        / "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/"
        "initrdscripts/nexios-bsp-init"
    )
    init = (scripts / "init").read_text(encoding="utf-8")
    selftest = (scripts / "nexios-bsp-selftest").read_text(encoding="utf-8")

    # When: the minimal init sequence and required self-tests are inspected.
    # Then: the PFDI app is started before ready and its liveness is required.
    assert "/usr/bin/pfdi-sample-app" in init
    assert "/etc/pfdi/pfdi_test_config_0.pack" in init
    assert "pfdi_service" in selftest
    assert "pidof pfdi-sample-app" in selftest
