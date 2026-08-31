from __future__ import annotations

from nexios_bsp_workflow_support import ROOT


def test_bsp_network_check_rejects_tunnel_only_interfaces() -> None:
    # Given: Linux creates sit/tunnel interfaces even without a usable BSP NIC.
    selftest = (
        ROOT
        / "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/"
        "initrdscripts/nexios-bsp-init/nexios-bsp-selftest"
    ).read_text(encoding="utf-8")

    # When: the network-device selection contract is inspected.
    # Then: tunnel devices cannot satisfy it and the first real NIC is stable.
    assert "lo|sit*|ip6tnl*|tunl*" in selftest
    assert 'network_device="${device_name}"\n    break' in selftest


def test_bsp_ready_marker_is_gated_by_required_selftests() -> None:
    # Given: the BSP shell marker is the runtime completion contract.
    initrd_scripts = (
        ROOT
        / "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/"
        "initrdscripts/nexios-bsp-init"
    )
    init = (initrd_scripts / "init").read_text(encoding="utf-8")
    selftest = (initrd_scripts / "nexios-bsp-selftest").read_text(
        encoding="utf-8"
    )

    # When: the init and self-test failure paths are inspected.
    # Then: required failures prevent the ready marker from being emitted.
    assert "if ! /usr/libexec/nexios-bsp/selftest; then" in init
    assert "NEXIOS_BSP_INITRAMFS_FAILED" in init
    assert 'failures="$((failures + 1))"' in selftest
    assert 'test "${failures}" -eq 0' in selftest


def test_bsp_selftest_covers_boot_and_partition_contracts() -> None:
    # Given: a successful minimal BSP boot must not pivot to the product rootfs.
    selftest = (
        ROOT
        / "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/"
        "initrdscripts/nexios-bsp-init/nexios-bsp-selftest"
    ).read_text(encoding="utf-8")

    # When: the required low-level checks are inspected.
    # Then: initramfs cmdline, console, timer, and two-partition WIC layout
    # are covered.
    for contract in (
        "rdinit=/init",
        "ttyAMA",
        "arch_timer",
        "/sys/class/block/vda1",
        "/sys/class/block/vda2",
        "/sys/class/block/vda3",
    ):
        assert contract in selftest
    assert "/sys/class/block/vda4" not in selftest
