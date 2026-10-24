"""ELF loading and bounded guest evidence for standalone QBox Zephyr."""
import importlib.util
import json
from pathlib import Path
import struct
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/run"))
spec = importlib.util.spec_from_file_location("qbox_zephyr", ROOT / "scripts/run/run_qbox_zephyr.py")
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


def elf_bytes(base=launcher.BASE):
    data = bytearray(132)
    data[:6] = b"\x7fELF\x02\x01"
    struct.pack_into("<H", data, 18, 183)
    struct.pack_into("<QQ", data, 24, base, 64)
    struct.pack_into("<HH", data, 54, 56, 1)
    struct.pack_into("<IIQQQQQQ", data, 64, 1, 5, 128, base, base, 4, 8, 4)
    data[128:] = b"test"
    return data


def test_elf_loads_entry_and_segment(tmp_path):
    path = tmp_path / "image.elf"
    path.write_bytes(elf_bytes())
    assert launcher.elf_payload(path) == (launcher.BASE, b"test")


@pytest.mark.parametrize("image", [b"bad", elf_bytes(0x40000000), elf_bytes()[:130]])
def test_reject_invalid_elf(tmp_path, image):
    path = tmp_path / "image.elf"
    path.write_bytes(image)
    with pytest.raises(ValueError):
        launcher.elf_payload(path)


def test_supervisor_requires_guest_marker(tmp_path):
    (tmp_path / "zephyr-uart.log").touch()
    (tmp_path / "run.json").write_text(json.dumps({"command": [sys.executable, "-c", "pass"], "environment": {}}))
    assert launcher.supervise(tmp_path, 2, True) == 1
    assert json.loads((tmp_path / "result.json").read_text())["boot_marker_observed"] is False


def test_supervisor_observes_uart_and_reaps_child(tmp_path):
    uart = tmp_path / "zephyr-uart.log"
    uart.touch()
    markers = b"".join(f"SI_CL1_BOOT_CPU cpu={i}\n".encode() for i in range(4)) + launcher.BOOT_MARKER
    code = f"from pathlib import Path; import time; Path({str(uart)!r}).write_bytes({markers!r}); time.sleep(30)"
    (tmp_path / "run.json").write_text(json.dumps({"command": [sys.executable, "-c", code], "environment": {}}))
    assert launcher.supervise(tmp_path, 2, True) == 0
    result = json.loads((tmp_path / "result.json").read_text())
    assert result["boot_marker_observed"] is True
    assert result["qbox_returncode"] is not None


def test_boot_marker_requires_all_cpus():
    assert not launcher.boot_complete(launcher.BOOT_MARKER)
    assert not launcher.boot_complete(b"SI_CL1_BOOT_CPU cpu=0\n" * 4 + launcher.BOOT_MARKER)


@pytest.mark.parametrize("timeout", ["nan", "inf", "-inf", "-1"])
def test_invalid_timeout_rejected_before_artifact_lookup(monkeypatch, timeout):
    monkeypatch.setattr(sys, "argv", ["run_qbox_zephyr.py", "--timeout=" + timeout])
    with pytest.raises(SystemExit) as error:
        launcher.main()
    assert error.value.code == 2
