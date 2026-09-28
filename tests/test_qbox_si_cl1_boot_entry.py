"""ELF-derived SI1 RVBAR and binary matching; no VM or external tools."""
import argparse
import binascii
import struct

import pytest

from scripts.run import run_qbox_apollo_fvp_full as runner


BASE = 0x140000000


@pytest.fixture
def inputs(tmp_path):
    elf = bytearray(0x400)
    elf[:7] = b"\x7fELF\x02\x01\x01"
    struct.pack_into("<HHIQQQIHHHHHH", elf, 16,
                     2, 183, 1, BASE + 4, 64, 0x200, 0, 64, 56, 1, 64, 3, 2)
    struct.pack_into("<IIQQQQQQ", elf, 64, 1, 5, 0x100, BASE, BASE, 8, 16, 4)
    elf[0x100:0x108] = b"ABCDEFGH"
    names = b"\0.text\0.shstrtab\0"
    elf[0x340:0x340 + len(names)] = names
    struct.pack_into("<IIQQQQIIQQ", elf, 0x240, 1, 1, 6, BASE, 0x100, 8, 0, 0, 4, 0)
    struct.pack_into("<IIQQQQIIQQ", elf, 0x280, 7, 3, 0, 0, 0x340, len(names), 0, 0, 1, 0)
    ep, bp = tmp_path / "si.elf", tmp_path / "si.bin"
    ep.write_bytes(elf)
    bp.write_bytes(b"ABCDEFGH")
    return argparse.Namespace(platform_param=[], build_only=False), {
        "si_cl1_symbols": ep, "si_cl1_image": bp}


def test_all_four_entry_defaults_and_evidence(inputs):
    args, artifacts = inputs
    assert runner.prepare_si_cl1_boot(args, artifacts) is None
    assert args.si_cl1_boot["entry"] == hex(BASE + 4)
    assert len(args.si_cl1_boot["elf_sha256"]) == 64
    params = runner.full_system_platform_params(args)
    for cpu in range(4):
        assert f"platform.si_cl1_cpu_{cpu}.rvbar={hex(BASE + 4)}" in params


def test_explicit_override_preserved(inputs):
    args, artifacts = inputs
    explicit = f"platform.si_cl1_cpu_2.rvbar={hex(BASE)}"
    args.platform_param = [explicit]
    assert runner.prepare_si_cl1_boot(args, artifacts) is None
    params = runner.full_system_platform_params(args)
    assert [p for p in params if p.startswith("platform.si_cl1_cpu_2.rvbar=")] == [explicit]
    assert args.si_cl1_boot["cpus"]["platform.si_cl1_cpu_2.rvbar"]["source"] == "explicit"


@pytest.mark.parametrize("offset,fmt,value", [
    (4, "B", 1), (18, "H", 40), (24, "Q", BASE + 1),
    (24, "Q", BASE + 12), (32, "Q", 2**64 - 1),
    (64 + 8, "Q", 2**64 - 1), (64 + 32, "Q", 2**64 - 1),
    (40, "Q", 2**64 - 1), (0x240 + 24, "Q", 2**64 - 1),
])
def test_malformed_elf_blocks(inputs, offset, fmt, value):
    args, artifacts = inputs
    data = bytearray(artifacts["si_cl1_symbols"].read_bytes())
    struct.pack_into("<" + fmt, data, offset, value)
    artifacts["si_cl1_symbols"].write_bytes(data)
    assert runner.prepare_si_cl1_boot(args, artifacts).startswith("si_cl1_boot_invalid:")
    assert args.si_cl1_boot["status"] == "BLOCKED"


def test_stale_binary_blocks(inputs):
    args, artifacts = inputs
    artifacts["si_cl1_image"].write_bytes(b"staleBIN")
    assert "do not match" in runner.prepare_si_cl1_boot(args, artifacts)


def test_invalid_explicit_override_blocks(inputs):
    args, artifacts = inputs
    args.platform_param = ["platform.si_cl1_cpu_0.rvbar=1"]
    assert runner.prepare_si_cl1_boot(args, artifacts)


def test_build_only_does_not_require_elf(inputs):
    args, artifacts = inputs
    args.build_only = True
    artifacts["si_cl1_symbols"].unlink()
    assert runner.prepare_si_cl1_boot(args, artifacts) is None
    assert args.si_cl1_boot["status"] == "SKIP"


def add_postbuild_crc_fixture(artifacts):
    """Model objcopy padding and Zephyr's binary-only final CRC patch."""
    elf = bytearray(artifacts["si_cl1_symbols"].read_bytes())
    names = b"\0.text\0.shstrtab\0.image_crc\0"
    elf[0x340:0x340 + len(names)] = names
    struct.pack_into("<H", elf, 60, 4)  # e_shnum
    struct.pack_into("<Q", elf, 64 + 32, 64)  # PT_LOAD p_filesz
    struct.pack_into("<Q", elf, 64 + 40, 64)  # PT_LOAD p_memsz
    struct.pack_into("<Q", elf, 0x280 + 32, len(names))  # shstrtab size
    struct.pack_into("<IIQQQQIIQQ", elf, 0x2c0,
                     17, 1, 3, BASE + 60, 0x13c, 4, 0, 0, 4, 0)
    # The .text bytes match, while unowned segment padding deliberately differs.
    binary = bytearray(b"ABCDEFGH" + b"\xff" * 56)
    binary[-4:] = binascii.crc32(binary[:-52]).to_bytes(4, "little")
    artifacts["si_cl1_symbols"].write_bytes(elf)
    artifacts["si_cl1_image"].write_bytes(binary)


def test_postbuild_crc_and_objcopy_padding_are_verified(inputs):
    args, artifacts = inputs
    add_postbuild_crc_fixture(artifacts)
    assert runner.prepare_si_cl1_boot(args, artifacts) is None
    assert args.si_cl1_boot["image_crc_verified"] is True
    assert args.si_cl1_boot["load_sections_verified"] == 2


def test_invalid_postbuild_crc_blocks(inputs):
    args, artifacts = inputs
    add_postbuild_crc_fixture(artifacts)
    binary = bytearray(artifacts["si_cl1_image"].read_bytes())
    binary[-1] ^= 1
    artifacts["si_cl1_image"].write_bytes(binary)
    assert "post-build image CRC" in runner.prepare_si_cl1_boot(args, artifacts)
    assert args.si_cl1_boot["status"] == "BLOCKED"


def test_crc_section_must_be_final_four_bytes(inputs):
    args, artifacts = inputs
    add_postbuild_crc_fixture(artifacts)
    elf = bytearray(artifacts["si_cl1_symbols"].read_bytes())
    struct.pack_into("<Q", elf, 0x2c0 + 16, BASE + 56)
    artifacts["si_cl1_symbols"].write_bytes(elf)
    assert "post-build image CRC" in runner.prepare_si_cl1_boot(args, artifacts)
    assert args.si_cl1_boot["status"] == "BLOCKED"
