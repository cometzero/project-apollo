"""Install Apollo UKIs in a private AutoSD disk, preserving boot-control state.

The EFI ukiboot loader, not this host tool, initializes the nightly image's
boot-control sentinel and updates its slot attempts. No GPT or rootfs changes
are made here. Callers must supply a disposable run copy, never the download.
"""

import hashlib
import os
from pathlib import Path
import shutil
import stat
import struct
import subprocess
import uuid
import zlib

try:
    from .autosd_uki import inspect_uki
except ImportError:  # Direct launcher execution puts scripts/run on sys.path.
    from autosd_uki import inspect_uki

SECTOR = 512
TYPES = {
    "efi": "c12a7328-f81f-11d2-ba4b-00a0c93ec93b",
    "ukiboot_a": "df331e4d-be00-463f-b4a7-8b43e18fb53a",
    "ukiboot_b": "df331e4d-be00-463f-b4a7-8b43e18fb53a",
    "ukibootctl": "fefd9070-346f-4c9a-85e6-17f07f922773",
    "root": "b921b045-1df0-41c3-af44-4c6f280d3fae",
}


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _open_disk(path, writable=False):
    fd = os.open(path, (os.O_RDWR if writable else os.O_RDONLY) | os.O_NOFOLLOW)
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        os.close(fd)
        raise ValueError("AutoSD disk must be a regular file")
    return os.fdopen(fd, "r+b" if writable else "rb")


def _read(stream, offset, size):
    stream.seek(offset)
    data = stream.read(size)
    if len(data) != size:
        raise ValueError("Truncated AutoSD disk")
    return data


def _header(stream, lba, sectors):
    data = _read(stream, lba * SECTOR, SECTOR)
    if data[:8] != b"EFI PART":
        raise ValueError("Missing GPT header")
    revision, size, crc, reserved = struct.unpack_from("<IIII", data, 8)
    if revision != 0x10000 or not 92 <= size <= SECTOR or reserved:
        raise ValueError("Unsupported GPT header")
    checked = bytearray(data[:size])
    checked[16:20] = b"\0" * 4
    if zlib.crc32(checked) != crc:
        raise ValueError("Invalid GPT header CRC")
    current, other, first, last = struct.unpack_from("<QQQQ", data, 24)
    table, count, entry_size, table_crc = struct.unpack_from("<QIII", data, 72)
    if current != lba or other != (sectors - 1 if lba == 1 else 1):
        raise ValueError("Invalid GPT header locations")
    table_size = count * entry_size
    if (entry_size < 128 or entry_size % 128 or not count or
            table_size > 16 * 1024 * 1024 or not 2 <= first <= last < sectors - 1):
        raise ValueError("Invalid GPT table bounds")
    table_end = table + (table_size + SECTOR - 1) // SECTOR
    if lba == 1:
        valid_table = 2 <= table < table_end <= first
    else:
        valid_table = last < table < table_end <= lba
    if not valid_table:
        raise ValueError("GPT table overlaps usable disk")
    entries = _read(stream, table * SECTOR, table_size)
    if zlib.crc32(entries) != table_crc:
        raise ValueError("Invalid GPT partition-table CRC")
    return {"first": first, "last": last, "guid": data[56:72],
            "count": count, "entry_size": entry_size, "entries": entries}


def _bootctl(data):
    magic = struct.unpack_from("<I", data)[0]
    crc_valid = zlib.crc32(data[:20]) == struct.unpack_from("<I", data, 20)[0]
    valid = magic == 1420550408 and crc_valid
    slots = [{"priority": data[4 + i * 4], "tries_remaining": data[5 + i * 4],
              "successful_boot": data[6 + i * 4]} for i in range(2)]
    return {"sha256": _sha(data), "magic": magic, "crc_valid": crc_valid,
            "valid": valid, "state": "valid" if valid else (
                "uninitialized" if data[:SECTOR] == b"X" * SECTOR else "invalid"),
            "slots": slots}


