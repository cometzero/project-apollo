from __future__ import annotations

from dataclasses import dataclass
import gzip
import importlib.util
import json
from pathlib import Path
import struct

import pytest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts/test/validate_qbox_apollo_pcie_irq_runtime.py"


@dataclass(frozen=True, slots=True)
class Bundle:
    manifest: Path
    uki: Path
    initramfs: Path
    dtb: Path
    arguments: list[str]
    guest_probe: Path
    guest_wrapper: Path


def load_validator(name: str):
    spec = importlib.util.spec_from_file_location(name, VALIDATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_newc(path: Path, entries: list[tuple[str, bytes]]) -> None:
    archive = bytearray()
    for inode, (name, data) in enumerate(entries, 1):
        encoded_name = name.encode() + b"\0"
        fields = (
            inode,
            0o100644,
            0,
            0,
            1,
            0,
            len(data),
            0,
            0,
            0,
            0,
            len(encoded_name),
            0,
        )
        archive.extend(
            b"070701" + b"".join(f"{value:08x}".encode() for value in fields)
        )
        archive.extend(encoded_name)
        archive.extend(b"\0" * (-len(archive) % 4))
        archive.extend(data)
        archive.extend(b"\0" * (-len(archive) % 4))
    trailer = b"TRAILER!!!\0"
    fields = (0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, len(trailer), 0)
    archive.extend(b"070701" + b"".join(f"{value:08x}".encode() for value in fields))
    archive.extend(trailer)
    archive.extend(b"\0" * (-len(archive) % 4))
    path.write_bytes(gzip.compress(bytes(archive), mtime=0))


def write_pe(
    path: Path,
    sections: list[tuple[str, bytes]],
    *,
    machine: int = 0xAA64,
    optional_size: int = 0xF0,
    magic: int = 0x20B,
    file_alignment: int = 0x200,
    raw_shift: int = 0,
) -> None:
    pe_offset = 0x80
    table = pe_offset + 24 + optional_size
    size_headers = (table + len(sections) * 40 + 0x1FF) & ~0x1FF
    raw_sizes = [(len(data) + 0x1FF) & ~0x1FF for _name, data in sections]
    image = bytearray(size_headers + sum(raw_sizes) + raw_shift)
    image[:2] = b"MZ"
    struct.pack_into("<I", image, 0x3C, pe_offset)
    image[pe_offset : pe_offset + 4] = b"PE\0\0"
    struct.pack_into(
        "<HHIIIHH",
        image,
        pe_offset + 4,
        machine,
        len(sections),
        0,
        0,
        0,
        optional_size,
        0,
    )
    optional = pe_offset + 24
    if optional_size >= 2:
        struct.pack_into("<H", image, optional, magic)
    if optional_size >= 40:
        struct.pack_into("<II", image, optional + 32, 0x1000, file_alignment)
    if optional_size >= 64:
        struct.pack_into("<I", image, optional + 60, size_headers)
    cursor = size_headers
    for index, ((name, data), raw_size) in enumerate(zip(sections, raw_sizes)):
        header = table + index * 40
        image[header : header + 8] = name.encode().ljust(8, b"\0")
        pointer = cursor + raw_shift
        struct.pack_into("<IIII", image, header + 8, len(data), 0, raw_size, pointer)
        image[pointer : pointer + len(data)] = data
        cursor += raw_size
    path.write_bytes(image)


def make_bundle(
    tmp_path: Path,
    *,
    machine: int = 0xAA64,
    optional_size: int = 0xF0,
    magic: int = 0x20B,
    file_alignment: int = 0x200,
    raw_shift: int = 0,
) -> Bundle:
    tmp_path.mkdir(parents=True, exist_ok=True)
    arguments = ["console=ttyAMA0"]
    common = " ".join(arguments).encode()
    manifest = tmp_path / "msix.json"
    manifest.write_text(json.dumps({"mode": "msix"}), encoding="utf-8")
    guest_probe, guest_wrapper = tmp_path / "guest", tmp_path / "wrapper"
    guest_probe.write_bytes(b"guest")
    guest_wrapper.write_bytes(b"wrapper")
    initramfs = tmp_path / "msix.cpio.gz"
    write_newc(
        initramfs,
        [
            ("etc/apollo-pcie-its-mode", b"msix\n"),
            ("usr/share/apollo-pcie-its/input-manifest.json", manifest.read_bytes()),
            ("usr/bin/apollo-pcie-its-guest", guest_probe.read_bytes()),
            ("usr/bin/qbox-apollo-pcie-irq-test", guest_wrapper.read_bytes()),
        ],
    )
    dtb = tmp_path / "profile.dtb"
    dtb.write_bytes(common)
    uki = tmp_path / "msix.efi"
    write_pe(
        uki,
        [(".cmdline", common), (".dtb", common), (".initrd", initramfs.read_bytes())],
        machine=machine,
        optional_size=optional_size,
        magic=magic,
        file_alignment=file_alignment,
        raw_shift=raw_shift,
    )
    return Bundle(manifest, uki, initramfs, dtb, arguments, guest_probe, guest_wrapper)


def validate(bundle: Bundle) -> None:
    load_validator(f"validate_{bundle.uki.parent.name}").validate_mode_payload(
        "msix",
        bundle.manifest,
        bundle.uki,
        bundle.initramfs,
        bundle.dtb,
        bundle.arguments,
        bundle.guest_probe,
        bundle.guest_wrapper,
    )


def metadata(image: bytearray) -> tuple[int, int, int, int]:
    pe = struct.unpack_from("<I", image, 0x3C)[0]
    optional = pe + 24
    table = optional + struct.unpack_from("<H", image, pe + 20)[0]
    size_headers = struct.unpack_from("<I", image, optional + 60)[0]
    return pe, optional, table, size_headers


def section(image: bytearray, table: int, index: int) -> int:
    return table + index * 40


def mutate_raw_offset(image: bytearray) -> None:
    _pe, _optional, table, _headers = metadata(image)
    header = section(image, table, 0)
    raw_size, raw_offset = struct.unpack_from("<II", image, header + 16)
    image.extend(b"\0")
    image[raw_offset + 1 : raw_offset + 1 + raw_size] = image[
        raw_offset : raw_offset + raw_size
    ]
    struct.pack_into("<I", image, header + 20, raw_offset + 1)


def mutate_raw_size(image: bytearray) -> None:
    _pe, _optional, table, _headers = metadata(image)
    header = section(image, table, 0)
    raw_size = struct.unpack_from("<I", image, header + 16)[0]
    struct.pack_into("<I", image, header + 16, raw_size + 1)


def mutate_header_overlap(image: bytearray) -> None:
    _pe, _optional, table, size_headers = metadata(image)
    header = section(image, table, 0)
    raw_size, raw_offset = struct.unpack_from("<II", image, header + 16)
    target = size_headers - raw_size
    image[target : target + raw_size] = image[raw_offset : raw_offset + raw_size]
    struct.pack_into("<I", image, header + 20, target)


def mutate_table_overflow(image: bytearray) -> None:
    _pe, optional, table, _headers = metadata(image)
    struct.pack_into("<I", image, optional + 60, table + 3 * 40 - 1)


def mutate_raw_eof(image: bytearray) -> None:
    _pe, _optional, table, _headers = metadata(image)
    header = section(image, table, 2)
    raw_size = struct.unpack_from("<I", image, header + 16)[0]
    struct.pack_into("<I", image, header + 20, len(image) - raw_size + 1)


def mutate_overlap(image: bytearray) -> None:
    _pe, _optional, table, _headers = metadata(image)
    first = struct.unpack_from("<I", image, section(image, table, 0) + 20)[0]
    struct.pack_into("<I", image, section(image, table, 1) + 20, first)


def mutate_virtual_gt_raw(image: bytearray) -> None:
    _pe, _optional, table, _headers = metadata(image)
    header = section(image, table, 0)
    raw_size = struct.unpack_from("<I", image, header + 16)[0]
    struct.pack_into("<I", image, header + 8, raw_size + 1)


def test_valid_aarch64_pe32_plus_is_accepted(tmp_path: Path) -> None:
    validate(make_bundle(tmp_path))


@pytest.mark.parametrize(
    ("name", "options"),
    [
        ("zero_optional_unaligned", {"optional_size": 0, "raw_shift": 1}),
        ("truncated_optional", {"optional_size": 32}),
        ("wrong_machine", {"machine": 0x8664}),
        ("wrong_magic", {"magic": 0x10B}),
        ("zero_file_alignment", {"file_alignment": 0}),
        ("non_power_two_alignment", {"file_alignment": 0x300}),
    ],
)
def test_invalid_pe_identity_is_rejected(
    tmp_path: Path, name: str, options: dict[str, int]
) -> None:
    bundle = make_bundle(tmp_path / name, **options)
    with pytest.raises(RuntimeError, match="mode_identity"):
        validate(bundle)


@pytest.mark.parametrize(
    "mutator",
    [
        mutate_raw_offset,
        mutate_raw_size,
        mutate_header_overlap,
        mutate_table_overflow,
        mutate_raw_eof,
        mutate_overlap,
        mutate_virtual_gt_raw,
    ],
)
def test_malformed_pe_ranges_are_rejected(tmp_path: Path, mutator) -> None:
    bundle = make_bundle(tmp_path)
    image = bytearray(bundle.uki.read_bytes())
    mutator(image)
    bundle.uki.write_bytes(image)
    with pytest.raises(RuntimeError, match="mode_identity"):
        validate(bundle)
