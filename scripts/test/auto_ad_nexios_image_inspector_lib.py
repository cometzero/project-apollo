#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import binascii
import hashlib
import re
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path


DEFAULT_EXPECTED = {"boot": "256M", "misc": "4M",
                    "rootro_a": "8192M", "rootro_b": "8192M",
                    "rootrw": "512M", "data": "4096M"}
EXPECTED_ORDER = list(DEFAULT_EXPECTED)
ESP_TYPE = "EF00"
LINUX_TYPE = "8300"
SECTOR_SIZE = 512
MISC_MAGIC = b"AANXBOOT"
MISC_VERSION = 1
MISC_HEADER_SIZE = 64
MISC_SIZE = 4 * 1024 * 1024
MISC_CRC_OFFSET, MISC_CRC_SIZE, MISC_RESERVED_OFFSET = 0x18, 4, 0x1C
ESP_REQUIRED_FILES = ("::/EFI/BOOT/bootaa64.efi", "::/loader/loader.conf",
                      "::/boot.scr", "::/Image")
ESP_SECURE_BOOT_AUTH_FILES = (
    "::/uefi-sb-authenticated-variables/PK.auth",
    "::/uefi-sb-authenticated-variables/KEK.auth",
    "::/uefi-sb-authenticated-variables/DB.auth",
    "::/uefi-sb-authenticated-variables/DBX.auth",
)
SLOT_UKI_FILES = {
    "a-slot": "::/EFI/Linux/a-slot/auto-ad-nexios-a.efi",
    "b-slot": "::/EFI/Linux/b-slot/auto-ad-nexios-b.efi",
}
SLOT_UKI_CMDLINES = {
    "a-slot": b"rootwait root=PARTLABEL=rootro_a ro console=",
    "b-slot": b"rootwait root=PARTLABEL=rootro_b ro console=",
}
SLOT_METADATA_FILES = {
    "a-slot": "::/EFI/Linux/a-slot/metadata",
    "b-slot": "::/EFI/Linux/b-slot/metadata",
}
SLOT_METADATA_VALUES = {
    "a-slot": b"slot=A\n",
    "b-slot": b"slot=B\n",
}


class InspectError(ValueError):
    pass


