from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess
from typing import Final

try:
    import qbox_apollo_pcie_irq_contract as profile_contract
except ModuleNotFoundError:
    from scripts.test import qbox_apollo_pcie_irq_contract as profile_contract


JsonObject = profile_contract.JsonObject
JsonValue = profile_contract.JsonValue
Mode = profile_contract.Mode
ProfileError = profile_contract.ProfileError
object_field = profile_contract.object_field
sha256 = profile_contract.sha256
string_field = profile_contract.string_field

BOOT_PARTITION_OFFSET: Final = 1024 * 1024
MODE_FILE: Final = "etc/apollo-pcie-its-mode"
MANIFEST_FILE: Final = "usr/share/apollo-pcie-its/input-manifest.json"
GUEST_PROBE_FILE: Final = "usr/bin/apollo-pcie-its-guest"
GUEST_WRAPPER_FILE: Final = "usr/bin/qbox-apollo-pcie-irq-test"
UKI_SLOTS: Final = (
    "::/EFI/Linux/a-slot/auto-ad-nexios-a.efi",
    "::/EFI/Linux/b-slot/auto-ad-nexios-b.efi",
)
MODE_ARTIFACT_ROLES: Final = ("input_manifest", "disk", "uki", "initramfs")


def validate_distinct_mode_artifacts(artifacts: JsonObject) -> None:
    for role in MODE_ARTIFACT_ROLES:
        msix = object_field(artifacts.get(f"msix_{role}"), "mode_identity")
        intx = object_field(artifacts.get(f"intx_{role}"), "mode_identity")
        msix_hash = string_field(msix.get("sha256"), "mode_identity")
        intx_hash = string_field(intx.get("sha256"), "mode_identity")
        if msix_hash == intx_hash:
            raise ProfileError("mode_identity")


def read_newc_members(path: Path, wanted: frozenset[str]) -> dict[str, bytes]:
    members: dict[str, bytes] = {}
    with gzip.open(path, "rb") as source:
        while True:
            header = source.read(110)
            if len(header) != 110 or header[:6] not in (b"070701", b"070702"):
                raise ProfileError("mode_identity")
            try:
                fields = [
                    int(header[6 + index * 8 : 14 + index * 8], 16)
                    for index in range(13)
                ]
            except ValueError as error:
                raise ProfileError("mode_identity") from error
            file_size = fields[6]
            name_size = fields[11]
            encoded_name = source.read(name_size)
            if len(encoded_name) != name_size or not encoded_name.endswith(b"\0"):
                raise ProfileError("mode_identity")
            name = encoded_name[:-1].decode("utf-8", errors="strict")
            source.read(-(110 + name_size) % 4)
            if name == "TRAILER!!!":
                break
            if name in wanted:
                if name in members:
                    raise ProfileError("mode_identity")
                data = source.read(file_size)
                if len(data) != file_size:
                    raise ProfileError("mode_identity")
                members[name] = data
            else:
                source.seek(file_size, 1)
            source.read(-file_size % 4)
    if members.keys() != wanted:
        raise ProfileError("mode_identity")
    return members


