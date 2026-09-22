"""PE validation and unsigned UKI adaptation contracts."""

import hashlib
from pathlib import Path
import struct
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.run import autosd_uki


@pytest.fixture
def uki(tmp_path):
    sections = [(".text", b"stub"), (".linux", b"kernel"),
                (".initrd", b"old initrd"), (".cmdline", b"old args\0"),
                (".dtb", b"old dtb"), (".uname", b"6.12\0")]
    data = bytearray(1024 + len(sections) * 512)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 60, 128)
    data[128:132] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", data, 132, 0xAA64, len(sections), 0, 0, 0, 240, 0x2022)
    opt = 152
    struct.pack_into("<H", data, opt, 0x20B)
    struct.pack_into("<I", data, opt + 16, 4096)
    struct.pack_into("<Q", data, opt + 24, 0x140000000)
    struct.pack_into("<II", data, opt + 32, 4096, 512)
    struct.pack_into("<II", data, opt + 56, 7 * 4096, 1024)
    struct.pack_into("<H", data, opt + 68, 10)
    struct.pack_into("<I", data, opt + 108, 16)
    for index, (name, payload) in enumerate(sections):
        header = opt + 240 + index * 40
        data[header:header + 8] = name.encode().ljust(8, b"\0")
        struct.pack_into("<IIII", data, header + 8, len(payload),
                         (index + 1) * 4096, 512, 1024 + index * 512)
        struct.pack_into("<I", data, header + 36, 0x40000040)
        start = 1024 + index * 512
        data[start:start + len(payload)] = payload
    path = tmp_path / "source.efi"
    path.write_bytes(data)
    return path


def test_inspect_kernel(uki):
    result = autosd_uki.inspect_uki(uki)
    assert result["kernel_sha256"] == hashlib.sha256(b"kernel").hexdigest()
    assert result["sections"][".initrd"]["size"] == len(b"old initrd")


@pytest.mark.parametrize("offset,value,fmt,message", [
    (132, 0x8664, "H", "AArch64"),
    (152, 0x10B, "H", "PE32"),
    (152 + 144, 1024, "I", "Signed"),
    (392 + 40 + 20, 999999, "I", "bounds"),
    (392 + 40 + 20, 1024, "I", "Overlapping"),
    (392 + 40 + 12, 4096, "I", "Overlapping"),
    (152 + 108, 999, "I", "directories"),
])
def test_reject_invalid_pe(uki, offset, value, fmt, message):
    data = bytearray(uki.read_bytes())
    struct.pack_into("<" + fmt, data, offset, value)
    uki.write_bytes(data)
    with pytest.raises(ValueError, match=message):
        autosd_uki.inspect_uki(uki)


def test_reject_truncated(uki):
    uki.write_bytes(uki.read_bytes()[:400])
    with pytest.raises(ValueError):
        autosd_uki.inspect_uki(uki)


def test_adapt_growing_initrd_preserves_kernel_and_stub(uki, tmp_path):
    try:
        autosd_uki._objcopy()
    except ValueError:
        pytest.skip("AArch64 GNU objcopy not installed")
    original = uki.read_bytes()
    initrd = tmp_path / "initrd"
    initrd.write_bytes(b"new initrd" * 10000)
    destination = tmp_path / "adapted.efi"
    result = autosd_uki.prepare_uki(uki, initrd, "root=UUID=test console=ttyAMA0", destination)
    assert uki.read_bytes() == original
    assert ".dtb" not in result["sections"]
    assert result["kernel_sha256"] == hashlib.sha256(b"kernel").hexdigest()
    assert result["sections"][".text"]["sha256"] == hashlib.sha256(b"stub").hexdigest()
    assert result["sections"][".initrd"]["size"] == initrd.stat().st_size
    data = destination.read_bytes()
    section = result["sections"][".cmdline"]
    assert data[section["offset"]:section["offset"] + section["size"]] == b"root=UUID=test console=ttyAMA0\0"


def test_refuse_overwrite_source(uki):
    with pytest.raises(ValueError, match="differ"):
        autosd_uki.prepare_uki(uki, uki, "root=test", uki)


def test_reject_multiline_command_line(uki, tmp_path):
    with pytest.raises(ValueError, match="single line"):
        autosd_uki.prepare_uki(uki, uki, "root=test\nfoo", tmp_path / "output")


def test_reject_signed_pcr_policy(uki):
    data = bytearray(uki.read_bytes())
    offset = 392 + 4 * 40
    data[offset:offset + 8] = b".pcrsig\0"
    uki.write_bytes(data)
    with pytest.raises(ValueError, match="signed PCR"):
        autosd_uki.inspect_uki(uki)


def test_legacy_lz4_terminates_only_complete_bare_stream():
    magic = struct.pack("<I", 0x184C2102)
    stream = magic + struct.pack("<I", 3) + b"abc"
    assert autosd_uki._terminate_legacy_lz4(stream) == (stream + b"\0" * 4, True)
    for data in (b"other-format", magic, stream + b"\0", stream + b"\0" * 4,
                 stream + b"\0" * 4 + b"\x1f\x8btrailing-cpio",
                 magic + struct.pack("<I", 100) + b"abc",
                 magic + struct.pack("<I", 9 << 20) + b"abc"):
        assert autosd_uki._terminate_legacy_lz4(data) == (data, False)


def test_legacy_lz4_records_original_and_embedded_hashes(uki, tmp_path):
    try:
        autosd_uki._objcopy()
    except ValueError:
        pytest.skip("AArch64 GNU objcopy not installed")
    original = struct.pack("<II", 0x184C2102, 3) + b"abc"
    initrd = tmp_path / "legacy-initrd"
    initrd.write_bytes(original)
    result = autosd_uki.prepare_uki(uki, initrd, "root=test", tmp_path / "out.efi")
    assert initrd.read_bytes() == original
    assert result["lz4_terminator_added"]
    assert result["input_initrd_sha256"] == hashlib.sha256(original).hexdigest()
    assert result["embedded_initrd_sha256"] == hashlib.sha256(original + b"\0" * 4).hexdigest()
    assert result["sections"][".initrd"]["sha256"] == result["embedded_initrd_sha256"]
