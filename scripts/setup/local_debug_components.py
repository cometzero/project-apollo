from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import NotRequired, TypedDict


@dataclass(frozen=True)
class Component:
    name: str
    label: str
    domain: str
    target: str
    elf_candidates: tuple[str, ...]
    default_symbols: tuple[str, ...]
    source_roots: tuple[str, ...]
    debugger: str = "gdb-multiarch"
    workspace_candidates: tuple[str, ...] = ()
    runtime_text_address: int | None = None


class ComponentRecord(TypedDict):
    label: str
    domain: str
    target: str
    elf: str
    gdb_script: str
    debugger: str
    arch: str
    has_symtab: bool
    has_debug_info: bool
    has_debug_line: bool
    default_symbol: str | None
    symbols: dict[str, str]
    text_address: str
    source_locations: dict[str, str]
    source_roots: list[str]
    linked_text_address: NotRequired[str]
    load_offset: NotRequired[str]
    build_id: NotRequired[str]
    runtime_elf: NotRequired[str]
    debug_file: NotRequired[str]
    members: NotRequired[list[str]]
    remote: NotRequired[str]


AP_TARGET = "RD_ASD.css.app00.cluster.cpu0"
RSE_TARGET = "RD_ASD.css.smb.rseil.rse.cpu"
SI_CL0_TARGET = "RD_ASD.css.smb.si.cluster0.cpu0"
SI_CL1_TARGET = "RD_ASD.css.smb.si.cluster1.cpu0"

COMPONENTS = (
    Component(
        "tfm-bl1_1", "TF-M BL1_1", "rse", RSE_TARGET,
        ("work/trusted-firmware-m/bin/bl1_1.elf",),
        ("Reset_Handler", "_start", "main"),
        ("hsoc-stack/components/system_mgmt/trusted-firmware-m",),
    ),
    Component(
        "tfm-bl1_2", "TF-M BL1_2", "rse", RSE_TARGET,
        ("work/trusted-firmware-m/bin/bl1_2.elf",),
        ("Reset_Handler", "_start", "main"),
        ("hsoc-stack/components/system_mgmt/trusted-firmware-m",),
    ),
    Component(
        "tfm-bl2", "TF-M BL2", "rse", RSE_TARGET,
        ("work/trusted-firmware-m/bin/bl2.elf",),
        ("Reset_Handler", "_start", "main"),
        ("hsoc-stack/components/system_mgmt/trusted-firmware-m",),
    ),
    Component(
        "tfm-s", "TF-M secure runtime", "rse", RSE_TARGET,
        ("work/trusted-firmware-m/bin/tfm_s.elf",),
        ("tfm_core_init", "main", "Reset_Handler", "_start"),
        ("hsoc-stack/components/system_mgmt/trusted-firmware-m",),
    ),
    Component(
        "scp-si0", "SCP-firmware SI0 RAMFW", "safety_island_cl0",
        SI_CL0_TARGET,
        ("work/scp-firmware/bin/apollo-qvp-si0-bl2.elf",
         "work/scp-firmware/bin/apollo-fvp-si0-bl2.elf"),
        ("arch_exception_reset", "platform_init_hook", "fwk_arch_init",
         "__fwk_run_main_loop"),
        ("hsoc-stack/components/system_mgmt/scp-firmware",),
    ),
    Component(
        "si-cl1-zephyr", "Safety Island CL1 Zephyr demo",
        "safety_island_cl1", SI_CL1_TARGET,
        ("deploy/firmware/zephyr-demos-cl1.elf",
         "../tmp_baremetal/deploy/images/apollo-qvp/zephyr-demos-cl1.elf",
         "../tmp_baremetal/deploy/images/apollo-fvp/zephyr-demos-cl1.elf"),
        ("z_cstart", "main"),
        ("arm-zena-css/components/safety_island/zephyr/src",
         "hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src"),
    ),
    Component(
        "tfa-bl2", "TF-A BL2", "tf_a", AP_TARGET,
        ("work/trusted-firmware-a/apollo_qvp/debug/bl2/bl2.elf",
         "work/trusted-firmware-a/apollo_fvp/debug/bl2/bl2.elf"),
        ("bl2_main", "_start"),
        ("hsoc-stack/components/primary_compute/trusted-firmware-a",),
    ),
    Component(
        "tfa-bl31", "TF-A BL31", "tf_a", AP_TARGET,
        ("work/trusted-firmware-a/apollo_qvp/debug/bl31/bl31.elf",
         "work/trusted-firmware-a/apollo_fvp/debug/bl31/bl31.elf"),
        ("bl31_main", "_start"),
        ("hsoc-stack/components/primary_compute/trusted-firmware-a",),
    ),
    Component(
        "optee-core", "OP-TEE core", "optee", AP_TARGET,
        ("work/optee-os/core/tee.elf",),
        ("_start", "generic_boot_init_primary", "init_primary_helper"),
        ("hsoc-stack/components/primary_compute/optee_os",),
    ),
    Component(
        "u-boot", "U-Boot", "u_boot_linux", AP_TARGET,
        ("work/u-boot/u-boot",),
        ("_start", "board_init_f", "dram_init", "relocate_code", "main_loop"),
        ("hsoc-stack/components/primary_compute/u-boot",),
        runtime_text_address=0xE0000000,
    ),
    Component(
        "linux", "Linux kernel", "u_boot_linux", AP_TARGET,
        ("work/linux/vmlinux",), ("start_kernel", "rest_init"),
        ("hsoc-stack/components/primary_compute/linux",),
    ),
)

HOST_COMPONENTS = (
    Component(
        "qbox-host", "QBox platforms-vp host", "qbox", "localhost",
        ("work/qbox-platform/platforms-vp",), ("sc_main", "main"),
        ("hsoc-stack/tools/qbox", "hsoc-stack/tools/qbox-platform"),
        debugger="gdb",
    ),
    Component(
        "qbox-core", "QBox core library", "qbox", "localhost",
        ("work/qbox-platform/qbox-core/libqbox.so",), (),
        ("hsoc-stack/tools/qbox",), debugger="gdb",
    ),
    Component(
        "libqemu-aarch64", "libqemu AArch64", "libqemu", "localhost",
        (), ("libqemu_init", "libqemu_gdbserver_start"),
        ("hsoc-stack/tools/qemu",), debugger="gdb",
        workspace_candidates=(
            "build/tmp_baremetal/work/x86_64-linux/qbox-libqemu-native/"
            "*/build/qemu-prefix/lib/libqemu-system-aarch64.so",
            "build/tmp_baremetal/work/x86_64-linux/qbox-libqemu-native/"
            "*/build/qemu-prefix/src/qemu-build/libqemu-system-aarch64.so",
        ),
    ),
)


def qbox_plugin_components(local_build: Path) -> tuple[Component, ...]:
    build_dir = local_build / "work/qbox-platform"
    components: list[Component] = []
    for elf in sorted(build_dir.glob("*.so")):
        if not elf.is_file():
            continue
        stem = elf.stem.lower().replace("_", "-")
        components.append(
            Component(
                f"qbox-plugin-{stem}", f"QBox plugin {elf.stem}",
                "qbox-plugin", "localhost",
                (str(elf.relative_to(local_build)),), (),
                ("hsoc-stack/tools/qbox", "hsoc-stack/tools/qbox-platform"),
                debugger="gdb",
            )
        )
    return tuple(components)
