#!/usr/bin/env python3
"""Inspect RD-Aspen FWU flash banks, metadata, and capsule handoff media."""

from __future__ import annotations

import argparse
import datetime as _dt
import gzip
import hashlib
import json
import struct
import uuid
from pathlib import Path


RSE_FLASH_RAW_SIZE = 0x04000000
AP_FLASH_RAW_SIZE = 0x08000000
FWU_PRIVATE_METADATA_REPLICA_OFFSETS = (0x5000, 0x6000)
FWU_METADATA_REPLICA_OFFSETS = (0x5000, 0x6000)
FWU_PRIVATE_METADATA_SIZE = 68
FWU_COMPONENT_NUMBER = 5

IMAGE_MAGIC = 0x96F3B83D
IMAGE_TLV_INFO_MAGIC = 0x6907
IMAGE_TLV_PROT_INFO_MAGIC = 0x6908
IMAGE_F_ENCRYPTED_AES128 = 0x00000004
IMAGE_F_ENCRYPTED_AES256 = 0x00000008
IMAGE_F_RAM_LOAD = 0x00000020
FIP_TOC_HEADER_NAME = 0xAA640001

RSE_BANKS = [
    {
        "component_index": 0,
        "component": "BL2",
        "media": "rse_flash",
        "primary_offset": 0x00007000,
        "secondary_offset": 0x00267000,
        "slot_size": 0x00020000,
        "parser": "raw",
    },
    {
        "component_index": 1,
        "component": "RSE_RUNTIME",
        "media": "rse_flash",
        "primary_offset": 0x00027000,
        "secondary_offset": 0x00287000,
        "slot_size": 0x00040000,
        "parser": "mcuboot",
    },
    {
        "component_index": 2,
        "component": "SI_CL0",
        "media": "rse_flash",
        "primary_offset": 0x00067000,
        "secondary_offset": 0x002C7000,
        "slot_size": 0x00100000,
        "parser": "mcuboot",
    },
    {
        "component_index": 3,
        "component": "AP_FIP",
        "media": "ap_flash",
        "primary_offset": 0x00007000,
        "secondary_offset": 0x00247000,
        "slot_size": 0x00240000,
        "parser": "fip",
    },
    {
        "component_index": 4,
        "component": "SI_CL1",
        "media": "rse_flash",
        "primary_offset": 0x00167000,
        "secondary_offset": 0x003C7000,
        "slot_size": 0x00100000,
        "parser": "mcuboot",
    },
]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_maybe_gzip(path: Path) -> tuple[bytes, dict[str, object]]:
    info: dict[str, object] = {
        "path": str(path),
        "exists": path.exists(),
    }
    if not path.exists():
        return b"", info
    raw = path.read_bytes()
    info.update(
        {
            "stored_size": len(raw),
            "stored_sha256": sha256(raw),
            "gzip": raw.startswith(b"\x1f\x8b"),
        }
    )
    if raw.startswith(b"\x1f\x8b"):
        data = gzip.decompress(raw)
        info.update(
            {
                "raw_size": len(data),
                "raw_sha256": sha256(data),
                "state": "gzip_decompressed_for_inspection",
            }
        )
        return data, info
    info.update(
        {
            "raw_size": len(raw),
            "raw_sha256": info["stored_sha256"],
            "state": "raw",
        }
    )
    return raw, info


def count_nonzero(data: bytes) -> int:
    return sum(1 for value in data if value)


def count_non_ff(data: bytes) -> int:
    return sum(1 for value in data if value != 0xFF)


def slot_state(data: bytes) -> str:
    if not data:
        return "missing"
    if not any(data):
        return "empty_zeroed"
    if all(value == 0xFF for value in data):
        return "empty_erased_ff"
    return "populated"