def pe_sections(path: Path, wanted: frozenset[str]) -> dict[str, bytes]:
    image = path.read_bytes()
    if len(image) < 0x40 or image[:2] != b"MZ":
        raise ProfileError("mode_identity")
    pe_offset = struct.unpack_from("<I", image, 0x3C)[0]
    if pe_offset + 24 > len(image) or image[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise ProfileError("mode_identity")
    machine = struct.unpack_from("<H", image, pe_offset + 4)[0]
    section_count = struct.unpack_from("<H", image, pe_offset + 6)[0]
    optional_size = struct.unpack_from("<H", image, pe_offset + 20)[0]
    optional = pe_offset + 24
    optional_end = optional + optional_size
    if machine != 0xAA64 or optional_size < 112 or optional_end > len(image):
        raise ProfileError("mode_identity")
    magic = struct.unpack_from("<H", image, optional)[0]
    file_alignment = struct.unpack_from("<I", image, optional + 36)[0]
    size_headers = struct.unpack_from("<I", image, optional + 60)[0]
    if (
        magic != 0x20B
        or file_alignment < 0x200
        or file_alignment > 0x10000
        or file_alignment & (file_alignment - 1)
    ):
        raise ProfileError("mode_identity")
    table = optional_end
    table_end = table + section_count * 40
    if (
        table_end > size_headers
        or size_headers > len(image)
        or size_headers % file_alignment
    ):
        raise ProfileError("mode_identity")
    sections: dict[str, bytes] = {}
    raw_ranges: list[tuple[int, int]] = []
    for index in range(section_count):
        offset = table + index * 40
        try:
            name = image[offset : offset + 8].rstrip(b"\0").decode("ascii")
        except UnicodeDecodeError as error:
            raise ProfileError("mode_identity") from error
        virtual_size = struct.unpack_from("<I", image, offset + 8)[0]
        raw_size, raw_offset = struct.unpack_from("<II", image, offset + 16)
        if raw_size:
            raw_end = raw_offset + raw_size
            if (
                raw_offset < size_headers
                or raw_offset % file_alignment
                or raw_size % file_alignment
                or raw_end > len(image)
            ):
                raise ProfileError("mode_identity")
            raw_ranges.append((raw_offset, raw_end))
        if name in wanted:
            if name in sections or virtual_size > raw_size:
                raise ProfileError("mode_identity")
            sections[name] = image[raw_offset : raw_offset + virtual_size]
    raw_ranges.sort()
    if any(
        end > following_start
        for (_start, end), (following_start, _following_end) in zip(
            raw_ranges, raw_ranges[1:]
        )
    ):
        raise ProfileError("mode_identity")
    if sections.keys() != wanted:
        raise ProfileError("mode_identity")
    return sections


def validate_mode_payload(
    mode: Mode,
    manifest: Path,
    uki: Path,
    initramfs: Path,
    dtb: Path,
    boot_arguments: list[str],
    guest_probe: Path,
    guest_wrapper: Path,
) -> None:
    try:
        payload: JsonValue = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProfileError("mode_identity") from error
    if not isinstance(payload, dict) or payload.get("mode") != mode:
        raise ProfileError("mode_identity")
    members = read_newc_members(
        initramfs,
        frozenset((MODE_FILE, MANIFEST_FILE, GUEST_PROBE_FILE, GUEST_WRAPPER_FILE)),
    )
    if (
        members[MODE_FILE] != f"{mode}\n".encode()
        or members[MANIFEST_FILE] != manifest.read_bytes()
        or hashlib.sha256(members[GUEST_PROBE_FILE]).hexdigest() != sha256(guest_probe)
        or hashlib.sha256(members[GUEST_WRAPPER_FILE]).hexdigest()
        != sha256(guest_wrapper)
    ):
        raise ProfileError("mode_identity")
    sections = pe_sections(uki, frozenset((".cmdline", ".dtb", ".initrd")))
    try:
        command_line = sections[".cmdline"].rstrip(b"\0").decode("utf-8")
    except UnicodeDecodeError as error:
        raise ProfileError("mode_identity") from error
    if (
        command_line != " ".join(boot_arguments)
        or hashlib.sha256(sections[".dtb"]).hexdigest() != sha256(dtb)
        or hashlib.sha256(sections[".initrd"]).hexdigest() != sha256(initramfs)
    ):
        raise ProfileError("mode_identity")


def validate_disk_slots(disk: Path, uki: Path) -> None:
    expected = sha256(uki)
    for slot in UKI_SLOTS:
        result = subprocess.run(
            ("mcopy", "-i", f"{disk}@@{BOOT_PARTITION_OFFSET}", slot, "-"),
            capture_output=True,
            check=False,
        )
        if (
            result.returncode != 0
            or hashlib.sha256(result.stdout).hexdigest() != expected
        ):
            raise ProfileError("mode_identity")
