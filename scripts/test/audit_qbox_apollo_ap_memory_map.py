#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any, Final


DESCRIPTION: Final = "Audit Apollo AP 9.1.1 memory-map coverage from QBox Lua objects."
DOC_REL_PATH: Final = "doc/arm_zena_css_dev_guide/09-programmers-model-for-zena-css.md"
PLAN_REL_PATH: Final = ".omo/plans/ap-ap-system-memory-map-qbox-gap.md"
T12_DOC_REL_PATHS: Final[tuple[str, ...]] = (
    "doc/apollo-qbox-hardware-ko.md",
    "doc/qbox-apollo-fvp-map-analysis.md",
    "doc/apollo-qbox-full-model/coverage-ledger.md",
)
FMU_CONFIG_REL_PATH: Final = (
    "hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/"
    "apollo-fvp/si0_ramfw/config_fmu.c"
)
SI0_MMAP_REL_PATH: Final = (
    "hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/"
    "apollo-fvp/si0_ramfw/include/si0_mmap.h"
)
EXPECTED_HIGH_DRAM_BASE: Final = 0x20000000000
EXPECTED_HIGH_DRAM_SIZE: Final = 0x80000000
AP_PROGRAMMER_MODEL_HIGH_DRAM_BASE: Final = 0x880000000
EXPECTED_HIGH_DRAM_DTS_CELLS: Final = "<0x200 0x00000000 0x0 0x80000000>"
AP_PROGRAMMER_MODEL_HIGH_DRAM_DTS_CELLS: Final = "<0x8 0x80000000 0x0 0x80000000>"
FINAL_REQUIRED_CLASSIFICATIONS: Final[set[str]] = {
    "covered",
    "partial_model",
    "explicit_placeholder",
}
AP_CL_NI710AE_FMUS: Final[tuple[str, ...]] = (
    "AP_CL0_NI710AE_FMU",
    "AP_CL1_NI710AE_FMU",
    "AP_CL2_NI710AE_FMU",
    "AP_CL3_NI710AE_FMU",
)
AP_FMU_SUBWINDOW_SIZE: Final = 0x100000
AP_FMU_MODELED_SIZE: Final = 0x50000
AP_FMU_QBOX_OBJECTS: Final[tuple[str, ...]] = (
    "ap_cl0_ni710ae_fmu",
    "ap_cl1_ni710ae_fmu",
    "ap_cl2_ni710ae_fmu",
    "ap_cl3_ni710ae_fmu",
)
AP_FMU_IMPLEMENTATION_PLAN: Final[tuple[dict[str, str | int], ...]] = (
    {
        "object": "ap_cl0_ni710ae_fmu",
        "firmware_name": "AP_CL0_NI710AE_FMU",
        "firmware_backing_base": 0xD0070000,
        "firmware_base_expression": "SI0_ATW6_NI710AE_CLUSTER0_BASE",
        "parent": "SI0_FMU_1",
        "parent_cr_index": 3,
        "parent_ncr_index": 1,
    },
    {
        "object": "ap_cl1_ni710ae_fmu",
        "firmware_name": "AP_CL1_NI710AE_FMU",
        "firmware_backing_base": 0xD0170000,
        "firmware_base_expression": "SI0_ATW7_NI710AE_CLUSTER1_BASE",
        "parent": "SI0_FMU_1",
        "parent_cr_index": 18,
        "parent_ncr_index": 16,
    },
    {
        "object": "ap_cl2_ni710ae_fmu",
        "firmware_name": "AP_CL2_NI710AE_FMU",
        "firmware_backing_base": 0xD0270000,
        "firmware_base_expression": "SI0_ATW8_NI710AE_CLUSTER2_BASE",
        "parent": "SI0_FMU_1",
        "parent_cr_index": 33,
        "parent_ncr_index": 31,
    },
    {
        "object": "ap_cl3_ni710ae_fmu",
        "firmware_name": "AP_CL3_NI710AE_FMU",
        "firmware_backing_base": 0xD0370000,
        "firmware_base_expression": "SI0_ATW9_NI710AE_CLUSTER3_BASE",
        "parent": "SI0_FMU_1",
        "parent_cr_index": 48,
        "parent_ncr_index": 46,
    },
)
T12_DOC_REQUIRED_CONCEPTS: Final[tuple[tuple[str, tuple[str, ...]], ...]] = (
    ("ap_programmer_model_high_dram_0x08_8000_0000", ("0x08_8000_0000", "0x880000000")),
    ("fvp_high_dram_bank1_0x200_0000_0000", ("0x200_0000_0000", "0x20000000000")),
    ("ap_sid", ("AP SID",)),
    ("rgic2lgic_messreg", ("RGIC2LGIC_MESSREG", "RGIC2LGIC")),
    ("app_subsystem_fmu", ("APP subsystem FMU",)),
    ("ap_secure_timer", ("AP secure timer",)),
    ("deferred", ("deferred",)),
    ("noc", ("NoC",)),
    ("cmn", ("CMN",)),
    ("pcie", ("PCIe",)),
    ("debug", ("debug",)),
    ("memory_controller", ("memory-controller",)),
)


@dataclass(frozen=True, slots=True)
class MapRow:
    name: str
    start: int
    size: int
    scope: str


@dataclass(frozen=True, slots=True)
class LuaSocket:
    lua_file: str
    object_name: str
    module_type: str
    socket_name: str
    address: int
    size: int


@dataclass(frozen=True, slots=True)
class ApViewBinding:
    lua_file: str
    object_name: str
    socket_name: str
    binding_kind: str


