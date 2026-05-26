#!/usr/bin/env python3
"""Run or preflight the RD-Aspen RSE-oriented QBox boot path."""

from __future__ import annotations

import argparse
import datetime as _dt
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import struct
import subprocess
import sys
import time


REQUIRED_TARGETS = [
    "platforms-vp",
    "keep_alive",
    "router",
    "gs_memory",
    "host_scr",
    "loader",
    "char_backend_file",
    "char_backend_stdio",
    "uart-pl011",
    "cpu_arm_cortexA720AE",
    "arm_gicv3",
    "arm_gicv3_its",
    "qemu_gpex",
    "arm_smmuv3",
    "reset_gpio",
    "pl031",
    "sbsa_gwdt",
    "cpu_arm_cortexM55",
    "nvic_armv7m",
    "remote_cpu",
    "mhuv3_stub",
    "host_ppu",
    "cc3xx",
    "dma350",
    "rse_atu",
    "rse_integrity_checker",
    "rse_kmu",
    "rse_lcm",
    "rse_sam",
    "strata_flash_j3",
    "rse_sysctrl",
]

PLATFORM_STDOUT_LOG = "qbox-platform.log"
QEMU_TRACE_LOG = "qemu-rse-trace.log"
RSE_PC_TRACE_LOG = "rse-pc-trace.log"
RSE_STRATA_STATS = "rse-strata-stats.json"
AP_STRATA_STATS = "ap-strata-stats.json"
WIC_BOOT_PARTITION_OFFSET = 2048 * 512
WIC_BOOT_ENTRY = "::/loader/entries/boot.conf"

