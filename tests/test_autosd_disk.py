"""AutoSD raw GPT validation and private-run disk preparation."""

import hashlib
from pathlib import Path
import struct
import sys
import uuid
import zlib

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.run import autosd_disk


def disk_bytes(entries=None):
    data = bytearray(80 * 512)
    data[450] = 0xEE
    data[510:512] = b"\x55\xaa"
    if entries is None:
        entries = bytearray(1024)
        for i, ((label, kind), (start, end)) in enumerate(zip(
                autosd_disk.TYPES.items(), [(4, 11), (12, 23), (24, 35), (36, 37), (38, 76)])):
            offset = i * 128
            entries[offset:offset + 16] = uuid.UUID(kind).bytes_le
            entries[offset + 16:offset + 32] = uuid.UUID(int=i + 1).bytes_le
            struct.pack_into("<QQ", entries, offset + 32, start, end)
            name = label.encode("utf-16-le")
            entries[offset + 56:offset + 56 + len(name)] = name
    data[2 * 512:4 * 512] = entries
    data[77 * 512:79 * 512] = entries
    for lba, other, table in ((1, 79, 2), (79, 1, 77)):
        header = bytearray(512)
        header[:8] = b"EFI PART"
        struct.pack_into("<IIIIQQQQ", header, 8, 0x10000, 92, 0, 0, lba, other, 4, 76)
        header[56:72] = uuid.UUID(int=50).bytes_le
        struct.pack_into("<QIII", header, 72, table, 8, 128, zlib.crc32(entries))
        struct.pack_into("<I", header, 16, zlib.crc32(header[:92]))
        data[lba * 512:(lba + 1) * 512] = header
    data[36 * 512:37 * 512] = b"X" * 512
    return data


@pytest.fixture
def disk(tmp_path):
    path = tmp_path / "private.raw"
    path.write_bytes(disk_bytes())
    return path


@pytest.fixture
def uki(tmp_path, monkeypatch):
    path = tmp_path / "adapted.efi"
    path.write_bytes(b"test-uki" * 32)
    monkeypatch.setattr(autosd_disk, "inspect_uki", lambda path: {"kernel_sha256": "kernel-sha"})
    return path


def test_inspect_uninitialized(disk):
    result = autosd_disk.inspect_disk(disk)
    assert result["bootctl"]["state"] == "uninitialized"
    assert not result["bootctl"]["valid"]
    assert result["partitions"]["ukiboot_a"]["index"] == 2
    assert result["partitions"]["ukibootctl"]["offset"] == 36 * 512


def test_valid_control(disk):
    data = bytearray(disk.read_bytes())
    control = bytearray(24)
    struct.pack_into("<I", control, 0, 1420550408)
    control[4:8] = bytes([15, 0, 1, 0])
    control[8:12] = bytes([14, 7, 0, 0])
    struct.pack_into("<I", control, 20, zlib.crc32(control[:20]))
    data[36 * 512:36 * 512 + 24] = control
    disk.write_bytes(data)
    state = autosd_disk.inspect_disk(disk)["bootctl"]
    assert state["valid"] and state["crc_valid"]
    assert state["slots"][0]["successful_boot"] == 1


@pytest.mark.parametrize("offset", [512 + 16, 79 * 512 + 16, 1024 + 32, 77 * 512 + 32])
def test_bad_crc(disk, offset):
    data = bytearray(disk.read_bytes())
    data[offset] ^= 1
    disk.write_bytes(data)
    with pytest.raises(ValueError, match="CRC"):
        autosd_disk.inspect_disk(disk)


def test_valid_but_disagreeing_headers(disk):
    data = bytearray(disk.read_bytes())
    start = 79 * 512
    data[start + 56] ^= 1
    struct.pack_into("<I", data, start + 16, 0)
    struct.pack_into("<I", data, start + 16, zlib.crc32(data[start:start + 92]))
    disk.write_bytes(data)
    with pytest.raises(ValueError, match="disagree"):
        autosd_disk.inspect_disk(disk)


@pytest.mark.parametrize("case,message", [("overlap", "Overlapping"), ("bounds", "bounds"),
    ("label", "duplicate"), ("guid", "duplicate"), ("type", "wrong-type")])