def run_command(argv):
    try:
        return subprocess.run(
            argv, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
    except OSError as exc:
        raise InspectError(f"failed to run {argv[0]!r}: {exc}") from exc


def require_tool(name):
    if not shutil.which(name):
        raise InspectError(f"required tool not found in PATH: {name}")


def parse_size(value):
    match = re.fullmatch(r"([0-9]+)([KMG])?", value.strip(), re.IGNORECASE)
    if not match:
        raise InspectError(f"invalid size {value!r}: expected integer K/M/G")
    scale = {"K": 1024, "M": 1024 * 1024, "G": 1024 * 1024 * 1024}
    return int(match.group(1)) * scale[(match.group(2) or "M").upper()]


def parse_expect_partitions(value):
    if not value:
        return dict(DEFAULT_EXPECTED)
    expected = {}
    for item in value.split(","):
        if "=" not in item:
            raise InspectError(
                f"invalid --expect-partitions item {item!r}: expected name=size"
            )
        name, size = item.split("=", 1)
        name = name.strip()
        if not name:
            raise InspectError("partition name cannot be empty")
        expected[name] = size.strip()
    return expected


def read_exact(path, offset, size):
    with Path(path).open("rb") as stream:
        stream.seek(offset)
        data = stream.read(size)
    if len(data) != size:
        raise InspectError(
            f"short read from {path}: offset={offset} size={size} got={len(data)}"
        )
    return data


def crc32_misc_header(blob):
    data = bytearray(blob[:MISC_RESERVED_OFFSET])
    data[MISC_CRC_OFFSET:MISC_CRC_OFFSET + MISC_CRC_SIZE] = b"\x00" * MISC_CRC_SIZE
    return binascii.crc32(data[:MISC_CRC_OFFSET]) & 0xFFFFFFFF


def parse_misc_blob(blob):
    if len(blob) != MISC_SIZE:
        raise InspectError(f"misc blob size mismatch: expected {MISC_SIZE}, got {len(blob)}")
    magic, version, header_size, slot, attempts, flags, generation = (
        struct.unpack_from("<8sIIBBHI", blob, 0)
    )
    crc_stored, = struct.unpack_from("<I", blob, MISC_CRC_OFFSET)
    crc_expected = crc32_misc_header(blob)
    if magic != MISC_MAGIC:
        raise InspectError(f"misc invalid magic: {magic!r}")
    if version != MISC_VERSION:
        raise InspectError(f"misc unsupported version: {version}")
    if header_size != MISC_HEADER_SIZE:
        raise InspectError(f"misc unsupported header size: {header_size}")
    if slot not in (0, 1):
        raise InspectError(f"misc invalid slot: {slot}")
    if crc_stored != crc_expected:
        raise InspectError(
            f"misc CRC mismatch: expected 0x{crc_expected:08x}, got 0x{crc_stored:08x}"
        )
    if any(blob[MISC_RESERVED_OFFSET:]):
        raise InspectError("misc reserved area is not zero-filled")
    return {
        "slot": "A" if slot == 0 else "B",
        "attempts": attempts,
        "flags": flags,
        "rollback_pending": bool(flags & 0x0001),
        "slot_successful": bool(flags & 0x0002),
        "generation": generation,
        "crc32": f"0x{crc_stored:08x}",
    }


def parse_sgdisk(wic):
    require_tool("sgdisk")
    proc = run_command(["sgdisk", "-p", str(wic)])
    if proc.returncode != 0:
        raise InspectError(proc.stderr.strip() or proc.stdout.strip())
    if "Partition table holds up to" not in proc.stdout:
        raise InspectError("sgdisk output does not describe a GPT partition table")
    row_re = re.compile(
        r"^\s*(\d+)\s+(\d+)\s+(\d+)\s+(.+?)\s+([0-9A-Fa-f]{4})\s+(.+?)\s*$"
    )
    partitions = []
    for line in proc.stdout.splitlines():
        match = row_re.match(line)
        if match:
            start, end = int(match.group(2)), int(match.group(3))
            partitions.append(
                {
                    "number": int(match.group(1)),
                    "start_sector": start,
                    "end_sector": end,
                    "offset": start * SECTOR_SIZE,
                    "size_bytes": (end - start + 1) * SECTOR_SIZE,
                    "code": match.group(5).upper(),
                    "name": match.group(6).strip(),
                }
            )
    if not partitions:
        raise InspectError("no partitions parsed from sgdisk output")
    return partitions


def partition_map(partitions):
    by_name = {}
    for part in partitions:
        if part["name"] in by_name:
            raise InspectError(f"duplicate partition name {part['name']!r}")
        by_name[part["name"]] = part
    return by_name


def check_partition_contract(partitions, expected):
    by_name = partition_map(partitions)
    actual_names = [part["name"] for part in partitions]
    if actual_names != list(expected):
        raise InspectError(
            f"partition order/name mismatch: expected {list(expected)}, got {actual_names}"
        )
    for name, size in expected.items():
        actual = by_name[name]["size_bytes"]
        expected_bytes = parse_size(size)
        if actual != expected_bytes:
            raise InspectError(
                f"partition {name} size mismatch: expected {expected_bytes} bytes, got {actual}"
            )
    for name, code in {
        "boot": ESP_TYPE,
        "misc": LINUX_TYPE,
        "rootro_a": LINUX_TYPE,
        "rootro_b": LINUX_TYPE,
        "rootrw": LINUX_TYPE,
        "data": LINUX_TYPE,
    }.items():
        if by_name[name]["code"] != code:
            raise InspectError(
                f"partition {name} type mismatch: expected {code}, got {by_name[name]['code']}"
            )
    return by_name


def blkid_probe(wic, part):
    require_tool("blkid")
    proc = run_command(
        ["blkid", "-p", "-o", "export", "-O", str(part["offset"]), "-S",
         str(part["size_bytes"]), str(wic)]
    )
    if proc.returncode != 0:
        return {"probed": False, "error": (proc.stderr or proc.stdout).strip()}
    result = {"probed": True}
    for line in proc.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key] = value
    return result


def copy_from_fat(wic, part, fat_path, out_path):
    require_tool("mcopy")
    proc = run_command(["mcopy", "-n", "-i", f"{wic}@@{part['offset']}", fat_path, str(out_path)])
    if proc.returncode != 0:
        raise InspectError(f"missing FAT file {fat_path}: {(proc.stderr or proc.stdout).strip()}")


