import importlib.util
import struct
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = (
    ROOT
    / "hsoc-stack/yocto/meta-hsoc-auto-solutions/recipes-bsp/"
    / "auto-ad-nexios-boot-state/files/make-auto-ad-nexios-misc.py"
)


def load_tool():
    spec = importlib.util.spec_from_file_location("auto_ad_nexios_misc", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def header_fields(blob):
    magic, version, header_size, slot, attempts, flags, generation = (
        struct.unpack_from("<8sIIBBHI", blob, 0)
    )
    crc, = struct.unpack_from("<I", blob, 0x18)
    return {
        "magic": magic,
        "version": version,
        "header_size": header_size,
        "slot": slot,
        "attempts": attempts,
        "flags": flags,
        "generation": generation,
        "crc": crc,
    }


def write_blob(path, blob):
    path.write_bytes(blob)
    return path


def test_default_slot_a_blob_header_and_size():
    misc = load_tool()
    blob = misc.build_blob()
    fields = header_fields(blob)

    assert len(blob) == 4 * 1024 * 1024
    assert fields == {
        "magic": b"AANXBOOT",
        "version": 1,
        "header_size": 64,
        "slot": 0,
        "attempts": 3,
        "flags": 0x0002,
        "generation": 0,
        "crc": misc.crc32_header(blob),
    }


def test_slot_b_generation(tmp_path):
    misc = load_tool()
    blob = misc.build_blob(slot="B")
    path = write_blob(tmp_path / "misc-b.bin", blob)

    fields = header_fields(blob)
    assert fields["slot"] == 1
    assert misc.validate_file(path)["slot"] == "B"


def test_crc_corruption_is_rejected(tmp_path):
    misc = load_tool()
    blob = bytearray(misc.build_blob())
    blob[0x11] ^= 0x01
    path = write_blob(tmp_path / "misc-corrupt.bin", blob)

    result = subprocess.run(
        [sys.executable, str(TOOL), "--validate", str(path)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "CRC mismatch" in result.stderr


def test_invalid_slot_is_rejected(tmp_path):
    misc = load_tool()
    blob = bytearray(misc.build_blob())
    blob[0x10] = 2
    struct.pack_into("<I", blob, 0x18, misc.crc32_header(blob))
    path = write_blob(tmp_path / "misc-invalid-slot.bin", blob)

    result = subprocess.run(
        [sys.executable, str(TOOL), "--validate", str(path)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "invalid slot" in result.stderr


def test_bad_magic_is_rejected(tmp_path):
    misc = load_tool()
    blob = bytearray(misc.build_blob())
    blob[0:8] = b"BADMAGIC"
    struct.pack_into("<I", blob, 0x18, misc.crc32_header(blob))
    path = write_blob(tmp_path / "misc-bad-magic.bin", blob)

    result = subprocess.run(
        [sys.executable, str(TOOL), "--validate", str(path)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "invalid magic" in result.stderr


def test_wrong_version_is_rejected(tmp_path):
    misc = load_tool()
    blob = bytearray(misc.build_blob())
    struct.pack_into("<I", blob, 0x08, 2)
    struct.pack_into("<I", blob, 0x18, misc.crc32_header(blob))
    path = write_blob(tmp_path / "misc-wrong-version.bin", blob)

    result = subprocess.run(
        [sys.executable, str(TOOL), "--validate", str(path)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "unsupported version" in result.stderr


def test_reserved_area_is_zero_filled():
    misc = load_tool()
    blob = misc.build_blob()

    assert blob[0x1C:] == b"\x00" * (len(blob) - 0x1C)


def test_truncated_blob_is_rejected(tmp_path):
    misc = load_tool()
    path = write_blob(tmp_path / "misc-short.bin", misc.build_blob()[:-1])

    result = subprocess.run(
        [sys.executable, str(TOOL), "--validate", str(path)],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "blob size mismatch" in result.stderr