def test_invalid_partitions(disk, case, message):
    entries = bytearray(disk_bytes()[1024:2048])
    if case == "overlap":
        struct.pack_into("<Q", entries, 128 + 32, 8)
    elif case == "bounds":
        struct.pack_into("<Q", entries, 128 + 40, 79)
    elif case == "label":
        entries[128 + 56:128 + 128] = entries[56:128]
    elif case == "guid":
        entries[128 + 16:128 + 32] = entries[16:32]
    else:
        entries[128:144] = uuid.UUID(int=123).bytes_le
    disk.write_bytes(disk_bytes(entries))
    with pytest.raises(ValueError, match=message):
        autosd_disk.inspect_disk(disk)


def test_write_slots_only(disk, uki):
    before = disk.read_bytes()
    result = autosd_disk.prepare_disk(disk, uki)
    expected = bytearray(before)
    for start in (12, 24):
        expected[start * 512:start * 512 + uki.stat().st_size] = uki.read_bytes()
    assert disk.read_bytes() == expected
    assert result["bootctl"]["state"] == "uninitialized"
    assert result["slot_image_sha256"] == hashlib.sha256(uki.read_bytes()).hexdigest()
    assert result["esp_partition"] == 1


def test_oversize_does_not_write(disk, uki):
    uki.write_bytes(b"a" * (12 * 512 + 1))
    before = disk.read_bytes()
    with pytest.raises(ValueError, match="capacity"):
        autosd_disk.prepare_disk(disk, uki)
    assert disk.read_bytes() == before


def test_partial_overrides_rejected(disk, uki):
    with pytest.raises(ValueError, match="together"):
        autosd_disk.prepare_disk(disk, uki, loader=uki)


def test_reject_disk_as_input(disk):
    with pytest.raises(ValueError, match="differ"):
        autosd_disk.prepare_disk(disk, disk)


def test_reject_missing_mtools_before_write(disk, uki, monkeypatch):
    monkeypatch.setattr(autosd_disk, "_efi_file", Path)
    monkeypatch.setattr(autosd_disk.shutil, "which", lambda name: None)
    before = disk.read_bytes()
    with pytest.raises(ValueError, match="mtools"):
        autosd_disk.prepare_disk(disk, uki, loader=uki, addon_a=uki, addon_b=uki)
    assert disk.read_bytes() == before


def test_reject_oversize_esp_inputs_before_write(disk, uki, monkeypatch):
    monkeypatch.setattr(autosd_disk, "_efi_file", Path)
    uki.write_bytes(b"x" * 2048)
    before = disk.read_bytes()
    with pytest.raises(ValueError, match="ESP capacity"):
        autosd_disk.prepare_disk(disk, uki, loader=uki, addon_a=uki, addon_b=uki)
    assert disk.read_bytes() == before


def test_reject_symlink(disk, tmp_path):
    link = tmp_path / "link.raw"
    link.symlink_to(disk)
    with pytest.raises(OSError):
        autosd_disk.inspect_disk(link)


def test_reject_nonregular():
    with pytest.raises(ValueError, match="regular file"):
        autosd_disk.inspect_disk("/dev/null")


def test_loader_override_commands(disk, uki, monkeypatch):
    monkeypatch.setattr(autosd_disk, "_efi_file", Path)
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        return type("Result", (), {"returncode": 1 if command[0] == "mdir" else 0})()

    monkeypatch.setattr(autosd_disk.subprocess, "run", run)
    result = autosd_disk.prepare_disk(disk, uki, loader=uki, addon_a=uki, addon_b=uki)
    assert len([c for c in calls if c[0] == "mcopy"]) == 3
    assert any(c[-1] == "::/EFI/BOOT/ukiboot_a.efi.extra.d/slot_a.addon.efi" for c in calls)
    assert result["bootctl"]["state"] == "uninitialized"
    assert result["efi_sources"]["loader"]["sha256"] == result["slot_image_sha256"]


def native_pe():
    data = bytearray(128)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 60, 64)
    data[64:70] = b"PE\0\0\x64\xaa"
    return data


def install_native_a(disk):
    data = bytearray(disk.read_bytes())
    data[12 * 512:12 * 512 + 128] = native_pe()
    disk.write_bytes(data)


