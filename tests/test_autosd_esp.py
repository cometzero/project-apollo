"""Fail-closed, byte-limited repair of a private AutoSD ESP."""

from pathlib import Path
import struct
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.run import autosd_esp


def fat16(dirty=True):
    data = bytearray(8192 * 512)
    struct.pack_into("<HBHBHH", data, 11, 512, 1, 1, 2, 512, 8192)
    struct.pack_into("<H", data, 22, 32)
    data[37] = int(dirty)
    data[38] = 0x29
    data[510:512] = b"\x55\xaa"
    return data


@pytest.fixture
def disks(tmp_path, monkeypatch):
    source = tmp_path / "source.raw"
    private = tmp_path / "private.raw"
    source.write_bytes(b"P" * 512 + fat16() + b"S" * 512)
    private.write_bytes(source.read_bytes())
    monkeypatch.setattr(autosd_esp.shutil, "which", lambda name: "/usr/sbin/fsck.fat")
    monkeypatch.setattr(autosd_esp, "inspect_disk", lambda path: {
        "disk_size": source.stat().st_size,
        "partitions": {"efi": {"offset": 512, "size": 8192 * 512}}})
    return source, private


def checker(monkeypatch, extra_repair=False, fail_verify=False, on_repair=None):
    calls = []

    def run(argv, **kwargs):
        calls.append(argv[1])
        image = Path(argv[2])
        data = bytearray(image.read_bytes())
        dirty = data[37] & 1
        if argv[1] == "-a":
            data[37] &= ~1
            if extra_repair:
                data[600] ^= 1
            image.write_bytes(data)
            if on_repair:
                on_repair()
        code = 1 if dirty or (fail_verify and len(calls) == 3) else 0
        return subprocess.CompletedProcess(argv, code, "checker output", "")

    monkeypatch.setattr(autosd_esp.subprocess, "run", run)
    return calls


def test_dirty_bit_only_and_source_preserved(disks, monkeypatch):
    source, private = disks
    before = source.read_bytes()
    calls = checker(monkeypatch)
    receipt = autosd_esp.check_private_esp(private)
    expected = bytearray(before)
    expected[512 + 37] &= ~1
    assert private.read_bytes() == expected
    assert source.read_bytes() == before
    assert calls == ["-n", "-a", "-n"]
    assert receipt["status"] == "dirty-bit-cleared"
    assert receipt["before_sha256"] != receipt["after_sha256"]
    assert all(c["stdout"] == "checker output" for c in receipt["commands"])


def test_clean_is_not_written(disks, monkeypatch):
    _, private = disks
    data = bytearray(private.read_bytes())
    data[512 + 37] = 0
    private.write_bytes(data)
    stat = private.stat()
    calls = checker(monkeypatch)
    receipt = autosd_esp.check_private_esp(private)
    assert calls == ["-n"]
    assert receipt["status"] == "clean"
    assert private.stat().st_mtime_ns == stat.st_mtime_ns


@pytest.mark.parametrize("extra,verify", [(True, False), (False, True)])
def test_other_corruption_never_written(disks, monkeypatch, extra, verify):
    source, private = disks
    checker(monkeypatch, extra_repair=extra, fail_verify=verify)
    with pytest.raises(ValueError):
        autosd_esp.check_private_esp(private)
    assert private.read_bytes() == source.read_bytes()


def test_out_of_bounds(disks, monkeypatch):
    source, private = disks
    monkeypatch.setattr(autosd_esp, "inspect_disk", lambda path: {
        "disk_size": 100, "partitions": {"efi": {"offset": 512, "size": 4096}}})
    with pytest.raises(ValueError, match="bounds"):
        autosd_esp.check_private_esp(private)
    assert private.read_bytes() == source.read_bytes()


def test_symlink_refused(disks, tmp_path):
    source, private = disks
    link = tmp_path / "link.raw"
    link.symlink_to(private)
    with pytest.raises(OSError):
        autosd_esp.check_private_esp(link)
    assert private.read_bytes() == source.read_bytes()


def test_concurrent_change_refused(disks, monkeypatch):
    _, private = disks
    def change():
        with private.open("r+b") as stream:
            stream.seek(512 + 700)
            stream.write(b"Z")
    checker(monkeypatch, on_repair=change)
    with pytest.raises(ValueError, match="changed"):
        autosd_esp.check_private_esp(private)
    assert private.read_bytes()[512 + 37] == 1


def test_missing_checker(disks, monkeypatch):
    monkeypatch.setattr(autosd_esp.shutil, "which", lambda name: None)
    with pytest.raises(ValueError, match="install dosfstools"):
        autosd_esp.check_private_esp(disks[1])


def test_fat32_flag_and_layout():
    boot = bytearray(512)
    struct.pack_into("<HBHBHH", boot, 11, 512, 1, 32, 2, 0, 0)
    struct.pack_into("<I", boot, 32, 70000)
    struct.pack_into("<I", boot, 36, 550)
    struct.pack_into("<I", boot, 44, 2)
    boot[66] = 0x29
    boot[510:512] = b"\x55\xaa"
    assert autosd_esp._flag_offset(boot, 70000 * 512) == (65, "FAT32")
    struct.pack_into("<I", boot, 44, 0)
    with pytest.raises(ValueError, match="layout"):
        autosd_esp._flag_offset(boot, 70000 * 512)


def test_invalid_bpb(disks):
    _, private = disks
    with private.open("r+b") as stream:
        stream.seek(512 + 13)
        stream.write(b"\x03")
    with pytest.raises(ValueError, match="BPB"):
        autosd_esp.check_private_esp(private)