EXPECTED_ROWS: Final[tuple[MapRow, ...]] = (
    MapRow("Shared SRAM", 0x00000000, 0x08000000, "required_now"),
    MapRow("AP Memory Expansion 1", 0x08000000, 0x08000000, "deferred_epic"),
    MapRow("System NoC0 GPV", 0x10000000, 0x01000000, "deferred_epic"),
    MapRow("System NoC1 GPV", 0x11000000, 0x01000000, "deferred_epic"),
    MapRow("System NoC2 GPV", 0x12000000, 0x01000000, "deferred_epic"),
    MapRow("System NoC3 GPV", 0x13000000, 0x01000000, "deferred_epic"),
    MapRow("NS_UART", 0x1A400000, 0x00010000, "required_now"),
    MapRow("S_UART", 0x1A410000, 0x00010000, "required_now"),
    MapRow("AP0_NS_WDOG0 CONTROL", 0x1A420000, 0x00010000, "required_now"),
    MapRow("AP0_NS_WDOG0 REFRESH", 0x1A430000, 0x00010000, "required_now"),
    MapRow("AP0_S_WDOG CONTROL", 0x1A460000, 0x00010000, "required_now"),
    MapRow("AP0_S_WDOG REFRESH", 0x1A470000, 0x00010000, "required_now"),
    MapRow("SID", 0x1A4A0000, 0x00010000, "required_now"),
    MapRow("AP0_REFCLK_CNTCTL", 0x1A810000, 0x00010000, "required_now"),
    MapRow("AP0_REFCLK_S_CNTBase1", 0x1A820000, 0x00010000, "required_now"),
    MapRow("AP0_REFCLK_NS_CNTBase0", 0x1A830000, 0x00010000, "required_now"),
    MapRow("SCMI_SCMI_MHU_SND_S", 0x1AC00000, 0x00030000, "deferred_epic"),
    MapRow("SCMI_SCMI_MHU_RCV_S", 0x1AC30000, 0x00030000, "deferred_epic"),
    MapRow("RSE_RSE_MHU_SND_S", 0x1AE00000, 0x00030000, "deferred_epic"),
    MapRow("RSE_RSE_MHU_RCV_S", 0x1AE30000, 0x00030000, "deferred_epic"),
    MapRow("SI_SI_MHU_SND_S", 0x1BA00000, 0x00030000, "deferred_epic"),
    MapRow("SI_SI_MHU_RCV_S", 0x1BA30000, 0x00030000, "deferred_epic"),
    MapRow("FMU Region", 0x1D000000, 0x00F00000, "required_now"),
    MapRow("STM", 0x1E000000, 0x01000000, "deferred_epic"),
    MapRow("GIC", 0x20000000, 0x08000000, "required_now"),
    MapRow("AP Memory Expansion", 0x30000000, 0x10000000, "required_now"),
    MapRow("System Management Domain Access Region", 0x40000000, 0x10000000, "required_now"),
    MapRow("SMD AP_EXP_I_1 NoC config space", 0x50000000, 0x00010000, "deferred_epic"),
    MapRow("RGIC2LGIC_MESSREG", 0x5FFF0000, 0x00010000, "required_now"),
    MapRow("PCIe NI-710AE Memory space1", 0x60000000, 0x20000000, "deferred_epic"),
    MapRow("DRAM low", 0x80000000, 0x80000000, "required_now"),
    MapRow("CMN GPV", 0x100000000, 0x40000000, "deferred_epic"),
    MapRow("Cluster management domain memory map", 0x140000000, 0x40000000, "deferred_epic"),
    MapRow("Memory controller control memory map", 0x180000000, 0x40000000, "deferred_epic"),
    MapRow("SMMU+NI-710AE GPV + PCIe CTRL+PHY", 0x1C0000000, 0x60000000, "required_now"),
    MapRow("AP Memory Expansion 2", 0x600000000, 0x200000000, "deferred_epic"),
    MapRow("Debug Memory Map", 0x800000000, 0x080000000, "deferred_epic"),
    MapRow("DRAM high", 0x880000000, 0x580000000, "deferred_epic"),
)
FAIL_IF_MISSING: Final[set[str]] = {
    "SID",
    "AP0_REFCLK_S_CNTBase1",
    "FMU Region",
    "RGIC2LGIC_MESSREG",
    "DRAM high",
}
PARTIAL_MODEL_ROWS: Final[dict[str, str]] = {
    "Shared SRAM": "QBox models the AP-used shared SRAM subwindow, not the full reserved programmer-model span.",
    "GIC": "QBox models AP GIC distributor, ITS, and active redistributors as subwindows.",
    "AP Memory Expansion": "QBox models the current RoS virtio and RTC AP expansion subwindows.",
    "System Management Domain Access Region": "QBox models the AP ATU translation aperture used by the current full-system path.",
    "DRAM low": "QBox backs the current bootable low DRAM extent and leaves the top carveout unbacked.",
    "SMMU+NI-710AE GPV + PCIe CTRL+PHY": "QBox models the AP SMMU subwindow; NI-710AE GPV and PCIe CTRL/PHY remain deferred.",
    "DRAM high": "QBox backs the current FVP-compatible 2 GiB high DRAM bank at the multichip DRAM aperture base.",
}
WATCHED_OBJECTS: Final[set[str]] = {
    "host_ap_shared_sram",
    "host_ap_dram1", "host_ap_dram2", "ap_primary_uart", "ap_secure_uart",
    "ap_watchdog_0", "ap_secure_wdog", "ap_secure_wdog_refresh",
    "ap_timer_mem", "ap_gic", "ap_gic_its", "ap_smmu_0",
    "ap_virtioblk_0", "ap_virtioblk_1", "ap_virtioblk_2", "ap_virtioblk_3",
    "ap_virtionet_0", "ap_virtiorng_0", "ap_rtc_0", "host_ap_atu",
    "host_ap_si_ns_scmi_mhu_pbx", "host_ap_si_ns_scmi_mhu_mbx",
    "host_ap_si_scmi_mhu_pbx", "host_ap_si_scmi_mhu_mbx", "host_ap_si_cl1_mhu_pbx",
    "host_ap_si_cl1_mhu_mbx", "host_ap_si_pfdi_monitor_mhu_pbx", "host_ap_rse_mhu_pbx",
    "host_ap_rse_mhu_mbx", "ap_sid", "ap_secure_timer_frame", "ap_rgic2lgic_messreg",
    "ap_cl0_ni710ae_fmu", "ap_cl1_ni710ae_fmu", "ap_cl2_ni710ae_fmu",
    "ap_cl3_ni710ae_fmu", "ap_fmu_region",
}
EXPLICIT_PLACEHOLDERS: Final[dict[str, set[str]]] = {
    "AP0_S_WDOG CONTROL": {"ap_secure_wdog"},
    "AP0_S_WDOG REFRESH": {"ap_secure_wdog_refresh"},
    "AP0_REFCLK_S_CNTBase1": {"ap_secure_timer_frame"},
    "RGIC2LGIC_MESSREG": {"ap_rgic2lgic_messreg"},
}
REQUIRED_AP_VIEW_BINDINGS: Final[dict[str, tuple[tuple[str, str], ...]]] = {
    "NS_UART": (("ap_primary_uart", "target_socket"),),
    "S_UART": (("ap_secure_uart", "target_socket"),),
    "AP0_NS_WDOG0 CONTROL": (("ap_watchdog_0", "refresh_mem"),),
    "AP0_NS_WDOG0 REFRESH": (("ap_watchdog_0", "control_mem"),),
    "AP0_S_WDOG CONTROL": (("ap_secure_wdog", "target_socket"),),
    "AP0_S_WDOG REFRESH": (("ap_secure_wdog_refresh", "target_socket"),),
    "SID": (("ap_sid", "target_socket"),),
    "AP0_REFCLK_CNTCTL": (("ap_timer_mem", "mem"),),
    "AP0_REFCLK_S_CNTBase1": (("ap_secure_timer_frame", "target_socket"),),
    "AP0_REFCLK_NS_CNTBase0": (("ap_timer_mem", "mem_view"),),
    "FMU Region": (
        ("ap_cl0_ni710ae_fmu", "target_socket"),
        ("ap_cl1_ni710ae_fmu", "target_socket"),
        ("ap_cl2_ni710ae_fmu", "target_socket"),
        ("ap_cl3_ni710ae_fmu", "target_socket"),
    ),
    "GIC": (("ap_gic", "dist_iface"), ("ap_gic", "redist_iface_*"), ("ap_gic_its", "mem")),
    "AP Memory Expansion": (
        ("ap_virtioblk_0", "mem"),
        ("ap_virtioblk_1", "mem"),
        ("ap_virtioblk_2", "mem"),
        ("ap_virtioblk_3", "mem"),
        ("ap_virtionet_0", "mem"),
        ("ap_virtiorng_0", "mem"),
        ("ap_rtc_0", "mem"),
    ),
    "System Management Domain Access Region": (("host_ap_atu", "translation_socket"),),
    "RGIC2LGIC_MESSREG": (("ap_rgic2lgic_messreg", "target_socket"),),
    "DRAM low": (("host_ap_dram1", "target_socket"),),
    "SMMU+NI-710AE GPV + PCIe CTRL+PHY": (("ap_smmu_0", "mem"),),
    "DRAM high": (("host_ap_dram2", "target_socket"),),
}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_address(value: str) -> int:
    return int(value.replace("_", ""), 16)


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def normalize_lookup(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def clean_markdown_link(value: str) -> str:
    match = re.fullmatch(r"\[([^\]]+)\]\([^)]+\)", value.strip())
    return match.group(1) if match else value.strip()


def parse_doc_table(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    in_table = False
    for line_no, line in enumerate(read_text(root / DOC_REL_PATH).splitlines(), start=1):
        if line.startswith("| Start address | End address | Size | Name |"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("| --- "):
            continue
        if not line.startswith("|"):
            if rows:
                break
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6:
            continue
        name = clean_markdown_link(cells[3])
        if name == "Reserved":
            continue
        rows.append(
            {
                "line": line_no,
                "start": parse_address(cells[0]),
                "end": parse_address(cells[1]),
                "size_text": cells[2],
                "name": name,
                "description": clean_markdown_link(cells[4]),
                "access_control": cells[5],
            }
        )
    return rows


def doc_name_for(row: MapRow) -> str:
    if row.name in {"DRAM low", "DRAM high"}:
        return "DRAM"
    return row.name


def compare_fixture_to_doc(root: Path) -> list[str]:
    doc_rows = parse_doc_table(root)
    mismatches: list[str] = []
    if len(doc_rows) != len(EXPECTED_ROWS):
        mismatches.append(f"row_count doc={len(doc_rows)} fixture={len(EXPECTED_ROWS)}")
    for index, (doc_row, row) in enumerate(zip(doc_rows, EXPECTED_ROWS), start=1):
        expected_end = row.start + row.size - 1
        if doc_row["start"] != row.start:
            mismatches.append(
                f"row {index} start: doc=0x{doc_row['start']:x} fixture=0x{row.start:x}"
            )
        if doc_row["end"] != expected_end:
            mismatches.append(
                f"row {index} end: doc=0x{doc_row['end']:x} fixture=0x{expected_end:x}"
            )
        if doc_row["name"] != doc_name_for(row):
            mismatches.append(
                f"row {index} name: doc={doc_row['name']!r} fixture={doc_name_for(row)!r}"
            )
    return mismatches


def row_aliases(row: MapRow) -> tuple[str, ...]:
    aliases = {
        "SID": ("AP SID", "System ID"),
        "AP0_REFCLK_S_CNTBase1": ("AP secure timer frame", "AP secure generic timer"),
        "FMU Region": ("APP subsystem FMU", "APP FMU"),
        "RGIC2LGIC_MESSREG": ("RGIC2LGIC", "remote GIC message register"),
        "DRAM low": ("DRAM", "low DRAM"),
        "DRAM high": ("DRAM", "high DRAM"),
        "AP Memory Expansion": ("RoS", "AP RoS"),
        "SMMU+NI-710AE GPV + PCIe CTRL+PHY": ("SMMU", "AP SMMU"),
    }
    return aliases.get(row.name, ())


def find_expected_rows(value: str) -> list[MapRow]:
    wanted = normalize_lookup(value)
    matches = []
    for row in EXPECTED_ROWS:
        names = (row.name, doc_name_for(row), slugify(row.name), *row_aliases(row))
        if any(normalize_lookup(name) == wanted for name in names):
            matches.append(row)
    return matches


def expected_row_to_json(row: MapRow) -> dict[str, str | int | list[str]]:
    return {
        "row_id": f"{slugify(row.name)}@0x{row.start:010x}",
        "name": row.name,
        "doc_name": doc_name_for(row),
        "start": row.start,
        "end": row.start + row.size - 1,
        "size": row.size,
        "classification": row.scope,
        "aliases": list(row_aliases(row)),
    }


def lua_block(text: str, start: int) -> str:
    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return text[start:]


def eval_lua_int(expr: str, constants: dict[str, int], tables: dict[str, list[int]]) -> int | None:
    value = expr.strip().rstrip(";")
    for table, entries in tables.items():
        for index, item in enumerate(entries, start=1):
            value = value.replace(f"{table}[{index}]", str(item))
    for name, item in sorted(constants.items(), key=lambda pair: len(pair[0]), reverse=True):
        value = re.sub(rf"\b{re.escape(name)}\b", str(item), value)
    if not re.fullmatch(r"[0-9xXa-fA-F+\-*/ ().]+", value):
        return None
    try:
        result = eval(value, {"__builtins__": {}}, {})
    except (ArithmeticError, NameError, SyntaxError):
        return None
    return int(result) if isinstance(result, int | float) else None


def parse_constants(text: str) -> tuple[dict[str, int], dict[str, list[int]]]:
    constants: dict[str, int] = {}
    tables: dict[str, list[int]] = {}
    match = re.search(r"block_base = \{([^}]+)\}", text, re.S)
    if match:
        tables["ap_virtio.block_base"] = [
            int(item, 0) for item in re.findall(r"0x[0-9a-fA-F]+", match.group(1))
        ]
    for name in ("mmio_size", "net_base", "rng_base"):
        match = re.search(rf"{name} = (0x[0-9a-fA-F]+|\d+);", text)
        if match:
            constants[f"ap_virtio.{name}"] = int(match.group(1), 0)
    for line in text.splitlines():
        match = re.match(r"(?:local )?([A-Z][A-Z0-9_]*) = ([^;\n]+)", line.strip())
        if match:
            parsed = eval_lua_int(match.group(2), constants, tables)
            if parsed is not None:
                constants[match.group(1)] = parsed
    return constants, tables


def module_type(block: str) -> str:
    match = re.search(r'moduletype = "([^"]+)"', block)
    return match.group(1) if match else "unknown"


def parse_object_sockets(text: str, lua_file: str, constants: dict[str, int], tables: dict[str, list[int]]) -> list[LuaSocket]:
    sockets: list[LuaSocket] = []
    for match in re.finditer(r"(?m)^    ([A-Za-z0-9_]+)\s*=\s*(?:[^{\n]*and\s*)?\{", text):
        object_name = match.group(1)
        if object_name not in WATCHED_OBJECTS:
            continue
        block = lua_block(text, match.end() - 1)
        current_module = module_type(block)
        for socket_match in re.finditer(r"([A-Za-z0-9_]+)\s*=\s*(?:[^{\n]*and\s*)?\{", block):
            socket = lua_block(block, socket_match.end() - 1)
            address_match = re.search(r"address = ([^;\n]+)", socket)
            size_match = re.search(r"size = ([^;\n]+)", socket)
            if not address_match or not size_match:
                continue
            address = eval_lua_int(address_match.group(1), constants, tables)
            size = eval_lua_int(size_match.group(1), constants, tables)
            if address is not None and size is not None:
                sockets.append(LuaSocket(lua_file, object_name, current_module, socket_match.group(1), address, size))
    return sockets


def strip_lua_comments(text: str) -> str:
    return re.sub(r"--.*", "", text)


def parse_ap_compute_bindings(text: str) -> list[ApViewBinding]:
    bindings: list[ApViewBinding] = []
    clean_text = strip_lua_comments(text)
    for match in re.finditer(
        r'bind_ap_socket\(\s*platform\.([A-Za-z0-9_]+)\s*,\s*"([A-Za-z0-9_]+)"\s*\)',
        clean_text,
    ):
        bindings.append(ApViewBinding("ap_compute.lua", match.group(1), match.group(2), "bind_ap_socket"))
    direct_assignment = re.search(
        r"platform\.host_ap_atu\.translation_socket\.bind\s*=\s*"
        r'"&ap_view_router\.initiator_socket"',
        clean_text,
    )
    if direct_assignment:
        bindings.append(
            ApViewBinding(
                "ap_compute.lua",
                "host_ap_atu",
                "translation_socket",
                "direct_ap_view_router_bind",
            )
        )
    if re.search(r"for\s+i\s*=\s*0\s*,\s*15\s+do.*?redist_iface_.*?end", clean_text, re.S):
        bindings.append(ApViewBinding("ap_compute.lua", "ap_gic", "redist_iface_*", "bind_ap_socket_loop"))
    return bindings


def parse_ros_bindings(ap_compute_text: str, ros_text: str) -> list[ApViewBinding]:
    if "ctx.ros.bind_ap_view_targets(platform, bind_ap_target)" not in strip_lua_comments(ap_compute_text):
        return []
    bindings: list[ApViewBinding] = []
    clean_text = strip_lua_comments(ros_text)
    for index in range(4):
        if re.search(
            r'platform\["ap_virtioblk_"\.\.i\].*?bind_ap_target\(virtio\.mem',
            clean_text,
            re.S,
        ):
            bindings.append(ApViewBinding("ros.lua", f"ap_virtioblk_{index}", "mem", "ros_bind_target_loop"))
    for match in re.finditer(
        r"bind_ap_target\(\s*platform\.([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)\s*\)",
        clean_text,
    ):
        bindings.append(ApViewBinding("ros.lua", match.group(1), match.group(2), "ros_bind_target"))
    return bindings


def current_ap_view_bindings(root: Path) -> list[ApViewBinding]:
    ap_compute = read_text(root / "tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua")
    ros = read_text(root / "tools/qbox-platform/platforms/apollo/hw-block/ros.lua")
    bindings = parse_ap_compute_bindings(ap_compute)
    bindings.extend(parse_ros_bindings(ap_compute, ros))
    return sorted(bindings, key=lambda item: (item.object_name, item.socket_name, item.lua_file))


def binding_to_json(binding: ApViewBinding) -> dict[str, str]:
    return {
        "lua_file": binding.lua_file,
        "object": binding.object_name,
        "socket": binding.socket_name,
        "binding_kind": binding.binding_kind,
    }


def binding_key(value: str) -> tuple[str, str]:
    pieces = value.split(":", maxsplit=1)
    if len(pieces) != 2 or not pieces[0] or not pieces[1]:
        raise argparse.ArgumentTypeError("expected OBJECT:SOCKET")
    return pieces[0], pieces[1]


def missing_ap_view_bindings(
    rows: list[dict[str, Any]],
    bindings: list[ApViewBinding],
    forbidden_bindings: set[tuple[str, str]],
) -> list[dict[str, str]]:
    existing = {
        (binding.object_name, binding.socket_name)
        for binding in bindings
        if (binding.object_name, binding.socket_name) not in forbidden_bindings
    }
    failures: list[dict[str, str]] = []
    for row in rows:
        if row["classification"] not in FINAL_REQUIRED_CLASSIFICATIONS:
            continue
        for object_name, socket_name in REQUIRED_AP_VIEW_BINDINGS.get(str(row["name"]), ()):
            if (object_name, socket_name) not in existing:
                failures.append(
                    {
                        "row": str(row["name"]),
                        "object": object_name,
                        "socket": socket_name,
                        "issue": "missing_ap_view_binding",
                    }
                )
    return failures


def add_gic_redists(sockets: list[LuaSocket], constants: dict[str, int]) -> None:
    base = constants.get("AP_GIC_REDIST_BASE")
    size = constants.get("AP_GIC_REDIST_SIZE")
    regions = constants.get("AP_GIC_ACTIVE_REDIST_REGIONS", 4)
    if base is None or size is None:
        return
    for index in range(regions):
        sockets.append(LuaSocket("rse.lua", "ap_gic", "arm_gicv3", f"redist_iface_{index}", base + index * size, size))


def add_smmu_factory_socket(text: str, sockets: list[LuaSocket], constants: dict[str, int], tables: dict[str, list[int]]) -> None:
    match = re.search(r"function ap_smmu_component\(\).*?return \{", text, re.S)
    if not match:
        return
    block = lua_block(text, match.end() - 1)
    current_module = module_type(block)
    address_match = re.search(r"address = ([^;\n]+)", block)
    size_match = re.search(r"size = ([^;\n]+)", block)
    if not address_match or not size_match:
        return
    address = eval_lua_int(address_match.group(1), constants, tables)
    size = eval_lua_int(size_match.group(1), constants, tables)
    if address is not None and size is not None:
        sockets.append(LuaSocket("rse.lua", "ap_smmu_0", current_module, "mem", address, size))


def current_coverage(root: Path) -> list[LuaSocket]:
    rse = read_text(root / "tools/qbox-platform/platforms/apollo/hw-block/rse.lua")
    constants, tables = parse_constants(rse)
    sockets = parse_object_sockets(rse, "rse.lua", constants, tables)
    add_gic_redists(sockets, constants)
    add_smmu_factory_socket(rse, sockets, constants, tables)
    return sorted(sockets, key=lambda item: (item.address, item.object_name, item.socket_name))


def overlaps(row: MapRow, socket: LuaSocket) -> bool:
    return socket.address < row.start + row.size and row.start < socket.address + socket.size


def fmu_subwindow_details(row: MapRow, sockets: list[LuaSocket]) -> dict[str, Any]:
    active_subwindows = []
    missing_objects = []
    unexpected_objects = []
    for index, plan in enumerate(AP_FMU_IMPLEMENTATION_PLAN):
        expected_start = row.start + index * AP_FMU_SUBWINDOW_SIZE
        expected_end = expected_start + AP_FMU_SUBWINDOW_SIZE - 1
        match = next(
            (
                socket for socket in sockets
                if (
                    socket.object_name == plan["object"]
                    and socket.module_type == "zena_fmu"
                    and socket.address == expected_start
                    and 0 < socket.size <= AP_FMU_SUBWINDOW_SIZE
                )
            ),
            None,
        )
        if match is None:
            missing_objects.append(str(plan["object"]))
            continue
        active_subwindows.append(
            {
                **plan,
                "ap_visible_base": expected_start,
                "ap_visible_end": expected_end,
                "ap_subwindow_size": AP_FMU_SUBWINDOW_SIZE,
                "modeled_base": match.address,
                "modeled_size": match.size,
                "modeled_end": match.address + match.size - 1,
                "module": match.module_type,
                "socket": match.socket_name,
                "lua_file": match.lua_file,
            }
        )
    for socket in sockets:
        if socket.object_name in AP_FMU_QBOX_OBJECTS and socket.module_type != "zena_fmu":
            unexpected_objects.append(socket_to_json(socket))
        if socket.object_name in AP_FMU_QBOX_OBJECTS and socket.size > AP_FMU_SUBWINDOW_SIZE:
            unexpected_objects.append(socket_to_json(socket))
    broad_placeholders = [
        socket for socket in sockets
        if (
            socket.module_type == "gs_memory"
            and socket.address <= row.start
            and socket.address + socket.size >= row.start + row.size
        )
    ]
    placeholder_only = bool(broad_placeholders) and not active_subwindows
    return {
        "active_subwindows": active_subwindows,
        "missing_objects": missing_objects,
        "unexpected_objects": unexpected_objects,
        "broad_placeholders": [socket_to_json(socket) for socket in broad_placeholders],
        "placeholder_only": placeholder_only,
        "expected_modeled_size_per_subwindow": AP_FMU_MODELED_SIZE,
        "modeled_coverage_bytes": sum(int(item["modeled_size"]) for item in active_subwindows),
        "ap_region_bytes": row.size,
        "notes": [
            "zena_fmu models the active banked register area at each firmware-derived cluster subwindow.",
            "Unimplemented AP FMU aggregate space is intentionally left unmapped instead of modeled as gs_memory.",
        ],
    }


def classify(row: MapRow, sockets: list[LuaSocket]) -> dict[str, Any]:
    if row.scope == "deferred_epic":
        status = "deferred_epic"
        matches: list[LuaSocket] = []
    else:
        matches = [socket for socket in sockets if overlaps(row, socket)]
        exact = [socket for socket in matches if socket.address <= row.start and socket.address + socket.size >= row.start + row.size]
        placeholder_objects = EXPLICIT_PLACEHOLDERS.get(row.name, set())
        placeholder_exact = [
            socket
            for socket in matches
            if (
                socket.object_name in placeholder_objects
                and socket.address == row.start
                and socket.size == row.size
            )
        ]
        invalid_placeholder = [
            socket
            for socket in matches
            if socket.object_name in placeholder_objects and socket not in placeholder_exact
        ]
        if row.name == "FMU Region":
            fmu_details = fmu_subwindow_details(row, matches)
            all_expected = (
                len(fmu_details["active_subwindows"]) == len(AP_FMU_IMPLEMENTATION_PLAN)
                and not fmu_details["missing_objects"]
                and not fmu_details["unexpected_objects"]
                and not fmu_details["broad_placeholders"]
            )
            status = (
                "partial_model" if all_expected
                else "placeholder_only" if fmu_details["placeholder_only"]
                else "invalid_placeholder" if fmu_details["broad_placeholders"]
                else "partial" if matches
                else "missing"
            )
        else:
            fmu_details = None
            status = (
                "explicit_placeholder" if placeholder_exact
                else "invalid_placeholder" if invalid_placeholder
                else "covered" if exact
                else "partial_model" if matches and row.name in PARTIAL_MODEL_ROWS
                else "partial" if matches
                else "missing"
            )
    result: dict[str, Any] = {
        "name": row.name,
        "start": row.start,
        "size": row.size,
        "scope": row.scope,
        "classification": status,
        "objects": [socket_to_json(socket) for socket in matches],
    }
    if row.name == "FMU Region" and row.scope != "deferred_epic":
        result["fmu_model"] = fmu_details
    if status == "partial_model" and row.name in PARTIAL_MODEL_ROWS:
        result["partial_model_reason"] = PARTIAL_MODEL_ROWS[row.name]
    return result


def socket_to_json(socket: LuaSocket) -> dict[str, str | int]:
    return {
        "lua_file": socket.lua_file,
        "object": socket.object_name,
        "module": socket.module_type,
        "socket": socket.socket_name,
        "address": socket.address,
        "size": socket.size,
    }


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def hex_or_missing(value: int | None) -> str:
    return "missing" if value is None else f"0x{value:x}"


def normalized_cells(value: str) -> str:
    return "<" + " ".join(value.strip().strip("<>").split()) + ">"


def dts_cell_address(cells: str) -> int | None:
    try:
        values = [int(value, 0) for value in cells.strip("<>").split()]
    except ValueError:
        return None
    return None if len(values) != 4 else (values[0] << 32) | values[1]


def high_dram_value_check(
    name: str, path: str, line: int | None, actual: int | None
) -> dict[str, str | int | bool | None]:
    fvp_compatible = actual == EXPECTED_HIGH_DRAM_BASE
    issue = (
        None
        if fvp_compatible
        else "ap_programmer_model_high_dram_base"
        if actual == AP_PROGRAMMER_MODEL_HIGH_DRAM_BASE
        else "unexpected_high_dram_base"
    )
    return {
        "name": name,
        "path": path,
        "line": line,
        "passed": fvp_compatible,
        "issue": issue,
        "current_value": hex_or_missing(actual),
        "expected_value": f"0x{EXPECTED_HIGH_DRAM_BASE:x}",
        "ap_programmer_model_value": f"0x{AP_PROGRAMMER_MODEL_HIGH_DRAM_BASE:x}",
        "fvp_compatible": fvp_compatible,
    }


def high_dram_inventory(root: Path) -> list[dict[str, str | int | bool | None]]:
    rse_path = "tools/qbox-platform/platforms/apollo/hw-block/rse.lua"
    primary_path = "tools/qbox-platform/platforms/apollo/hw-block/primary_compute.lua"
    dts_path = (
        "hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/arm/"
        "apollo-fvp.dts"
    )
    rse = read_text(root / rse_path)
    primary = read_text(root / primary_path)
    dts = read_text(root / dts_path)
    rse_match = re.search(r"\b(?:local\s+)?HOST_AP_DRAM2_BASE\s*=\s*(0x[0-9a-fA-F]+|\d+)", rse)
    primary_match = re.search(r"\bram_1\s*=\s*\{.*?\baddress\s*=\s*(0x[0-9a-fA-F]+|\d+)\s*;", primary, re.S)
    dts_node = re.search(r"memory@80000000\s*\{(?P<body>.*?)\n\s*\};", dts, re.S)
    dts_cells = re.findall(r"<[^>]+>", dts_node.group("body")) if dts_node else []
    dts_high = normalized_cells(dts_cells[1]) if len(dts_cells) > 1 else "missing"
    dts_base = None if dts_high == "missing" else dts_cell_address(dts_high)
    return [
        high_dram_value_check(
            "full_system_host_ap_dram2_base",
            rse_path,
            None if rse_match is None else line_for_offset(rse, rse_match.start(1)),
            None if rse_match is None else int(rse_match.group(1), 0),
        ),
        high_dram_value_check(
            "direct_boot_ram_1_base",
            primary_path,
            None if primary_match is None else line_for_offset(primary, primary_match.start(1)),
            None if primary_match is None else int(primary_match.group(1), 0),
        ),
        {
            "name": "local_build_linux_dts_high_memory_cells",
            "path": dts_path,
            "line": None if dts_node is None or len(dts_cells) <= 1 else line_for_offset(dts, dts.find(dts_cells[1], dts_node.start("body"))),
            "passed": dts_high == EXPECTED_HIGH_DRAM_DTS_CELLS,
            "issue": None if dts_high == EXPECTED_HIGH_DRAM_DTS_CELLS else "ap_programmer_model_high_dram_dts_cells" if dts_high == AP_PROGRAMMER_MODEL_HIGH_DRAM_DTS_CELLS else "unexpected_high_dram_dts_cells",
            "current_value": hex_or_missing(dts_base),
            "current_cells": dts_high,
            "expected_value": f"0x{EXPECTED_HIGH_DRAM_BASE:x}",
            "expected_size": f"0x{EXPECTED_HIGH_DRAM_SIZE:x}",
            "expected_cells": EXPECTED_HIGH_DRAM_DTS_CELLS,
            "ap_programmer_model_cells": AP_PROGRAMMER_MODEL_HIGH_DRAM_DTS_CELLS,
            "fvp_compatible": dts_high == EXPECTED_HIGH_DRAM_DTS_CELLS,
        },
    ]


def strip_c_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*", "", text)


def join_c_continuations(text: str) -> str:
    return re.sub(r"\\\n\s*", " ", text)


def eval_c_int(expr: str, constants: dict[str, int]) -> int | None:
    value = expr.strip()
    for name, item in sorted(constants.items(), key=lambda pair: len(pair[0]), reverse=True):
        value = re.sub(rf"\b{re.escape(name)}\b", str(item), value)
    if not re.fullmatch(r"[0-9xXa-fA-F+\-*/ ().]+", value):
        return None
    try:
        result = eval(value, {"__builtins__": {}}, {})
    except (ArithmeticError, NameError, SyntaxError):
        return None
    return int(result) if isinstance(result, int | float) else None


def parse_c_defines(text: str) -> dict[str, int]:
    constants: dict[str, int] = {
        "FWK_KIB": 1024,
        "FWK_MIB": 1024 * 1024,
        "FWK_GIB": 1024 * 1024 * 1024,
    }
    pending: dict[str, str] = {}
    for line in join_c_continuations(strip_c_comments(text)).splitlines():
        match = re.match(r"\s*#\s*define\s+([A-Z][A-Z0-9_]+)\s+(.+?)\s*$", line)
        if match:
            pending[match.group(1)] = match.group(2)
    progressed = True
    while progressed:
        progressed = False
        for name, expr in list(pending.items()):
            parsed = eval_c_int(expr, constants)
            if parsed is not None:
                constants[name] = parsed
                del pending[name]
                progressed = True
    return constants


def fmu_entry_block(text: str, entry_name: str) -> tuple[str, int] | None:
    match = re.search(rf"(?m)^    \[{re.escape(entry_name)}\]\s*=\s*\{{", text)
    if not match:
        return None
    next_entry = re.search(r"(?m)^    \[[A-Za-z0-9_]+\]\s*=\s*\{", text[match.end() :])
    end = len(text) if next_entry is None else match.end() + next_entry.start()
    return text[match.start() : end], line_for_offset(text, match.start())


def c_define_line(text: str, define_name: str) -> int | None:
    pattern = re.compile(rf"\s*#\s*define\s+{re.escape(define_name)}\b")
    for line_no, line in enumerate(text.splitlines(), start=1):
        if pattern.match(line):
            return line_no
    return None


def parse_fmu_entries(
    config_text: str,
    mmap_text: str,
    mmap_constants: dict[str, int],
    simulated_missing_bases: set[str],
) -> list[dict[str, str | int | None]]:
    entries: list[dict[str, str | int | None]] = []
    for name in AP_CL_NI710AE_FMUS:
        block_location = fmu_entry_block(config_text, name)
        block = None if block_location is None else block_location[0]
        config_line = None if block_location is None else block_location[1]
        base_expr = None
        base_define_line = None
        resolved_base = None
        parent = None
        parent_cr_index = None
        parent_ncr_index = None
        implementation = None
        firmware_name = None
        if block is not None:
            if name not in simulated_missing_bases:
                base_match = re.search(r"\.base\s*=\s*([^,\n]+)", block)
                if base_match:
                    base_expr = base_match.group(1).strip()
                    base_define_line = c_define_line(mmap_text, base_expr)
                    resolved_base = eval_c_int(base_expr, mmap_constants)
            parent_match = re.search(r"\.parent\s*=\s*([^,\n]+)", block)
            parent = None if parent_match is None else parent_match.group(1).strip()
            firmware_name_match = re.search(r'\.name\s*=\s*"([^"]+)"', block)
            firmware_name = None if firmware_name_match is None else firmware_name_match.group(1)
            cr_match = re.search(r"\.parent_cr_index\s*=\s*(\d+)", block)
            ncr_match = re.search(r"\.parent_ncr_index\s*=\s*(\d+)", block)
            parent_cr_index = None if cr_match is None else int(cr_match.group(1))
            parent_ncr_index = None if ncr_match is None else int(ncr_match.group(1))
            impl_match = re.search(r"\.implementation\s*=\s*([^,\n]+)", block)
            implementation = None if impl_match is None else impl_match.group(1).strip()
        entries.append(
            {
                "name": name,
                "firmware_name": firmware_name,
                "firmware_config_line": config_line,
                "firmware_base_expression": base_expr,
                "firmware_base_define_line": base_define_line,
                "firmware_resolved_base": resolved_base,
                "parent": parent,
                "parent_cr_index": parent_cr_index,
                "parent_ncr_index": parent_ncr_index,
                "implementation": implementation,
            }
        )
    return entries


def parse_fmu_doc_rows(root: Path) -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    for line_no, line in enumerate(read_text(root / DOC_REL_PATH).splitlines(), start=1):
        if not line.startswith("| 0x"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6 or not cells[3].startswith("FMU_"):
            continue
        rows.append(
            {
                "line": line_no,
                "start": parse_address(cells[0]),
                "end": parse_address(cells[1]),
                "size_text": cells[2],
                "name": cells[3],
                "description": clean_markdown_link(cells[4]),
                "access_control": cells[5],
            }
        )
    return rows


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def check_docs(root: Path, doc_paths: list[Path]) -> dict[str, Any]:
    checked_files: list[str] = []
    missing_files: list[str] = []
    evidence_hits: dict[str, list[dict[str, str | int]]] = {
        concept: [] for concept, _terms in T12_DOC_REQUIRED_CONCEPTS
    }
    for path in doc_paths:
        doc_path = path if path.is_absolute() else root / path
        display = display_path(doc_path, root)
        checked_files.append(display)
        try:
            lines = read_text(doc_path).splitlines()
        except FileNotFoundError:
            missing_files.append(display)
            continue
        for line_no, line in enumerate(lines, start=1):
            normalized_line = line.casefold()
            for concept, terms in T12_DOC_REQUIRED_CONCEPTS:
                for term in terms:
                    if term.casefold() in normalized_line:
                        evidence_hits[concept].append(
                            {
                                "file": display,
                                "line": line_no,
                                "term": term,
                                "text": line.strip(),
                            }
                        )
                        break
    missing_concepts = [
        concept for concept, _terms in T12_DOC_REQUIRED_CONCEPTS
        if not evidence_hits[concept]
    ]
    return {
        "passed": not missing_files and not missing_concepts,
        "check": "t12-docs",
        "checked_files": checked_files,
        "required_concepts": [
            {"concept": concept, "terms": list(terms)}
            for concept, terms in T12_DOC_REQUIRED_CONCEPTS
        ],
        "missing_files": missing_files,
        "missing_concepts": missing_concepts,
        "evidence_hits": evidence_hits,
    }


def collect_fmu_plan(
    root: Path, fmu_config_path: Path, fmu_mmap_path: Path, simulated_missing_bases: set[str]
) -> dict[str, Any]:
    config_text = read_text(fmu_config_path)
    mmap_text = read_text(fmu_mmap_path)
    mmap_constants = parse_c_defines(mmap_text)
    fmu_entries = parse_fmu_entries(config_text, mmap_text, mmap_constants, simulated_missing_bases)
    ap_fmu_row = next(row for row in EXPECTED_ROWS if row.name == "FMU Region")
    ap_doc_row = next(
        row
        for row in parse_doc_table(root)
        if row["name"] == "FMU Region" and row["start"] == ap_fmu_row.start
    )
    smd_rows = parse_fmu_doc_rows(root)
    smd_cluster_rows = [row for row in smd_rows if re.fullmatch(r"FMU_CLUSTER_00[0-3]", str(row["name"]))]
    by_cluster = {str(row["name"]): row for row in smd_cluster_rows}
    enriched_entries: list[dict[str, Any]] = []
    for index, entry in enumerate(fmu_entries):
        cluster_row = by_cluster.get(f"FMU_CLUSTER_00{index}")
        ap_subwindow_start = ap_fmu_row.start + index * AP_FMU_SUBWINDOW_SIZE
        enriched_entries.append(
            {
                **entry,
                "firmware_resolved_base_hex": hex_or_missing(entry["firmware_resolved_base"]),
                "smd_source_window": cluster_row,
                "target_ap_9_1_1_coverage_row": expected_row_to_json(ap_fmu_row),
                "target_ap_subwindow": {
                    "name": f"APP_FMU_CLUSTER_{index:03d}",
                    "start": ap_subwindow_start,
                    "end": ap_subwindow_start + AP_FMU_SUBWINDOW_SIZE - 1,
                    "size": AP_FMU_SUBWINDOW_SIZE,
                    "derivation": (
                        "AP 9.1.1 FMU Region is a 15 MB aggregate; "
                        "cluster subwindow order follows the SMD FMU_CLUSTER_000..003 rows."
                    ),
                },
            }
        )
    missing_bases = [
        str(entry["name"])
        for entry in enriched_entries
        if entry["firmware_base_expression"] is None or entry["firmware_resolved_base"] is None
    ]
    return {
        "passed": not missing_bases and len(enriched_entries) == len(AP_CL_NI710AE_FMUS),
        "check": "collect-fmu-plan",
        "source_of_truth": {
            "scp_fmu_config": display_path(fmu_config_path, root),
            "scp_mmap": display_path(fmu_mmap_path, root),
            "ap_programmer_model": DOC_REL_PATH,
            "fmu_design_doc": "arm-zena-css/documentation/design/fmu.rst",
        },
        "target_ap_9_1_1_coverage_row": expected_row_to_json(ap_fmu_row),
        "target_ap_9_1_1_doc_row": ap_doc_row,
        "selected_fmu_entries": list(AP_CL_NI710AE_FMUS),
        "fmu_subwindows": enriched_entries,
        "smd_fmu_source_windows": smd_cluster_rows,
        "missing_base_entries": missing_bases,
        "qa_simulated_missing_bases": sorted(simulated_missing_bases),
        "notes": [
            "T5 records the firmware-consumed NI-710AE cluster FMU subwindows only.",
            "It intentionally does not claim the full 15 MB APP FMU row is a monolithic model.",
        ],
    }


def parse_hex(value: str) -> int:
    try:
        return int(value, 0)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid integer: {value}") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--check", choices=("coverage", "high-dram"), default="coverage")
    parser.add_argument("--check-docs", action="store_true")
    parser.add_argument(
        "--doc-path",
        action="append",
        type=Path,
        default=[],
        help="QA hook: override T12 documentation paths checked by --check-docs.",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--list-expected", action="store_true")
    parser.add_argument("--require-row", action="append", default=[])
    parser.add_argument(
        "--forbid-object",
        action="append",
        default=[],
        help="QA hook: ignore the named QBox object while computing coverage.",
    )
    parser.add_argument(
        "--forbid-placeholder-only",
        action="store_true",
        help="Fail if the APP FMU region is represented only by a broad gs_memory placeholder.",
    )
    parser.add_argument(
        "--forbid-ap-view-bind",
        action="append",
        type=binding_key,
        default=[],
        metavar="OBJECT:SOCKET",
        help="QA hook: ignore one AP logical-view binding while validating reachability.",
    )
    parser.add_argument("--expect-current-host-ap-dram2", type=parse_hex)
    parser.add_argument("--collect-fmu-plan", action="store_true")
    parser.add_argument("--fmu-config", type=Path, default=Path(FMU_CONFIG_REL_PATH))
    parser.add_argument("--fmu-mmap", type=Path, default=Path(SI0_MMAP_REL_PATH))
    parser.add_argument(
        "--simulate-missing-fmu-base",
        action="append",
        choices=AP_CL_NI710AE_FMUS,
        default=[],
        help="QA hook: treat the selected AP_CLx NI710AE FMU as lacking a base.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = workspace_root()
    if args.check_docs:
        doc_paths = args.doc_path if args.doc_path else [Path(path) for path in T12_DOC_REL_PATHS]
        result = check_docs(root, doc_paths)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            print(args.output)
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        if result["passed"]:
            return 0
        for failure in result["missing_files"]:
            print(f"FAIL missing doc: {failure}", file=sys.stderr)
        for failure in result["missing_concepts"]:
            print(f"FAIL missing doc concept: {failure}", file=sys.stderr)
        return 2
    if args.collect_fmu_plan:
        fmu_config_path = args.fmu_config if args.fmu_config.is_absolute() else root / args.fmu_config
        fmu_mmap_path = args.fmu_mmap if args.fmu_mmap.is_absolute() else root / args.fmu_mmap
        result = collect_fmu_plan(
            root,
            fmu_config_path,
            fmu_mmap_path,
            set(args.simulate_missing_fmu_base),
        )
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            print(args.output)
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        if result["passed"]:
            return 0
        for failure in result["missing_base_entries"]:
            print(f"FAIL missing FMU base: {failure}", file=sys.stderr)
        return 2
    if args.check == "high-dram":
        checks = high_dram_inventory(root)
        result = {
            "passed": all(check["passed"] for check in checks),
            "check": "high-dram",
            "expected": {
                "high_dram_base": f"0x{EXPECTED_HIGH_DRAM_BASE:x}",
                "high_dram_size": f"0x{EXPECTED_HIGH_DRAM_SIZE:x}",
                "dts_high_memory_cells": EXPECTED_HIGH_DRAM_DTS_CELLS,
            },
            "checks": checks,
            "failures": [check for check in checks if not check["passed"]],
        }
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            print(args.output)
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        if result["passed"]:
            return 0
        for failure in result["failures"]:
            print(f"FAIL {failure['path']} {failure['current_value']}", file=sys.stderr)
        return 2
    raw_sockets = current_coverage(root)
    sockets = [
        socket for socket in raw_sockets
        if socket.object_name not in set(args.forbid_object)
    ]
    rows = [classify(row, sockets) for row in EXPECTED_ROWS]
    ap_view_bindings = current_ap_view_bindings(root)
    forbidden_ap_view_bindings = set(args.forbid_ap_view_bind)
    ap_view_binding_failures = missing_ap_view_bindings(
        rows,
        ap_view_bindings,
        forbidden_ap_view_bindings,
    )
    doc_rows = parse_doc_table(root)
    fixture_mismatches = compare_fixture_to_doc(root)
    missing_required = [
        row["name"]
        for row in rows
        if row["scope"] == "required_now"
        and row["classification"] not in FINAL_REQUIRED_CLASSIFICATIONS
    ]
    required_missing = [name for name in args.require_row if not find_expected_rows(name)]
    required_matches = {
        name: [expected_row_to_json(row) for row in find_expected_rows(name)]
        for name in args.require_row
        if find_expected_rows(name)
    }
    required_row_status_failures = [
        name
        for name, matches in required_matches.items()
        if any(
            row["name"] == match["name"]
            and row["classification"] not in FINAL_REQUIRED_CLASSIFICATIONS
            for row in rows
            for match in matches
        )
    ]
    placeholder_only_failures: list[str] = []
    placeholder_only_rejection_probe: dict[str, Any] | None = None
    if args.forbid_placeholder_only:
        fmu_row = next(row for row in rows if row["name"] == "FMU Region")
        fmu_model = fmu_row.get("fmu_model", {})
        if (
            fmu_row["classification"] == "placeholder_only"
            or fmu_model.get("placeholder_only")
            or fmu_model.get("broad_placeholders")
        ):
            placeholder_only_failures.append("FMU Region placeholder-only coverage")
        fmu_expected = next(row for row in EXPECTED_ROWS if row.name == "FMU Region")
        synthetic_blob = LuaSocket(
            "qa-synthetic.lua",
            "ap_fmu_region",
            "gs_memory",
            "target_socket",
            fmu_expected.start,
            fmu_expected.size,
        )
        synthetic_result = classify(fmu_expected, [synthetic_blob])
        probe_passed = synthetic_result["classification"] == "placeholder_only"
        placeholder_only_rejection_probe = {
            "passed": probe_passed,
            "synthetic_object": socket_to_json(synthetic_blob),
            "classification": synthetic_result["classification"],
        }
        if not probe_passed:
            placeholder_only_failures.append("FMU Region placeholder-only rejection probe")
    expected_mismatch: list[str] = []
    if args.expect_current_host_ap_dram2 is not None:
        dram2 = next((socket for socket in sockets if socket.object_name == "host_ap_dram2"), None)
        actual = None if dram2 is None else dram2.address
        if actual != args.expect_current_host_ap_dram2:
            expected_mismatch.append(
                f"host_ap_dram2 expected 0x{args.expect_current_host_ap_dram2:x}, actual "
                f"{'missing' if actual is None else f'0x{actual:x}'}"
            )
    if args.list_expected:
        coverage_failures = []
    elif args.require_row:
        coverage_failures = required_row_status_failures
    else:
        coverage_failures = missing_required
    result = {
        "passed": (
            not fixture_mismatches
            and not required_missing
            and not coverage_failures
            and not ap_view_binding_failures
            and not placeholder_only_failures
            and not expected_mismatch
        ),
        "check": "expected-map-fixture",
        "coverage_gating": "non_gating_t1_surface",
        "final_required_allowed_classifications": sorted(FINAL_REQUIRED_CLASSIFICATIONS),
        "source_doc": str(root / DOC_REL_PATH),
        "source_doc_table_header_line": 91,
        "plan": str(root / PLAN_REL_PATH),
        "expected_row_count": len(EXPECTED_ROWS),
        "expected_map_row_count": len(EXPECTED_ROWS),
        "source_non_reserved_row_count": len(doc_rows),
        "required_now_row_count": sum(row.scope == "required_now" for row in EXPECTED_ROWS),
        "deferred_epic_row_count": sum(row.scope == "deferred_epic" for row in EXPECTED_ROWS),
        "required_now_row_names": [
            row.name for row in EXPECTED_ROWS if row.scope == "required_now"
        ],
        "deferred_epic_row_names": [
            row.name for row in EXPECTED_ROWS if row.scope == "deferred_epic"
        ],
        "expected_rows": [expected_row_to_json(row) for row in EXPECTED_ROWS],
        "fixture_doc_mismatches": fixture_mismatches,
        "classifications": rows,
        "current_qbox_ap_map": [socket_to_json(socket) for socket in sockets],
        "ap_view_binding_required_rows": {
            name: [
                {"object": object_name, "socket": socket_name}
                for object_name, socket_name in bindings
            ]
            for name, bindings in REQUIRED_AP_VIEW_BINDINGS.items()
        },
        "ap_view_bindings": [binding_to_json(binding) for binding in ap_view_bindings],
        "forbidden_ap_view_bindings": [
            {"object": object_name, "socket": socket_name}
            for object_name, socket_name in sorted(forbidden_ap_view_bindings)
        ],
        "ap_view_binding_failures": ap_view_binding_failures,
        "forbidden_objects": sorted(set(args.forbid_object)),
        "forbidden_qbox_ap_map": [
            socket_to_json(socket)
            for socket in raw_sockets
            if socket.object_name in set(args.forbid_object)
        ],
        "missing_required_now": missing_required,
        "required_row_failures": required_missing,
        "required_row_status_failures": required_row_status_failures,
        "required_row_matches": required_matches,
        "forbid_placeholder_only": args.forbid_placeholder_only,
        "placeholder_only_failures": placeholder_only_failures,
        "placeholder_only_rejection_probe": placeholder_only_rejection_probe,
        "expectation_failures": expected_mismatch,
        "sources": [
            DOC_REL_PATH,
            PLAN_REL_PATH,
            "tools/qbox-platform/platforms/apollo/hw-block/rse.lua",
            "tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua",
            "tools/qbox-platform/platforms/apollo/hw-block/ros.lua",
        ],
    }
    if args.list_expected:
        for row in EXPECTED_ROWS:
            print(
                f"{slugify(row.name)}@0x{row.start:010x} "
                f"0x{row.start:010x}..0x{row.start + row.size - 1:010x} "
                f"{row.scope} {row.name}"
            )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(args.output)
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    if result["passed"]:
        return 0
    for failure in (
        fixture_mismatches
        + coverage_failures
        + required_missing
        + [
            f"missing AP view binding: {failure['row']} "
            f"{failure['object']}:{failure['socket']}"
            for failure in ap_view_binding_failures
        ]
        + placeholder_only_failures
        + expected_mismatch
    ):
        print(f"FAIL {failure}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