def parse_mcuboot(data: bytes, offset: int) -> dict[str, object]:
    info: dict[str, object] = {"offset": hex(offset)}
    if offset + 24 > len(data):
        info["valid"] = False
        info["reason"] = "header_out_of_range"
        return info

    magic, load_addr, header_size, protected_tlv_size, image_size, flags = (
        struct.unpack_from("<IIHHII", data, offset)
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

    tlv_offset = header_size + image_size
    if offset + tlv_offset + 4 > len(data):
        info["valid"] = False
        info["reason"] = "tlv_info_out_of_range"
        return info

    tlv_magic, tlv_total = struct.unpack_from("<HH", data, offset + tlv_offset)
    info["tlv_offset"] = hex(tlv_offset)
    info["first_tlv_magic"] = hex(tlv_magic)
    info["first_tlv_total"] = hex(tlv_total)
    if tlv_magic == IMAGE_TLV_PROT_INFO_MAGIC:
        if protected_tlv_size != tlv_total:
            info["valid"] = False
            info["reason"] = "protected_tlv_size_mismatch"
            return info
        unprotected_tlv_offset = tlv_offset + tlv_total
        if offset + unprotected_tlv_offset + 4 > len(data):
            info["valid"] = False
            info["reason"] = "unprotected_tlv_info_out_of_range"
            return info
        tlv_magic, tlv_total = struct.unpack_from(
            "<HH", data, offset + unprotected_tlv_offset
        )
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

    info["valid"] = True
    info["boot_read_image_size"] = hex(tlv_offset + protected_tlv_size + tlv_total)
    return info


def parse_fip(data: bytes, offset: int) -> dict[str, object]:
    info: dict[str, object] = {"offset": hex(offset)}
    if offset + 16 > len(data):
        info["valid"] = False
        info["reason"] = "toc_header_out_of_range"
        return info

    name, serial, flags = struct.unpack_from("<IIQ", data, offset)
    info.update({"toc_name": hex(name), "serial": hex(serial), "flags": hex(flags)})
    if name != FIP_TOC_HEADER_NAME:
        info["valid"] = False
        info["reason"] = "invalid_fip_toc_header"
        return info

    entries = []
    current = offset + 16
    for _ in range(64):
        if current + 40 > len(data):
            break
        uuid_bytes = data[current : current + 16]
        entry_offset, size, entry_flags = struct.unpack_from("<QQQ", data, current + 16)
        if uuid_bytes == bytes(16):
            break
        entries.append(
            {
                "uuid": str(uuid.UUID(bytes_le=uuid_bytes)),
                "offset": hex(entry_offset),
                "size": hex(size),
                "flags": hex(entry_flags),
            }
        )
        current += 40

    info["valid"] = True
    info["entry_count"] = len(entries)
    info["entries"] = entries
    return info


def analyze_slot(
    media: bytes, *, offset: int, size: int, parser: str
) -> dict[str, object]:
    slot = media[offset : min(len(media), offset + size)]
    info: dict[str, object] = {
        "offset": hex(offset),
        "size": hex(size),
        "available_size": hex(len(slot)),
        "state": slot_state(slot),
        "nonzero_bytes": count_nonzero(slot),
        "non_ff_bytes": count_non_ff(slot),
        "sha256": sha256(slot) if slot else None,
        "header16": slot[:16].hex(),
    }
    if parser == "mcuboot":
        info["image"] = parse_mcuboot(media, offset)
    elif parser == "fip":
        info["image"] = parse_fip(media, offset)
    return info


def analyze_banks(rse_flash: bytes, ap_flash: bytes) -> list[dict[str, object]]:
    media = {"rse_flash": rse_flash, "ap_flash": ap_flash}
    banks = []
    for bank in RSE_BANKS:
        data = media[bank["media"]]
        primary = analyze_slot(
            data,
            offset=int(bank["primary_offset"]),
            size=int(bank["slot_size"]),
            parser=str(bank["parser"]),
        )
        secondary = analyze_slot(
            data,
            offset=int(bank["secondary_offset"]),
            size=int(bank["slot_size"]),
            parser=str(bank["parser"]),
        )
        banks.append(
            {
                "component_index": bank["component_index"],
                "component": bank["component"],
                "media": bank["media"],
                "slot_size": hex(int(bank["slot_size"])),
                "primary": primary,
                "secondary": secondary,
            }
        )
    return banks


def parse_private_metadata(data: bytes, offset: int) -> dict[str, object]:
    raw = data[offset : offset + FWU_PRIVATE_METADATA_SIZE]
    info: dict[str, object] = {
        "offset": hex(offset),
        "size": FWU_PRIVATE_METADATA_SIZE,
        "available_size": len(raw),
        "sha256": sha256(raw) if raw else None,
        "header16": raw[:16].hex(),
    }
    if len(raw) < FWU_PRIVATE_METADATA_SIZE:
        info["valid_shape"] = False
        info["reason"] = "metadata_out_of_range"
        return info
    boot_index = raw[0]
    states = list(raw[1 : 1 + FWU_COMPONENT_NUMBER])
    info.update(
        {
            "boot_index": boot_index,
            "fwu_image_state": states,
            "boot_index_valid": boot_index in (0, 1),
            "states_valid": all(0 <= state <= 8 for state in states),
            "all_zero_ready": raw == bytes(FWU_PRIVATE_METADATA_SIZE),
        }
    )
    return info


def parse_fwu_metadata_v2(data: bytes, offset: int) -> dict[str, object]:
    info: dict[str, object] = {"offset": hex(offset)}
    if offset + 32 > len(data):
        info["valid_shape"] = False
        info["reason"] = "metadata_header_out_of_range"
        return info
    crc32, version, active, previous, size, desc_offset, reserved1 = struct.unpack_from(
        "<IIIIIHH", data, offset
    )
    bank_state = list(data[offset + 24 : offset + 28])
    info.update(
        {
            "crc32": hex(crc32),
            "version": version,
            "active_index": active,
            "previous_active_index": previous,
            "metadata_size": size,
            "desc_offset": hex(desc_offset),
            "bank_state": [hex(value) for value in bank_state],
            "reserved1": hex(reserved1),
            "valid_shape": version == 2 and size > 0 and offset + size <= len(data),
        }
    )
    if info["valid_shape"]:
        raw = data[offset : offset + size]
        info["sha256"] = sha256(raw)
        if desc_offset + 8 <= size:
            num_banks, reserved, num_images, image_entry_size, bank_info_entry_size = (
                struct.unpack_from("<BBHHH", raw, desc_offset)
            )
            info["fw_desc"] = {
                "num_banks": num_banks,
                "reserved": reserved,
                "num_images": num_images,
                "img_entry_size": image_entry_size,
                "bank_info_entry_size": bank_info_entry_size,
            }
    return info


def analyze_metadata(rse_flash: bytes, ap_flash: bytes) -> dict[str, object]:
    return {
        "rse_private_metadata": [
            parse_private_metadata(rse_flash, offset)
            for offset in FWU_PRIVATE_METADATA_REPLICA_OFFSETS
        ],
        "ap_fwu_metadata": [
            parse_fwu_metadata_v2(ap_flash, offset)
            for offset in FWU_METADATA_REPLICA_OFFSETS
        ],
    }


def parse_mbr_partition(data: bytes) -> dict[str, object]:
    if len(data) < 512:
        return {"valid": False, "reason": "disk_too_small"}
    info: dict[str, object] = {
        "mbr_signature": data[510:512].hex(),
        "valid": data[510:512] == b"\x55\xaa",
        "partitions": [],
    }
    for index in range(4):
        entry = data[446 + index * 16 : 446 + (index + 1) * 16]
        part_type = entry[4]
        start_lba = int.from_bytes(entry[8:12], "little")
        sectors = int.from_bytes(entry[12:16], "little")
        if part_type or start_lba or sectors:
            info["partitions"].append(
                {
                    "index": index,
                    "type": hex(part_type),
                    "start_lba": start_lba,
                    "sectors": sectors,
                    "offset": start_lba * 512,
                    "size": sectors * 512,
                }
            )
    return info


def fat_root_entries(data: bytes, part_offset: int) -> list[dict[str, object]]:
    boot = data[part_offset : part_offset + 512]
    if len(boot) < 64:
        return []
    bytes_per_sector = int.from_bytes(boot[11:13], "little")
    sectors_per_cluster = boot[13]
    reserved_sectors = int.from_bytes(boot[14:16], "little")
    fat_count = boot[16]
    root_entries = int.from_bytes(boot[17:19], "little")
    sectors_per_fat = int.from_bytes(boot[22:24], "little")
    if not all([bytes_per_sector, sectors_per_cluster, reserved_sectors, fat_count, root_entries]):
        return []
    root_dir_offset = part_offset + (
        (reserved_sectors + fat_count * sectors_per_fat) * bytes_per_sector
    )
    root_dir_size = root_entries * 32
    root = data[root_dir_offset : root_dir_offset + root_dir_size]
    entries = []
    for entry_offset in range(0, len(root), 32):
        entry = root[entry_offset : entry_offset + 32]
        if len(entry) < 32 or entry[0] == 0x00:
            break
        if entry[0] == 0xE5 or entry[11] == 0x0F:
            continue
        name = entry[0:8].decode("ascii", errors="replace").rstrip()
        ext = entry[8:11].decode("ascii", errors="replace").rstrip()
        filename = f"{name}.{ext}" if ext else name
        entries.append(
            {
                "name": filename.lower(),
                "raw_name": entry[0:11].decode("ascii", errors="replace"),
                "attr": hex(entry[11]),
                "cluster": int.from_bytes(entry[26:28], "little"),
                "size": int.from_bytes(entry[28:32], "little"),
            }
        )
    return entries


def analyze_capsule(
    disk_path: Path, capsule_path: Path | None, manifest_path: Path | None
) -> dict[str, object]:
    disk = disk_path.read_bytes() if disk_path.exists() else b""
    disk_info = parse_mbr_partition(disk)
    root_entries: list[dict[str, object]] = []
    if disk_info.get("partitions"):
        root_entries = fat_root_entries(disk, int(disk_info["partitions"][0]["offset"]))
    fw_cap = next((entry for entry in root_entries if entry["name"] == "fw.cap"), None)
    info: dict[str, object] = {
        "disk": {
            "path": str(disk_path),
            "exists": disk_path.exists(),
            "size": disk_path.stat().st_size if disk_path.exists() else None,
            "sha256": sha256(disk) if disk else None,
            "mbr": disk_info,
            "fat_root_entries": root_entries,
            "fw_cap_entry": fw_cap,
            "fw_cap_present": fw_cap is not None,
        }
    }
    if capsule_path is not None:
        capsule = capsule_path.read_bytes() if capsule_path.exists() else b""
        info["capsule"] = {
            "path": str(capsule_path),
            "exists": capsule_path.exists(),
            "size": capsule_path.stat().st_size if capsule_path.exists() else None,
            "sha256": sha256(capsule) if capsule else None,
            "disk_size_matches": bool(fw_cap and capsule_path.exists() and fw_cap["size"] == capsule_path.stat().st_size),
        }
    if manifest_path is not None and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        payloads = manifest.get("Payloads", [])
        info["manifest"] = {
            "path": str(manifest_path),
            "payload_count": len(payloads),
            "components": [
                {
                    "component": payload.get("Component"),
                    "update_image_index": payload.get("UpdateImageIndex"),
                    "payload": payload.get("Payload"),
                    "guid": payload.get("Guid"),
                }
                for payload in payloads
            ],
        }
    return info


def write_summary(report: dict[str, object], path: Path) -> None:
    lines = [
        "# QBox RD-Aspen FWU Inspection",
        "",
        f"- RSE flash raw size: {report['images']['rse_flash'].get('raw_size')}",
        f"- AP flash raw size: {report['images']['ap_flash'].get('raw_size')}",
        f"- Capsule disk fw.cap present: {report['capsule']['disk'].get('fw_cap_present')}",
        "",
        "## Banks",
        "",
    ]
    for bank in report["banks"]:
        lines.append(
            "- {component} ({media}) primary={primary} secondary={secondary}".format(
                component=bank["component"],
                media=bank["media"],
                primary=bank["primary"]["state"],
                secondary=bank["secondary"]["state"],
            )
        )
    lines.extend(["", "## Metadata", ""])
    for entry in report["metadata"]["rse_private_metadata"]:
        lines.append(
            "- RSE private metadata {offset}: boot_index={boot} states={states} all_zero_ready={ready}".format(
                offset=entry["offset"],
                boot=entry.get("boot_index"),
                states=entry.get("fwu_image_state"),
                ready=entry.get("all_zero_ready"),
            )
        )
    for entry in report["metadata"]["ap_fwu_metadata"]:
        lines.append(
            "- AP FWU metadata {offset}: version={version} active={active} previous={previous} banks={banks}".format(
                offset=entry["offset"],
                version=entry.get("version"),
                active=entry.get("active_index"),
                previous=entry.get("previous_active_index"),
                banks=entry.get("bank_state"),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    deploy = root / "build/tmp_baremetal/deploy/images/fvp-rd-aspen"
    parser = argparse.ArgumentParser(
        description="Inspect RD-Aspen FWU flash banks, metadata, and capsule media."
    )
    parser.add_argument("--rse-flash", type=Path, default=deploy / "rse-flash-image.img")
    parser.add_argument("--ap-flash", type=Path, default=deploy / "ap-flash-image.img")
    parser.add_argument(
        "--efi-capsule-disk",
        type=Path,
        default=deploy / "efi-capsule-update-disk-image-fvp-rd-aspen.img",
    )
    parser.add_argument(
        "--capsule",
        type=Path,
        default=deploy / "efi-capsule-update-image.img.uefi.capsule",
    )
    parser.add_argument(
        "--capsule-manifest",
        type=Path,
        default=deploy / "efi-capsule-update-image.img.json",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "build/qbox-fvp-rd-aspen" / f"fwu-inspect-{timestamp()}",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rse_flash, rse_info = read_maybe_gzip(args.rse_flash)
    ap_flash, ap_info = read_maybe_gzip(args.ap_flash)

    report: dict[str, object] = {
        "inputs": {
            "rse_flash": str(args.rse_flash.resolve()),
            "ap_flash": str(args.ap_flash.resolve()),
            "efi_capsule_disk": str(args.efi_capsule_disk.resolve()),
            "capsule": str(args.capsule.resolve()),
            "capsule_manifest": str(args.capsule_manifest.resolve()),
        },
        "expected_raw_sizes": {
            "rse_flash": RSE_FLASH_RAW_SIZE,
            "ap_flash": AP_FLASH_RAW_SIZE,
        },
        "images": {
            "rse_flash": rse_info,
            "ap_flash": ap_info,
        },
        "banks": analyze_banks(rse_flash, ap_flash),
        "metadata": analyze_metadata(rse_flash, ap_flash),
        "capsule": analyze_capsule(
            args.efi_capsule_disk, args.capsule, args.capsule_manifest
        ),
    }
    manifest_components = (
        report.get("capsule", {}).get("manifest", {}).get("components", [])
    )
    fwu_components = [
        component
        for component in manifest_components
        if not str(component.get("component", "")).startswith("DUMMY_")
    ]
    report["checks"] = {
        "rse_flash_raw_size_matches": len(rse_flash) == RSE_FLASH_RAW_SIZE,
        "ap_flash_raw_size_matches": len(ap_flash) == AP_FLASH_RAW_SIZE,
        "capsule_fw_cap_present": report["capsule"]["disk"].get("fw_cap_present"),
        "capsule_size_matches_manifest_image": report["capsule"]
        .get("capsule", {})
        .get("disk_size_matches"),
        "cfg2_fwu_component_count_is_5": len(fwu_components) == 5,
    }

    report_path = args.out_dir / "fwu-inspection.json"
    summary_path = args.out_dir / "summary.md"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    write_summary(report, summary_path)
    print(args.out_dir)
    print(report_path)
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
