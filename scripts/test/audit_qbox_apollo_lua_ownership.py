#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import Final

try:
    from apollo_lua_descriptor import evaluated_platform, DescriptorError
except ModuleNotFoundError:
    from scripts.test.apollo_lua_descriptor import evaluated_platform, DescriptorError


DESCRIPTION: Final = "Audit Apollo QBox Lua hardware-object ownership."
APOLLO_REL: Final = "hsoc-stack/tools/qbox-platform/platforms/apollo"
ROS_OBJECTS: Final = {
    "ap_virtioblk_0",
    "ap_virtioblk_1",
    "ap_virtioblk_2",
    "ap_virtioblk_3",
    "ap_virtionet_0",
    "ap_virtiorng_0",
    "ap_rtc_0",
}
SI_CL0_OBJECTS: Final = {
    "host_si_cl0_sram",
    "host_si_cl0_cub",
    "host_si_cl0_clus_ppu",
    "host_si_cl0_core0_ppu",
}
SI_CL1_OBJECTS: Final = {
    "host_si_cl1_sram",
    "host_si_cl1_cub",
    "host_si_cl1_clus_ppu",
}
SYSTEM_MGMT_PREFIXES: Final = (
    "host_ap_rse_",
    "host_ap_si_",
    "host_rse_si_",
    "host_smd",
)
SYSTEM_MGMT_OBJECTS: Final = {
    "host_ap_atu",
    "host_si_pik",
    "host_si_scr",
    "host_si_atu",
    "host_css_counters_timers",
    "host_systop_pik",
    "host_smcf_sram",
}
FORBIDDEN_RSE_PREFIXES: Final = (
    "ap_",
    "host_ap_",
    "host_si_",
    "host_rse_si_",
    "host_smd",
    "si_cl0_",
    "si_cl1_",
)


@dataclass(frozen=True, slots=True)
class LuaObject:
    name: str
    owner_file: str
    module_type: str
    domain: str


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def module_type(block: str) -> str:
    match = re.search(r'moduletype\s*=\s*"([^"]+)"', block)
    return match.group(1) if match else "unknown"


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


def classify(name: str) -> str:
    if name in ROS_OBJECTS:
        return "ros"
    if name in SI_CL0_OBJECTS or name.startswith("si_cl0_"):
        return "si_cl0"
    if name in SI_CL1_OBJECTS or name.startswith("si_cl1_"):
        return "si_cl1"
    if name in SYSTEM_MGMT_OBJECTS or name.startswith(SYSTEM_MGMT_PREFIXES):
        return "system_mgmt"
    if name.startswith(("ap_", "host_ap_", "rse_ap_")):
        return "ap_compute"
    if name.startswith("rse_") or name in {"qemu_inst", "qemu_inst_mgr"}:
        return "rse"
    if name in {"host_router", "keep_alive_0"}:
        return "fabric"
    return "unknown"


def iter_lua_objects(path: Path, text: str) -> list[LuaObject]:
    objects: list[LuaObject] = []
    pattern = re.compile(
        r"(?m)^(?:    |)platform\.?([A-Za-z0-9_]+)\s*=\s*(?:[^{\n]*and\s*)?\{"
        r"|^    ([A-Za-z0-9_]+)\s*=\s*(?:[^{\n]*and\s*)?\{"
    )
    for match in pattern.finditer(text):
        name = match.group(1) or match.group(2)
        block = lua_block(text, match.end() - 1)
        objects.append(
            LuaObject(
                name=name,
                owner_file=path.name,
                module_type=module_type(block),
                domain=classify(name),
            )
        )
    return sorted(objects, key=lambda item: (item.owner_file, item.name))


def object_to_json(value: LuaObject) -> dict[str, str]:
    return {
        "name": value.name,
        "owner_file": value.owner_file,
        "module_type": value.module_type,
        "domain": value.domain,
    }


def forbidden_rse_objects(objects: list[LuaObject]) -> list[LuaObject]:
    return [
        item
        for item in objects
        if (item.owner_file == "hw-block/rse.lua" or
            item.owner_file.startswith("soc/hw-block/rse/"))
        and item.name.startswith(FORBIDDEN_RSE_PREFIXES)
    ]


def evaluated_objects(source_root: Path) -> list[LuaObject]:
    platform, locations = evaluated_platform(source_root)
    objects = []

    def visit(value: object, path: str) -> None:
        if not isinstance(value, dict):
            return
        if "moduletype" in value and path != "platform":
            name = path.removeprefix("platform.")
            source = locations.get(path, {}).get("path", "unknown").removeprefix("./")
            domain = classify(name)
            if domain == "unknown" and source.startswith("soc/hw-block/"):
                domain = source.split("/")[2]
            elif source.startswith("board/"):
                domain = "board"
            elif source.startswith("vp/") and domain == "unknown":
                domain = "vp"
            objects.append(LuaObject(name, source, value["moduletype"], domain))
        for key, child in value.items():
            visit(child, path + "." + str(key))

    visit(platform, "platform")
    return sorted(objects, key=lambda obj: (obj.owner_file, obj.name))


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--source-root", type=Path, default=root / APOLLO_REL)
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "build/qbox-apollo-qvp/subsystem-lua-ownership.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        objects = evaluated_objects(args.source_root)
    except DescriptorError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    forbidden = forbidden_rse_objects(objects)
    result = {
        "passed": args.report_only or not forbidden,
        "report_only": args.report_only,
        "object_count": len(objects),
        "forbidden_rse_object_count": len(forbidden),
        "objects": [object_to_json(item) for item in objects],
        "forbidden_rse_objects": [object_to_json(item) for item in forbidden],
        "profile": "evaluated-full-system-defaults-ap-enabled",
        "limitations": ["First-observed function provenance, not exact assignment lines.",
                        "Static descriptor ownership; no instantiated hardware or runtime evidence."],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(args.output)
    if forbidden and not args.report_only:
        for item in forbidden:
            print(f"FAIL rse owns {item.name} ({item.domain})", file=sys.stderr)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
