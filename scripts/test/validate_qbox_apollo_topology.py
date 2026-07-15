#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT_DIR = (
    ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block"
)
EXPORTER = DEFAULT_CONTRACT_DIR / "export_machine_contract.lua"
CONTRACT_FILES = (
    "topology.lua",
    "address_map.lua",
    "transaction_routes.lua",
    "signal_routes.lua",
    "boot_control.lua",
    "software_contract.lua",
    "machine_contract.lua",
    "export_machine_contract.lua",
)
POLICY_BRIDGES = {"atu", "apu", "atu_apu"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def named_index(
    values: list[dict[str, Any]],
    label: str,
    errors: list[dict[str, str]],
    key: str = "name",
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for value in values:
        name = value.get(key)
        if not isinstance(name, str) or not name:
            errors.append({"id": f"{label}:missing_name", "message": label})
            continue
        if name in result:
            errors.append({"id": f"{label}:duplicate:{name}", "message": name})
            continue
        result[name] = value
    return result


def validate_addresses(
    address_map: dict[str, Any],
    views: dict[str, dict[str, Any]],
    bridges: dict[str, dict[str, Any]],
    errors: list[dict[str, str]],
) -> set[str]:
    ranges = address_map.get("ranges", [])
    indexed = named_index(ranges, "address", errors)
    by_view: dict[str, list[dict[str, Any]]] = {}
    backing_sizes: dict[str, int] = {}
    for name, item in indexed.items():
        view = item.get("view")
        if view not in views:
            errors.append({"id": f"address:view:{name}:{view}", "message": name})
            continue
        base = item.get("base")
        size = item.get("size")
        if not isinstance(base, int) or not isinstance(size, int) or base < 0 or size <= 0:
            errors.append({"id": f"address:range:{name}", "message": name})
            continue
        end = base + size
        width = views[view].get("width")
        if not isinstance(width, int) or width < 1 or end > 1 << width:
            errors.append({"id": f"address:width:{view}:{name}", "message": name})
        bridge = item.get("bridge")
        if bridge is not None and bridge not in bridges:
            errors.append({"id": f"address:bridge:{name}:{bridge}", "message": name})
        if "priority" in item or "alias_of" in item:
            for required in ("reason", "source", "owner"):
                if not item.get(required):
                    errors.append(
                        {"id": f"address:annotation:{name}:{required}", "message": name}
                    )
        backing = item.get("backing")
        if isinstance(backing, str):
            backing_size = item.get("backing_size", size)
            previous = backing_sizes.setdefault(backing, backing_size)
            if previous != backing_size:
                errors.append(
                    {"id": f"address:backing_size:{backing}:{name}", "message": name}
                )
        by_view.setdefault(view, []).append(item)

    for view, items in by_view.items():
        ordered = sorted(items, key=lambda item: (item["base"], item["name"]))
        for left_index, left in enumerate(ordered):
            left_end = left["base"] + left["size"]
            for right in ordered[left_index + 1 :]:
                if right["base"] >= left_end:
                    break
                documented = bool(
                    (left.get("alias_of") or right.get("alias_of"))
                    and left.get("reason", right.get("reason"))
                )
                if not documented:
                    errors.append(
                        {
                            "id": f"address:overlap:{view}:{left['name']}:{right['name']}",
                            "message": f"{left['name']} overlaps {right['name']}",
                        }
                    )
    return {str(item.get("target")) for item in ranges if item.get("target")}


def validate_transactions(
    transaction: dict[str, Any],
    views: dict[str, dict[str, Any]],
    routers: dict[str, dict[str, Any]],
    bridges: dict[str, dict[str, Any]],
    targets: set[str],
    errors: list[dict[str, str]],
) -> None:
    initiators = named_index(transaction.get("initiators", []), "initiator", errors)
    routes = named_index(transaction.get("routes", []), "transaction", errors)
    for name, route in routes.items():
        initiator_value = route.get("initiator")
        initiator = initiator_value if isinstance(initiator_value, str) else ""
        if initiator not in initiators:
            errors.append(
                {
                    "id": f"transaction:initiator:{name}:{initiator}",
                    "message": name,
                }
            )
        source = route.get("from")
        target_view = route.get("to")
        if source not in views or target_view not in views:
            errors.append({"id": f"transaction:view:{name}", "message": name})
        target = route.get("target")
        if target not in routers and target not in targets:
            errors.append({"id": f"transaction:target:{name}:{target}", "message": name})
        if source != target_view:
            bridge_value = route.get("bridge")
            bridge_name = bridge_value if isinstance(bridge_value, str) else ""
            bridge = bridges.get(bridge_name)
            if bridge is None or bridge.get("kind") not in POLICY_BRIDGES:
                errors.append({"id": f"transaction:policy_bridge:{name}", "message": name})
        if route.get("requester_required") or route.get("stream_id_required"):
            initiator_data = initiators.get(initiator, {})
            if route.get("requester_required") and "requester" not in initiator_data:
                errors.append({"id": f"transaction:requester:{name}", "message": name})
            if route.get("stream_id_required") and "stream_id" not in initiator_data:
                errors.append({"id": f"transaction:stream_id:{name}", "message": name})


def validate_signals(signal: dict[str, Any], errors: list[dict[str, str]]) -> None:
    routes = named_index(signal.get("irq_routes", []), "irq", errors)
    used: dict[tuple[str, str, int], str] = {}
    for name, route in routes.items():
        if not route.get("source") or not route.get("sink"):
            errors.append({"id": f"irq:dangling:{name}", "message": name})
        irq_id = route.get("id")
        if not isinstance(irq_id, int):
            errors.append({"id": f"irq:id:{name}", "message": name})
            continue
        key = (str(route.get("controller")), str(route.get("kind")), irq_id)
        if key in used:
            errors.append({"id": f"irq:duplicate:{key[0]}:{key[1]}:{key[2]}", "message": name})
        used[key] = name
    for group in ("reset_routes", "fault_routes"):
        for name, route in named_index(signal.get(group, []), group, errors).items():
            if not route.get("source") or not route.get("sink"):
                errors.append({"id": f"{group}:dangling:{name}", "message": name})


def validate_boot_and_software(
    boot: dict[str, Any],
    software: dict[str, Any],
    domains: set[str],
    errors: list[dict[str, str]],
) -> None:
    actors = set(software.get("actors", []))
    actor_aliases = domains | actors | {"tfa"}
    sequence = named_index(boot.get("sequence", []), "boot", errors, "id")
    for name, step in sequence.items():
        if step.get("actor") not in actor_aliases:
            errors.append({"id": f"boot:actor:{name}:{step.get('actor')}", "message": name})
        dependency = step.get("after")
        if dependency is not None and dependency not in sequence:
            errors.append({"id": f"boot:dependency:{name}:{dependency}", "message": name})
    for interface in software.get("interfaces", []):
        name = str(interface.get("name"))
        for field in ("producer", "consumer"):
            if interface.get(field) not in actors:
                errors.append(
                    {"id": f"software:{field}:{name}:{interface.get(field)}", "message": name}
                )
    for region in software.get("shared_memory", []):
        region_name = str(region.get("name"))
        layout = sorted(region.get("regions", []), key=lambda item: item.get("offset", -1))
        cursor = 0
        for item in layout:
            if item.get("offset") != cursor:
                errors.append({"id": f"software:layout:{region_name}", "message": region_name})
                break
            cursor += item.get("size", 0)
        if cursor != region.get("size"):
            errors.append({"id": f"software:size:{region_name}", "message": region_name})


def validate_contract(output_dir: Path) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    topology = load_json(output_dir / "topology.json")
    address_map = load_json(output_dir / "address-routes.json")
    transaction = load_json(output_dir / "transaction-routes.json")
    signal = {
        "irq_routes": load_json(output_dir / "irq-routes.json").get("routes", []),
        **load_json(output_dir / "reset-routes.json"),
    }
    boot = load_json(output_dir / "boot-routes.json")
    software = load_json(output_dir / "software-routes.json")

    domains = named_index(topology.get("domains", []), "domain", errors)
    views = named_index(topology.get("views", []), "view", errors)
    routers = named_index(topology.get("routers", []), "router", errors)
    bridges = named_index(topology.get("bridges", []), "bridge", errors)
    scopes = {item.get("name") for item in topology.get("scopes", [])}
    for name, view in views.items():
        if view.get("domain") not in domains:
            errors.append({"id": f"view:domain:{name}:{view.get('domain')}", "message": name})
    for name, router in routers.items():
        if router.get("view") not in views:
            errors.append({"id": f"router:view:{name}:{router.get('view')}", "message": name})
    for name, bridge in bridges.items():
        if bridge.get("from") not in views or bridge.get("to") not in views:
            errors.append({"id": f"bridge:view:{name}", "message": name})
        if bridge.get("scope") not in scopes:
            errors.append({"id": f"bridge:scope:{name}", "message": name})

    targets = validate_addresses(address_map, views, bridges, errors)
    validate_transactions(transaction, views, routers, bridges, targets, errors)
    validate_signals(signal, errors)
    validate_boot_and_software(boot, software, set(domains), errors)
    return sorted(errors, key=lambda item: item["id"])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_record(name: str, path: Path, hash_file: bool = True) -> dict[str, Any]:
    exists = path.is_file()
    return {
        "name": name,
        "path": str(path.resolve()),
        "exists": exists,
        "size": path.stat().st_size if exists else None,
        "sha256": sha256(path) if exists and hash_file else None,
        "hash_status": "collected" if exists and hash_file else "deferred_or_missing",
    }


def git_revision(path: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=path,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def config_value(text: str, name: str) -> str | None:
    match = re.search(rf'^\s*{re.escape(name)}\s*(?:\?\?=|=)\s*"([^"]+)"', text, re.MULTILINE)
    return match.group(1) if match else None


def artifact_manifest(contract_dir: Path, hash_artifacts: bool) -> dict[str, Any]:
    local_conf = ROOT / "build/conf/local.conf"
    local_text = local_conf.read_text(encoding="utf-8")
    source_artifacts = [
        artifact_record("local_conf", local_conf),
        artifact_record("bblayers_conf", ROOT / "build/conf/bblayers.conf"),
        artifact_record("templateconf", ROOT / "build/conf/templateconf.cfg"),
    ]
    source_artifacts.extend(
        artifact_record(f"contract_{Path(name).stem}", contract_dir / name)
        for name in CONTRACT_FILES[:6]
    )
    runtime_paths = {
        "local_rse_rom": ROOT / "build/local-apollo-qvp/deploy/firmware/rse-rom-image.img",
        "local_rse_flash": ROOT / "build/local-apollo-qvp/deploy/firmware/rse-flash-image.img",
        "local_rse_otp": ROOT / "build/local-apollo-qvp/deploy/firmware/rse-otp-image.img",
        "local_ap_flash": ROOT / "build/local-apollo-qvp/deploy/firmware/ap-flash-image.img",
        "local_si_cl0": ROOT / "build/local-apollo-qvp/deploy/firmware/si0_ramfw.bin",
        "local_si_cl1": ROOT / "build/local-apollo-qvp/deploy/firmware/zephyr-demos-cl1.bin",
        "local_dtb": ROOT / "build/local-apollo-qvp/deploy/boot/apollo-qvp.dtb",
        "local_rootfs": ROOT / "build/local-apollo-qvp/deploy/boot/apollo-qvp-local-disk.img",
        "yocto_rootfs": ROOT / "build/tmp_baremetal/deploy/images/apollo-qvp/nexios-image-apollo-qvp.wic",
        "yocto_qboxconf": ROOT / "build/tmp_baremetal/deploy/images/apollo-qvp/nexios-image-apollo-qvp.qboxconf",
    }
    source_artifacts.extend(
        artifact_record(name, path, hash_artifacts) for name, path in runtime_paths.items()
    )
    return {
        "schema_version": 1,
        "configuration": {
            "machine": config_value(local_text, "MACHINE"),
            "rd_aspen_variant": config_value(local_text, "RD_ASPEN_VARIANT"),
            "pc_cpus_count_default": int(config_value(local_text, "PC_CPUS_COUNT_DEFAULT") or 0),
            "tmpdir": config_value(local_text, "TMPDIR"),
        },
        "source_revisions": {
            "workspace": git_revision(ROOT),
            "qbox": git_revision(ROOT / "hsoc-stack/tools/qbox"),
            "qbox_platform": git_revision(ROOT / "hsoc-stack/tools/qbox-platform"),
            "qemu": git_revision(ROOT / "hsoc-stack/tools/qemu"),
        },
        "artifacts": source_artifacts,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and export the Apollo QVP machine contract")
    parser.add_argument("--contract-dir", type=Path, default=DEFAULT_CONTRACT_DIR)
    parser.add_argument(
        "--emit",
        type=Path,
        default=ROOT / "build/qbox-apollo-qvp/topology/topology.json",
    )
    parser.add_argument("--hash-artifacts", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract_dir = args.contract_dir.resolve()
    output_dir = args.emit.resolve().parent
    output_dir.mkdir(parents=True, exist_ok=True)
    lua = shutil.which("lua")
    if lua is None:
        errors = [{"id": "exporter:missing_lua", "message": "lua executable not found"}]
    else:
        result = subprocess.run(
            [lua, str(EXPORTER), "--contract-dir", str(contract_dir), "--out-dir", str(output_dir)],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode:
            errors = [{"id": "exporter:lua", "message": result.stderr.strip()}]
        else:
            errors = validate_contract(output_dir)

    write_json(output_dir / "artifacts.json", artifact_manifest(contract_dir, args.hash_artifacts))
    report = {
        "schema_version": 1,
        "status": "pass" if not errors else "fail",
        "contract_dir": str(contract_dir),
        "topology": str(args.emit.resolve()),
        "errors": errors,
    }
    write_json(output_dir / "validation.json", report)
    print(output_dir / "validation.json")
    if errors:
        for error in errors:
            print(f"FAIL {error['id']}: {error['message']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
