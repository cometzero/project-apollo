#!/usr/bin/env python3
"""Run or preflight the Apollo FVP full-system QBox path."""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import time
from typing import Any


CONSOLE_LOGS = {
    "platform": "qbox-platform.log",
    "rse": "qbox-rse.log",
    "si_cl0": "qbox-safety-island-cl0.log",
    "si_cl1": "qbox-safety-island-cl1.log",
    "secure_console": "qbox-secure-console.log",
    "primary_console": "qbox-primary-console.log",
}
RD_ASPEN_CHILD_RESULT = "rd-aspen-result.json"
RSE_LCS_CM = "0xcccc3c3c"
RSE_LCS_SE = 0xEEEEA5A5

GATES = ["G0", "G1", "G2", "G3", "G4", "G5"]
EXPECTED_AP_CPUS = 4
APOLLO_PRIMARY_LOGIN_PROMPT = "apollo-fvp login:"
APOLLO_PRIMARY_SHELL_MARKER = "~ #"
CHILD_FAIL_PATTERNS = [
    "Kernel panic",
    "Unable to mount root fs",
    "No working init found",
    "[ERR]",
    "[ERROR]",
]
CHILD_REQUIRED_MARKERS = {
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
}
CHILD_LOG_ALIASES = {
    "rse": "qbox-rse.log",
    "scp": "qbox-safety-island-cl0.log",
    "secure_console": "qbox-secure-console.log",
    "primary_console": "qbox-primary-console.log",
}
LEGACY_HIGH_DRAM_REG_BYTES = bytes.fromhex(
    "0000000080000000000000007f00000000000200000000000000000080000000"
)
MIGRATED_HIGH_DRAM_REG_BYTES = bytes.fromhex(
    "0000000080000000000000007f00000000000008800000000000000080000000"
)
LEGACY_HIGH_DRAM_DTS_FRAGMENT = """\
\t\t0x00000000  0x80000000  0x00000000  0x7F000000
\t\t0x00000200  0x00000000  0x00000000  0x80000000
"""
MIGRATED_HIGH_DRAM_DTS_FRAGMENT = """\
\t\t0x00000000  0x80000000  0x00000000  0x7F000000
\t\t0x00000008  0x80000000  0x00000000  0x80000000
"""
LEGACY_HIGH_DRAM_DTS_COMMENT = (
    "Bank 1: start = 0x0000_0200_0000_0000, size = 2 GiB (0x8000_0000)"
)
MIGRATED_HIGH_DRAM_DTS_COMMENT = (
    "Bank 1: start = 0x0000_0008_8000_0000, size = 2 GiB (0x8000_0000)"
)
AP_FLASH_SIZE = 0x48D000
AP_FLASH_FIP_A_OFFSET = 0x7000
AP_FLASH_FIP_B_OFFSET = 0x247000
AP_FLASH_FIP_B_SIZE = 0x240000
AP_FIP_IMAGE_GUID = "5d904717-0904-53cd-b240-df7c91ef4918"
FWU_METADATA_GUID = "8a7a84a0-8387-40f6-ab41-a8b9a5a60d23"
AP_CPU_COUNT_RE = re.compile(r"^ap cpus:\s*(?P<count>\d+)\s*$", re.MULTILINE)
LIVE_CL1_REQUIRED_MARKERS = {
    "cpu0_oor": "Out of Reset (OoR) completed on CPU: 0",
    "zephyr_boot": "Booting Zephyr OS",
    "pfdi_agent": "PFDI Agent setup complete",
    "pfdi_service": "PFDI service ready",
    "network_configured": "si_net_init: Network interface configured",
}
LIVE_CL1_POST_LOGIN_DRIVERS = [
    "arm_si_rproc",
    "rpmsg",
    "hipc_ethsi1",
]
LIVE_CL0_REQUIRED_MARKERS = {
    "scp_started": "[SI0_PLATFORM] SCP started",
    "module_init_complete": "[FWK] Module initialization complete!",
    "gic_multiview_configured": "GIC-multiview configured successfully",
}
MARKER_GROUP_PRIORITY = [
    "rse",
    "si_cl0",
    "si_cl1",
    "ap_firmware",
    "linux",
    "post_login",
    "maps_and_interrupts",
]


def has_unexpected_shadowed_range(platform_log: str) -> bool:
    for line in platform_log.splitlines():
        lowered = line.lower()
        if "shadowed" not in lowered:
            continue
        if "_atu_check_" in lowered:
            continue
        if "platform.ap_view_passthrough.target_socket" in lowered:
            continue
        return True
    return False


def platform_observations(out_dir: Path) -> dict[str, Any]:
    platform_log = read_log(out_dir / CONSOLE_LOGS["platform"])
    ap_cpu_match = AP_CPU_COUNT_RE.search(platform_log)
    ap_cpus = int(ap_cpu_match.group("count")) if ap_cpu_match else None
    return {
        "ap_cpus": ap_cpus,
        "expected_ap_cpus": EXPECTED_AP_CPUS,
        "ap_cpus_enabled_for_full_system": ap_cpus == EXPECTED_AP_CPUS,
        "unexpected_shadowed_range": has_unexpected_shadowed_range(platform_log),
    }


def secure_console_observations(out_dir: Path) -> dict[str, Any]:
    secure_log = read_log(out_dir / CONSOLE_LOGS["secure_console"])
    return {
        "ap_bl2_console": "NOTICE:  BL2:" in secure_log,
        "bl31_console": "NOTICE:  BL31:" in secure_log,
        "optee_console": "OP-TEE version:" in secure_log,
        "rse_comms_mhu_init_failed": (
            "[RSE-COMMS] Host to RSE MHU driver initialization failed" in secure_log
        ),
        "mhu_wrapper_assert": (
            "ASSERT: drivers/arm/mhu/mhu_wrapper_v3_x.c:" in secure_log
        ),
    }


def primary_console_observations(out_dir: Path) -> dict[str, Any]:
    primary_log = read_log(out_dir / CONSOLE_LOGS["primary_console"])
    return {
        "u_boot_console": "U-Boot " in primary_log,
        "linux_kernel_console": (
            "Booting Linux on physical CPU" in primary_log
            or "Linux version " in primary_log
        ),
        "login_prompt": "apollo-fvp login:" in primary_log,
        "root_shell": "~ #" in primary_log,
    }


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def artifact_record(path: Path) -> dict[str, Any]:
    exists = path.exists()
    return {
        "path": str(path.resolve()),
        "exists": exists,
        "size": path.stat().st_size if exists and path.is_file() else None,
    }


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def read_log(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def clean_console_text(text: str) -> str:
    return re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text).replace("\r", "")


def keep_running_child_logs(out_dir: Path) -> dict[str, str]:
    return {
        role: read_log(out_dir / filename)
        for role, filename in CHILD_LOG_ALIASES.items()
    }


def keep_running_probe_state(primary_console: str, *, requested: bool) -> dict[str, Any]:
    clean_primary = clean_console_text(primary_console)
    driver_patterns = {
        "arm_si_rproc": (
            "arm_si_rproc_modprobe_rc:0" in clean_primary
            or "remoteproc_state_after:si-cl1:attached" in clean_primary
            or "remoteproc_state:si-cl1:attached" in clean_primary
        ),
        "rpmsg": (
            "rpmsg_net_modprobe_rc:0" in clean_primary
            and "virtio_rpmsg_bus_modprobe_rc:0" in clean_primary
        ),
        "hipc_ethsi1": (
            "ethsi1_iplink_rc:0" in clean_primary
            or "rpmsg_device:virtio6.ethsi1" in clean_primary
        ),
    }
    return {
        "requested": requested,
        "secure_service_requested": False,
        "fwu_requested": False,
        "sent_login": APOLLO_PRIMARY_LOGIN_PROMPT in clean_primary,
        "sent_probe": "__QBOX_PROBE_START__" in clean_primary,
        "complete": "__QBOX_PROBE_DONE__" in clean_primary,
        "done_marker": "__QBOX_PROBE_DONE__" in clean_primary,
        "driver_patterns": driver_patterns,
        "return_codes": {
            match.group(1): int(match.group(2))
            for match in re.finditer(r"\b([A-Za-z0-9_]+_rc):(\d+)\b", clean_primary)
        },
    }


def synthesize_keep_running_child_status(
    args: argparse.Namespace,
    command: list[str],
    *,
    child_returncode: int | None,
) -> dict[str, Any]:
    logs = keep_running_child_logs(args.out_dir)
    combined = clean_console_text("\n".join(logs.values()))
    marker_groups = {
        group: {marker: marker in combined for marker in markers}
        for group, markers in CHILD_REQUIRED_MARKERS.items()
    }
    marker_groups["linux_boot"] = {
        APOLLO_PRIMARY_LOGIN_PROMPT: APOLLO_PRIMARY_LOGIN_PROMPT in combined,
        APOLLO_PRIMARY_SHELL_MARKER: APOLLO_PRIMARY_SHELL_MARKER in combined,
    }
    fail_hits = {pattern: pattern in combined for pattern in CHILD_FAIL_PATTERNS}
    probe = keep_running_probe_state(
        logs.get("primary_console", ""),
        requested=bool(args.post_login_probe),
    )
    linux_hit = any(marker_groups["linux_boot"].values())
    non_linux_hit = all(
        hit
        for group, markers in marker_groups.items()
        if group != "linux_boot"
        for hit in markers.values()
    )
    probe_ready = not args.post_login_probe or bool(probe.get("complete"))
    passed = bool(non_linux_hit and linux_hit and probe_ready and not any(fail_hits.values()))
    scp_strategy = "real-si-scp" if args.si_mode == "live-cl0-cl1" else "service-model"
    return {
        "passed": passed,
        "blocker": None,
        "marker_hits": marker_groups,
        "fail_patterns": fail_hits,
        "log_bytes": sum(
            len(text.encode("utf-8", errors="replace")) for text in logs.values()
        ),
        "post_login_probe": probe,
        "scp_service_model": {
            "strategy": scp_strategy,
            "live_scp_cpu_gdb": scp_strategy == "real-si-scp",
        },
        "runtime_artifacts": {},
        "rse_boot_timing_profile": {},
        "cc3xx_stats": None,
        "qbox_perf_profile": None,
        "remotepass_dmi_cache": {"enabled": bool(args.remotepass_dmi_cache)},
        "platform_returncode": child_returncode,
        "command": command,
    }


