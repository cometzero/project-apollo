from __future__ import annotations

import gzip
import importlib.util
from pathlib import Path
import struct

import pytest


ROOT = Path(__file__).resolve().parents[1]
INSPECTOR_PATH = ROOT / "scripts/test/qbox_apollo_pcie_irq_inspect.py"


def load_inspector(name: str):
    spec = importlib.util.spec_from_file_location(name, INSPECTOR_PATH)
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


def write_pe(path: Path, entries: list[tuple[str, bytes]]) -> None:
    pe_offset = 0x80
    optional_size = 0xF0
    table_offset = pe_offset + 24 + optional_size
    raw_offset = (table_offset + len(entries) * 40 + 0x1FF) & ~0x1FF
    raw_sizes = [(len(data) + 0x1FF) & ~0x1FF for _name, data in entries]
    image = bytearray(raw_offset + sum(raw_sizes))
    image[0:2] = b"MZ"
    struct.pack_into("<I", image, 0x3C, pe_offset)
    image[pe_offset : pe_offset + 4] = b"PE\0\0"
    struct.pack_into(
        "<HHIIIHH",
        image,
        pe_offset + 4,
        0xAA64,
        len(entries),
        0,
        0,
        0,
        optional_size,
        0,
    )
    optional = pe_offset + 24
    struct.pack_into("<H", image, optional, 0x20B)
    struct.pack_into("<II", image, optional + 32, 0x1000, 0x200)
    struct.pack_into("<I", image, optional + 60, raw_offset)
    cursor = raw_offset
    for index, (name, data) in enumerate(entries):
        header = table_offset + index * 40
        image[header : header + 8] = name.encode().ljust(8, b"\0")
        struct.pack_into(
            "<IIII", image, header + 8, len(data), 0, raw_sizes[index], cursor
        )
        image[cursor : cursor + len(data)] = data
        cursor += raw_sizes[index]
    path.write_bytes(image)


@pytest.mark.parametrize("duplicate", [".cmdline", ".dtb", ".initrd"])
def test_pe_parser_rejects_each_duplicate_required_section(
    tmp_path: Path, duplicate: str
) -> None:
    inspector = load_inspector(f"duplicate_pe_{duplicate}")
    required = [(".cmdline", b"cmd"), (".dtb", b"dtb"), (".initrd", b"initrd")]
    image = tmp_path / "duplicate.efi"
    write_pe(image, [*required, (duplicate, b"replacement")])
    with pytest.raises(RuntimeError, match="mode_identity"):
        inspector.pe_sections(image, frozenset(name for name, _data in required))


@pytest.mark.parametrize(
    "duplicate",
    [
        "etc/apollo-pcie-its-mode",
        "usr/share/apollo-pcie-its/input-manifest.json",
        "usr/bin/apollo-pcie-its-guest",
        "usr/bin/qbox-apollo-pcie-irq-test",
    ],
)
def test_newc_parser_rejects_each_duplicate_required_member(
    tmp_path: Path, duplicate: str
) -> None:
    inspector = load_inspector(f"duplicate_newc_{Path(duplicate).name}")
    required = [
        ("etc/apollo-pcie-its-mode", b"msix\n"),
        ("usr/share/apollo-pcie-its/input-manifest.json", b"{}"),
        ("usr/bin/apollo-pcie-its-guest", b"guest"),
        ("usr/bin/qbox-apollo-pcie-irq-test", b"wrapper"),
    ]
    archive = tmp_path / "duplicate.cpio.gz"
    write_newc(archive, [*required, (duplicate, b"replacement")])
    with pytest.raises(RuntimeError, match="mode_identity"):
        inspector.read_newc_members(
            archive, frozenset(name for name, _data in required)
        )


def test_parsers_allow_duplicate_unrelated_payloads(tmp_path: Path) -> None:
    inspector = load_inspector("duplicate_unrelated")
    pe = tmp_path / "unrelated.efi"
    write_pe(
        pe,
        [
            (".cmdline", b"cmd"),
            (".dtb", b"dtb"),
            (".initrd", b"initrd"),
            (".junk", b"one"),
            (".junk", b"two"),
        ],
    )
    assert (
        inspector.pe_sections(pe, frozenset((".cmdline", ".dtb", ".initrd")))[
            ".cmdline"
        ]
        == b"cmd"
    )
    archive = tmp_path / "unrelated.cpio.gz"
    required = [
        ("etc/apollo-pcie-its-mode", b"msix\n"),
        ("usr/share/apollo-pcie-its/input-manifest.json", b"{}"),
        ("usr/bin/apollo-pcie-its-guest", b"guest"),
        ("usr/bin/qbox-apollo-pcie-irq-test", b"wrapper"),
    ]
    write_newc(archive, [*required, ("unrelated", b"one"), ("unrelated", b"two")])
    assert (
        inspector.read_newc_members(
            archive, frozenset(name for name, _data in required)
        )["etc/apollo-pcie-its-mode"]
        == b"msix\n"
    )