def sha256_file(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def pe_has_authenticode_certificate(path):
    data = Path(path).read_bytes()
    if len(data) < 0x100 or data[:2] != b"MZ":
        raise InspectError(f"{path} is not a PE/COFF image")
    pe_offset, = struct.unpack_from("<I", data, 0x3C)
    if pe_offset + 24 >= len(data) or data[pe_offset:pe_offset + 4] != b"PE\0\0":
        raise InspectError(f"{path} is missing PE signature")
    optional_offset = pe_offset + 24
    magic, = struct.unpack_from("<H", data, optional_offset)
    if magic == 0x20B:
        security_dir_offset = optional_offset + 112 + (4 * 8)
    elif magic == 0x10B:
        security_dir_offset = optional_offset + 96 + (4 * 8)
    else:
        raise InspectError(f"{path} has unsupported PE optional header magic")
    if security_dir_offset + 8 > len(data):
        raise InspectError(f"{path} PE data directories are truncated")
    cert_offset, cert_size = struct.unpack_from("<II", data, security_dir_offset)
    return cert_offset != 0 and cert_size != 0


def inspect_esp_slots(wic, by_name, secure_boot, deploy_dir):
    result = {"files": {}, "slots": {}}
    with tempfile.TemporaryDirectory(prefix="aanx-esp-") as tmpdir:
        required_files = ESP_REQUIRED_FILES
        if secure_boot == "1":
            required_files += ESP_SECURE_BOOT_AUTH_FILES
        for index, fat_path in enumerate(required_files):
            out_path = Path(tmpdir) / f"boot-{index}"
            copy_from_fat(wic, by_name["boot"], fat_path, out_path)
            result["files"][fat_path.replace("::", "")] = out_path.stat().st_size

        for name in ("a-slot", "b-slot"):
            files = {}
            metadata_fat_path = SLOT_METADATA_FILES[name]
            metadata_path = Path(tmpdir) / f"{name}-metadata"
            copy_from_fat(wic, by_name["boot"], metadata_fat_path, metadata_path)
            metadata_value = metadata_path.read_bytes()
            if metadata_value != SLOT_METADATA_VALUES[name]:
                raise InspectError(
                    f"{name} metadata mismatch: expected "
                    f"{SLOT_METADATA_VALUES[name]!r}, got {metadata_value!r}"
                )
            files[metadata_fat_path.replace("::", "")] = metadata_path.stat().st_size

            uki_fat_path = SLOT_UKI_FILES[name]
            uki_path = Path(tmpdir) / f"{name}-uki.efi"
            copy_from_fat(wic, by_name["boot"], uki_fat_path, uki_path)
            if SLOT_UKI_CMDLINES[name] not in uki_path.read_bytes():
                raise InspectError(f"{name} UKI command line does not target its rootro slot")
            deploy_path = deploy_dir / Path(uki_fat_path).name
            if not deploy_path.exists():
                raise InspectError(f"missing deployed UKI artifact: {deploy_path}")
            esp_sha256 = sha256_file(uki_path)
            deploy_sha256 = sha256_file(deploy_path)
            if esp_sha256 != deploy_sha256:
                raise InspectError(f"{name} ESP UKI does not match deploy artifact")
            uki_signed = None
            if secure_boot == "1":
                uki_signed = pe_has_authenticode_certificate(uki_path)
                if not uki_signed:
                    raise InspectError(f"{name} UKI is unsigned but UEFI_SECURE_BOOT=1")
            files[uki_fat_path.replace("::", "")] = uki_path.stat().st_size
            result["slots"][name] = {
                "files": files,
                "metadata_slot": "A" if name == "a-slot" else "B",
                "uki_cmdline_root": "rootro_a" if name == "a-slot" else "rootro_b",
                "uki_deploy_artifact": str(deploy_path),
                "uki_sha256": esp_sha256,
                "uki_signed": uki_signed,
                "secure_boot_policy": secure_boot or "unknown",
            }
    return result


def find_deploy_artifact(deploy_dir, names):
    for name in names:
        path = deploy_dir / name
        if path.exists():
            return path
    return None
