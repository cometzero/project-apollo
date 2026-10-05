"""Optional vMCU boot argument must preserve unsigned BSP payloads and defaults."""

import hashlib
from pathlib import Path
import struct
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/run"))
import qbox_vmcu_boot as boot
from autosd_uki import inspect_uki


def make_uki(path, cmdline=b"rdinit=/init rw console=ttyAMA0\0"):
    sections = [(".text", b"stub"), (".linux", b"kernel"), (".initrd", b"initrd"),
                (".cmdline", cmdline), (".dtb", b"device-tree")]
    data = bytearray(1024 + len(sections) * 512)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 60, 128)
    data[128:132] = b"PE\0\0"
    struct.pack_into("<HHIIIHH", data, 132, 0xaa64, len(sections), 0, 0, 0, 240, 0x2022)
    optional = 152
    struct.pack_into("<H", data, optional, 0x20b)
    struct.pack_into("<Q", data, optional + 24, 0x140000000)
    struct.pack_into("<II", data, optional + 32, 4096, 512)
    struct.pack_into("<II", data, optional + 56, 6 * 4096, 1024)
    struct.pack_into("<I", data, optional + 108, 16)
    for index, (name, payload) in enumerate(sections):
        header = optional + 240 + index * 40
        data[header:header + 8] = name.encode().ljust(8, b"\0")
        struct.pack_into("<IIII", data, header + 8, len(payload),
                         (index + 1) * 4096, 512, 1024 + index * 512)
        data[1024 + index * 512:1024 + index * 512 + len(payload)] = payload
    path.write_bytes(data)
    return path


def test_add_bootarg_preserves_payloads_and_source(tmp_path):
    source = make_uki(tmp_path / "source.efi")
    original = source.read_bytes()
    before = inspect_uki(source)
    target = tmp_path / "target.efi"
    result = boot.patch_bsp_uki(source, target)
    after = inspect_uki(target)
    assert source.read_bytes() == original
    assert target.stat().st_size == len(original)
    assert result["new_bootargs"] == "rdinit=/init rw console=ttyAMA0 apollo.vmcu=1"
    assert result["source_sha256"] == hashlib.sha256(original).hexdigest()
    assert after["sections"][".cmdline"]["raw_size"] == 512
    for name in (".text", ".linux", ".initrd", ".dtb"):
        assert after["sections"][name] == before["sections"][name]


def test_idempotent_bootarg_and_conflicting_values(tmp_path):
    source = make_uki(tmp_path / "source.efi", b"rdinit=/init apollo.vmcu=0 apollo.vmcu=1\0")
    target = tmp_path / "target.efi"
    first = boot.patch_bsp_uki(source, target)
    second = boot.patch_bsp_uki(target, tmp_path / "twice.efi")
    assert first["new_bootargs"] == "rdinit=/init apollo.vmcu=1"
    assert first["sha256"] == second["sha256"]


@pytest.mark.parametrize("cmdline,reason", [
    (b"root=PARTLABEL=rootro_a console=ttyAMA0\0", "BSP"),
    (b"rdinit=/init\0hidden\0", "BSP"),
    (b"rdinit=/init\nconsole=ttyAMA0\0", "BSP"),
    (b"rdinit=/init " + b"x" * 491 + b"\0", "padding"),
])
def test_reject_wrong_image_or_insufficient_padding(tmp_path, cmdline, reason):
    source = make_uki(tmp_path / "source.efi", cmdline)
    with pytest.raises(ValueError, match=reason):
        boot.patch_bsp_uki(source, tmp_path / "target.efi")


def test_reject_signed_uki(tmp_path):
    source = make_uki(tmp_path / "source.efi")
    data = bytearray(source.read_bytes())
    struct.pack_into("<I", data, 152 + 144, 1024)
    source.write_bytes(data)
    with pytest.raises(ValueError, match="Signed"):
        boot.patch_bsp_uki(source, tmp_path / "target.efi")


def test_reject_occupied_padding(tmp_path):
    source = make_uki(tmp_path / "source.efi")
    data = bytearray(source.read_bytes())
    data[1024 + 3 * 512 + 511] = 1
    source.write_bytes(data)
    with pytest.raises(ValueError, match="nonzero"):
        boot.patch_bsp_uki(source, tmp_path / "target.efi")


def test_reject_overwrite_source(tmp_path):
    source = make_uki(tmp_path / "source.efi")
    with pytest.raises(ValueError, match="differ"):
        boot.patch_bsp_uki(source, source)


@pytest.mark.parametrize("enabled,filename,state", [
    (False, "nexios-bsp-initramfs-apollo-qvp.wic", "disabled"),
    (True, "nexios-image-apollo-qvp.wic", "skipped_non_bsp_image"),
    (True, "baremetal-image-fvp-rd-aspen.wic", "skipped_non_bsp_image"),
])
def test_disabled_and_other_products_are_not_accessed(tmp_path, enabled, filename, state):
    def forbidden(*args):
        pytest.fail("Image access is forbidden on this path")
    source = tmp_path / filename  # Deliberately does not exist.
    actual, info = boot.prepare_vmcu_rootfs(source, tmp_path, enabled=enabled,
                                          copy_image=forbidden, image_location=forbidden)
    assert actual == source and not info["changed"] and info["state"] == state
