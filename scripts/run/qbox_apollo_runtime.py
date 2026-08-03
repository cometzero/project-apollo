"""Internal Apollo QBox runtime engine.

This module is not a standalone entrypoint. The canonical full-system runner
invokes it through its private ``--runtime-child`` process boundary.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import stat
import struct
import subprocess
import sys
import time

from gic720ae_operation_manifest import load_operations, serialize_operation


REQUIRED_TARGETS = [
    "platforms-vp",
    "keep_alive",
    "addrtr",
    "router",
    "gs_memory",
    "host_scr",
    "loader",
    "char_backend_file",
    "char_backend_stdio",
    "uart-pl011",
    "global_peripheral_initiator",
    "cpu_arm_cortexA720AE",
    "cpu_arm_cortexR82",
    "arm_gicv3",
    "arm_gicv3_its",
    "qemu_gpex",
    "virtio_mmio_blk",
    "virtio_mmio_net",
    "virtio_mmio_rng",
    "arm_smmuv3",
    "mmu720ae",
    "reset_gpio",
    "pl031",
    "sbsa_gwdt",
    "cpu_arm_cortexM55",
    "nvic_armv7m",
    "qemu_cc3xx",
    "qemu_hexagon_qtimer",
    "mhu320ae",
    "gicx00_multiview",
    "host_cmn_cyprus",
    "host_gtimer",
    "host_ni710ae_nci",
    "host_ppu",
    "cc3xx",
    "dma350",
    "rse_atu",
    "rse_integrity_checker",
    "rse_kmu",
    "rse_lcm",
    "rse_sam",
    "strata_flash_j3",
    "host_smcf_mgi",
    "host_system_pll",
    "reset_fanout",
    "rse_sysctrl",
]

PLATFORM_STDOUT_LOG = "qbox-platform.log"
QEMU_TRACE_LOG = "qemu-rse-trace.log"
RSE_PC_TRACE_LOG = "rse-pc-trace.log"
AP_PC_TRACE_LOG = "ap-pc-trace.log"
RSE_CC3XX_STATS = "rse-cc3xx-stats.json"
QBOX_PERF_PROFILE_DIR = "qbox-perf-profile"
MAX_REQUIRED_PASS_MARKERS = 32
MAX_REQUIRED_PASS_MARKER_FILES = 8
MAX_REQUIRED_PASS_MARKER_BYTES = 1024 * 1024
MAX_REQUIRED_PASS_MARKER_LENGTH = 512
QEMU_INITIATOR_PROFILE_DIR = "qemu-initiator"
CC3XX_PROFILE = "qemu-cc3xx-profile.json"
RSE_HOTPATH_PROFILE = "rse-hotpath-profile.json"
QBOX_RUNTIME_EXECUTABLES = {
    "platforms-vp",
}
SRAM_DMI_FORBIDDEN_ENV = (
    "QBOX_RDASPEN_HOST_SI_CL0_SRAM_MAP_FILE",
    "QBOX_RDASPEN_HOST_SI_CL1_SRAM_MAP_FILE",
    "QBOX_RDASPEN_HOST_AP_SHARED_SRAM_MAP_FILE",
    "QBOX_RDASPEN_HOST_AP_BL2_HEADER_SRAM_MAP_FILE",
    "QBOX_RDASPEN_RSE_DIRECT_FILE_ALIASES",
    "QBOX_RDASPEN_RSE_DIRECT_SI_SRAM_ALIAS",
    "QBOX_RDASPEN_RSE_DIRECT_SI_SRAM_CODE_ALIAS_SIZE",
)
SRAM_DMI_SHM_PREFIXES = ("ra-si0-", "ra-si1-", "ra-aps-", "ra-aph-")
RSE_CC3XX_BASE_S = 0x50154000
RSE_HOTPATH_MEMCPY_DEFAULT = 0x11000488
RSE_HOTPATH_MEMSET_DEFAULT = 0x11000448
RSE_LMS_VERIFY_DEFAULT = 0x11009BAD
WIC_BOOT_PARTITION_OFFSET = 2048 * 512
WIC_BOOT_ENTRY = "::/loader/entries/boot.conf"
WIC_UBOOT_SCRIPT = "::/boot.scr"

CONSOLE_LOGS = {
    "rse": "qbox-rse.log",
    "scp": "qbox-scp.log",
    "secure_console": "qbox-secure-console.log",
    "primary_console": "qbox-primary-console.log",
}
RANGE_LIMITED_FLASH_DMI_DEFAULTS = {
    "QBOX_RDASPEN_ATU_DMI": "true",
    "QBOX_RDASPEN_BOOT_FLASH_DMI": "true",
    "QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES": "0x7000:0x260000",
    "QBOX_RDASPEN_HOST_MEMORY_DMI": "true",
    "QBOX_RDASPEN_AP_FLASH_DMI_RANGES": "0x7000:0x240000",
}
CC3XX_STATUS_READ_FASTPATH_VALUES = {
    0x0B0: 0x00000001,  # PKA_PIPE_RDY
    0x0B4: 0x00000001,  # PKA_DONE
    0x470: 0x00000000,  # AES_BUSY
    0x4FC: 0x00000001,  # AES_RBG_SEEDING_RDY
    0x824: 0xFFFFFFFF,  # CLK_STATUS
    0x910: 0x00000000,  # CRYPTO_BUSY
    0x91C: 0x00000000,  # HASH_BUSY
    0xA7C: 0x00000001,  # HOST_CC_IS_IDLE
    0xA90: 0x00000001,  # HOST_SF_READY
    0xC20: 0x00000000,  # DIN_MEM_DMA_BUSY
    0xC38: 0x00000000,  # DIN_SRAM_DMA_BUSY
    0xC50: 0x00000001,  # FIFO_IN_EMPTY
    0xD20: 0x00000000,  # DOUT_MEM_DMA_BUSY
    0xD38: 0x00000000,  # DOUT_SRAM_DMA_BUSY
    0xD50: 0x00000001,  # DOUT_FIFO_EMPTY
}

REQUIRED_MARKERS = {
    "rse_boot": [
        "Starting TF-M BL1_1",
        "Jumping to the first image slot",
    ],
    "rse_scp_handoff": [
        "Init SCMI comm to SCP succeeded",
        "RSE to SCP SCMI power on AP succeeded",
        "SCMI Comms subscribed to power state notifications",
    ],
    "measured_boot": [
        "BL1_2",
        "BL2",
        "SI_CL0",
        "AP_BL2",
        "RT_0",
        "SECURE_RT_EL3",
        "SECURE_RT_EL1_SPMD",
        "BL_33",
    ],
    "linux_boot": [
        "fvp-rd-aspen login:",
        "root@fvp-rd-aspen",
    ],
}

PROGRESS_MARKERS = {
    "rse_bl1_1": "Starting TF-M BL1_1",
    "rse_jump_bl1_2": "Jumping to BL1_2",
    "rse_bl1_2": "Starting TF-M BL1_2",
    "rse_attempt_image_0": "Attempting to boot image 0",
    "rse_bl2_decrypted": "BL2 image decrypted successfully",
    "rse_bl2_validated": "BL2 image validated successfully",
    "rse_jump_bl2": "Jumping to BL2",
    "rse_image_4_loaded": "Image 4 loaded from the primary slot",
    "rse_si_mbist": "BL2: SI MBIST happens here",
    "rse_image_3_loaded": "Image 3 loaded from the primary slot",
    "rse_image_2_loaded": "Image 2 loaded from the primary slot",
    "rse_image_0_loaded": "Image 0 loaded from the primary slot",
    "rse_first_image_slot": "Jumping to the first image slot",
    "rse_runtime_handoff": "Jumping to the first image slot",
    "rse_scp_power_on_ap": "RSE to SCP SCMI power on AP succeeded",
    "measured_boot_bl33": "BL_33",
    "tf_a_mboot_fw_config": "sw_type     : FW_CONFIG",
    "tf_a_mboot_secure_rt_el3": "sw_type     : SECURE_RT_EL3",
    "tf_a_mboot_hw_config": "sw_type     : HW_CONFIG",
    "tf_a_mboot_secure_rt_el1_spmd": "sw_type     : SECURE_RT_EL1_SPMD",
    "tf_a_mboot_bl33": "sw_type     : BL_33",
    "primary_efi_mm_partition": "EFI: MM partition ID 0x8006",
    "uboot_mm_partition": "EFI: MM partition ID 0x8006",
    "primary_pk_enrolled": "PK key is enrolled successfully!",
    "primary_kek_enrolled": "KEK key is enrolled successfully!",
    "primary_db_enrolled": "db key is enrolled successfully!",
    "primary_dbx_enrolled": "dbx key is enrolled successfully!",
    "primary_fwu_regular_state": "FWU: System booting in Regular State",
    "fwu_regular_state": "FWU: System booting in Regular State",
    "primary_bootflow_script": "** Booting bootflow",
    "primary_efi_bootaa64": "Booting /\\EFI\\BOOT\\BOOTAA64.EFI",
    "primary_linux_cpu": "Booting Linux on physical CPU",
    "primary_linux_version": "Linux version ",
    "primary_login_prompt": "fvp-rd-aspen login:",
    "primary_root_shell": "root@fvp-rd-aspen",
    "secure_smmgw_discovery_fallback": "Logging service discovery failed",
    "secure_seproxy_remove_missing": "secure_storage_ipc_remove",
    "ps_test_403": "TEST: 403",
    "ps_insufficient_space": "Insufficient space check",
    "ps_check_1_overload": "[Check 1] Overload storage space",
    "ps_uid_insufficient_space": "set failed due to insufficient space",
    "ps_remove_all_registered_uids": "Remove all registered UIDs",
    "ps_check_2_overload": "[Check 2] Overload storage again",
}

RSE_BOOT_PROFILE_MARKERS = [
    ("rse_bl1_1", "TF-M BL1_1 start"),
    ("rse_jump_bl1_2", "BL1_1 to BL1_2 handoff"),
    ("rse_bl1_2", "TF-M BL1_2 start"),
    ("rse_attempt_image_0", "BL1_2 image 0 selection"),
    ("rse_bl2_decrypted", "BL2 decrypt complete"),
    ("rse_bl2_validated", "BL2 validation complete"),
    ("rse_jump_bl2", "BL1_2 to BL2 handoff"),
    ("rse_image_4_loaded", "SI CL1 image loaded"),
    ("rse_image_3_loaded", "SI CL0 image loaded"),
    ("rse_image_2_loaded", "AP BL2 image loaded"),
    ("rse_image_0_loaded", "RSE runtime image loaded"),
    ("rse_scp_power_on_ap", "AP power-on SCMI complete"),
    ("rse_first_image_slot", "RSE runtime handoff"),
    ("measured_boot_bl33", "U-Boot measured boot marker"),
    ("primary_linux_cpu", "Linux CPU boot marker"),
    ("primary_login_prompt", "Linux login prompt"),
]

SERVICE_MODEL_GAPS = [
    "Safety Island CL0/SCP firmware is represented by a protocol-correct "
    "SystemC/TLM service model, not by a live SCP CPU.",
    "SCP-Firmware symbols are available for GDB source inspection, but the "
    "service-model path does not expose a live SCP CPU GDB target.",
    "The modeled SCMI/MHU behavior is limited to RD-Aspen boot, power-domain, "
    "system-power notification, and PFDI monitor transactions observed so far.",
]

PROBE_DONE_MARKER = "__QBOX_PROBE_DONE__"
SECURE_SERVICE_PROBE_DONE_MARKER = "__QBOX_SECURE_SERVICE_PROBE_DONE__"
FWU_PROBE_START_MARKER = "__QBOX_FWU_PROBE_START__"
FWU_REBOOT_REQUESTED_MARKER = "__QBOX_FWU_REBOOT_REQUESTED__"
LOGIN_READY_PATTERNS = [
    r"fvp-rd-aspen login:",
    r"Started .*Serial Getty on ttyAMA0",
    r"Reached target .*Login Prompts",
]
POST_LOGIN_PROBE_COMMANDS = [
    "echo __QBOX_PROBE_START__",
    "uname -a",
    "printf 'possible='; cat /sys/devices/system/cpu/possible",
    "printf 'present='; cat /sys/devices/system/cpu/present",
    "printf 'online='; cat /sys/devices/system/cpu/online",
    "printf 'cpuinfo_processors='; grep -c '^processor' /proc/cpuinfo",
    "printf 'cpu_directories='; ls -d /sys/devices/system/cpu/cpu[0-9]* 2>/dev/null | wc -l",
    "modprobe -v arm_si_rproc timeout=500; echo arm_si_rproc_modprobe_rc:$?",
    "for d in /sys/class/remoteproc/remoteproc*; do [ -f $d/name ] && echo remoteproc_state:$(cat $d/name):$(cat $d/state); done",
    "for d in /sys/class/remoteproc/remoteproc*; do [ -f $d/state ] && [ \"$(cat $d/state)\" = detached ] && echo attach > $d/state 2>/dev/null || true; done",
    "for d in /sys/class/remoteproc/remoteproc*; do [ -f $d/name ] && echo remoteproc_state_after:$(cat $d/name):$(cat $d/state); done",
    "if command -v od >/dev/null && [ -r /dev/mem ]; then dd if=/dev/mem of=/tmp/si-cl1-rsctbl.bin bs=4096 skip=256 count=1 2>/dev/null; echo si_cl1_rsctbl_dd_rc:$?; od -An -tx4 -N 128 /tmp/si-cl1-rsctbl.bin 2>/dev/null | sed 's/^/si_cl1_rsctbl_word:/'; echo si_cl1_rsctbl_od_rc:$?; else echo si_cl1_rsctbl_dd_rc:127; fi",
    "modprobe -v rpmsg_ns; echo rpmsg_ns_modprobe_rc:$?",
    "modprobe -v virtio_rpmsg_bus; echo virtio_rpmsg_bus_modprobe_rc:$?",
    "modprobe -v rpmsg_net; echo rpmsg_net_modprobe_rc:$?",
    "for i in $(seq 1 100); do ls /sys/bus/rpmsg/devices/virtio*.ethsi1.* >/dev/null 2>&1 && break; sleep 0.1; done",
    "for i in $(seq 1 100); do ip link show ethsi1 >/dev/null 2>&1 && break; sleep 0.1; done",
    "ls -l /sys/bus/virtio/devices || true",
    "ls -l /sys/bus/rpmsg/devices || true",
    "for d in /sys/bus/rpmsg/devices/*; do [ -e $d/name ] && echo rpmsg_device:$(basename $d):$(cat $d/name); done",
    "for d in /sys/bus/event_source/devices/arm_dsu* /sys/bus/event_source/devices/dsu*; do [ -d $d ] && echo dsu_pmu_event_source:$(basename $d); done",
    "dsu_pmu_found=0; for d in /sys/bus/event_source/devices/arm_dsu* /sys/bus/event_source/devices/dsu*; do [ -d \"$d\" ] && dsu_pmu_found=1; done; if [ \"$dsu_pmu_found\" -eq 1 ]; then echo dsu_pmu_event_source_rc:0; else echo dsu_pmu_event_source_rc:1; fi",
    "ip link show ethsi1; echo ethsi1_iplink_rc:$?",
    "ip link show || true",
    "dmesg | grep -Ei 'gic|its|pl011|ttyAMA|watchdog|rtc|virtio|rng|eth|scmi|mhu|smmu|remoteproc|rpmsg|pfdi|hipc|ras|pmu|dsu|timer' || true",
    "cat /proc/interrupts | grep -Ei 'uart-pl011|virtio|rtc-pl031|arch_timer|GIC|ITS|gwdt|smmu|ras|estatus|mhu|scmi|remoteproc' || true",
    "lsmod | grep -Ei 'virtio|rng|pfdi|hipc|rpmsg|remoteproc|scmi|mhu|smmu' || true",
    "modprobe -v openvswitch; echo openvswitch_modprobe_rc:$?",
    "modprobe -v pfdi_misc; echo pfdi_misc_modprobe_rc:$?",
    "pfdi-cli --info; echo pfdi_info_rc:$?",
    "pfdi-cli --pfdi_info 0; echo pfdi_firmware_info_rc:$?",
    "pfdi-cli --count 0; echo pfdi_count_rc:$?",
    "pfdi-cli --result 0; echo pfdi_cpu0_result_rc:$?",
    "pfdi-cli --result 1; echo pfdi_cpu1_result_rc:$?",
    "pfdi-cli --result 2; echo pfdi_cpu2_result_rc:$?",
    "pfdi-cli --result 3; echo pfdi_cpu3_result_rc:$?",
    "systemctl is-system-running || true",
    "systemctl --failed --no-pager || true",
    "echo failed_units_count:$(systemctl --failed --no-legend --plain 2>/dev/null | wc -l)",
    f"echo {PROBE_DONE_MARKER}",
]

SECURE_SERVICE_PROBE_BINARIES = [
    "uefi-test",
    "psa-iat-api-test",
    "psa-its-api-test",
    "psa-ps-api-test",
    "ts-service-test",
]
SECURE_SERVICE_DIAG_DONE_MARKER = "__QBOX_SECURE_SERVICE_DIAG_DONE__"
SECURE_SERVICE_TEST_COMMANDS = {
    "ts": ("ts-service-test -lg", "secure_ts_service_test_lg_rc"),
    "iat": ("psa-iat-api-test", "secure_psa_iat_api_test_rc"),
    "its": ("psa-its-api-test", "secure_psa_its_api_test_rc"),
    "ps": ("psa-ps-api-test", "secure_psa_ps_api_test_rc"),
    "uefi": ("uefi-test", "secure_uefi_test_rc"),
}
SECURE_SERVICE_TEST_BINARIES = {
    name: command.split()[0]
    for name, (command, _rc_name) in SECURE_SERVICE_TEST_COMMANDS.items()
}
DEFAULT_SECURE_SERVICE_TESTS = ["ts", "iat", "its", "ps", "uefi"]


def fwu_probe_commands(system_running_timeout_s: int) -> list[str]:
    system_running_timeout_s = max(1, system_running_timeout_s)
    return [
        f"echo {FWU_PROBE_START_MARKER}",
        f"timeout {system_running_timeout_s}s systemctl is-system-running --wait; "
        "echo fwu_system_running_rc:$?",
        "lsblk -no NAME /dev/vda1; echo fwu_lsblk_vda1_rc:$?",
        "lsblk -no NAME /dev/vdb1; echo fwu_lsblk_vdb1_rc:$?",
        "mkdir -p /boot /mnt; echo fwu_mkdir_mountpoints_rc:$?",
        "findmnt /boot >/dev/null 2>&1 || mount /dev/vda1 /boot; "
        "echo fwu_mount_boot_rc:$?",
        "findmnt /mnt >/dev/null 2>&1 || mount /dev/vdb1 /mnt; "
        "echo fwu_mount_capsule_rc:$?",
        "findmnt -T /boot -o TARGET,SOURCE -n || true",
        "findmnt -T /mnt -o TARGET,SOURCE -n || true",
        "test -f /mnt/fw.cap; echo fwu_capsule_present_rc:$?",
        "mkdir -p /boot/EFI/UpdateCapsule; echo fwu_mkdir_capsule_rc:$?",
        "cp -rf /mnt/fw.cap /boot/EFI/UpdateCapsule/; echo fwu_copy_capsule_rc:$?",
        "test -f /boot/EFI/UpdateCapsule/fw.cap; echo fwu_capsule_copy_rc:$?",
        "sync",
        f"echo {FWU_REBOOT_REQUESTED_MARKER}",
        "reboot",
    ]

POST_LOGIN_DRIVER_PATTERNS = {
    "arm_si_rproc": [
        r"arm_si_rproc_modprobe_rc:0|arm-si-rproc|si-rproc",
        r"remoteproc_state(_after)?:si-cl1:(attached|running)|remoteproc remoteproc0: remote processor si-cl1 is now attached",
    ],
    "rpmsg": [
        r"virtio_rpmsg_bus_modprobe_rc:0|virtio_rpmsg_bus|virtio_rpmsg_bus .*rpmsg host is online",
        r"rpmsg_net_modprobe_rc:0|rpmsg_net",
    ],
    "hipc_ethsi1": [
        r"ethsi1_iplink_rc:0|\bethsi1:",
        r"rpmsg_device:.*ethsi1|virtio_rpmsg_bus .*ethsi1",
    ],
    "virtio": [
        r"virtio_blk|virtio_net|virtio_rng|/sys/bus/virtio/devices",
    ],
    "pl011_uart": [
        r"ttyAMA0|1a400000\.serial|uart-pl011",
    ],
    "smmu_v3": [
        r"arm-smmu-v3|1c0000000\.iommu|iommu@1c0000000",
    ],
    "dsu_pmu": [
        r"dsu_pmu_event_source_rc:0|probe of dsu-pmu-0 returned 0|arm_dsu_0",
        r"dsu_pmu_event_source:.*(arm_dsu|dsu)|dsu-pmu-0|arm_dsu_0",
    ],
    "pfdi_4cpu": [
        r"pfdi_misc_modprobe_rc:0",
        r"pfdi_info_rc:0",
        r"libPFDI version:\s*1\.0",
        r"pfdi_firmware_info_rc:0",
        r"pfdi_count_rc:0",
        r"pfdi_cpu0_result_rc:0",
        r"CPU0: Out of Reset \(OoR\) test OK",
        r"pfdi_cpu1_result_rc:0",
        r"CPU1: Out of Reset \(OoR\) test OK",
        r"pfdi_cpu2_result_rc:0",
        r"CPU2: Out of Reset \(OoR\) test OK",
        r"pfdi_cpu3_result_rc:0",
        r"CPU3: Out of Reset \(OoR\) test OK",
    ],
}

SECURE_SERVICE_FAILURE_PATTERNS = {
    "se_proxy_error": r"E/SEPROXY|SP panicked",
    "smm_gateway_error": r"E/SMMGW|SP is busy|Failed to read PK",
    "uefi_variable_error": r"Failed to set EFI variable|Can't populate EFI variables",
}

ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\a]*(?:\a|\x1b\\)")
TRACE_RESET_RE = re.compile(
    r"Loaded reset SP (0x[0-9a-fA-F]+) PC (0x[0-9a-fA-F]+) from vector table"
)
TRACE_EXCEPTION_RE = re.compile(r"Taking exception \d+ \[([^\]]+)\] on CPU (\d+)")
TRACE_FAULT_ADDR_RE = re.compile(r"\.\.\.at fault address (0x[0-9a-fA-F]+)")
TRACE_PMSA_RE = re.compile(
    r"PMSA MPU lookup for (\w+) at (0x[0-9a-fA-F]+)"
)
ATU_TRANSLATION_ERROR_RE = re.compile(
    r"(?P<component>\S+) (?P<access>dbg_)?translate_(?P<command>read|write) "
    r"logical=(?P<logical>0x[0-9a-fA-F]+) "
    r"physical=(?P<physical>0x[0-9a-fA-F]+) "
    r"len=(?P<length>0x[0-9a-fA-F]+) status=error"
)
PC_TRACE_RE = re.compile(
    r"(?:(?P<component>\S+)\s+)?pc_trace sample=(?P<sample>\d+) seen=(?P<seen>\d+) "
    r"sc_time=(?P<sc_time>.*?) vclock_ns=(?P<vclock_ns>\d+) "
    r"pc=(?P<pc>0x[0-9a-fA-F]+) mem_io_pc=(?P<mem_io_pc>0x[0-9a-fA-F]+)"
    r"(?P<extra>.*)$"
)
TRACE_KV_RE = re.compile(r"(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>0x[0-9a-fA-F]+|-?\d+)")
QEMU_IN_ASM_ADDR_RE = re.compile(r"^\s*(0x[0-9a-fA-F]+):")
MAP_TEXT_SECTION_RE = re.compile(r"^\s*\.text\.(?P<symbol>[A-Za-z0-9_.$]+)\s*$")
MAP_SECTION_RANGE_RE = re.compile(
    r"^\s*(?P<start>0x[0-9a-fA-F]+)\s+(?P<size>0x[0-9a-fA-F]+)\s+"
)
FAIL_PATTERNS = [
    "Kernel panic",
    "Unable to mount root fs",
    "No working init found",
    "[ERR]",
    "[ERROR]",
]
KNOWN_RUNTIME_BLOCKERS = [
    (
        "BL2 image signature failed to validate",
        "bl1_2_bl2_signature_validation_failed",
    ),
    ("Signature validation failed", "bl1_2_signature_validation_failed"),
    ("BL2 image failed to decrypt", "bl1_2_bl2_decrypt_failed"),
]
ARMV7M_EXCEPTIONS = {
    0: "Thread",
    1: "Reset",
    2: "NMI",
    3: "HardFault",
    4: "MemManage",
    5: "BusFault",
    6: "UsageFault",
    7: "SecureFault",
    11: "SVCall",
    12: "DebugMonitor",
    14: "PendSV",
    15: "SysTick",
}

BOOT_ENC_TRACE_SYMBOLS = [
    "bootutil_aes_kw_unwrap",
    "boot_decrypt_key",
    "boot_enc_load",
    "boot_enc_set_key",
    "boot_enc_decrypt",
]
RSE_BL2_CFI_TRACE_SYMBOLS = [
    "cfi_strataflashj3_read",
    "cfi_strataflashj3_program",
    "cfi_strataflashj3_program_data_byte",
    "cfi_strataflashj3_erase",
    "erase_block",
    "nor_cfi_reg_read",
    "nor_byte_program",
    "nor_poll_dws_byte",
]
RSE_BL1_1_TRACE_SYMBOLS = [
    "cfi_strataflashj3_read",
    "nor_cfi_reg_read",
    "cc3xx_lowlevel_hash_uninit",
    "cc3xx_lowlevel_hash_init",
    "cc3xx_lowlevel_hash_update",
    "cc3xx_lowlevel_hash_get_state",
    "cc3xx_lowlevel_hash_set_state",
    "cc3xx_lowlevel_hash_finish",
    "cc3xx_lowlevel_dma_buffered_input_data",
    "cc3xx_lowlevel_dma_flush_buffer",
    "cc3xx_lowlevel_set_engine",
    "kmu_random_delay",
]

RSE_FWU_PRIVATE_METADATA_OFFSET = 0x5000
RSE_FWU_PRIVATE_METADATA_SIZE = 68
RSE_FWU_COMPONENT_NUMBER = 5
RSE_FWU_BOOT_INDEX_SLOT0 = 0
RSE_FWU_VALID_BOOT_INDICES = {0, 1}
RSE_FWU_VALID_STATES = set(range(9))
RSE_BOOT_FLASH_BASE_S = 0xB0000000
RSE_BOOT_FLASH_SIZE = 0x04000000
AP_BOOT_FLASH_IMAGE_SIZE = 0x08000000
FLASH_ERASED_VALUE = 0xFF
HOST_SI_CL0_SRAM_WINDOW_SIZE = 0x01000000
HOST_SI_CL0_IMG_HDR_LOGICAL_BASE = 0x70083C00
HOST_SI_CL0_IMG_CODE_LOGICAL_BASE = 0x70084000
HOST_SI_CL0_HEADER_FILE_OFFSET = 0x000FFC00
HOST_SI_CL0_CODE_FILE_OFFSET = 0x00000000
HOST_SI_CL0_SAMPLE_SIZE = 0x400
HOST_SI_CL1_SRAM_WINDOW_SIZE = 0x01000000
HOST_SI_CL1_IMG_HDR_LOGICAL_BASE = 0x70185C00
HOST_SI_CL1_IMG_CODE_LOGICAL_BASE = 0x70186000
HOST_SI_CL1_HEADER_FILE_OFFSET = 0x000FFC00
HOST_SI_CL1_CODE_FILE_OFFSET = 0x00000000
HOST_SI_CL1_SAMPLE_SIZE = 0x400
HOST_SI_IMG_HEADER_ALIAS_SIZE = 0x400
HOST_SI_IMG_CODE_ALIAS_SIZE_FALLBACK = 0x00100000
HOST_AP_SHARED_SRAM_SIZE = 0x00100000
HOST_AP_BL2_IMG_HDR_LOGICAL_BASE = 0x70001C00
HOST_AP_BL2_IMG_CODE_LOGICAL_BASE = 0x70002000
HOST_AP_BL2_HEADER_FILE_OFFSET = 0x00001C00
HOST_AP_BL2_CODE_FILE_OFFSET = 0x00082000
HOST_AP_BL2_IMG_HEADER_ALIAS_SIZE = 0x400
HOST_AP_BL2_IMG_CODE_ALIAS_SIZE_FALLBACK = 0x00080000
HOST_AP_BL2_HEADER_SRAM_SIZE = 0x00080000
HOST_AP_BL2_HEADER_RSC_TABLE_OFFSET = 0x00000000
HOST_AP_BL2_HEADER_VRING0_OFFSET = 0x00020000
HOST_AP_BL2_HEADER_VRING1_OFFSET = 0x00040000
HOST_AP_BL2_HEADER_VDEV0BUFFER_OFFSET = 0x00060000
HOST_AP_BL2_HEADER_SAMPLE_SIZE = 0x80
EXTRA_VIRTIO_BLK_SIZE = 0
SI_CL0_PRIMARY_FLASH_OFFSET = 0x00067000
SI_CL0_SECONDARY_FLASH_OFFSET = 0x002C7000
SI_CL1_PRIMARY_FLASH_OFFSET = 0x00167000
SI_CL1_SECONDARY_FLASH_OFFSET = 0x003C7000
RSE_SECURE_PRIMARY_FLASH_OFFSET = 0x00027000
RSE_SECURE_SECONDARY_FLASH_OFFSET = 0x00287000
RSE_BOOT_FLASH_PRE_PRIMARY_SCAN_OFFSET = 0x00007000
RSE_BOOT_FLASH_PRE_PRIMARY_SCAN_SIZE = (
    RSE_SECURE_PRIMARY_FLASH_OFFSET - RSE_BOOT_FLASH_PRE_PRIMARY_SCAN_OFFSET
)
RSE_FLASH_IMG_SIZE = 0x03000000
RSE_FLASH_PS_SIZE = 0x00100000
RSE_FLASH_ITS_SIZE = 0x00040000
RSE_BOOT_FLASH_STORAGE_OFFSET = RSE_FLASH_IMG_SIZE
RSE_BOOT_FLASH_STORAGE_SIZE = RSE_FLASH_PS_SIZE + RSE_FLASH_ITS_SIZE
RSE_STORAGE_METADATA_FORMAT_VERSION = 2
RSE_STORAGE_SCHEMA_ID = "apollo-qvp-cfg2-tfm-ps-its-v1"
RSE_FLASH_STATE_STATUS_FILE = "rse-flash-state.json"
RSE_BOOT_FLASH_IMAGE_SLOT_OFFSETS = [
    RSE_SECURE_PRIMARY_FLASH_OFFSET,
    SI_CL0_PRIMARY_FLASH_OFFSET,
    SI_CL1_PRIMARY_FLASH_OFFSET,
    RSE_SECURE_SECONDARY_FLASH_OFFSET,
    SI_CL0_SECONDARY_FLASH_OFFSET,
    SI_CL1_SECONDARY_FLASH_OFFSET,
]
HOST_AP_FLASH_LOGICAL_BASE = 0x703A6000
AP_FLASH_FIP_PRIMARY_OFFSET = 0x00007000
AP_FLASH_FIP_SECONDARY_OFFSET = 0x00247000
AP_FLASH_FIP_SIZE = 0x00240000
RSE_BL2_SYMBOL_DEFAULTS = {
    "boot_go_for_image_id": 0x3101E288,
    "boot_load_image_to_sram": 0x3101E758,
    "boot_enc_load": 0x3101EEB6,
    "boot_enc_set_key": 0x3101EF52,
    "boot_enc_decrypt": 0x3101EF8C,
    "bootutil_img_validate": 0x3101F010,
    "bootutil_img_hash": 0x3101F3AA,
    "bootutil_verify_sig": 0x3101F5BC,
    "bootutil_keys": 0x31000454,
    "bootutil_key_cnt": 0x3102BBD0,
    "FIH_SUCCESS": 0x310027DC,
    "delay_cycles": 0x31021AC8,
    "memcpy": 0x3101D176,
    "memset": 0x3101D136,
}
RSE_BL2_LIBC_HOTPATH_SYMBOLS = {
    "rse_hotpath_memcpy_addr": "memcpy",
    "rse_hotpath_memset_addr": "memset",
}
RSE_BL1_2_SYMBOL_DEFAULTS = {
    "pq_crypto_verify": RSE_LMS_VERIFY_DEFAULT,
}
RSE_BL2_HOOK_SYMBOLS = {
    "rse_bl2_boot_go_for_image_id_addr": "boot_go_for_image_id",
    "rse_bl2_boot_load_image_to_sram_addr": "boot_load_image_to_sram",
    "rse_bl2_boot_enc_load_addr": "boot_enc_load",
    "rse_bl2_boot_enc_set_key_addr": "boot_enc_set_key",
    "rse_bl2_boot_enc_decrypt_addr": "boot_enc_decrypt",
    "rse_bl2_bootutil_img_validate_addr": "bootutil_img_validate",
    "rse_bl2_bootutil_img_hash_addr": "bootutil_img_hash",
    "rse_bl2_bootutil_verify_sig_addr": "bootutil_verify_sig",
    "rse_bl2_bootutil_keys_addr": "bootutil_keys",
    "rse_bl2_bootutil_key_cnt_addr": "bootutil_key_cnt",
    "rse_bl2_fih_success_addr": "FIH_SUCCESS",
    "rse_bl2_delay_cycles_addr": "delay_cycles",
}
RSE_BL2_BOOT_STATE_LAYOUT_DEFAULTS = {
    "image_count": 5,
    "curr_img_offset": 0x10C8,
    "imgs_offset": 0x0,
    "image_stride": 88,
    "slot_stride": 44,
    "slot_usage_offset": 0x10D0,
    "slot_usage_stride": 16,
    "slot_usage_img_dst_offset": 8,
    "slot_usage_img_sz_offset": 12,
}
IMAGE_MAGIC = 0x96F3B83D
IMAGE_TLV_INFO_MAGIC = 0x6907
IMAGE_TLV_PROT_INFO_MAGIC = 0x6908
IMAGE_F_ENCRYPTED_AES128 = 0x00000004
IMAGE_F_ENCRYPTED_AES256 = 0x00000008
IMAGE_F_RAM_LOAD = 0x00000020
IMAGE_TLV_ENC_KW = 0x31
EXPECTED_ENC_KW_LEN_AES128 = 0x18


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def qbox_build_dir(root: Path) -> Path:
    default_dir = root / "build/local-apollo-fvp/work/qbox-platform"
    return Path(
        os.environ.get(
            "QBOX_PLATFORM_BUILD_DIR",
            os.environ.get("QBOX_BUILD_DIR", str(default_dir)),
        )
    ).resolve()


def qbox_core_dir(root: Path) -> Path:
    return Path(os.environ.get("QBOX_CORE_DIR", str(root / "hsoc-stack/tools/qbox"))).resolve()


def qbox_platform_dir(root: Path) -> Path:
    return Path(
        os.environ.get("QBOX_PLATFORM_DIR", str(root / "hsoc-stack/tools/qbox-platform"))
    ).resolve()


def installed_libqemu_library_paths(build_dir: Path) -> list[Path]:
    paths: list[Path] = []

    installed_libqemu_dir = build_dir.parent / "lib/libqemu"
    if installed_libqemu_dir.is_dir():
        paths.append(installed_libqemu_dir)

    for parent in build_dir.parents:
        if parent.parent.name != "sysroots-components":
            continue
        component_lib_dir = parent / "qbox-libqemu-native/usr/lib"
        if component_lib_dir.is_dir() and component_lib_dir not in paths:
            paths.append(component_lib_dir)
        break

    cache = build_dir / "CMakeCache.txt"
    try:
        lines = cache.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return paths

    for line in lines:
        if not line.startswith("libqemu_DIR:") or "=" not in line:
            continue
        cmake_dir = Path(line.split("=", 1)[1]).expanduser()
        lib_dir = cmake_dir.parent.parent
        if lib_dir.is_dir() and lib_dir not in paths:
            paths.append(lib_dir)
        for parent in lib_dir.parents:
            if parent.name != "sysroots-components":
                continue
            dependency_glob = (
                "work/x86_64-linux/qbox-libqemu-native/*/"
                "recipe-sysroot-native/usr/lib"
            )
            for dependency_dir in sorted(parent.parent.glob(dependency_glob)):
                if dependency_dir.is_dir() and dependency_dir not in paths:
                    paths.append(dependency_dir)
            break
    return paths


def installed_provider_library_paths(build_dir: Path) -> list[Path]:
    if build_dir.name != "bin":
        return []

    provider_root = build_dir.parent.parent
    components_arch_dir = provider_root.parent
    sysroots_components_dir = components_arch_dir.parent
    if sysroots_components_dir.name != "sysroots-components":
        return []

    paths: list[Path] = []
    provider_lib_dir = build_dir.parent / "lib"
    for path in (provider_lib_dir, provider_lib_dir / "qbox/modules"):
        if path.is_dir():
            paths.append(path)

    recipe_lib_glob = (
        f"work/*/{provider_root.name}/*/recipe-sysroot-native/usr/lib"
    )
    for path in sorted(sysroots_components_dir.parent.glob(recipe_lib_glob)):
        if path.is_dir() and path not in paths:
            paths.append(path)
    return paths


def timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    print("+ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def cmake_cache_values(cache: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not cache.exists():
        return values

    for line in cache.read_text(errors="replace").splitlines():
        if not line or line.startswith(("#", "//")) or "=" not in line:
            continue
        key_type, value = line.split("=", 1)
        key = key_type.split(":", 1)[0]
        values[key] = value
    return values


def qbox_sdk_native_sysroot(root: Path, build_dir: Path) -> Path | None:
    candidates: list[Path] = []
    for name in ("QBOX_NATIVE_SDK_SYSROOT", "SDK_NATIVE_SYSROOT"):
        value = os.environ.get(name)
        if value:
            candidates.append(Path(value).expanduser())

    local_build_dir = build_dir.parent.parent
    if local_build_dir.name.startswith("local-"):
        sdk_name = "local-sdk-" + local_build_dir.name.removeprefix("local-")
        candidates.extend(
            sorted((local_build_dir.parent / sdk_name / "sysroots").glob(
                "*-pokysdk-linux"
            ))
        )
    candidates.extend(
        path
        for sdk_dir in sorted((root / "build").glob("local-sdk-*"))
        for path in sorted((sdk_dir / "sysroots").glob("*-pokysdk-linux"))
    )

    for candidate in candidates:
        native_bin = candidate / "usr/bin"
        if all((native_bin / tool).is_file() for tool in ("python3", "meson", "meson.real")):
            return candidate.resolve()
    return None


def qbox_sdk_native_build_env(
    root: Path, build_dir: Path
) -> tuple[dict[str, str], list[str]]:
    env = os.environ.copy()
    native_sysroot = qbox_sdk_native_sysroot(root, build_dir)
    if native_sysroot is None:
        return env, []

    native_bin = native_sysroot / "usr/bin"
    tool_shim = build_dir / ".qbox-sdk-native-tools"
    tool_shim.mkdir(parents=True, exist_ok=True)
    tools = {
        "python3": native_bin / "python3",
        "nativepython3": native_bin / "python3",
        "meson": native_bin / "meson",
        "meson.real": native_bin / "meson.real",
    }
    for name, target in tools.items():
        link = tool_shim / name
        if link.is_symlink() and link.resolve() == target.resolve():
            continue
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(target)

    for name in (
        "OECORE_NATIVE_SYSROOT",
        "OECORE_TARGET_SYSROOT",
        "SDKTARGETSYSROOT",
        "SDKPATH",
        "CONFIG_SITE",
        "PKG_CONFIG_SYSROOT_DIR",
        "PKG_CONFIG_PATH",
        "PKG_CONFIG_LIBDIR",
        "OECORE_ACLOCAL_OPTS",
        "TARGET_PREFIX",
        "CONFIGURE_FLAGS",
        "CC",
        "CXX",
        "CPP",
        "LD",
        "AR",
        "AS",
        "STRIP",
        "OBJCOPY",
        "OBJDUMP",
        "READELF",
        "NM",
        "RANLIB",
        "CFLAGS",
        "CXXFLAGS",
        "CPPFLAGS",
        "LDFLAGS",
        "KCFLAGS",
    ):
        env.pop(name, None)
    env["PATH"] = os.pathsep.join((str(tool_shim), env.get("PATH", "")))
    env["PYTHONNOUSERSITE"] = "1"
    return env, [f"-DLIBQEMU_PYTHON={native_bin / 'python3'}"]


def ensure_qbox_targets(root: Path, jobs: int) -> None:
    core_dir = qbox_core_dir(root)
    platform_dir = qbox_platform_dir(root)
    build_dir = qbox_build_dir(root)
    cache = build_dir / "CMakeCache.txt"
    local_qemu = (root / "hsoc-stack/tools/qemu").resolve()
    libqemu_git = os.environ.get("QBOX_LIBQEMU_GIT", f"file://{local_qemu}")
    libqemu_source = os.environ.get(
        "QBOX_FETCHCONTENT_SOURCE_DIR_LIBQEMU", str(local_qemu)
    )
    libqemu_build_always = os.environ.get("QBOX_LIBQEMU_BUILD_ALWAYS", "ON")
    apollo_build_target = os.environ.get(
        "QBOX_APOLLO_BUILD_TARGET", "apollo_fvp_full_system"
    )
    install_prefix = str((build_dir / "install").resolve())
    build_env, sdk_cmake_args = qbox_sdk_native_build_env(root, build_dir)

    configure_cmd = [
        "cmake",
        "-S",
        str(platform_dir),
        "-B",
        str(build_dir),
    ]
    expected_cache = {
        "QBOX_CORE_SOURCE_DIR": str(core_dir),
        "QBOX_QEMU_SOURCE_DIR": str(local_qemu),
        "CMAKE_INSTALL_PREFIX": install_prefix,
        "LIBQEMU_GIT": libqemu_git,
        "FETCHCONTENT_SOURCE_DIR_LIBQEMU": libqemu_source,
        "LIBQEMU_BUILD_ALWAYS": libqemu_build_always,
        "QBOX_USE_SYSTEM_LIBQEMU": "OFF",
        "QBOX_APOLLO_BUILD_TARGET": apollo_build_target,
    }
    for argument in sdk_cmake_args:
        key, value = argument.removeprefix("-D").split("=", 1)
        expected_cache[key] = value
    for key, value in expected_cache.items():
        if value:
            configure_cmd.append(f"-D{key}={value}")

    cache_values = cmake_cache_values(cache)
    needs_configure = not cache.exists()
    for key, value in expected_cache.items():
        if value and cache_values.get(key) != value:
            needs_configure = True
            break
    if needs_configure:
        run(configure_cmd, cwd=root, env=build_env)

    build_targets = [apollo_build_target] if apollo_build_target else REQUIRED_TARGETS
    cmd = [
        "cmake",
        "--build",
        str(build_dir),
        "--target",
        *build_targets,
        "--parallel",
        str(jobs),
    ]
    run(cmd, cwd=root, env=build_env)


def copy_if_requested(src: Path, dst_dir: Path, *, copy: bool) -> Path:
    if not copy:
        return src
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    shutil.copy2(src, dst)
    return dst


def copy_sparse(src: Path, dst: Path, *, chunk_size: int = 1024 * 1024) -> None:
    """Copy sparse image data without expanding zero-filled holes."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    with src.open("rb") as source, dst.open("wb") as target:
        while True:
            data = source.read(chunk_size)
            if not data:
                break
            if data == b"\0" * len(data):
                target.seek(len(data), os.SEEK_CUR)
            else:
                target.write(data)
        target.truncate(src.stat().st_size)
    shutil.copystat(src, dst, follow_symlinks=True)


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_file_region(
    path: Path,
    *,
    offset: int,
    size: int,
    chunk_size: int = 1024 * 1024,
) -> str:
    digest = hashlib.sha256()
    remaining = size
    with path.open("rb") as source:
        source.seek(offset)
        while remaining:
            data = source.read(min(chunk_size, remaining))
            if not data:
                raise RuntimeError(
                    f"rse_flash_state_storage_truncated:{path}:{offset}:{size}"
                )
            digest.update(data)
            remaining -= len(data)
    return digest.hexdigest()


