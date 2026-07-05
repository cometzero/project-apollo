#!/usr/bin/env python3
"""Prepare and smoke-test GDB debug helpers for QBox RD-Aspen RSE boot."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import textwrap
import time


PLATFORM_STDOUT_LOG = "qbox-platform.log"
RANGE_LIMITED_FLASH_DMI_DEFAULTS = {
    "QBOX_RDASPEN_ATU_DMI": "true",
    "QBOX_RDASPEN_BOOT_FLASH_DMI": "true",
    "QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES": "0x7000:0x260000",
    "QBOX_RDASPEN_HOST_MEMORY_DMI": "true",
    "QBOX_RDASPEN_AP_FLASH_DMI_RANGES": "0x7000:0x240000",
}


def qbox_probe_env_defaults(
    run_dir: Path,
    range_limited_flash_dmi: bool = False,
    flash_stats: bool = False,
    flash_stats_interval: int = 512,
    mhu_trace: bool = True,
    mhu_trace_limit: int = 2000,
) -> dict[str, str]:
    env = {
        "QBOX_RDASPEN_ENABLE_AP_CPUS": "true",
        "QBOX_RDASPEN_RSE_LOCAL_CRYPTO": "true",
        "QBOX_RDASPEN_RSE_LOCAL_BOOT_FLASH": "true",
        "QBOX_RDASPEN_ATU_DMI": "false",
        "QBOX_RDASPEN_BOOT_FLASH_DMI": "false",
        "QBOX_RDASPEN_BOOT_FLASH_DMI_RANGES": "",
        "QBOX_RDASPEN_HOST_MEMORY_DMI": "false",
        "QBOX_RDASPEN_AP_FLASH_DMI_RANGES": "",
        "QBOX_RDASPEN_RSE_DTCM_DMI": "true",
        "QBOX_RDASPEN_RSE_ITCM_DMI": "true",
        "QBOX_RDASPEN_RSE_VM_DMI": "true",
        "QBOX_RDASPEN_MHU_TRACE": "true" if mhu_trace else "false",
        "QBOX_RDASPEN_MHU_TRACE_LIMIT": str(mhu_trace_limit),
        "QBOX_RDASPEN_MHU_TRACE_FILE": str(run_dir / "mhuv3-trace.log"),
    }
    if range_limited_flash_dmi:
        env.update(RANGE_LIMITED_FLASH_DMI_DEFAULTS)
    if flash_stats:
        env.update(
            {
                "QBOX_RDASPEN_RSE_BOOT_FLASH_STATS_FILE": str(
                    run_dir / "rse-strata-stats.json"
                ),
                "QBOX_RDASPEN_AP_FLASH_STATS_FILE": str(
                    run_dir / "ap-strata-stats.json"
                ),
                "QBOX_RDASPEN_FLASH_STATS_INTERVAL": str(flash_stats_interval),
            }
        )
    return env


def shell_env_block(
    run_dir: Path,
    indent: str = "",
    range_limited_flash_dmi: bool = False,
    flash_stats: bool = False,
    flash_stats_interval: int = 512,
    mhu_trace: bool = True,
    mhu_trace_limit: int = 2000,
) -> str:
    env = qbox_probe_env(
        run_dir,
        range_limited_flash_dmi,
        flash_stats,
        flash_stats_interval,
        mhu_trace,
        mhu_trace_limit,
    )
    return (" \\\n" + indent).join(
        f"{key}={env[key]}"
        for key in qbox_probe_env_defaults(
            run_dir,
            range_limited_flash_dmi,
            flash_stats,
            flash_stats_interval,
            mhu_trace,
            mhu_trace_limit,
        )
    )


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def first_match(root: Path, pattern: str) -> Path | None:
    matches = sorted(root.glob(pattern))
    return matches[0] if matches else None


def rel(root: Path, path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def symbol_paths(root: Path) -> dict[str, Path | None]:
    deploy = root / "build/tmp_baremetal/deploy/images/fvp-rd-aspen"
    tfm = (
        "build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/"
        "trusted-firmware-m/*/build/bin"
    )
    linux = (
        "build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/"
        "linux-yocto-rt/*/linux-fvp_rd_aspen-preempt-rt-build"
    )
    scp = (
        "build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/"
        "scp-firmware/*/build/ramfw/si0/bin"
    )
    tfa = (
        "build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/"
        "trusted-firmware-a/*"
    )
    uboot = "build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/u-boot/*"
    optee = "build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/optee-os/*"
    ts_se_proxy = (
        "build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/"
        "ts-sp-se-proxy/*"
    )
    ts_smm_gateway = (
        "build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/"
        "ts-sp-smm-gateway/*"
    )
    zephyr = (
        "build/tmp_baremetal/work/fvp_rd_aspen_safety_island_c1-zephyr/"
        "zephyr-demos-cl1/*/deploy-zephyr-demos-cl1"
    )
    return {
        "tfm_bl1_1": first_match(root, f"{tfm}/bl1_1.elf"),
        "tfm_bl1_2": first_match(root, f"{tfm}/bl1_2.elf"),
        "tfm_bl2": first_match(root, f"{tfm}/bl2.elf"),
        "tfm_s": first_match(root, f"{tfm}/tfm_s.elf"),
        "scp_firmware": first_match(root, f"{scp}/rdaspen-si0-bl2.elf")
        or deploy / "si0_ramfw.elf",
        "tfa_bl31": first_match(root, f"{tfa}/build/rdaspen/debug/bl31/bl31.elf"),
        "tfa_bl2": first_match(root, f"{tfa}/build/rdaspen/debug/bl2/bl2.elf"),
        "optee_core": first_match(root, f"{optee}/build/core/tee.elf")
        or deploy / "optee/tee.elf",
        "u_boot": first_match(root, f"{uboot}/build/u-boot"),
        "ts_se_proxy": first_match(root, f"{ts_se_proxy}/build/se-proxy_*"),
        "ts_smm_gateway": first_match(root, f"{ts_smm_gateway}/build/smm-gateway_*"),
        "linux_vmlinux": first_match(root, f"{linux}/vmlinux"),
        "linux_system_map": first_match(root, f"{linux}/System.map"),
        "linux_image": first_match(root, f"{linux}/arch/arm64/boot/Image"),
        "si_cl1_zephyr": deploy / "zephyr-demos-cl1.elf"
        if (deploy / "zephyr-demos-cl1.elf").exists()
        else first_match(root, f"{zephyr}/zephyr-demos-cl1.elf"),
    }


def yocto_work_entry(root: Path, recipe: str) -> Path | None:
    return first_match(root, f"build/tmp_baremetal/work/fvp_rd_aspen-poky-linux/{recipe}/*")


def source_paths(root: Path) -> dict[str, Path | None]:
    tfm_work = yocto_work_entry(root, "trusted-firmware-m")
    scp_work = yocto_work_entry(root, "scp-firmware")
    tfa_work = yocto_work_entry(root, "trusted-firmware-a")
    uboot_work = yocto_work_entry(root, "u-boot")
    optee_work = yocto_work_entry(root, "optee-os")
    linux_work = yocto_work_entry(root, "linux-yocto-rt")
    ts_se_proxy_work = yocto_work_entry(root, "ts-sp-se-proxy")
    ts_smm_gateway_work = yocto_work_entry(root, "ts-sp-smm-gateway")
    zephyr_work = first_match(
        root,
        "build/tmp_baremetal/work/fvp-rd-aspen_safety_island_c1-zephyr/"
        "zephyr-demos-cl1/*",
    ) or first_match(
        root,
        "build/tmp_baremetal/work/fvp_rd_aspen_safety_island_c1-zephyr/"
        "zephyr-demos-cl1/*",
    )
    tfm_git = tfm_work / "git" if tfm_work else None
    tfm_nested = tfm_git / "tfm" if tfm_git else None
    tfm_source = tfm_nested if tfm_nested and tfm_nested.exists() else tfm_git
    linux_build = (
        linux_work / "linux-fvp_rd_aspen-preempt-rt-build" if linux_work else None
    )
    linux_git = linux_work / "git" if linux_work else None
    linux_source = linux_git if linux_git and linux_git.exists() else linux_build
    zephyr_git = zephyr_work / "git" if zephyr_work else None
    zephyr_build = zephyr_work / "build" if zephyr_work else None
    paths: dict[str, Path | None] = {
        "tfm_work": tfm_work,
        "tfm_source": tfm_source,
        "scp_work": scp_work,
        "scp_source": scp_work / "git" if scp_work else None,
        "tfa_work": tfa_work,
        "tfa_source": tfa_work / "git" if tfa_work else None,
        "uboot_work": uboot_work,
        "uboot_source": uboot_work / "git" if uboot_work else None,
        "optee_work": optee_work,
        "optee_source": optee_work / "git" if optee_work else None,
        "ts_se_proxy_work": ts_se_proxy_work,
        "ts_se_proxy_source": ts_se_proxy_work / "git" if ts_se_proxy_work else None,
        "ts_smm_gateway_work": ts_smm_gateway_work,
        "ts_smm_gateway_source": (
            ts_smm_gateway_work / "git" if ts_smm_gateway_work else None
        ),
        "linux_work": linux_work,
        "linux_source": linux_source,
        "linux_build": linux_build,
        "zephyr_work": zephyr_work,
        "zephyr_source": zephyr_git,
        "zephyr_build": zephyr_build,
    }
    return {key: path for key, path in paths.items() if path is None or path.exists()}


def source_map_lines(sources: dict[str, Path | None], components: list[str]) -> str:
    lines = ["set debuginfod enabled off"]
    component_recipes = {
        "tfm": ("tfm_work", "tfm_source", "trusted-firmware-m"),
        "scp": ("scp_work", "scp_source", "scp-firmware"),
        "tfa": ("tfa_work", "tfa_source", "trusted-firmware-a"),
        "uboot": ("uboot_work", "uboot_source", "u-boot"),
        "optee": ("optee_work", "optee_source", "optee-os"),
        "linux": ("linux_work", "linux_source", "linux-yocto-rt"),
        "ts_se_proxy": ("ts_se_proxy_work", "ts_se_proxy_source", "ts-sp-se-proxy"),
        "ts_smm_gateway": (
            "ts_smm_gateway_work",
            "ts_smm_gateway_source",
            "ts-sp-smm-gateway",
        ),
        "zephyr": ("zephyr_work", "zephyr_source", "zephyr-demos-cl1"),
    }
    for component in components:
        work_key, source_key, recipe = component_recipes[component]
        work = sources.get(work_key)
        source = sources.get(source_key)
        if work is None or source is None:
            continue
        lines.append(f"set substitute-path /usr/src/debug/{recipe}/{work.name} {source}")
        lines.append(f"directory {source}")
    if (
        "linux" in components
        and sources.get("linux_build") is not None
        and sources.get("linux_build") != sources.get("linux_source")
    ):
        lines.append(f"directory {sources['linux_build']}")
    if (
        "zephyr" in components
        and sources.get("zephyr_build") is not None
        and sources.get("zephyr_build") != sources.get("zephyr_source")
    ):
        lines.append(f"directory {sources['zephyr_build']}")
    return "\n".join(lines)


def default_rootfs(root: Path) -> Path:
    probe = (
        root
        / "build/qbox-fvp-rd-aspen/"
        "rse-t019da-bootargs-console-probe-20260524-v1/rootfs-console-probe.wic"
    )
    if probe.exists():
        return probe
    return (
        root
        / "build/tmp_baremetal/deploy/images/fvp-rd-aspen/"
        "baremetal-image-fvp-rd-aspen.wic"
    )


def write_text(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(data).lstrip(), encoding="utf-8")


def gdb_path(root: Path) -> str:
    native = (
        root
        / "build/tmp_baremetal/sysroots-components/x86_64/"
        "gcc-arm-none-eabi-native/usr/libexec/"
        "gcc-arm-none-eabi-13.3.rel1/bin/arm-none-eabi-gdb"
    )
    if native.exists():
        return str(native)
    return "gdb-multiarch"


def arm_readelf_path(root: Path) -> str:
    gdb = Path(gdb_path(root))
    readelf = gdb.with_name("arm-none-eabi-readelf")
    if readelf.exists():
        return str(readelf)
    return "readelf"


def arm_objdump_path(root: Path) -> str:
    gdb = Path(gdb_path(root))
    objdump = gdb.with_name("arm-none-eabi-objdump")
    if objdump.exists():
        return str(objdump)
    return "objdump"


def elf_function_disassembly(root: Path, elf: Path | None, function: str) -> list[str]:
    if elf is None:
        return []
    try:
        result = subprocess.run(
            [arm_objdump_path(root), "-d", "--line-numbers", str(elf)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:
        return []
    function_header = re.compile(rf"^[0-9a-fA-F]+ <{re.escape(function)}>:$")
    next_header = re.compile(r"^[0-9a-fA-F]+ <[^>]+>:$")
    lines: list[str] = []
    in_function = False
    for line in result.stdout.splitlines():
        if function_header.match(line):
            in_function = True
            lines.append(line)
            continue
        if in_function and next_header.match(line):
            break
        if in_function:
            lines.append(line)
    return lines


def instruction_address(line: str) -> str | None:
    match = re.match(r"\s*([0-9a-fA-F]+):", line)
    if not match:
        return None
    return "0x" + match.group(1)


def cbnz_r0_targets(lines: list[str], function: str) -> list[str]:
    pattern = re.compile(
        rf"\bcbnz\s+r0,\s*([0-9a-fA-F]+)\s+<{re.escape(function)}(?:\+[^>]*)?>"
    )
    targets: list[str] = []
    for line in lines:
        match = pattern.search(line)
        if match:
            address = "0x" + match.group(1)
            if address not in targets:
                targets.append(address)
    return targets


def cbz_r0_fallthroughs(lines: list[str]) -> list[str]:
    fallthroughs: list[str] = []
    for index, line in enumerate(lines):
        if not re.search(r"\bcbz\s+r0,", line):
            continue
        for next_line in lines[index + 1 :]:
            addr = instruction_address(next_line)
            if addr is not None:
                fallthroughs.append(addr)
                break
    return fallthroughs


def conditional_branch_targets(
    lines: list[str], function: str, mnemonics: list[str]
) -> list[str]:
    mnemonic_re = "|".join(re.escape(mnemonic) for mnemonic in mnemonics)
    pattern = re.compile(
        rf"\b(?:{mnemonic_re})(?:\.\w+)?\s+([0-9a-fA-F]+)\s+"
        rf"<{re.escape(function)}(?:\+[^>]*)?>"
    )
    targets: list[str] = []
    for line in lines:
        match = pattern.search(line)
        if match:
            address = "0x" + match.group(1)
            if address not in targets:
                targets.append(address)
    return targets


def first_instruction_matching(lines: list[str], pattern: str) -> str | None:
    regex = re.compile(pattern)
    for line in lines:
        if regex.search(line):
            return instruction_address(line)
    return None


def call_fallthroughs(lines: list[str], callee: str) -> list[str]:
    fallthroughs: list[str] = []
    call_re = re.compile(rf"\bbl(?:x)?\b.*<{re.escape(callee)}>")
    for index, line in enumerate(lines):
        if not call_re.search(line):
            continue
        for next_line in lines[index + 1 :]:
            addr = instruction_address(next_line)
            if addr is not None:
                fallthroughs.append(addr)
                break
    return fallthroughs


def elf_section_address(root: Path, elf: Path | None, section: str) -> str | None:
    if elf is None:
        return None
    try:
        result = subprocess.run(
            [arm_readelf_path(root), "-S", str(elf)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) >= 5 and fields[1] == section:
            return "0x" + fields[3]
        if len(fields) >= 6 and fields[2] == section:
            return "0x" + fields[4]
    return None


def qbox_source_setup(root: Path) -> str:
    qbox = root / "hsoc-stack/tools/qbox"
    qbox_platform = root / "hsoc-stack/tools/qbox-platform"
    paths = [
        qbox,
        qbox / "systemc-components",
        qbox / "qemu-components",
        qbox / "libqbox",
        qbox / "libqemu-cxx",
        qbox / "build",
        qbox_platform / "platforms/fvp-rd-aspen-rse",
        qbox_platform / "platforms/fvp-rd-aspen",
        qbox_platform / "systemc-components",
        qbox_platform / "qemu-components",
    ]
    lines = ["set debuginfod enabled off"]
    lines.extend(f"directory {path}" for path in paths if path.exists())
    return "\n".join(lines)


def write_gdb_scripts(
    root: Path,
    out_dir: Path,
    symbols: dict[str, Path | None],
    rse_port: int,
    ap_port: int,
    scp_port: int,
    scp_strategy: str,
    host_sample_seconds: int,
) -> dict[str, Path]:
    gdb_dir = out_dir / "gdb"
    probe_dir = out_dir / "probes"
    probe_dir.mkdir(parents=True, exist_ok=True)
    scripts: dict[str, Path] = {}
    sources = source_paths(root)
    tfm_source_setup = source_map_lines(sources, ["tfm"])
    linux_source_setup = source_map_lines(sources, ["linux"])
    scp_source_setup = source_map_lines(sources, ["scp"])
    zephyr_source_setup = source_map_lines(sources, ["zephyr"])
    tfa_source_setup = source_map_lines(sources, ["tfa"])
    optee_source_setup = source_map_lines(sources, ["optee"])
    uboot_source_setup = source_map_lines(sources, ["uboot"])
    host_source_setup = qbox_source_setup(root)
    ps_table_init_get_returns = call_fallthroughs(
        elf_function_disassembly(root, symbols.get("tfm_s"), "ps_object_table_init"),
        "psa_its_get",
    )
    ps_table_save_set_returns = call_fallthroughs(
        elf_function_disassembly(root, symbols.get("tfm_s"), "ps_object_table_save_table"),
        "psa_its_set",
    )
    its_file_info_meta_returns = call_fallthroughs(
        elf_function_disassembly(root, symbols.get("tfm_s"), "its_flash_fs_file_get_info"),
        "its_flash_fs_mblock_get_file_idx_meta",
    )
    its_file_write_lines = elf_function_disassembly(
        root, symbols.get("tfm_s"), "its_flash_fs_file_write"
    )
    its_file_write_meta_returns = call_fallthroughs(
        its_file_write_lines,
        "its_flash_fs_mblock_get_file_idx_meta",
    )
    its_file_write_finalize_returns = call_fallthroughs(
        its_file_write_lines,
        "its_flash_fs_mblock_meta_update_finalize",
    )
    ps_table_get_return_breaks = ""
    if len(ps_table_init_get_returns) >= 2:
        ps_table_get_return_breaks = f"""
            break *{ps_table_init_get_returns[0]}
            commands
              silent
              printf "TRACE ps_object_table_init table0 psa_its_get return status=0x%x signed=%d pc=0x%x lr=0x%x\\n", $r0, (int)$r0, $pc, $lr
              continue
            end
            break *{ps_table_init_get_returns[1]}
            commands
              silent
              printf "TRACE ps_object_table_init table1 psa_its_get return status=0x%x signed=%d pc=0x%x lr=0x%x\\n", $r0, (int)$r0, $pc, $lr
              continue
            end
        """
    ps_table_set_return_breaks = ""
    if ps_table_save_set_returns:
        ps_table_set_return_breaks = f"""
            break *{ps_table_save_set_returns[0]}
            commands
              silent
              printf "TRACE ps_object_table_save_table psa_its_set return status=0x%x signed=%d pc=0x%x lr=0x%x\\n", $r0, (int)$r0, $pc, $lr
              continue
            end
        """
    its_fs_return_breaks = ""
    if its_file_info_meta_returns:
        its_fs_return_breaks += f"""
            break *{its_file_info_meta_returns[0]}
            commands
              silent
              printf "TRACE its_flash_fs_file_get_info mblock_get_file_idx_meta return status=0x%x signed=%d pc=0x%x lr=0x%x\\n", $r0, (int)$r0, $pc, $lr
              continue
            end
        """
    if its_file_write_meta_returns:
        its_fs_return_breaks += f"""
            break *{its_file_write_meta_returns[0]}
            commands
              silent
              printf "TRACE its_flash_fs_file_write initial mblock_get_file_idx_meta return status=0x%x signed=%d pc=0x%x lr=0x%x\\n", $r0, (int)$r0, $pc, $lr
              continue
            end
        """
    if its_file_write_finalize_returns:
        its_fs_return_breaks += f"""
            break *{its_file_write_finalize_returns[0]}
            commands
              silent
              printf "TRACE its_flash_fs_file_write meta_update_finalize return status=0x%x signed=%d pc=0x%x lr=0x%x\\n", $r0, (int)$r0, $pc, $lr
              continue
            end
        """

    write_text(
        gdb_dir / "qbox-host.gdb",
        f"""
        set pagination off
        set confirm off
        set print thread-events off
        {host_source_setup}
        handle SIGPIPE nostop noprint pass
        handle SIGUSR1 nostop noprint pass
        set detach-on-fork on
        set follow-fork-mode parent
        info threads
        thread apply all bt 8
        detach
        quit
        """,
    )
    scripts["qbox_host"] = gdb_dir / "qbox-host.gdb"
    write_text(
        gdb_dir / "qbox-host-run.gdb",
        f"""
        set pagination off
        set confirm off
        set print thread-events off
        {host_source_setup}
        handle SIGPIPE nostop noprint pass
        handle SIGUSR1 nostop noprint pass
        set detach-on-fork on
        set follow-fork-mode parent
        set breakpoint pending on
        run
        thread apply all bt 8
        quit
        """,
    )
    scripts["qbox_host_run"] = gdb_dir / "qbox-host-run.gdb"
    write_text(
        gdb_dir / "qbox-host-sample.gdb",
        f"""
        set pagination off
        set confirm off
        set print thread-events off
        set mi-async on
        {host_source_setup}
        handle SIGPIPE nostop noprint pass
        handle SIGUSR1 nostop noprint pass
        set detach-on-fork on
        set follow-fork-mode parent
        set breakpoint pending on
        run
        info threads
        thread apply all bt 12
        kill
        quit
        """,
    )
    scripts["qbox_host_sample"] = gdb_dir / "qbox-host-sample.gdb"

    if symbols["tfm_bl1_1"] is not None:
        add_symbols: list[str] = []
        for key in ["tfm_bl1_2", "tfm_bl2"]:
            elf = symbols[key]
            text_addr = elf_section_address(root, elf, ".text")
            if elf is not None and text_addr is not None:
                add_symbols.append(f"add-symbol-file {elf} {text_addr}")
        write_text(
            gdb_dir / "tfm-rse-current.gdb",
            f"""
            set pagination off
            set confirm off
            set print pretty on
            {tfm_source_setup}
            file {symbols["tfm_bl1_1"]}
            {"\n".join(add_symbols)}
            target remote 127.0.0.1:{rse_port}
            info symbol $pc
            info registers pc sp lr r0 r1 r2 r3 r4 r5 r6 r7 r8 r9 r10 r11 r12
            info registers xpsr primask faultmask basepri control
            printf "TRACE fault-status-register read skipped; may fault in unprivileged TF-M partitions\\n"
            x/16wx $sp
            x/8i $pc
            bt
            detach
            quit
            """,
        )
        scripts["tfm_rse_current"] = gdb_dir / "tfm-rse-current.gdb"

    for key, name in [
        ("tfm_bl1_1", "tfm-bl1_1.gdb"),
        ("tfm_bl1_2", "tfm-bl1_2.gdb"),
        ("tfm_bl2", "tfm-bl2.gdb"),
        ("tfm_s", "tfm-s.gdb"),
    ]:
        elf = symbols[key]
        if elf is None:
            continue
        write_text(
            gdb_dir / name,
            f"""
            set pagination off
            set confirm off
            set print pretty on
            {tfm_source_setup}
            file {elf}
            target remote 127.0.0.1:{rse_port}
            info symbol $pc
            info registers pc sp lr r0 r1 r2 r3 r4 r5 r6 r7 r8 r9 r10 r11 r12
            info registers xpsr primask faultmask basepri control
            printf "TRACE fault-status-register read skipped; may fault in unprivileged TF-M partitions\\n"
            x/16wx $sp
            x/8i $pc
            bt
            detach
            quit
            """,
        )
        scripts[key] = gdb_dir / name

    tfm_source = sources.get("tfm_source")
    if symbols["tfm_s"] is not None and tfm_source is not None:
        tfm_core_lines = elf_function_disassembly(
            root, symbols["tfm_s"], "tfm_core_init"
        )
        platform_lines = elf_function_disassembly(
            root, symbols["tfm_s"], "tfm_hal_platform_init"
        )
        tfm_core_targets = cbnz_r0_targets(tfm_core_lines, "tfm_core_init")
        platform_targets = cbnz_r0_targets(
            platform_lines, "tfm_hal_platform_init"
        )
        platform_fallthroughs = cbz_r0_fallthroughs(platform_lines)

        def stop_breakpoint(address: str, message: str) -> str:
            return textwrap.dedent(
                f"""
                hbreak *{address}
                commands
                  silent
                  printf "{message} pc=0x%x\\n", $pc
                  dump_tfm_state
                  detach
                  quit
                end
                """
            ).strip()

        branch_breakpoints: list[str] = []
        for label, address in zip(
            [
                "FAIL tfm_core_init static-boundary branch",
                "FAIL tfm_core_init platform-init branch",
                "FAIL tfm_core_init otp-init branch",
                "FAIL tfm_core_init provisioning-query branch",
                "FAIL tfm_core_init provisioning-perform branch",
            ],
            tfm_core_targets,
        ):
            branch_breakpoints.append(stop_breakpoint(address, label))
        for label, address in zip(
            [
                "FAIL tfm_hal_platform_init clock-config branch",
                "FAIL tfm_hal_platform_init fault-handler branch",
                "FAIL tfm_hal_platform_init reset-config branch",
                "FAIL tfm_hal_platform_init debug-init branch",
                "FAIL tfm_hal_platform_init sam-init branch",
                "FAIL tfm_hal_platform_init nvic-target-state branch",
                "FAIL tfm_hal_platform_init nvic-enable branch",
            ],
            platform_targets,
        ):
            branch_breakpoints.append(stop_breakpoint(address, label))
        for label, address in zip(
            [
                "FAIL tfm_hal_platform_init atu-init branch",
                "FAIL tfm_hal_platform_init dma-init branch",
            ],
            platform_fallthroughs,
        ):
            branch_breakpoints.append(stop_breakpoint(address, label))

        common_return = first_instruction_matching(
            tfm_core_lines, r"\bmov\s+r0,\s*r4"
        )
        if common_return is not None:
            branch_breakpoints.append(
                textwrap.dedent(
                    f"""
                    hbreak *{common_return}
                    commands
                      silent
                      if $r4 == 0
                        printf "SUCCESS tfm_core_init common-return pc=0x%x\\n", $pc
                      else
                        printf "TRACE tfm_core_init common-return nonzero-r4=0x%x pc=0x%x\\n", $r4, $pc
                      end
                      dump_tfm_state
                      detach
                      quit
                    end
                    """
                ).strip()
            )

        write_text(
            gdb_dir / "tfm-core-init-trace.gdb",
            f"""
            set pagination off
            set confirm off
            set print pretty on
            set breakpoint pending on
            {tfm_source_setup}
            file {symbols["tfm_s"]}
            target remote 127.0.0.1:{rse_port}
            set $tfm_fwu_info_hits = 0
            set $tfm_fwu_info_component = 0
            set $tfm_fwu_info_query_state = 0
            set $tfm_fwu_info_query_impl = 0
            define dump_tfm_state
              info symbol $pc
              info registers pc sp lr r0 r1 r2 r3 r4 r5 r6 r7 r8 r9 r10 r11 r12
              info registers xpsr primask faultmask basepri control
              printf "TRACE fault-status-register read skipped; may fault in unprivileged TF-M partitions\\n"
              x/8i $pc
              bt
            end
            hbreak tfm_core_init
            commands
              silent
              printf "TRACE tfm_core_init entry pc=0x%x\\n", $pc
              dump_tfm_state
              continue
            end
            {"\n".join(branch_breakpoints)}
            hbreak tfm_hal_system_halt
            commands
              silent
              printf "TRACE tfm_hal_system_halt pc=0x%x\\n", $pc
              dump_tfm_state
              detach
              quit
            end
            continue
            """,
        )
        scripts["tfm_core_init_trace"] = gdb_dir / "tfm-core-init-trace.gdb"

        static_boundary_lines = elf_function_disassembly(
            root, symbols["tfm_s"], "tfm_hal_set_up_static_boundaries"
        )
        mpc_cfg_lines = elf_function_disassembly(
            root, symbols["tfm_s"], "mpc_init_cfg"
        )
        mpc_sie_lines = elf_function_disassembly(
            root, symbols["tfm_s"], "mpc_sie_init"
        )
        boundary_failure_targets = conditional_branch_targets(
            static_boundary_lines,
            "tfm_hal_set_up_static_boundaries",
            ["bne", "bls"],
        )
        mpc_failure_targets = cbnz_r0_targets(mpc_cfg_lines, "mpc_init_cfg")
        mpc_return = first_instruction_matching(
            mpc_cfg_lines, r"\bpop\s+\{r3,\s*pc\}"
        )
        static_boundary_success = first_instruction_matching(
            static_boundary_lines, r"\bmovs?\s+r0,\s*#0"
        )
        sie_unsupported_targets = conditional_branch_targets(
            mpc_sie_lines, "mpc_sie_init", ["bne"]
        )

        static_breakpoints: list[str] = []
        for label, address in zip(
            [
                "FAIL static-boundary mpc_init_cfg branch",
                "FAIL static-boundary ppc_init_cfg branch",
                "FAIL static-boundary mpu-region-count branch",
            ],
            boundary_failure_targets,
        ):
            static_breakpoints.append(stop_breakpoint(address, label))
        for label, address in zip(
            [
                "FAIL mpc_init_cfg Driver_VM0_MPC.Initialize branch",
                "FAIL mpc_init_cfg Driver_VM1_MPC.Initialize branch",
            ],
            mpc_failure_targets,
        ):
            static_breakpoints.append(stop_breakpoint(address, label))
        if len(mpc_failure_targets) > 2:
            for address in mpc_failure_targets[2:]:
                static_breakpoints.append(
                    textwrap.dedent(
                        f"""
                        hbreak *{address}
                        commands
                          silent
                          if $r0 == 0
                            printf "TRACE mpc_init_cfg shared-return success pc=0x%x\\n", $pc
                            dump_tfm_state
                            dump_mpc_regs
                            continue
                          else
                            printf "FAIL mpc_init_cfg shared-return nonzero-r0=0x%x pc=0x%x\\n", $r0, $pc
                            dump_tfm_state
                            dump_mpc_regs
                            detach
                            quit
                          end
                        end
                        """
                    ).strip()
                )
        if mpc_return is not None and mpc_return not in mpc_failure_targets:
            static_breakpoints.append(
                textwrap.dedent(
                    f"""
                    hbreak *{mpc_return}
                    commands
                      silent
                      if $r0 == 0
                        printf "TRACE mpc_init_cfg return success pc=0x%x\\n", $pc
                        dump_tfm_state
                        dump_mpc_regs
                        continue
                      else
                        printf "FAIL mpc_init_cfg return nonzero-r0=0x%x pc=0x%x\\n", $r0, $pc
                        dump_tfm_state
                        dump_mpc_regs
                        detach
                        quit
                      end
                    end
                    """
                ).strip()
            )
        for address in sie_unsupported_targets:
            static_breakpoints.append(
                textwrap.dedent(
                    f"""
                    hbreak *{address}
                    commands
                      silent
                      printf "FAIL mpc_sie_init unsupported-hardware-version version=0x%x pc=0x%x\\n", $r2, $pc
                      dump_tfm_state
                      dump_mpc_regs
                      detach
                      quit
                    end
                    """
                ).strip()
            )
        if static_boundary_success is not None:
            static_breakpoints.append(
                textwrap.dedent(
                    f"""
                    hbreak *{static_boundary_success}
                    commands
                      silent
                      printf "SUCCESS static-boundary return pc=0x%x\\n", $pc
                      dump_tfm_state
                      dump_mpc_regs
                      detach
                      quit
                    end
                    """
                ).strip()
            )

        write_text(
            gdb_dir / "tfm-static-boundary-trace.gdb",
            f"""
            set pagination off
            set confirm off
            set print pretty on
            set breakpoint pending on
            {tfm_source_setup}
            file {symbols["tfm_s"]}
            target remote 127.0.0.1:{rse_port}
            define dump_tfm_state
              info symbol $pc
              info registers pc sp lr r0 r1 r2 r3 r4 r5 r6 r7 r8 r9 r10 r11 r12
              info registers xpsr primask faultmask basepri control
              printf "TRACE fault-status-register read skipped; may fault in unprivileged TF-M partitions\\n"
              x/8i $pc
              bt
            end
            define dump_mpc_regs
              printf "TRACE MPC VM0 ctrl/blk/pidr snapshot\\n"
              x/wx 0x50083000
              x/wx 0x50083010
              x/wx 0x50083014
              x/wx 0x50083fe0
              printf "TRACE MPC VM1 ctrl/blk/pidr snapshot\\n"
              x/wx 0x50084000
              x/wx 0x50084010
              x/wx 0x50084014
              x/wx 0x50084fe0
            end
            hbreak tfm_hal_set_up_static_boundaries
            commands
              silent
              printf "TRACE tfm_hal_set_up_static_boundaries entry pc=0x%x\\n", $pc
              dump_tfm_state
              dump_mpc_regs
              continue
            end
            hbreak mpc_init_cfg
            commands
              silent
              printf "TRACE mpc_init_cfg entry pc=0x%x\\n", $pc
              dump_tfm_state
              dump_mpc_regs
              continue
            end
            hbreak mpc_sie_init
            commands
              silent
              printf "TRACE mpc_sie_init entry dev=0x%x pc=0x%x\\n", $r0, $pc
              dump_tfm_state
              dump_mpc_regs
              continue
            end
            {"\n".join(static_breakpoints)}
            continue
            """,
        )
        scripts["tfm_static_boundary_trace"] = (
            gdb_dir / "tfm-static-boundary-trace.gdb"
        )

        write_text(
            gdb_dir / "tfm-partition-panic-trace.gdb",
            f"""
            set pagination off
            set confirm off
            set print pretty on
            set breakpoint pending on
            {tfm_source_setup}
            file {symbols["tfm_s"]}
            target remote 127.0.0.1:{rse_port}
            set $tfm_fwu_info_hits = 0
            define dump_tfm_state
              info symbol $pc
              info symbol $lr
              info registers pc sp lr r0 r1 r2 r3 r4 r5 r6 r7 r8 r9 r10 r11 r12
              info registers xpsr primask faultmask basepri control
              printf "TRACE fault-status-register read skipped; may fault in unprivileged TF-M partitions\\n"
              x/24wx $sp
              x/8i $pc
              bt
            end
            define dump_partition_from_pointer
              set $part = (struct partition_t *)$arg0
              if $part == 0
                printf "TRACE current-partition addr=0x0\\n"
              else
                printf "TRACE current-partition addr=0x%x p_ldinf=0x%x boundary=0x%x allowed=0x%x waiting=0x%x asserted=0x%x\\n", (unsigned int)$part, (unsigned int)$part->p_ldinf, $part->boundary, $part->signals_allowed, $part->signals_waiting, $part->signals_asserted
                if $part->p_ldinf != 0
                  printf "TRACE current-load-info pid=0x%x flags=0x%x entry=0x%x stack_size=0x%x heap_size=0x%x deps=%u services=%u assets=%u irqs=%u load_order=0x%x\\n", $part->p_ldinf->pid, $part->p_ldinf->flags, $part->p_ldinf->entry, $part->p_ldinf->stack_size, $part->p_ldinf->heap_size, $part->p_ldinf->ndeps, $part->p_ldinf->nservices, $part->p_ldinf->nassets, $part->p_ldinf->nirqs, $part->p_ldinf->load_order
                end
              end
            end
            define dump_current_partition
              printf "TRACE pid-map 0x100=TFM_SP_PS 0x101=TFM_SP_ITS 0x103=TFM_SP_CRYPTO 0x104=TFM_SP_PLATFORM 0x105=TFM_SP_INITIAL_ATTESTATION 0x107=TFM_SP_FWU 0x113=TFM_SP_MEASURED_BOOT 0x117=SCMI_COMMS_PARTITION\\n"
              printf "TRACE p_curr_thrd=0x%x\\n", (unsigned int)p_curr_thrd
              if p_curr_thrd != 0
                p/x *p_curr_thrd
                set $part_from_thrd = (struct partition_t *)((uintptr_t)p_curr_thrd - 40)
                printf "TRACE partition-from-thread-field\\n"
                dump_partition_from_pointer $part_from_thrd
                if p_curr_thrd->p_context_ctrl != 0
                  set $part_from_ctx = (struct partition_t *)((uintptr_t)p_curr_thrd->p_context_ctrl - 24)
                  printf "TRACE partition-from-context-field\\n"
                  dump_partition_from_pointer $part_from_ctx
                end
              end
            end
            hbreak psa_panic
            commands
              silent
              printf "TRACE psa_panic entry pc=0x%x lr=0x%x\\n", $pc, $lr
              dump_tfm_state
              dump_current_partition
              detach
              quit
            end
            hbreak psa_panic_thread_fn_call
            commands
              silent
              printf "TRACE psa_panic_thread_fn_call entry pc=0x%x lr=0x%x\\n", $pc, $lr
              dump_tfm_state
              dump_current_partition
              detach
              quit
            end
            hbreak tfm_spm_partition_psa_panic
            commands
              silent
              printf "TRACE tfm_spm_partition_psa_panic entry pc=0x%x lr=0x%x\\n", $pc, $lr
              dump_tfm_state
              dump_current_partition
              detach
              quit
            end
            hbreak tfm_hal_system_halt
            commands
              silent
              printf "TRACE tfm_hal_system_halt pc=0x%x lr=0x%x\\n", $pc, $lr
              dump_tfm_state
              dump_current_partition
              detach
              quit
            end
            continue
            """,
        )
        scripts["tfm_partition_panic_trace"] = (
            gdb_dir / "tfm-partition-panic-trace.gdb"
        )

        write_text(
            gdb_dir / "tfm-ns-mailbox-trace.gdb",
            f"""
            set pagination off
            set confirm off
            set print pretty on
            set breakpoint pending on
            {tfm_source_setup}
            file {symbols["tfm_s"]}
            target remote 127.0.0.1:{rse_port}
            define dump_tfm_regs
              info symbol $pc
              info symbol $lr
              info registers pc sp lr r0 r1 r2 r3 r4 r5 r6 r7 r8 r9 r10 r11 r12
              info registers xpsr primask faultmask basepri control msp psp
              x/8i $pc
              bt
            end
            define dump_fault_frame
              printf "TRACE fault-status CFSR/BFAR/HFSR/SHCSR\\n"
              x/wx 0xe000ed28
              x/wx 0xe000ed38
              x/wx 0xe000ed2c
              x/wx 0xe000ed24
              set $exc_return = $lr
              set $frame = $msp
              if ($exc_return & 4)
                set $frame = $psp
              end
              printf "TRACE exception-frame exc_return=0x%x frame=0x%x\\n", $exc_return, $frame
              x/8wx $frame
              set $stacked_r0 = *(uint32_t *)$frame
              set $stacked_r1 = *(uint32_t *)($frame + 4)
              set $stacked_r2 = *(uint32_t *)($frame + 8)
              set $stacked_r3 = *(uint32_t *)($frame + 12)
              set $stacked_r12 = *(uint32_t *)($frame + 16)
              set $stacked_lr = *(uint32_t *)($frame + 20)
              set $stacked_pc = *(uint32_t *)($frame + 24)
              set $stacked_xpsr = *(uint32_t *)($frame + 28)
              printf "TRACE stacked r0=0x%x r1=0x%x r2=0x%x r3=0x%x r12=0x%x lr=0x%x pc=0x%x xpsr=0x%x\\n", $stacked_r0, $stacked_r1, $stacked_r2, $stacked_r3, $stacked_r12, $stacked_lr, $stacked_pc, $stacked_xpsr
              info symbol $stacked_pc
              x/10i $stacked_pc - 12
            end
            hbreak ns_agent_mailbox_entry
            commands
              silent
              printf "TRACE ns_agent_mailbox_entry pc=0x%x lr=0x%x\\n", $pc, $lr
              dump_tfm_regs
              continue
            end
            hbreak tfm_inter_core_comm_init
            commands
              silent
              printf "TRACE tfm_inter_core_comm_init pc=0x%x lr=0x%x\\n", $pc, $lr
              dump_tfm_regs
              continue
            end
            hbreak tfm_multi_core_hal_init
            commands
              silent
              printf "TRACE tfm_multi_core_hal_init pc=0x%x lr=0x%x\\n", $pc, $lr
              dump_tfm_regs
              continue
            end
            hbreak sfcp_init
            commands
              silent
              printf "TRACE sfcp_init pc=0x%x lr=0x%x\\n", $pc, $lr
              dump_tfm_regs
              continue
            end
            hbreak sfcp_register_msg_handler
            commands
              silent
              printf "TRACE sfcp_register_msg_handler pc=0x%x lr=0x%x\\n", $pc, $lr
              dump_tfm_regs
              continue
            end
            hbreak mailbox_enable_interrupts
            commands
              silent
              printf "TRACE mailbox_enable_interrupts pc=0x%x lr=0x%x\\n", $pc, $lr
              dump_tfm_regs
              continue
            end
            hbreak psa_irq_enable
            commands
              silent
              printf "TRACE psa_irq_enable signal=0x%x pc=0x%x lr=0x%x\\n", $r0, $pc, $lr
              dump_tfm_regs
              continue
            end
            hbreak psa_wait
            commands
              silent
              printf "TRACE psa_wait mask=0x%x timeout=0x%x pc=0x%x lr=0x%x\\n", $r0, $r1, $pc, $lr
              dump_tfm_regs
              continue
            end
            hbreak BusFault_Handler
            commands
              silent
              printf "TRACE BusFault_Handler pc=0x%x lr=0x%x\\n", $pc, $lr
              dump_tfm_regs
              dump_fault_frame
              detach
              quit
            end
            hbreak HardFault_Handler
            commands
              silent
              printf "TRACE HardFault_Handler pc=0x%x lr=0x%x\\n", $pc, $lr
              dump_tfm_regs
              dump_fault_frame
              detach
              quit
            end
            hbreak MemManage_Handler
            commands
              silent
              printf "TRACE MemManage_Handler pc=0x%x lr=0x%x\\n", $pc, $lr
              dump_tfm_regs
              dump_fault_frame
              detach
              quit
            end
            continue
            """,
        )
        scripts["tfm_ns_mailbox_trace"] = (
            gdb_dir / "tfm-ns-mailbox-trace.gdb"
        )

        write_text(
            gdb_dir / "tfm-its-init-trace.gdb",
            f"""
            set pagination off
            set confirm off
            set print pretty on
            set breakpoint pending on
            {tfm_source_setup}
            file {symbols["tfm_s"]}
            target remote 127.0.0.1:{rse_port}
            define dump_tfm_state
              info symbol $pc
              info symbol $lr
              info registers pc sp lr r0 r1 r2 r3 r4 r5 r6 r7 r8 r9 r10 r11 r12
              info registers xpsr primask faultmask basepri control
              printf "TRACE fault-status-register read skipped; may fault in unprivileged TF-M partitions\\n"
              x/16wx $sp
              x/8i $pc
              bt
            end
            hbreak psa_panic
            commands
              silent
              printf "TRACE psa_panic entry pc=0x%x lr=0x%x\\n", $pc, $lr
              dump_tfm_state
              detach
              quit
            end
            tbreak tfm_its_init
            continue
            printf "TRACE tfm_its_init stop pc=0x%x lr=0x%x\\n", $pc, $lr
            info line *$pc
            bt
            next
            printf "TRACE after init_its_fs_cfg r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            next
            printf "TRACE after ITS cfg status check r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            next
            printf "TRACE after its_flash_fs_init_ctx r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            next
            printf "TRACE after ITS init ctx status check r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            next
            printf "TRACE after first its_flash_fs_prepare r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            next
            printf "TRACE after ITS create-layout branch test r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            next
            printf "TRACE before/at its_flash_fs_wipe_all r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            next
            printf "TRACE after its_flash_fs_wipe_all r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            next
            printf "TRACE after ITS wipe status check r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            next
            printf "TRACE after second its_flash_fs_prepare r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            continue
            """,
        )
        scripts["tfm_its_init_trace"] = gdb_dir / "tfm-its-init-trace.gdb"

        write_text(
            gdb_dir / "tfm-ps-init-trace.gdb",
            f"""
            set pagination off
            set confirm off
            set print pretty on
            set breakpoint pending on
            {tfm_source_setup}
            file {symbols["tfm_s"]}
            target remote 127.0.0.1:{rse_port}
            define dump_tfm_state
              info symbol $pc
              info symbol $lr
              info registers pc sp lr r0 r1 r2 r3 r4 r5 r6 r7 r8 r9 r10 r11 r12
              info registers xpsr primask faultmask basepri control
              printf "TRACE fault-status-register read skipped; may fault in unprivileged TF-M partitions\\n"
              x/16wx $sp
              x/8i $pc
              bt
            end
            hbreak psa_panic
            commands
              silent
              printf "TRACE psa_panic entry pc=0x%x lr=0x%x\\n", $pc, $lr
              dump_tfm_state
              detach
              quit
            end
            tbreak tfm_ps_init
            continue
            printf "TRACE tfm_ps_init stop pc=0x%x lr=0x%x\\n", $pc, $lr
            info line *$pc
            bt
            next
            printf "TRACE tfm_ps_init step1 r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            next
            printf "TRACE tfm_ps_init step2 r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            next
            printf "TRACE tfm_ps_init step3 r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            next
            printf "TRACE tfm_ps_init step4 r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            next
            printf "TRACE tfm_ps_init step5 r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            next
            printf "TRACE tfm_ps_init step6 r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            next
            printf "TRACE tfm_ps_init step7 r0=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
            info line *$pc
            continue
            """,
        )
        scripts["tfm_ps_init_trace"] = gdb_dir / "tfm-ps-init-trace.gdb"

        write_text(
            gdb_dir / "tfm-ps-object-table-trace.gdb",
            f"""
            set pagination off
            set confirm off
            set print pretty on
            set breakpoint pending on
            {tfm_source_setup}
            file {symbols["tfm_s"]}
            target remote 127.0.0.1:{rse_port}
            set $ps_object_table_init_hits = 0
            define dump_tfm_state
              info symbol $pc
              info symbol $lr
              info registers pc sp lr r0 r1 r2 r3 r4 r5 r6 r7 r8 r9 r10 r11 r12
              info registers xpsr primask faultmask basepri control
              printf "TRACE fault-status-register read skipped; may fault in unprivileged TF-M partitions\\n"
              x/16wx $sp
              x/8i $pc
              bt
            end
            define dump_ps_init_ctx
              set $ctx = (struct ps_obj_table_init_ctx_t *)$arg0
              printf "TRACE ps-init-ctx addr=0x%x table0=0x%x table1=0x%x state0=%d state1=%d\\n", (unsigned int)$ctx, (unsigned int)$ctx->p_table[0], (unsigned int)$ctx->p_table[1], $ctx->table_state[0], $ctx->table_state[1]
              if $ctx->p_table[0] != 0
                printf "TRACE table0 first 96 bytes\\n"
                x/96bx $ctx->p_table[0]
                p/x *$ctx->p_table[0]
              end
              if $ctx->p_table[1] != 0
                printf "TRACE table1 first 96 bytes\\n"
                x/96bx $ctx->p_table[1]
                p/x *$ctx->p_table[1]
              end
            end
            break ps_object_table_init
            commands
              silent
              set $ps_object_table_init_hits = $ps_object_table_init_hits + 1
              printf "TRACE ps_object_table_init #%d entry obj_data=0x%x pc=0x%x lr=0x%x\\n", $ps_object_table_init_hits, $r0, $pc, $lr
              bt 5
              continue
            end
            {ps_table_get_return_breaks}
            break ps_set_active_object_table
            commands
              silent
              printf "TRACE ps_set_active_object_table entry init_ctx=0x%x pc=0x%x lr=0x%x\\n", $r0, $pc, $lr
              dump_ps_init_ctx $r0
              continue
            end
            break ps_object_table_create
            commands
              silent
              printf "TRACE ps_object_table_create entry pc=0x%x lr=0x%x\\n", $pc, $lr
              bt 5
              continue
            end
            break ps_object_table_save_table
            commands
              silent
              printf "TRACE ps_object_table_save_table entry obj_table=0x%x pc=0x%x lr=0x%x\\n", $r0, $pc, $lr
              x/96bx $r0
              continue
            end
            {ps_table_set_return_breaks}
            {its_fs_return_breaks}
            break its_flash_fs_file_get_info
            commands
              silent
              printf "TRACE its_flash_fs_file_get_info entry ctx=0x%x fid=0x%x info=0x%x pc=0x%x lr=0x%x\\n", $r0, $r1, $r2, $pc, $lr
              x/12bx $r1
              continue
            end
            break its_flash_fs_file_write
            commands
              silent
              printf "TRACE its_flash_fs_file_write entry ctx=0x%x fid=0x%x finfo=0x%x data_size=0x%x offset=0x%x data=0x%x pc=0x%x lr=0x%x\\n", $r0, $r1, $r2, $r3, *(unsigned int *)$sp, *(unsigned int *)($sp + 4), $pc, $lr
              x/12bx $r1
              p/x *(struct its_flash_fs_file_info_t *)$r2
              if *(unsigned int *)($sp + 4) != 0
                x/32bx *(unsigned int *)($sp + 4)
              end
              continue
            end
            break its_flash_fs_mblock_update_scratch_file_meta
            commands
              silent
              printf "TRACE its_flash_fs_mblock_update_scratch_file_meta ctx=0x%x idx=%u file_meta=0x%x pc=0x%x lr=0x%x\\n", $r0, $r1, $r2, $pc, $lr
              p/x *(struct its_file_meta_t *)$r2
              continue
            end
            break its_flash_fs_mblock_meta_update_finalize
            commands
              silent
              printf "TRACE its_flash_fs_mblock_meta_update_finalize ctx=0x%x pc=0x%x lr=0x%x\\n", $r0, $pc, $lr
              continue
            end
            set $tfm_flash_trace_hits = 0
            break Driver_FLASH0_ProgramData
            commands
              silent
              set $tfm_flash_trace_hits = $tfm_flash_trace_hits + 1
              if $tfm_flash_trace_hits <= 80
                printf "TRACE Driver_FLASH0_ProgramData addr=0x%x data=0x%x cnt=0x%x pc=0x%x lr=0x%x\\n", $r0, $r1, $r2, $pc, $lr
                x/32bx $r1
              end
              continue
            end
            break Driver_FLASH1_ProgramData
            commands
              silent
              set $tfm_flash_trace_hits = $tfm_flash_trace_hits + 1
              if $tfm_flash_trace_hits <= 80
                printf "TRACE Driver_FLASH1_ProgramData addr=0x%x data=0x%x cnt=0x%x pc=0x%x lr=0x%x\\n", $r0, $r1, $r2, $pc, $lr
                x/32bx $r1
              end
              continue
            end
            break Driver_FLASH0_EraseSector
            commands
              silent
              printf "TRACE Driver_FLASH0_EraseSector addr=0x%x pc=0x%x lr=0x%x\\n", $r0, $pc, $lr
              continue
            end
            break Driver_FLASH1_EraseSector
            commands
              silent
              printf "TRACE Driver_FLASH1_EraseSector addr=0x%x pc=0x%x lr=0x%x\\n", $r0, $pc, $lr
              continue
            end
            break ps_crypto_get_iv
            commands
              silent
              printf "TRACE ps_crypto_get_iv crypto=0x%x pc=0x%x lr=0x%x\\n", $r0, $pc, $lr
              x/32bx $r0
              continue
            end
            break ps_crypto_generate_auth_tag
            commands
              silent
              printf "TRACE ps_crypto_generate_auth_tag crypto=0x%x add=0x%x add_len=0x%x pc=0x%x lr=0x%x\\n", $r0, $r1, $r2, $pc, $lr
              x/32bx $r0
              x/32bx $r1
              continue
            end
            break ps_crypto_authenticate
            commands
              silent
              printf "TRACE ps_crypto_authenticate crypto=0x%x add=0x%x add_len=0x%x pc=0x%x lr=0x%x\\n", $r0, $r1, $r2, $pc, $lr
              x/32bx $r0
              x/32bx $r1
              continue
            end
            break ps_crypto_setkey
            commands
              silent
              printf "TRACE ps_crypto_setkey ps_key=0x%x label=0x%x label_len=0x%x pc=0x%x lr=0x%x\\n", $r0, $r1, $r2, $pc, $lr
              x/32bx $r1
              continue
            end
            break tfm_plat_get_huk
            commands
              silent
              printf "TRACE tfm_plat_get_huk buf=0x%x buf_len=0x%x pc=0x%x lr=0x%x\\n", $r1, $r2, $pc, $lr
              continue
            end
            break psa_key_derivation_input_key
            commands
              silent
              printf "TRACE psa_key_derivation_input_key op=0x%x step=0x%x key=0x%x pc=0x%x lr=0x%x\\n", $r0, $r1, $r2, $pc, $lr
              continue
            end
            break psa_key_derivation_output_key
            commands
              silent
              printf "TRACE psa_key_derivation_output_key attr=0x%x op=0x%x key=0x%x pc=0x%x lr=0x%x\\n", $r0, $r1, $r2, $pc, $lr
              continue
            end
            break psa_aead_encrypt
            commands
              silent
              printf "TRACE psa_aead_encrypt key=0x%x alg=0x%x nonce=0x%x nonce_len=0x%x pc=0x%x lr=0x%x\\n", $r0, $r1, $r2, $r3, $pc, $lr
              continue
            end
            break psa_aead_decrypt
            commands
              silent
              printf "TRACE psa_aead_decrypt key=0x%x alg=0x%x nonce=0x%x nonce_len=0x%x pc=0x%x lr=0x%x\\n", $r0, $r1, $r2, $r3, $pc, $lr
              continue
            end
            break psa_its_get
            commands
              silent
              printf "TRACE psa_its_get entry uid=0x%08x%08x offset=0x%x size=0x%x data=0x%x data_len_ptr=0x%x pc=0x%x lr=0x%x\\n", $r1, $r0, $r2, $r3, *(unsigned int *)$sp, *(unsigned int *)($sp + 4), $pc, $lr
              continue
            end
            break psa_its_set
            commands
              silent
              printf "TRACE psa_its_set entry uid=0x%08x%08x size=0x%x data=0x%x flags=0x%x pc=0x%x lr=0x%x\\n", $r1, $r0, $r2, $r3, *(unsigned int *)$sp, $pc, $lr
              x/96bx $r3
              continue
            end
            break psa_its_remove
            commands
              silent
              printf "TRACE psa_its_remove uid=0x%08x%08x pc=0x%x lr=0x%x\\n", $r1, $r0, $pc, $lr
              continue
            end
            hbreak psa_panic
            commands
              silent
              printf "TRACE psa_panic entry pc=0x%x lr=0x%x after ps-object-table trace\\n", $pc, $lr
              dump_tfm_state
              detach
              quit
            end
            continue
            """,
        )
        scripts["tfm_ps_object_table_trace"] = (
            gdb_dir / "tfm-ps-object-table-trace.gdb"
        )

        write_text(
            gdb_dir / "tfm-fwu-query-trace.gdb",
            f"""
            set pagination off
            set confirm off
            set print pretty on
            set breakpoint pending on
            set logging file {probe_dir / "tfm-fwu-query-trace-gdb.log"}
            set logging overwrite on
            set logging redirect off
            set logging enabled on
            set $tfm_fwu_info_hits = 0
            set $sfcp_pa_deser_hits = 0
            set $sfcp_atu_alloc_hits = 0
            {tfm_source_setup}
            file {symbols["tfm_s"]}
            target remote 127.0.0.1:{rse_port}
            define dump_tfm_state
              info symbol $pc
              info symbol $lr
              info registers pc sp lr r0 r1 r2 r3 r4 r5 r6 r7 r8 r9 r10 r11 r12
              info registers xpsr primask faultmask basepri control
              x/16wx $sp
              x/8i $pc
              bt
            end
            break fwu_bootloader_init
            commands
              silent
              printf "TRACE fwu_bootloader_init entry pc=0x%x lr=0x%x\\n", $pc, $lr
              continue
            end
            break fwu_bootloader_get_image_info
            commands
              silent
              set $tfm_fwu_info_hits = $tfm_fwu_info_hits + 1
              set $tfm_fwu_info_component = $r0
              set $tfm_fwu_info_query_state = $r1
              set $tfm_fwu_info_query_impl = $r2
              set $tfm_fwu_info_return = $lr & ~1
              printf "TRACE fwu_bootloader_get_image_info #%d entry component=%u query_state=%u query_impl_info=%u info=0x%x pc=0x%x lr=0x%x\\n", $tfm_fwu_info_hits, $r0, $r1, $r2, $r3, $pc, $lr
              tbreak *$tfm_fwu_info_return
              commands
                silent
                printf "TRACE fwu_bootloader_get_image_info return component=%u query_state=%u query_impl_info=%u status=0x%x signed=%d pc=0x%x\\n", $tfm_fwu_info_component, $tfm_fwu_info_query_state, $tfm_fwu_info_query_impl, $r0, (int)$r0, $pc
                if $r0 != 0
                  dump_tfm_state
                  detach
                  quit
                end
                continue
              end
              continue
            end
            break tfm_fwu_query
            commands
              silent
              set $tfm_fwu_query_return = $lr & ~1
              printf "TRACE tfm_fwu_query entry msg=0x%x pc=0x%x lr=0x%x\\n", $r0, $pc, $lr
              tbreak *$tfm_fwu_query_return
              commands
                silent
                printf "TRACE tfm_fwu_query return status=0x%x signed=%d pc=0x%x\\n", $r0, (int)$r0, $pc
                if $r0 != 0
                  dump_tfm_state
                  detach
                  quit
                end
                continue
              end
              continue
            end
            break sfcp_protocol_pointer_access_deserialize_msg
            commands
              silent
              set $sfcp_pa_deser_hits = $sfcp_pa_deser_hits + 1
              set $sfcp_pa_deser_return = $lr & ~1
              set $sfcp_pa_deser_req = $r0
              set $sfcp_pa_deser_msg = $r1
              set $sfcp_pa_deser_len = $r2
              printf "TRACE sfcp_pointer_access_deserialize_msg #%d entry req=0x%x msg=0x%x msg_len=0x%x pc=0x%x lr=0x%x\\n", $sfcp_pa_deser_hits, $r0, $r1, $r2, $pc, $lr
              printf "TRACE sfcp_pointer_access_msg words: "
              x/12wx $sfcp_pa_deser_msg
              tbreak *$sfcp_pa_deser_return
              commands
                silent
                printf "TRACE sfcp_pointer_access_deserialize_msg return req=0x%x msg=0x%x msg_len=0x%x status=0x%x signed=%d pc=0x%x\\n", $sfcp_pa_deser_req, $sfcp_pa_deser_msg, $sfcp_pa_deser_len, $r0, (int)$r0, $pc
                if $r0 != 0
                  dump_tfm_state
                  detach
                  quit
                end
                continue
              end
              continue
            end
            break comms_atu_alloc_region
            commands
              silent
              set $sfcp_atu_alloc_hits = $sfcp_atu_alloc_hits + 1
              set $sfcp_atu_alloc_return = $lr & ~1
              set $sfcp_atu_alloc_host = $r0
              set $sfcp_atu_alloc_size = $r2
              set $sfcp_atu_alloc_regionp = $r3
              printf "TRACE comms_atu_alloc_region #%d entry host=0x%08x%08x size=0x%x regionp=0x%x pc=0x%x lr=0x%x\\n", $sfcp_atu_alloc_hits, $r1, $r0, $r2, $r3, $pc, $lr
              tbreak *$sfcp_atu_alloc_return
              commands
                silent
                printf "TRACE comms_atu_alloc_region return host_low=0x%x size=0x%x status=0x%x signed=%d", $sfcp_atu_alloc_host, $sfcp_atu_alloc_size, $r0, (int)$r0
                if $sfcp_atu_alloc_regionp != 0
                  printf " region=%u", *(unsigned char *)$sfcp_atu_alloc_regionp
                end
                printf " pc=0x%x\\n", $pc
                if $r0 != 0
                  dump_tfm_state
                  detach
                  quit
                end
                continue
              end
              continue
            end
            hbreak psa_panic
            commands
              silent
              printf "TRACE psa_panic entry pc=0x%x lr=0x%x during fwu-query trace\\n", $pc, $lr
                dump_tfm_state
                detach
                quit
            end
            continue
            """,
        )
        scripts["tfm_fwu_query_trace"] = gdb_dir / "tfm-fwu-query-trace.gdb"

        write_text(
            gdb_dir / "tfm-fwu-start-trace.gdb",
            f"""
            set pagination off
            set confirm off
            set print pretty on
            set breakpoint pending on
            set logging file {probe_dir / "tfm-fwu-start-trace-gdb.log"}
            set logging overwrite on
            set logging redirect off
            set logging enabled on
            set $fwu_start_hits = 0
            set $fwu_trace_active = 0
            {tfm_source_setup}
            file {symbols["tfm_s"]}
            target remote 127.0.0.1:{rse_port}
            define dump_tfm_state
              info symbol $pc
              info symbol $lr
              info registers pc sp lr r0 r1 r2 r3 r4 r5 r6 r7 r8 r9 r10 r11 r12
              info registers xpsr primask faultmask basepri control
              x/16wx $sp
              x/8i $pc
              bt
            end
            define print_flash_area
              if $arg0 != 0
                printf " fa_id=%u fa_dev=%u fa_off=0x%x fa_size=0x%x", ((struct flash_area *)$arg0)->fa_id, ((struct flash_area *)$arg0)->fa_device_id, ((struct flash_area *)$arg0)->fa_off, ((struct flash_area *)$arg0)->fa_size
              end
            end
            break tfm_fwu_start
            commands
              silent
              set $fwu_trace_active = 1
              set $fwu_start_hits = $fwu_start_hits + 1
              set $fwu_start_return = $lr & ~1
              printf "TRACE tfm_fwu_start #%d entry msg=0x%x pc=0x%x lr=0x%x\\n", $fwu_start_hits, $r0, $pc, $lr
              tbreak *$fwu_start_return
              commands
                silent
                printf "TRACE tfm_fwu_start #%d return status=0x%x signed=%d pc=0x%x\\n", $fwu_start_hits, $r0, (int)$r0, $pc
                set $fwu_trace_active = 0
                if $r0 != 0
                  dump_tfm_state
                  detach
                  quit
                end
                continue
              end
              continue
            end
            break fwu_bootloader_get_image_info
            commands
              silent
              if $fwu_trace_active == 0
                continue
              end
              set $fwu_info_component = $r0
              set $fwu_info_query_state = $r1
              set $fwu_info_query_impl = $r2
              set $fwu_info_return = $lr & ~1
              printf "TRACE fwu_bootloader_get_image_info entry component=%u query_state=%u query_impl_info=%u info=0x%x pc=0x%x lr=0x%x\\n", $r0, $r1, $r2, $r3, $pc, $lr
              tbreak *$fwu_info_return
              commands
                silent
                printf "TRACE fwu_bootloader_get_image_info return component=%u status=0x%x signed=%d pc=0x%x\\n", $fwu_info_component, $r0, (int)$r0, $pc
                if $r0 != 0
                  dump_tfm_state
                  detach
                  quit
                end
                continue
              end
              continue
            end
            break fwu_bootloader_staging_area_init
            commands
              silent
              set $fwu_staging_component = $r0
              set $fwu_staging_manifest_size = $r2
              set $fwu_staging_return = $lr & ~1
              printf "TRACE fwu_bootloader_staging_area_init entry component=%u manifest=0x%x manifest_size=%u pc=0x%x lr=0x%x\\n", $r0, $r1, $r2, $pc, $lr
              tbreak *$fwu_staging_return
              commands
                silent
                printf "TRACE fwu_bootloader_staging_area_init return component=%u manifest_size=%u status=0x%x signed=%d pc=0x%x\\n", $fwu_staging_component, $fwu_staging_manifest_size, $r0, (int)$r0, $pc
                if $r0 != 0
                  dump_tfm_state
                  detach
                  quit
                end
                continue
              end
              continue
            end
            break flash_area_open
            commands
              silent
              if $fwu_trace_active == 0
                continue
              end
              set $fwu_flash_open_id = $r0
              set $fwu_flash_open_areap = $r1
              set $fwu_flash_open_return = $lr & ~1
              printf "TRACE flash_area_open entry id=%u area_ptr=0x%x pc=0x%x lr=0x%x\\n", $r0, $r1, $pc, $lr
              tbreak *$fwu_flash_open_return
              commands
                silent
                printf "TRACE flash_area_open return id=%u status=0x%x signed=%d", $fwu_flash_open_id, $r0, (int)$r0
                if $r0 == 0
                  set $fwu_open_fap = *(struct flash_area **)$fwu_flash_open_areap
                  print_flash_area $fwu_open_fap
                end
                printf " pc=0x%x\\n", $pc
                if $r0 != 0
                  dump_tfm_state
                  detach
                  quit
                end
                continue
              end
              continue
            end
            break flash_area_erase
            commands
              silent
              if $fwu_trace_active == 0
                continue
              end
              set $fwu_erase_fap = $r0
              set $fwu_erase_off = $r1
              set $fwu_erase_len = $r2
              set $fwu_erase_return = $lr & ~1
              printf "TRACE flash_area_erase entry off=0x%x len=0x%x", $r1, $r2
              print_flash_area $fwu_erase_fap
              printf " pc=0x%x lr=0x%x\\n", $pc, $lr
              tbreak *$fwu_erase_return
              commands
                silent
                printf "TRACE flash_area_erase return off=0x%x len=0x%x status=0x%x signed=%d", $fwu_erase_off, $fwu_erase_len, $r0, (int)$r0
                print_flash_area $fwu_erase_fap
                printf " pc=0x%x\\n", $pc
                if $r0 != 0
                  dump_tfm_state
                  detach
                  quit
                end
                continue
              end
              continue
            end
            break flash_area_write
            commands
              silent
              if $fwu_trace_active == 0
                continue
              end
              set $fwu_write_fap = $r0
              set $fwu_write_off = $r1
              set $fwu_write_len = $r3
              set $fwu_write_return = $lr & ~1
              printf "TRACE flash_area_write entry off=0x%x len=0x%x", $r1, $r3
              print_flash_area $fwu_write_fap
              printf " pc=0x%x lr=0x%x\\n", $pc, $lr
              tbreak *$fwu_write_return
              commands
                silent
                printf "TRACE flash_area_write return off=0x%x len=0x%x status=0x%x signed=%d", $fwu_write_off, $fwu_write_len, $r0, (int)$r0
                print_flash_area $fwu_write_fap
                printf " pc=0x%x\\n", $pc
                if $r0 != 0
                  dump_tfm_state
                  detach
                  quit
                end
                continue
              end
              continue
            end
            break Driver_FLASH0_EraseSector
            commands
              silent
              if $fwu_trace_active == 0
                continue
              end
              set $fwu_driver0_erase_addr = $r0
              set $fwu_driver0_erase_return = $lr & ~1
              printf "TRACE Driver_FLASH0_EraseSector entry addr=0x%x pc=0x%x lr=0x%x\\n", $r0, $pc, $lr
              tbreak *$fwu_driver0_erase_return
              commands
                silent
                printf "TRACE Driver_FLASH0_EraseSector return addr=0x%x status=0x%x signed=%d pc=0x%x\\n", $fwu_driver0_erase_addr, $r0, (int)$r0, $pc
                if $r0 != 0
                  dump_tfm_state
                  detach
                  quit
                end
                continue
              end
              continue
            end
            break Driver_FLASH1_EraseSector
            commands
              silent
              if $fwu_trace_active == 0
                continue
              end
              set $fwu_driver1_erase_addr = $r0
              set $fwu_driver1_erase_return = $lr & ~1
              printf "TRACE Driver_FLASH1_EraseSector entry addr=0x%x pc=0x%x lr=0x%x\\n", $r0, $pc, $lr
              tbreak *$fwu_driver1_erase_return
              commands
                silent
                printf "TRACE Driver_FLASH1_EraseSector return addr=0x%x status=0x%x signed=%d pc=0x%x\\n", $fwu_driver1_erase_addr, $r0, (int)$r0, $pc
                if $r0 != 0
                  dump_tfm_state
                  detach
                  quit
                end
                continue
              end
              continue
            end
            hbreak psa_panic
            commands
              silent
              printf "TRACE psa_panic entry pc=0x%x lr=0x%x during fwu-start trace\\n", $pc, $lr
              dump_tfm_state
              detach
              quit
            end
            continue
            """,
        )
        scripts["tfm_fwu_start_trace"] = gdb_dir / "tfm-fwu-start-trace.gdb"

    if symbols["linux_vmlinux"] is not None:
        write_text(
            gdb_dir / "linux-ap.gdb",
            f"""
            set pagination off
            set confirm off
            set print pretty on
            {linux_source_setup}
            file {symbols["linux_vmlinux"]}
            target remote 127.0.0.1:{ap_port}
            info symbol $pc
            info registers pc sp x0 x1 x2 x3 x29 x30
            info threads
            x/8i $pc
            bt
            thread apply all bt 4
            # Useful breakpoints after connecting interactively:
            # hbreak start_kernel
            # hbreak arm_si_rproc_probe
            # hbreak rproc_boot
            # hbreak arm_si_rproc_get_loaded_rsc_table
            detach
            quit
            """,
        )
        scripts["linux_ap"] = gdb_dir / "linux-ap.gdb"

    for key, name, setup in [
        ("tfa_bl31", "ap-tfa-bl31.gdb", tfa_source_setup),
        ("tfa_bl2", "ap-tfa-bl2.gdb", tfa_source_setup),
        ("optee_core", "ap-optee-core.gdb", optee_source_setup),
    ]:
        elf = symbols[key]
        if elf is None:
            continue
        write_text(
            gdb_dir / name,
            f"""
            set pagination off
            set confirm off
            set print pretty on
            {setup}
            file {elf}
            target remote 127.0.0.1:{ap_port}
            info symbol $pc
            info registers pc sp x0 x1 x2 x3 x18 x29 x30
            info threads
            x/8i $pc
            bt
            thread apply all bt 4
            detach
            quit
            """,
        )
        scripts[key] = gdb_dir / name

    if symbols["u_boot"] is not None:
        write_text(
            gdb_dir / "ap-u-boot.gdb",
            f"""
            set pagination off
            set confirm off
            set print pretty on
            {uboot_source_setup}
            file {symbols["u_boot"]}
            target remote 127.0.0.1:{ap_port}
            info symbol $pc
            info registers pc sp x0 x1 x2 x3 x18 x29 x30
            info threads
            x/8i $pc
            bt
            thread apply all bt 4
            # If the target is in relocated U-Boot, use x18/global-data
            # interactively to compute reloc_off and reload symbols at the
            # relocated .text base before setting breakpoints.
            detach
            quit
            """,
        )
        scripts["u_boot"] = gdb_dir / "ap-u-boot.gdb"

    if symbols["scp_firmware"] is not None:
        scp_live_target = ""
        if scp_strategy == "real-si-scp":
            scp_live_target = f"""
            target remote 127.0.0.1:{scp_port}
            info symbol $pc
            info registers pc sp lr r0 r1 r2 r3 r4 r5 r6 r7 r8 r9 r10 r11 r12
            info registers xpsr primask faultmask basepri control
            x/8i $pc
            bt
            detach
            """
        write_text(
            gdb_dir / "scp-firmware-symbols.gdb",
            f"""
            set pagination off
            set confirm off
            set print pretty on
            {scp_source_setup}
            file {symbols["scp_firmware"]}
            info files
            {scp_live_target}
            quit
            """,
        )
        scripts["scp_firmware"] = gdb_dir / "scp-firmware-symbols.gdb"

    if symbols["si_cl1_zephyr"] is not None:
        write_text(
            gdb_dir / "si-cl1-zephyr-symbols.gdb",
            f"""
            set pagination off
            set confirm off
            set print pretty on
            {zephyr_source_setup}
            file {symbols["si_cl1_zephyr"]}
            # The current QBox RSE path attaches SI CL1 through remoteproc,
            # but no SI CL1 CPU gdb_port is instantiated yet.
            info files
            quit
            """,
        )
        scripts["si_cl1_zephyr"] = gdb_dir / "si-cl1-zephyr-symbols.gdb"

    return scripts


def platform_params(rse_port: int, ap_port: int) -> list[str]:
    return [
        f"platform.rse_cpu_pass.cpu_0.gdb_port={rse_port}",
        f"platform.ap_cpu_0.gdb_port={ap_port}",
    ]


TS_SP_UUIDS = {
    "46bb39d1-b4d9-45b5-88ff-040027dab249": "ts_se_proxy",
    "ed32d533-99e6-4209-9cc0-2d72cdd998a7": "ts_smm_gateway",
}


def secure_partition_load_bases(secure_console: Path) -> dict[str, int]:
    if not secure_console.exists():
        return {}
    bases: dict[str, int] = {}
    pattern = re.compile(r"ELF \(([0-9a-fA-F-]+)\) at (0x[0-9a-fA-F]+)")
    for line in secure_console.read_text(
        encoding="utf-8", errors="replace"
    ).splitlines():
        match = pattern.search(line)
        if not match:
            continue
        key = TS_SP_UUIDS.get(match.group(1).lower())
        if key is not None:
            bases[key] = int(match.group(2), 16)
    return bases


def write_ap_secure_services_probe_script(
    root: Path,
    symbols: dict[str, Path | None],
    secure_console: Path,
    script: Path,
    ap_port: int,
) -> Path | None:
    bases = secure_partition_load_bases(secure_console)
    add_symbols: list[str] = []
    for key in ["ts_se_proxy", "ts_smm_gateway"]:
        elf = symbols.get(key)
        base = bases.get(key)
        text = elf_section_address(root, elf, ".text")
        if elf is None or base is None or text is None:
            continue
        add_symbols.append(
            f"add-symbol-file {elf} 0x{base + int(text, 16):x}"
        )
    if not add_symbols:
        return None

    setup = source_map_lines(source_paths(root), ["ts_se_proxy", "ts_smm_gateway"])
    write_text(
        script,
        f"""
        set pagination off
        set confirm off
        set print pretty on
        set architecture aarch64
        {setup}
        target remote 127.0.0.1:{ap_port}
        {"\n".join(add_symbols)}
        info symbol $pc
        info registers pc sp x0 x1 x2 x3 x18 x29 x30
        info threads
        x/8i $pc
        bt
        thread apply all bt 4
        detach
        quit
        """,
    )
    return script


def runner_command(root: Path, args: argparse.Namespace, run_dir: Path) -> list[str]:
    cmd = [
        "python3",
        str(root / "scripts/run/run_qbox_fvp_rd_aspen_rse.py"),
        "--skip-build",
        "--timeout",
        str(args.runner_timeout),
        "--scp-strategy",
        args.scp_strategy,
        "--out-dir",
        str(run_dir),
        "--rootfs",
        str(args.rootfs),
    ]
    if args.rse_flash is not None:
        cmd.extend(["--rse-flash", str(args.rse_flash)])
    if args.ap_flash is not None:
        cmd.extend(["--ap-flash", str(args.ap_flash)])
    if args.rse_otp is not None:
        cmd.extend(["--rse-otp", str(args.rse_otp)])
    if args.efi_capsule_disk is not None:
        cmd.extend(["--efi-capsule-disk", str(args.efi_capsule_disk)])
    if not args.copy_writable_flash:
        cmd.append("--no-copy-writable-flash")
    if args.keep_running_after_pass:
        cmd.append("--keep-running-after-pass")
    for param in platform_params(args.rse_port, args.ap_port):
        cmd.extend(["--platform-param", param])
    if args.ignore_fail_patterns:
        cmd.append("--ignore-fail-patterns")
    return cmd


def write_readme(
    root: Path,
    out_dir: Path,
    args: argparse.Namespace,
    scripts: dict[str, Path],
    symbols: dict[str, Path | None],
) -> None:
    gdb = gdb_path(root)
    run_dir = out_dir / "run"
    qbox_params = " ".join(f"--platform-param {p}" for p in platform_params(args.rse_port, args.ap_port))
    runner_options = ""
    if not args.copy_writable_flash:
        runner_options += "          --no-copy-writable-flash \\\n"
    if args.keep_running_after_pass:
        runner_options += "          --keep-running-after-pass \\\n"
    symbol_lines = "\n".join(
        f"- {name}: {rel(root, path) if path and path.exists() else 'missing'}"
        for name, path in symbols.items()
    )
    script_lines = "\n".join(
        f"- {name}: {rel(root, path)}" for name, path in sorted(scripts.items())
    )
    if args.scp_strategy == "service-model":
        scp_readme_note = (
            "SCP-Firmware note: this bundle uses "
            "`scp-strategy=service-model`, so there is no live SCP CPU GDB "
            "target. The SCP symbol script is still generated for "
            "source/symbol inspection."
        )
        scp_port_label = "SCP-Firmware placeholder"
    else:
        scp_readme_note = (
            "SCP-Firmware note: this bundle uses "
            f"`scp-strategy={args.scp_strategy}`. The generated SCP script "
            f"attempts `target remote 127.0.0.1:{args.scp_port}`, but that "
            "port is live only when the platform instantiates a real SCP CPU "
            "GDB server; check `scp_port_listening` in `progress-report.md`."
        )
        scp_port_label = "SCP-Firmware GDB candidate"
    if args.range_limited_flash_dmi:
        dmi_readme_note = (
            "Range-limited flash DMI note: this bundle enables ATU DMI, "
            "host-memory DMI, RSE boot-flash DMI for `0x7000:0x260000`, "
            "and AP flash DMI for `0x7000:0x240000`. Full-device "
            "boot-flash DMI remains unsafe for TF-M ITS initialization."
        )
    else:
        dmi_readme_note = (
            "Flash DMI note: this bundle keeps boot-flash DMI disabled by "
            "default. Use `--range-limited-flash-dmi` for the current "
            "storage-safe fast GDB path."
        )
    readme = textwrap.dedent(
        f"""
        # QBox RD-Aspen GDB Debug Bundle

        {dmi_readme_note}

        Run QBox with RSE and AP CPU GDB servers:

        ```bash
        {shell_env_block(run_dir, "        ", args.range_limited_flash_dmi, args.flash_stats, args.flash_stats_interval, args.mhu_trace, args.mhu_trace_limit)} \\
        python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \\
          --skip-build \\
          --timeout {args.runner_timeout} \\
          --scp-strategy {args.scp_strategy} \\
          --out-dir {run_dir} \\
          --rootfs {args.rootfs} \\
{runner_options}          {qbox_params}
        ```

        Run QBox itself under host GDB, which avoids Linux `ptrace_scope`
        attach restrictions and captures a short thread/backtrace sample:

        ```bash
        {shell_env_block(run_dir, "        ", args.range_limited_flash_dmi, args.flash_stats, args.flash_stats_interval, args.mhu_trace, args.mhu_trace_limit)} \\
        python3 scripts/run/run_qbox_fvp_rd_aspen_rse.py \\
          --skip-build \\
          --timeout {args.runner_timeout} \\
          --scp-strategy {args.scp_strategy} \\
          --out-dir {run_dir} \\
          --rootfs {args.rootfs} \\
{runner_options}          --host-gdb-script {scripts["qbox_host_sample"]} \\
          {qbox_params}
        ```

        Attach to TF-M/RSE:

        ```bash
        {gdb} -x {scripts.get("tfm_rse_current", out_dir / "gdb/tfm-rse-current.gdb")}
        # Image-specific symbol views, when needed:
        {gdb} -x {scripts.get("tfm_bl1_1", out_dir / "gdb/tfm-bl1_1.gdb")}
        {gdb} -x {scripts.get("tfm_bl2", out_dir / "gdb/tfm-bl2.gdb")}
        {gdb} -x {scripts.get("tfm_s", out_dir / "gdb/tfm-s.gdb")}
        # Branch trace for the current TF-M runtime panic:
        {gdb} -x {scripts.get("tfm_core_init_trace", out_dir / "gdb/tfm-core-init-trace.gdb")}
        # Lower-level trace for TF-M static-boundary/MPC setup:
        {gdb} -x {scripts.get("tfm_static_boundary_trace", out_dir / "gdb/tfm-static-boundary-trace.gdb")}
        # Partition-level trace for the post-core-init TF-M psa_panic path:
        {gdb} -x {scripts.get("tfm_partition_panic_trace", out_dir / "gdb/tfm-partition-panic-trace.gdb")}
        # ITS init trace for TF-M flash filesystem erase/program failures:
        {gdb} -x {scripts.get("tfm_its_init_trace", out_dir / "gdb/tfm-its-init-trace.gdb")}
        # PS init trace for TF-M protected-storage initialization failures:
        {gdb} -x {scripts.get("tfm_ps_init_trace", out_dir / "gdb/tfm-ps-init-trace.gdb")}
        # PS object-table/key trace for prepare/authentication failures:
        {gdb} -x {scripts.get("tfm_ps_object_table_trace", out_dir / "gdb/tfm-ps-object-table-trace.gdb")}
        # FWU query trace for SE-Proxy psa_fwu_query failures:
        {gdb} -x {scripts.get("tfm_fwu_query_trace", out_dir / "gdb/tfm-fwu-query-trace.gdb")}
        # FWU start/staging trace for capsule write-path failures:
        {gdb} -x {scripts.get("tfm_fwu_start_trace", out_dir / "gdb/tfm-fwu-start-trace.gdb")}
        ```

        Attach to AP firmware or Linux. The AP QEMU GDB target is opened
        through AP CPU0; use `info threads` inside GDB to inspect the visible
        AP CPU threads. Use the firmware scripts when the PC is still in TF-A,
        OP-TEE, or U-Boot, and the Linux script after the kernel has started:

        ```bash
        gdb-multiarch -x {scripts.get("tfa_bl31", out_dir / "gdb/ap-tfa-bl31.gdb")}
        gdb-multiarch -x {scripts.get("optee_core", out_dir / "gdb/ap-optee-core.gdb")}
        gdb-multiarch -x {scripts.get("u_boot", out_dir / "gdb/ap-u-boot.gdb")}
        gdb-multiarch -x {scripts.get("linux_ap", out_dir / "gdb/linux-ap.gdb")}
        ```

        Trusted Services secure partitions such as SE-Proxy and SMM Gateway are
        position-independent OP-TEE SP images. Their load bases are printed in
        `{run_dir / "qbox-secure-console.log"}` as `ELF (<uuid>) at <base>`.
        When `--launch` is used, this helper parses those bases and writes
        `probes/ap-secure-services-later.gdb` plus
        `probes/ap-secure-services-later.txt` for the sampled run.

        Inspect SCP-Firmware symbols/source:

        ```bash
        gdb-multiarch -x {scripts.get("scp_firmware", out_dir / "gdb/scp-firmware-symbols.gdb")}
        ```

        Inspect SI CL1 Zephyr symbols/source:

        ```bash
        gdb-multiarch -x {scripts.get("si_cl1_zephyr", out_dir / "gdb/si-cl1-zephyr-symbols.gdb")}
        ```

        Attach to QBox host process:

        ```bash
        gdb -p $(pgrep -n platforms-vp) -x {scripts["qbox_host"]}
        ```

        If that attach command reports `ptrace_scope`, use the host-GDB launch
        command above instead of changing system policy.

        For minimal perturbation when checking only the later progress point,
        regenerate this bundle with `--launch --sample-only --sample-delay N`.
        Add `--keep-running-after-pass` when the target should stay attachable
        after the normal pass condition.
        Add `--copy-writable-flash` when first-boot secure-storage or UEFI
        variable writeback behavior needs the same per-run writable flash
        copies as the normal runtime helper.

        {scp_readme_note}

        ## Ports

        - RSE/TF-M: {args.rse_port}
        - AP/Linux CPU0: {args.ap_port}
        - {scp_port_label}: {args.scp_port}

        ## Symbol Files
        """
    ).lstrip()
    readme += "\n" + symbol_lines + "\n"
    readme += textwrap.dedent(
        """

        ## GDB Scripts
        """
    )
    readme += "\n" + script_lines + "\n"
    (out_dir / "README.md").write_text(readme, encoding="utf-8")


def port_is_listening(port: int) -> bool:
    target = f"{port:04X}"
    for table in [Path("/proc/net/tcp"), Path("/proc/net/tcp6")]:
        try:
            lines = table.read_text(encoding="utf-8").splitlines()[1:]
        except FileNotFoundError:
            continue
        for line in lines:
            fields = line.split()
            if len(fields) < 4:
                continue
            local_addr = fields[1]
            state = fields[3]
            if state == "0A" and local_addr.rsplit(":", 1)[-1].upper() == target:
                return True
    return False


def wait_for_port(port: int, timeout_s: int) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if port_is_listening(port):
            return True
        time.sleep(0.2)
    return False


def child_pids(parent: int) -> list[int]:
    children: list[int] = []
    for proc_dir in Path("/proc").iterdir():
        if not proc_dir.name.isdigit():
            continue
        try:
            stat = (proc_dir / "stat").read_text(encoding="utf-8")
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
        close = stat.rfind(")")
        if close < 0:
            continue
        fields = stat[close + 2 :].split()
        if len(fields) >= 2 and int(fields[1]) == parent:
            children.append(int(proc_dir.name))
    return children


def cmdline(pid: int) -> str:
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return ""
    return raw.replace(b"\x00", b" ").decode("utf-8", errors="replace").strip()


def find_platform_pid(root_pid: int) -> int | None:
    pending = [root_pid]
    seen: set[int] = set()
    while pending:
        pid = pending.pop(0)
        if pid in seen:
            continue
        seen.add(pid)
        line = cmdline(pid)
        if "platforms-vp" in line:
            return pid
        pending.extend(child_pids(pid))
    return None


def run_probe(command: list[str], output: Path, timeout_s: int) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)

    def completed_output(data: str | bytes | None) -> str:
        if data is None:
            return ""
        if isinstance(data, bytes):
            return data.decode("utf-8", errors="replace")
        return data

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout_s,
            check=False,
        )
        output.write_text(
            "$ " + " ".join(command) + "\n"
            + f"exit_code={result.returncode}\n\n"
            + result.stdout,
            encoding="utf-8",
        )
        return result.returncode
    except subprocess.TimeoutExpired as exc:
        output.write_text(
            "$ " + " ".join(command) + "\n"
            + f"timed_out_after={timeout_s}s\n\n"
            + completed_output(exc.stdout),
            encoding="utf-8",
        )
        return 124


def qbox_probe_env(
    run_dir: Path,
    range_limited_flash_dmi: bool = False,
    flash_stats: bool = False,
    flash_stats_interval: int = 512,
    mhu_trace: bool = True,
    mhu_trace_limit: int = 2000,
) -> dict[str, str]:
    env = os.environ.copy()
    for key, value in qbox_probe_env_defaults(
        run_dir,
        range_limited_flash_dmi,
        flash_stats,
        flash_stats_interval,
        mhu_trace,
        mhu_trace_limit,
    ).items():
        env.setdefault(key, value)
    return env


def qbox_effective_probe_env(
    run_dir: Path,
    range_limited_flash_dmi: bool = False,
    flash_stats: bool = False,
    flash_stats_interval: int = 512,
    mhu_trace: bool = True,
    mhu_trace_limit: int = 2000,
) -> dict[str, str]:
    env = qbox_probe_env(
        run_dir,
        range_limited_flash_dmi,
        flash_stats,
        flash_stats_interval,
        mhu_trace,
        mhu_trace_limit,
    )
    return {
        key: env[key]
        for key in sorted(
            qbox_probe_env_defaults(
                run_dir,
                range_limited_flash_dmi,
                flash_stats,
                flash_stats_interval,
                mhu_trace,
                mhu_trace_limit,
            )
        )
        if key in env
    }


def terminate_process(proc: subprocess.Popen[object]) -> None:
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


def terminate_process_group(pid: int) -> None:
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if not Path(f"/proc/{pid}").exists():
            return
        time.sleep(0.1)
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        return


def descendant_pids(parent: int) -> list[int]:
    pending = [parent]
    seen: set[int] = set()
    result: list[int] = []
    while pending:
        pid = pending.pop(0)
        if pid in seen:
            continue
        seen.add(pid)
        children = child_pids(pid)
        result.extend(children)
        pending.extend(children)
    return result


def find_gdb_child(root_pid: int, script: Path) -> int | None:
    script_name = str(script)
    for pid in descendant_pids(root_pid):
        line = cmdline(pid)
        if "gdb" in line and script_name in line:
            return pid
    return None


def run_host_gdb_sample(
    root: Path,
    args: argparse.Namespace,
    scripts: dict[str, Path],
    out_dir: Path,
) -> dict[str, object]:
    run_dir = out_dir / "host-gdb-run"
    cmd = runner_command(root, args, run_dir)
    cmd.extend(["--host-gdb-script", str(scripts["qbox_host_sample"])])
    probe_dir = out_dir / "probes"
    probe_dir.mkdir(parents=True, exist_ok=True)
    wrapper_log = probe_dir / "qbox-host-launch.txt"
    with wrapper_log.open("w", encoding="utf-8", errors="replace") as log:
        log.write("$ " + " ".join(cmd) + "\n")
        proc = subprocess.Popen(
            cmd,
            cwd=root,
            env=qbox_probe_env(
                run_dir,
                args.range_limited_flash_dmi,
                args.flash_stats,
                args.flash_stats_interval,
                args.mhu_trace,
                args.mhu_trace_limit,
            ),
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            text=True,
        )
        gdb_pid: int | None = None
        try:
            deadline = time.monotonic() + max(args.port_timeout, 5)
            while time.monotonic() < deadline:
                gdb_pid = find_gdb_child(proc.pid, scripts["qbox_host_sample"])
                if gdb_pid is not None:
                    break
                if proc.poll() is not None:
                    break
                time.sleep(0.2)
            if gdb_pid is not None:
                time.sleep(args.host_sample_seconds)
                try:
                    os.kill(gdb_pid, signal.SIGINT)
                    log.write(f"\nsent_sigint_to_gdb_pid={gdb_pid}\n")
                except ProcessLookupError:
                    log.write(f"\ngdb_pid_exited_before_sigint={gdb_pid}\n")
            else:
                log.write("\ngdb_child_not_found\n")
            rc = proc.wait(timeout=max(args.gdb_timeout + 20, 25))
        except subprocess.TimeoutExpired:
            terminate_process(proc)
            rc = 124
            log.write(f"\ntimed_out_after={max(args.gdb_timeout + 20, 25)}s\n")
    return {
        "host_gdb_sample_rc": rc,
        "host_gdb_sample_gdb_pid": gdb_pid,
        "host_gdb_sample_wrapper": str(wrapper_log),
        "host_gdb_sample_log": str(run_dir / PLATFORM_STDOUT_LOG),
        "host_gdb_sample_result": str(run_dir / "result.json"),
        "host_gdb_sample_backtrace_captured": host_gdb_backtrace_captured(
            run_dir / PLATFORM_STDOUT_LOG
        ),
    }


def wait_for_sample_point(
    args: argparse.Namespace,
    run_dir: Path,
) -> dict[str, object]:
    start = time.monotonic()
    deadline = time.monotonic() + args.sample_delay
    marker = args.sample_marker
    marker_log = args.sample_marker_log
    if marker_log is None and marker:
        marker_log = run_dir / "qbox-primary-console.log"

    while time.monotonic() < deadline:
        if marker and marker_log and marker_log.exists():
            data = marker_log.read_text(encoding="utf-8", errors="replace")
            if marker in data:
                if args.sample_marker_post_delay:
                    time.sleep(max(0, args.sample_marker_post_delay))
                return {
                    "sample_marker": marker,
                    "sample_marker_log": str(marker_log),
                    "sample_marker_found": True,
                    "sample_marker_post_delay": args.sample_marker_post_delay,
                    "sample_wait_seconds": round(time.monotonic() - start, 3),
                }
        if not marker:
            break
        time.sleep(0.5)

    if not marker:
        time.sleep(max(0, args.sample_delay))

    return {
        "sample_marker": marker,
        "sample_marker_log": str(marker_log) if marker_log else None,
        "sample_marker_found": False if marker else None,
        "sample_marker_post_delay": args.sample_marker_post_delay if marker else None,
        "sample_wait_seconds": round(time.monotonic() - start, 3),
    }


def launch_and_probe(
    root: Path,
    args: argparse.Namespace,
    scripts: dict[str, Path],
    out_dir: Path,
) -> dict[str, object]:
    run_dir = out_dir / "run"
    cmd = runner_command(root, args, run_dir)
    env = qbox_probe_env(
        run_dir,
        args.range_limited_flash_dmi,
        args.flash_stats,
        args.flash_stats_interval,
        args.mhu_trace,
        args.mhu_trace_limit,
    )
    wrapper_log = out_dir / "runner-wrapper.log"
    wrapper_log.parent.mkdir(parents=True, exist_ok=True)
    with wrapper_log.open("w", encoding="utf-8", errors="replace") as log:
        proc = subprocess.Popen(
            cmd,
            cwd=root,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            text=True,
        )

    probes: dict[str, object] = {
        "runner_pid": proc.pid,
        "runner_command": cmd,
        "wrapper_log": str(wrapper_log),
    }
    probe_dir = out_dir / "probes"
    gdb_multi = "gdb-multiarch"
    arm_gdb = gdb_path(root)
    platform_pid: int | None = None

    try:
        probes["rse_port_listening"] = wait_for_port(args.rse_port, args.port_timeout)
        platform_pid = find_platform_pid(proc.pid)
        probes["platform_pid"] = platform_pid
        if platform_pid is not None and not args.sample_only:
            probes["qbox_host_probe_rc"] = run_probe(
                ["gdb", "-batch", "-p", str(platform_pid), "-x", str(scripts["qbox_host"])],
                probe_dir / "qbox-host.txt",
                args.gdb_timeout,
            )
        tfm_probe_script = scripts.get("tfm_rse_current") or scripts.get("tfm_bl1_1")
        if (
            probes["rse_port_listening"]
            and tfm_probe_script is not None
            and not args.sample_only
        ):
            probes["tfm_initial_probe_rc"] = run_probe(
                [arm_gdb, "-batch", "-x", str(tfm_probe_script)],
                probe_dir / "tfm-initial.txt",
                args.gdb_timeout,
            )
        if (
            probes["rse_port_listening"]
            and args.tfm_core_init_trace
            and "tfm_core_init_trace" in scripts
        ):
            probes["tfm_core_init_trace_rc"] = run_probe(
                [arm_gdb, "-batch", "-x", str(scripts["tfm_core_init_trace"])],
                probe_dir / "tfm-core-init-trace.txt",
                args.trace_timeout,
            )
        if (
            probes["rse_port_listening"]
            and args.tfm_static_boundary_trace
            and "tfm_static_boundary_trace" in scripts
        ):
            probes["tfm_static_boundary_trace_rc"] = run_probe(
                [arm_gdb, "-batch", "-x", str(scripts["tfm_static_boundary_trace"])],
                probe_dir / "tfm-static-boundary-trace.txt",
                args.trace_timeout,
            )
        if (
            probes["rse_port_listening"]
            and args.tfm_partition_panic_trace
            and "tfm_partition_panic_trace" in scripts
        ):
            probes["tfm_partition_panic_trace_rc"] = run_probe(
                [arm_gdb, "-batch", "-x", str(scripts["tfm_partition_panic_trace"])],
                probe_dir / "tfm-partition-panic-trace.txt",
                args.trace_timeout,
            )
        if (
            probes["rse_port_listening"]
            and args.tfm_ns_mailbox_trace
            and "tfm_ns_mailbox_trace" in scripts
        ):
            probes["tfm_ns_mailbox_trace_rc"] = run_probe(
                [arm_gdb, "-batch", "-x", str(scripts["tfm_ns_mailbox_trace"])],
                probe_dir / "tfm-ns-mailbox-trace.txt",
                args.trace_timeout,
            )
        if (
            probes["rse_port_listening"]
            and args.tfm_its_init_trace
            and "tfm_its_init_trace" in scripts
        ):
            probes["tfm_its_init_trace_rc"] = run_probe(
                [arm_gdb, "-batch", "-x", str(scripts["tfm_its_init_trace"])],
                probe_dir / "tfm-its-init-trace.txt",
                args.trace_timeout,
            )
        if (
            probes["rse_port_listening"]
            and args.tfm_ps_init_trace
            and "tfm_ps_init_trace" in scripts
        ):
            probes["tfm_ps_init_trace_rc"] = run_probe(
                [arm_gdb, "-batch", "-x", str(scripts["tfm_ps_init_trace"])],
                probe_dir / "tfm-ps-init-trace.txt",
                args.trace_timeout,
            )
        if (
            probes["rse_port_listening"]
            and args.tfm_ps_object_table_trace
            and "tfm_ps_object_table_trace" in scripts
        ):
            probes["tfm_ps_object_table_trace_rc"] = run_probe(
                [arm_gdb, "-batch", "-x", str(scripts["tfm_ps_object_table_trace"])],
                probe_dir / "tfm-ps-object-table-trace.txt",
                args.trace_timeout,
            )
        if (
            probes["rse_port_listening"]
            and args.tfm_fwu_query_trace
            and "tfm_fwu_query_trace" in scripts
        ):
            probes["tfm_fwu_query_trace_rc"] = run_probe(
                [arm_gdb, "-batch", "-x", str(scripts["tfm_fwu_query_trace"])],
                probe_dir / "tfm-fwu-query-trace.txt",
                args.trace_timeout,
            )
        if (
            probes["rse_port_listening"]
            and args.tfm_fwu_start_trace
            and not args.trace_after_sample
            and "tfm_fwu_start_trace" in scripts
        ):
            probes["tfm_fwu_start_trace_rc"] = run_probe(
                [arm_gdb, "-batch", "-x", str(scripts["tfm_fwu_start_trace"])],
                probe_dir / "tfm-fwu-start-trace.txt",
                args.trace_timeout,
            )
        probes["ap_port_listening"] = wait_for_port(args.ap_port, args.port_timeout)
        if probes["ap_port_listening"] and "linux_ap" in scripts and not args.sample_only:
            probes["linux_initial_probe_rc"] = run_probe(
                [gdb_multi, "-batch", "-x", str(scripts["linux_ap"])],
                probe_dir / "linux-initial.txt",
                args.gdb_timeout,
            )
        probes["scp_port_listening"] = wait_for_port(
            args.scp_port,
            args.port_timeout if args.scp_strategy == "real-si-scp" else 1,
        )
        if "scp_firmware" in scripts:
            probes["scp_symbol_probe_rc"] = run_probe(
                [gdb_multi, "-batch", "-x", str(scripts["scp_firmware"])],
                probe_dir / "scp-symbols.txt",
                args.gdb_timeout,
            )
        if "si_cl1_zephyr" in scripts:
            probes["si_cl1_symbol_probe_rc"] = run_probe(
                [gdb_multi, "-batch", "-x", str(scripts["si_cl1_zephyr"])],
                probe_dir / "si-cl1-zephyr-symbols.txt",
                args.gdb_timeout,
            )
        probes.update(wait_for_sample_point(args, run_dir))
        if (
            wait_for_port(args.rse_port, 2)
            and args.tfm_fwu_start_trace
            and args.trace_after_sample
            and "tfm_fwu_start_trace" in scripts
        ):
            probes["tfm_fwu_start_trace_rc"] = run_probe(
                [arm_gdb, "-batch", "-x", str(scripts["tfm_fwu_start_trace"])],
                probe_dir / "tfm-fwu-start-trace.txt",
                args.trace_timeout,
            )
        if wait_for_port(args.rse_port, 2) and tfm_probe_script is not None:
            probes["tfm_later_probe_rc"] = run_probe(
                [arm_gdb, "-batch", "-x", str(tfm_probe_script)],
                probe_dir / "tfm-later.txt",
                args.gdb_timeout,
            )
        if wait_for_port(args.rse_port, 2) and "tfm_s" in scripts:
            probes["tfm_s_later_probe_rc"] = run_probe(
                [arm_gdb, "-batch", "-x", str(scripts["tfm_s"])],
                probe_dir / "tfm-s-later.txt",
                args.gdb_timeout,
            )
        if wait_for_port(args.ap_port, 2) and "linux_ap" in scripts:
            probes["linux_later_probe_rc"] = run_probe(
                [gdb_multi, "-batch", "-x", str(scripts["linux_ap"])],
                probe_dir / "linux-later.txt",
                args.gdb_timeout,
            )
        if wait_for_port(args.ap_port, 2):
            secure_sp_script = write_ap_secure_services_probe_script(
                root,
                symbol_paths(root),
                secure_console=run_dir / "qbox-secure-console.log",
                script=probe_dir / "ap-secure-services-later.gdb",
                ap_port=args.ap_port,
            )
            if secure_sp_script is not None:
                probes["ap_secure_services_later_probe_rc"] = run_probe(
                    [gdb_multi, "-batch", "-x", str(secure_sp_script)],
                    probe_dir / "ap-secure-services-later.txt",
                    args.gdb_timeout,
                )
        for key, output in [
            ("tfa_bl31", "ap-tfa-bl31-later.txt"),
            ("tfa_bl2", "ap-tfa-bl2-later.txt"),
            ("optee_core", "ap-optee-core-later.txt"),
            ("u_boot", "ap-u-boot-later.txt"),
        ]:
            if wait_for_port(args.ap_port, 2) and key in scripts:
                probes[f"{key}_later_probe_rc"] = run_probe(
                    [gdb_multi, "-batch", "-x", str(scripts[key])],
                    probe_dir / output,
                    args.gdb_timeout,
                )
    finally:
        if platform_pid is not None:
            terminate_process_group(platform_pid)
        terminate_process(proc)
        probes["runner_returncode"] = proc.returncode
    if args.host_sample:
        probes.update(run_host_gdb_sample(root, args, scripts, out_dir))
    return probes


def probe_excerpt(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    interesting: list[str] = []
    for line in lines:
        stripped = line.strip()
        if (
            stripped.startswith("exit_code=")
            or stripped.startswith("timed_out_after=")
            or stripped.startswith("TRACE ")
            or stripped.startswith("FAIL ")
            or stripped.startswith("SUCCESS ")
            or stripped.startswith("pc ")
            or stripped.startswith("sp ")
            or stripped.startswith("#0")
            or stripped.startswith("ptrace:")
            or stripped.startswith("Could not attach")
            or stripped.startswith("Symbols from ")
            or stripped.startswith("Entry point:")
            or " in section " in stripped
            or stripped.startswith("No symbol matches")
        ):
            interesting.append(stripped)
    return interesting[:8]


def host_gdb_excerpt(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    interesting: list[str] = []
    for line in lines:
        stripped = line.strip()
        if (
            stripped.startswith("Thread ")
            or stripped.startswith("#")
            or stripped.startswith("* ")
            or stripped.startswith("Program received")
            or stripped.startswith("[Inferior ")
            or "SC_START" in stripped
            or "sc_core::" in stripped
            or "gs::" in stripped
            or "QemuInstance" in stripped
        ):
            interesting.append(stripped)
    return interesting[:24]


def host_gdb_backtrace_captured(path: Path) -> bool:
    if not path.exists():
        return False
    data = path.read_text(encoding="utf-8", errors="replace")
    return (
        "received signal SIGINT, Interrupt" in data
        and "#0" in data
        and ("QemuCpu::" in data or "sc_core::sc_start" in data)
    )


def write_progress_report(
    root: Path,
    out_dir: Path,
    metadata: dict[str, object],
) -> None:
    probe = metadata.get("probe")
    probe_dir = out_dir / "probes"
    scp_strategy = metadata.get("scp_strategy")
    if scp_strategy == "service-model":
        scp_target_note = (
            "- SCP-Firmware: source/symbol mapping is available; "
            "`scp-strategy=service-model` does not instantiate a live SCP CPU "
            "GDB port."
        )
    else:
        scp_target_note = (
            f"- SCP-Firmware: generated for `scp-strategy={scp_strategy}`; "
            "the script includes a live `target remote` attempt, but "
            "`scp_port_listening` below is authoritative for whether a real "
            "SCP CPU GDB server was instantiated."
        )
    lines = [
        "# QBox RD-Aspen GDB Progress Report",
        "",
        "## Live debug targets",
        "",
        "- QBox host: use `gdb --args` through `gdb/qbox-host-run.gdb`, or attach with `gdb/qbox-host.gdb` when host ptrace policy allows it.",
        "- TF-M/RSE: live remote target on the configured RSE port.",
        "- AP firmware/Linux CPU0: live remote target on the configured AP port, with TF-A, OP-TEE, U-Boot, and Linux symbol scripts.",
        scp_target_note,
        "",
        "## Ports",
        "",
    ]
    ports = metadata.get("ports", {})
    if isinstance(ports, dict):
        for name, port in ports.items():
            lines.append(f"- {name}: {port}")

    lines.extend(["", "## Symbol files", ""])
    symbols = metadata.get("symbols", {})
    if isinstance(symbols, dict):
        for name, path in symbols.items():
            lines.append(f"- {name}: {path or 'missing'}")

    lines.extend(["", "## Source maps", ""])
    sources = metadata.get("source_paths", {})
    if isinstance(sources, dict):
        for name, path in sources.items():
            lines.append(f"- {name}: {path or 'missing'}")

    if isinstance(probe, dict):
        lines.extend(["", "## Probe result", ""])
        for key in [
            "rse_port_listening",
            "tfm_initial_probe_rc",
            "tfm_core_init_trace_rc",
            "tfm_static_boundary_trace_rc",
            "tfm_partition_panic_trace_rc",
            "tfm_ns_mailbox_trace_rc",
            "tfm_its_init_trace_rc",
            "tfm_ps_init_trace_rc",
            "tfm_ps_object_table_trace_rc",
            "tfm_fwu_query_trace_rc",
            "tfm_fwu_start_trace_rc",
            "tfm_later_probe_rc",
            "tfm_s_later_probe_rc",
            "sample_marker",
            "sample_marker_log",
            "sample_marker_found",
            "sample_marker_post_delay",
            "sample_wait_seconds",
            "ap_port_listening",
            "linux_initial_probe_rc",
            "linux_later_probe_rc",
            "ap_secure_services_later_probe_rc",
            "tfa_bl31_later_probe_rc",
            "tfa_bl2_later_probe_rc",
            "optee_core_later_probe_rc",
            "u_boot_later_probe_rc",
            "scp_port_listening",
            "scp_symbol_probe_rc",
            "si_cl1_symbol_probe_rc",
            "qbox_host_probe_rc",
            "host_gdb_sample_rc",
            "runner_returncode",
        ]:
            if key in probe:
                lines.append(f"- {key}: {probe[key]}")
        if "host_gdb_sample_log" in probe:
            lines.append(f"- host_gdb_sample_log: `{probe['host_gdb_sample_log']}`")
        if "host_gdb_sample_backtrace_captured" in probe:
            lines.append(
                f"- host_gdb_sample_backtrace_captured: {probe['host_gdb_sample_backtrace_captured']}"
            )

        lines.extend(["", "## Probe excerpts", ""])
        for name in [
            "tfm-initial.txt",
            "tfm-core-init-trace.txt",
            "tfm-static-boundary-trace.txt",
            "tfm-partition-panic-trace.txt",
            "tfm-ns-mailbox-trace.txt",
            "tfm-its-init-trace.txt",
            "tfm-ps-init-trace.txt",
            "tfm-ps-object-table-trace.txt",
            "tfm-fwu-query-trace.txt",
            "tfm-fwu-start-trace.txt",
            "tfm-later.txt",
            "tfm-s-later.txt",
            "linux-initial.txt",
            "linux-later.txt",
            "ap-secure-services-later.txt",
            "ap-tfa-bl31-later.txt",
            "ap-tfa-bl2-later.txt",
            "ap-optee-core-later.txt",
            "ap-u-boot-later.txt",
            "scp-symbols.txt",
            "si-cl1-zephyr-symbols.txt",
            "qbox-host.txt",
        ]:
            excerpt = probe_excerpt(probe_dir / name)
            if not excerpt:
                continue
            lines.append(f"### {name}")
            lines.extend(f"- `{line}`" for line in excerpt)
            lines.append("")
        host_log = probe.get("host_gdb_sample_log")
        if isinstance(host_log, str):
            excerpt = host_gdb_excerpt(Path(host_log))
            if excerpt:
                lines.append("### qbox-host-gdb-sample")
                lines.extend(f"- `{line}`" for line in excerpt)
                lines.append("")

    launch_env = metadata.get("launch_env")
    if isinstance(launch_env, dict):
        lines.extend(["", "## Launch environment", ""])
        for key in sorted(launch_env):
            lines.append(f"- {key}: `{launch_env[key]}`")
        lines.append("")

    readme = out_dir / "README.md"
    debug_env = out_dir / "debug-env.json"
    lines.extend(
        [
            "## Artifacts",
            "",
            f"- README: `{rel(root, readme)}`",
            f"- Metadata: `{rel(root, debug_env)}`",
            f"- GDB scripts: `{rel(root, out_dir / 'gdb')}`",
            f"- Probe logs: `{rel(root, probe_dir)}`",
            "",
        ]
    )
    (out_dir / "progress-report.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    parser = argparse.ArgumentParser(
        description="Prepare GDB scripts for QBox RD-Aspen RSE/AP/Linux debug."
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "build/qbox-fvp-rd-aspen" / f"gdb-debug-{timestamp()}",
    )
    parser.add_argument("--rootfs", type=Path, default=default_rootfs(root))
    parser.add_argument(
        "--rse-flash",
        type=Path,
        help="Pass-through RSE flash image for the QBox runner.",
    )
    parser.add_argument(
        "--ap-flash",
        type=Path,
        help="Pass-through AP flash image for the QBox runner.",
    )
    parser.add_argument(
        "--rse-otp",
        type=Path,
        help="Pass-through RSE OTP image for the QBox runner.",
    )
    parser.add_argument(
        "--efi-capsule-disk",
        type=Path,
        help="Pass-through capsule disk image for the QBox runner.",
    )
    parser.add_argument("--rse-port", type=int, default=12340)
    parser.add_argument("--ap-port", type=int, default=12341)
    parser.add_argument("--scp-port", type=int, default=12342)
    parser.add_argument(
        "--scp-strategy",
        choices=["service-model", "real-si-scp"],
        default="service-model",
        help="Pass-through runner SCP strategy. The current helper still treats SCP as symbol-only unless a live SCP CPU target is instantiated.",
    )
    parser.add_argument("--runner-timeout", type=int, default=45)
    parser.add_argument("--port-timeout", type=int, default=8)
    parser.add_argument("--gdb-timeout", type=int, default=8)
    parser.add_argument(
        "--trace-timeout",
        type=int,
        default=150,
        help="Timeout for long-running branch trace GDB scripts.",
    )
    parser.add_argument(
        "--trace-after-sample",
        action="store_true",
        help=(
            "Run selected long trace scripts after --sample-delay or "
            "--sample-marker instead of attaching before the sample point."
        ),
    )
    parser.add_argument("--sample-delay", type=int, default=8)
    parser.add_argument(
        "--sample-marker",
        help=(
            "When launching, wait up to --sample-delay seconds for this text "
            "to appear before running the later GDB probes."
        ),
    )
    parser.add_argument(
        "--sample-marker-log",
        type=Path,
        help=(
            "Log file to scan for --sample-marker. Defaults to the run "
            "directory's qbox-primary-console.log."
        ),
    )
    parser.add_argument(
        "--sample-marker-post-delay",
        type=int,
        default=0,
        help="After --sample-marker is found, wait this many seconds before later GDB probes.",
    )
    parser.add_argument("--host-sample-seconds", type=int, default=5)
    parser.add_argument(
        "--host-sample",
        action="store_true",
        help="After CPU probes, launch QBox under host GDB and capture a short thread/backtrace sample.",
    )
    parser.add_argument(
        "--sample-only",
        action="store_true",
        help="Wait for the sample delay before probing live targets, avoiding early GDB attach perturbation.",
    )
    parser.add_argument(
        "--keep-running-after-pass",
        action="store_true",
        help=(
            "Pass --keep-running-after-pass to keep QBox attachable after "
            "normal pass until this helper finishes its bounded GDB probes."
        ),
    )
    parser.add_argument(
        "--copy-writable-flash",
        action="store_true",
        help=(
            "Use per-run writable RSE/AP flash copies instead of the helper's "
            "default --no-copy-writable-flash mode."
        ),
    )
    parser.add_argument(
        "--range-limited-flash-dmi",
        action="store_true",
        help=(
            "Enable the storage-safe fast path used by current GDB probes: "
            "ATU DMI, host-memory DMI, RSE boot-flash DMI limited to "
            "0x7000:0x260000, and AP flash DMI limited to 0x7000:0x240000. "
            "The full-device boot-flash DMI path is intentionally avoided "
            "because it still breaks TF-M ITS initialization."
        ),
    )
    parser.add_argument(
        "--flash-stats",
        action="store_true",
        help=(
            "Enable periodic Strata flash statistics files in the launched "
            "QBox run directory for RSE boot flash and AP flash."
        ),
    )
    parser.add_argument(
        "--flash-stats-interval",
        type=int,
        default=512,
        help="Write Strata flash statistics every N target writes when --flash-stats is enabled.",
    )
    parser.add_argument(
        "--mhu-trace",
        dest="mhu_trace",
        action="store_true",
        default=True,
        help="Enable QBox MHU trace logging in launched debug runs.",
    )
    parser.add_argument(
        "--no-mhu-trace",
        dest="mhu_trace",
        action="store_false",
        help=(
            "Disable QBox MHU trace logging. This keeps marker-gated "
            "post-login samples closer to normal runner timing."
        ),
    )
    parser.add_argument(
        "--mhu-trace-limit",
        type=int,
        default=2000,
        help="Maximum MHU trace events requested from the QBox platform.",
    )
    parser.add_argument(
        "--ignore-fail-patterns",
        action="store_true",
        help=(
            "Pass --ignore-fail-patterns to the runner so firmware fatal logs "
            "remain live long enough for GDB probes."
        ),
    )
    parser.add_argument(
        "--tfm-core-init-trace",
        action="store_true",
        help=(
            "Run the TF-M runtime branch trace script to identify which "
            "tfm_core_init or tfm_hal_platform_init branch reaches panic."
        ),
    )
    parser.add_argument(
        "--tfm-static-boundary-trace",
        action="store_true",
        help=(
            "Run the TF-M static-boundary trace script to identify whether "
            "MPC, PPC, or MPU setup causes tfm_core_init failure."
        ),
    )
    parser.add_argument(
        "--tfm-partition-panic-trace",
        action="store_true",
        help=(
            "Run the TF-M partition panic trace script to identify which "
            "runtime partition calls psa_panic after core initialization."
        ),
    )
    parser.add_argument(
        "--tfm-ns-mailbox-trace",
        action="store_true",
        help=(
            "Run the TF-M NS mailbox trace script to capture the SFCP init "
            "path and stacked BusFault frame for ns_agent_mailbox_entry."
        ),
    )
    parser.add_argument(
        "--tfm-its-init-trace",
        action="store_true",
        help=(
            "Run the TF-M ITS init trace script to inspect flash filesystem "
            "erase/program return values before the ITS partition panic."
        ),
    )
    parser.add_argument(
        "--tfm-ps-init-trace",
        action="store_true",
        help=(
            "Run the TF-M PS init trace script to inspect protected-storage "
            "prepare/wipe return values before the PS partition panic."
        ),
    )
    parser.add_argument(
        "--tfm-ps-object-table-trace",
        action="store_true",
        help=(
            "Run the TF-M PS object-table trace script to inspect ITS table "
            "read/write, table state, authentication, and HUK/key derivation "
            "traffic before the PS prepare failure."
        ),
    )
    parser.add_argument(
        "--tfm-fwu-query-trace",
        action="store_true",
        help=(
            "Run the TF-M FWU query trace script to inspect fwu_bootloader_init, "
            "metadata reads, private metadata writeback, get_image_info, and "
            "tfm_fwu_query return status for SE-Proxy psa_fwu_query failures."
        ),
    )
    parser.add_argument(
        "--tfm-fwu-start-trace",
        action="store_true",
        help=(
            "Run the TF-M FWU start/staging trace script to inspect "
            "tfm_fwu_start, staging-area init, flash-area open/erase/write, "
            "and the first non-zero FWU write-path return status."
        ),
    )
    parser.add_argument(
        "--launch",
        action="store_true",
        help="Launch QBox with GDB ports and run short non-interactive probes.",
    )
    args = parser.parse_args()
    if args.flash_stats and args.flash_stats_interval <= 0:
        parser.error("--flash-stats-interval must be positive when --flash-stats is enabled")
    if args.mhu_trace_limit < 0:
        parser.error("--mhu-trace-limit must be non-negative")
    return args


def main() -> int:
    root = workspace_root()
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    symbols = symbol_paths(root)
    sources = source_paths(root)
    scripts = write_gdb_scripts(
        root,
        args.out_dir,
        symbols,
        args.rse_port,
        args.ap_port,
        args.scp_port,
        args.scp_strategy,
        args.host_sample_seconds,
    )
    write_readme(root, args.out_dir, args, scripts, symbols)
    metadata: dict[str, object] = {
        "out_dir": str(args.out_dir),
        "rootfs": str(args.rootfs),
        "rse_flash": str(args.rse_flash) if args.rse_flash else None,
        "ap_flash": str(args.ap_flash) if args.ap_flash else None,
        "rse_otp": str(args.rse_otp) if args.rse_otp else None,
        "efi_capsule_disk": (
            str(args.efi_capsule_disk) if args.efi_capsule_disk else None
        ),
        "ports": {
            "rse_tfm": args.rse_port,
            "ap_linux_cpu0": args.ap_port,
            "scp_placeholder": args.scp_port,
        },
        "scp_strategy": args.scp_strategy,
        "symbols": {key: rel(root, path) for key, path in symbols.items()},
        "source_paths": {key: rel(root, path) for key, path in sources.items()},
        "gdb_scripts": {key: rel(root, path) for key, path in scripts.items()},
        "runner_command": runner_command(root, args, args.out_dir / "run"),
        "launch_env": qbox_effective_probe_env(
            args.out_dir / "run",
            args.range_limited_flash_dmi,
            args.flash_stats,
            args.flash_stats_interval,
            args.mhu_trace,
            args.mhu_trace_limit,
        ),
        "launch_env_defaults": qbox_probe_env_defaults(
            args.out_dir / "run",
            args.range_limited_flash_dmi,
            args.flash_stats,
            args.flash_stats_interval,
            args.mhu_trace,
            args.mhu_trace_limit,
        ),
        "host_sample_seconds": args.host_sample_seconds,
        "sample_only": args.sample_only,
        "keep_running_after_pass": args.keep_running_after_pass,
        "copy_writable_flash": args.copy_writable_flash,
        "range_limited_flash_dmi": args.range_limited_flash_dmi,
        "mhu_trace": args.mhu_trace,
        "mhu_trace_limit": args.mhu_trace_limit,
        "tfm_core_init_trace": args.tfm_core_init_trace,
        "tfm_static_boundary_trace": args.tfm_static_boundary_trace,
        "tfm_partition_panic_trace": args.tfm_partition_panic_trace,
        "tfm_ns_mailbox_trace": args.tfm_ns_mailbox_trace,
        "tfm_its_init_trace": args.tfm_its_init_trace,
        "tfm_ps_init_trace": args.tfm_ps_init_trace,
        "tfm_ps_object_table_trace": args.tfm_ps_object_table_trace,
        "tfm_fwu_query_trace": args.tfm_fwu_query_trace,
        "tfm_fwu_start_trace": args.tfm_fwu_start_trace,
        "trace_after_sample": args.trace_after_sample,
        "trace_timeout": args.trace_timeout,
    }
    if args.launch:
        metadata["probe"] = launch_and_probe(root, args, scripts, args.out_dir)
    (args.out_dir / "debug-env.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_progress_report(root, args.out_dir, metadata)
    print(args.out_dir)
    print(args.out_dir / "README.md")
    print(args.out_dir / "debug-env.json")
    print(args.out_dir / "progress-report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