def _inspect(stream):
    size = os.fstat(stream.fileno()).st_size
    if size < 6 * SECTOR or size % SECTOR:
        raise ValueError("Invalid sector-aligned AutoSD disk size")
    sectors = size // SECTOR
    mbr = _read(stream, 0, SECTOR)
    if mbr[510:512] != b"\x55\xaa" or not any(mbr[450 + i * 16] == 0xEE for i in range(4)):
        raise ValueError("Missing protective GPT MBR")
    primary, backup = _header(stream, 1, sectors), _header(stream, sectors - 1, sectors)
    if primary != backup:
        raise ValueError("Primary and backup GPT disagree")
    parts, guids, ranges = {}, set(), []
    for index in range(primary["count"]):
        offset = index * primary["entry_size"]
        entry = primary["entries"][offset:offset + primary["entry_size"]]
        if entry[:16] == b"\0" * 16:
            continue
        kind, guid = (str(uuid.UUID(bytes_le=entry[start:start + 16])) for start in (0, 16))
        start, end = struct.unpack_from("<QQ", entry, 32)
        try:
            label = entry[56:128].decode("utf-16-le").split("\0", 1)[0]
        except UnicodeError as error:
            raise ValueError("Invalid GPT partition label") from error
        if not label or label in parts or guid in guids or guid == str(uuid.UUID(int=0)):
            raise ValueError("Missing or duplicate GPT partition identity")
        if not primary["first"] <= start <= end <= primary["last"]:
            raise ValueError("GPT partition outside usable bounds")
        if any(start <= previous_end and end >= previous_start for previous_start, previous_end in ranges):
            raise ValueError("Overlapping GPT partitions")
        ranges.append((start, end))
        guids.add(guid)
        parts[label] = {"index": index + 1, "start_lba": start, "sectors": end - start + 1,
                        "offset": start * SECTOR, "size": (end - start + 1) * SECTOR,
                        "type": kind, "uuid": guid}
    for label, kind in TYPES.items():
        if label not in parts or parts[label]["type"] != kind:
            raise ValueError(f"Missing or wrong-type AutoSD partition: {label}")
    control = parts["ukibootctl"]
    if not SECTOR <= control["size"] <= 16 * 1024 * 1024:
        raise ValueError("Unsupported boot-control partition size")
    bootctl = _bootctl(_read(stream, control["offset"], control["size"]))
    return {"disk_size": size, "sector_size": SECTOR, "partitions": parts, "bootctl": bootctl}


def inspect_disk(path):
    """Validate both GPTs and report AutoSD partitions and boot-control state."""
    with _open_disk(path) as stream:
        return _inspect(stream)


def _efi_file(path):
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"Missing EFI input: {path}")
    with path.open("rb") as stream:
        header = stream.read(64)
        if len(header) != 64 or header[:2] != b"MZ":
            raise ValueError(f"Invalid EFI input: {path}")
        stream.seek(struct.unpack_from("<I", header, 60)[0])
        if stream.read(6) != b"PE\0\0\x64\xaa":
            raise ValueError(f"Expected AArch64 EFI input: {path}")
    return path


def _write_esp(disk, partitions, loader, addon_a, addon_b):
    image = f"{Path(disk).absolute()}@@{partitions['efi']['offset']}"
    for letter in ("a", "b"):
        directory = f"::/EFI/BOOT/ukiboot_{letter}.efi.extra.d"
        exists = subprocess.run(["mdir", "-i", image, directory], capture_output=True)
        if exists.returncode:
            subprocess.run(["mmd", "-i", image, directory], check=True, capture_output=True)
    for source, target in ((loader, "BOOTAA64.EFI"),
                           (addon_a, "ukiboot_a.efi.extra.d/slot_a.addon.efi"),
                           (addon_b, "ukiboot_b.efi.extra.d/slot_b.addon.efi")):
        subprocess.run(["mcopy", "-o", "-i", image, str(source), f"::/EFI/BOOT/{target}"],
                       check=True, capture_output=True)


def _native_payloads(stream, partitions):
    hashes, headers = {}, {}
    for label in ("ukiboot_a", "ukiboot_b", "ukibootctl"):
        part = partitions[label]
        stream.seek(part["offset"])
        digest = hashlib.sha256()
        remaining = part["size"]
        while remaining:
            block = stream.read(min(1024 * 1024, remaining))
            if not block:
                raise ValueError("Truncated native partition")
            digest.update(block)
            remaining -= len(block)
        hashes[label] = digest.hexdigest()
        if label != "ukibootctl":
            header = _read(stream, part["offset"], 64)
            pe_offset = struct.unpack_from("<I", header, 60)[0]
            headers[label] = (header[:2] == b"MZ" and 64 <= pe_offset <= part["size"] - 6
                              and _read(stream, part["offset"] + pe_offset, 6)
                              == b"PE\0\0\x64\xaa")
    return hashes, headers