@pytest.mark.parametrize("initialized", [False, True])
def test_native_preserves_entire_disk(disk, initialized):
    if initialized:
        test_valid_control(disk)
    install_native_a(disk)
    before = disk.read_bytes()
    result = autosd_disk.prepare_native_disk(disk)
    assert disk.read_bytes() == before
    assert result["native_slot_pe_aarch64"] == {"ukiboot_a": True, "ukiboot_b": False}
    for label in ("ukiboot_a", "ukiboot_b"):
        p = result["partitions"][label]
        assert result["native_slot_sha256"][label] == hashlib.sha256(
            before[p["offset"]:p["offset"] + p["size"]]).hexdigest()
    assert result["bootctl_partition_sha256"] == result["bootctl"]["sha256"]
    assert result["payload_policy"] == "preserve-native-slots-and-bootctl"
    assert result["efi_sources"] == {}


def test_native_overrides_only_esp(disk, tmp_path, monkeypatch):
    install_native_a(disk)
    loader = tmp_path / "loader.efi"
    loader.write_bytes(native_pe())
    before = disk.read_bytes()
    calls = []
    monkeypatch.setattr(autosd_disk.shutil, "which", lambda name: "/mock/" + name)

    def run(command, **kwargs):
        calls.append(command)
        if command[0] == "mcopy":
            with disk.open("r+b") as stream:
                stream.seek(4 * 512)
                stream.write(b"ESP override")
        return type("Result", (), {"returncode": 0})()

    monkeypatch.setattr(autosd_disk.subprocess, "run", run)
    result = autosd_disk.prepare_native_disk(disk, loader=loader, addon_a=loader, addon_b=loader)
    expected = bytearray(before)
    expected[4 * 512:4 * 512 + 12] = b"ESP override"
    assert disk.read_bytes() == expected
    assert len([c for c in calls if c[0] == "mcopy"]) == 3
    assert result["efi_sources"]["loader"]["sha256"] == hashlib.sha256(loader.read_bytes()).hexdigest()


@pytest.mark.parametrize("case", ["invalid-control", "missing-headers", "wrong-arch", "out-of-slot"])
def test_native_rejects_invalid_without_write(disk, case):
    if case != "missing-headers":
        install_native_a(disk)
    data = bytearray(disk.read_bytes())
    if case == "invalid-control":
        data[36 * 512] = 0
    elif case == "wrong-arch":
        data[12 * 512 + 68:12 * 512 + 70] = b"\x64\x86"
    elif case == "out-of-slot":
        struct.pack_into("<I", data, 12 * 512 + 60, 12 * 512)
    disk.write_bytes(data)
    with pytest.raises(ValueError):
        autosd_disk.prepare_native_disk(disk)
    assert disk.read_bytes() == data


def test_native_override_guards(disk, tmp_path, monkeypatch):
    install_native_a(disk)
    before = disk.read_bytes()
    with pytest.raises(ValueError, match="together"):
        autosd_disk.prepare_native_disk(disk, loader=disk)
    with pytest.raises(ValueError, match="differ"):
        autosd_disk.prepare_native_disk(disk, loader=disk, addon_a=disk, addon_b=disk)
    loader = tmp_path / "loader.efi"
    loader.write_bytes(native_pe())
    monkeypatch.setattr(autosd_disk.shutil, "which", lambda name: None)
    with pytest.raises(ValueError, match="mtools"):
        autosd_disk.prepare_native_disk(disk, loader=loader, addon_a=loader, addon_b=loader)
    assert disk.read_bytes() == before


def test_native_detects_unexpected_slot_write(disk, tmp_path, monkeypatch):
    install_native_a(disk)
    loader = tmp_path / "loader.efi"
    loader.write_bytes(native_pe())
    monkeypatch.setattr(autosd_disk.shutil, "which", lambda name: name)

    def corrupt(*args):
        with disk.open("r+b") as stream:
            stream.seek(24 * 512 + 200)
            stream.write(b"unexpected")

    monkeypatch.setattr(autosd_disk, "_write_esp", corrupt)
    with pytest.raises(ValueError, match="changed GPT, slots"):
        autosd_disk.prepare_native_disk(disk, loader=loader, addon_a=loader, addon_b=loader)