CONSOLE_LOGS = {
    "rse": "qbox-rse.log",
    "scp": "qbox-scp.log",
    "secure_console": "qbox-secure-console.log",
    "primary_console": "qbox-primary-console.log",
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
    "rse_first_image_slot": "Jumping to the first image slot",
    "rse_scp_power_on_ap": "RSE to SCP SCMI power on AP succeeded",
    "measured_boot_bl33": "BL_33",
    "primary_efi_mm_partition": "EFI: MM partition ID 0x8006",
    "primary_pk_enrolled": "PK key is enrolled successfully!",
    "primary_kek_enrolled": "KEK key is enrolled successfully!",
    "primary_db_enrolled": "db key is enrolled successfully!",
    "primary_dbx_enrolled": "dbx key is enrolled successfully!",
    "primary_fwu_regular_state": "FWU: System booting in Regular State",
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
}

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
    "modprobe -v arm_si_rproc timeout=500; echo arm_si_rproc_modprobe_rc:$?",
    "for d in /sys/class/remoteproc/remoteproc*; do [ -f $d/name ] && echo remoteproc_state:$(cat $d/name):$(cat $d/state); done",
    "for d in /sys/class/remoteproc/remoteproc*; do [ -f $d/state ] && [ \"$(cat $d/state)\" = detached ] && echo attach > $d/state 2>/dev/null || true; done",
    "for d in /sys/class/remoteproc/remoteproc*; do [ -f $d/name ] && echo remoteproc_state_after:$(cat $d/name):$(cat $d/state); done",
    "modprobe -v rpmsg_ns; echo rpmsg_ns_modprobe_rc:$?",
    "modprobe -v virtio_rpmsg_bus; echo virtio_rpmsg_bus_modprobe_rc:$?",
    "modprobe -v rpmsg_net; echo rpmsg_net_modprobe_rc:$?",
    "ls -l /sys/bus/virtio/devices || true",
    "ls -l /sys/bus/rpmsg/devices || true",
    "for d in /sys/bus/rpmsg/devices/*; do [ -e $d/name ] && echo rpmsg_device:$(basename $d):$(cat $d/name); done",
    "ip link show ethsi1; echo ethsi1_iplink_rc:$?",
    "ip link show || true",
    f"echo {PROBE_DONE_MARKER}",
    "dmesg | grep -Ei 'gic|its|pl011|ttyAMA|watchdog|rtc|virtio|rng|eth|scmi|mhu|smmu|remoteproc|rpmsg|pfdi|hipc|ras|pmu|dsu|timer' || true",
    "cat /proc/interrupts | grep -Ei 'uart-pl011|virtio|rtc-pl031|arch_timer|GIC|ITS|gwdt|smmu|ras|estatus|mhu|scmi|remoteproc' || true",
    "lsmod | grep -Ei 'virtio|rng|pfdi|hipc|rpmsg|remoteproc|scmi|mhu|smmu' || true",
    "modprobe -v openvswitch; echo openvswitch_modprobe_rc:$?",
    "modprobe -v pfdi_misc; echo pfdi_misc_modprobe_rc:$?",
    "systemctl is-system-running || true",
    "systemctl --failed --no-pager || true",
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
RSE_PC_TRACE_RE = re.compile(
    r"pc_trace sample=(?P<sample>\d+) seen=(?P<seen>\d+) "
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

RSE_FWU_PRIVATE_METADATA_OFFSET = 0x5000
RSE_FWU_PRIVATE_METADATA_SIZE = 68
RSE_FWU_COMPONENT_NUMBER = 5
RSE_FWU_BOOT_INDEX_SLOT0 = 0
RSE_FWU_VALID_BOOT_INDICES = {0, 1}
RSE_FWU_VALID_STATES = set(range(9))
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
EXTRA_VIRTIO_BLK_SIZE = 64 * 1024 * 1024
SI_CL0_PRIMARY_FLASH_OFFSET = 0x00067000
SI_CL0_SECONDARY_FLASH_OFFSET = 0x002C7000
SI_CL1_PRIMARY_FLASH_OFFSET = 0x00167000
SI_CL1_SECONDARY_FLASH_OFFSET = 0x003C7000
IMAGE_MAGIC = 0x96F3B83D
IMAGE_TLV_INFO_MAGIC = 0x6907
IMAGE_TLV_PROT_INFO_MAGIC = 0x6908
IMAGE_F_ENCRYPTED_AES128 = 0x00000004
IMAGE_F_ENCRYPTED_AES256 = 0x00000008
IMAGE_F_RAM_LOAD = 0x00000020
IMAGE_TLV_ENC_KW = 0x31
EXPECTED_ENC_KW_LEN_AES128 = 0x18


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    print("+ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def ensure_qbox_targets(root: Path, jobs: int) -> None:
    cmd = [
        "cmake",
        "--build",
        str(root / "tools/qbox/build"),
        "--target",
        *REQUIRED_TARGETS,
        "--parallel",
        str(jobs),
    ]
    run(cmd, cwd=root)


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


def patch_boot_entry_options(text: str, *, profile: str) -> tuple[str, str, str]:
    old_options = ""
    new_lines: list[str] = []
    patched = False
    for line in text.splitlines():
        if not patched and line.startswith("options "):
            old_options = line[len("options ") :].strip()
            tokens = [
                token
                for token in old_options.split()
                if token not in {"ignore_loglevel", "initcall_debug"}
                and not token.startswith("earlycon=")
                and not token.startswith("console=")
            ]
            tokens.append("console=ttyAMA0,115200")
            if profile == "verbose-console":
                tokens.extend(
                    [
                        "earlycon=pl011,mmio32,0x1a400000",
                        "ignore_loglevel",
                        "initcall_debug",
                    ]
                )
            new_options = " ".join(tokens)
            new_lines.append("options " + new_options)
            patched = True
            continue
        new_lines.append(line)
    if not patched:
        raise RuntimeError("boot_entry_missing_options_line")
    return "\n".join(new_lines) + "\n", old_options, new_options


def prepare_rootfs_for_qbox(
    src: Path, dst_dir: Path, *, profile: str
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
    boot_entry = read_boot_entry(dst)
    patched, old_options, new_options = patch_boot_entry_options(
        boot_entry, profile=profile
    )
    write_boot_entry(dst, patched, dst_dir)
    info.update(
        {
            "output": str(dst),
            "state": "copied_and_patched_boot_entry",
            "changed": old_options != new_options,
            "boot_entry": WIC_BOOT_ENTRY,
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
            "state": info["state"] + "_padded_to_qbox_flash_size",
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


def evaluate(logs: dict[str, str]) -> dict[str, object]:
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
    passed = all_non_linux and linux_hit and not any(fail_hits.values())
    return {
        "passed": passed,
        "marker_hits": marker_hits,
        "fail_patterns": fail_hits,
        "log_bytes": sum(len(text.encode("utf-8", errors="replace")) for text in logs.values()),
    }


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


def parse_flash_stats(args: argparse.Namespace) -> dict[str, object]:
    if not args.flash_stats:
        return {"enabled": False}

    result: dict[str, object] = {
        "enabled": True,
        "interval": args.flash_stats_interval,
    }
    for name, filename in (
        ("rse_boot_flash", RSE_STRATA_STATS),
        ("ap_flash", AP_STRATA_STATS),
    ):
        path = args.out_dir / filename
        parsed = read_json_artifact(path)
        result[name] = {
            "path": str(path.resolve()),
            "present": parsed is not None,
            "stats": parsed,
        }
    return result


def qemu_trace_enabled(args: argparse.Namespace) -> bool:
    return bool(args.qemu_trace or args.qemu_trace_filter or args.boot_enc_trace)


def default_bl2_map(root: Path) -> Path:
    return (
        root
        / "build/tmp_baremetal/work/fvp_rd_aspen-poky-linux"
        / "trusted-firmware-m/2.2.2+git/build/bin/bl2.map"
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


def parse_rse_pc_trace(out_dir: Path, enabled: bool) -> dict[str, object] | None:
    if not enabled:
        return None
    trace_path = out_dir / RSE_PC_TRACE_LOG
    if not trace_path.exists():
        return {
            "enabled": True,
            "trace_log": str(trace_path.resolve()),
            "present": False,
        }

    samples: list[dict[str, object]] = []
    line_count = 0
    for line in trace_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line_count += 1
        match = RSE_PC_TRACE_RE.search(line)
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
            "trace_log": str(trace_path.resolve()),
            "present": True,
            "line_count": line_count,
            "sample_count": 0,
        }

    unique_tail = []
    for sample in samples[-32:]:
        pc = sample["pc"]
        if pc not in unique_tail:
            unique_tail.append(pc)

    result: dict[str, object] = {
        "enabled": True,
        "trace_log": str(trace_path.resolve()),
        "present": True,
        "line_count": line_count,
        "sample_count": len(samples),
        "first_sample": samples[0],
        "last_sample": samples[-1],
        "tail_unique_pcs": unique_tail,
    }
    last_exception_state = samples[-1].get("exception_state")
    if isinstance(last_exception_state, dict):
        result["last_exception_state"] = last_exception_state
    return result


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
            f"QBox RD-Aspen RSE-oriented boot did not start.\n"
            f"console: {role}\n"
            f"reason: {reason}\n"
        )
        path.write_text(text, encoding="utf-8")
        logs[role] = text
    return logs


def probe_requires_ap_cpus(args: argparse.Namespace) -> bool:
    return bool(args.post_login_probe or args.secure_service_probe or args.fwu_probe)


def qbox_env(root: Path, args: argparse.Namespace, artifacts: dict[str, Path]) -> dict[str, str]:
    env = os.environ.copy()
    lib_paths = [
        root / "tools/qbox/build",
        root / "tools/qbox/build/_deps/libqemu-build/qemu-prefix/lib",
    ]
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
    env["QBOX_RDASPEN_AP_FLASH"] = str(artifacts["ap_flash"])
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
    env["QBOX_RDASPEN_UART_READ_FILE"] = os.devnull
    env["QBOX_REMOTE_CPU_EXEC"] = str((root / "tools/qbox/build/remote_cpu").resolve())
    extra_qemu_args = qemu_trace_args(root, args)
    if extra_qemu_args:
        env["QBOX_RDASPEN_RSE_QEMU_ARGS"] = extra_qemu_args
    if args.flash_stats:
        env["QBOX_RDASPEN_RSE_BOOT_FLASH_STATS_FILE"] = str(
            args.out_dir / RSE_STRATA_STATS
        )
        env["QBOX_RDASPEN_AP_FLASH_STATS_FILE"] = str(
            args.out_dir / AP_STRATA_STATS
        )
        env["QBOX_RDASPEN_FLASH_STATS_INTERVAL"] = str(
            args.flash_stats_interval
        )
    if args.pc_trace:
        env["QBOX_RDASPEN_RSE_PC_TRACE"] = "true"
        env["QBOX_RDASPEN_RSE_PC_TRACE_FILE"] = str(args.out_dir / RSE_PC_TRACE_LOG)
        env["QBOX_RDASPEN_RSE_PC_TRACE_INTERVAL"] = str(args.pc_trace_interval)
        env["QBOX_RDASPEN_RSE_PC_TRACE_LIMIT"] = str(args.pc_trace_limit)
        env["QBOX_RDASPEN_AP_PC_TRACE"] = "true"
        env["QBOX_RDASPEN_AP_PC_TRACE_FILE"] = str(args.out_dir / "ap-pc-trace.log")
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


def write_primary_uart(fd: int, text: str) -> None:
    os.write(fd, text.encode("utf-8"))


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
    return {
        "requested": bool(args.post_login_probe),
        "secure_service_requested": bool(args.secure_service_probe),
        "fwu_requested": bool(args.fwu_probe),
        "sent_login": False,
        "sent_probe": False,
        "complete": False,
        "input_path": None,
        "actions": [],
        "login_attempts": 0,
        "last_login_time": 0.0,
    }


def drive_post_login_probe(
    args: argparse.Namespace,
    logs: dict[str, str],
    state: dict[str, object],
    fifo_fd: int | None,
) -> None:
    if not args.post_login_probe or fifo_fd is None:
        return
    clean_primary = clean_text(logs.get("primary_console", ""))
    actions = state.setdefault("actions", [])
    assert isinstance(actions, list)
    login_ready = any(
        re.search(pattern, clean_primary, re.IGNORECASE | re.MULTILINE)
        for pattern in LOGIN_READY_PATTERNS
    )
    login_attempts = int(state.get("login_attempts", 0))
    last_login_time = float(state.get("last_login_time", 0.0))
    retry_login = (
        bool(state["sent_login"])
        and not state["sent_probe"]
        and login_ready
        and login_attempts < 6
        and time.monotonic() - last_login_time >= 5.0
    )
    if (not state["sent_login"] and login_ready) or retry_login:
        prefix = "" if "fvp-rd-aspen login:" in clean_primary else "\n"
        write_primary_uart(fifo_fd, prefix + args.login_user + "\n")
        state["sent_login"] = True
        state["login_attempts"] = login_attempts + 1
        state["last_login_time"] = time.monotonic()
        actions.append(f"sent_login_attempt_{login_attempts + 1}")
    if (
        state["sent_login"]
        and not state["sent_probe"]
        and re.search(r"root@fvp-rd-aspen[^\n]*[#>]\s*$", clean_primary, re.MULTILINE)
    ):
        write_primary_uart(fifo_fd, "\n".join(post_login_probe_commands(args)) + "\n")
        state["sent_probe"] = True
        actions.append("sent_probe")
    if PROBE_DONE_MARKER in clean_primary:
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
]:
    out_dir = args.out_dir
    cmd = [
        str((root / "tools/qbox/build/platforms-vp").resolve()),
        "-l",
        str(args.conf.resolve()),
    ]
    for param in args.platform_param:
        cmd.extend(["-p", param])
    if args.host_gdb_script:
        cmd = [
            "gdb",
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
    if args.post_login_probe:
        fifo_path, primary_uart_fd = open_post_login_probe_fifo(out_dir)
        env["QBOX_RDASPEN_PRIMARY_UART_READ_FILE"] = str(fifo_path)
        post_login_probe["input_path"] = str(fifo_path)
    timed_out = False
    interrupted = False
    logs = {role: "" for role in CONSOLE_LOGS}
    progress_marker_first_hits: dict[str, dict[str, object]] = {}
    platform_log = out_dir / PLATFORM_STDOUT_LOG
    platform_stdout = ""

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
                status = evaluate(live_logs)
                probe_complete = bool(post_login_probe.get("complete"))
                if (
                    args.post_login_probe
                    and probe_complete
                    and not args.keep_running_after_pass
                ):
                    stop_process(proc)
                    break
                if (
                    status["passed"]
                    and (not args.post_login_probe or probe_complete)
                    and not args.keep_running_after_pass
                ) or (
                    any(status["fail_patterns"].values())
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

    for role, filename in CONSOLE_LOGS.items():
        path = out_dir / filename
        if path.exists():
            logs[role] = path.read_text(encoding="utf-8", errors="replace")
            continue
        text = (
            "QBox RD-Aspen RSE-oriented boot did not create this console log.\n"
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
    probe_eval = evaluate_post_login_probe(
        logs.get("primary_console", ""),
        logs.get("secure_console", ""),
        logs.get("rse", ""),
    )
    post_login_probe.update(probe_eval)
    fwu_complete = bool(probe_eval.get("fwu_probe", {}).get("complete"))
    if (not args.fwu_probe and probe_eval.get("done_marker")) or fwu_complete:
        post_login_probe["complete"] = True
    if args.post_login_probe:
        action_log = out_dir / "post-login-probe-actions.log"
        action_lines = [
            f"requested: {post_login_probe['requested']}",
            f"secure_service_requested: {post_login_probe['secure_service_requested']}",
            f"fwu_requested: {post_login_probe['fwu_requested']}",
            f"input_path: {post_login_probe.get('input_path')}",
            f"sent_login: {post_login_probe['sent_login']}",
            f"sent_probe: {post_login_probe['sent_probe']}",
            f"complete: {post_login_probe['complete']}",
            "actions:",
            *[f"  - {action}" for action in post_login_probe.get("actions", [])],
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
    host_si_cl0_sram: dict[str, object] | None = None,
    host_si_cl1_sram: dict[str, object] | None = None,
    boot_enc_trace: dict[str, object] | None = None,
    post_login_probe: dict[str, object] | None = None,
    progress_marker_first_hits: dict[str, dict[str, object]] | None = None,
) -> int:
    out_dir = args.out_dir
    runtime_artifacts = artifacts if runtime_artifacts is None else runtime_artifacts
    status = evaluate(logs)
    if blocker:
        status["passed"] = False
    rse_boot_started = any(status["marker_hits"]["rse_boot"].values())
    rse_boot_complete = all(status["marker_hits"]["rse_boot"].values())
    rse_scp_complete = all(status["marker_hits"]["rse_scp_handoff"].values())
    ap_boot_started = bool(logs.get("secure_console", "").strip())
    ap_boot_label = (
        "functional-model"
        if status["passed"]
        else ("partial-model" if ap_boot_started else "not-modeled")
    )
    static_label = "not-modeled" if blocker else "static-map-only"
    try:
        conf_text = args.conf.read_text()
    except OSError:
        conf_text = ""
    rse_boot_media_label = (
        "cfi-strata-flash-partial-model"
        if "strata_flash_j3" in conf_text
        else ("functional-model" if rse_boot_complete else static_label)
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
    status.update(
        {
            "boot_mode": "rse-oriented",
            "scp_strategy": args.scp_strategy,
            "scp_service_model": scp_service_model,
            "fidelity_labels": {
                "rse_cortex_m55_boot": "functional-model" if rse_boot_started else static_label,
                "rse_boot_media": rse_boot_media_label,
                "rse_cc3xx": "hash-aes-cmac-modular-pka-model",
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
                "mhuv3": "temporary-stub",
                "rse_scp_endpoint": rse_scp_endpoint_label,
                "rse_oriented_ap_boot": ap_boot_label,
            },
            "input_artifacts": {name: str(path) for name, path in artifacts.items()},
            "runtime_artifacts": {name: str(path) for name, path in runtime_artifacts.items()},
            "copied_writable_artifacts": {name: str(path) for name, path in copied.items()},
            "flash_image_preparation": flash_image_preparation,
            "ap_flash_image_preparation": ap_flash_image_preparation,
            "rootfs_preparation": rootfs_preparation,
            "rse_fwu_private_metadata": rse_fwu_private_metadata,
            "host_si_cl0_sram": host_si_cl0_sram,
            "host_si_cl1_sram": host_si_cl1_sram,
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
            "flash_stats": parse_flash_stats(args),
            "rse_pc_trace": rse_pc_trace,
            "boot_enc_trace": boot_enc_trace,
            "post_login_probe": post_login_probe
            if post_login_probe is not None
            else {
                "requested": bool(args.post_login_probe),
                "secure_service_requested": bool(args.secure_service_probe),
                "fwu_requested": bool(args.fwu_probe),
                "complete": False,
                **evaluate_post_login_probe(
                    logs.get("primary_console", ""),
                    logs.get("secure_console", ""),
                    logs.get("rse", ""),
                ),
            },
            "first_failing_register_access": first_fault,
            "blocker": blocker,
            "timed_out": timed_out,
            "interrupted": interrupted,
            "platform_returncode": platform_rc,
            "runtime_elapsed_s": runtime_elapsed_s,
            "progress_marker_first_hits": progress_marker_first_hits or {},
            "command": command,
            "runner_argv": sys.argv,
        }
    )
    result_path = out_dir / "result.json"
    summary_path = out_dir / "summary.txt"
    result_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        f"passed: {status['passed']}",
        f"boot_mode: {status['boot_mode']}",
        f"scp_strategy: {status['scp_strategy']}",
        "scp_service_model: "
        + json.dumps(status["scp_service_model"], sort_keys=True),
        f"blocker: {blocker or 'none'}",
        "console_logs:",
        *[f"  - {role}: {path}" for role, path in status["console_logs"].items()],
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
                f"  - {name}: {float(hit['elapsed_s']):.3f}s "
                f"({hit['marker']})"
                for name, hit in sorted(
                    (progress_marker_first_hits or {}).items(),
                    key=lambda item: float(item[1].get("elapsed_s", 0.0)),
                )
            ]
            or ["  none"]
        ),
        f"qemu_trace_log: {status['qemu_trace_log'] or 'disabled'}",
        "flash_stats: " + json.dumps(status["flash_stats"], sort_keys=True),
        "rse_pc_trace: "
        + (
            json.dumps(rse_pc_trace, sort_keys=True)
            if rse_pc_trace
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
            json.dumps(status["post_login_probe"], sort_keys=True)
            if status.get("post_login_probe", {}).get("requested")
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
    for group, hits in status["marker_hits"].items():
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


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    deploy = root / "build/tmp_baremetal/deploy/images/fvp-rd-aspen"
    parser = argparse.ArgumentParser(
        description="Run or preflight the QBox RD-Aspen RSE-oriented boot path."
    )
    parser.add_argument(
        "--conf",
        type=Path,
        default=root / "tools/qbox/platforms/fvp-rd-aspen-rse/conf.lua",
        help="RSE-oriented QBox Lua config. Missing config is reported as an implementation blocker.",
    )
    parser.add_argument("--rse-rom", type=Path, default=deploy / "rse-rom-image.img")
    parser.add_argument("--rse-flash", type=Path, default=deploy / "rse-flash-image.img")
    parser.add_argument("--rse-otp", type=Path, default=deploy / "rse-otp-image.img")
    parser.add_argument("--ap-flash", type=Path, default=deploy / "ap-flash-image.img")
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
        "--efi-capsule-disk",
        type=Path,
        default=deploy / "efi-capsule-update-disk-image-fvp-rd-aspen.img",
        help="FVP ros.virtio_block1 image used by RD-Aspen U-Boot FWU flow.",
    )
    parser.add_argument(
        "--provisioning-bundle",
        type=Path,
        default=deploy / "combined_provisioning_message.bin",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "build/qbox-fvp-rd-aspen" / f"rse-{timestamp()}",
    )
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    parser.add_argument(
        "--scp-strategy",
        choices=["service-model", "real-si-scp"],
        default="service-model",
    )
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument(
        "--no-copy-writable-flash",
        action="store_true",
        help="Use deploy flash/OTP images directly instead of per-run copies.",
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
            "After the primary Linux UART reaches the login prompt, feed root "
            "and run driver/remoteproc/RPMsg probes through a FIFO-backed UART "
            "input file. This avoids static prefeed being consumed by U-Boot."
        ),
    )
    parser.add_argument(
        "--secure-service-probe",
        action="store_true",
        help=(
            "Extend --post-login-probe with bounded Trusted Services userspace "
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
            "Extend --post-login-probe with the RD-Aspen capsule-on-disk FWU "
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
    parser.add_argument("--login-user", default="root")
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
    parser.add_argument(
        "--flash-stats",
        action="store_true",
        help=(
            "Enable periodic Strata flash statistics files in the QBox run "
            "directory for RSE boot flash and AP flash."
        ),
    )
    parser.add_argument(
        "--flash-stats-interval",
        type=int,
        default=512,
        help=(
            "Write Strata flash statistics every N target writes when "
            "--flash-stats is enabled."
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
    args = parser.parse_args()
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
    if args.qemu_trace_filter or args.boot_enc_trace:
        args.qemu_trace = True
    if args.flash_stats and args.flash_stats_interval <= 0:
        parser.error("--flash-stats-interval must be positive")
    return args


def main() -> int:
    root = workspace_root()
    args = parse_args()
    args.out_dir = args.out_dir.resolve()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "rse_rom": args.rse_rom.resolve(),
        "rse_flash": args.rse_flash.resolve(),
        "rse_otp": args.rse_otp.resolve(),
        "ap_flash": args.ap_flash.resolve(),
        "rootfs": args.rootfs.resolve(),
        "efi_capsule_disk": args.efi_capsule_disk.resolve(),
        "provisioning_bundle": args.provisioning_bundle.resolve(),
    }

    required_artifacts = artifacts
    missing = [
        f"{name}: {path}" for name, path in required_artifacts.items() if not path.exists()
    ]
    copied: dict[str, Path] = {}
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
    copied["rse_flash"] = copy_if_requested(artifacts["rse_flash"], image_dir, copy=copy)
    copied["rse_flash"], flash_image_preparation = prepare_flash_for_qbox(
        copied["rse_flash"],
        image_dir,
        min_size=RSE_BOOT_FLASH_SIZE,
        allow_pad=copy,
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
        str((root / "tools/qbox/build/platforms-vp").resolve()),
        "-l",
        str(args.conf.resolve()),
    ]
    for param in args.platform_param:
        command.extend(["-p", param])
    if args.host_gdb_script:
        command = [
            "gdb",
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
            host_si_cl0_sram=host_si_cl0_sram,
            host_si_cl1_sram=host_si_cl1_sram,
        )

    (
        platform_rc,
        logs,
        timed_out,
        interrupted,
        runtime_elapsed_s,
        post_login_probe,
        progress_marker_first_hits,
    ) = run_platform(
        root, args, run_artifacts
    )
    host_si_cl0_sram = analyze_host_si_cl0_sram(
        host_si_cl0_sram_path, run_artifacts.get("rse_flash")
    )
    host_si_cl1_sram = analyze_host_si_cl1_sram(
        host_si_cl1_sram_path, run_artifacts.get("rse_flash")
    )
    rse_pc_trace = parse_rse_pc_trace(args.out_dir, args.pc_trace)
    boot_enc_trace = parse_boot_enc_trace(root, args.out_dir, args.boot_enc_trace)
    runtime_blocker = None
    first_fault = parse_qemu_trace(args.out_dir, qemu_trace_enabled(args))
    if first_fault is None:
        first_fault = parse_platform_translation_error(args.out_dir)
    current_status = evaluate(logs)
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
    if post_login_probe_not_reached and timed_out:
        runtime_blocker = "qbox_post_login_probe_not_reached_timeout"
    elif post_login_probe_not_reached:
        runtime_blocker = "qbox_post_login_probe_not_reached"
    elif fwu_probe_incomplete and timed_out:
        runtime_blocker = "qbox_fwu_probe_incomplete_timeout"
    elif fwu_probe_incomplete:
        runtime_blocker = "qbox_fwu_probe_incomplete"
    elif secure_service_incomplete and timed_out:
        runtime_blocker = "qbox_secure_service_probe_incomplete_timeout"
    elif secure_service_incomplete:
        runtime_blocker = "qbox_secure_service_probe_incomplete"
    elif post_login_probe_incomplete and timed_out:
        runtime_blocker = "qbox_post_login_probe_incomplete_timeout"
    elif post_login_probe_incomplete:
        runtime_blocker = "qbox_post_login_probe_incomplete"
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
        host_si_cl0_sram=host_si_cl0_sram,
        host_si_cl1_sram=host_si_cl1_sram,
        boot_enc_trace=boot_enc_trace,
        post_login_probe=post_login_probe,
        progress_marker_first_hits=progress_marker_first_hits,
    )


if __name__ == "__main__":
    raise SystemExit(main())