def prepare_native_disk(disk, *, loader=None, addon_a=None, addon_b=None):
    """Preserve native slot/control bytes; optionally override only the private ESP.

    PE checks identify available AArch64 slots, not UKI signatures or bootability.
    An initially empty inactive slot is valid. No BLS/rootfs extraction is needed.
    """
    overrides = (loader, addon_a, addon_b)
    if any(p is not None for p in overrides) and not all(p is not None for p in overrides):
        raise ValueError("Provide loader, addon_a and addon_b together")
    if any(Path(disk).samefile(p) for p in overrides if p is not None):
        raise ValueError("Disk must differ from EFI inputs")
    inputs = [_efi_file(p) for p in overrides] if loader is not None else []
    with _open_disk(disk) as stream:
        before = _inspect(stream)
        if before["bootctl"]["state"] not in ("valid", "uninitialized"):
            raise ValueError("Invalid native boot-control state")
        hashes, headers = _native_payloads(stream, before["partitions"])
    if not any(headers.values()):
        raise ValueError("No native AArch64 PE slot found")
    if inputs:
        for command in ("mdir", "mmd", "mcopy"):
            if not shutil.which(command):
                raise ValueError(f"Missing mtools command: {command}")
        if sum(p.stat().st_size for p in inputs) >= before["partitions"]["efi"]["size"]:
            raise ValueError("EFI overrides exceed ESP capacity")
        _write_esp(disk, before["partitions"], *inputs)
    with _open_disk(disk) as stream:
        after = _inspect(stream)
        after_hashes, _ = _native_payloads(stream, after["partitions"])
    if before != after or hashes != after_hashes:
        raise ValueError("Native preparation changed GPT, slots or boot-control state")
    after.update({"boot_path": "/EFI/BOOT/BOOTAA64.EFI",
                  "esp_partition": after["partitions"]["efi"]["index"],
                  "native_slot_sha256": {name: hashes[name] for name in headers},
                  "native_slot_pe_aarch64": headers,
                  "bootctl_partition_sha256": hashes["ukibootctl"],
                  "payload_policy": "preserve-native-slots-and-bootctl",
                  "loader_source": str(loader) if inputs else "native ESP",
                  "efi_sources": {name: {"path": str(path), "sha256": _sha(path.read_bytes())}
                                  for name, path in zip(("loader", "addon_a", "addon_b"), inputs)}})
    return after


def prepare_disk(disk, uki, *, loader=None, addon_a=None, addon_b=None):
    """Write both UKI slots on a private run copy; never initialize bootctl.

    Optional loader/addons must be provided together and built for EFI/BOOT.
    With no overrides the nightly image's existing ESP remains unchanged.
    """
    if any(item is not None for item in (loader, addon_a, addon_b)) and not all(
            item is not None for item in (loader, addon_a, addon_b)):
        raise ValueError("Provide loader, addon_a and addon_b together")
    inputs = [Path(uki)] + ([_efi_file(p) for p in (loader, addon_a, addon_b)] if loader is not None else [])
    if any(Path(disk).samefile(path) for path in inputs):
        raise ValueError("Disk must differ from EFI inputs")
    inspected = inspect_uki(uki)
    payload = Path(uki).read_bytes()
    with _open_disk(disk, writable=True) as stream:
        before = _inspect(stream)
        if loader is not None:
            for command in ("mdir", "mmd", "mcopy"):
                if not shutil.which(command):
                    raise ValueError(f"Missing mtools command: {command}")
            if sum(path.stat().st_size for path in inputs[1:]) >= before["partitions"]["efi"]["size"]:
                raise ValueError("EFI overrides exceed ESP capacity")
        for label in ("ukiboot_a", "ukiboot_b"):
            if len(payload) > before["partitions"][label]["size"]:
                raise ValueError(f"UKI exceeds {label} partition capacity")
        for label in ("ukiboot_a", "ukiboot_b"):
            stream.seek(before["partitions"][label]["offset"])
            stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    if loader is not None:
        _write_esp(disk, before["partitions"], loader, addon_a, addon_b)
    after = inspect_disk(disk)
    if after["bootctl"] != before["bootctl"] or after["partitions"] != before["partitions"]:
        raise ValueError("Disk preparation unexpectedly changed GPT or boot-control state")
    after.update({"boot_path": "/EFI/BOOT/BOOTAA64.EFI", "esp_partition": after["partitions"]["efi"]["index"],
                  "slot_image_sha256": _sha(payload), "slot_image_size": len(payload),
                  "kernel_sha256": inspected["kernel_sha256"],
                  "loader_source": str(loader) if loader is not None else "nightly ESP"})
    if loader is not None:
        after["efi_sources"] = {name: {"path": str(path), "sha256": _sha(Path(path).read_bytes())}
                                for name, path in (("loader", loader), ("addon_a", addon_a), ("addon_b", addon_b))}
    return after
