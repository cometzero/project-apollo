from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import subprocess


ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "yocto_build.sh"
RUN_SCRIPT = ROOT / "run_qbox_yocto.sh"


def run_build_dry_run(
    tmp_path: Path,
    args: list[str],
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "APOLLO_AUTO_RESOURCE_LIMITS": "0",
            "BUILD_DIR": str(tmp_path / "build"),
        }
    )
    return subprocess.run(
        [str(BUILD_SCRIPT), "--dry-run", *args],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def touch_file(path: Path, content: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_qbox_bsp_tree(tmp_path: Path) -> Path:
    yocto_build = tmp_path / "build"
    deploy = yocto_build / "tmp_baremetal/deploy/images/apollo-qvp"
    work = yocto_build / "tmp_baremetal/work/apollo_qvp-poky-linux"
    components = yocto_build / "tmp_baremetal/sysroots-components"
    provider = components / "x86_64/qbox-apollo-qvp-native/usr"
    bindir = provider / "bin"
    data_dir = provider / "share/qbox"
    recipe_sysroot = (
        yocto_build
        / "tmp_baremetal/work/x86_64-linux/qbox-apollo-qvp-native/1.0/"
        "recipe-sysroot-native"
    )

    for path in (
        deploy / "nexios-bsp-initramfs-apollo-qvp.wic",
        deploy / "efi-capsule-update-disk-image-apollo-qvp.img",
        deploy / "rse-rom-image.img",
        deploy / "rse-flash-image.img",
        deploy / "ap-flash-image.img",
        deploy / "bl2.elf",
        deploy / "combined_provisioning_message.bin",
        deploy / "apollo-qvp.dtb",
        deploy / "si0_ramfw.bin",
        deploy / "zephyr-demos-cl1.bin",
        deploy / "zephyr-demos-cl1.elf",
        work / "trusted-firmware-m/2.2.2+git/build/bin/bl1_2.elf",
        work / "trusted-firmware-m/2.2.2+git/build/bin/bl2.elf",
        bindir / "platforms-vp",
        data_dir / "platforms/apollo/apollo-qvp.lua",
    ):
        touch_file(path)
    (bindir / "platforms-vp").chmod(0o755)
    (deploy / "rse-otp-image.img").write_bytes(b"otp")
    (provider / "lib/qbox/modules").mkdir(parents=True)
    recipe_sysroot.mkdir(parents=True)

    qboxconf = deploy / "nexios-bsp-initramfs-apollo-qvp.qboxconf"
    qboxconf.write_text(
        json.dumps(
            {
                "provider": {
                    "name": "qbox-apollo-qvp-native",
                    "bindir": str(bindir),
                    "libdir": str(provider / "lib"),
                    "module_dir": str(provider / "lib/qbox/modules"),
                    "data_dir": str(data_dir),
                },
                "sysroot": {
                    "components_dir": str(components),
                    "recipe_sysroot_native": str(recipe_sysroot),
                },
                "exe": "platforms-vp",
                "config": "platforms/apollo/apollo-qvp.lua",
                "images": {
                    "rootfs_wic": "nexios-bsp-initramfs-apollo-qvp.wic",
                },
                "env": {"QBOX_APOLLO_NUM_CPUS": "4"},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return yocto_build


def run_qbox_bsp_dry_run(tmp_path: Path) -> subprocess.CompletedProcess[str]:
    yocto_build = create_qbox_bsp_tree(tmp_path)
    env = os.environ.copy()
    for name in (
        "DEPLOY_DIR",
        "IMAGE_BASENAME",
        "LOCAL_BUILD_DIR",
        "QBOX_BUILD_DIR",
        "QBOX_CONF",
        "QBOX_CONF_FILE",
        "YOCTO_BUILD_DIR",
        "YOCTO_WORK_DIR",
    ):
        env.pop(name, None)
    return subprocess.run(
        [
            str(RUN_SCRIPT),
            "--build-dir",
            str(yocto_build),
            "--bsp",
            "--headless",
            "--dry-run",
        ],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def runner_argv(output: str) -> list[str]:
    lines = output.splitlines()
    marker_index = lines.index("Headless QBox runner command:")
    return shlex.split(lines[marker_index + 1])


def test_default_build_includes_product_and_bsp_targets(tmp_path: Path) -> None:
    # Given: the default Apollo QVP build profile.
    # When: the public build wrapper is inspected through dry-run.
    result = run_build_dry_run(tmp_path, [])

    # Then: both public image targets are requested.
    assert result.returncode == 0, result.stderr
    assert "nexios-bsp-initramfs" in result.stdout.split()
    assert result.stdout.split()[-1] == "nexios-image"


def test_bsp_build_requests_only_bsp_target(tmp_path: Path) -> None:
    # Given: the dedicated BSP build profile.
    # When: --bsp is selected through the public wrapper.
    result = run_build_dry_run(tmp_path, ["--bsp"])

    # Then: no product image target is requested.
    assert result.returncode == 0, result.stderr
    assert result.stdout.split()[-1] == "nexios-bsp-initramfs"
    assert "nexios-image" not in result.stdout.split()


def test_bsp_build_disables_product_initramfs_dependencies(tmp_path: Path) -> None:
    # Given: the product distro normally injects dm-verity initramfs globally.
    # When: the dedicated BSP build profile is selected.
    result = run_build_dry_run(tmp_path, ["--bsp"])

    # Then: BitBake receives the BSP-only dependency mode explicitly.
    assert result.returncode == 0, result.stderr
    assert "APOLLO_BSP_BUILD_ONLY=1" in result.stdout.split()


def test_bsp_build_preserves_multiconfig_selection(tmp_path: Path) -> None:
    # Given: the dm-verity-on multiconfig and the BSP-only profile.
    # When: both options are selected.
    result = run_build_dry_run(tmp_path, ["--bsp", "--dm-verity=on"])

    # Then: only the BSP target carries the selected multiconfig prefix.
    assert result.returncode == 0, result.stderr
    assert result.stdout.split()[-1] == (
        "mc:apollo-qvp-dm-verity:nexios-bsp-initramfs"
    )
    assert "mc:apollo-qvp-dm-verity:nexios-image" not in result.stdout


def test_qbox_bsp_profile_selects_bsp_artifacts_and_markers(
    tmp_path: Path,
) -> None:
    # Given: an isolated QVP deploy tree containing only BSP image artifacts.
    # When: the QBox wrapper is run with --bsp.
    result = run_qbox_bsp_dry_run(tmp_path)

    # Then: the child runner receives the BSP WIC and completion contract.
    assert result.returncode == 0, result.stderr
    assert "boot profile:  bsp-initramfs" in result.stdout
    assert "nexios-bsp-initramfs-apollo-qvp.qboxconf" in result.stdout
    argv = runner_argv(result.stdout)
    assert argv[argv.index("--rootfs") + 1].endswith(
        "nexios-bsp-initramfs-apollo-qvp.wic"
    )
    assert argv[argv.index("--primary-login-prompt") + 1] == (
        "NEXIOS_BSP_INITRAMFS_READY"
    )
    assert argv[argv.index("--primary-shell-marker") + 1] == "nexios-bsp#"


def test_bsp_metadata_contract_files_exist() -> None:
    # Given: the two owning Yocto layers.
    auto_layer = ROOT / "hsoc-stack/yocto/meta-hsoc-auto-solutions"
    bsp_layer = ROOT / "hsoc-stack/yocto/meta-hsoc-bsp"

    # When: the BSP image contract is inspected.
    expected = (
        auto_layer / "recipes-core/images/nexios-bsp-initramfs.bb",
        auto_layer / "recipes-core/initrdscripts/nexios-bsp-init_1.0.bb",
        auto_layer / "recipes-core/initrdscripts/nexios-bsp-init/init",
        auto_layer
        / "recipes-core/initrdscripts/nexios-bsp-init/nexios-bsp-selftest",
        bsp_layer / "wic/apollo-fvp-nexios-bsp-initramfs.wks.in",
        bsp_layer / "wic/apollo-qvp-nexios-bsp-initramfs.wks.in",
    )

    # Then: every BitBake-consumed metadata input exists.
    assert all(path.is_file() for path in expected)


def test_bsp_uki_uses_timestamp_stable_initramfs_link() -> None:
    # Given: image tasks may remain stamped while BitBake reparses DATETIME.
    image_recipe = (
        ROOT
        / "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-core/images/"
        "nexios-bsp-initramfs.bb"
    ).read_text(encoding="utf-8")

    # When: the UKI input path is resolved after a later parse.
    # Then: it uses the stable image link, not the timestamped IMAGE_NAME.
    assert (
        'AUTO_AD_NEXIOS_UKI_INITRD = '
        '"${IMGDEPLOYDIR}/${IMAGE_LINK_NAME}.cpio.gz"'
    ) in image_recipe
    assert '${IMGDEPLOYDIR}/${IMAGE_NAME}.cpio.gz' not in image_recipe


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
    # Then: initramfs cmdline, console, timer, and A/B WIC layout are covered.
    for contract in (
        "rdinit=/init",
        "ttyAMA",
        "arch_timer",
        "/sys/class/block/vda1",
        "/sys/class/block/vda2",
        "/sys/class/block/vda3",
        "/sys/class/block/vda4",
    ):
        assert contract in selftest


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
    assert "${bindir}/pfdi-sample-app" in split
    assert "${sysconfdir}/pfdi/*.pack" in split


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