def finalize_rse_flash_state_status(
    status: dict[str, object],
) -> dict[str, object]:
    if not status.get("enabled"):
        return status

    state = Path(str(status["path"]))
    regions = status.get("storage_regions")
    if not isinstance(regions, dict):
        return status
    for value in regions.values():
        if not isinstance(value, dict):
            continue
        try:
            after_hash = sha256_file_region(
                state,
                offset=int(value["offset"]),
                size=int(value["size"]),
            )
        except (OSError, RuntimeError, KeyError, TypeError, ValueError) as exc:
            value["after_sha256"] = None
            value["hash_error"] = str(exc)
            continue
        value["after_sha256"] = after_hash
        value["changed"] = after_hash != value.get("before_sha256")
    return status


def rse_storage_compatibility(rse_otp: Path) -> dict[str, object]:
    descriptor: dict[str, object] = {
        "schema_id": RSE_STORAGE_SCHEMA_ID,
        "image_size": RSE_FLASH_IMG_SIZE,
        "ps_offset": RSE_FLASH_IMG_SIZE,
        "ps_size": RSE_FLASH_PS_SIZE,
        "its_offset": RSE_FLASH_IMG_SIZE + RSE_FLASH_PS_SIZE,
        "its_size": RSE_FLASH_ITS_SIZE,
        "otp_sha256": sha256_file(rse_otp),
    }
    encoded = json.dumps(
        descriptor,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {
        **descriptor,
        "fingerprint": hashlib.sha256(encoded).hexdigest(),
    }


def copy_file_region(
    source: Path,
    destination: Path,
    *,
    offset: int,
    size: int,
    chunk_size: int = 1024 * 1024,
) -> None:
    remaining = size
    with source.open("rb") as source_file, destination.open("r+b") as destination_file:
        source_file.seek(offset)
        destination_file.seek(offset)
        while remaining:
            data = source_file.read(min(chunk_size, remaining))
            if not data:
                raise RuntimeError(
                    f"rse_flash_state_storage_truncated:{source}:{offset}:{size}"
                )
            destination_file.write(data)
            remaining -= len(data)


def write_json_atomic(path: Path, value: dict[str, object]) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temporary.write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def prepare_persistent_rse_flash(
    source: Path,
    state: Path,
    *,
    reset: bool,
    minimum_size: int,
    storage_compatibility: dict[str, object],
) -> tuple[Path, dict[str, object], object]:
    source = source.resolve()
    state = state.resolve()
    if source == state:
        raise RuntimeError(f"rse_flash_state_matches_source:{state}")

    state.parent.mkdir(parents=True, exist_ok=True)
    metadata_path = state.with_name(state.name + ".source.json")
    lock_path = state.with_name(state.name + ".lock")
    lock = lock_path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        lock.close()
        raise RuntimeError(f"rse_flash_state_in_use:{state}") from exc

    source_size = source.stat().st_size
    source_hash = sha256_file(source)
    storage_end = RSE_BOOT_FLASH_STORAGE_OFFSET + RSE_BOOT_FLASH_STORAGE_SIZE
    if minimum_size < storage_end:
        lock.close()
        raise RuntimeError(
            f"rse_flash_state_storage_out_of_range:{minimum_size}:{storage_end}"
        )
    expected_fingerprint = storage_compatibility["fingerprint"]
    metadata: dict[str, object] = {}
    if metadata_path.exists():
        try:
            candidate = json.loads(metadata_path.read_text(encoding="utf-8"))
            if isinstance(candidate, dict):
                metadata = candidate
        except (OSError, json.JSONDecodeError):
            metadata = {}

    state_valid = bool(
        state.exists()
        and state.stat().st_size >= max(minimum_size, storage_end)
        and metadata.get("format_version") == RSE_STORAGE_METADATA_FORMAT_VERSION
        and metadata.get("storage_fingerprint") == expected_fingerprint
    )
    source_matches = bool(
        state_valid
        and metadata.get("source_sha256") == source_hash
        and metadata.get("source_size") == source_size
    )
    if reset:
        action = "reset"
    elif source_matches:
        action = "reused"
    elif state_valid:
        action = "storage-preserved"
    elif state.exists() or metadata_path.exists():
        action = "refreshed"
    else:
        action = "created"

    if action != "reused":
        temporary = state.with_name(f".{state.name}.tmp-{os.getpid()}")
        try:
            copy_sparse(source, temporary)
            pad_flash_image(temporary, minimum_size)
            if action == "storage-preserved":
                copy_file_region(
                    state,
                    temporary,
                    offset=RSE_BOOT_FLASH_STORAGE_OFFSET,
                    size=RSE_BOOT_FLASH_STORAGE_SIZE,
                )
            os.replace(temporary, state)
        finally:
            temporary.unlink(missing_ok=True)
        metadata = {
            "format_version": RSE_STORAGE_METADATA_FORMAT_VERSION,
            "source_sha256": source_hash,
            "source_size": source_size,
            "source_path": str(source),
            "state_size": state.stat().st_size,
            "storage_fingerprint": expected_fingerprint,
            "storage_compatibility": storage_compatibility,
        }
        write_json_atomic(metadata_path, metadata)

    status: dict[str, object] = {
        "enabled": True,
        "action": action,
        "path": str(state),
        "metadata_path": str(metadata_path),
        "lock_path": str(lock_path),
        "source_path": str(source),
        "source_sha256": source_hash,
        "source_size": source_size,
        "state_size": state.stat().st_size,
        "storage_preserved": action in {"reused", "storage-preserved"},
        "storage_offset": RSE_BOOT_FLASH_STORAGE_OFFSET,
        "storage_size": RSE_BOOT_FLASH_STORAGE_SIZE,
        "storage_compatibility": storage_compatibility,
        "storage_regions": {
            "ps": {
                "offset": RSE_FLASH_IMG_SIZE,
                "size": RSE_FLASH_PS_SIZE,
                "before_sha256": sha256_file_region(
                    state,
                    offset=RSE_FLASH_IMG_SIZE,
                    size=RSE_FLASH_PS_SIZE,
                ),
            },
            "its": {
                "offset": RSE_FLASH_IMG_SIZE + RSE_FLASH_PS_SIZE,
                "size": RSE_FLASH_ITS_SIZE,
                "before_sha256": sha256_file_region(
                    state,
                    offset=RSE_FLASH_IMG_SIZE + RSE_FLASH_PS_SIZE,
                    size=RSE_FLASH_ITS_SIZE,
                ),
            },
        },
    }
    return state, status, lock


def mtools_image_arg(image: Path) -> str:
    return f"{image}@@{WIC_BOOT_PARTITION_OFFSET}"


def ensure_mtools() -> None:
    missing = [tool for tool in ["mtype", "mcopy"] if shutil.which(tool) is None]
    if missing:
        raise RuntimeError("missing_mtools:" + ",".join(missing))


def read_boot_entry(image: Path) -> str:
    ensure_mtools()
    result = subprocess.run(
        ["mtype", "-i", mtools_image_arg(image), WIC_BOOT_ENTRY],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("mtype_boot_entry_failed:" + result.stderr.strip())
    return result.stdout


def write_boot_entry(image: Path, text: str, tmp_dir: Path) -> None:
    ensure_mtools()
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp = tmp_dir / "boot.conf"
    tmp.write_text(text, encoding="utf-8")
    result = subprocess.run(
        ["mcopy", "-o", "-i", mtools_image_arg(image), str(tmp), WIC_BOOT_ENTRY],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("mcopy_boot_entry_failed:" + result.stderr.strip())


def patched_bootargs(
    old_options: str, *, profile: str, maxcpus: int | None = None
) -> str:
    tokens = [
        token
        for token in old_options.split()
        if token not in {"ignore_loglevel", "initcall_debug"}
        and not token.startswith("earlycon=")
        and not token.startswith("console=")
        and not token.startswith("maxcpus=")
    ]
    tokens.append("console=ttyAMA0,115200")
    if maxcpus is not None:
        tokens.append(f"maxcpus={maxcpus}")
    if profile == "verbose-console":
        tokens.extend(
            [
                "earlycon=pl011,mmio32,0x1a400000",
                "ignore_loglevel",
                "initcall_debug",
            ]
        )
    return " ".join(tokens)


def patch_boot_entry_options(
    text: str, *, profile: str, maxcpus: int | None = None
) -> tuple[str, str, str]:
    old_options = ""
    new_options = ""
    new_lines: list[str] = []
    patched = False
    for line in text.splitlines():
        if not patched and line.startswith("options "):
            old_options = line[len("options ") :].strip()
            new_options = patched_bootargs(
                old_options, profile=profile, maxcpus=maxcpus
            )
            new_lines.append("options " + new_options)
            patched = True
            continue
        new_lines.append(line)
    if not patched:
        raise RuntimeError("boot_entry_missing_options_line")
    return "\n".join(new_lines) + "\n", old_options, new_options


def extract_uboot_script_payload(data: bytes) -> bytes:
    if len(data) >= 8 and int.from_bytes(data[:4], "big") == len(data) - 8:
        return data[8:]
    return data


def patch_uboot_script_options(
    text: str, *, profile: str, maxcpus: int | None = None
) -> tuple[str, str, str]:
    old_options = ""
    new_options = ""
    new_lines: list[str] = []
    patched = False
    for line in text.splitlines():
        if not patched and line.startswith("setenv bootargs "):
            prefix = "setenv bootargs "
            old_options = line[len(prefix) :].strip()
            quote = ""
            if len(old_options) >= 2 and old_options[0] == old_options[-1] == '"':
                old_options = old_options[1:-1]
                quote = '"'
            new_options = patched_bootargs(
                old_options, profile=profile, maxcpus=maxcpus
            )
            new_lines.append(prefix + quote + new_options + quote)
            patched = True
            continue
        new_lines.append(line)
    if not patched:
        raise RuntimeError("uboot_script_missing_bootargs_line")
    return "\n".join(new_lines) + "\n", old_options, new_options


def patch_uboot_script(
    image: Path,
    tmp_dir: Path,
    *,
    profile: str,
    maxcpus: int | None = None,
) -> tuple[str, str]:
    ensure_mtools()
    for tool in ["dumpimage", "mkimage"]:
        if shutil.which(tool) is None:
            raise RuntimeError(f"missing_tool:{tool}")

    tmp_dir.mkdir(parents=True, exist_ok=True)
    old_script = tmp_dir / "boot.scr.orig"
    extracted = tmp_dir / "boot.scr.payload"
    patched_text = tmp_dir / "boot.scr.txt"
    new_script = tmp_dir / "boot.scr"
    result = subprocess.run(
        ["mcopy", "-o", "-i", mtools_image_arg(image), WIC_UBOOT_SCRIPT, str(old_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("mcopy_uboot_script_failed:" + result.stderr.strip())
    result = subprocess.run(
        ["dumpimage", "-T", "script", "-p", "0", "-o", str(extracted), str(old_script)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("dumpimage_uboot_script_failed:" + result.stderr.strip())

    script = extract_uboot_script_payload(extracted.read_bytes()).decode("utf-8")
    patched, old_options, new_options = patch_uboot_script_options(
        script, profile=profile, maxcpus=maxcpus
    )
    patched_text.write_text(patched, encoding="utf-8")
    result = subprocess.run(
        [
            "mkimage",
            "-A",
            "arm64",
            "-T",
            "script",
            "-C",
            "none",
            "-n",
            "Apollo FVP local boot",
            "-d",
            str(patched_text),
            str(new_script),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("mkimage_uboot_script_failed:" + result.stderr.strip())
    result = subprocess.run(
        ["mcopy", "-o", "-i", mtools_image_arg(image), str(new_script), WIC_UBOOT_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("mcopy_patched_uboot_script_failed:" + result.stderr.strip())
    return old_options, new_options


def prepare_rootfs_for_qbox(
    src: Path,
    dst_dir: Path,
    *,
    profile: str,
    maxcpus: int | None = None,
) -> tuple[Path, dict[str, object]]:
    info: dict[str, object] = {
        "input": str(src),
        "output": str(src),
        "profile": profile,
        "changed": False,
    }
    if profile == "none":
        info["state"] = "unchanged"
        return src, info

    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / f"{src.stem}-{profile}{src.suffix}"
    copy_sparse(src, dst)
    try:
        boot_entry = read_boot_entry(dst)
        patched, old_options, new_options = patch_boot_entry_options(
            boot_entry, profile=profile, maxcpus=maxcpus
        )
        write_boot_entry(dst, patched, dst_dir)
        boot_entry_name = WIC_BOOT_ENTRY
        state = "copied_and_patched_boot_entry"
    except RuntimeError as exc:
        if not str(exc).startswith("mtype_boot_entry_failed:"):
            raise
        old_options, new_options = patch_uboot_script(
            dst, dst_dir, profile=profile, maxcpus=maxcpus
        )
        boot_entry_name = WIC_UBOOT_SCRIPT
        state = "copied_and_patched_uboot_script"
    info.update(
        {
            "output": str(dst),
            "state": state,
            "changed": old_options != new_options,
            "boot_entry": boot_entry_name,
            "boot_partition_offset": WIC_BOOT_PARTITION_OFFSET,
            "old_options": old_options,
            "new_options": new_options,
        }
    )
    return dst, info


def pad_flash_image(
    path: Path, target_size: int, *, chunk_size: int = 1024 * 1024
) -> int:
    current_size = path.stat().st_size
    if current_size >= target_size:
        return 0

    remaining = target_size - current_size
    fill = bytes([FLASH_ERASED_VALUE]) * min(chunk_size, remaining)
    with path.open("ab") as flash:
        while remaining:
            write_size = min(len(fill), remaining)
            flash.write(fill[:write_size])
            remaining -= write_size
    return target_size - current_size


def prepare_flash_for_qbox(
    src: Path,
    dst_dir: Path,
    *,
    min_size: int | None = None,
    allow_pad: bool = False,
) -> tuple[Path, dict[str, object]]:
    info: dict[str, object] = {
        "input": str(src),
        "output": str(src),
        "state": "raw",
        "changed": False,
    }
    with src.open("rb") as flash:
        magic = flash.read(2)
    path = src
    can_modify = allow_pad
    if magic == b"\x1f\x8b":
        dst_dir.mkdir(parents=True, exist_ok=True)
        path = dst_dir / f"{src.stem}.raw{src.suffix}"
        with gzip.open(src, "rb") as compressed, path.open("wb") as raw:
            shutil.copyfileobj(compressed, raw)
        can_modify = True
        info.update(
            {
                "output": str(path),
                "state": "gzip_decompressed_for_qbox_raw_memory",
                "changed": True,
                "compressed_size": src.stat().st_size,
                "raw_size": path.stat().st_size,
            }
        )

    if min_size is None:
        return path, info

    size_before_pad = path.stat().st_size
    info["minimum_size"] = min_size
    info["size_before_pad"] = size_before_pad
    if size_before_pad >= min_size:
        info["pad_state"] = "not_required"
        return path, info

    if not can_modify:
        info["pad_state"] = "skipped_source_not_copied"
        info["pad_required_bytes"] = min_size - size_before_pad
        return path, info

    padded_bytes = pad_flash_image(path, min_size)
    info.update(
        {
            "output": str(path),
            "changed": True,
            "pad_state": "padded_with_erased_value",
            "pad_erased_value": hex(FLASH_ERASED_VALUE),
            "padded_bytes": padded_bytes,
            "padded_size": path.stat().st_size,
            "state": str(info["state"]) + "_padded_to_qbox_flash_size",
        }
    )
    return path, info


def prepare_sparse_file(path: Path, size: int) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as backing:
        backing.truncate(size)
    return path


def hex_range(start: int, end: int) -> dict[str, str]:
    return {"start": hex(start), "end": hex(end)}


def find_nonzero_ranges(data: bytes, *, limit: int = 16) -> tuple[int, list[dict[str, str]]]:
    count = 0
    ranges: list[dict[str, str]] = []
    start: int | None = None
    for offset, value in enumerate(data):
        if value:
            count += 1
            if start is None:
                start = offset
        elif start is not None:
            if len(ranges) < limit:
                ranges.append(hex_range(start, offset))
            start = None
    if start is not None and len(ranges) < limit:
        ranges.append(hex_range(start, len(data)))
    return count, ranges


def nonzero_count(data: bytes) -> int:
    return sum(1 for value in data if value)


def flash_matches(sample: bytes, flash_path: Path | None) -> list[str]:
    if not sample or not any(sample) or flash_path is None or not flash_path.exists():
        return []
    flash = flash_path.read_bytes()
    matches: list[str] = []
    offset = flash.find(sample)
    while offset != -1 and len(matches) < 8:
        matches.append(hex(offset))
        offset = flash.find(sample, offset + 1)
    return matches


def parse_mcuboot_ram_load_size(flash: bytes, offset: int) -> dict[str, object]:
    info: dict[str, object] = {"offset": hex(offset)}
    if offset + 24 > len(flash):
        info["valid"] = False
        info["reason"] = "header_out_of_range"
        return info

    magic, load_addr, header_size, protected_tlv_size, image_size, flags = (
        struct.unpack_from("<IIHHII", flash, offset)
    )
    info.update(
        {
            "magic": hex(magic),
            "load_addr": hex(load_addr),
            "header_size": hex(header_size),
            "protected_tlv_size": hex(protected_tlv_size),
            "image_size": hex(image_size),
            "flags": hex(flags),
            "encrypted": bool(flags & (IMAGE_F_ENCRYPTED_AES128 | IMAGE_F_ENCRYPTED_AES256)),
            "ram_load": bool(flags & IMAGE_F_RAM_LOAD),
        }
    )
    if magic != IMAGE_MAGIC:
        info["valid"] = False
        info["reason"] = "invalid_image_magic"
        return info

    def parse_tlv_entries(start: int, total: int) -> list[dict[str, str]]:
        entries: list[dict[str, str]] = []
        current = start + 4
        end = start + total
        while current + 4 <= end and len(entries) < 32:
            tlv_type, tlv_len = struct.unpack_from("<HH", flash, offset + current)
            entries.append(
                {
                    "offset": hex(current),
                    "type": hex(tlv_type),
                    "length": hex(tlv_len),
                }
            )
            current += 4 + tlv_len
        return entries

    tlv_offset = header_size + image_size
    if offset + tlv_offset + 4 > len(flash):
        info["valid"] = False
        info["reason"] = "tlv_info_out_of_range"
        return info

    tlv_magic, tlv_total = struct.unpack_from("<HH", flash, offset + tlv_offset)
    info["tlv_offset"] = hex(tlv_offset)
    info["first_tlv_magic"] = hex(tlv_magic)
    info["first_tlv_total"] = hex(tlv_total)
    if tlv_magic == IMAGE_TLV_PROT_INFO_MAGIC:
        if protected_tlv_size != tlv_total:
            info["valid"] = False
            info["reason"] = "protected_tlv_size_mismatch"
            return info
        info["protected_tlvs"] = parse_tlv_entries(tlv_offset, tlv_total)
        unprotected_tlv_offset = tlv_offset + tlv_total
        if offset + unprotected_tlv_offset + 4 > len(flash):
            info["valid"] = False
            info["reason"] = "unprotected_tlv_info_out_of_range"
            return info
        tlv_magic, tlv_total = struct.unpack_from("<HH", flash, offset + unprotected_tlv_offset)
        info["unprotected_tlv_offset"] = hex(unprotected_tlv_offset)
        info["unprotected_tlv_magic"] = hex(tlv_magic)
        info["unprotected_tlv_total"] = hex(tlv_total)
    elif protected_tlv_size:
        info["valid"] = False
        info["reason"] = "missing_protected_tlv_info"
        return info

    if tlv_magic != IMAGE_TLV_INFO_MAGIC:
        info["valid"] = False
        info["reason"] = "invalid_image_tlv_magic"
        return info

    unprotected_entries = parse_tlv_entries(
        int(str(info.get("unprotected_tlv_offset", hex(tlv_offset))), 16),
        tlv_total,
    )
    info["unprotected_tlvs"] = unprotected_entries
    info["expected_encryption_tlv"] = {
        "type": hex(IMAGE_TLV_ENC_KW),
        "length": hex(EXPECTED_ENC_KW_LEN_AES128),
        "present": any(
            entry["type"] == hex(IMAGE_TLV_ENC_KW)
            and entry["length"] == hex(EXPECTED_ENC_KW_LEN_AES128)
            for entry in unprotected_entries
        ),
    }
    total_size = tlv_offset + protected_tlv_size + tlv_total
    info["valid"] = True
    info["boot_read_image_size"] = hex(total_size)
    return info


def si_mapped_image(
    data: bytes,
    *,
    header_file_offset: int,
    code_file_offset: int,
    sample_size: int,
) -> bytes:
    return (
        data[header_file_offset : header_file_offset + sample_size]
        + data[code_file_offset:header_file_offset]
    )


def matching_prefix_len(left: bytes, right: bytes) -> int:
    limit = min(len(left), len(right))
    for offset in range(limit):
        if left[offset] != right[offset]:
            return offset
    return limit


def si_slot_match(
    data: bytes,
    flash: bytes,
    *,
    name: str,
    offset: int,
    header_file_offset: int,
    code_file_offset: int,
    sample_size: int,
) -> dict[str, object]:
    image_info = parse_mcuboot_ram_load_size(flash, offset)
    mapped = si_mapped_image(
        data,
        header_file_offset=header_file_offset,
        code_file_offset=code_file_offset,
        sample_size=sample_size,
    )
    slot = flash[offset : offset + len(mapped)]
    valid_image = bool(image_info.get("valid"))
    prefix = matching_prefix_len(mapped, slot) if valid_image else 0
    boot_size_hex = image_info.get("boot_read_image_size")
    boot_size = int(boot_size_hex, 16) if isinstance(boot_size_hex, str) else None
    return {
        "slot": name,
        "flash_offset": hex(offset),
        "image": image_info,
        "header_match": valid_image and (
            data[
                header_file_offset : header_file_offset + sample_size
            ]
            == flash[offset : offset + sample_size]
        ),
        "code_start_match": valid_image and (
            data[code_file_offset : code_file_offset + sample_size]
            == flash[offset + sample_size : offset + (2 * sample_size)]
        ),
        "mapped_prefix_match": hex(prefix),
        "copied_full_boot_image": bool(boot_size is not None and prefix >= boot_size),
        "payload_still_matches_flash": bool(boot_size is not None and prefix >= boot_size),
    }


def sample_region(
    data: bytes,
    *,
    offset: int,
    size: int,
    flash_path: Path | None,
) -> dict[str, object]:
    sample = data[offset : min(len(data), offset + size)]
    return {
        "file_offset": hex(offset),
        "size": hex(len(sample)),
        "nonzero_bytes": nonzero_count(sample),
        "sha256": hashlib.sha256(sample).hexdigest() if sample else None,
        "flash_matches": flash_matches(sample, flash_path),
    }


def analyze_host_si_sram(
    path: Path | None,
    flash_path: Path | None,
    *,
    expected_size: int,
    image_header_logical_base: int,
    image_code_logical_base: int,
    header_file_offset: int,
    code_file_offset: int,
    sample_size: int,
    primary_flash_offset: int,
    secondary_flash_offset: int,
) -> dict[str, object] | None:
    if path is None:
        return None
    info: dict[str, object] = {
        "path": str(path),
        "expected_size": expected_size,
        "logical_layout": {
            "image_header_logical_base": hex(image_header_logical_base),
            "image_code_logical_base": hex(image_code_logical_base),
            "header_file_offset": hex(header_file_offset),
            "code_file_offset": hex(code_file_offset),
        },
    }
    if not path.exists():
        info.update({"exists": False})
        return info

    data = path.read_bytes()
    flash = flash_path.read_bytes() if flash_path is not None and flash_path.exists() else b""
    slot_matches = [
        si_slot_match(
            data,
            flash,
            name="primary",
            offset=primary_flash_offset,
            header_file_offset=header_file_offset,
            code_file_offset=code_file_offset,
            sample_size=sample_size,
        ),
        si_slot_match(
            data,
            flash,
            name="secondary",
            offset=secondary_flash_offset,
            header_file_offset=header_file_offset,
            code_file_offset=code_file_offset,
            sample_size=sample_size,
        ),
    ] if flash else []
    full_primary_copy = any(
        match.get("slot") == "primary" and match.get("copied_full_boot_image")
        for match in slot_matches
    )
    nonzero, ranges = find_nonzero_ranges(data)
    info.update(
        {
            "exists": True,
            "size": len(data),
            "nonzero_bytes": nonzero,
            "nonzero_ranges": ranges,
            "header_sample": sample_region(
                data,
                offset=header_file_offset,
                size=sample_size,
                flash_path=flash_path,
            ),
            "code_start_sample": sample_region(
                data,
                offset=code_file_offset,
                size=sample_size,
                flash_path=flash_path,
            ),
            "slot_matches": slot_matches,
            "classification": (
                "flash_area_read_completed_before_encrypted_image_key_or_decrypt"
                if full_primary_copy
                else (
                    "host_window_contains_nonzero_runtime_data"
                    if nonzero
                    else "host_window_copy_not_observed"
                )
            ),
        }
    )
    if nonzero:
        first_nonzero = next(offset for offset, value in enumerate(data) if value)
        first_sample_offset = first_nonzero & ~(sample_size - 1)
        info["first_nonzero_sample"] = sample_region(
            data,
            offset=first_sample_offset,
            size=sample_size,
            flash_path=flash_path,
        )
    return info


def analyze_host_si_cl0_sram(
    path: Path | None, flash_path: Path | None
) -> dict[str, object] | None:
    return analyze_host_si_sram(
        path,
        flash_path,
        expected_size=HOST_SI_CL0_SRAM_WINDOW_SIZE,
        image_header_logical_base=HOST_SI_CL0_IMG_HDR_LOGICAL_BASE,
        image_code_logical_base=HOST_SI_CL0_IMG_CODE_LOGICAL_BASE,
        header_file_offset=HOST_SI_CL0_HEADER_FILE_OFFSET,
        code_file_offset=HOST_SI_CL0_CODE_FILE_OFFSET,
        sample_size=HOST_SI_CL0_SAMPLE_SIZE,
        primary_flash_offset=SI_CL0_PRIMARY_FLASH_OFFSET,
        secondary_flash_offset=SI_CL0_SECONDARY_FLASH_OFFSET,
    )


def analyze_host_si_cl1_sram(
    path: Path | None, flash_path: Path | None
) -> dict[str, object] | None:
    return analyze_host_si_sram(
        path,
        flash_path,
        expected_size=HOST_SI_CL1_SRAM_WINDOW_SIZE,
        image_header_logical_base=HOST_SI_CL1_IMG_HDR_LOGICAL_BASE,
        image_code_logical_base=HOST_SI_CL1_IMG_CODE_LOGICAL_BASE,
        header_file_offset=HOST_SI_CL1_HEADER_FILE_OFFSET,
        code_file_offset=HOST_SI_CL1_CODE_FILE_OFFSET,
        sample_size=HOST_SI_CL1_SAMPLE_SIZE,
        primary_flash_offset=SI_CL1_PRIMARY_FLASH_OFFSET,
        secondary_flash_offset=SI_CL1_SECONDARY_FLASH_OFFSET,
    )


def analyze_host_ap_bl2_header_sram(path: Path | None) -> dict[str, object] | None:
    if path is None:
        return None
    info: dict[str, object] = {
        "path": str(path),
        "expected_size": HOST_AP_BL2_HEADER_SRAM_SIZE,
        "logical_layout": {
            "rsctbl_ap_pa": "0x00100000",
            "vdev0vring0_ap_pa": "0x00120000",
            "vdev0vring1_ap_pa": "0x00140000",
            "vdev0buffer_ap_pa": "0x00160000",
        },
    }
    if not path.exists():
        info.update({"exists": False})
        return info

    data = path.read_bytes()
    nonzero, ranges = find_nonzero_ranges(data)
    sample = data[
        HOST_AP_BL2_HEADER_RSC_TABLE_OFFSET:
        HOST_AP_BL2_HEADER_RSC_TABLE_OFFSET + HOST_AP_BL2_HEADER_SAMPLE_SIZE
    ]
    words = list(struct.unpack_from("<" + ("I" * (len(sample) // 4)), sample)) if sample else []
    rsc_offset = words[4] if len(words) > 4 else None
    looks_like_resource_table = bool(
        len(words) >= 5
        and words[0] in {1, 2}
        and 0 < words[1] < 16
        and words[2] == 0
        and words[3] == 0
        and isinstance(rsc_offset, int)
        and 0x14 <= rsc_offset < 0x20000
    )
    info.update(
        {
            "exists": True,
            "size": len(data),
            "nonzero_bytes": nonzero,
            "nonzero_ranges": ranges,
            "resource_table_words": [hex(word) for word in words[:16]],
            "resource_table_candidate": looks_like_resource_table,
            "resource_table_sample": sample_region(
                data,
                offset=HOST_AP_BL2_HEADER_RSC_TABLE_OFFSET,
                size=HOST_AP_BL2_HEADER_SAMPLE_SIZE,
                flash_path=None,
            ),
            "vdev0vring0_sample": sample_region(
                data,
                offset=HOST_AP_BL2_HEADER_VRING0_OFFSET,
                size=HOST_AP_BL2_HEADER_SAMPLE_SIZE,
                flash_path=None,
            ),
            "vdev0vring1_sample": sample_region(
                data,
                offset=HOST_AP_BL2_HEADER_VRING1_OFFSET,
                size=HOST_AP_BL2_HEADER_SAMPLE_SIZE,
                flash_path=None,
            ),
            "vdev0buffer_sample": sample_region(
                data,
                offset=HOST_AP_BL2_HEADER_VDEV0BUFFER_OFFSET,
                size=HOST_AP_BL2_HEADER_SAMPLE_SIZE,
                flash_path=None,
            ),
            "classification": (
                "resource_table_visible"
                if looks_like_resource_table
                else (
                    "host_window_contains_nonzero_runtime_data"
                    if nonzero
                    else "resource_table_not_written"
                )
            ),
        }
    )
    return info


def init_rse_fwu_private_metadata(
    rse_flash: Path, *, enabled: bool, writable_copy: bool
) -> dict[str, object]:
    info: dict[str, object] = {
        "enabled": enabled,
        "path": str(rse_flash),
        "offset": hex(RSE_FWU_PRIVATE_METADATA_OFFSET),
        "metadata_size": RSE_FWU_PRIVATE_METADATA_SIZE,
        "changed": False,
    }
    if not enabled:
        info["state"] = "disabled"
        return info
    if not writable_copy:
        info["state"] = "skipped_not_writable_copy"
        return info

    try:
        image_size = rse_flash.stat().st_size
    except OSError as exc:
        info["state"] = "error"
        info["error"] = str(exc)
        return info
    info["image_size"] = image_size

    min_size = RSE_FWU_PRIVATE_METADATA_OFFSET + RSE_FWU_PRIVATE_METADATA_SIZE
    if image_size < min_size:
        info["state"] = "error"
        info["error"] = f"image_too_small:{image_size}<0x{min_size:x}"
        return info

    with rse_flash.open("r+b") as flash:
        flash.seek(RSE_FWU_PRIVATE_METADATA_OFFSET)
        before = flash.read(RSE_FWU_PRIVATE_METADATA_SIZE)
        boot_index = before[0]
        fwu_states = list(before[1 : 1 + RSE_FWU_COMPONENT_NUMBER])
        info["previous_boot_index"] = boot_index
        info["previous_fwu_states"] = fwu_states
        info["previous_header_hex"] = before[:8].hex()

        boot_valid = boot_index in RSE_FWU_VALID_BOOT_INDICES
        states_valid = all(state in RSE_FWU_VALID_STATES for state in fwu_states)
        if boot_valid and states_valid:
            info["state"] = "existing_valid"
            info["boot_index"] = boot_index
            return info

        metadata = bytes(RSE_FWU_PRIVATE_METADATA_SIZE)
        flash.seek(RSE_FWU_PRIVATE_METADATA_OFFSET)
        flash.write(metadata)
        flash.flush()
        os.fsync(flash.fileno())

    info["state"] = "initialized_slot0_ready"
    info["changed"] = True
    info["boot_index"] = RSE_FWU_BOOT_INDEX_SLOT0
    info["fwu_states"] = [0] * RSE_FWU_COMPONENT_NUMBER
    return info


def clean_text(text: str) -> str:
    return ANSI_RE.sub("", text).replace("\r", "")


def evaluate(
    logs: dict[str, str], *, rse_sram_dmi_smoke: bool = False
) -> dict[str, object]:
    combined = clean_text("\n".join(logs.values()))
    marker_hits = {
        group: {marker: marker in combined for marker in markers}
        for group, markers in REQUIRED_MARKERS.items()
    }
    fail_hits = {pattern: pattern in combined for pattern in FAIL_PATTERNS}
    linux_hit = any(marker_hits["linux_boot"].values())
    all_non_linux = all(
        hit
        for group, hits in marker_hits.items()
        if group != "linux_boot"
        for hit in hits.values()
    )
    rse_sram_dmi_smoke_hit = (
        "BL2 image validated successfully" in combined
        and "Jumping to BL2" in combined
        and "Image 4 loaded from the primary slot" in combined
        and "BL2: SI MBIST happens here" in combined
    )
    pass_mode = "full_system"
    passed = all_non_linux and linux_hit
    if rse_sram_dmi_smoke and rse_sram_dmi_smoke_hit:
        passed = True
        pass_mode = "rse_sram_dmi_smoke"
    passed = passed and not any(fail_hits.values())
    return {
        "passed": passed,
        "pass_mode": pass_mode if passed else "none",
        "rse_sram_dmi_smoke_pass": rse_sram_dmi_smoke_hit,
        "marker_hits": marker_hits,
        "fail_patterns": fail_hits,
        "log_bytes": sum(len(text.encode("utf-8", errors="replace")) for text in logs.values()),
    }


def object_dict(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}
    return {str(key): item for key, item in value.items()}


def bool_dict(value: object) -> dict[str, bool]:
    return {key: bool(item) for key, item in object_dict(value).items()}


def nested_bool_dict(value: object) -> dict[str, dict[str, bool]]:
    return {key: bool_dict(item) for key, item in object_dict(value).items()}


def string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def update_progress_marker_first_hits(
    logs: dict[str, str],
    first_hits: dict[str, dict[str, object]],
    elapsed_s: float,
) -> None:
    combined = clean_text("\n".join(logs.values()))
    for name, marker in PROGRESS_MARKERS.items():
        if name not in first_hits and marker in combined:
            first_hits[name] = {
                "elapsed_s": elapsed_s,
                "marker": marker,
            }


def progress_elapsed_s(
    first_hits: dict[str, dict[str, object]], name: str
) -> float | None:
    hit = first_hits.get(name)
    if not isinstance(hit, dict):
        return None
    value = hit.get("elapsed_s")
    return float(value) if isinstance(value, (int, float)) else None


def progress_hit_elapsed_s(hit: dict[str, object]) -> float:
    value = hit.get("elapsed_s")
    return float(value) if isinstance(value, (int, float)) else 0.0


def rounded_s(value: float | None) -> float | None:
    return round(value, 3) if value is not None else None


def build_rse_boot_timing_profile(
    first_hits: dict[str, dict[str, object]] | None,
) -> dict[str, object]:
    first_hits = first_hits or {}
    markers: list[dict[str, object]] = []
    deltas: list[dict[str, object]] = []
    previous_name: str | None = None
    previous_label: str | None = None
    previous_elapsed: float | None = None

    for name, label in RSE_BOOT_PROFILE_MARKERS:
        elapsed = progress_elapsed_s(first_hits, name)
        entry: dict[str, object] = {
            "name": name,
            "label": label,
            "marker": PROGRESS_MARKERS[name],
            "seen": elapsed is not None,
            "elapsed_s": rounded_s(elapsed),
        }
        markers.append(entry)
        if elapsed is None:
            continue
        if previous_elapsed is not None and previous_name is not None:
            delta = elapsed - previous_elapsed
            deltas.append(
                {
                    "from": previous_name,
                    "from_label": previous_label,
                    "to": name,
                    "to_label": label,
                    "delta_s": rounded_s(delta),
                }
            )
        previous_name = name
        previous_label = label
        previous_elapsed = elapsed

    slowest_delta = None
    if deltas:
        slowest_delta = max(
            deltas,
            key=progress_hit_elapsed_s,
        )

    def span(start: str, end: str) -> float | None:
        start_elapsed = progress_elapsed_s(first_hits, start)
        end_elapsed = progress_elapsed_s(first_hits, end)
        if start_elapsed is None or end_elapsed is None:
            return None
        return end_elapsed - start_elapsed

    return {
        "markers": markers,
        "deltas": deltas,
        "slowest_delta": slowest_delta,
        "summary": {
            "bl1_1_to_bl2_s": rounded_s(span("rse_bl1_1", "rse_jump_bl2")),
            "bl2_to_rse_runtime_handoff_s": rounded_s(
                span("rse_jump_bl2", "rse_first_image_slot")
            ),
            "rse_start_to_runtime_handoff_s": rounded_s(
                span("rse_bl1_1", "rse_first_image_slot")
            ),
            "rse_start_to_ap_power_on_s": rounded_s(
                span("rse_bl1_1", "rse_scp_power_on_ap")
            ),
            "rse_start_to_linux_boot_s": rounded_s(
                span("rse_bl1_1", "primary_linux_cpu")
            ),
            "rse_start_to_login_prompt_s": rounded_s(
                span("rse_bl1_1", "primary_login_prompt")
            ),
        },
    }


def shell_safe_probe_key(binary: str) -> str:
    return binary.replace("-", "_")


def parse_secure_service_tests(value: str) -> list[str]:
    requested: list[str] = []
    valid = set(SECURE_SERVICE_TEST_COMMANDS)
    for token in (part.strip().lower() for part in value.split(",")):
        if not token:
            continue
        if token == "all":
            requested.extend(DEFAULT_SECURE_SERVICE_TESTS)
            continue
        if token == "none":
            continue
        if token not in valid:
            choices = ",".join(["all", "none"] + sorted(valid))
            raise argparse.ArgumentTypeError(
                f"unknown secure-service test '{token}', choose from {choices}"
            )
        requested.append(token)

    selected: list[str] = []
    for token in requested:
        if token not in selected:
            selected.append(token)
    return selected


def parse_psa_test_list(value: str) -> str:
    test_list = value.strip()
    if not test_list:
        return ""
    if not re.fullmatch(r"(test_[0-9]{3};)+", test_list):
        raise argparse.ArgumentTypeError(
            "PSA test list must match 'test_NNN;' entries, "
            "for example 'test_403;'"
        )
    return test_list


def secure_service_probe_commands(
    timeout_s: int, tests: list[str], ps_test_list: str = ""
) -> list[str]:
    timeout_s = max(1, timeout_s)
    selected_tests = tests or []
    commands = [
        "echo __QBOX_SECURE_SERVICE_PROBE_START__",
        f"echo secure_service_tests:{','.join(selected_tests) or 'none'}",
        f"echo secure_service_ps_test_list:{ps_test_list or 'none'}",
    ]
    for binary in SECURE_SERVICE_PROBE_BINARIES:
        key = shell_safe_probe_key(binary)
        commands.append(
            f"command -v {binary} >/dev/null 2>&1; "
            f"echo secure_{key}_present_rc:$?"
        )
    commands.extend(
        [
            "echo __QBOX_SECURE_SERVICE_DIAG_START__",
            "test -e /dev/tee0; echo secure_dev_tee0_present_rc:$?",
            "test -e /dev/teepriv0; echo secure_dev_teepriv0_present_rc:$?",
            "test -d /sys/bus/arm_ffa/devices; "
            "echo secure_sys_arm_ffa_devices_present_rc:$?",
            "test -d /sys/bus/tee/devices; "
            "echo secure_sys_tee_devices_present_rc:$?",
            "ls -l /dev/tee* /dev/ffa* 2>/dev/null || true",
            "for d in /sys/bus/arm_ffa/devices/*; do "
            "[ -e \"$d\" ] || continue; "
            "echo secure_arm_ffa_device:$(basename \"$d\"); "
            "for f in uuid id modalias driver_override; do "
            "[ -e \"$d/$f\" ] && echo secure_arm_ffa_attr:$(basename \"$d\"):$f:$(cat \"$d/$f\"); "
            "done; done",
            "for d in /sys/bus/tee/devices/*; do "
            "[ -e \"$d\" ] || continue; "
            "echo secure_tee_device:$(basename \"$d\"); "
            "for f in uuid tee_version need_supplicant modalias; do "
            "[ -e \"$d/$f\" ] && echo secure_tee_attr:$(basename \"$d\"):$f:$(cat \"$d/$f\"); "
            "done; done",
            "lsmod | grep -Ei '(^|_)(tee|optee|ffa|tstee)|arm_ffa' || true",
            "dmesg | grep -Ei 'arm-ffa|optee|tstee|tee|se-proxy|smm|psa|trusted|spmc|ffa|rpc|secure' || true",
            "find /usr/bin -maxdepth 1 -type f | "
            "grep -E '/(psa|ts-|uefi|xtest|tee)' || true",
            "if command -v rpm >/dev/null 2>&1; then "
            "rpm -qa | grep -Ei '^(ts-|trusted|psa|optee|tee|uefi)' || true; fi",
            "if command -v opkg >/dev/null 2>&1; then "
            "opkg list-installed | grep -Ei '^(ts-|trusted|psa|optee|tee|uefi)' || true; fi",
            f"echo {SECURE_SERVICE_DIAG_DONE_MARKER}",
        ]
    )
    for test_name in selected_tests:
        command, rc_name = SECURE_SERVICE_TEST_COMMANDS[test_name]
        if test_name == "ps" and ps_test_list:
            command = f"{command} -t {shlex.quote(ps_test_list)}"
        commands.append(f"timeout {timeout_s}s {command}; echo {rc_name}:$?")
    commands.append(f"echo {SECURE_SERVICE_PROBE_DONE_MARKER}")
    return commands


def post_login_probe_commands(args: argparse.Namespace) -> list[str]:
    commands: list[str] = []
    done_command = f"echo {PROBE_DONE_MARKER}"
    for command in POST_LOGIN_PROBE_COMMANDS:
        if command == done_command and args.secure_service_probe:
            commands.extend(
                secure_service_probe_commands(
                    args.secure_service_probe_timeout,
                    args.secure_service_probe_tests,
                    args.secure_service_ps_test_list,
                )
            )
        if command == done_command and args.fwu_probe:
            continue
        commands.append(command)
    if args.fwu_probe:
        commands.extend(fwu_probe_commands(args.fwu_system_running_timeout))
    return commands


def evaluate_fwu_probe(
    clean_primary: str, clean_rse: str, clean_secure: str, rc_hits: dict[str, int]
) -> dict[str, object]:
    updating = re.search(r"FWU: Updating (\d+) payload\(s\)", clean_primary)
    rse_image_1_count = len(
        re.findall(r"\[INF\] Attempting to boot image 1", clean_rse)
    )
    fip_b_count = len(
        re.findall(
            r"INFO:\s+Booting with partition FIP_B",
            clean_secure,
            re.IGNORECASE,
        )
    )
    trial_state_count = len(
        re.findall(r"FWU: System booting in Trial State", clean_primary)
    )
    regular_state_count = len(
        re.findall(r"FWU: System booting in Regular State", clean_primary)
    )
    capsule_applied = (
        "Applying capsule fw.cap succeeded." in clean_primary
        and "Reboot after firmware update." in clean_primary
    )
    complete = bool(
        FWU_REBOOT_REQUESTED_MARKER in clean_primary
        and updating
        and capsule_applied
        and rse_image_1_count > 0
        and fip_b_count > 0
        and trial_state_count > 0
    )
    return {
        "start_marker": FWU_PROBE_START_MARKER in clean_primary,
        "reboot_requested_marker": FWU_REBOOT_REQUESTED_MARKER in clean_primary,
        "updating_payloads": int(updating.group(1)) if updating else None,
        "capsule_apply_succeeded": "Applying capsule fw.cap succeeded."
        in clean_primary,
        "reboot_after_update": "Reboot after firmware update." in clean_primary,
        "capsule_applied": capsule_applied,
        "rse_image_1_count": rse_image_1_count,
        "fip_b_count": fip_b_count,
        "trial_state_count": trial_state_count,
        "regular_state_count": regular_state_count,
        "return_codes": {
            name: value for name, value in rc_hits.items() if name.startswith("fwu_")
        },
        "complete": complete,
    }


def parse_ps_test_403_progress(clean_primary: str) -> dict[str, object]:
    matches = list(re.finditer(r"TEST:\s*403\b[^\n]*", clean_primary))
    if not matches:
        return {"started": False}

    match = matches[-1]
    tail = clean_primary[match.end() :]
    end_offsets = [
        stop.start()
        for stop in re.finditer(
            r"\n(?:TEST:\s*\d+\b|secure_psa_ps_api_test_rc:|"
            r"__QBOX_SECURE_SERVICE_PROBE_DONE__)",
            tail,
        )
    ]
    end = match.end() + min(end_offsets) if end_offsets else len(clean_primary)
    section = clean_primary[match.start() : end]
    checks = [
        int(check.group(1))
        for check in re.finditer(r"\[Check\s+(\d+)\]", section)
    ]
    insufficient_space_uids = [
        int(uid.group(1))
        for uid in re.finditer(
            r"UID\s+(\d+)\s+set failed due to insufficient space",
            section,
        )
    ]
    removing_uids = [
        int(uid.group(1))
        for uid in re.finditer(r"Removing UID\s+(\d+)", section)
    ]
    last_observed_line = ""
    for line in section.splitlines():
        line = line.strip()
        if line and not line.startswith("root@"):
            last_observed_line = line

    return {
        "started": True,
        "checks_seen": checks,
        "last_check": checks[-1] if checks else None,
        "insufficient_space_uid": (
            insufficient_space_uids[-1] if insufficient_space_uids else None
        ),
        "remove_all_registered_uids": "Remove all registered UIDs" in section,
        "removing_uid_count": len(removing_uids),
        "last_removing_uid": removing_uids[-1] if removing_uids else None,
        "test_result_passed": "TEST RESULT: PASSED" in section,
        "test_result_failed": "TEST RESULT: FAILED" in section,
        "last_observed_line": last_observed_line,
    }


def parse_secure_service_progress(clean_primary: str) -> dict[str, object]:
    tests = re.findall(r"\bsecure_service_tests:([^\n]+)", clean_primary)
    ps_test_lists = re.findall(
        r"\bsecure_service_ps_test_list:([^\n]+)", clean_primary
    )
    return {
        "requested_tests": tests[-1].strip() if tests else None,
        "ps_test_list": ps_test_lists[-1].strip() if ps_test_lists else None,
        "ps_test_403": parse_ps_test_403_progress(clean_primary),
    }


def evaluate_post_login_probe(
    primary_console: str, secure_console: str = "", rse_console: str = ""
) -> dict[str, object]:
    clean_primary = clean_text(primary_console)
    clean_secure = clean_text(secure_console)
    clean_rse = clean_text(rse_console)
    driver_hits = {
        name: all(
            re.search(pattern, clean_primary, re.IGNORECASE | re.MULTILINE)
            for pattern in patterns
        )
        for name, patterns in POST_LOGIN_DRIVER_PATTERNS.items()
    }
    rc_hits = {
        match.group(1): int(match.group(2))
        for match in re.finditer(r"\b([A-Za-z0-9_]+_rc):(\d+)\b", clean_primary)
    }
    secure_presence = {
        binary: rc_hits.get(f"secure_{shell_safe_probe_key(binary)}_present_rc")
        for binary in SECURE_SERVICE_PROBE_BINARIES
    }
    secure_return_codes = {
        name: value for name, value in rc_hits.items() if name.startswith("secure_")
    }
    secure_failures = {
        name: bool(
            re.search(pattern, clean_secure, re.IGNORECASE | re.MULTILINE)
            or re.search(pattern, clean_primary, re.IGNORECASE | re.MULTILINE)
        )
        for name, pattern in SECURE_SERVICE_FAILURE_PATTERNS.items()
    }
    return {
        "done_marker": PROBE_DONE_MARKER in clean_primary,
        "driver_patterns": driver_hits,
        "return_codes": rc_hits,
        "secure_service_probe": {
            "done_marker": SECURE_SERVICE_PROBE_DONE_MARKER in clean_primary,
            "diag_done_marker": SECURE_SERVICE_DIAG_DONE_MARKER in clean_primary,
            "binary_presence_rc": secure_presence,
            "return_codes": secure_return_codes,
            "observed_failures": secure_failures,
            "progress": parse_secure_service_progress(clean_primary),
        },
        "fwu_probe": evaluate_fwu_probe(
            clean_primary, clean_rse, clean_secure, rc_hits
        ),
    }


def fwu_probe_stage_complete(logs: dict[str, str]) -> bool:
    primary = clean_text(logs.get("primary_console", ""))
    rse = clean_text(logs.get("rse", ""))
    secure = clean_text(logs.get("secure_console", ""))
    rc_hits = {
        match.group(1): int(match.group(2))
        for match in re.finditer(r"\b([A-Za-z0-9_]+_rc):(\d+)\b", primary)
    }
    return bool(evaluate_fwu_probe(primary, rse, secure, rc_hits)["complete"])


def selected_secure_service_failures(
    selected_tests: list[str], secure_service_eval: dict[str, object]
) -> dict[str, object]:
    presence = secure_service_eval.get("binary_presence_rc", {})
    return_codes = secure_service_eval.get("return_codes", {})
    diag_done = bool(secure_service_eval.get("diag_done_marker"))
    probe_done = bool(secure_service_eval.get("done_marker"))
    failures: dict[str, object] = {}

    if not isinstance(presence, dict) or not isinstance(return_codes, dict):
        return failures

    for test_name in selected_tests:
        binary = SECURE_SERVICE_TEST_BINARIES[test_name]
        presence_key = f"secure_{shell_safe_probe_key(binary)}_present_rc"
        presence_rc = presence.get(binary)
        if presence_rc is None:
            if diag_done:
                failures[presence_key] = "missing"
        elif presence_rc != 0:
            failures[presence_key] = presence_rc

        rc_name = SECURE_SERVICE_TEST_COMMANDS[test_name][1]
        rc = return_codes.get(rc_name)
        if rc is None:
            if probe_done:
                failures[rc_name] = "missing"
        elif rc != 0:
            failures[rc_name] = rc

    return failures


def format_rc_failures(failures: dict[str, object]) -> str:
    return ",".join(f"{name}={failures[name]}" for name in sorted(failures))


def classify_ps403_progress_blocker(
    secure_service_eval: dict[str, object],
) -> str | None:
    progress = secure_service_eval.get("progress", {})
    if not isinstance(progress, dict):
        return None
    ps_test_403 = progress.get("ps_test_403", {})
    if not isinstance(ps_test_403, dict) or not ps_test_403.get("started"):
        return None

    insufficient_uid = ps_test_403.get("insufficient_space_uid")
    if ps_test_403.get("remove_all_registered_uids"):
        if isinstance(insufficient_uid, int):
            return f"qbox_secure_service_ps403_cleanup_timeout:uid_{insufficient_uid}"
        return "qbox_secure_service_ps403_cleanup_timeout"

    if isinstance(insufficient_uid, int):
        return f"qbox_secure_service_ps403_insufficient_space_timeout:uid_{insufficient_uid}"

    last_check = ps_test_403.get("last_check")
    if isinstance(last_check, int):
        return f"qbox_secure_service_ps403_timeout:check_{last_check}"

    return "qbox_secure_service_ps403_timeout:started"


def classify_known_runtime_blocker(logs: dict[str, str]) -> str | None:
    combined = clean_text("\n".join(logs.values()))
    for marker, blocker in KNOWN_RUNTIME_BLOCKERS:
        if marker in combined:
            return blocker
    return None


def read_console_logs(out_dir: Path) -> dict[str, str]:
    logs: dict[str, str] = {}
    for role, filename in CONSOLE_LOGS.items():
        path = out_dir / filename
        if path.exists():
            logs[role] = path.read_text(encoding="utf-8", errors="replace")
        else:
            logs[role] = ""
    return logs


def read_required_pass_marker_file(path: Path) -> str:
    flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError:
        return ""
    try:
        file_stat = os.fstat(fd)
        if not stat.S_ISREG(file_stat.st_mode):
            return ""
        data = os.read(fd, MAX_REQUIRED_PASS_MARKER_BYTES)
    except OSError:
        return ""
    finally:
        os.close(fd)
    return data.decode("utf-8", errors="replace")


def required_pass_marker_argument_error(requirements: list[list[str]]) -> str | None:
    if len(requirements) > MAX_REQUIRED_PASS_MARKERS:
        return f"--required-pass-marker may be used at most {MAX_REQUIRED_PASS_MARKERS} times"
    filenames = {filename for filename, _marker in requirements}
    if len(filenames) > MAX_REQUIRED_PASS_MARKER_FILES:
        return (
            "--required-pass-marker may reference at most "
            f"{MAX_REQUIRED_PASS_MARKER_FILES} files"
        )
    for filename, marker in requirements:
        if not marker or len(marker) > MAX_REQUIRED_PASS_MARKER_LENGTH:
            return (
                "--required-pass-marker MARKER must contain 1 to "
                f"{MAX_REQUIRED_PASS_MARKER_LENGTH} characters"
            )
        if not all(char.isprintable() for char in filename + marker):
            return "--required-pass-marker arguments must not contain control characters"
    return None


def missing_required_pass_markers(requirements: list[list[str]]) -> list[str]:
    texts: dict[Path, str] = {}
    missing: list[str] = []
    for filename, marker in requirements:
        path = Path(filename)
        if path not in texts:
            texts[path] = read_required_pass_marker_file(path)
        if marker not in texts[path]:
            missing.append(f"{path}:{marker}")
    return missing


def required_pass_marker_blocker(
    base_passed: bool,
    missing: list[str],
    timed_out: bool,
) -> str | None:
    if not base_passed or not missing:
        return None
    prefix = (
        "qbox_required_pass_marker_timeout:"
        if timed_out
        else "qbox_required_pass_marker_missing:"
    )
    return prefix + ",".join(missing)


def parse_qemu_trace(out_dir: Path, enabled: bool) -> dict[str, str] | None:
    if not enabled:
        return None
    trace_path = out_dir / QEMU_TRACE_LOG
    if not trace_path.exists():
        return None

    text = trace_path.read_text(encoding="utf-8", errors="replace")
    reset = TRACE_RESET_RE.search(text)
    exception = TRACE_EXCEPTION_RE.search(text)
    fault = TRACE_FAULT_ADDR_RE.search(text)
    pmsa_matches = list(TRACE_PMSA_RE.finditer(text))
    pmsa = None
    if fault:
        for match in pmsa_matches:
            if match.start() > fault.start():
                break
            pmsa = match
    if not any((reset, exception, fault, pmsa)):
        return None
    if not any((exception, fault)):
        return None

    first_fault: dict[str, str] = {"trace_log": str(trace_path.resolve())}
    if reset:
        first_fault["reset_sp"] = reset.group(1).lower()
        first_fault["reset_pc"] = reset.group(2).lower()
    if exception:
        first_fault["exception"] = exception.group(1)
        first_fault["cpu"] = exception.group(2)
    if fault:
        first_fault["fault_address"] = fault.group(1).lower()
    if pmsa:
        first_fault["access_type"] = pmsa.group(1)
        first_fault["access_address"] = pmsa.group(2).lower()
    return first_fault


def read_json_artifact(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None

    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


def parse_cc3xx_stats(args: argparse.Namespace) -> dict[str, object]:
    if not (args.cc3xx_stats or args.qbox_perf_profile):
        return {"enabled": False}

    path = args.out_dir / RSE_CC3XX_STATS
    parsed = read_json_artifact(path)
    return {
        "enabled": True,
        "interval": args.cc3xx_stats_interval,
        "path": str(path.resolve()),
        "present": parsed is not None,
        "stats": parsed,
    }


def parse_qbox_perf_profile(args: argparse.Namespace) -> dict[str, object]:
    if not args.qbox_perf_profile:
        return {"enabled": False}

    profile_root = args.out_dir / QBOX_PERF_PROFILE_DIR
    qemu_initiator_dir = profile_root / QEMU_INITIATOR_PROFILE_DIR
    cc3xx_profile = profile_root / CC3XX_PROFILE
    hotpath_profile = profile_root / RSE_HOTPATH_PROFILE

    def parse_profile_dir(path: Path) -> list[dict[str, object]]:
        result: list[dict[str, object]] = []
        if not path.exists():
            return result
        for profile in sorted(path.glob("*.json")):
            parsed = read_json_artifact(profile)
            result.append(
                {
                    "path": str(profile.resolve()),
                    "present": parsed is not None,
                    "stats": parsed,
                }
            )
        return result

    cc3xx_parsed = read_json_artifact(cc3xx_profile)
    hotpath_parsed = read_json_artifact(hotpath_profile)
    return {
        "enabled": True,
        "root": str(profile_root.resolve()),
        "qemu_initiator_dir": str(qemu_initiator_dir.resolve()),
        "cc3xx_profile": {
            "path": str(cc3xx_profile.resolve()),
            "present": cc3xx_parsed is not None,
            "stats": cc3xx_parsed,
        },
        "rse_hotpath_profile": {
            "path": str(hotpath_profile.resolve()),
            "present": hotpath_parsed is not None,
            "stats": hotpath_parsed,
        },
        "qemu_initiator_profiles": parse_profile_dir(qemu_initiator_dir),
    }


def qemu_trace_enabled(args: argparse.Namespace) -> bool:
    return bool(args.qemu_trace or args.qemu_trace_filter or args.boot_enc_trace)


def cc3xx_status_read_fastpath_spec() -> str:
    return ",".join(
        f"0x{RSE_CC3XX_BASE_S + offset:x}=0x{value:x}"
        for offset, value in sorted(CC3XX_STATUS_READ_FASTPATH_VALUES.items())
    )


def cc3xx_local_mmio_fastpath_spec() -> str:
    return f"0x{RSE_CC3XX_BASE_S:x}:0x2000"


def rse_storage_direct_fastpath_spec() -> str:
    return (
        f"0x{RSE_BOOT_FLASH_BASE_S + RSE_BOOT_FLASH_STORAGE_OFFSET:x}:"
        f"0x{RSE_BOOT_FLASH_STORAGE_SIZE:x}"
    )


def append_env_csv(env: dict[str, str], key: str, value: str) -> None:
    existing = env.get(key, "").strip()
    env[key] = f"{existing},{value}" if existing else value


def direct_file_alias_entry(
    address: int, size: int, file_offset: int, access: str, path: Path
) -> str:
    return f"0x{address:x}:0x{size:x}:0x{file_offset:x}:{access}:{path}"


def round_up(value: int, alignment: int) -> int:
    return ((value + alignment - 1) // alignment) * alignment


def rse_si_payload_alias_size(
    flash_path: Path | None, offsets: list[int], override_size: int
) -> int:
    if override_size > 0:
        return override_size
    if flash_path is None or not flash_path.exists():
        return HOST_SI_IMG_CODE_ALIAS_SIZE_FALLBACK

    try:
        flash = flash_path.read_bytes()
    except OSError:
        return HOST_SI_IMG_CODE_ALIAS_SIZE_FALLBACK

    payload_sizes: list[int] = []
    for offset in offsets:
        image_info = parse_mcuboot_ram_load_size(flash, offset)
        boot_size_hex = image_info.get("boot_read_image_size")
        if not image_info.get("valid") or not isinstance(boot_size_hex, str):
            continue
        boot_size = int(boot_size_hex, 16)
        payload_sizes.append(max(0, boot_size - HOST_SI_IMG_HEADER_ALIAS_SIZE))

    if not payload_sizes:
        return HOST_SI_IMG_CODE_ALIAS_SIZE_FALLBACK
    return round_up(max(payload_sizes), 0x1000)


def rse_ap_bl2_payload_alias_size(
    flash_path: Path | None, override_size: int
) -> int:
    if override_size > 0:
        return override_size
    if flash_path is None or not flash_path.exists():
        return HOST_AP_BL2_IMG_CODE_ALIAS_SIZE_FALLBACK

    try:
        flash = flash_path.read_bytes()
    except OSError:
        return HOST_AP_BL2_IMG_CODE_ALIAS_SIZE_FALLBACK

    magic = IMAGE_MAGIC.to_bytes(4, "little")
    payload_sizes: list[int] = []
    start = 0
    while True:
        offset = flash.find(magic, start)
        if offset < 0:
            break
        image_info = parse_mcuboot_ram_load_size(flash, offset)
        boot_size_hex = image_info.get("boot_read_image_size")
        if (
            image_info.get("valid")
            and image_info.get("load_addr") == hex(HOST_AP_BL2_IMG_HDR_LOGICAL_BASE)
            and isinstance(boot_size_hex, str)
        ):
            boot_size = int(boot_size_hex, 16)
            payload_sizes.append(max(0, boot_size - HOST_AP_BL2_IMG_HEADER_ALIAS_SIZE))
        start = offset + 1

    if not payload_sizes:
        return HOST_AP_BL2_IMG_CODE_ALIAS_SIZE_FALLBACK
    return round_up(max(payload_sizes), 0x1000)


def mcuboot_read_alias_ranges(
    flash_path: Path | None, offsets: list[int]
) -> list[tuple[int, int]]:
    if flash_path is None or not flash_path.exists():
        return []

    try:
        flash = flash_path.read_bytes()
    except OSError:
        return []

    ranges: list[tuple[int, int]] = []
    for offset in offsets:
        image_info = parse_mcuboot_ram_load_size(flash, offset)
        boot_size_hex = image_info.get("boot_read_image_size")
        if not image_info.get("valid") or not isinstance(boot_size_hex, str):
            continue
        boot_size = int(boot_size_hex, 16)
        ranges.append((offset, round_up(boot_size, 0x1000)))
    return ranges


def rse_boot_flash_direct_read_ranges(
    flash_path: Path | None,
) -> list[tuple[str, int, int]]:
    if flash_path is None or not flash_path.exists():
        return []

    ranges: list[tuple[str, int, int]] = [
        (
            "pre_primary_scan",
            RSE_BOOT_FLASH_PRE_PRIMARY_SCAN_OFFSET,
            RSE_BOOT_FLASH_PRE_PRIMARY_SCAN_SIZE,
        )
    ]
    ranges.extend(
        (f"mcuboot_slot_{offset:x}", offset, size)
        for offset, size in mcuboot_read_alias_ranges(
            flash_path, RSE_BOOT_FLASH_IMAGE_SLOT_OFFSETS
        )
    )
    return ranges


def rse_direct_rse_flash_alias_spec(artifacts: dict[str, Path]) -> str:
    rse_flash = artifacts.get("rse_flash")
    if rse_flash is None:
        return ""
    return ";".join(
        direct_file_alias_entry(
            RSE_BOOT_FLASH_BASE_S + offset,
            size,
            offset,
            "ro",
            rse_flash,
        )
        for _, offset, size in rse_boot_flash_direct_read_ranges(rse_flash)
    )


def rse_direct_ap_fip_alias_spec(artifacts: dict[str, Path]) -> str:
    ap_flash = artifacts.get("ap_flash")
    if ap_flash is None or not ap_flash.exists():
        return ""
    return direct_file_alias_entry(
        HOST_AP_FLASH_LOGICAL_BASE + AP_FLASH_FIP_PRIMARY_OFFSET,
        AP_FLASH_FIP_SIZE,
        AP_FLASH_FIP_PRIMARY_OFFSET,
        "ro",
        ap_flash,
    )


def rse_direct_si_sram_alias_spec(
    artifacts: dict[str, Path], code_alias_size: int
) -> str:
    rse_flash = artifacts.get("rse_flash")
    cl0_code_alias_size = rse_si_payload_alias_size(
        rse_flash,
        [SI_CL0_PRIMARY_FLASH_OFFSET, SI_CL0_SECONDARY_FLASH_OFFSET],
        code_alias_size,
    )
    cl1_code_alias_size = rse_si_payload_alias_size(
        rse_flash,
        [SI_CL1_PRIMARY_FLASH_OFFSET, SI_CL1_SECONDARY_FLASH_OFFSET],
        code_alias_size,
    )
    return ";".join(
        [
            direct_file_alias_entry(
                HOST_SI_CL0_IMG_HDR_LOGICAL_BASE,
                HOST_SI_IMG_HEADER_ALIAS_SIZE,
                HOST_SI_CL0_HEADER_FILE_OFFSET,
                "rw",
                artifacts["host_si_cl0_sram"],
            ),
            direct_file_alias_entry(
                HOST_SI_CL0_IMG_CODE_LOGICAL_BASE,
                cl0_code_alias_size,
                HOST_SI_CL0_CODE_FILE_OFFSET,
                "rw",
                artifacts["host_si_cl0_sram"],
            ),
            direct_file_alias_entry(
                HOST_SI_CL1_IMG_HDR_LOGICAL_BASE,
                HOST_SI_IMG_HEADER_ALIAS_SIZE,
                HOST_SI_CL1_HEADER_FILE_OFFSET,
                "rw",
                artifacts["host_si_cl1_sram"],
            ),
            direct_file_alias_entry(
                HOST_SI_CL1_IMG_CODE_LOGICAL_BASE,
                cl1_code_alias_size,
                HOST_SI_CL1_CODE_FILE_OFFSET,
                "rw",
                artifacts["host_si_cl1_sram"],
            ),
        ]
    )


def rse_direct_ap_bl2_alias_spec(
    artifacts: dict[str, Path], code_alias_size: int
) -> str:
    ap_flash = artifacts.get("ap_flash")
    ap_bl2_code_alias_size = rse_ap_bl2_payload_alias_size(
        ap_flash, code_alias_size
    )
    return ";".join(
        [
            direct_file_alias_entry(
                HOST_AP_BL2_IMG_HDR_LOGICAL_BASE,
                HOST_AP_BL2_IMG_HEADER_ALIAS_SIZE,
                HOST_AP_BL2_HEADER_FILE_OFFSET,
                "rw",
                artifacts["host_ap_bl2_header_sram"],
            ),
            direct_file_alias_entry(
                HOST_AP_BL2_IMG_CODE_LOGICAL_BASE,
                ap_bl2_code_alias_size,
                HOST_AP_BL2_CODE_FILE_OFFSET,
                "rw",
                artifacts["host_ap_shared_sram"],
            ),
        ]
    )


def rse_direct_file_aliases_for_args(
    args: argparse.Namespace, artifacts: dict[str, Path]
) -> str:
    if args.rse_direct_file_aliases:
        return args.rse_direct_file_aliases

    specs: list[str] = []
    if args.rse_direct_si_sram_alias:
        specs.append(
            rse_direct_si_sram_alias_spec(
                artifacts, args.rse_direct_si_sram_code_alias_size
            )
        )
    if args.rse_direct_ap_bl2_alias:
        specs.append(
            rse_direct_ap_bl2_alias_spec(
                artifacts, args.rse_direct_ap_bl2_code_alias_size
            )
        )
    if args.rse_direct_rse_flash_alias:
        specs.append(rse_direct_rse_flash_alias_spec(artifacts))
    if args.rse_direct_ap_fip_alias:
        specs.append(rse_direct_ap_fip_alias_spec(artifacts))
    return ";".join(spec for spec in specs if spec)


def rse_fast_boot_sram_dmi_result(args: argparse.Namespace) -> dict[str, object]:
    dmi_env = {
        "QBOX_RDASPEN_ATU_DMI": "true" if args.range_limited_flash_dmi else "",
        "QBOX_RDASPEN_HOST_MEMORY_DMI": "true" if args.range_limited_flash_dmi else "",
        "QBOX_RDASPEN_HOST_SI_SRAM_DMI": (
            "true" if args.rse_fast_boot_sram_dmi else ""
        ),
        "QBOX_RDASPEN_HOST_SRAM_SHARED_MEMORY": (
            "true" if args.rse_fast_boot_sram_dmi else ""
        ),
    }
    forbidden_effective_env = {name: "" for name in SRAM_DMI_FORBIDDEN_ENV}
    return {
        "enabled": bool(args.rse_fast_boot_sram_dmi),
        "host_sram_shared_memory": bool(args.rse_fast_boot_sram_dmi),
        "range_limited_flash_dmi": bool(args.range_limited_flash_dmi),
        "legacy_fast_boot_aliases_blocked": bool(args.rse_fast_boot_sram_dmi),
        "env": dmi_env,
        "forbidden_ambient_env": forbidden_effective_env,
    }


def ap_fip_logical_aperture_result(args: argparse.Namespace) -> dict[str, object]:
    return {
        "enabled": False,
        "mode": "atu_systemc_route",
        "direct_file_alias": False,
        "scope_plan": "",
        "fidelity_note": "",
    }


def rse_direct_file_aliases_summary(args: argparse.Namespace) -> dict[str, object]:
    return {
        "enabled": bool(
            args.rse_direct_si_sram_alias
            or args.rse_direct_ap_bl2_alias
            or args.rse_direct_rse_flash_alias
            or args.rse_direct_ap_fip_alias
            or args.rse_direct_file_aliases
        ),
        "fast_boot_aliases_preset": bool(args.rse_fast_boot_aliases),
        "si_sram": bool(args.rse_direct_si_sram_alias),
        "ap_bl2": bool(args.rse_direct_ap_bl2_alias),
        "rse_boot_flash": bool(args.rse_direct_rse_flash_alias),
        "ap_fip": bool(args.rse_direct_ap_fip_alias),
        "raw_spec_present": bool(args.rse_direct_file_aliases),
    }


def host_sram_backing_entry(
    *,
    path: Path | None,
    shared_memory: bool,
    dmi_allow: bool,
    size: int,
) -> dict[str, object]:
    file_created = bool(path is not None and path.exists())
    if path is not None:
        mode = "map_file"
    elif shared_memory:
        mode = "shared_memory"
    elif size > 0:
        mode = "allocated"
    else:
        mode = "not_present"
    return {
        "mode": mode,
        "map_file": str(path) if path is not None else None,
        "shared_memory": shared_memory,
        "dmi_allow": dmi_allow,
        "file_created": file_created,
        "size": size,
    }


def host_sram_backing_result(
    args: argparse.Namespace, runtime_artifacts: dict[str, Path]
) -> dict[str, object]:
    shared_memory = bool(args.rse_fast_boot_sram_dmi)
    host_memory_dmi = bool(args.range_limited_flash_dmi)
    host_si_sram_dmi = bool(args.rse_fast_boot_sram_dmi)
    return {
        "host_si_cl0_sram": host_sram_backing_entry(
            path=runtime_artifacts.get("host_si_cl0_sram"),
            shared_memory=shared_memory,
            dmi_allow=host_si_sram_dmi,
            size=HOST_SI_CL0_SRAM_WINDOW_SIZE,
        ),
        "host_si_cl1_sram": host_sram_backing_entry(
            path=runtime_artifacts.get("host_si_cl1_sram"),
            shared_memory=shared_memory,
            dmi_allow=host_si_sram_dmi,
            size=HOST_SI_CL1_SRAM_WINDOW_SIZE,
        ),
        "host_ap_shared_sram": host_sram_backing_entry(
            path=runtime_artifacts.get("host_ap_shared_sram"),
            shared_memory=shared_memory,
            dmi_allow=host_memory_dmi,
            size=HOST_AP_SHARED_SRAM_SIZE,
        ),
        "host_ap_bl2_header_sram": host_sram_backing_entry(
            path=runtime_artifacts.get("host_ap_bl2_header_sram"),
            shared_memory=shared_memory,
            dmi_allow=host_memory_dmi,
            size=HOST_AP_BL2_HEADER_SRAM_SIZE,
        ),
    }


def default_bl2_map(root: Path) -> Path:
    return (
        root
        / "build/tmp_baremetal/work/fvp_rd_aspen-poky-linux"
        / "trusted-firmware-m/2.2.2+git/build/bin/bl2.map"
    )


def default_rse_bl2_elf(root: Path) -> Path:
    return (
        root
        / "build/tmp_baremetal/work/fvp_rd_aspen-poky-linux"
        / "trusted-firmware-m/2.2.2+git/build/bin/bl2.elf"
    )


def default_rse_bl1_2_elf(root: Path) -> Path:
    return (
        root
        / "build/tmp_baremetal/work/fvp_rd_aspen-poky-linux"
        / "trusted-firmware-m/2.2.2+git/build/bin/bl1_2.elf"
    )


def default_bl1_1_map(root: Path) -> Path:
    return (
        root
        / "build/tmp_baremetal/work/fvp_rd_aspen-poky-linux"
        / "trusted-firmware-m/2.2.2+git/build/bin/bl1_1.map"
    )


def parse_map_text_ranges(map_path: Path, symbols: list[str]) -> dict[str, dict[str, int]]:
    if not map_path.exists():
        return {}

    wanted = set(symbols)
    ranges: dict[str, dict[str, int]] = {}
    current_symbol: str | None = None
    for line in map_path.read_text(encoding="utf-8", errors="replace").splitlines():
        section = MAP_TEXT_SECTION_RE.match(line)
        if section:
            symbol = section.group("symbol")
            current_symbol = symbol if symbol in wanted else None
            continue

        if current_symbol is None:
            continue
        section_range = MAP_SECTION_RANGE_RE.match(line)
        if not section_range:
            continue
        start = int(section_range.group("start"), 16)
        size = int(section_range.group("size"), 16)
        ranges[current_symbol] = {"start": start, "end": start + size, "size": size}
        current_symbol = None
    return ranges


def parse_elf_symbols(elf_path: Path, symbols: list[str]) -> dict[str, int]:
    if not elf_path.exists():
        return {}

    nm = shutil.which("llvm-nm") or shutil.which("nm")
    if nm is None:
        return {}

    proc = subprocess.run(
        [nm, "-n", str(elf_path)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if proc.returncode != 0:
        return {}

    wanted = set(symbols)
    found: dict[str, int] = {}
    for line in proc.stdout.splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        value, _kind, name = parts[:3]
        if name not in wanted:
            continue
        try:
            found[name] = int(value, 16)
        except ValueError:
            continue
    return found


def resolve_rse_bl2_hook_symbols(args: argparse.Namespace, root: Path) -> None:
    if args.rse_bl2_elf is None:
        args.rse_bl2_elf = default_rse_bl2_elf(root)
    else:
        args.rse_bl2_elf = args.rse_bl2_elf.resolve()

    parsed = parse_elf_symbols(args.rse_bl2_elf, list(RSE_BL2_SYMBOL_DEFAULTS))
    resolved: dict[str, int] = {}
    missing: list[str] = []
    for attr, symbol in RSE_BL2_HOOK_SYMBOLS.items():
        explicit = getattr(args, attr)
        if explicit is not None:
            value = explicit
        elif symbol in parsed:
            value = parsed[symbol]
        else:
            value = RSE_BL2_SYMBOL_DEFAULTS[symbol]
            missing.append(symbol)
        if explicit is None and symbol == "delay_cycles":
            value += 2
        setattr(args, attr, value)
        resolved[symbol] = value

    libc_resolved: dict[str, int] = {}
    libc_missing: list[str] = []
    if args.rse_bl2_libc_hotpath:
        args.rse_hotpath_accel = True
        for attr, symbol in RSE_BL2_LIBC_HOTPATH_SYMBOLS.items():
            explicit = getattr(args, attr)
            if explicit is not None:
                value = explicit
            elif symbol in parsed:
                value = parsed[symbol]
            else:
                value = RSE_BL2_SYMBOL_DEFAULTS[symbol]
                libc_missing.append(symbol)
            setattr(args, attr, value)
            libc_resolved[symbol] = value

    args.rse_bl2_symbol_source = {
        "elf": str(args.rse_bl2_elf),
        "elf_exists": args.rse_bl2_elf.exists(),
        "parsed": bool(parsed),
        "missing": missing,
        "resolved": {name: hex(value) for name, value in sorted(resolved.items())},
        "libc_hotpath": {
            "enabled": bool(args.rse_bl2_libc_hotpath),
            "missing": libc_missing,
            "resolved": {
                name: hex(value) for name, value in sorted(libc_resolved.items())
            },
        },
    }


def resolve_rse_bl1_2_lms_symbol(args: argparse.Namespace, root: Path) -> None:
    if args.rse_bl1_2_elf is None:
        if args.rse_bl2_elf is not None:
            sibling = args.rse_bl2_elf.with_name("bl1_2.elf")
            args.rse_bl1_2_elf = sibling if sibling.exists() else default_rse_bl1_2_elf(root)
        else:
            args.rse_bl1_2_elf = default_rse_bl1_2_elf(root)
    else:
        args.rse_bl1_2_elf = args.rse_bl1_2_elf.resolve()

    symbol = "pq_crypto_verify"
    parsed = parse_elf_symbols(args.rse_bl1_2_elf, list(RSE_BL1_2_SYMBOL_DEFAULTS))
    explicit = args.rse_lms_verify_addr
    if explicit is not None:
        value = explicit
        missing: list[str] = []
    elif symbol in parsed:
        value = parsed[symbol]
        missing = []
    else:
        value = RSE_BL1_2_SYMBOL_DEFAULTS[symbol]
        missing = [symbol]

    args.rse_lms_verify_addr = value
    args.rse_bl1_2_symbol_source = {
        "elf": str(args.rse_bl1_2_elf),
        "elf_exists": args.rse_bl1_2_elf.exists(),
        "parsed": bool(parsed),
        "missing": missing,
        "resolved": {symbol: hex(value)},
    }


def default_boot_enc_trace_filter(root: Path) -> str | None:
    ranges = parse_map_text_ranges(default_bl2_map(root), BOOT_ENC_TRACE_SYMBOLS)
    if not ranges:
        return None

    start = min(item["start"] for item in ranges.values())
    end = max(item["end"] for item in ranges.values())
    return f"0x{start:x}+0x{end - start:x}"


def qemu_trace_args(root: Path, args: argparse.Namespace) -> str | None:
    if not qemu_trace_enabled(args):
        return None

    trace_filter = args.qemu_trace_filter
    if args.boot_enc_trace and not trace_filter:
        trace_filter = default_boot_enc_trace_filter(root)

    parts = [
        "-D",
        str(args.out_dir / QEMU_TRACE_LOG),
        "-d",
        args.qemu_trace_events,
    ]
    if trace_filter:
        parts.extend(["-dfilter", trace_filter])
    return " ".join(parts)


def parse_boot_enc_trace(root: Path, out_dir: Path, enabled: bool) -> dict[str, object] | None:
    if not enabled:
        return None

    trace_path = out_dir / QEMU_TRACE_LOG
    result: dict[str, object] = {
        "enabled": True,
        "trace_log": str(trace_path.resolve()),
        "bl2_map": str(default_bl2_map(root).resolve()),
    }
    if not trace_path.exists():
        result["present"] = False
        result["classification"] = "missing_qemu_trace_log"
        return result

    ranges = parse_map_text_ranges(default_bl2_map(root), BOOT_ENC_TRACE_SYMBOLS)
    result["present"] = True
    result["symbol_ranges"] = {
        symbol: {
            "start": f"0x{item['start']:x}",
            "end": f"0x{item['end']:x}",
            "size": f"0x{item['size']:x}",
        }
        for symbol, item in ranges.items()
    }
    if not ranges:
        result["classification"] = "missing_bl2_symbol_ranges"
        return result

    hit_counts = {symbol: 0 for symbol in ranges}
    first_hits: dict[str, str] = {}
    sampled_addresses: list[str] = []
    trace_address_count = 0
    for line in trace_path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = QEMU_IN_ASM_ADDR_RE.match(line)
        if not match:
            continue
        trace_address_count += 1
        addr = int(match.group(1), 16)
        for symbol, item in ranges.items():
            if item["start"] <= addr < item["end"]:
                hit_counts[symbol] += 1
                first_hits.setdefault(symbol, f"0x{addr:x}")
                if len(sampled_addresses) < 64:
                    sampled_addresses.append(f"0x{addr:x}")
                break

    result["trace_address_count"] = trace_address_count
    result["hit_counts"] = hit_counts
    result["first_hits"] = first_hits
    result["sampled_addresses"] = sampled_addresses
    result["control_flow_note"] = (
        "ram_load.c calls boot_enc_set_key() only when boot_enc_load() returns 0."
    )

    if hit_counts.get("boot_enc_set_key", 0):
        if hit_counts.get("boot_enc_decrypt", 0):
            classification = "boot_enc_set_key_and_decrypt_reached"
        else:
            classification = "boot_enc_set_key_reached_before_failure"
    elif hit_counts.get("boot_decrypt_key", 0) or hit_counts.get(
        "bootutil_aes_kw_unwrap", 0
    ):
        classification = "boot_enc_load_decrypt_key_failed_before_set_key"
    elif hit_counts.get("boot_enc_load", 0):
        classification = "boot_enc_load_failed_before_decrypt_key"
    else:
        classification = "no_boot_enc_trace_hits"
    result["classification"] = classification
    return result


def parse_platform_translation_error(out_dir: Path) -> dict[str, str] | None:
    platform_log = out_dir / PLATFORM_STDOUT_LOG
    if not platform_log.exists():
        return None

    for line in platform_log.read_text(encoding="utf-8", errors="replace").splitlines():
        match = ATU_TRANSLATION_ERROR_RE.search(line)
        if not match:
            continue
        return {
            "source": "platform_log",
            "component": match.group("component"),
            "access": f"translate_{match.group('command')}",
            "logical_address": match.group("logical").lower(),
            "physical_address": match.group("physical").lower(),
            "length": match.group("length").lower(),
        }
    return None


def parse_trace_value(value: str) -> int | str:
    if value.startswith("0x"):
        return value.lower()
    return int(value)


def armv7m_exception_name(exception: int) -> str:
    if exception >= 16:
        return f"IRQ{exception - 16}"
    return ARMV7M_EXCEPTIONS.get(exception, f"Exception{exception}")


def parse_cpu_pc_trace(
    out_dir: Path, enabled: bool, filename: str, role: str
) -> dict[str, object] | None:
    if not enabled:
        return None
    trace_path = out_dir / filename
    if not trace_path.exists():
        return {
            "enabled": True,
            "role": role,
            "trace_log": str(trace_path.resolve()),
            "present": False,
        }

    samples: list[dict[str, object]] = []
    line_count = 0
    for line in trace_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line_count += 1
        match = PC_TRACE_RE.search(line)
        if not match:
            continue
        sample: dict[str, object] = {
            "sample": int(match.group("sample")),
            "seen": int(match.group("seen")),
            "sc_time": match.group("sc_time"),
            "vclock_ns": int(match.group("vclock_ns")),
            "pc": match.group("pc").lower(),
            "mem_io_pc": match.group("mem_io_pc").lower(),
        }
        component = match.group("component")
        if component:
            sample["component"] = component
        exception_state = {
            kv.group("key"): parse_trace_value(kv.group("value"))
            for kv in TRACE_KV_RE.finditer(match.group("extra"))
        }
        exception = exception_state.get("exception")
        if isinstance(exception, int):
            exception_state["exception_name"] = armv7m_exception_name(exception)
        if exception_state:
            sample["exception_state"] = exception_state
        samples.append(sample)

    if not samples:
        return {
            "enabled": True,
            "role": role,
            "trace_log": str(trace_path.resolve()),
            "present": True,
            "line_count": line_count,
            "sample_count": 0,
        }

    unique_tail = []
    last_samples_by_component: dict[str, dict[str, object]] = {}
    component_counts: dict[str, int] = {}
    for sample in samples:
        component = str(sample.get("component", "unknown"))
        last_samples_by_component[component] = sample
        component_counts[component] = component_counts.get(component, 0) + 1
    for sample in samples[-32:]:
        pc = sample["pc"]
        if pc not in unique_tail:
            unique_tail.append(pc)

    result: dict[str, object] = {
        "enabled": True,
        "role": role,
        "trace_log": str(trace_path.resolve()),
        "present": True,
        "line_count": line_count,
        "sample_count": len(samples),
        "component_counts": component_counts,
        "first_sample": samples[0],
        "last_sample": samples[-1],
        "last_samples_by_component": last_samples_by_component,
        "tail_unique_pcs": unique_tail,
    }
    last_exception_state = samples[-1].get("exception_state")
    if isinstance(last_exception_state, dict):
        result["last_exception_state"] = last_exception_state
    return result


def parse_rse_pc_trace(out_dir: Path, enabled: bool) -> dict[str, object] | None:
    return parse_cpu_pc_trace(out_dir, enabled, RSE_PC_TRACE_LOG, "rse")


def parse_ap_pc_trace(out_dir: Path, enabled: bool) -> dict[str, object] | None:
    return parse_cpu_pc_trace(out_dir, enabled, AP_PC_TRACE_LOG, "ap")


def classify_pc_trace_blocker(
    root: Path,
    rse_pc_trace: dict[str, object] | None,
    timed_out: bool,
) -> str | None:
    if not rse_pc_trace:
        return None
    last_sample = rse_pc_trace.get("last_sample")
    if not isinstance(last_sample, dict):
        return None
    pc = last_sample.get("pc")
    exception_state = last_sample.get("exception_state")
    exception = None
    if isinstance(exception_state, dict):
        exception = exception_state.get("exception")
    if pc == "0x3101d80c" and isinstance(exception, int) and exception != 0:
        return "bl2_exception_handler_after_psa_crypto"
    if isinstance(exception, int) and exception != 0:
        name = armv7m_exception_name(exception).lower()
        return f"rse_exception:{name}"
    if timed_out and isinstance(pc, str):
        try:
            pc_value = int(pc, 16)
        except ValueError:
            return None
        ranges = parse_map_text_ranges(default_bl2_map(root), RSE_BL2_CFI_TRACE_SYMBOLS)
        for symbol, item in ranges.items():
            if item["start"] <= pc_value < item["end"]:
                return f"rse_bl2_cfi_flash_io_timeout:{symbol}"
        ranges = parse_map_text_ranges(default_bl1_1_map(root), RSE_BL1_1_TRACE_SYMBOLS)
        for symbol, item in ranges.items():
            if item["start"] <= pc_value < item["end"]:
                if symbol.startswith("cfi_") or symbol.startswith("nor_"):
                    return f"rse_bl1_1_cfi_flash_io_timeout:{symbol}"
                return f"rse_bl1_1_cc3xx_crypto_timeout:{symbol}"
    return None


def classify_boot_enc_trace_blocker(
    logs: dict[str, str], boot_enc_trace: dict[str, object] | None
) -> str | None:
    if not boot_enc_trace:
        return None

    combined = clean_text("\n".join(logs.values()))
    if "Image 3 RAM loading to 0x70083c00 is failed." not in combined:
        return None

    classification = boot_enc_trace.get("classification")
    if classification in (
        "boot_enc_load_decrypt_key_failed_before_set_key",
        "boot_enc_load_failed_before_decrypt_key",
        "boot_enc_set_key_reached_before_failure",
        "boot_enc_set_key_and_decrypt_reached",
    ):
        return f"si_cl0_{classification}"
    return None


def write_placeholder_logs(out_dir: Path, reason: str) -> dict[str, str]:
    logs: dict[str, str] = {}
    for role, filename in CONSOLE_LOGS.items():
        path = out_dir / filename
        text = (
            f"QBox Apollo RSE-oriented boot did not start.\n"
            f"console: {role}\n"
            f"reason: {reason}\n"
        )
        path.write_text(text, encoding="utf-8")
        logs[role] = text
    return logs


def probe_requires_ap_cpus(args: argparse.Namespace) -> bool:
    return bool(
        args.post_login_probe
        or args.secure_service_probe
        or args.fwu_probe
        or args.primary_operation_manifest is not None
    )


def env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


RUNNER_CONTROL_ENV = (
    "QBOX_RDASPEN_RESULT_PATH",
    "QBOX_RDASPEN_SUMMARY_PATH",
)
REMOVED_RUNNER_ENV = (
    "QBOX_RSE_CPU_MODE",
    "QBOX_REMOTE_CPU_EXEC",
    "QBOX_RDASPEN_REMOTEPASS_DMI_CACHE",
    "QBOX_RDASPEN_RSE_HOTPATH_TLM_FALLBACK",
)


def strip_runner_control_env(env: dict[str, str]) -> dict[str, str]:
    for name in RUNNER_CONTROL_ENV + REMOVED_RUNNER_ENV:
        env.pop(name, None)
    return env


def parse_int_auto(value: str) -> int | None:
    try:
        return int(value, 0)
    except ValueError:
        return None


def qbox_platform_param_value(param: str) -> str:
    key, sep, value = param.partition("=")
    if not sep:
        return param

    parsed = parse_int_auto(value.strip())
    if parsed is None:
        return param

    return f"{key}={parsed}"


def is_blank_file(path: Path) -> bool:
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                return True
            if any(chunk):
                return False


def rse_lcm_uses_se_fast_path(args: argparse.Namespace) -> bool:
    lcs = os.environ.get("QBOX_RDASPEN_RSE_LCM_LCS", "").strip()
    for param in args.platform_param:
        if param.startswith("platform.rse_lcm_regs.lcs="):
            lcs = param.split("=", 1)[1].strip()

    if not lcs:
        return True

    value = parse_int_auto(lcs)
    return value is None or value == 0xEEEEA5A5


def apply_primary_console_profile(args: argparse.Namespace) -> None:
    REQUIRED_MARKERS["linux_boot"] = [
        args.primary_login_prompt,
        args.primary_shell_marker,
    ]
    PROGRESS_MARKERS["primary_login_prompt"] = args.primary_login_prompt
    PROGRESS_MARKERS["primary_root_shell"] = args.primary_shell_marker
    LOGIN_READY_PATTERNS[:] = [
        re.escape(args.primary_login_prompt),
        r"Started .*Serial Getty on ttyAMA0",
        r"Reached target .*Login Prompts",
    ]


def qbox_env(root: Path, args: argparse.Namespace, artifacts: dict[str, Path]) -> dict[str, str]:
    env = strip_runner_control_env(os.environ.copy())
    if args.rse_fast_boot_sram_dmi:
        for name in SRAM_DMI_FORBIDDEN_ENV:
            env.pop(name, None)
    build_dir = qbox_build_dir(root)
    lib_paths = [build_dir, *installed_provider_library_paths(build_dir)]
    lib_paths.extend([
        build_dir / "lib",
        build_dir / "qbox-core",
        build_dir / "_deps/report-build",
        build_dir / "_deps/fmt-build",
        build_dir / "_deps/systemccci-build/configuration/src",
        build_dir / "_deps/systemccci-build/inspection/src",
        build_dir / "_deps/systemclanguage-build/src",
        build_dir / "_deps/rpclib-build",
        build_dir / "_deps/libqemu-build/qemu-prefix/lib",
        *installed_libqemu_library_paths(build_dir),
    ])
    current = env.get("LD_LIBRARY_PATH")
    if current:
        lib_paths.append(Path(current))
    env["LD_LIBRARY_PATH"] = ":".join(str(path) for path in lib_paths)
    if probe_requires_ap_cpus(args):
        env["QBOX_RDASPEN_ENABLE_AP_CPUS"] = "true"
    env["QBOX_RDASPEN_RSE_ROM"] = str(artifacts["rse_rom"])
    env["QBOX_RDASPEN_RSE_FLASH"] = str(artifacts["rse_flash"])
    env["QBOX_RDASPEN_RSE_OTP"] = str(artifacts["rse_otp"])
    env["QBOX_RDASPEN_RSE_OTP_WRITEBACK"] = (
        "false" if args.no_copy_writable_flash else "true"
    )
    env["QBOX_RDASPEN_FLASH_WRITEBACK"] = (
        "false" if args.no_copy_writable_flash else "true"
    )
    env["QBOX_RDASPEN_RSE_FLASH_BACKEND"] = args.rse_flash_backend
    env["QBOX_RDASPEN_SMMU_BACKEND"] = args.smmu_backend
    env["QBOX_RDASPEN_AP_FLASH"] = str(artifacts["ap_flash"])
    if args.ap_bl2_elf:
        env["QBOX_RDASPEN_AP_BL2_ELF"] = str(args.ap_bl2_elf)
    env["QBOX_RDASPEN_ROOTFS"] = str(artifacts["rootfs"])
    for index in range(1, 4):
        artifact_name = f"extra_blk{index}"
        if artifact_name in artifacts:
            env[f"QBOX_RDASPEN_EXTRA_BLK{index}"] = str(artifacts[artifact_name])
    if "host_si_cl0_sram" in artifacts:
        env["QBOX_RDASPEN_HOST_SI_CL0_SRAM_MAP_FILE"] = str(
            artifacts["host_si_cl0_sram"]
        )
    if "host_si_cl1_sram" in artifacts:
        env["QBOX_RDASPEN_HOST_SI_CL1_SRAM_MAP_FILE"] = str(
            artifacts["host_si_cl1_sram"]
        )
    if "host_ap_shared_sram" in artifacts:
        env["QBOX_RDASPEN_HOST_AP_SHARED_SRAM_MAP_FILE"] = str(
            artifacts["host_ap_shared_sram"]
        )
    if "host_ap_bl2_header_sram" in artifacts:
        env["QBOX_RDASPEN_HOST_AP_BL2_HEADER_SRAM_MAP_FILE"] = str(
            artifacts["host_ap_bl2_header_sram"]
        )
    env["QBOX_RDASPEN_PROVISIONING_BUNDLE"] = str(artifacts["provisioning_bundle"])
    env["QBOX_RDASPEN_RSE_SCP_STRATEGY"] = args.scp_strategy
    env["QBOX_RDASPEN_RSE_LOG"] = str(args.out_dir / CONSOLE_LOGS["rse"])
    env["QBOX_RDASPEN_SCP_LOG"] = str(args.out_dir / CONSOLE_LOGS["scp"])
    env["QBOX_RDASPEN_SECURE_CONSOLE_LOG"] = str(
        args.out_dir / CONSOLE_LOGS["secure_console"]
    )
    env["QBOX_RDASPEN_PRIMARY_CONSOLE_LOG"] = str(
        args.out_dir / CONSOLE_LOGS["primary_console"]
    )
    env.setdefault("QBOX_RDASPEN_UART_READ_FILE", os.devnull)
    extra_qemu_args = qemu_trace_args(root, args)
    if extra_qemu_args:
        env["QBOX_RDASPEN_RSE_QEMU_ARGS"] = extra_qemu_args
    if args.range_limited_flash_dmi:
        env.update(RANGE_LIMITED_FLASH_DMI_DEFAULTS)
    if args.rse_fast_boot_sram_dmi:
        env["QBOX_RDASPEN_HOST_SI_SRAM_DMI"] = "true"
        env["QBOX_RDASPEN_HOST_SRAM_SHARED_MEMORY"] = "true"
    if args.cc3xx_stats or args.qbox_perf_profile:
        env["QBOX_RDASPEN_CC3XX_STATS_FILE"] = str(
            args.out_dir / RSE_CC3XX_STATS
        )
        env["QBOX_RDASPEN_CC3XX_STATS_INTERVAL"] = str(
            args.cc3xx_stats_interval
        )
    if args.qbox_perf_profile:
        profile_root = args.out_dir / QBOX_PERF_PROFILE_DIR
        qemu_initiator_dir = profile_root / QEMU_INITIATOR_PROFILE_DIR
        qemu_initiator_dir.mkdir(parents=True, exist_ok=True)
        env["QBOX_QEMU_INITIATOR_PROFILE_DIR"] = str(qemu_initiator_dir)
        env["QBOX_CC3XX_PROFILE_FILE"] = str(profile_root / CC3XX_PROFILE)
        env["QBOX_CC3XX_TIMING_STATS"] = "1"
        env["QBOX_PROFILE_FLUSH_INTERVAL"] = str(args.qbox_perf_profile_interval)
        if (
            args.rse_hotpath_accel
            or args.rse_lms_accel
            or args.rse_bl2_load_profile
            or args.rse_bl2_load_accel
            or args.rse_bl2_boot_enc_accel
            or args.rse_bl2_img_hash_accel
            or args.rse_bl2_verify_sig_accel
            or args.rse_bl2_delay_accel
        ):
            env["QBOX_RDASPEN_RSE_HOTPATH_PROFILE_FILE"] = str(
                profile_root / RSE_HOTPATH_PROFILE
            )
            env["QBOX_RDASPEN_RSE_HOTPATH_PROFILE_INTERVAL"] = str(
                args.qbox_perf_profile_interval
            )
    if args.rse_hotpath_accel:
        env["QBOX_RDASPEN_RSE_HOTPATH_ACCEL"] = "true"
        env["QBOX_RDASPEN_RSE_HOTPATH_MAX_BYTES"] = str(
            args.rse_hotpath_max_bytes
        )
        if args.rse_hotpath_memcpy_addr is not None:
            env["QBOX_RDASPEN_RSE_HOTPATH_MEMCPY_ADDR"] = str(
                args.rse_hotpath_memcpy_addr
            )
        if args.rse_hotpath_memset_addr is not None:
            env["QBOX_RDASPEN_RSE_HOTPATH_MEMSET_ADDR"] = str(
                args.rse_hotpath_memset_addr
            )
    if args.rse_lms_accel:
        env["QBOX_RDASPEN_RSE_LMS_ACCEL"] = "true"
        env["QBOX_RDASPEN_RSE_LMS_VERIFY_ADDR"] = str(
            args.rse_lms_verify_addr
        )
        env["QBOX_RDASPEN_RSE_LMS_MAX_DATA_BYTES"] = str(
            args.rse_lms_max_data_bytes
        )
    if args.rse_bl2_load_profile:
        env["QBOX_RDASPEN_RSE_BL2_LOAD_PROFILE"] = "true"
    if (
        args.rse_bl2_load_profile
        or args.rse_bl2_load_accel
        or args.rse_bl2_boot_enc_accel
        or args.rse_bl2_img_hash_accel
        or args.rse_bl2_verify_sig_accel
        or args.rse_bl2_delay_accel
    ):
        env["QBOX_RDASPEN_RSE_BL2_BOOT_GO_FOR_IMAGE_ID_ADDR"] = str(
            args.rse_bl2_boot_go_for_image_id_addr
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_LOAD_IMAGE_TO_SRAM_ADDR"] = str(
            args.rse_bl2_boot_load_image_to_sram_addr
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_ENC_LOAD_ADDR"] = str(
            args.rse_bl2_boot_enc_load_addr
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_ENC_SET_KEY_ADDR"] = str(
            args.rse_bl2_boot_enc_set_key_addr
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_ENC_DECRYPT_ADDR"] = str(
            args.rse_bl2_boot_enc_decrypt_addr
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOTUTIL_IMG_VALIDATE_ADDR"] = str(
            args.rse_bl2_bootutil_img_validate_addr
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOTUTIL_IMG_HASH_ADDR"] = str(
            args.rse_bl2_bootutil_img_hash_addr
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOTUTIL_VERIFY_SIG_ADDR"] = str(
            args.rse_bl2_bootutil_verify_sig_addr
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOTUTIL_KEYS_ADDR"] = str(
            args.rse_bl2_bootutil_keys_addr
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOTUTIL_KEY_CNT_ADDR"] = str(
            args.rse_bl2_bootutil_key_cnt_addr
        )
        env["QBOX_RDASPEN_RSE_BL2_FIH_SUCCESS_ADDR"] = str(
            args.rse_bl2_fih_success_addr
        )
        env["QBOX_RDASPEN_RSE_BL2_DELAY_CYCLES_ADDR"] = str(
            args.rse_bl2_delay_cycles_addr
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_IMAGE_COUNT"] = str(
            args.rse_bl2_boot_image_count
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_STATE_CURR_IMG_OFFSET"] = str(
            args.rse_bl2_boot_state_curr_img_offset
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_STATE_IMGS_OFFSET"] = str(
            args.rse_bl2_boot_state_imgs_offset
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_STATE_IMAGE_STRIDE"] = str(
            args.rse_bl2_boot_state_image_stride
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_STATE_SLOT_STRIDE"] = str(
            args.rse_bl2_boot_state_slot_stride
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_STATE_SLOT_USAGE_OFFSET"] = str(
            args.rse_bl2_boot_state_slot_usage_offset
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_STATE_SLOT_USAGE_STRIDE"] = str(
            args.rse_bl2_boot_state_slot_usage_stride
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_SLOT_USAGE_IMG_DST_OFFSET"] = str(
            args.rse_bl2_boot_slot_usage_img_dst_offset
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_SLOT_USAGE_IMG_SZ_OFFSET"] = str(
            args.rse_bl2_boot_slot_usage_img_sz_offset
        )
    if args.rse_bl2_load_accel:
        env["QBOX_RDASPEN_RSE_BL2_LOAD_ACCEL"] = "true"
        env["QBOX_RDASPEN_RSE_BL2_LOAD_ACCEL_MAX_BYTES"] = str(
            args.rse_bl2_load_accel_max_bytes
        )
    if args.rse_bl2_boot_enc_accel:
        env["QBOX_RDASPEN_RSE_BL2_BOOT_ENC_ACCEL"] = "true"
    if args.rse_bl2_boot_enc_accel or args.rse_bl2_load_accel:
        env["QBOX_RDASPEN_RSE_BL2_BOOT_STATUS_ENCKEY_OFFSET"] = str(
            args.rse_bl2_boot_status_enckey_offset
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_ENC_KEY_BYTES"] = str(
            args.rse_bl2_boot_enc_key_bytes
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_ENC_KEY_STRIDE"] = str(
            args.rse_bl2_boot_enc_key_stride
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_ENC_SLOTS"] = str(
            args.rse_bl2_boot_enc_slots
        )
        env["QBOX_RDASPEN_RSE_BL2_BOOT_ENC_MAX_BYTES"] = str(
            args.rse_bl2_boot_enc_max_bytes
        )
    if args.rse_bl2_img_hash_accel:
        env["QBOX_RDASPEN_RSE_BL2_IMG_HASH_ACCEL"] = "true"
        env["QBOX_RDASPEN_RSE_BL2_IMG_HASH_MAX_BYTES"] = str(
            args.rse_bl2_img_hash_max_bytes
        )
        env["QBOX_RDASPEN_RSE_BL2_IMG_HASH_MAX_SEED_BYTES"] = str(
            args.rse_bl2_img_hash_max_seed_bytes
        )
    if args.rse_bl2_verify_sig_accel:
        env["QBOX_RDASPEN_RSE_BL2_VERIFY_SIG_ACCEL"] = "true"
        env["QBOX_RDASPEN_RSE_BL2_VERIFY_SIG_MAX_KEY_BYTES"] = str(
            args.rse_bl2_verify_sig_max_key_bytes
        )
        env["QBOX_RDASPEN_RSE_BL2_VERIFY_SIG_MAX_SIG_BYTES"] = str(
            args.rse_bl2_verify_sig_max_sig_bytes
        )
    if args.rse_bl2_verify_sig_skip:
        env["QBOX_RDASPEN_RSE_BL2_VERIFY_SIG_ACCEL"] = "true"
        env["QBOX_RDASPEN_RSE_BL2_VERIFY_SIG_SKIP"] = "true"
    if args.rse_bl2_delay_accel:
        env["QBOX_RDASPEN_RSE_BL2_DELAY_ACCEL"] = "true"
        env["QBOX_RDASPEN_RSE_BL2_DELAY_MAX_CYCLES"] = str(
            args.rse_bl2_delay_max_cycles
        )
        env["QBOX_RDASPEN_RSE_BL2_DELAY_EXPECTED_HITS"] = str(
            args.rse_bl2_delay_expected_hits
        )
    direct_file_aliases = rse_direct_file_aliases_for_args(args, artifacts)
    if direct_file_aliases:
        env["QBOX_RDASPEN_RSE_DIRECT_FILE_ALIASES"] = direct_file_aliases
    if args.rse_direct_si_sram_alias:
        env["QBOX_RDASPEN_RSE_DIRECT_SI_SRAM_ALIAS"] = "true"
        env["QBOX_RDASPEN_RSE_DIRECT_SI_SRAM_CODE_ALIAS_SIZE"] = str(
            args.rse_direct_si_sram_code_alias_size
        )
    if args.cc3xx_qemu_native_backend:
        env["QBOX_RDASPEN_CC3XX_BACKEND"] = "qemu-native"
        append_env_csv(
            env,
            "QBOX_RDASPEN_RSE_MMIO_DIRECT_FASTPATH_RANGES",
            cc3xx_local_mmio_fastpath_spec(),
        )
    if args.rse_storage_direct_fastpath:
        append_env_csv(
            env,
            "QBOX_RDASPEN_RSE_MMIO_DIRECT_FASTPATH_RANGES",
            rse_storage_direct_fastpath_spec(),
        )
    if args.cc3xx_status_read_fastpath:
        env["QBOX_RDASPEN_RSE_MMIO_READ_FASTPATH"] = (
            cc3xx_status_read_fastpath_spec()
        )
    if args.cc3xx_local_mmio_fastpath:
        append_env_csv(
            env,
            "QBOX_RDASPEN_RSE_MMIO_DIRECT_FASTPATH_RANGES",
            cc3xx_local_mmio_fastpath_spec(),
        )
    if args.pc_trace:
        env["QBOX_RDASPEN_RSE_PC_TRACE"] = "true"
        env["QBOX_RDASPEN_RSE_PC_TRACE_FILE"] = str(args.out_dir / RSE_PC_TRACE_LOG)
        env["QBOX_RDASPEN_RSE_PC_TRACE_INTERVAL"] = str(args.pc_trace_interval)
        env["QBOX_RDASPEN_RSE_PC_TRACE_LIMIT"] = str(args.pc_trace_limit)
        env["QBOX_RDASPEN_AP_PC_TRACE"] = "true"
        env["QBOX_RDASPEN_AP_PC_TRACE_FILE"] = str(args.out_dir / AP_PC_TRACE_LOG)
        env["QBOX_RDASPEN_AP_PC_TRACE_INTERVAL"] = str(args.pc_trace_interval)
        env["QBOX_RDASPEN_AP_PC_TRACE_LIMIT"] = str(args.pc_trace_limit)
        if args.exception_trace:
            env["QBOX_RDASPEN_RSE_EXCEPTION_TRACE"] = "true"
            env["QBOX_RDASPEN_AP_EXCEPTION_TRACE"] = "true"
    return env


def stop_process(proc: subprocess.Popen[bytes]) -> None:
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait(timeout=5)


def qbox_runtime_processes() -> list[dict[str, object]]:
    processes: list[dict[str, object]] = []
    proc_root = Path("/proc")
    if not proc_root.exists():
        return processes
    for entry in proc_root.iterdir():
        if not entry.name.isdigit():
            continue
        cmdline_path = entry / "cmdline"
        try:
            raw = cmdline_path.read_bytes()
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if not raw:
            continue
        parts = [part.decode("utf-8", errors="replace") for part in raw.split(b"\0") if part]
        if not parts:
            continue
        executable = Path(parts[0]).name
        if executable in QBOX_RUNTIME_EXECUTABLES or any(
            any(part.endswith(f"/{name}") for name in QBOX_RUNTIME_EXECUTABLES)
            for part in parts
        ):
            processes.append({"pid": int(entry.name), "cmdline": parts})
    return processes


def cleanup_sram_dmi_shared_memory(phase: str) -> dict[str, object]:
    result: dict[str, object] = {
        "phase": phase,
        "prefixes": list(SRAM_DMI_SHM_PREFIXES),
        "safe": False,
        "removed": [],
        "remaining": [],
        "skipped_live_processes": [],
        "errors": [],
    }
    shm_root = Path("/dev/shm")
    if not shm_root.exists():
        result["safe"] = True
        return result

    live_processes = qbox_runtime_processes()
    if live_processes:
        result["skipped_live_processes"] = live_processes
        return result

    result["safe"] = True
    for prefix in SRAM_DMI_SHM_PREFIXES:
        for path in sorted(shm_root.glob(prefix + "*")):
            try:
                path.unlink()
                cast_removed = result["removed"]
                assert isinstance(cast_removed, list)
                cast_removed.append(str(path))
            except FileNotFoundError:
                continue
            except OSError as exc:
                cast_errors = result["errors"]
                assert isinstance(cast_errors, list)
                cast_errors.append(f"{path}: {exc}")
    remaining: list[str] = []
    for prefix in SRAM_DMI_SHM_PREFIXES:
        remaining.extend(str(path) for path in sorted(shm_root.glob(prefix + "*")))
    result["remaining"] = remaining
    return result


def write_primary_uart(fd: int, text: str) -> None:
    os.write(fd, text.encode("utf-8"))


def write_primary_uart_bytes(fd: int, data: bytes) -> None:
    os.write(fd, data)


def open_post_login_probe_fifo(out_dir: Path) -> tuple[Path, int]:
    fifo_path = out_dir / "primary-uart-input.fifo"
    try:
        fifo_path.unlink()
    except FileNotFoundError:
        pass
    os.mkfifo(fifo_path)
    fd = os.open(fifo_path, os.O_RDWR | os.O_NONBLOCK)
    return fifo_path, fd


def make_probe_state(args: argparse.Namespace) -> dict[str, object]:
    operations: list[dict[str, object]] = []
    if args.primary_operation_manifest is not None:
        operations = load_operations(
            args.primary_operation_manifest,
            args.primary_operation_schema,
        )
    return {
        "requested": bool(args.post_login_probe or operations),
        "operation_manifest_requested": bool(operations),
        "operations": operations,
        "operation_records": [],
        "operation_module_path": (
            str(args.primary_operation_module_path)
            if args.primary_operation_module_path is not None
            else ""
        ),
        "secure_service_requested": bool(args.secure_service_probe),
        "fwu_requested": bool(args.fwu_probe),
        "sent_login": False,
        "sent_probe": False,
        "complete": False,
        "passed": False,
        "input_path": None,
        "actions": [],
        "login_attempts": 0,
        "last_login_time": 0.0,
        "command_index": 0,
        "last_prompt_end": 0,
    }


def drive_post_login_probe(
    args: argparse.Namespace,
    logs: dict[str, str],
    state: dict[str, object],
    fifo_fd: int | None,
) -> None:
    operation_mode = bool(state.get("operation_manifest_requested"))
    if not args.post_login_probe and not operation_mode or fifo_fd is None:
        return
    clean_primary = clean_text(logs.get("primary_console", ""))
    actions = state.setdefault("actions", [])
    assert isinstance(actions, list)
    login_ready = bool(
        args.primary_login_prompt in clean_primary
        or any(
            re.search(pattern, clean_primary, re.IGNORECASE | re.MULTILINE)
            for pattern in LOGIN_READY_PATTERNS
        )
    )
    login_attempts_value = state.get("login_attempts", 0)
    last_login_time_value = state.get("last_login_time", 0.0)
    assert isinstance(login_attempts_value, int)
    assert isinstance(last_login_time_value, int | float)
    login_attempts = int(login_attempts_value)
    last_login_time = float(last_login_time_value)
    shell_prompt_matches = list(
        re.finditer(args.primary_shell_prompt_re, clean_primary, re.MULTILINE)
    )
    shell_prompt_end = shell_prompt_matches[-1].end() if shell_prompt_matches else 0
    retry_login = (
        bool(state["sent_login"])
        and not state["sent_probe"]
        and login_ready
        and login_attempts < 6
        and time.monotonic() - last_login_time >= 5.0
    )
    if not state["sent_login"] and shell_prompt_matches:
        state["sent_login"] = True
        actions.append("shell_prompt_already_ready")
    elif (not state["sent_login"] and login_ready) or retry_login:
        prefix = "" if args.primary_login_prompt in clean_primary else "\n"
        write_primary_uart(fifo_fd, prefix + args.login_user + "\n")
        state["sent_login"] = True
        state["login_attempts"] = login_attempts + 1
        state["last_login_time"] = time.monotonic()
        actions.append(f"sent_login_attempt_{login_attempts + 1}")
    command_index_value = state.get("command_index", 0)
    last_prompt_end_value = state.get("last_prompt_end", 0)
    assert isinstance(command_index_value, int)
    assert isinstance(last_prompt_end_value, int)
    command_index = int(command_index_value)
    last_prompt_end = int(last_prompt_end_value)
    commands = post_login_probe_commands(args)
    command_ready = bool(
        state["sent_login"]
        and shell_prompt_end > 0
        and (
            not state["sent_probe"]
            or shell_prompt_end > last_prompt_end
        )
    )
    records = state.get("operation_records")
    assert isinstance(records, list)
    if (
        operation_mode
        and state["sent_probe"]
        and shell_prompt_end > last_prompt_end
        and len(records) < command_index
    ):
        operations = state.get("operations")
        assert isinstance(operations, list)
        stdout = clean_primary[last_prompt_end:shell_prompt_end]
        counters = [
            {
                "kind": kind,
                "target_cpu": int(cpu),
                "count": int(count),
            }
            for kind, cpu, count in re.findall(
                r"\b(ipi|spi) target=(\d+)(?: cpu=\d+)? count=(\d+)",
                stdout,
            )
        ]
        records.append({
            "index": command_index - 1,
            "operation": operations[command_index - 1],
            "stdout": stdout,
            "exit_status": None,
            "exit_status_observed": False,
            "counters": counters,
            "completed": True,
        })
    operations_value = state.get("operations")
    assert isinstance(operations_value, list)
    command_count = len(operations_value) if operation_mode else len(commands)
    if command_ready and command_index < command_count:
        if operation_mode:
            module_path = Path(str(state.get("operation_module_path", "")))
            chunks = serialize_operation(
                operations_value[command_index],
                module_path=module_path,
            )
            for chunk in chunks:
                write_primary_uart_bytes(fifo_fd, chunk)
        else:
            write_primary_uart(fifo_fd, commands[command_index] + "\n")
        state["sent_probe"] = True
        state["command_index"] = command_index + 1
        state["last_prompt_end"] = shell_prompt_end
        actions.append(f"sent_primary_operation_{command_index + 1}")
    completed_command_index = state.get("command_index", 0)
    assert isinstance(completed_command_index, int)
    if (
        operation_mode
        and completed_command_index >= command_count
        and len(records) >= command_count
    ):
        state["complete"] = True
    elif completed_command_index >= len(commands) and PROBE_DONE_MARKER in clean_primary:
        state["complete"] = True
    if args.fwu_probe and fwu_probe_stage_complete(logs):
        state["complete"] = True


def run_platform(
    root: Path, args: argparse.Namespace, artifacts: dict[str, Path]
) -> tuple[
    int,
    dict[str, str],
    bool,
    bool,
    float,
    dict[str, object],
    dict[str, dict[str, object]],
    list[dict[str, object]],
]:
    out_dir = args.out_dir
    build_dir = qbox_build_dir(root)
    cmd = [
        str((build_dir / "platforms-vp").resolve()),
        "-l",
        str(args.conf.resolve()),
    ]
    for param in args.platform_param:
        cmd.extend(["-p", qbox_platform_param_value(param)])
    if args.host_gdb_script:
        cmd = [
            os.environ.get("QBOX_HOST_GDB_EXEC", "gdb"),
            "-q",
            "-iex",
            "set debuginfod enabled off",
            "-x",
            str(args.host_gdb_script.resolve()),
            "--args",
        ] + cmd
    env = qbox_env(root, args, artifacts)
    post_login_probe = make_probe_state(args)
    primary_uart_fd: int | None = None
    if args.post_login_probe or args.primary_operation_manifest is not None:
        fifo_path, primary_uart_fd = open_post_login_probe_fifo(out_dir)
        env["QBOX_RDASPEN_PRIMARY_UART_READ_FILE"] = str(fifo_path)
        post_login_probe["input_path"] = str(fifo_path)
    timed_out = False
    interrupted = False
    logs = {role: "" for role in CONSOLE_LOGS}
    progress_marker_first_hits: dict[str, dict[str, object]] = {}
    platform_log = out_dir / PLATFORM_STDOUT_LOG
    platform_stdout = ""
    rse_sram_dmi_smoke_pass_at: float | None = None
    shared_memory_cleanup: list[dict[str, object]] = []
    if args.rse_fast_boot_sram_dmi:
        shared_memory_cleanup.append(cleanup_sram_dmi_shared_memory("before_run"))

    print(f"log: {platform_log}", flush=True)
    print("+ " + " ".join(cmd), flush=True)
    start = time.monotonic()
    proc = subprocess.Popen(
        cmd,
        cwd=root,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    try:
        with platform_log.open("w", encoding="utf-8", errors="replace", buffering=1) as log:
            assert proc.stdout is not None
            os.set_blocking(proc.stdout.fileno(), False)
            while args.timeout <= 0 or time.monotonic() - start < args.timeout:
                try:
                    chunk = os.read(proc.stdout.fileno(), 65536)
                except BlockingIOError:
                    chunk = b""
                if chunk:
                    decoded = chunk.decode("utf-8", errors="replace")
                    log.write(decoded)
                    platform_stdout += decoded
                logs = read_console_logs(out_dir)
                drive_post_login_probe(args, logs, post_login_probe, primary_uart_fd)
                live_logs = {**logs, "platform_stdout": platform_stdout}
                update_progress_marker_first_hits(
                    live_logs,
                    progress_marker_first_hits,
                    time.monotonic() - start,
                )
                status = evaluate(
                    live_logs,
                    rse_sram_dmi_smoke=args.rse_sram_dmi_smoke,
                )
                required_markers_missing = missing_required_pass_markers(
                    args.required_pass_marker
                )
                probe_complete = bool(post_login_probe.get("complete"))
                probe_requested = bool(
                    args.post_login_probe
                    or args.primary_operation_manifest is not None
                )
                if (
                    probe_requested
                    and probe_complete
                    and not args.keep_running_after_pass
                ):
                    stop_process(proc)
                    break
                pass_condition_hit = (
                    status["passed"]
                    and not required_markers_missing
                    and (not probe_requested or probe_complete)
                    and not args.keep_running_after_pass
                )
                if pass_condition_hit:
                    now = time.monotonic()
                    if (
                        args.rse_sram_dmi_smoke
                        and args.rse_sram_dmi_smoke_grace_s > 0.0
                    ):
                        if rse_sram_dmi_smoke_pass_at is None:
                            rse_sram_dmi_smoke_pass_at = now
                        if (
                            now - rse_sram_dmi_smoke_pass_at
                            < args.rse_sram_dmi_smoke_grace_s
                        ):
                            if chunk:
                                continue
                            if proc.poll() is not None:
                                break
                            time.sleep(0.1)
                            continue
                    stop_process(proc)
                    break
                if (
                    any(bool_dict(status.get("fail_patterns")).values())
                    and not args.ignore_fail_patterns
                ):
                    stop_process(proc)
                    break
                if chunk:
                    continue
                if proc.poll() is not None:
                    break
                time.sleep(0.1)
            else:
                timed_out = True
                stop_process(proc)
    except KeyboardInterrupt:
        interrupted = True
        stop_process(proc)
    finally:
        elapsed_s = time.monotonic() - start
        stop_process(proc)
        if primary_uart_fd is not None:
            os.close(primary_uart_fd)
        if args.rse_fast_boot_sram_dmi and not interrupted:
            shared_memory_cleanup.append(
                cleanup_sram_dmi_shared_memory("after_run")
            )

    for role, filename in CONSOLE_LOGS.items():
        path = out_dir / filename
        if path.exists():
            logs[role] = path.read_text(encoding="utf-8", errors="replace")
            continue
        text = (
            "QBox Apollo RSE-oriented boot did not create this console log.\n"
            f"console: {role}\n"
            f"platform_stdout_log: {platform_log}\n"
        )
        path.write_text(text, encoding="utf-8")
        logs[role] = text

    if platform_stdout and not logs["rse"].strip():
        logs["rse"] = platform_stdout
    update_progress_marker_first_hits(
        {**logs, "platform_stdout": platform_stdout},
        progress_marker_first_hits,
        elapsed_s,
    )

    rc = proc.returncode if proc.returncode is not None else 1
    if args.primary_operation_manifest is not None:
        post_login_probe["passed"] = bool(post_login_probe.get("complete"))
    else:
        probe_eval = evaluate_post_login_probe(
            logs.get("primary_console", ""),
            logs.get("secure_console", ""),
            logs.get("rse", ""),
        )
        post_login_probe.update(probe_eval)
        fwu_probe = object_dict(probe_eval.get("fwu_probe"))
        fwu_complete = bool(fwu_probe.get("complete"))
        if (not args.fwu_probe and probe_eval.get("done_marker")) or fwu_complete:
            post_login_probe["complete"] = True
        post_login_probe["passed"] = bool(
            args.post_login_probe
            and post_login_probe.get("sent_probe")
            and post_login_probe.get("complete")
            and all(
                bool(value)
                for value in object_dict(probe_eval.get("driver_patterns")).values()
            )
        )
    if args.post_login_probe or args.primary_operation_manifest is not None:
        action_log = out_dir / "post-login-probe-actions.log"
        action_lines = [
            f"requested: {post_login_probe['requested']}",
            f"secure_service_requested: {post_login_probe['secure_service_requested']}",
            f"fwu_requested: {post_login_probe['fwu_requested']}",
            f"input_path: {post_login_probe.get('input_path')}",
            f"sent_login: {post_login_probe['sent_login']}",
            f"sent_probe: {post_login_probe['sent_probe']}",
            f"complete: {post_login_probe['complete']}",
            f"passed: {post_login_probe['passed']}",
            "actions:",
            *[f"  - {action}" for action in string_list(post_login_probe.get("actions"))],
        ]
        action_log.write_text("\n".join(action_lines) + "\n", encoding="utf-8")
        post_login_probe["action_log"] = str(action_log)
    return (
        rc,
        logs,
        timed_out,
        interrupted,
        elapsed_s,
        post_login_probe,
        progress_marker_first_hits,
        shared_memory_cleanup,
    )


def write_result(
    args: argparse.Namespace,
    artifacts: dict[str, Path],
    copied: dict[str, Path],
    logs: dict[str, str],
    *,
    runtime_artifacts: dict[str, Path] | None = None,
    first_fault: dict[str, str] | None = None,
    flash_image_preparation: dict[str, object] | None = None,
    ap_flash_image_preparation: dict[str, object] | None = None,
    rootfs_preparation: dict[str, object] | None = None,
    command: list[str],
    timed_out: bool,
    interrupted: bool,
    blocker: str | None,
    platform_rc: int | None,
    runtime_elapsed_s: float | None = None,
    rse_fwu_private_metadata: dict[str, object] | None = None,
    rse_pc_trace: dict[str, object] | None = None,
    ap_pc_trace: dict[str, object] | None = None,
    host_si_cl0_sram: dict[str, object] | None = None,
    host_si_cl1_sram: dict[str, object] | None = None,
    host_ap_bl2_header_sram: dict[str, object] | None = None,
    boot_enc_trace: dict[str, object] | None = None,
    post_login_probe: dict[str, object] | None = None,
    progress_marker_first_hits: dict[str, dict[str, object]] | None = None,
    shared_memory_cleanup: list[dict[str, object]] | None = None,
) -> int:
    out_dir = args.out_dir
    args.rse_flash_state_status = finalize_rse_flash_state_status(
        getattr(
            args,
            "rse_flash_state_status",
            {"enabled": False, "action": "ephemeral"},
        )
    )
    write_json_atomic(
        out_dir / RSE_FLASH_STATE_STATUS_FILE,
        args.rse_flash_state_status,
    )
    runtime_artifacts = artifacts if runtime_artifacts is None else runtime_artifacts
    status = evaluate(logs, rse_sram_dmi_smoke=args.rse_sram_dmi_smoke)
    if blocker:
        status["passed"] = False
    marker_hits = nested_bool_dict(status.get("marker_hits"))
    rse_boot_started = any(marker_hits.get("rse_boot", {}).values())
    rse_scp_complete = all(marker_hits.get("rse_scp_handoff", {}).values())
    ap_boot_started = bool(logs.get("secure_console", "").strip())
    ap_boot_label = (
        "functional-model"
        if status["passed"]
        else ("partial-model" if ap_boot_started else "not-modeled")
    )
    rse_boot_timing_profile = build_rse_boot_timing_profile(
        progress_marker_first_hits
    )
    cc3xx_backend = "qemu-native" if args.cc3xx_qemu_native_backend else "systemc"
    cc3xx_label = (
        "hash-aes-cmac-modular-pka-qemu-native-model"
        if args.cc3xx_qemu_native_backend
        else "hash-aes-cmac-modular-pka-model"
    )
    if args.cc3xx_local_mmio_fastpath:
        cc3xx_label += "-local-mmio-fastpath"
    if args.cc3xx_status_read_fastpath:
        cc3xx_label += "-status-read-fastpath"

    static_label = "not-modeled" if blocker else "static-map-only"
    rse_boot_media_label = (
        "qemu-cfi01-local-single-state-model"
        if args.rse_flash_backend == "qemu-cfi-local"
        else "cfi-strata-flash-partial-model"
    )
    rse_scp_endpoint_label = "functional-model" if rse_scp_complete else "not-modeled"
    scp_service_model = {
        "strategy": args.scp_strategy,
        "endpoint_fidelity": rse_scp_endpoint_label,
        "live_scp_cpu_gdb": args.scp_strategy != "service-model",
        "remaining_real_scp_gaps": (
            SERVICE_MODEL_GAPS if args.scp_strategy == "service-model" else []
        ),
    }
    rse_hotpath_memcpy_addr = (
        args.rse_hotpath_memcpy_addr
        if args.rse_hotpath_memcpy_addr is not None
        else RSE_HOTPATH_MEMCPY_DEFAULT
    )
    rse_hotpath_memset_addr = (
        args.rse_hotpath_memset_addr
        if args.rse_hotpath_memset_addr is not None
        else RSE_HOTPATH_MEMSET_DEFAULT
    )

    status.update(
        {
            "boot_mode": "rse-oriented",
            "scp_strategy": args.scp_strategy,
            "smmu_backend": args.smmu_backend,
            "rse_flash_backend": args.rse_flash_backend,
            "range_limited_flash_dmi": args.range_limited_flash_dmi,
            "rse_fast_boot_sram_dmi": rse_fast_boot_sram_dmi_result(args),
            "ap_fip_logical_aperture": ap_fip_logical_aperture_result(args),
            "cc3xx_status_read_fastpath": {
                "enabled": args.cc3xx_status_read_fastpath,
                "entries": len(CC3XX_STATUS_READ_FASTPATH_VALUES)
                if args.cc3xx_status_read_fastpath
                else 0,
            },
            "cc3xx_backend": cc3xx_backend,
            "cc3xx_local_mmio_fastpath": {
                "enabled": (
                    args.cc3xx_local_mmio_fastpath
                    or args.cc3xx_qemu_native_backend
                ),
                "implicit_by_qemu_native_backend": args.cc3xx_qemu_native_backend,
                "ranges": [cc3xx_local_mmio_fastpath_spec()]
                if (
                    args.cc3xx_local_mmio_fastpath
                    or args.cc3xx_qemu_native_backend
                )
                else [],
            },
            "rse_storage_direct_fastpath": {
                "enabled": bool(args.rse_storage_direct_fastpath),
                "range": rse_storage_direct_fastpath_spec()
                if args.rse_storage_direct_fastpath
                else "",
                "flash_layout": {
                    "image_offset": hex(RSE_FLASH_IMG_SIZE),
                    "ps_size": hex(RSE_FLASH_PS_SIZE),
                    "its_size": hex(RSE_FLASH_ITS_SIZE),
                },
                "fidelity_note": (
                    "keeps the Strata CFI model active; removes QEMU-to-SystemC "
                    "thread crossing for the RSE PS/ITS flash storage window"
                ),
            },
            "scp_service_model": scp_service_model,
            "fidelity_labels": {
                "rse_cortex_m55_boot": "functional-model" if rse_boot_started else static_label,
                "rse_boot_media": rse_boot_media_label,
                "rse_cc3xx": cc3xx_label,
                "rse_dma350": "functional-fill-copy-model",
                "rse_lcm": "otp-backed-register-model",
                "rse_integrity_checker": "touched-status-model",
                "rse_kmu": "touched-register-model",
                "rse_sysctrl": "touched-register-model",
                "host_si_scr": "sid-system-cfg-register-model",
                "rse_sacfg": "static-map-only",
                "rse_nsacfg": "static-map-only",
                "rse_atu": (
                    "translation-dmi-model"
                    if os.environ.get("QBOX_RDASPEN_ATU_DMI") == "true"
                    else "translation-model"
                ),
                "rse_ap_fip_visibility": (
                    "legacy-direct-file-alias"
                    if args.rse_direct_ap_fip_alias
                    else "atu-systemc-route"
                ),
                "mhuv3": "systemc-mhu320ae",
                "rse_scp_endpoint": rse_scp_endpoint_label,
                "rse_oriented_ap_boot": ap_boot_label,
            },
            "input_artifacts": {name: str(path) for name, path in artifacts.items()},
            "runtime_artifacts": {name: str(path) for name, path in runtime_artifacts.items()},
            "copied_writable_artifacts": {name: str(path) for name, path in copied.items()},
            "rse_flash_state": getattr(
                args,
                "rse_flash_state_status",
                {"enabled": False, "action": "ephemeral"},
            ),
            "flash_image_preparation": flash_image_preparation,
            "ap_flash_image_preparation": ap_flash_image_preparation,
            "rootfs_preparation": rootfs_preparation,
            "rse_fwu_private_metadata": rse_fwu_private_metadata,
            "host_si_cl0_sram": host_si_cl0_sram,
            "host_si_cl1_sram": host_si_cl1_sram,
            "host_ap_bl2_header_sram": host_ap_bl2_header_sram,
            "host_sram_backing": host_sram_backing_result(args, runtime_artifacts),
            "console_logs": {
                role: str((out_dir / filename).resolve())
                for role, filename in CONSOLE_LOGS.items()
            },
            "platform_stdout_log": str((out_dir / PLATFORM_STDOUT_LOG).resolve()),
            "qemu_trace_log": (
                str((out_dir / QEMU_TRACE_LOG).resolve())
                if qemu_trace_enabled(args)
                else None
            ),
            "cc3xx_stats": parse_cc3xx_stats(args),
            "qbox_perf_profile": parse_qbox_perf_profile(args),
            "rse_hotpath_accel": {
                "enabled": bool(args.rse_hotpath_accel),
                "bl2_libc_hotpath": bool(args.rse_bl2_libc_hotpath),
                "memcpy_addr": hex(rse_hotpath_memcpy_addr),
                "memset_addr": hex(rse_hotpath_memset_addr),
                "max_bytes": args.rse_hotpath_max_bytes,
            },
            "rse_lms_accel": {
                "enabled": bool(args.rse_lms_accel),
                "verify_addr": hex(args.rse_lms_verify_addr),
                "max_data_bytes": args.rse_lms_max_data_bytes,
                "symbol_source": args.rse_bl1_2_symbol_source,
                "hook": "qemu-tcg-pc-entry",
                "effective_when": "qbox_perf_profile.rse_hotpath_profile.stats.lms_hits > 0",
            },
            "rse_bl2_load_profile": {
                "enabled": bool(args.rse_bl2_load_profile),
                "hook": "qemu-tcg-pc-entry",
                "symbol_source": args.rse_bl2_symbol_source,
                "addresses": {
                    "boot_go_for_image_id": hex(args.rse_bl2_boot_go_for_image_id_addr),
                    "boot_load_image_to_sram": hex(args.rse_bl2_boot_load_image_to_sram_addr),
                    "boot_enc_load": hex(args.rse_bl2_boot_enc_load_addr),
                    "boot_enc_set_key": hex(args.rse_bl2_boot_enc_set_key_addr),
                    "boot_enc_decrypt": hex(args.rse_bl2_boot_enc_decrypt_addr),
                    "bootutil_img_validate": hex(args.rse_bl2_bootutil_img_validate_addr),
                    "bootutil_img_hash": hex(args.rse_bl2_bootutil_img_hash_addr),
                    "bootutil_verify_sig": hex(args.rse_bl2_bootutil_verify_sig_addr),
                    "delay_cycles": hex(args.rse_bl2_delay_cycles_addr),
                },
                "state_layout": {
                    "image_count": args.rse_bl2_boot_image_count,
                    "curr_img_offset": hex(args.rse_bl2_boot_state_curr_img_offset),
                    "imgs_offset": hex(args.rse_bl2_boot_state_imgs_offset),
                    "image_stride": args.rse_bl2_boot_state_image_stride,
                    "slot_stride": args.rse_bl2_boot_state_slot_stride,
                    "slot_usage_offset": hex(args.rse_bl2_boot_state_slot_usage_offset),
                    "slot_usage_stride": args.rse_bl2_boot_state_slot_usage_stride,
                    "slot_usage_img_dst_offset": hex(
                        args.rse_bl2_boot_slot_usage_img_dst_offset
                    ),
                    "slot_usage_img_sz_offset": hex(
                        args.rse_bl2_boot_slot_usage_img_sz_offset
                    ),
                },
                "effective_when": "qbox_perf_profile.rse_hotpath_profile.stats.bl2_load_profile.sites.*.hits > 0",
            },
            "rse_bl2_load_accel": {
                "enabled": bool(args.rse_bl2_load_accel),
                "hook": "qemu-tcg-pc-entry",
                "decrypt_addr": hex(args.rse_bl2_boot_enc_decrypt_addr),
                "max_bytes": args.rse_bl2_load_accel_max_bytes,
                "supported_flags": "0x24",
                "guest_checks_preserved": [
                    "boot_enc_load",
                    "boot_enc_set_key",
                    "boot_verify_ram_load_address",
                    "bootutil_img_validate",
                    "bootutil_verify_sig",
                    "security counter check",
                ],
                "effective_when": "qbox_perf_profile.rse_hotpath_profile.stats.bl2_load_accel.hits > 0",
            },
            "rse_bl2_boot_enc_accel": {
                "enabled": bool(args.rse_bl2_boot_enc_accel),
                "hook": "qemu-tcg-pc-entry",
                "set_key_addr": hex(args.rse_bl2_boot_enc_set_key_addr),
                "decrypt_addr": hex(args.rse_bl2_boot_enc_decrypt_addr),
                "boot_status_enckey_offset": hex(args.rse_bl2_boot_status_enckey_offset),
                "key_bytes": args.rse_bl2_boot_enc_key_bytes,
                "key_stride": args.rse_bl2_boot_enc_key_stride,
                "slots": args.rse_bl2_boot_enc_slots,
                "max_bytes": args.rse_bl2_boot_enc_max_bytes,
                "effective_when": "qbox_perf_profile.rse_hotpath_profile.stats.bl2_boot_enc_accel.decrypt_hits > 0",
            },
            "rse_bl2_img_hash_accel": {
                "enabled": bool(args.rse_bl2_img_hash_accel),
                "hook": "qemu-tcg-pc-entry",
                "img_hash_addr": hex(args.rse_bl2_bootutil_img_hash_addr),
                "max_bytes": args.rse_bl2_img_hash_max_bytes,
                "max_seed_bytes": args.rse_bl2_img_hash_max_seed_bytes,
                "guest_checks_preserved": [
                    "bootutil_img_validate TLV traversal",
                    "bootutil_verify_sig",
                    "MCUBOOT_HW_ROLLBACK_PROT security counter",
                ],
                "effective_when": "qbox_perf_profile.rse_hotpath_profile.stats.bl2_img_hash_accel.hits > 0",
            },
            "rse_bl2_verify_sig_accel": {
                "enabled": bool(args.rse_bl2_verify_sig_accel),
                "hook": "qemu-tcg-pc-entry",
                "skip_enabled": bool(args.rse_bl2_verify_sig_skip),
                "verify_sig_addr": hex(args.rse_bl2_bootutil_verify_sig_addr),
                "bootutil_keys_addr": hex(args.rse_bl2_bootutil_keys_addr),
                "bootutil_key_cnt_addr": hex(args.rse_bl2_bootutil_key_cnt_addr),
                "fih_success_addr": hex(args.rse_bl2_fih_success_addr),
                "max_key_bytes": args.rse_bl2_verify_sig_max_key_bytes,
                "max_sig_bytes": args.rse_bl2_verify_sig_max_sig_bytes,
                "effective_when": "qbox_perf_profile.rse_hotpath_profile.stats.bl2_verify_sig_accel.verify_matches > 0",
            },
            "rse_bl2_delay_accel": {
                "enabled": bool(args.rse_bl2_delay_accel),
                "hook": "qemu-tcg-pc-entry",
                "delay_cycles_addr": hex(args.rse_bl2_delay_cycles_addr),
                "max_cycles": args.rse_bl2_delay_max_cycles,
                "expected_hits": args.rse_bl2_delay_expected_hits,
                "fidelity_note": (
                    "opt-in performance mode; skips the configured prefix of TF-M BL2 "
                    "delay_cycles loops; the default preserves the SI startup wait"
                ),
                "effective_when": "qbox_perf_profile.rse_hotpath_profile.stats.bl2_delay_accel.hits > 0",
            },
            "rse_direct_si_sram_alias": {
                "enabled": bool(
                    args.rse_direct_si_sram_alias
                    or args.rse_direct_ap_bl2_alias
                    or args.rse_direct_rse_flash_alias
                    or args.rse_direct_ap_fip_alias
                    or args.rse_direct_file_aliases
                ),
                "fast_boot_aliases_preset": bool(args.rse_fast_boot_aliases),
                "si_sram_preset": bool(args.rse_direct_si_sram_alias),
                "ap_bl2_preset": bool(args.rse_direct_ap_bl2_alias),
                "rse_boot_flash_preset": bool(args.rse_direct_rse_flash_alias),
                "ap_fip_preset": bool(args.rse_direct_ap_fip_alias),
                "code_alias_size": args.rse_direct_si_sram_code_alias_size,
                "ap_bl2_code_alias_size": args.rse_direct_ap_bl2_code_alias_size,
                "header_alias_size": HOST_SI_IMG_HEADER_ALIAS_SIZE,
                "ap_bl2_header_alias_size": HOST_AP_BL2_IMG_HEADER_ALIAS_SIZE,
                "rse_boot_flash_ranges": [
                    {"name": name, "offset": hex(offset), "size": hex(size)}
                    for name, offset, size in rse_boot_flash_direct_read_ranges(
                        runtime_artifacts.get("rse_flash")
                    )
                ] if args.rse_direct_rse_flash_alias else [],
                "ap_fip_range": {
                    "offset": hex(AP_FLASH_FIP_PRIMARY_OFFSET),
                    "size": hex(AP_FLASH_FIP_SIZE),
                    "logical_base": hex(
                        HOST_AP_FLASH_LOGICAL_BASE + AP_FLASH_FIP_PRIMARY_OFFSET
                    ),
                } if args.rse_direct_ap_fip_alias else {},
                "direct_file_aliases": (
                    rse_direct_file_aliases_for_args(args, runtime_artifacts)
                    if (
                        args.rse_direct_file_aliases
                        or (
                            args.rse_direct_si_sram_alias
                            and "host_si_cl0_sram" in runtime_artifacts
                            and "host_si_cl1_sram" in runtime_artifacts
                        )
                        or (
                            args.rse_direct_ap_bl2_alias
                            and "host_ap_shared_sram" in runtime_artifacts
                            and "host_ap_bl2_header_sram" in runtime_artifacts
                        )
                        or args.rse_direct_rse_flash_alias
                        or args.rse_direct_ap_fip_alias
                    )
                    else ""
                ),
                "fidelity_note": (
                    "opt-in performance mode; bypasses RSE ATU/SystemC "
                    "routing only for selected RAM-load image ranges"
                ),
            },
            "rse_direct_file_aliases_summary": rse_direct_file_aliases_summary(args),
            "rse_pc_trace": rse_pc_trace,
            "ap_pc_trace": ap_pc_trace,
            "boot_enc_trace": boot_enc_trace,
            "post_login_probe": post_login_probe
            if post_login_probe is not None
            else {
                "requested": bool(args.post_login_probe),
                "secure_service_requested": bool(args.secure_service_probe),
                "fwu_requested": bool(args.fwu_probe),
                "complete": False,
                "passed": False,
                **evaluate_post_login_probe(
                    logs.get("primary_console", ""),
                    logs.get("secure_console", ""),
                    logs.get("rse", ""),
                ),
            },
            "shared_memory_cleanup": shared_memory_cleanup or [],
            "first_failing_register_access": first_fault,
            "blocker": blocker,
            "timed_out": timed_out,
            "interrupted": interrupted,
            "platform_returncode": platform_rc,
            "runtime_elapsed_s": runtime_elapsed_s,
            "progress_marker_first_hits": progress_marker_first_hits or {},
            "rse_boot_timing_profile": rse_boot_timing_profile,
            "command": command,
            "runner_argv": sys.argv,
        }
    )
    result_path = Path(
        os.environ.get("QBOX_RDASPEN_RESULT_PATH", str(out_dir / "result.json"))
    )
    summary_path = Path(
        os.environ.get("QBOX_RDASPEN_SUMMARY_PATH", str(out_dir / "summary.txt"))
    )
    result_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    console_logs = object_dict(status.get("console_logs"))
    cc3xx_stats = object_dict(status.get("cc3xx_stats"))
    qbox_perf_profile = object_dict(status.get("qbox_perf_profile"))
    status_post_login_probe = object_dict(status.get("post_login_probe"))

    lines = [
        f"passed: {status['passed']}",
        f"boot_mode: {status['boot_mode']}",
        f"scp_strategy: {status['scp_strategy']}",
        f"smmu_backend: {status['smmu_backend']}",
        f"range_limited_flash_dmi: {status['range_limited_flash_dmi']}",
        "cc3xx_status_read_fastpath: "
        + json.dumps(status["cc3xx_status_read_fastpath"], sort_keys=True),
        "cc3xx_backend: " + str(status["cc3xx_backend"]),
        "cc3xx_local_mmio_fastpath: "
        + json.dumps(status["cc3xx_local_mmio_fastpath"], sort_keys=True),
        "rse_storage_direct_fastpath: "
        + json.dumps(status["rse_storage_direct_fastpath"], sort_keys=True),
        "rse_flash_state: "
        + json.dumps(status["rse_flash_state"], sort_keys=True),
        "rse_hotpath_accel: "
        + json.dumps(status["rse_hotpath_accel"], sort_keys=True),
        "rse_lms_accel: "
        + json.dumps(status["rse_lms_accel"], sort_keys=True),
        "rse_bl2_load_profile: "
        + json.dumps(status["rse_bl2_load_profile"], sort_keys=True),
        "rse_bl2_load_accel: "
        + json.dumps(status["rse_bl2_load_accel"], sort_keys=True),
        "rse_bl2_boot_enc_accel: "
        + json.dumps(status["rse_bl2_boot_enc_accel"], sort_keys=True),
        "rse_bl2_img_hash_accel: "
        + json.dumps(status["rse_bl2_img_hash_accel"], sort_keys=True),
        "rse_bl2_verify_sig_accel: "
        + json.dumps(status["rse_bl2_verify_sig_accel"], sort_keys=True),
        "rse_bl2_delay_accel: "
        + json.dumps(status["rse_bl2_delay_accel"], sort_keys=True),
        "rse_direct_si_sram_alias: "
        + json.dumps(status["rse_direct_si_sram_alias"], sort_keys=True),
        "scp_service_model: "
        + json.dumps(status["scp_service_model"], sort_keys=True),
        f"blocker: {blocker or 'none'}",
        "console_logs:",
        *[f"  - {role}: {path}" for role, path in console_logs.items()],
        f"platform_stdout_log: {status['platform_stdout_log']}",
        "runtime_elapsed_s: "
        + (
            f"{runtime_elapsed_s:.3f}"
            if runtime_elapsed_s is not None
            else "not_run"
        ),
        "progress_marker_first_hits:",
        *(
            [
                f"  - {name}: {progress_hit_elapsed_s(hit):.3f}s "
                f"({hit.get('marker', '')})"
                for name, hit in sorted(
                    (progress_marker_first_hits or {}).items(),
                    key=lambda item: progress_hit_elapsed_s(item[1]),
                )
            ]
            or ["  none"]
        ),
        "rse_boot_timing_profile:",
        "  summary: " + json.dumps(
            rse_boot_timing_profile["summary"], sort_keys=True
        ),
        "  slowest_delta: " + (
            json.dumps(rse_boot_timing_profile["slowest_delta"], sort_keys=True)
            if rse_boot_timing_profile["slowest_delta"]
            else "none"
        ),
        f"qemu_trace_log: {status['qemu_trace_log'] or 'disabled'}",
        "cc3xx_stats: "
        + json.dumps(
            {
                "enabled": cc3xx_stats.get("enabled"),
                "path": cc3xx_stats.get("path"),
                "present": cc3xx_stats.get("present"),
            },
            sort_keys=True,
        ),
        "qbox_perf_profile: "
        + json.dumps(
            {
                "enabled": qbox_perf_profile.get("enabled"),
                "root": qbox_perf_profile.get("root"),
            },
            sort_keys=True,
        ),
        "rse_pc_trace: "
        + (
            json.dumps(rse_pc_trace, sort_keys=True)
            if rse_pc_trace
            else "disabled"
        ),
        "ap_pc_trace: "
        + (
            json.dumps(ap_pc_trace, sort_keys=True)
            if ap_pc_trace
            else "disabled"
        ),
        "host_si_cl0_sram: "
        + (
            json.dumps(host_si_cl0_sram, sort_keys=True)
            if host_si_cl0_sram
            else "disabled"
        ),
        "host_si_cl1_sram: "
        + (
            json.dumps(host_si_cl1_sram, sort_keys=True)
            if host_si_cl1_sram
            else "disabled"
        ),
        "boot_enc_trace: "
        + (
            json.dumps(boot_enc_trace, sort_keys=True)
            if boot_enc_trace
            else "disabled"
        ),
        "post_login_probe: "
        + (
            json.dumps(status_post_login_probe, sort_keys=True)
            if status_post_login_probe.get("requested")
            else "disabled"
        ),
        "first_failing_register_access: "
        + (
            json.dumps(first_fault, sort_keys=True)
            if first_fault
            else "none"
        ),
        "flash_image_preparation: "
        + (
            json.dumps(flash_image_preparation, sort_keys=True)
            if flash_image_preparation
            else "none"
        ),
        "ap_flash_image_preparation: "
        + (
            json.dumps(ap_flash_image_preparation, sort_keys=True)
            if ap_flash_image_preparation
            else "none"
        ),
        "rootfs_preparation: "
        + (
            json.dumps(rootfs_preparation, sort_keys=True)
            if rootfs_preparation
            else "none"
        ),
        "marker_hits:",
    ]
    for group, hits in marker_hits.items():
        lines.append(f"  {group}:")
        for marker, hit in hits.items():
            lines.append(f"    - {marker}: {hit}")
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out_dir)
    print(summary_path)
    print(result_path)
    if interrupted:
        return 130
    return 0 if status["passed"] else 1


def build_parser() -> argparse.ArgumentParser:
    root = workspace_root()
    deploy = root / "build/tmp_baremetal/deploy/images/fvp-rd-aspen"
    parser = argparse.ArgumentParser(
        description="Run or preflight the QBox Apollo RSE-oriented boot path."
    )
    parser.add_argument(
        "--conf",
        type=Path,
        default=root / "hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp.lua",
        help="RSE-oriented QBox Lua config. Missing config is reported as an implementation blocker.",
    )
    parser.add_argument("--rse-rom", type=Path, default=deploy / "rse-rom-image.img")
    parser.add_argument("--rse-flash", type=Path, default=deploy / "rse-flash-image.img")
    parser.add_argument(
        "--rse-flash-state",
        type=Path,
        help=(
            "Persistent writable RSE flash state. The runner reuses it only "
            "while the source RSE flash hash and size remain unchanged."
        ),
    )
    parser.add_argument(
        "--reset-rse-flash-state",
        action="store_true",
        help="Recreate --rse-flash-state from the current source image.",
    )
    parser.add_argument(
        "--rse-flash-backend",
        choices=("systemc-strata", "qemu-cfi-local"),
        default="qemu-cfi-local",
        help=(
            "RSE boot flash model. qemu-cfi-local maps one QEMU CFI01 "
            "MemoryRegion into the RSE CPU and exports that same state to TLM."
        ),
    )
    parser.add_argument("--rse-otp", type=Path, default=deploy / "rse-otp-image.img")
    parser.add_argument("--ap-flash", type=Path, default=deploy / "ap-flash-image.img")
    parser.add_argument(
        "--ap-bl2-elf",
        type=Path,
        help=(
            "Optional AP BL2 ELF used by the QBox reset loader. When omitted, "
            "the Lua platform default is used."
        ),
    )
    parser.add_argument(
        "--ap-dtb",
        type=Path,
        help="AP DTB identity forwarded by the full-system front runner.",
    )
    parser.add_argument(
        "--rse-bl2-elf",
        type=Path,
        help=(
            "Optional RSE TF-M BL2 ELF used to resolve BL2 hook symbols. "
            "When omitted, the Yocto build BL2 ELF is used if present."
        ),
    )
    parser.add_argument(
        "--rse-bl1-2-elf",
        type=Path,
        help=(
            "Optional RSE TF-M BL1_2 ELF used to resolve the LMS verify hook "
            "symbol. When omitted, the runner uses bl1_2.elf next to the "
            "selected BL2 ELF, then the Yocto default."
        ),
    )
    parser.add_argument(
        "--rootfs",
        type=Path,
        default=deploy / "baremetal-image-fvp-rd-aspen.wic",
        help="FVP ros.virtio_block0 image.",
    )
    parser.add_argument(
        "--rootfs-bootargs-profile",
        choices=["none", "quiet-console", "verbose-console"],
        default="none",
        help=(
            "Copy the WIC rootfs into the run directory and patch "
            "loader/entries/boot.conf. quiet-console keeps ttyAMA0 console "
            "without initcall_debug/ignore_loglevel; verbose-console also "
            "adds earlycon and verbose initcall logging."
        ),
    )
    parser.add_argument(
        "--rootfs-maxcpus",
        type=int,
        help=(
            "Replace any maxcpus= boot argument when patching the rootfs "
            "boot entry. Omit to retain the lower-level runner's legacy "
            "behavior of removing maxcpus=."
        ),
    )
    parser.add_argument(
        "--efi-capsule-disk",
        type=Path,
        default=deploy / "efi-capsule-update-disk-image-fvp-rd-aspen.img",
        help="FVP ros.virtio_block1 image used by the Apollo U-Boot FWU flow.",
    )
    parser.add_argument(
        "--provisioning-bundle",
        type=Path,
        default=deploy / "combined_provisioning_message.bin",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "build/qbox-apollo-fvp" / f"rse-{timestamp()}",
    )
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    parser.add_argument(
        "--qbox-build-dir",
        type=Path,
        help=(
            "QBox CMake build directory. Defaults to "
            "build/local-apollo-fvp/work/qbox-platform."
        ),
    )
    parser.add_argument(
        "--scp-strategy",
        choices=["service-model", "real-si-scp"],
        default="service-model",
    )
    parser.add_argument(
        "--smmu-backend",
        choices=["qemu-arm-smmuv3", "systemc-mmu720ae"],
        default="systemc-mmu720ae",
        help="SMMU backend used by the AP side of the Apollo Lua platform.",
    )
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument(
        "--no-copy-writable-flash",
        action="store_true",
        help="Use deploy flash/OTP images directly instead of per-run copies.",
    )
    parser.add_argument(
        "--allow-blank-rse-otp",
        action="store_true",
        help=(
            "Allow launching with an all-zero RSE OTP image. This is only "
            "useful for explicit LCM/provisioning experiments; normal SE "
            "fast boot requires a provisioned OTP image."
        ),
    )
    parser.add_argument(
        "--no-init-rse-fwu-metadata",
        action="store_true",
        help=(
            "Do not initialize the per-run RSE flash FWU private metadata "
            "copy at offset 0x5000."
        ),
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate inputs and write result.json without launching QBox.",
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="Build required QBox targets and exit before artifact validation.",
    )
    parser.add_argument(
        "--platform-param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help=(
            "Additional QBox CCI parameter passed as '-p KEY=VALUE'. "
            "Use this for CPU gdb_port settings and other runtime-only "
            "debug knobs."
        ),
    )
    parser.add_argument(
        "--host-gdb-script",
        type=Path,
        help=(
            "Run platforms-vp under host gdb with the given command file. "
            "This is useful when ptrace_scope blocks attaching to an already "
            "running QBox process."
        ),
    )
    parser.add_argument(
        "--ignore-fail-patterns",
        action="store_true",
        help=(
            "Keep QBox running until timeout even if console fail patterns are "
            "observed. This is intended for GDB/debug sessions; result.json "
            "still records the matched fail patterns."
        ),
    )
    parser.add_argument(
        "--post-login-probe",
        action="store_true",
        help=(
            "Log in on the primary UART and run bounded Linux driver and "
            "service probes before accepting a full-system pass."
        ),
    )
    parser.add_argument("--primary-operation-manifest", type=Path)
    parser.add_argument("--primary-operation-schema", type=Path)
    parser.add_argument("--primary-operation-module-path", type=Path)
    parser.add_argument(
        "--secure-service-probe",
        action="store_true",
        help=(
            "Run bounded Trusted Services userspace "
            "checks for SE-Proxy, PSA Initial Attestation, ITS, PS, and UEFI "
            "variable paths. Results are recorded in result.json and do not "
            "change the boot pass criteria."
        ),
    )
    parser.add_argument(
        "--secure-service-probe-timeout",
        type=int,
        default=20,
        help="Per-command timeout in seconds for --secure-service-probe.",
    )
    parser.add_argument(
        "--secure-service-probe-tests",
        default="all",
        help=(
            "Comma-separated secure-service tests to run after diagnostics. "
            "Use all, none, or any of: ts, iat, its, ps, uefi. This allows "
            "PS-only runs that match the FVP comparison probes."
        ),
    )
    parser.add_argument(
        "--secure-service-ps-test-list",
        type=parse_psa_test_list,
        default="",
        help=(
            "Optional PSA Architecture Test Suite -t list for "
            "psa-ps-api-test, for example 'test_403;'. Use with "
            "--secure-service-probe-tests ps to focus short-timeout PS "
            "debug runs on one protected-storage test."
        ),
    )
    parser.add_argument(
        "--fwu-probe",
        action="store_true",
        help=(
            "Run the Apollo capsule-on-disk FWU "
            "setup sequence, reboot, and log-marker evaluation for bank-1 "
            "RSE/TF-A/U-Boot progress."
        ),
    )
    parser.add_argument(
        "--fwu-system-running-timeout",
        type=int,
        default=180,
        help=(
            "Timeout in seconds for the FWU probe's systemctl "
            "is-system-running wait before mounting/copying the capsule."
        ),
    )
    parser.add_argument(
        "--keep-running-after-pass",
        action="store_true",
        help=(
            "Do not stop immediately after the normal pass condition or "
            "post-login probe completion. This is intended for bounded GDB "
            "debug sessions that need the target to remain attachable."
        ),
    )
    parser.add_argument(
        "--required-pass-marker",
        action="append",
        nargs=2,
        default=[],
        metavar=("FILE", "MARKER"),
        help=(
            "Require MARKER to appear in FILE before the normal pass "
            "condition may stop QBox. May be specified more than once."
        ),
    )
    parser.add_argument(
        "--rse-sram-dmi-smoke-grace-s",
        type=float,
        default=5.0,
        help=(
            "Seconds to keep the platform running after the RSE SRAM-DMI smoke "
            "marker before stopping, so QBox hotpath profiles capture the "
            "completed BL2 load/hash accelerator work."
        ),
    )
    parser.add_argument("--login-user", default="root")
    parser.add_argument("--primary-login-prompt", default="fvp-rd-aspen login:")
    parser.add_argument("--primary-shell-marker", default="root@fvp-rd-aspen")
    parser.add_argument(
        "--primary-shell-prompt-re",
        default=r"root@fvp-rd-aspen[^\n]*[#>]\s*$",
        help="Regex that indicates the primary console shell is ready.",
    )
    parser.add_argument(
        "--qemu-trace",
        action="store_true",
        help="Enable QEMU in_asm/int/mmu/unimp/guest_errors trace output.",
    )
    parser.add_argument(
        "--qemu-trace-events",
        default="in_asm,int,mmu,unimp,guest_errors",
        help="QEMU -d trace event list used when QEMU tracing is enabled.",
    )
    parser.add_argument(
        "--qemu-trace-filter",
        help=(
            "Optional QEMU -dfilter range list. This also enables QEMU trace "
            "output."
        ),
    )
    parser.add_argument(
        "--boot-enc-trace",
        action="store_true",
        help=(
            "Enable QEMU in_asm trace for the BL2 boot_enc AES-KW/AES-CTR "
            "path and classify which boot_enc function ranges executed."
        ),
    )
    flash_dmi_group = parser.add_mutually_exclusive_group()
    flash_dmi_group.add_argument(
        "--range-limited-flash-dmi",
        dest="range_limited_flash_dmi",
        action="store_true",
        help=(
            "Enable the storage-safe fast path: ATU DMI, host-memory DMI, "
            "RSE boot-flash DMI limited to 0x7000:0x260000, and AP flash "
            "DMI limited to 0x7000:0x240000. Full-device boot-flash DMI is "
            "avoided because it can break TF-M ITS initialization."
        ),
    )
    flash_dmi_group.add_argument(
        "--no-range-limited-flash-dmi",
        dest="range_limited_flash_dmi",
        action="store_false",
        help=(
            "Disable range-limited flash, ATU, and host-memory DMI even when "
            "the RSE SRAM-DMI preset is selected."
        ),
    )
    parser.set_defaults(range_limited_flash_dmi=None)
    parser.add_argument(
        "--cc3xx-stats",
        action="store_true",
        help=(
            "Enable aggregate CC3XX statistics in the QBox run directory for "
            "RSE BL1_2 validation slow-path analysis."
        ),
    )
    parser.add_argument(
        "--qbox-perf-profile",
        action="store_true",
        help=(
            "Enable QBox-side performance profile artifacts for QEMU "
            "initiator path and QEMU-native CC3XX. "
            "This also enables CC3XX timing stats in rse-cc3xx-stats.json."
        ),
    )
    parser.add_argument(
        "--qbox-perf-profile-interval",
        type=int,
        default=1024,
        help=(
            "Flush QBox performance profile JSON files every N profiled "
            "events when --qbox-perf-profile is enabled."
        ),
    )
    parser.add_argument(
        "--rse-hotpath-accel",
        action="store_true",
        help=(
            "Enable opt-in QBox semantic acceleration for known RSE BL1_1 "
            "memcpy/memset loop heads. This targets the RSE BL2 image "
            "validation slow path and falls back to normal QEMU execution "
            "when the active PC or DMI range does not match."
        ),
    )
    parser.add_argument(
        "--rse-hotpath-memcpy-addr",
        type=lambda value: int(value, 0),
        help="Override RSE hotpath memcpy Thumb entry address.",
    )
    parser.add_argument(
        "--rse-hotpath-memset-addr",
        type=lambda value: int(value, 0),
        help="Override RSE hotpath memset Thumb entry address.",
    )
    parser.add_argument(
        "--rse-bl2-libc-hotpath",
        action="store_true",
        help=(
            "Use the active RSE BL2 ELF memcpy/memset symbols for "
            "--rse-hotpath-accel. This targets TF-M BL2 libc loops instead "
            "of the BL1_1 defaults."
        ),
    )
    parser.add_argument(
        "--rse-hotpath-max-bytes",
        type=int,
        default=16 * 1024 * 1024,
        help=(
            "Maximum byte count accepted by --rse-hotpath-accel for one "
            "semantic memcpy/memset operation."
        ),
    )
    parser.add_argument(
        "--rse-lms-accel",
        action="store_true",
        help=(
            "Enable experimental opt-in RSE BL1_2 LMS verify semantic "
            "acceleration. The QEMU TCG PC-entry hook validates the fixed "
            "LMS/LMOTS signature in host code when it observes the verify "
            "function entry PC, then falls back to normal firmware execution "
            "on PC, input length, DMI, or signature mismatch. Check "
            "qbox_perf_profile.rse_hotpath_profile.stats.lms_hits to confirm "
            "it was effective."
        ),
    )
    parser.add_argument(
        "--rse-lms-max-data-bytes",
        type=int,
        default=16 * 1024 * 1024,
        help="Maximum message byte count accepted by --rse-lms-accel.",
    )
    parser.add_argument(
        "--rse-lms-verify-addr",
        type=lambda value: int(value, 0),
        help=(
            "Override RSE BL1_2 pq_crypto_verify Thumb entry address for "
            "--rse-lms-accel."
        ),
    )
    parser.add_argument(
        "--rse-bl2-load-profile",
        action="store_true",
        help=(
            "Record opt-in RSE BL2 image load/decrypt/validate function "
            "entry samples in qbox_perf_profile/rse-hotpath-profile.json. "
            "This is profiling only and does not skip guest firmware code."
        ),
    )
    parser.add_argument(
        "--rse-bl2-boot-go-for-image-id-addr",
        type=lambda value: int(value, 0),
        help="Override RSE BL2 boot_go_for_image_id Thumb entry address.",
    )
    parser.add_argument(
        "--rse-bl2-boot-load-image-to-sram-addr",
        type=lambda value: int(value, 0),
        help="Override RSE BL2 boot_load_image_to_sram Thumb entry address.",
    )
    parser.add_argument(
        "--rse-bl2-boot-enc-load-addr",
        type=lambda value: int(value, 0),
        help="Override RSE BL2 boot_enc_load Thumb entry address.",
    )
    parser.add_argument(
        "--rse-bl2-boot-enc-set-key-addr",
        type=lambda value: int(value, 0),
        help="Override RSE BL2 boot_enc_set_key Thumb entry address.",
    )
    parser.add_argument(
        "--rse-bl2-boot-enc-decrypt-addr",
        type=lambda value: int(value, 0),
        help="Override RSE BL2 boot_enc_decrypt Thumb entry address.",
    )
    parser.add_argument(
        "--rse-bl2-bootutil-img-validate-addr",
        type=lambda value: int(value, 0),
        help="Override RSE BL2 bootutil_img_validate Thumb entry address.",
    )
    parser.add_argument(
        "--rse-bl2-bootutil-img-hash-addr",
        type=lambda value: int(value, 0),
        help="Override RSE BL2 bootutil_img_hash Thumb entry address.",
    )
    parser.add_argument(
        "--rse-bl2-bootutil-verify-sig-addr",
        type=lambda value: int(value, 0),
        help="Override RSE BL2 bootutil_verify_sig Thumb entry address.",
    )
    parser.add_argument(
        "--rse-bl2-bootutil-keys-addr",
        type=lambda value: int(value, 0),
        help="Override RSE BL2 bootutil_keys address.",
    )
    parser.add_argument(
        "--rse-bl2-bootutil-key-cnt-addr",
        type=lambda value: int(value, 0),
        help="Override RSE BL2 bootutil_key_cnt address.",
    )
    parser.add_argument(
        "--rse-bl2-fih-success-addr",
        type=lambda value: int(value, 0),
        help="Override RSE BL2 FIH_SUCCESS address.",
    )
    parser.add_argument(
        "--rse-bl2-boot-image-count",
        type=int,
        default=RSE_BL2_BOOT_STATE_LAYOUT_DEFAULTS["image_count"],
        help="MCUBoot BOOT_IMAGE_NUMBER for BL2 boot_loader_state snapshots.",
    )
    parser.add_argument(
        "--rse-bl2-boot-state-curr-img-offset",
        type=lambda value: int(value, 0),
        default=RSE_BL2_BOOT_STATE_LAYOUT_DEFAULTS["curr_img_offset"],
        help="Offset of boot_loader_state.curr_img_idx for BL2 RAM-load snapshots.",
    )
    parser.add_argument(
        "--rse-bl2-boot-state-imgs-offset",
        type=lambda value: int(value, 0),
        default=RSE_BL2_BOOT_STATE_LAYOUT_DEFAULTS["imgs_offset"],
        help="Offset of boot_loader_state.imgs for BL2 RAM-load snapshots.",
    )
    parser.add_argument(
        "--rse-bl2-boot-state-image-stride",
        type=int,
        default=RSE_BL2_BOOT_STATE_LAYOUT_DEFAULTS["image_stride"],
        help="Stride between boot_loader_state.imgs image entries.",
    )
    parser.add_argument(
        "--rse-bl2-boot-state-slot-stride",
        type=int,
        default=RSE_BL2_BOOT_STATE_LAYOUT_DEFAULTS["slot_stride"],
        help="Stride between boot_loader_state.imgs slot entries.",
    )
    parser.add_argument(
        "--rse-bl2-boot-state-slot-usage-offset",
        type=lambda value: int(value, 0),
        default=RSE_BL2_BOOT_STATE_LAYOUT_DEFAULTS["slot_usage_offset"],
        help="Offset of boot_loader_state.slot_usage.",
    )
    parser.add_argument(
        "--rse-bl2-boot-state-slot-usage-stride",
        type=int,
        default=RSE_BL2_BOOT_STATE_LAYOUT_DEFAULTS["slot_usage_stride"],
        help="Stride between boot_loader_state.slot_usage entries.",
    )
    parser.add_argument(
        "--rse-bl2-boot-slot-usage-img-dst-offset",
        type=lambda value: int(value, 0),
        default=RSE_BL2_BOOT_STATE_LAYOUT_DEFAULTS["slot_usage_img_dst_offset"],
        help="Offset of slot_usage_t.img_dst.",
    )
    parser.add_argument(
        "--rse-bl2-boot-slot-usage-img-sz-offset",
        type=lambda value: int(value, 0),
        default=RSE_BL2_BOOT_STATE_LAYOUT_DEFAULTS["slot_usage_img_sz_offset"],
        help="Offset of slot_usage_t.img_sz.",
    )
    parser.add_argument(
        "--rse-bl2-boot-enc-accel",
        action="store_true",
        help=(
            "Enable opt-in RSE BL2 boot_enc_decrypt acceleration. The hook "
            "captures the AES key at boot_enc_set_key, decrypts only matching "
            "boot_enc_decrypt chunks with the same AES-CTR algorithm, and "
            "falls back to guest firmware execution on any mismatch."
        ),
    )
    parser.add_argument(
        "--rse-bl2-load-accel",
        action="store_true",
        help=(
            "Enable opt-in RSE BL2 RAM-load payload acceleration. The hook "
            "uses the boot_load_image_to_sram snapshot and the key captured at "
            "boot_enc_set_key to decrypt one supported RAM_LOAD AES-128 image "
            "payload in host code, then skips only the remaining decrypt calls "
            "for that already-decrypted image."
        ),
    )
    parser.add_argument(
        "--rse-bl2-load-accel-max-bytes",
        type=int,
        default=16 * 1024 * 1024,
        help="Maximum payload byte count accepted by --rse-bl2-load-accel.",
    )
    parser.add_argument(
        "--rse-bl2-boot-status-enckey-offset",
        type=lambda value: int(value, 0),
        default=0x0C,
        help="Offset of struct boot_status.enckey in the active RSE BL2 build.",
    )
    parser.add_argument(
        "--rse-bl2-boot-enc-key-bytes",
        type=int,
        default=16,
        help="AES key byte count used by RSE BL2 encrypted images.",
    )
    parser.add_argument(
        "--rse-bl2-boot-enc-key-stride",
        type=int,
        default=16,
        help="Byte stride between boot_status.enckey slots.",
    )
    parser.add_argument(
        "--rse-bl2-boot-enc-slots",
        type=int,
        default=2,
        help="Number of encrypted image slots in struct boot_status.enckey.",
    )
    parser.add_argument(
        "--rse-bl2-boot-enc-max-bytes",
        type=int,
        default=4096,
        help="Maximum byte count accepted by --rse-bl2-boot-enc-accel.",
    )
    parser.add_argument(
        "--rse-bl2-img-hash-accel",
        action="store_true",
        help=(
            "Enable opt-in RSE BL2 bootutil_img_hash acceleration. The hook "
            "computes the MCUBoot RAM_LOAD SHA256 in host code, writes the "
            "guest hash result buffer, and leaves signature and rollback "
            "counter verification on the normal guest firmware path."
        ),
    )
    parser.add_argument(
        "--rse-bl2-img-hash-max-bytes",
        type=int,
        default=16 * 1024 * 1024,
        help="Maximum image hash byte count accepted by --rse-bl2-img-hash-accel.",
    )
    parser.add_argument(
        "--rse-bl2-img-hash-max-seed-bytes",
        type=int,
        default=4096,
        help="Maximum optional seed byte count accepted by --rse-bl2-img-hash-accel.",
    )
    parser.add_argument(
        "--rse-bl2-verify-sig-accel",
        action="store_true",
        help=(
            "Enable opt-in RSE BL2 bootutil_verify_sig host verification. The "
            "QEMU TCG PC-entry hook reads bootutil_keys, hash, and DER "
            "signature from guest memory and performs host-native ECDSA-P256 "
            "verification for profiling. Guest firmware still performs the "
            "secure-boot verification unless the low-level CCI skip switch is "
            "set manually for experiments."
        ),
    )
    parser.add_argument(
        "--rse-bl2-verify-sig-skip",
        action="store_true",
        help=(
            "After host-native ECDSA verification succeeds, skip the guest "
            "bootutil_verify_sig body by returning FIH_SUCCESS. This is a "
            "positive-boot performance experiment and must stay disabled for "
            "negative secure-boot, FWU, and fidelity evidence."
        ),
    )
    parser.add_argument(
        "--rse-bl2-verify-sig-max-key-bytes",
        type=int,
        default=512,
        help="Maximum public-key byte count accepted by --rse-bl2-verify-sig-accel.",
    )
    parser.add_argument(
        "--rse-bl2-verify-sig-max-sig-bytes",
        type=int,
        default=128,
        help="Maximum DER signature byte count accepted by --rse-bl2-verify-sig-accel.",
    )
    parser.add_argument(
        "--rse-bl2-delay-accel",
        action="store_true",
        help=(
            "Enable opt-in RSE BL2 delay_cycles acceleration. By default the "
            "hook skips the LBIST and MBIST mimic loops while preserving the "
            "SI startup wait without changing TF-M binaries."
        ),
    )
    parser.add_argument(
        "--rse-bl2-delay-cycles-addr",
        type=lambda value: int(value, 0),
        help="Override effective RSE BL2 delay_cycles hook PC.",
    )
    parser.add_argument(
        "--rse-bl2-delay-max-cycles",
        type=int,
        default=50 * 1000 * 1000,
        help="Maximum cycle count accepted by --rse-bl2-delay-accel.",
    )
    parser.add_argument(
        "--rse-bl2-delay-expected-hits",
        type=int,
        default=2,
        help=(
            "Clear the BL2 delay PC watch after this many successful skips. "
            "The default preserves the third, SI startup wait; use 0 to keep the watch armed."
        ),
    )
    parser.add_argument(
        "--rse-direct-si-sram-alias",
        action="store_true",
        help=(
            "Install opt-in QEMU direct file-backed aliases for the RSE view "
            "of SI CL0/CL1 image header and payload SRAM windows. This targets "
            "RSE BL2 SI image loading overhead and bypasses "
            "ATU/SystemC routing only for those narrow ranges."
        ),
    )
    parser.add_argument(
        "--rse-direct-si-sram-code-alias-size",
        type=int,
        default=0,
        help=(
            "Override per-cluster code payload alias size for "
            "--rse-direct-si-sram-alias. The default 0 computes the size from "
            "the current rse-flash MCUBoot headers and rounds up to 4KiB."
        ),
    )
    parser.add_argument(
        "--rse-direct-ap-bl2-alias",
        action="store_true",
        help=(
            "Install opt-in QEMU direct file-backed aliases for the RSE AP "
            "BL2 RAM-load header and payload windows. The header maps to "
            "host-ap-bl2-header-sram.bin offset 0x1c00 and the payload maps "
            "to host-ap-shared-sram.bin offset 0x82000 to match the TF-M AP "
            "BL2 ATU layout."
        ),
    )
    parser.add_argument(
        "--rse-direct-ap-bl2-code-alias-size",
        type=int,
        default=0,
        help=(
            "Override AP BL2 payload alias size for --rse-direct-ap-bl2-alias. "
            "The default 0 computes the size from the current AP flash "
            "MCUBoot header and rounds up to 4KiB."
        ),
    )
    parser.add_argument(
        "--rse-direct-rse-flash-alias",
        action="store_true",
        help=(
            "Install opt-in read-only QEMU direct file aliases for valid "
            "MCUBoot image read ranges and the pre-primary scan window in "
            "RSE boot flash. Empty secondary slots and FWU metadata outside "
            "that scan window remain on the flash model."
        ),
    )
    parser.add_argument(
        "--rse-direct-ap-fip-alias",
        action="store_true",
        help=(
            "Install an opt-in read-only QEMU direct file alias for the active "
            "AP flash FIP slot as seen through the RSE AP-flash ATU window."
        ),
    )
    parser.add_argument(
        "--rse-fast-boot-aliases",
        action="store_true",
        help=(
            "Enable the validated QBox RSE fast-boot alias set: SI SRAM, AP "
            "BL2 RAM-load, RSE boot-flash image reads, AP FIP reads, and the "
            "RSE PS/ITS storage direct-MMIO fastpath. This is a "
            "performance/fidelity tradeoff preset and does not bypass "
            "signature, hash, or CFI flash command success checks."
        ),
    )
    parser.add_argument(
        "--rse-fast-boot-sram-dmi",
        action="store_true",
        help=(
            "Enable the RSE fast-boot SRAM DMI/shared-memory preset. This sets "
            "range-limited flash DMI, host SI SRAM DMI/shared memory, RSE "
            "storage direct fastpath without enabling direct file-backed "
            "SRAM/AP-BL2 aliases."
        ),
    )
    parser.add_argument(
        "--rse-sram-dmi-smoke",
        action="store_true",
        help=(
            "Allow the RSE SRAM-DMI smoke marker to satisfy the runner pass "
            "condition. This is only for bounded RSE-focused smoke runs; "
            "post-login, secure-service, and FWU probes must complete through "
            "their normal full-system criteria."
        ),
    )
    parser.add_argument(
        "--rse-storage-direct-fastpath",
        action="store_true",
        help=(
            "Use QBox local direct MMIO calls for the RSE boot-flash PS/ITS "
            "storage window. The Strata CFI model remains active, but QEMU "
            "does not bounce each byte access through run_on_sysc."
        ),
    )
    parser.add_argument(
        "--rse-direct-file-aliases",
        default="",
        help=(
            "Override direct file aliases with a semicolon-separated "
            "addr:size:file_offset:ro|rw:path spec."
        ),
    )
    parser.add_argument(
        "--cc3xx-stats-interval",
        type=int,
        default=1024,
        help=(
            "Write CC3XX statistics every N target accesses when "
            "--cc3xx-stats is enabled."
        ),
    )
    parser.add_argument(
        "--cc3xx-status-read-fastpath",
        action="store_true",
        help=(
            "Enable an opt-in QEMU-side MMIO read fast path for RSE CC3XX "
            "ready/status registers. Writes and data-path reads still go "
            "through the SystemC CC3XX model."
        ),
    )
    parser.add_argument(
        "--cc3xx-qemu-native-backend",
        action="store_true",
        help=(
            "Use the QEMU-native RSE CC3XX backend. It reuses the shared "
            "cc3xx_core model but exposes the register window as a QEMU "
            "MemoryRegion and enables the CC3XX direct MMIO fast path to "
            "remove the per-MMIO run_on_sysc bridge."
        ),
    )
    parser.add_argument(
        "--cc3xx-local-mmio-fastpath",
        action="store_true",
        help=(
            "Enable an opt-in QEMU-local direct TLM fast path for the RSE "
            "CC3XX MMIO window. This preserves the CC3XX model side effects "
            "but skips the run_on_sysc bridge for that window."
        ),
    )
    parser.add_argument(
        "--pc-trace",
        action="store_true",
        help="Enable lightweight file-backed RSE Cortex-M55 PC sampling.",
    )
    parser.add_argument(
        "--pc-trace-interval",
        type=int,
        default=1,
        help="Emit one RSE PC sample every N CPU loop sync points when --pc-trace is used.",
    )
    parser.add_argument(
        "--pc-trace-limit",
        type=int,
        default=4096,
        help="Maximum RSE PC samples to record when --pc-trace is used.",
    )
    parser.add_argument(
        "--exception-trace",
        action="store_true",
        help="Include Arm M-profile RSE and AArch64 AP register state in PC samples.",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    root = workspace_root()
    parser = build_parser()
    args = parser.parse_args(argv)
    operation_args = (
        args.primary_operation_manifest,
        args.primary_operation_schema,
        args.primary_operation_module_path,
    )
    if any(value is not None for value in operation_args) and not all(
        value is not None for value in operation_args
    ):
        parser.error(
            "--primary-operation-manifest, --primary-operation-schema, and "
            "--primary-operation-module-path must be used together"
        )
    required_marker_error = required_pass_marker_argument_error(
        args.required_pass_marker
    )
    if required_marker_error:
        parser.error(required_marker_error)
    if args.qbox_build_dir is not None:
        resolved_qbox_build_dir = str(args.qbox_build_dir.resolve())
        os.environ["QBOX_PLATFORM_BUILD_DIR"] = resolved_qbox_build_dir
        os.environ["QBOX_BUILD_DIR"] = resolved_qbox_build_dir
    try:
        args.secure_service_probe_tests = parse_secure_service_tests(
            args.secure_service_probe_tests
        )
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
    if args.exception_trace:
        args.pc_trace = True
    if args.secure_service_probe or args.fwu_probe:
        args.post_login_probe = True
    if args.rse_sram_dmi_smoke:
        conflicts = [
            name
            for name, enabled in (
                ("--post-login-probe", args.post_login_probe),
                ("--secure-service-probe", args.secure_service_probe),
                ("--fwu-probe", args.fwu_probe),
            )
            if enabled
        ]
        if conflicts:
            parser.error(
                "--rse-sram-dmi-smoke cannot be used with "
                + ", ".join(conflicts)
            )
    if args.qemu_trace_filter or args.boot_enc_trace:
        args.qemu_trace = True
    if (args.cc3xx_stats or args.qbox_perf_profile) and args.cc3xx_stats_interval <= 0:
        parser.error("--cc3xx-stats-interval must be positive")
    if args.qbox_perf_profile and args.qbox_perf_profile_interval <= 0:
        parser.error("--qbox-perf-profile-interval must be positive")
    if args.rootfs_maxcpus is not None and not 1 <= args.rootfs_maxcpus <= 16:
        parser.error("--rootfs-maxcpus must be 1..16")
    if args.rse_hotpath_max_bytes <= 0:
        parser.error("--rse-hotpath-max-bytes must be positive")
    if args.rse_hotpath_memcpy_addr is not None and args.rse_hotpath_memcpy_addr <= 0:
        parser.error("--rse-hotpath-memcpy-addr must be positive")
    if args.rse_hotpath_memset_addr is not None and args.rse_hotpath_memset_addr <= 0:
        parser.error("--rse-hotpath-memset-addr must be positive")
    if args.rse_lms_max_data_bytes <= 0:
        parser.error("--rse-lms-max-data-bytes must be positive")
    if args.rse_lms_verify_addr is not None and args.rse_lms_verify_addr <= 0:
        parser.error("--rse-lms-verify-addr must be positive")
    if args.rse_bl2_boot_enc_key_bytes not in (16, 24, 32):
        parser.error("--rse-bl2-boot-enc-key-bytes must be 16, 24, or 32")
    if args.rse_bl2_boot_enc_key_stride < args.rse_bl2_boot_enc_key_bytes:
        parser.error("--rse-bl2-boot-enc-key-stride must be >= key bytes")
    if args.rse_bl2_boot_enc_slots <= 0:
        parser.error("--rse-bl2-boot-enc-slots must be positive")
    if args.rse_bl2_boot_enc_max_bytes <= 0:
        parser.error("--rse-bl2-boot-enc-max-bytes must be positive")
    if args.rse_bl2_load_accel_max_bytes <= 0:
        parser.error("--rse-bl2-load-accel-max-bytes must be positive")
    if args.rse_bl2_img_hash_max_bytes <= 0:
        parser.error("--rse-bl2-img-hash-max-bytes must be positive")
    if args.rse_bl2_img_hash_max_seed_bytes < 0:
        parser.error("--rse-bl2-img-hash-max-seed-bytes must be non-negative")
    if args.rse_bl2_verify_sig_max_key_bytes <= 0:
        parser.error("--rse-bl2-verify-sig-max-key-bytes must be positive")
    if args.rse_bl2_verify_sig_max_sig_bytes <= 0:
        parser.error("--rse-bl2-verify-sig-max-sig-bytes must be positive")
    if args.rse_bl2_delay_max_cycles <= 0:
        parser.error("--rse-bl2-delay-max-cycles must be positive")
    if args.rse_bl2_delay_expected_hits < 0:
        parser.error("--rse-bl2-delay-expected-hits must be non-negative")
    if args.rse_bl2_boot_image_count <= 0:
        parser.error("--rse-bl2-boot-image-count must be positive")
    if args.rse_bl2_boot_state_image_stride <= 0:
        parser.error("--rse-bl2-boot-state-image-stride must be positive")
    if args.rse_bl2_boot_state_slot_stride <= 0:
        parser.error("--rse-bl2-boot-state-slot-stride must be positive")
    if args.rse_bl2_boot_state_slot_usage_stride <= 0:
        parser.error("--rse-bl2-boot-state-slot-usage-stride must be positive")
    if args.rse_bl2_verify_sig_skip:
        args.rse_bl2_verify_sig_accel = True
    if args.rse_direct_si_sram_code_alias_size < 0:
        parser.error("--rse-direct-si-sram-code-alias-size must be non-negative")
    if args.rse_direct_ap_bl2_code_alias_size < 0:
        parser.error("--rse-direct-ap-bl2-code-alias-size must be non-negative")
    if args.rse_fast_boot_sram_dmi:
        conflicts = [
            name
            for name, enabled in (
                ("--rse-fast-boot-aliases", args.rse_fast_boot_aliases),
                ("--rse-direct-si-sram-alias", args.rse_direct_si_sram_alias),
                ("--rse-direct-ap-bl2-alias", args.rse_direct_ap_bl2_alias),
                ("--rse-direct-file-aliases", bool(args.rse_direct_file_aliases)),
            )
            if enabled
        ]
        if conflicts:
            parser.error(
                "--rse-fast-boot-sram-dmi cannot be used with "
                + ", ".join(conflicts)
            )
        ambient_conflicts = [
            name for name in SRAM_DMI_FORBIDDEN_ENV if os.environ.get(name)
        ]
        if ambient_conflicts:
            parser.error(
                "--rse-fast-boot-sram-dmi forbids ambient direct-alias/map-file "
                "environment overrides: "
                + ", ".join(ambient_conflicts)
            )
        if args.range_limited_flash_dmi is None:
            args.range_limited_flash_dmi = True
        args.rse_storage_direct_fastpath = True
    if args.range_limited_flash_dmi is None:
        args.range_limited_flash_dmi = False
    if args.rse_fast_boot_aliases:
        args.rse_direct_si_sram_alias = True
        args.rse_direct_ap_bl2_alias = True
        args.rse_direct_rse_flash_alias = True
        args.rse_direct_ap_fip_alias = True
        args.rse_storage_direct_fastpath = True
    if args.build_only and args.skip_build:
        parser.error("--build-only cannot be used with --skip-build")
    if args.reset_rse_flash_state and args.rse_flash_state is None:
        parser.error("--reset-rse-flash-state requires --rse-flash-state")
    if args.build_only:
        return args
    resolve_rse_bl2_hook_symbols(args, root)
    resolve_rse_bl1_2_lms_symbol(args, root)
    return args


def main(argv: list[str] | None = None) -> int:
    root = workspace_root()
    args = parse_args(argv)
    args.out_dir = args.out_dir.resolve()
    if args.ap_bl2_elf:
        args.ap_bl2_elf = args.ap_bl2_elf.resolve()
    apply_primary_console_profile(args)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.build_only:
        try:
            ensure_qbox_targets(root, args.jobs)
        except subprocess.CalledProcessError as exc:
            return exc.returncode or 1
        return 0

    artifacts = {
        "rse_rom": args.rse_rom.resolve(),
        "rse_flash": args.rse_flash.resolve(),
        "rse_otp": args.rse_otp.resolve(),
        "ap_flash": args.ap_flash.resolve(),
        "rootfs": args.rootfs.resolve(),
        "efi_capsule_disk": args.efi_capsule_disk.resolve(),
        "provisioning_bundle": args.provisioning_bundle.resolve(),
    }
    if args.ap_bl2_elf:
        artifacts["ap_bl2_elf"] = args.ap_bl2_elf

    required_artifacts = artifacts
    missing = [
        f"{name}: {path}" for name, path in required_artifacts.items() if not path.exists()
    ]
    copied: dict[str, Path] = {}
    rse_flash_state_lock: object | None = None
    args.rse_flash_state_status = {"enabled": False, "action": "ephemeral"}
    blocker = None
    command: list[str] = []
    platform_rc: int | None = None
    timed_out = False
    interrupted = False
    rse_fwu_private_metadata: dict[str, object] | None = None
    flash_image_preparation: dict[str, object] | None = None
    ap_flash_image_preparation: dict[str, object] | None = None
    rootfs_preparation: dict[str, object] | None = None
    host_si_cl0_sram: dict[str, object] | None = None
    host_si_cl0_sram_path: Path | None = None
    host_si_cl1_sram: dict[str, object] | None = None
    host_si_cl1_sram_path: Path | None = None
    host_ap_bl2_header_sram: dict[str, object] | None = None
    host_ap_bl2_header_sram_path: Path | None = None
    post_login_probe: dict[str, object] | None = None

    if missing:
        blocker = "missing_artifacts: " + "; ".join(missing)
        logs = write_placeholder_logs(args.out_dir, blocker)
        return write_result(
            args,
            artifacts,
            copied,
            logs,
            runtime_artifacts=artifacts,
            flash_image_preparation=flash_image_preparation,
            ap_flash_image_preparation=ap_flash_image_preparation,
            rootfs_preparation=rootfs_preparation,
            command=command,
            timed_out=timed_out,
            interrupted=interrupted,
            blocker=blocker,
            platform_rc=platform_rc,
            rse_fwu_private_metadata=rse_fwu_private_metadata,
            rse_pc_trace=parse_rse_pc_trace(args.out_dir, args.pc_trace),
        )

    image_dir = args.out_dir / "writable-images"
    copy = not args.no_copy_writable_flash
    if args.rse_flash_state is not None:
        try:
            (
                copied["rse_flash"],
                args.rse_flash_state_status,
                rse_flash_state_lock,
            ) = prepare_persistent_rse_flash(
                artifacts["rse_flash"],
                args.rse_flash_state,
                reset=args.reset_rse_flash_state,
                minimum_size=RSE_BOOT_FLASH_SIZE,
                storage_compatibility=rse_storage_compatibility(
                    artifacts["rse_otp"]
                ),
            )
        except RuntimeError as exc:
            blocker = str(exc)
            logs = write_placeholder_logs(args.out_dir, blocker)
            return write_result(
                args,
                artifacts,
                copied,
                logs,
                runtime_artifacts=artifacts,
                command=command,
                timed_out=timed_out,
                interrupted=interrupted,
                blocker=blocker,
                platform_rc=platform_rc,
            )
    else:
        copied["rse_flash"] = copy_if_requested(
            artifacts["rse_flash"], image_dir, copy=copy
        )
    write_json_atomic(
        args.out_dir / RSE_FLASH_STATE_STATUS_FILE,
        args.rse_flash_state_status,
    )
    copied["rse_flash"], flash_image_preparation = prepare_flash_for_qbox(
        copied["rse_flash"],
        image_dir,
        min_size=RSE_BOOT_FLASH_SIZE,
        allow_pad=copy or args.rse_flash_state is not None,
    )
    copied["rse_otp"] = copy_if_requested(artifacts["rse_otp"], image_dir, copy=copy)
    copied["ap_flash"] = copy_if_requested(artifacts["ap_flash"], image_dir, copy=copy)
    copied["ap_flash"], ap_flash_image_preparation = prepare_flash_for_qbox(
        copied["ap_flash"],
        image_dir,
        min_size=AP_BOOT_FLASH_IMAGE_SIZE,
        allow_pad=copy,
    )
    run_artifacts = dict(artifacts)
    run_artifacts.update(copied)
    try:
        run_artifacts["rootfs"], rootfs_preparation = prepare_rootfs_for_qbox(
            artifacts["rootfs"],
            image_dir,
            profile=args.rootfs_bootargs_profile,
            maxcpus=args.rootfs_maxcpus,
        )
    except RuntimeError as exc:
        blocker = str(exc)
        logs = write_placeholder_logs(args.out_dir, blocker)
        return write_result(
            args,
            artifacts,
            copied,
            logs,
            runtime_artifacts=run_artifacts,
            flash_image_preparation=flash_image_preparation,
            ap_flash_image_preparation=ap_flash_image_preparation,
            rootfs_preparation=rootfs_preparation,
            command=command,
            timed_out=timed_out,
            interrupted=interrupted,
            blocker=blocker,
            platform_rc=platform_rc,
            rse_fwu_private_metadata=rse_fwu_private_metadata,
            rse_pc_trace=parse_rse_pc_trace(args.out_dir, args.pc_trace),
        )
    if rootfs_preparation and rootfs_preparation.get("changed"):
        copied["rootfs"] = run_artifacts["rootfs"]
    run_artifacts["extra_blk1"] = artifacts["efi_capsule_disk"]
    if args.cc3xx_stats or args.qbox_perf_profile:
        run_artifacts["rse_cc3xx_stats"] = args.out_dir / RSE_CC3XX_STATS
    if args.qbox_perf_profile:
        run_artifacts["qbox_perf_profile"] = args.out_dir / QBOX_PERF_PROFILE_DIR
    if args.rse_direct_si_sram_alias:
        host_si_cl0_sram_path = prepare_sparse_file(
            args.out_dir / "host-si-cl0-sram.bin",
            HOST_SI_CL0_SRAM_WINDOW_SIZE,
        )
        run_artifacts["host_si_cl0_sram"] = host_si_cl0_sram_path
        host_si_cl1_sram_path = prepare_sparse_file(
            args.out_dir / "host-si-cl1-sram.bin",
            HOST_SI_CL1_SRAM_WINDOW_SIZE,
        )
        run_artifacts["host_si_cl1_sram"] = host_si_cl1_sram_path
    if args.rse_direct_ap_bl2_alias:
        run_artifacts["host_ap_shared_sram"] = prepare_sparse_file(
            args.out_dir / "host-ap-shared-sram.bin",
            HOST_AP_SHARED_SRAM_SIZE,
        )
    if args.rse_direct_ap_bl2_alias or env_flag("QBOX_RDASPEN_CAPTURE_HOST_AP_BL2_HEADER_SRAM"):
        host_ap_bl2_header_sram_path = prepare_sparse_file(
            args.out_dir / "host-ap-bl2-header-sram.bin",
            HOST_AP_BL2_HEADER_SRAM_SIZE,
        )
        run_artifacts["host_ap_bl2_header_sram"] = host_ap_bl2_header_sram_path
    for index in range(2, 4):
        run_artifacts[f"extra_blk{index}"] = prepare_sparse_file(
            args.out_dir / f"extra-blk{index}.raw",
            EXTRA_VIRTIO_BLK_SIZE,
        )
    rse_fwu_private_metadata = init_rse_fwu_private_metadata(
        run_artifacts["rse_flash"],
        enabled=not args.no_init_rse_fwu_metadata,
        writable_copy=copy or bool(flash_image_preparation.get("changed")),
    )

    if (
        not args.allow_blank_rse_otp
        and rse_lcm_uses_se_fast_path(args)
        and is_blank_file(run_artifacts["rse_otp"])
    ):
        blocker = (
            "blank_rse_otp_requires_provisioned_fast_boot:"
            f"{run_artifacts['rse_otp']}"
        )
        logs = write_placeholder_logs(args.out_dir, blocker)
        return write_result(
            args,
            artifacts,
            copied,
            logs,
            runtime_artifacts=run_artifacts,
            flash_image_preparation=flash_image_preparation,
            ap_flash_image_preparation=ap_flash_image_preparation,
            rootfs_preparation=rootfs_preparation,
            command=command,
            timed_out=timed_out,
            interrupted=interrupted,
            blocker=blocker,
            platform_rc=platform_rc,
            rse_fwu_private_metadata=rse_fwu_private_metadata,
            rse_pc_trace=parse_rse_pc_trace(args.out_dir, args.pc_trace),
        )

    if not args.skip_build:
        try:
            ensure_qbox_targets(root, args.jobs)
        except subprocess.CalledProcessError as exc:
            blocker = f"qbox_build_failed:{exc.returncode}"
            logs = write_placeholder_logs(args.out_dir, blocker)
            return write_result(
                args,
                artifacts,
                copied,
                logs,
                runtime_artifacts=run_artifacts,
                flash_image_preparation=flash_image_preparation,
                ap_flash_image_preparation=ap_flash_image_preparation,
                rootfs_preparation=rootfs_preparation,
                command=command,
                timed_out=timed_out,
                interrupted=interrupted,
                blocker=blocker,
                platform_rc=platform_rc,
                rse_fwu_private_metadata=rse_fwu_private_metadata,
                rse_pc_trace=parse_rse_pc_trace(args.out_dir, args.pc_trace),
            )

    if not args.conf.exists():
        blocker = f"rse_qbox_config_missing:{args.conf.resolve()}"
        logs = write_placeholder_logs(args.out_dir, blocker)
        return write_result(
            args,
            artifacts,
            copied,
            logs,
            runtime_artifacts=run_artifacts,
            flash_image_preparation=flash_image_preparation,
            ap_flash_image_preparation=ap_flash_image_preparation,
            rootfs_preparation=rootfs_preparation,
            command=command,
            timed_out=timed_out,
            interrupted=interrupted,
            blocker=blocker,
            platform_rc=platform_rc,
            rse_fwu_private_metadata=rse_fwu_private_metadata,
            rse_pc_trace=parse_rse_pc_trace(args.out_dir, args.pc_trace),
        )

    command = [
        str((qbox_build_dir(root) / "platforms-vp").resolve()),
        "-l",
        str(args.conf.resolve()),
    ]
    for param in args.platform_param:
        command.extend(["-p", qbox_platform_param_value(param)])
    if args.host_gdb_script:
        command = [
            os.environ.get("QBOX_HOST_GDB_EXEC", "gdb"),
            "-q",
            "-iex",
            "set debuginfod enabled off",
            "-x",
            str(args.host_gdb_script.resolve()),
            "--args",
        ] + command
    if args.check_only:
        blocker = "check_only_no_runtime"
        logs = write_placeholder_logs(args.out_dir, blocker)
        host_si_cl0_sram = analyze_host_si_cl0_sram(
            host_si_cl0_sram_path, run_artifacts.get("rse_flash")
        )
        host_si_cl1_sram = analyze_host_si_cl1_sram(
            host_si_cl1_sram_path, run_artifacts.get("rse_flash")
        )
        host_ap_bl2_header_sram = analyze_host_ap_bl2_header_sram(
            host_ap_bl2_header_sram_path
        )
        return write_result(
            args,
            artifacts,
            copied,
            logs,
            runtime_artifacts=run_artifacts,
            flash_image_preparation=flash_image_preparation,
            ap_flash_image_preparation=ap_flash_image_preparation,
            rootfs_preparation=rootfs_preparation,
            command=command,
            timed_out=timed_out,
            interrupted=interrupted,
            blocker=blocker,
            platform_rc=platform_rc,
            rse_fwu_private_metadata=rse_fwu_private_metadata,
            rse_pc_trace=parse_rse_pc_trace(args.out_dir, args.pc_trace),
            ap_pc_trace=parse_ap_pc_trace(args.out_dir, args.pc_trace),
            host_si_cl0_sram=host_si_cl0_sram,
            host_si_cl1_sram=host_si_cl1_sram,
            host_ap_bl2_header_sram=host_ap_bl2_header_sram,
        )

    (
        platform_rc,
        logs,
        timed_out,
        interrupted,
        runtime_elapsed_s,
        post_login_probe,
        progress_marker_first_hits,
        shared_memory_cleanup,
    ) = run_platform(
        root, args, run_artifacts
    )
    host_si_cl0_sram = analyze_host_si_cl0_sram(
        host_si_cl0_sram_path, run_artifacts.get("rse_flash")
    )
    host_si_cl1_sram = analyze_host_si_cl1_sram(
        host_si_cl1_sram_path, run_artifacts.get("rse_flash")
    )
    host_ap_bl2_header_sram = analyze_host_ap_bl2_header_sram(
        host_ap_bl2_header_sram_path
    )
    rse_pc_trace = parse_rse_pc_trace(args.out_dir, args.pc_trace)
    ap_pc_trace = parse_ap_pc_trace(args.out_dir, args.pc_trace)
    boot_enc_trace = parse_boot_enc_trace(root, args.out_dir, args.boot_enc_trace)
    runtime_blocker = None
    first_fault = parse_qemu_trace(args.out_dir, qemu_trace_enabled(args))
    if first_fault is None:
        first_fault = parse_platform_translation_error(args.out_dir)
    current_status = evaluate(logs, rse_sram_dmi_smoke=args.rse_sram_dmi_smoke)
    required_markers_missing = missing_required_pass_markers(
        args.required_pass_marker
    )
    required_marker_blocker = required_pass_marker_blocker(
        bool(current_status["passed"]),
        required_markers_missing,
        timed_out,
    )
    known_runtime_blocker = classify_known_runtime_blocker(logs)
    pc_trace_blocker = classify_pc_trace_blocker(root, rse_pc_trace, timed_out)
    boot_enc_trace_blocker = classify_boot_enc_trace_blocker(logs, boot_enc_trace)
    fwu_probe_incomplete = bool(
        args.fwu_probe and post_login_probe and not post_login_probe.get("complete")
    )
    secure_service_eval = (
        post_login_probe.get("secure_service_probe")
        if post_login_probe
        else {}
    )
    secure_service_incomplete = bool(
        args.secure_service_probe
        and isinstance(secure_service_eval, dict)
        and not secure_service_eval.get("done_marker")
    )
    secure_service_failures = (
        selected_secure_service_failures(
            args.secure_service_probe_tests, secure_service_eval
        )
        if args.secure_service_probe and isinstance(secure_service_eval, dict)
        else {}
    )
    if secure_service_failures and isinstance(secure_service_eval, dict):
        secure_service_eval["failed_return_codes"] = secure_service_failures
    secure_service_ps403_blocker = (
        classify_ps403_progress_blocker(secure_service_eval)
        if args.secure_service_probe and isinstance(secure_service_eval, dict)
        else None
    )
    post_login_probe_incomplete = bool(
        args.post_login_probe
        and post_login_probe
        and not post_login_probe.get("complete")
    )
    post_login_probe_not_reached = bool(
        args.post_login_probe
        and post_login_probe
        and not post_login_probe.get("sent_probe")
    )
    post_login_probe_failed = bool(
        args.post_login_probe
        and post_login_probe
        and post_login_probe.get("complete")
        and not post_login_probe.get("passed")
    )
    if post_login_probe_not_reached and timed_out:
        runtime_blocker = "qbox_post_login_probe_not_reached_timeout"
    elif post_login_probe_not_reached:
        runtime_blocker = "qbox_post_login_probe_not_reached"
    elif fwu_probe_incomplete and timed_out:
        runtime_blocker = "qbox_fwu_probe_incomplete_timeout"
    elif fwu_probe_incomplete:
        runtime_blocker = "qbox_fwu_probe_incomplete"
    elif secure_service_incomplete and timed_out and secure_service_ps403_blocker:
        runtime_blocker = secure_service_ps403_blocker
    elif secure_service_incomplete and timed_out:
        runtime_blocker = "qbox_secure_service_probe_incomplete_timeout"
    elif secure_service_incomplete:
        runtime_blocker = "qbox_secure_service_probe_incomplete"
    elif secure_service_failures:
        runtime_blocker = (
            "qbox_secure_service_probe_failed:"
            + format_rc_failures(secure_service_failures)
        )
    elif post_login_probe_failed:
        runtime_blocker = "qbox_post_login_probe_failed"
    elif post_login_probe_incomplete and timed_out:
        runtime_blocker = "qbox_post_login_probe_incomplete_timeout"
    elif post_login_probe_incomplete:
        runtime_blocker = "qbox_post_login_probe_incomplete"
    elif required_marker_blocker:
        runtime_blocker = required_marker_blocker
    elif current_status["passed"]:
        runtime_blocker = None
    elif first_fault and first_fault.get("fault_address"):
        runtime_blocker = f"rse_first_fault:{first_fault['fault_address']}"
    elif first_fault and first_fault.get("physical_address"):
        runtime_blocker = f"rse_atu_translation_error:{first_fault['physical_address']}"
    elif boot_enc_trace_blocker:
        runtime_blocker = boot_enc_trace_blocker
    elif known_runtime_blocker:
        runtime_blocker = known_runtime_blocker
    elif pc_trace_blocker:
        runtime_blocker = pc_trace_blocker
    elif timed_out:
        runtime_blocker = "qbox_platform_timeout"
    elif platform_rc != 0 and not (
        args.post_login_probe and post_login_probe.get("complete")
    ):
        runtime_blocker = f"qbox_platform_failed:{platform_rc}"
    return write_result(
        args,
        artifacts,
        copied,
        logs,
        runtime_artifacts=run_artifacts,
        first_fault=first_fault,
        flash_image_preparation=flash_image_preparation,
        ap_flash_image_preparation=ap_flash_image_preparation,
        rootfs_preparation=rootfs_preparation,
        command=command,
        timed_out=timed_out,
        interrupted=interrupted,
        blocker=runtime_blocker,
        platform_rc=platform_rc,
        runtime_elapsed_s=runtime_elapsed_s,
        rse_fwu_private_metadata=rse_fwu_private_metadata,
        rse_pc_trace=rse_pc_trace,
        ap_pc_trace=ap_pc_trace,
        host_si_cl0_sram=host_si_cl0_sram,
        host_si_cl1_sram=host_si_cl1_sram,
        host_ap_bl2_header_sram=host_ap_bl2_header_sram,
        boot_enc_trace=boot_enc_trace,
        post_login_probe=post_login_probe,
        progress_marker_first_hits=progress_marker_first_hits,
        shared_memory_cleanup=shared_memory_cleanup,
    )