def write_keep_running_child_result(
    args: argparse.Namespace,
    command: list[str],
    *,
    child_returncode: int | None,
    blocker: str | None = None,
) -> dict[str, Any]:
    status = synthesize_keep_running_child_status(
        args,
        command,
        child_returncode=child_returncode,
    )
    if blocker:
        status["passed"] = False
        status["blocker"] = blocker
    (args.out_dir / "result.json").write_text(
        json.dumps(status, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return status


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def default_artifacts(local_build_dir: Path) -> dict[str, Path]:
    deploy = local_build_dir / "deploy"
    boot = deploy / "boot"
    firmware = deploy / "firmware"
    return {
        "rse_rom": firmware / "rse-rom-image.img",
        "rse_flash": firmware / "rse-flash-image.img",
        "rse_otp": firmware / "rse-otp-image.img",
        "ap_flash": firmware / "ap-flash-image.img",
        "fip": firmware / "fip.bin",
        "signed_ap_bl2": local_build_dir / "work/signing/deploy/signed_bl2.bin",
        "init_fwu_metadata": firmware / "init_fwu_metadata.bin",
        "ap_bl2_elf": (
            local_build_dir / "work/trusted-firmware-a/apollo_fvp/debug/bl2/bl2.elf"
        ),
        "rse_bl1_2_elf": local_build_dir / "work/trusted-firmware-m/bin/bl1_2.elf",
        "rse_bl2_elf": local_build_dir / "work/trusted-firmware-m/bin/bl2.elf",
        "rootfs": boot / "apollo-fvp-local-disk.img",
        "efi_capsule_disk": boot / "boot-fat.img",
        "provisioning_bundle": firmware / "combined_provisioning_message.bin",
        "ap_dtb": boot / "apollo-fvp.dtb",
        "rse_symbols": local_build_dir / "debug/symbols.json",
        "si_cl0_image": firmware / "si0_ramfw.bin",
        "si_cl1_image": firmware / "zephyr-demos-cl1.bin",
        "si_cl1_symbols": firmware / "zephyr-demos-cl1.elf",
    }


def resolved_artifacts(args: argparse.Namespace) -> dict[str, Path]:
    artifacts = default_artifacts(args.local_build_dir)
    overrides = {
        "rse_rom": args.rse_rom,
        "rse_flash": args.rse_flash,
        "rse_otp": args.rse_otp,
        "ap_flash": args.ap_flash,
        "ap_bl2_elf": args.ap_bl2_elf,
        "rse_bl1_2_elf": args.rse_bl1_2_elf,
        "rse_bl2_elf": args.rse_bl2_elf,
        "rootfs": args.rootfs,
        "efi_capsule_disk": args.efi_capsule_disk,
        "provisioning_bundle": args.provisioning_bundle,
        "ap_dtb": args.ap_dtb,
        "rse_symbols": args.rse_symbols,
        "si_cl0_image": args.si_cl0_image,
        "si_cl1_image": args.si_cl1_image,
        "si_cl1_symbols": args.si_cl1_symbols,
    }
    for name, value in overrides.items():
        if value is not None:
            artifacts[name] = value
    return {name: path.resolve() for name, path in artifacts.items()}


def sha256_files(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def first_existing_glob(pattern: str) -> Path | None:
    matches = sorted(Path().glob(pattern))
    return matches[0].resolve() if matches else None


def copytree_real_files(src: Path, dst: Path) -> None:
    shutil.copytree(
        src,
        dst,
        copy_function=shutil.copy2,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
    )


def break_source_hardlinks(src: Path, dst: Path) -> int:
    replaced = 0
    for dst_file in dst.rglob("*"):
        if not dst_file.is_file():
            continue
        relative = dst_file.relative_to(dst)
        src_file = src / relative
        if not src_file.exists():
            continue
        try:
            if not dst_file.samefile(src_file):
                continue
        except OSError:
            continue
        tmp_file = dst_file.with_name(f"{dst_file.name}.nohardlink")
        shutil.copy2(dst_file, tmp_file)
        tmp_file.replace(dst_file)
        replaced += 1
    return replaced


def migrate_tfa_hw_config_source(tfa_src: Path) -> Path:
    dts = tfa_src / "fdts/apollo_fvp_fvp.dts"
    text = dts.read_text(encoding="utf-8")
    if LEGACY_HIGH_DRAM_DTS_FRAGMENT not in text:
        if MIGRATED_HIGH_DRAM_DTS_FRAGMENT in text:
            return dts
        raise RuntimeError(f"legacy high-DRAM memory tuple not found in {dts}")
    text = text.replace(LEGACY_HIGH_DRAM_DTS_FRAGMENT, MIGRATED_HIGH_DRAM_DTS_FRAGMENT)
    text = text.replace(LEGACY_HIGH_DRAM_DTS_COMMENT, MIGRATED_HIGH_DRAM_DTS_COMMENT)
    tmp_dts = dts.with_name(f"{dts.name}.tmp")
    tmp_dts.write_text(text, encoding="utf-8")
    tmp_dts.replace(dts)
    return dts


def tfa_native_workdir(root: Path) -> Path | None:
    work_root = root / "build/tmp_baremetal/work/apollo_fvp-poky-linux/trusted-firmware-a"
    if not work_root.exists():
        return None
    matches = sorted(path for path in work_root.iterdir() if path.is_dir())
    return matches[0].resolve() if matches else None


def tfa_make_env(root: Path) -> dict[str, str]:
    env = os.environ.copy()
    path_entries = []
    sdk_cross = root / "build/local-sdk/sysroots/x86_64-pokysdk-linux/usr/bin/aarch64-poky-linux"
    sdk_native = root / "build/local-sdk/sysroots/x86_64-pokysdk-linux/usr/bin"
    for sdk_path in (sdk_cross, sdk_native):
        if sdk_path.exists():
            path_entries.append(str(sdk_path))
    workdir = tfa_native_workdir(root)
    if workdir is not None:
        native = workdir / "recipe-sysroot-native"
        native_bin = native / "usr/bin"
        if native_bin.exists():
            path_entries.append(str(native_bin))
        site_packages = sorted((native / "usr/lib").glob("python*/site-packages"))
        if site_packages:
            current = env.get("PYTHONPATH", "")
            prefix = str(site_packages[0])
            env["PYTHONPATH"] = f"{prefix}:{current}" if current else prefix
    if path_entries:
        env["PATH"] = ":".join(path_entries + [env.get("PATH", "")])
    return env


def build_migrated_tfa_fip(
    args: argparse.Namespace,
    artifacts: dict[str, Path],
    work_dir: Path,
) -> dict[str, Any]:
    root = workspace_root()
    tfa_src = root / "hsoc-stack/components/primary_compute/trusted-firmware-a"
    build_base = work_dir / "build"
    migrated_src = work_dir / "trusted-firmware-a-src"
    log_path = work_dir / "tfa-build.log"
    status: dict[str, Any] = {
        "source": str(tfa_src),
        "migrated_source": str(migrated_src),
        "build_base": str(build_base),
        "log": str(log_path),
        "command": [],
    }
    if not tfa_src.exists():
        status["blocker"] = f"missing_tfa_source:{tfa_src}"
        return status

    if not migrated_src.exists():
        copytree_real_files(tfa_src, migrated_src)
        status["source_copy_mode"] = "copy2_no_hardlinks"
    else:
        status["source_copy_mode"] = "existing_tree_checked_for_source_hardlinks"
    status["source_hardlinks_broken"] = break_source_hardlinks(tfa_src, migrated_src)
    try:
        migrated_dts = migrate_tfa_hw_config_source(migrated_src)
    except RuntimeError as exc:
        status["blocker"] = str(exc)
        return status
    status["migrated_hw_config_source"] = str(migrated_dts)

    build_base.mkdir(parents=True, exist_ok=True)
    env = tfa_make_env(root)
    cmd = [
        "make",
        "-C",
        str(migrated_src),
        "-j1",
        f"LD={os.environ.get('AARCH64_PREFIX', 'aarch64-poky-linux-')}ld",
        f"CC={os.environ.get('AARCH64_PREFIX', 'aarch64-poky-linux-')}gcc",
        f"BUILD_BASE={build_base}",
        "PLAT=apollo_fvp",
        "SPD=spmd",
        "SPMD_SPM_AT_SEL2=0",
        "DEBUG=1",
        "MBEDTLS_DIR=mbedtls",
        f"BL33={root / 'build/local-apollo-fvp/deploy/u-boot/u-boot.bin'}",
        f"BL32={root / 'build/local-apollo-fvp/deploy/optee/tee-pager_v2.bin'}",
        "HOSTCC=gcc",
        "host-poetry=",
        f"PLATFORM_CORE_COUNT={os.environ.get('PC_CPUS_COUNT', '4')}",
        "LINUX_DTS=0",
        "MEASURED_BOOT=1",
        "TRUSTED_BOARD_BOOT=1",
        "GENERATE_COT=1",
        "COT=tbbr",
        "FAULT_INJECTION_SUPPORT=1",
        "LOG_LEVEL=40",
        "ARM_ROTPK_LOCATION=devel_rsa",
        "ARM_ROTPK_LOCATION_ID=ARM_ROTPK_DEVEL_RSA_ID",
        "ROT_KEY=plat/arm/board/common/rotpk/arm_rotprivk_rsa.pem",
        f"PFDI_SUPPORT={os.environ.get('PFDI_SUPPORT', '1')}",
        f"SCMI_PFDI_MONITOR={os.environ.get('PFDI_MONITOR_SUPPORT', '1')}",
        "ARM_GPT_SUPPORT=1",
        "NR_OF_FW_BANKS=2",
        "NR_OF_IMAGES_IN_FW_BANK=5",
        "PSA_FWU_SUPPORT=1",
        f"RD_ASPEN_VARIANT={os.environ.get('RD_ASPEN_VARIANT', 'cfg2')}",
        f"APOLLO_FVP_VARIANT={os.environ.get('RD_ASPEN_VARIANT', 'cfg2')}",
        "bl2",
        "fip",
    ]
    status["command"] = cmd
    with log_path.open("w", encoding="utf-8") as log:
        proc = subprocess.run(
            cmd,
            cwd=root,
            env=env,
            text=True,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
    status["returncode"] = proc.returncode
    if proc.returncode:
        status["blocker"] = f"tfa_fip_rebuild_failed:{proc.returncode}:{log_path}"
        return status

    fip = build_base / "apollo_fvp/debug/fip.bin"
    hw_config = build_base / "apollo_fvp/debug/fdts/apollo_fvp_fvp.dtb"
    status["fip"] = str(fip)
    status["hw_config"] = str(hw_config)
    if not fip.exists():
        status["blocker"] = f"missing_rebuilt_fip:{fip}"
    elif not hw_config.exists():
        status["blocker"] = f"missing_rebuilt_hw_config:{hw_config}"
    else:
        hw_data = hw_config.read_bytes()
        status["hw_config_legacy_tuple_count"] = hw_data.count(LEGACY_HIGH_DRAM_REG_BYTES)
        status["hw_config_migrated_tuple_count"] = hw_data.count(MIGRATED_HIGH_DRAM_REG_BYTES)
        if status["hw_config_legacy_tuple_count"]:
            status["blocker"] = f"rebuilt_hw_config_still_legacy:{hw_config}"
        elif not status["hw_config_migrated_tuple_count"]:
            status["blocker"] = f"rebuilt_hw_config_missing_migrated_tuple:{hw_config}"
    return status


def run_fiptool_update(
    fiptool: Path,
    source_fip: Path,
    signed_bl2: Path,
    output_fip: Path,
) -> dict[str, Any]:
    shutil.copy2(source_fip, output_fip)
    cmd = [str(fiptool), "update", "--tb-fw", str(signed_bl2), str(output_fip)]
    proc = subprocess.run(
        cmd,
        cwd=workspace_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "output": proc.stdout,
        "output_fip": str(output_fip),
    }


def gpt_add(image: Path, index: int, name: str, offset: int, size: int, guid: str) -> None:
    start = offset // 512
    end = (offset + size) // 512 - 1
    subprocess.run(
        [
            "sgdisk",
            "--set-alignment=1",
            f"--new={index}:{start}:{end}",
            f"--typecode={index}:{guid}",
            f"--change-name={index}:{name}",
            str(image),
        ],
        stdout=subprocess.DEVNULL,
        check=True,
    )


def write_at(image: Path, offset: int, source: Path, max_size: int = 0) -> None:
    data = source.read_bytes()
    if max_size and len(data) > max_size:
        raise RuntimeError(f"{source} is {len(data)} bytes, exceeds slot size {max_size}")
    with image.open("r+b") as handle:
        handle.seek(offset)
        handle.write(data)


def create_ap_flash_image(
    fip_with_bl2: Path,
    init_fwu_metadata: Path,
    output: Path,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as handle:
        handle.truncate(AP_FLASH_SIZE)
    fip_a_size = ((fip_with_bl2.stat().st_size + 511) // 512) * 512
    gpt_add(output, 1, "reserved_1", 0x4400, 0x0C00, "8300")
    gpt_add(output, 2, "FWU-Metadata", 0x5000, 0x0200, FWU_METADATA_GUID)
    gpt_add(output, 3, "Bkup-FWU-Metadata", 0x6000, 0x0200, FWU_METADATA_GUID)
    gpt_add(output, 4, "FIP_A", AP_FLASH_FIP_A_OFFSET, fip_a_size, AP_FIP_IMAGE_GUID)
    gpt_add(output, 5, "FIP_B", AP_FLASH_FIP_B_OFFSET, AP_FLASH_FIP_B_SIZE, AP_FIP_IMAGE_GUID)
    gpt_add(output, 6, "reserved_2", 0x487000, 0x1000, "8300")
    write_at(output, 0x5000, init_fwu_metadata, 0x0200)
    write_at(output, 0x6000, init_fwu_metadata, 0x0200)
    write_at(output, AP_FLASH_FIP_A_OFFSET, fip_with_bl2, fip_a_size)
    write_at(output, AP_FLASH_FIP_B_OFFSET, fip_with_bl2, AP_FLASH_FIP_B_SIZE)


def extract_containing_fdt(data: bytes, offset: int) -> tuple[int, int] | None:
    magic = b"\xd0\x0d\xfe\xed"
    start = offset
    while start >= 0:
        start = data.rfind(magic, 0, start + 1)
        if start < 0:
            return None
        if start + 8 > len(data):
            return None
        total_size = struct.unpack(">I", data[start + 4 : start + 8])[0]
        end = start + total_size
        if offset >= start and offset + len(LEGACY_HIGH_DRAM_REG_BYTES) <= end <= len(data):
            return start, end
        start -= 1
    return None


def dtc_decompile(dtb: Path, dts: Path) -> dict[str, Any]:
    cmd = ["dtc", "-I", "dtb", "-O", "dts", "-o", str(dts), str(dtb)]
    proc = subprocess.run(
        cmd,
        cwd=workspace_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "output": proc.stdout,
    }


def validate_dtb_pair(
    original_dtb: Path,
    patched_dtb: Path,
    original_dts: Path,
    patched_dts: Path,
) -> dict[str, Any]:
    original = dtc_decompile(original_dtb, original_dts)
    patched = dtc_decompile(patched_dtb, patched_dts)
    return {
        "returncode": original["returncode"] or patched["returncode"],
        "original": original,
        "patched": patched,
    }


def prepare_signed_high_dram_ap_flash(
    args: argparse.Namespace, artifacts: dict[str, Path]
) -> dict[str, Any]:
    src_ap_flash = artifacts["ap_flash"]
    status: dict[str, Any] = {
        "input": str(src_ap_flash),
        "output": str(src_ap_flash),
        "changed": False,
        "state": "missing_input" if not src_ap_flash.exists() else "not_needed",
        "legacy_high_dram_base": "0x20000000000",
        "migrated_high_dram_base": "0x880000000",
        "authentication": "not_evaluated",
    }
    if not src_ap_flash.exists():
        return status

    ap_flash_data = src_ap_flash.read_bytes()
    legacy_count = ap_flash_data.count(LEGACY_HIGH_DRAM_REG_BYTES)
    migrated_count = ap_flash_data.count(MIGRATED_HIGH_DRAM_REG_BYTES)
    status["input_legacy_tuple_count"] = legacy_count
    status["input_migrated_tuple_count"] = migrated_count
    if legacy_count == 0:
        status["state"] = "already_migrated" if migrated_count else "no_matching_fdt_memory_tuple"
        status["authentication"] = "preserved_existing_ap_flash"
        return status

    work_dir = args.out_dir / "signed-high-dram-handoff"
    output_flash = work_dir / "ap-flash-image-high-dram-migrated.img"
    output_fip_with_bl2 = work_dir / "fip_with_bl2-high-dram-migrated.bin"
    manifest_path = work_dir / "manifest.sha256"
    required = [
        root_path
        for root_path in [
            artifacts["signed_ap_bl2"],
            artifacts["init_fwu_metadata"],
            workspace_root() / "hsoc-stack/components/primary_compute/trusted-firmware-a/fdts/apollo_fvp_fvp.dts",
            workspace_root() / "build/local-apollo-fvp/deploy/u-boot/u-boot.bin",
            workspace_root() / "build/local-apollo-fvp/deploy/optee/tee-pager_v2.bin",
        ]
        if not root_path.exists()
    ]
    if required:
        status["state"] = "missing_rebuild_inputs"
        status["blocker"] = "missing_rebuild_input:" + ",".join(str(path) for path in required)
        return status

    fiptool = (
        workspace_root()
        / "build/local-apollo-fvp/work/trusted-firmware-a/apollo_fvp/debug/tools/fiptool/fiptool"
    )
    if not fiptool.exists():
        status["state"] = "missing_rebuild_tool"
        status["blocker"] = f"missing_fiptool:{fiptool}"
        return status

    work_dir.mkdir(parents=True, exist_ok=True)
    manifest_inputs = [
        artifacts["signed_ap_bl2"],
        artifacts["init_fwu_metadata"],
        workspace_root() / "hsoc-stack/components/primary_compute/trusted-firmware-a/fdts/apollo_fvp_fvp.dts",
        workspace_root() / "build/local-apollo-fvp/deploy/u-boot/u-boot.bin",
        workspace_root() / "build/local-apollo-fvp/deploy/optee/tee-pager_v2.bin",
    ]
    manifest = sha256_files(manifest_inputs)
    status["manifest"] = manifest
    if (
        output_flash.exists()
        and output_fip_with_bl2.exists()
        and manifest_path.exists()
        and manifest_path.read_text(encoding="utf-8").strip() == manifest
    ):
        output_data = output_flash.read_bytes()
        if output_data.count(LEGACY_HIGH_DRAM_REG_BYTES) == 0 and output_data.count(
            MIGRATED_HIGH_DRAM_REG_BYTES
        ):
            artifacts["ap_flash"] = output_flash.resolve()
            status.update(
                {
                    "output": str(output_flash.resolve()),
                    "changed": True,
                    "state": "reused_signed_migrated_ap_flash",
                    "output_legacy_tuple_count": 0,
                    "output_migrated_tuple_count": output_data.count(MIGRATED_HIGH_DRAM_REG_BYTES),
                    "authentication": "reused_fip_rebuilt_with_tf_a_cot_development_rot_key",
                }
            )
            return status

    tfa_status = build_migrated_tfa_fip(args, artifacts, work_dir)
    status["tfa_rebuild"] = tfa_status
    if tfa_status.get("blocker"):
        status["state"] = "tfa_rebuild_blocked"
        status["blocker"] = str(tfa_status["blocker"])
        return status

    fip_status = run_fiptool_update(
        fiptool,
        Path(str(tfa_status["fip"])),
        artifacts["signed_ap_bl2"],
        output_fip_with_bl2,
    )
    status["fip_update"] = fip_status
    if fip_status["returncode"]:
        status["state"] = "fip_update_failed"
        status["blocker"] = f"fiptool_update_failed:{fip_status['returncode']}"
        return status

    try:
        create_ap_flash_image(output_fip_with_bl2, artifacts["init_fwu_metadata"], output_flash)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        status["state"] = "ap_flash_repack_failed"
        status["blocker"] = f"ap_flash_repack_failed:{exc}"
        return status

    output_data = output_flash.read_bytes()
    status.update(
        {
            "output": str(output_flash.resolve()),
            "changed": True,
            "state": "rebuilt_signed_migrated_ap_flash",
            "output_legacy_tuple_count": output_data.count(LEGACY_HIGH_DRAM_REG_BYTES),
            "output_migrated_tuple_count": output_data.count(MIGRATED_HIGH_DRAM_REG_BYTES),
            "authentication": (
                "TF-A fip target regenerated TBBR certificates with "
                "TRUSTED_BOARD_BOOT=1 GENERATE_COT=1 and the project development ROT key; "
                "the AP flash was repacked from that rebuilt FIP plus the existing signed BL2."
            ),
        }
    )
    if status["output_legacy_tuple_count"]:
        status["blocker"] = f"rebuilt_ap_flash_still_contains_legacy_tuple:{output_flash}"
        return status
    if not status["output_migrated_tuple_count"]:
        status["blocker"] = f"rebuilt_ap_flash_missing_migrated_tuple:{output_flash}"
        return status
    manifest_path.write_text(manifest + "\n", encoding="utf-8")
    artifacts["ap_flash"] = output_flash.resolve()
    return status


def patch_high_dram_tuple_in_image(
    args: argparse.Namespace,
    artifacts: dict[str, Path],
    artifact_key: str,
    output_name: str,
) -> dict[str, Any]:
    src = artifacts[artifact_key]
    status: dict[str, Any] = {
        "artifact": artifact_key,
        "input": str(src),
        "output": str(src),
        "changed": False,
        "state": "missing_input" if not src.exists() else "unchanged",
        "dtb_path": "/apollo-fvp.dtb",
        "legacy_high_dram_base": "0x20000000000",
        "migrated_high_dram_base": "0x880000000",
        "patched_offsets": [],
        "validation": "not_evaluated",
    }
    if not src.exists():
        return status

    data = src.read_bytes()
    old_count = data.count(LEGACY_HIGH_DRAM_REG_BYTES)
    new_count = data.count(MIGRATED_HIGH_DRAM_REG_BYTES)
    status["legacy_tuple_count"] = old_count
    status["migrated_tuple_count"] = new_count
    if old_count == 0:
        status["state"] = "already_migrated" if new_count else "no_matching_fdt_memory_tuple"
        status["validation"] = "unchanged_no_legacy_tuple"
        return status
    if old_count != 1:
        status["state"] = "ambiguous_fdt_memory_tuple_count"
        status["blocker"] = f"expected_one_legacy_tuple_found:{old_count}:{src}"
        return status

    args.out_dir.mkdir(parents=True, exist_ok=True)
    dst = args.out_dir / output_name
    offset = data.find(LEGACY_HIGH_DRAM_REG_BYTES)
    fdt = extract_containing_fdt(data, offset)
    if fdt is None:
        status["state"] = "legacy_tuple_not_in_valid_fdt"
        status["blocker"] = f"legacy_tuple_not_in_valid_fdt:{src}:{hex(offset)}"
        return status
    fdt_start, fdt_end = fdt
    fdt_data = data[fdt_start:fdt_end]
    if fdt_data.count(LEGACY_HIGH_DRAM_REG_BYTES) != 1:
        status["state"] = "ambiguous_fdt_local_tuple_count"
        status["blocker"] = f"expected_one_legacy_tuple_in_fdt:{src}:{hex(fdt_start)}"
        return status

    patched = (
        data[:offset]
        + MIGRATED_HIGH_DRAM_REG_BYTES
        + data[offset + len(LEGACY_HIGH_DRAM_REG_BYTES) :]
    )
    patched_fdt = patched[fdt_start:fdt_end]
    if patched_fdt.count(LEGACY_HIGH_DRAM_REG_BYTES) != 0:
        status["state"] = "patch_validation_failed"
        status["blocker"] = f"patched_fdt_still_contains_legacy_tuple:{src}:{hex(fdt_start)}"
        return status
    if patched_fdt.count(MIGRATED_HIGH_DRAM_REG_BYTES) != 1:
        status["state"] = "patch_validation_failed"
        status["blocker"] = f"patched_fdt_missing_single_migrated_tuple:{src}:{hex(fdt_start)}"
        return status

    original_fdt = args.out_dir / f"{artifact_key}-high-dram-original.dtb"
    patched_fdt_path = args.out_dir / f"{artifact_key}-high-dram-patched.dtb"
    original_dts = args.out_dir / f"{artifact_key}-high-dram-original.dts"
    patched_dts = args.out_dir / f"{artifact_key}-high-dram-patched.dts"
    original_fdt.write_bytes(fdt_data)
    patched_fdt_path.write_bytes(patched_fdt)
    dtc_status = validate_dtb_pair(original_fdt, patched_fdt_path, original_dts, patched_dts)
    status["dtc_validation"] = dtc_status
    if dtc_status["returncode"] != 0:
        status["state"] = "dtc_validation_failed"
        status["blocker"] = f"dtc_validation_failed:{patched_fdt_path}"
        return status

    dst.write_bytes(patched)
    shutil.copystat(src, dst, follow_symlinks=True)
    artifacts[artifact_key] = dst.resolve()
    status.update(
        {
            "output": str(dst.resolve()),
            "changed": True,
            "state": "patched_boot_disk_fdt_memory_reg",
            "patched_offsets": [hex(offset)],
            "fdt_offset": hex(fdt_start),
            "fdt_size": fdt_end - fdt_start,
            "original_fdt": str(original_fdt.resolve()),
            "patched_fdt": str(patched_fdt_path.resolve()),
            "original_dts": str(original_dts.resolve()),
            "patched_dts": str(patched_dts.resolve()),
            "patched_tuple_count": old_count,
            "legacy_tuple_count_after": patched.count(LEGACY_HIGH_DRAM_REG_BYTES),
            "migrated_tuple_count_after": patched.count(MIGRATED_HIGH_DRAM_REG_BYTES),
            "validation": "single_tuple_in_extracted_fdt",
        }
    )
    return status


def prepare_migrated_boot_artifacts(
    args: argparse.Namespace, artifacts: dict[str, Path]
) -> dict[str, Any]:
    checks = [
        patch_high_dram_tuple_in_image(
            args,
            artifacts,
            "rootfs",
            "apollo-fvp-local-disk-high-dram-migrated.img",
        ),
        patch_high_dram_tuple_in_image(
            args,
            artifacts,
            "efi_capsule_disk",
            "boot-fat-high-dram-migrated.img",
        ),
    ]
    return {
        "changed": any(bool(check["changed"]) for check in checks),
        "state": "patched_boot_artifacts" if any(bool(check["changed"]) for check in checks) else "unchanged",
        "critical_artifact": "rootfs:/apollo-fvp.dtb",
        "checks": checks,
    }


def missing_required(args: argparse.Namespace, artifacts: dict[str, Path]) -> list[str]:
    required = [
        "rse_rom",
        "rse_flash",
        "rse_otp",
        "ap_flash",
        "ap_bl2_elf",
        "rse_bl1_2_elf",
        "rse_bl2_elf",
        "rootfs",
        "efi_capsule_disk",
        "provisioning_bundle",
        "ap_dtb",
        "rse_symbols",
        "si_cl0_image",
        "si_cl1_image",
        "si_cl1_symbols",
    ]
    missing = [
        f"missing_artifact:{name}:{artifacts[name]}"
        for name in required
        if not artifacts[name].exists()
    ]
    if not args.conf.exists():
        missing.append(f"missing_artifact:conf:{args.conf}")
    return missing


def parse_int_auto(value: str) -> int | None:
    try:
        return int(value, 0)
    except ValueError:
        return None


def is_blank_file(path: Path) -> bool:
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                return True
            if any(chunk):
                return False


def forwarded_arg_present(args: argparse.Namespace, name: str) -> bool:
    return any(item == name or item.startswith(name + "=") for item in args.forward_args)


def platform_param_value(args: argparse.Namespace, key: str) -> str | None:
    prefix = key + "="
    for param in args.platform_param:
        if param.startswith(prefix):
            return param.split("=", 1)[1].strip()
    return None


def rse_lcm_uses_se_fast_path(args: argparse.Namespace) -> bool:
    lcs = platform_param_value(args, "platform.rse_lcm_regs.lcs")
    if lcs is None:
        lcs = os.environ.get("QBOX_RDASPEN_RSE_LCM_LCS", "").strip()
    if not lcs:
        return True
    value = parse_int_auto(lcs)
    return value is None or value == RSE_LCS_SE


def ensure_default_debug_manifest(
    args: argparse.Namespace,
    artifacts: dict[str, Path],
) -> str | None:
    if args.rse_symbols is not None:
        return None
    symbol_path = artifacts["rse_symbols"]
    if symbol_path.exists():
        return None
    default_symbol_path = default_artifacts(args.local_build_dir)["rse_symbols"].resolve()
    if symbol_path != default_symbol_path:
        return None

    setup_script = workspace_root() / "scripts/setup_local_debug_env.py"
    if not setup_script.exists():
        return f"missing_artifact:rse_symbols:{symbol_path}"

    args.out_dir.mkdir(parents=True, exist_ok=True)
    log_path = args.out_dir / "debug-manifest-generate.log"
    cmd = [
        sys.executable,
        str(setup_script),
        "--local-build-dir",
        str(args.local_build_dir),
        "--out-dir",
        str(symbol_path.parent),
    ]
    proc = subprocess.run(
        cmd,
        cwd=workspace_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_path.write_text(
        "+ " + " ".join(cmd) + "\n" + proc.stdout,
        encoding="utf-8",
    )
    if proc.returncode:
        return f"debug_manifest_generation_failed:{proc.returncode}:{log_path}"
    if not symbol_path.exists():
        return f"missing_artifact:rse_symbols:{symbol_path}"
    return None


def should_auto_provision_rse_otp(
    args: argparse.Namespace,
    artifacts: dict[str, Path],
) -> tuple[bool, str]:
    if not args.auto_provision_rse_otp:
        return False, "disabled"
    if args.check_only or args.build_only or args.isolated:
        return False, "non_runtime_mode"
    if args.rse_otp is not None:
        return False, "explicit_rse_otp"
    if args.no_copy_writable_flash:
        return False, "no_copy_writable_flash"
    if forwarded_arg_present(args, "--allow-blank-rse-otp"):
        return False, "explicit_blank_otp_experiment"
    if not rse_lcm_uses_se_fast_path(args):
        return False, "non_se_lifecycle"
    otp = artifacts["rse_otp"]
    if not otp.exists():
        return False, "missing_rse_otp"
    if not is_blank_file(otp):
        return False, "already_provisioned"
    return True, "blank_default_rse_otp"


def clone_args(args: argparse.Namespace) -> argparse.Namespace:
    values = vars(args).copy()
    values["platform_param"] = list(args.platform_param)
    values["forward_args"] = list(args.forward_args)
    return argparse.Namespace(**values)


def make_rse_otp_provision_args(args: argparse.Namespace) -> argparse.Namespace:
    provision_args = clone_args(args)
    provision_args.out_dir = args.out_dir / "rse-otp-provisioning-pass"
    provision_args.si_mode = "service-model"
    provision_args.post_login_probe = False
    provision_args.keep_running_after_pass = False
    provision_args.live_trace = False
    provision_args.timeout = args.rse_otp_provision_timeout
    provision_args.provision_blank_rse_otp = True
    if platform_param_value(provision_args, "platform.rse_lcm_regs.lcs") is None:
        provision_args.platform_param.append(f"platform.rse_lcm_regs.lcs={RSE_LCS_CM}")
    return provision_args


def persist_provisioned_rse_otp(
    artifacts: dict[str, Path],
    child_status: dict[str, Any] | None,
) -> tuple[bool, str | None]:
    runtime_path = (child_status or {}).get("runtime_artifacts", {}).get("rse_otp")
    if not runtime_path:
        return False, "missing_runtime_rse_otp"
    runtime_otp = Path(str(runtime_path))
    if not runtime_otp.exists():
        return False, f"missing_runtime_rse_otp:{runtime_otp}"
    if is_blank_file(runtime_otp):
        return False, f"blank_runtime_rse_otp:{runtime_otp}"

    deploy_otp = artifacts["rse_otp"]
    deploy_otp.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(runtime_otp, deploy_otp)
    return True, str(runtime_otp.resolve())


def auto_provision_rse_otp(
    args: argparse.Namespace,
    artifacts: dict[str, Path],
) -> str | None:
    requested, reason = should_auto_provision_rse_otp(args, artifacts)
    status: dict[str, Any] = {
        "enabled": args.auto_provision_rse_otp,
        "requested": requested,
        "reason": reason,
    }
    args.rse_otp_auto_provision = status
    if not requested:
        return None

    provision_args = make_rse_otp_provision_args(args)
    status.update(
        {
            "out_dir": str(provision_args.out_dir.resolve()),
            "lcs": RSE_LCS_CM,
            "si_mode": provision_args.si_mode,
            "timeout": provision_args.timeout,
        }
    )
    child_rc, command = run_child(provision_args, artifacts)
    child_result = provision_args.out_dir / "result.json"
    child_status = read_json(child_result)
    status.update(
        {
            "child_returncode": child_rc,
            "child_result": str(child_result.resolve()),
            "child_passed": bool(child_status.get("passed")) if child_status else False,
            "child_blocker": child_status.get("blocker") if child_status else None,
            "command": command,
        }
    )

    persisted, detail = persist_provisioned_rse_otp(artifacts, child_status)
    status["persisted"] = persisted
    if persisted:
        status["runtime_rse_otp"] = detail
        status["deploy_rse_otp"] = str(artifacts["rse_otp"].resolve())
        return None

    status["error"] = detail
    return "rse_otp_auto_provision_failed:" + str(detail)


def gate_status(
    *,
    args: argparse.Namespace,
    child_status: dict[str, Any] | None,
    blocker: str | None,
    check_only: bool,
) -> dict[str, str]:
    gates = {gate: "not_run" for gate in GATES}
    if blocker:
        if blocker.startswith("missing_artifact"):
            gates["G0"] = "fail"
            return gates
        gates["G0"] = "pass"
        if args.si_mode == "service-model":
            gates["G2"] = "blocked"
        elif args.si_mode == "live-cl1":
            gates["G3"] = "blocked"
        elif args.si_mode == "live-cl0-cl1":
            gates["G4"] = "blocked"
        return gates

    gates["G0"] = "pass"
    if check_only or args.build_only:
        return gates

    child_passed = bool(child_status and child_status.get("passed"))
    child_blocker = None
    if child_status:
        child_blocker = child_status.get("blocker")

    if args.si_mode == "service-model":
        gates["G2"] = "pass" if child_passed else ("blocked" if child_blocker else "fail")
    elif args.si_mode == "live-cl1":
        gates["G3"] = "pass" if child_passed else ("blocked" if child_blocker else "fail")
    elif args.si_mode == "live-cl0-cl1":
        gates["G4"] = "pass" if child_passed else ("blocked" if child_blocker else "fail")
    return gates


def all_hits(markers: Any) -> bool:
    return isinstance(markers, dict) and bool(markers) and all(
        bool(value) for value in markers.values()
    )


def child_marker_hits(child_status: dict[str, Any] | None) -> dict[str, dict[str, bool]]:
    marker_hits = (child_status or {}).get("marker_hits", {})
    if not isinstance(marker_hits, dict):
        return {}
    normalized: dict[str, dict[str, bool]] = {}
    for group, hits in marker_hits.items():
        if isinstance(group, str) and isinstance(hits, dict):
            normalized[group] = {str(name): bool(value) for name, value in hits.items()}
    return normalized


def post_login_probe(child_status: dict[str, Any] | None) -> dict[str, Any]:
    probe = (child_status or {}).get("post_login_probe")
    return probe if isinstance(probe, dict) else {}


def child_rse_boot_timing_profile(
    child_status: dict[str, Any] | None,
) -> dict[str, Any]:
    profile = (child_status or {}).get("rse_boot_timing_profile")
    if isinstance(profile, dict):
        return profile

    first_hits = (child_status or {}).get("progress_marker_first_hits")
    if not isinstance(first_hits, dict):
        return {}
    markers = []
    for name, hit in sorted(
        first_hits.items(),
        key=lambda item: float(item[1].get("elapsed_s", 0.0))
        if isinstance(item[1], dict)
        else 0.0,
    ):
        if not isinstance(hit, dict):
            continue
        markers.append(
            {
                "name": str(name),
                "marker": hit.get("marker"),
                "seen": True,
                "elapsed_s": hit.get("elapsed_s"),
            }
        )
    return {"markers": markers, "deltas": [], "slowest_delta": None, "summary": {}}


def marker_from_child(
    markers: dict[str, dict[str, bool]],
    group: str,
    marker: str,
) -> bool:
    return bool(markers.get(group, {}).get(marker))


def build_marker_groups(
    args: argparse.Namespace,
    child_status: dict[str, Any] | None,
) -> dict[str, dict[str, bool]]:
    groups = child_marker_hits(child_status)
    measured_boot = groups.get("measured_boot", {})
    linux_boot = groups.get("linux_boot", {})
    rse_scp = groups.get("rse_scp_handoff", {})
    probe = post_login_probe(child_status)
    driver_patterns = probe.get("driver_patterns", {})
    if not isinstance(driver_patterns, dict):
        driver_patterns = {}
    platform_obs = platform_observations(args.out_dir)
    secure_obs = secure_console_observations(args.out_dir)
    primary_obs = primary_console_observations(args.out_dir)
    cl1_log = read_log(args.out_dir / CONSOLE_LOGS["si_cl1"])

    groups["rse"] = {
        "tfm_bl1_1": marker_from_child(groups, "rse_boot", "Starting TF-M BL1_1"),
        "first_image_slot": marker_from_child(
            groups, "rse_boot", "Jumping to the first image slot"
        ),
        "scmi_handoff": all_hits(rse_scp),
    }
    groups["ap_firmware"] = {
        "ap_cpus_enabled": bool(platform_obs["ap_cpus_enabled_for_full_system"]),
        "ap_bl2": bool(measured_boot.get("AP_BL2") and secure_obs["ap_bl2_console"]),
        "bl31": bool(measured_boot.get("SECURE_RT_EL3") and secure_obs["bl31_console"]),
        "optee": bool(
            measured_boot.get("SECURE_RT_EL1_SPMD") and secure_obs["optee_console"]
        ),
        "u_boot": bool(measured_boot.get("BL_33") and primary_obs["u_boot_console"]),
    }
    groups["linux"] = {
        "login_prompt": bool(linux_boot.get("apollo-fvp login:")),
        "root_shell": bool(linux_boot.get("~ #")),
    }
    groups["maps_and_interrupts"] = {
        "no_unexpected_shadowed_ranges": not bool(platform_obs["unexpected_shadowed_range"]),
        "rse_scp_handoff": all_hits(rse_scp),
    }

    if args.si_mode == "service-model":
        groups["si_cl0"] = {
            "service_model_recorded": True,
            "si_cl0_image_manifest": bool(measured_boot.get("SI_CL0")),
        }
        groups["si_cl1"] = {
            "service_model_recorded": True,
        }
    elif args.si_mode == "live-cl1":
        groups["si_cl0"] = {
            "service_model_recorded": True,
            "si_cl0_image_manifest": bool(measured_boot.get("SI_CL0")),
        }
        groups["si_cl1"] = {
            name: marker in cl1_log
            for name, marker in LIVE_CL1_REQUIRED_MARKERS.items()
        }
    else:
        cl0_log = read_log(args.out_dir / CONSOLE_LOGS["si_cl0"])
        child_scp = (child_status or {}).get("scp_service_model", {})
        live_scp_cpu = (
            isinstance(child_scp, dict)
            and bool(child_scp.get("live_scp_cpu_gdb"))
            and child_scp.get("strategy") == "real-si-scp"
        )
        groups["si_cl0"] = {
            "scp_log_present": bool(cl0_log.strip()),
            **{
                name: marker in cl0_log
                for name, marker in LIVE_CL0_REQUIRED_MARKERS.items()
            },
            "live_scp_strategy_recorded": live_scp_cpu,
            "service_model_not_used": live_scp_cpu,
        }
        groups["si_cl1"] = {
            name: marker in cl1_log
            for name, marker in LIVE_CL1_REQUIRED_MARKERS.items()
        }

    if probe:
        groups["post_login"] = {
            "probe_complete": bool(probe.get("complete")),
            **{
                name: bool(driver_patterns.get(name))
                for name in LIVE_CL1_POST_LOGIN_DRIVERS
            },
        }

    return groups


def missing_markers(markers: dict[str, bool]) -> list[str]:
    return [name for name, value in markers.items() if not value]


def live_cl1_gate_blocker(
    args: argparse.Namespace,
    marker_groups: dict[str, dict[str, bool]],
    child_status: dict[str, Any] | None,
) -> str | None:
    if args.si_mode not in {"live-cl1", "live-cl0-cl1"}:
        return None
    prefix = "live_cl1" if args.si_mode == "live-cl1" else "live_cl0_cl1"
    if child_status and not child_status.get("passed"):
        child_blocker = child_status.get("blocker")
        return str(child_blocker) if child_blocker else None
    map_missing = missing_markers(marker_groups.get("maps_and_interrupts", {}))
    if map_missing:
        return f"{prefix}_map_blocked:" + ",".join(map_missing)
    if args.si_mode == "live-cl0-cl1":
        cl0_missing = missing_markers(marker_groups.get("si_cl0", {}))
        if cl0_missing:
            return f"{prefix}_marker_blocked:" + ",".join(cl0_missing)
    cl1_missing = missing_markers(marker_groups.get("si_cl1", {}))
    if cl1_missing:
        return f"{prefix}_marker_blocked:" + ",".join(cl1_missing)
    post_login = marker_groups.get("post_login", {})
    post_login_missing = missing_markers(
        {
            name: post_login.get(name, False)
            for name in ["probe_complete", *LIVE_CL1_POST_LOGIN_DRIVERS]
        }
    )
    if post_login_missing:
        return f"{prefix}_hipc_rpmsg_blocked:" + ",".join(post_login_missing)
    return None


def write_result(
    args: argparse.Namespace,
    artifacts: dict[str, Path],
    *,
    command: list[str],
    child_status: dict[str, Any] | None,
    child_returncode: int | None,
    blocker: str | None,
    check_only: bool,
) -> int:
    args.out_dir.mkdir(parents=True, exist_ok=True)
    input_artifacts = {
        name: artifact_record(path) for name, path in sorted(artifacts.items())
    }
    marker_groups = build_marker_groups(args, child_status)
    platform_obs = platform_observations(args.out_dir)
    secure_obs = secure_console_observations(args.out_dir)
    primary_obs = primary_console_observations(args.out_dir)
    gate_blocker = None
    if not check_only and not args.build_only:
        gate_blocker = live_cl1_gate_blocker(args, marker_groups, child_status)
    if not blocker and gate_blocker:
        blocker = gate_blocker
    gates = gate_status(
        args=args,
        child_status=child_status,
        blocker=blocker,
        check_only=check_only,
    )
    passed = bool(
        not blocker and (check_only or args.build_only or (child_status or {}).get("passed"))
    )
    if (check_only or args.build_only) and not blocker:
        passed = True
    if blocker:
        passed = False

    console_logs = {
        name: str((args.out_dir / filename).resolve())
        for name, filename in CONSOLE_LOGS.items()
    }
    service_model_debt = []
    if args.si_mode == "service-model":
        service_model_debt = [
            "Safety Island CL0 SCP-firmware is represented by the RD-Aspen "
            "RSE/SCP service model for this gate.",
            "Safety Island CL1 Zephyr behavior is represented by the "
            "service-model AP-SI RPMsg/HIPC path for this gate.",
        ]
    mhu_trace_logs = {}
    if args.si_mode in {"live-cl1", "live-cl0-cl1"}:
        mhu_trace_logs = {
            "ap_si": str((args.out_dir / "ap-si-mhuv3-trace.log").resolve()),
            "si_cl1": str((args.out_dir / "si-cl1-mhuv3-trace.log").resolve()),
        }
    qbox_performance_options = {
        "remotepass_dmi_cache": bool(args.remotepass_dmi_cache),
        "rse_hotpath_accel": bool(args.rse_hotpath_accel),
        "rse_bl2_libc_hotpath": bool(args.rse_bl2_libc_hotpath),
        "rse_lms_accel": bool(args.rse_lms_accel),
        "rse_bl2_load_accel": bool(args.rse_bl2_load_accel),
        "rse_bl2_boot_enc_accel": bool(args.rse_bl2_boot_enc_accel),
        "rse_bl2_img_hash_accel": bool(args.rse_bl2_img_hash_accel),
        "rse_bl2_verify_sig_accel": bool(args.rse_bl2_verify_sig_accel),
        "rse_bl2_delay_accel": bool(args.rse_bl2_delay_accel),
        "cc3xx_qemu_native_backend": bool(args.cc3xx_qemu_native_backend),
        "rse_fast_boot_aliases": bool(args.rse_fast_boot_aliases),
    }
    status: dict[str, Any] = {
        "passed": passed,
        "verdict": "pass" if passed else ("blocked" if blocker else "fail"),
        "boot_mode": "apollo-full-system",
        "safety_island_mode": args.si_mode,
        "smmu_backend": args.smmu_backend,
        "mhu_backend": "systemc-mhu320ae",
        "qbox_performance_preset": args.qbox_performance_preset,
        "qbox_performance_options": qbox_performance_options,
        "ap_high_dram_handoff_patch": getattr(
            args,
            "ap_high_dram_handoff_patch",
            {"changed": False, "state": "not_evaluated"},
        ),
        "ap_high_dram_signed_handoff": getattr(
            args,
            "ap_high_dram_signed_handoff",
            {"changed": False, "state": "not_evaluated"},
        ),
        "rse_otp_auto_provision": getattr(
            args,
            "rse_otp_auto_provision",
            {"enabled": False, "requested": False},
        ),
        "range_limited_flash_dmi": args.range_limited_flash_dmi,
        "live_trace": args.live_trace,
        "completion_gates": gates,
        "input_artifacts": input_artifacts,
        "runtime_artifacts": (child_status or {}).get("runtime_artifacts", {}),
        "console_logs": console_logs,
        "mhu_trace_logs": mhu_trace_logs,
        "platform_stdout_log": console_logs["platform"],
        "platform_observations": platform_obs,
        "secure_console_observations": secure_obs,
        "primary_console_observations": primary_obs,
        "marker_groups": marker_groups,
        "first_failing_marker": (
            None if check_only or args.build_only else first_failing_marker(marker_groups)
        ),
        "post_login_probe": (child_status or {}).get("post_login_probe"),
        "rse_boot_timing_profile": child_rse_boot_timing_profile(child_status),
        "cc3xx_stats": (child_status or {}).get("cc3xx_stats"),
        "qbox_perf_profile": (child_status or {}).get("qbox_perf_profile"),
        "remotepass_dmi_cache": (child_status or {}).get("remotepass_dmi_cache"),
        "completion_gate_blocker": gate_blocker,
        "child_scp_service_model": (child_status or {}).get("scp_service_model"),
        "service_model_debt": service_model_debt,
        "blocker": blocker or (child_status or {}).get("blocker"),
        "child_result": str((args.out_dir / RD_ASPEN_CHILD_RESULT).resolve())
        if child_status
        else None,
        "child_returncode": child_returncode,
        "command": command,
        "runner_argv": sys.argv,
    }

    result_path = args.out_dir / "result.json"
    summary_path = args.out_dir / "summary.txt"
    result_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    lines = [
        f"passed: {status['passed']}",
        f"verdict: {status['verdict']}",
        f"boot_mode: {status['boot_mode']}",
        f"safety_island_mode: {args.si_mode}",
        f"smmu_backend: {status['smmu_backend']}",
        f"mhu_backend: {status['mhu_backend']}",
        f"qbox_performance_preset: {status['qbox_performance_preset']}",
        "qbox_performance_options: "
        + json.dumps(status["qbox_performance_options"], sort_keys=True),
        "ap_high_dram_handoff_patch: "
        + json.dumps(status["ap_high_dram_handoff_patch"], sort_keys=True),
        "ap_high_dram_signed_handoff: "
        + json.dumps(status["ap_high_dram_signed_handoff"], sort_keys=True),
        "rse_otp_auto_provision: "
        + json.dumps(status["rse_otp_auto_provision"], sort_keys=True),
        f"range_limited_flash_dmi: {status['range_limited_flash_dmi']}",
        f"live_trace: {status['live_trace']}",
        f"blocker: {status['blocker'] or 'none'}",
        "rse_boot_timing_profile: "
        + json.dumps(status["rse_boot_timing_profile"], sort_keys=True),
        "completion_gates:",
        *[f"  - {gate}: {verdict}" for gate, verdict in gates.items()],
        "input_artifacts:",
        *[
            f"  - {name}: {record['path']} exists={record['exists']} size={record['size']}"
            for name, record in input_artifacts.items()
        ],
        "console_logs:",
        *[f"  - {name}: {path}" for name, path in console_logs.items()],
    ]
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(args.out_dir)
    print(summary_path)
    print(result_path)
    return 0 if passed else 1


def first_failing_marker(marker_groups: Any) -> str | None:
    if not isinstance(marker_groups, dict):
        return None
    ordered_groups = [
        group for group in MARKER_GROUP_PRIORITY if group in marker_groups
    ]
    ordered_groups.extend(
        group for group in marker_groups if group not in set(ordered_groups)
    )
    for group in ordered_groups:
        hits = marker_groups.get(group)
        if not isinstance(hits, dict):
            continue
        for marker, hit in hits.items():
            if not hit:
                return f"{group}:{marker}"
    return None


def copy_child_logs(args: argparse.Namespace) -> None:
    aliases = {
        "qbox-platform.log": "qbox-platform.log",
        "qbox-rse.log": "qbox-rse.log",
        "qbox-secure-console.log": "qbox-secure-console.log",
        "qbox-primary-console.log": "qbox-primary-console.log",
    }
    if args.si_mode != "live-cl0-cl1":
        aliases["qbox-scp.log"] = "qbox-safety-island-cl0.log"
    for src_name, dst_name in aliases.items():
        src = args.out_dir / src_name
        dst = args.out_dir / dst_name
        if src.exists() and src != dst:
            shutil.copy2(src, dst)
    cl1 = args.out_dir / "qbox-safety-island-cl1.log"
    if not cl1.exists():
        write_text(
            cl1,
            "Apollo full-system CL1 log placeholder.\n"
            f"safety_island_mode: {args.si_mode}\n"
            "live CL1 is not yet wired in the service-model baseline.\n",
        )


def clear_run_outputs(out_dir: Path) -> None:
    stale_files = {
        "result.json",
        "summary.txt",
        RD_ASPEN_CHILD_RESULT,
        "rd-aspen-summary.txt",
        "post-login-probe-actions.log",
        "primary-uart-input.fifo",
        "comparison.json",
        "map-comparison.json",
        "coverage-audit.json",
        "final-verification.json",
        "ap-si-mhuv3-trace.log",
        "si-cl1-mhuv3-trace.log",
        "si-cl0-pc-trace.log",
    }
    stale_files.update(CONSOLE_LOGS.values())
    stale_files.add("qbox-scp.log")
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in stale_files:
        path = out_dir / name
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def write_blocker_logs(args: argparse.Namespace, blocker: str) -> None:
    for name, filename in CONSOLE_LOGS.items():
        write_text(
            args.out_dir / filename,
            "Apollo full-system QBox run did not start.\n"
            f"console: {name}\n"
            f"blocker: {blocker}\n",
        )


def live_mode_blocker(args: argparse.Namespace) -> str | None:
    if args.isolated:
        return None
    return None


def isolated_command(args: argparse.Namespace, artifacts: dict[str, Path]) -> list[str]:
    root = workspace_root()
    if args.si_mode != "live-cl1":
        raise ValueError("--isolated is currently implemented only for --si-mode live-cl1")
    cmd = [
        sys.executable,
        str(root / "scripts/run_qbox_apollo_fvp_si_cl1.py"),
        "--image",
        str(artifacts["si_cl1_image"]),
        "--symbols",
        str(artifacts["si_cl1_symbols"]),
        "--out-dir",
        str(args.out_dir),
        "--timeout",
        str(args.timeout),
        "--jobs",
        str(args.jobs),
    ]
    if args.skip_build:
        cmd.append("--skip-build")
    return cmd


def run_isolated(args: argparse.Namespace, artifacts: dict[str, Path]) -> int:
    cmd = isolated_command(args, artifacts)
    print("+ " + " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=workspace_root(), check=False)
    return proc.returncode


def wait_for_keep_running_child_pass(
    args: argparse.Namespace,
    proc: subprocess.Popen[bytes],
    command: list[str],
) -> int:
    start = time.monotonic()
    result_path = args.out_dir / "result.json"
    while True:
        child_status = read_json(result_path)
        if child_status.get("passed"):
            return 0

        synthesized = synthesize_keep_running_child_status(
            args,
            command,
            child_returncode=proc.poll(),
        )
        if synthesized.get("passed"):
            write_keep_running_child_result(
                args,
                command,
                child_returncode=proc.poll(),
            )
            return 0

        rc = proc.poll()
        if rc is not None:
            if not result_path.exists():
                write_keep_running_child_result(
                    args,
                    command,
                    child_returncode=rc,
                    blocker=f"child_failed:{rc}",
                )
            return rc

        if args.timeout > 0 and time.monotonic() - start >= args.timeout:
            proc.terminate()
            try:
                rc = proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                rc = proc.wait(timeout=10)
            write_keep_running_child_result(
                args,
                command,
                child_returncode=rc,
                blocker="child_keep_running_timeout",
            )
            return rc if rc else 1

        time.sleep(0.2)


def child_command(args: argparse.Namespace, artifacts: dict[str, Path]) -> list[str]:
    root = workspace_root()
    scp_strategy = "service-model"
    if args.si_mode == "live-cl0-cl1":
        scp_strategy = "real-si-scp"
    cmd = [
        sys.executable,
        str(root / "scripts/run_qbox_fvp_rd_aspen_rse.py"),
        "--conf",
        str(args.conf),
        "--rse-rom",
        str(artifacts["rse_rom"]),
        "--rse-flash",
        str(artifacts["rse_flash"]),
        "--rse-otp",
        str(artifacts["rse_otp"]),
        "--ap-flash",
        str(artifacts["ap_flash"]),
        "--ap-bl2-elf",
        str(artifacts["ap_bl2_elf"]),
        "--rse-bl1-2-elf",
        str(artifacts["rse_bl1_2_elf"]),
        "--rse-bl2-elf",
        str(artifacts["rse_bl2_elf"]),
        "--rootfs",
        str(artifacts["rootfs"]),
        "--efi-capsule-disk",
        str(artifacts["efi_capsule_disk"]),
        "--provisioning-bundle",
        str(artifacts["provisioning_bundle"]),
        "--out-dir",
        str(args.out_dir),
        "--timeout",
        str(args.timeout),
        "--jobs",
        str(args.jobs),
        "--scp-strategy",
        scp_strategy,
        "--smmu-backend",
        args.smmu_backend,
        "--rootfs-bootargs-profile",
        args.rootfs_bootargs_profile,
        "--primary-login-prompt",
        "apollo-fvp login:",
        "--primary-shell-marker",
        "~ #",
        "--primary-shell-prompt-re",
        r"(?:root@apollo-fvp[^\n]*[#>]|\S+ #)\s*$",
    ]
    if args.skip_build:
        cmd.append("--skip-build")
    if args.no_copy_writable_flash:
        cmd.append("--no-copy-writable-flash")
    if args.range_limited_flash_dmi:
        cmd.append("--range-limited-flash-dmi")
    if args.cc3xx_stats:
        cmd.append("--cc3xx-stats")
        cmd.extend(["--cc3xx-stats-interval", str(args.cc3xx_stats_interval)])
    if args.qbox_perf_profile:
        cmd.append("--qbox-perf-profile")
        cmd.extend([
            "--qbox-perf-profile-interval",
            str(args.qbox_perf_profile_interval),
        ])
    if args.remotepass_dmi_cache:
        cmd.append("--remotepass-dmi-cache")
    if args.rse_hotpath_accel:
        cmd.append("--rse-hotpath-accel")
        cmd.extend(["--rse-hotpath-max-bytes", str(args.rse_hotpath_max_bytes)])
    if args.rse_hotpath_memcpy_addr is not None:
        cmd.extend(["--rse-hotpath-memcpy-addr", hex(args.rse_hotpath_memcpy_addr)])
    if args.rse_hotpath_memset_addr is not None:
        cmd.extend(["--rse-hotpath-memset-addr", hex(args.rse_hotpath_memset_addr)])
    if args.rse_bl2_libc_hotpath:
        cmd.append("--rse-bl2-libc-hotpath")
    if args.rse_lms_accel:
        cmd.append("--rse-lms-accel")
        cmd.extend(["--rse-lms-max-data-bytes", str(args.rse_lms_max_data_bytes)])
    if args.rse_lms_verify_addr is not None:
        cmd.extend(["--rse-lms-verify-addr", hex(args.rse_lms_verify_addr)])
    if args.rse_bl2_load_accel:
        cmd.append("--rse-bl2-load-accel")
        cmd.extend([
            "--rse-bl2-load-accel-max-bytes",
            str(args.rse_bl2_load_accel_max_bytes),
        ])
    if args.rse_bl2_boot_enc_accel:
        cmd.append("--rse-bl2-boot-enc-accel")
    if args.rse_bl2_img_hash_accel:
        cmd.append("--rse-bl2-img-hash-accel")
        cmd.extend([
            "--rse-bl2-img-hash-max-bytes",
            str(args.rse_bl2_img_hash_max_bytes),
            "--rse-bl2-img-hash-max-seed-bytes",
            str(args.rse_bl2_img_hash_max_seed_bytes),
        ])
    if args.rse_bl2_verify_sig_accel:
        cmd.append("--rse-bl2-verify-sig-accel")
        cmd.extend([
            "--rse-bl2-verify-sig-max-key-bytes",
            str(args.rse_bl2_verify_sig_max_key_bytes),
            "--rse-bl2-verify-sig-max-sig-bytes",
            str(args.rse_bl2_verify_sig_max_sig_bytes),
        ])
    if args.rse_bl2_verify_sig_skip:
        cmd.append("--rse-bl2-verify-sig-skip")
    if args.rse_bl2_delay_accel:
        cmd.append("--rse-bl2-delay-accel")
        cmd.extend([
            "--rse-bl2-delay-max-cycles",
            str(args.rse_bl2_delay_max_cycles),
            "--rse-bl2-delay-expected-hits",
            str(args.rse_bl2_delay_expected_hits),
        ])
    if args.cc3xx_status_read_fastpath:
        cmd.append("--cc3xx-status-read-fastpath")
    if args.cc3xx_qemu_native_backend:
        cmd.append("--cc3xx-qemu-native-backend")
    if args.cc3xx_local_mmio_fastpath:
        cmd.append("--cc3xx-local-mmio-fastpath")
    if args.rse_fast_boot_aliases:
        cmd.append("--rse-fast-boot-aliases")
    if getattr(args, "provision_blank_rse_otp", False):
        cmd.append("--allow-blank-rse-otp")
    if args.post_login_probe:
        cmd.append("--post-login-probe")
    if args.keep_running_after_pass:
        cmd.append("--keep-running-after-pass")
    if args.build_only:
        cmd.append("--check-only")
    for param in args.platform_param:
        cmd.extend(["--platform-param", param])
    return cmd + args.forward_args


def run_child(args: argparse.Namespace, artifacts: dict[str, Path]) -> tuple[int, list[str]]:
    cmd = child_command(args, artifacts)
    clear_run_outputs(args.out_dir)
    print("+ " + " ".join(cmd), flush=True)
    env = os.environ.copy()
    env["QBOX_APOLLO_FULL_SI_MODE"] = args.si_mode
    if not args.build_only:
        # Full-system runtime evidence must include the AP firmware/Linux path.
        # The reused RD-Aspen runner only enables AP CPUs for probe-oriented
        # runs by default, which is useful for RSE-only diagnostics but is not
        # a valid Apollo full-system runtime shape.
        env["QBOX_RDASPEN_ENABLE_AP_CPUS"] = "true"
    if args.si_mode == "live-cl0-cl1":
        env["QBOX_APOLLO_FULL_LIVE_CL0"] = "true"
        env["QBOX_APOLLO_FULL_SI_CL0_IMAGE"] = str(artifacts["si_cl0_image"])
        env["QBOX_APOLLO_FULL_SI_CL0_LOG"] = str(
            (args.out_dir / "qbox-safety-island-cl0.log").resolve()
        )
        if args.live_trace:
            env["QBOX_APOLLO_FULL_SI_GIC_MULTIVIEW_TRACE"] = "true"
            env["QBOX_APOLLO_FULL_SI_CL0_PC_TRACE"] = "true"
            env["QBOX_APOLLO_FULL_SI_CL0_EXCEPTION_TRACE"] = "true"
            env["QBOX_APOLLO_FULL_SI_CL0_PC_TRACE_LIMIT"] = "4096"
            env["QBOX_APOLLO_FULL_SI_CL0_PC_TRACE_FILE"] = str(
                (args.out_dir / "si-cl0-pc-trace.log").resolve()
            )
    if args.si_mode in {"live-cl1", "live-cl0-cl1"}:
        env["QBOX_APOLLO_FULL_LIVE_CL1"] = "true"
        env["QBOX_APOLLO_FULL_SI_CL1_IMAGE"] = str(artifacts["si_cl1_image"])
        env["QBOX_APOLLO_FULL_SI_CL1_LOG"] = str(
            (args.out_dir / "qbox-safety-island-cl1.log").resolve()
        )
        if args.live_trace:
            env["QBOX_APOLLO_FULL_SI_CL1_MHU_TRACE"] = "true"
            env["QBOX_APOLLO_FULL_SI_CL1_MHU_TRACE_LIMIT"] = "8192"
            env["QBOX_RDASPEN_MHU_TRACE"] = "true"
            env["QBOX_RDASPEN_MHU_TRACE_LIMIT"] = "8192"
            env["QBOX_RDASPEN_MHU_TRACE_FILE"] = str(
                (args.out_dir / "ap-si-mhuv3-trace.log").resolve()
            )
            env["QBOX_APOLLO_FULL_SI_CL1_MHU_TRACE_FILE"] = str(
                (args.out_dir / "si-cl1-mhuv3-trace.log").resolve()
            )
    if args.keep_running_after_pass and not args.build_only:
        env["QBOX_RDASPEN_RESULT_PATH"] = str(
            (args.out_dir / RD_ASPEN_CHILD_RESULT).resolve()
        )
        env["QBOX_RDASPEN_SUMMARY_PATH"] = str(
            (args.out_dir / "rd-aspen-summary.txt").resolve()
        )
        proc = subprocess.Popen(cmd, cwd=workspace_root(), env=env)
        return wait_for_keep_running_child_pass(args, proc, cmd), cmd

    proc = subprocess.run(cmd, cwd=workspace_root(), env=env, check=False)
    return proc.returncode, cmd


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--conf",
        type=Path,
        default=root / "tools/qbox/platforms/apollo/apollo-qvp.lua",
    )
    parser.add_argument(
        "--local-build-dir",
        type=Path,
        default=root / "build/local-apollo-fvp",
    )
    parser.add_argument(
        "--si-mode",
        choices=["service-model", "live-cl1", "live-cl0-cl1"],
        default="service-model",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "build/qbox-apollo-fvp" / f"full-{timestamp()}",
    )
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--build-only", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument(
        "--auto-provision-rse-otp",
        dest="auto_provision_rse_otp",
        action="store_true",
        help=(
            "Fallback for legacy or experimental local-build outputs: when "
            "the RSE OTP image is all zeroes, run a bounded CM-lifecycle QBox "
            "provisioning pass first and persist the resulting OTP before the "
            "requested full-system boot."
        ),
    )
    parser.add_argument(
        "--no-auto-provision-rse-otp",
        dest="auto_provision_rse_otp",
        action="store_false",
        help="Disable the blank RSE OTP fallback helper.",
    )
    parser.add_argument("--rse-otp-provision-timeout", type=int, default=600)
    parser.add_argument(
        "--isolated",
        action="store_true",
        help="Run the isolated live Safety Island mode for this --si-mode.",
    )
    parser.add_argument("--post-login-probe", action="store_true")
    parser.add_argument(
        "--keep-running-after-pass",
        action="store_true",
        help=(
            "Forward to the RSE-oriented runner so QBox remains alive after "
            "the pass condition."
        ),
    )
    parser.add_argument(
        "--smmu-backend",
        choices=["qemu-arm-smmuv3", "systemc-mmu720ae"],
        default="systemc-mmu720ae",
        help="Forwarded SMMU backend for the AP side of the QBox platform.",
    )
    parser.add_argument("--no-copy-writable-flash", action="store_true")
    parser.add_argument("--rootfs-bootargs-profile", default="none")
    perf_group = parser.add_mutually_exclusive_group()
    perf_group.add_argument(
        "--qbox-performance-preset",
        dest="qbox_performance_preset",
        action="store_true",
        help=(
            "Enable the validated QBox Apollo full-system boot acceleration "
            "preset. This is the default."
        ),
    )
    perf_group.add_argument(
        "--no-qbox-performance-preset",
        dest="qbox_performance_preset",
        action="store_false",
        help=(
            "Disable the default acceleration preset for fidelity or debug "
            "experiments."
        ),
    )
    dmi_group = parser.add_mutually_exclusive_group()
    dmi_group.add_argument(
        "--range-limited-flash-dmi",
        dest="range_limited_flash_dmi",
        action="store_true",
        help=(
            "Forward the storage-safe Strata flash DMI fast path to the "
            "RD-Aspen runner. This is enabled by default for Apollo full-system "
            "boot performance."
        ),
    )
    dmi_group.add_argument(
        "--no-range-limited-flash-dmi",
        dest="range_limited_flash_dmi",
        action="store_false",
        help=(
            "Disable the range-limited flash DMI fast path for storage "
            "fidelity experiments."
        ),
    )
    parser.set_defaults(qbox_performance_preset=True, range_limited_flash_dmi=True)
    parser.set_defaults(auto_provision_rse_otp=True)
    parser.add_argument(
        "--cc3xx-stats",
        action="store_true",
        help="Forward CC3XX aggregate statistics collection to the RSE runner.",
    )
    parser.add_argument(
        "--qbox-perf-profile",
        action="store_true",
        help=(
            "Forward QBox-side performance profile collection to the RSE "
            "runner."
        ),
    )
    parser.add_argument("--qbox-perf-profile-interval", type=int, default=1024)
    parser.add_argument(
        "--remotepass-dmi-cache",
        action="store_true",
        help="Forward the RSE RemotePass shared-memory DMI cache option.",
    )
    parser.add_argument(
        "--rse-hotpath-accel",
        action="store_true",
        help="Forward RSE BL1_1 memcpy/memset semantic hotpath acceleration.",
    )
    parser.add_argument("--rse-hotpath-max-bytes", type=int, default=16 * 1024 * 1024)
    parser.add_argument(
        "--rse-hotpath-memcpy-addr",
        type=lambda value: int(value, 0),
        help="Forward RSE hotpath memcpy Thumb entry address override.",
    )
    parser.add_argument(
        "--rse-hotpath-memset-addr",
        type=lambda value: int(value, 0),
        help="Forward RSE hotpath memset Thumb entry address override.",
    )
    parser.add_argument(
        "--rse-bl2-libc-hotpath",
        action="store_true",
        help="Forward RSE BL2 libc memcpy/memset hotpath selection.",
    )
    parser.add_argument(
        "--rse-lms-accel",
        action="store_true",
        help=(
            "Forward experimental RSE BL1_2 LMS verify semantic acceleration. "
            "Confirm effectiveness from the forwarded RSE perf profile "
            "lms_hits counter."
        ),
    )
    parser.add_argument("--rse-lms-max-data-bytes", type=int, default=16 * 1024 * 1024)
    parser.add_argument(
        "--rse-lms-verify-addr",
        type=lambda value: int(value, 0),
        help="Forward RSE BL1_2 pq_crypto_verify Thumb entry override.",
    )
    parser.add_argument(
        "--rse-bl2-load-accel",
        action="store_true",
        help="Forward RSE BL2 RAM-load payload semantic acceleration.",
    )
    parser.add_argument("--rse-bl2-load-accel-max-bytes", type=int, default=16 * 1024 * 1024)
    parser.add_argument(
        "--rse-bl2-boot-enc-accel",
        action="store_true",
        help="Forward RSE BL2 boot_enc_decrypt semantic acceleration.",
    )
    parser.add_argument(
        "--rse-bl2-img-hash-accel",
        action="store_true",
        help="Forward RSE BL2 bootutil_img_hash host-native SHA256 acceleration.",
    )
    parser.add_argument("--rse-bl2-img-hash-max-bytes", type=int, default=16 * 1024 * 1024)
    parser.add_argument("--rse-bl2-img-hash-max-seed-bytes", type=int, default=4096)
    parser.add_argument(
        "--rse-bl2-verify-sig-accel",
        action="store_true",
        help="Forward RSE BL2 bootutil_verify_sig host-native ECDSA acceleration.",
    )
    parser.add_argument(
        "--rse-bl2-verify-sig-skip",
        action="store_true",
        help=(
            "Forward the positive-boot-only RSE BL2 bootutil_verify_sig skip "
            "after host-native ECDSA verification succeeds."
        ),
    )
    parser.add_argument("--rse-bl2-verify-sig-max-key-bytes", type=int, default=512)
    parser.add_argument("--rse-bl2-verify-sig-max-sig-bytes", type=int, default=128)
    parser.add_argument(
        "--rse-bl2-delay-accel",
        action="store_true",
        help=(
            "Forward RSE BL2 delay_cycles acceleration for LBIST, MBIST, "
            "and CL1 boot wait mimic loops."
        ),
    )
    parser.add_argument("--rse-bl2-delay-max-cycles", type=int, default=50 * 1000 * 1000)
    parser.add_argument("--rse-bl2-delay-expected-hits", type=int, default=3)
    parser.add_argument("--cc3xx-stats-interval", type=int, default=1024)
    parser.add_argument(
        "--cc3xx-status-read-fastpath",
        action="store_true",
        help="Forward the RSE CC3XX QEMU-side status-read fast path.",
    )
    parser.add_argument(
        "--cc3xx-qemu-native-backend",
        action="store_true",
        help=(
            "Forward the RSE CC3XX QEMU-native backend selection. This also "
            "enables the CC3XX direct MMIO fast path in the RSE runner."
        ),
    )
    parser.add_argument(
        "--cc3xx-local-mmio-fastpath",
        action="store_true",
        help="Forward the RSE CC3XX QEMU-local direct MMIO fast path.",
    )
    parser.add_argument(
        "--rse-fast-boot-aliases",
        action="store_true",
        help=(
            "Forward the validated RSE fast-boot direct alias preset to the "
            "RSE runner."
        ),
    )
    parser.add_argument(
        "--live-trace",
        action="store_true",
        help=(
            "Enable verbose live Safety Island GIC/MHU/PC traces. The "
            "default keeps UART logs and runtime markers but avoids trace "
            "overhead during boot-performance checks."
        ),
    )
    parser.add_argument("--platform-param", action="append", default=[])
    parser.add_argument("--rse-rom", type=Path)
    parser.add_argument("--rse-flash", type=Path)
    parser.add_argument("--rse-otp", type=Path)
    parser.add_argument("--ap-flash", type=Path)
    parser.add_argument("--ap-bl2-elf", type=Path)
    parser.add_argument("--rse-bl1-2-elf", type=Path)
    parser.add_argument("--rse-bl2-elf", type=Path)
    parser.add_argument("--rootfs", type=Path)
    parser.add_argument("--efi-capsule-disk", type=Path)
    parser.add_argument("--provisioning-bundle", type=Path)
    parser.add_argument("--ap-dtb", type=Path)
    parser.add_argument("--rse-symbols", type=Path)
    parser.add_argument("--si-cl0-image", type=Path)
    parser.add_argument("--si-cl1-image", type=Path)
    parser.add_argument("--si-cl1-symbols", type=Path)
    args, forward_args = parser.parse_known_args()
    args.forward_args = forward_args
    args.conf = args.conf.resolve()
    args.local_build_dir = args.local_build_dir.resolve()
    args.out_dir = args.out_dir.resolve()
    if args.qbox_performance_preset:
        args.remotepass_dmi_cache = True
        args.rse_hotpath_accel = True
        args.rse_bl2_libc_hotpath = True
        args.rse_lms_accel = True
        args.rse_bl2_load_accel = True
        args.rse_bl2_boot_enc_accel = True
        args.rse_bl2_img_hash_accel = True
        args.rse_bl2_verify_sig_accel = True
        args.rse_bl2_delay_accel = True
        args.cc3xx_qemu_native_backend = True
        args.rse_fast_boot_aliases = True
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
    if args.rse_otp_provision_timeout <= 0:
        parser.error("--rse-otp-provision-timeout must be positive")
    if args.rse_bl2_verify_sig_skip:
        args.rse_bl2_verify_sig_accel = True
    return args


def main() -> int:
    args = parse_args()
    args.provision_blank_rse_otp = False
    args.rse_otp_auto_provision = {
        "enabled": args.auto_provision_rse_otp,
        "requested": False,
        "reason": "not_evaluated",
    }
    artifacts = resolved_artifacts(args)
    print("Preparing signed AP flash and high-DRAM boot artifacts...", flush=True)
    args.ap_high_dram_signed_handoff = prepare_signed_high_dram_ap_flash(args, artifacts)
    print(
        "Signed AP flash preparation: "
        + str(args.ap_high_dram_signed_handoff.get("state", "unknown")),
        flush=True,
    )
    args.ap_high_dram_handoff_patch = prepare_migrated_boot_artifacts(args, artifacts)
    print(
        "Boot disk high-DRAM preparation: "
        + str(args.ap_high_dram_handoff_patch.get("state", "unknown")),
        flush=True,
    )
    debug_manifest_blocker = ensure_default_debug_manifest(args, artifacts)
    missing = missing_required(args, artifacts)
    signed_handoff_blocker = args.ap_high_dram_signed_handoff.get("blocker")
    blocker = (
        signed_handoff_blocker
        or debug_manifest_blocker
        or ("; ".join(missing) if missing else None)
    )
    if args.check_only or blocker:
        return write_result(
            args,
            artifacts,
            command=[],
            child_status=None,
            child_returncode=None,
            blocker=blocker,
            check_only=True,
        )

    if args.isolated:
        if args.si_mode != "live-cl1":
            blocker = "isolated_mode_not_implemented_for:" + args.si_mode
            write_blocker_logs(args, blocker)
            return write_result(
                args,
                artifacts,
                command=[],
                child_status=None,
                child_returncode=None,
                blocker=blocker,
                check_only=False,
            )
        return run_isolated(args, artifacts)

    blocker = live_mode_blocker(args)
    if blocker:
        write_blocker_logs(args, blocker)
        return write_result(
            args,
            artifacts,
            command=[],
            child_status=None,
            child_returncode=None,
            blocker=blocker,
            check_only=False,
        )

    blocker = auto_provision_rse_otp(args, artifacts)
    if blocker:
        write_blocker_logs(args, blocker)
        return write_result(
            args,
            artifacts,
            command=[],
            child_status=None,
            child_returncode=None,
            blocker=blocker,
            check_only=False,
        )

    child_rc, command = run_child(args, artifacts)
    child_result = args.out_dir / "result.json"
    child_status = read_json(child_result)
    if child_status:
        shutil.copy2(child_result, args.out_dir / RD_ASPEN_CHILD_RESULT)
    copy_child_logs(args)
    blocker = child_status.get("blocker") if child_status else f"child_failed:{child_rc}"
    if child_status and not child_status.get("passed") and not blocker and child_rc:
        blocker = f"child_failed:{child_rc}"
    if args.build_only and blocker == "check_only_no_runtime":
        child_status["passed"] = True
        child_status["blocker"] = None
        child_status["apollo_full_note"] = "build_only_no_runtime"
        blocker = None
    if child_status and child_status.get("passed"):
        blocker = None
    return write_result(
        args,
        artifacts,
        command=command,
        child_status=child_status,
        child_returncode=child_rc,
        blocker=blocker,
        check_only=False,
    )


if __name__ == "__main__":
    raise SystemExit(main())
