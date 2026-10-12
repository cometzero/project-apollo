"""Exercise the same libfdt handoff code that runs from AP SRAM."""
import ctypes
from pathlib import Path
import shutil
import struct
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
BOOT = ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/linux-boot"
LIBFDT = ROOT / "hsoc-stack/components/primary_compute/trusted-firmware-a/lib/libfdt"


@pytest.fixture(scope="module")
def fixup(tmp_path_factory):
    if not shutil.which("cc") or not shutil.which("dtc"):
        pytest.skip("native C compiler and dtc are required")
    output = tmp_path_factory.mktemp("boot-fdt") / "fixup.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2", "-I" + str(LIBFDT),
        str(BOOT / "fdt.c"),
        *(str(LIBFDT / name) for name in
          ("fdt.c", "fdt_ro.c", "fdt_rw.c", "fdt_wip.c", "fdt_check.c")),
        "-o", str(output),
    ], check=True)
    library = ctypes.CDLL(str(output))
    function = library.boot_fixup_fdt
    function.argtypes = [ctypes.c_void_p, ctypes.c_ulong,
                         ctypes.c_uint64, ctypes.c_uint64]
    function.restype = ctypes.c_int
    return function


def make_dtb(stale=False, chosen=True):
    properties = ("linux,initrd-start = <0 0x12300000>; "
                  "linux,initrd-end = <0 0x12400000>;") if stale else ""
    node = f'chosen {{ bootargs = "console=ttyAMA0"; {properties} }};' if chosen else ""
    return subprocess.check_output(
        ["dtc", "-q", "-I", "dts", "-O", "dtb"],
        input=f'/dts-v1/; / {{ {node} test-device {{ status = "okay"; }}; }};'.encode())


def canonical(blob):
    text = subprocess.check_output(["dtc", "-q", "-s", "-I", "dtb", "-O", "dts"],
                                   input=blob).decode()
    return [line for line in text.splitlines() if "linux,initrd-" not in line]


@pytest.mark.parametrize("size", [0, 23, 4097])
@pytest.mark.parametrize("stale", [False, True])
def test_runtime_handoff_preserves_other_properties(fixup, tmp_path, size, stale):
    original = make_dtb(stale)
    buffer = ctypes.create_string_buffer(original, len(original) + 256)
    assert fixup(buffer, len(buffer), 0x90000000, size) == 0
    length = struct.unpack_from(">I", buffer.raw, 4)[0]
    updated = buffer.raw[:length]
    assert canonical(updated) == canonical(original)
    path = tmp_path / "updated.dtb"
    path.write_bytes(updated)
    for prop, value in [("linux,initrd-start", 0x90000000),
                        ("linux,initrd-end", 0x90000000 + size)]:
        result = subprocess.run(["fdtget", "-tx", str(path), "/chosen", prop],
                                capture_output=True, text=True)
        if size:
            assert result.returncode == 0
            assert [int(cell, 16) for cell in result.stdout.split()] == [0, value]
        else:
            assert result.returncode != 0


def test_runtime_handoff_rejects_bad_input(fixup):
    original = make_dtb()
    buffer = ctypes.create_string_buffer(original, len(original) + 256)
    assert fixup(buffer, 0x200001, 0, 0) < 0
    assert fixup(buffer, len(buffer), 0xffffffffffffffff, 2) < 0
    assert fixup(buffer, len(original), 0x90000000, 4096) < 0
    invalid = ctypes.create_string_buffer(b"bad header", 256)
    assert fixup(invalid, len(invalid), 0x90000000, 4096) < 0
    missing_chosen = make_dtb(chosen=False)
    buffer = ctypes.create_string_buffer(missing_chosen, len(missing_chosen) + 256)
    assert fixup(buffer, len(buffer), 0x90000000, 4096) < 0
