"""Integrated image selection and bounded guest evidence for QBox Zephyr."""
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/run"))
spec = importlib.util.spec_from_file_location("qbox_zephyr", ROOT / "scripts/run/run_qbox_zephyr.py")
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


def boot_output():
    return (b"".join(f"Out of Reset (OoR) completed on CPU: {i}\n".encode()
                     for i in range(4)) + launcher.BOOT_MARKER + b"\n" + launcher.SHELL_PROMPT)


def test_dry_run_uses_integrated_binary_without_repacking(tmp_path, monkeypatch, capsys):
    elf = tmp_path / "zephyr-demos-cl1.elf"
    image = elf.with_suffix(".bin")
    conf = tmp_path / "nexios-bsp-initramfs-apollo-qvp.qboxconf"
    for path in (elf, image, conf):
        path.write_bytes(b"fixture")
    calls = []
    def validate(args, artifacts):
        calls.append(artifacts)
        return {"entry": "0x140000004", "image_crc_verified": True}
    monkeypatch.setattr(launcher, "si_cl1_boot_config", validate)
    monkeypatch.setattr(launcher, "provider_environment", lambda *args: {
        "QBOXCONF_EXE": sys.executable, "QBOXCONF_LD_LIBRARY_PATH": ""})
    out = tmp_path / "run"
    monkeypatch.setattr(sys, "argv", ["run_qbox_zephyr.py", "--dry-run",
        "--deploy-dir", str(tmp_path), "--out-dir", str(out)])
    assert launcher.main() == 0
    plan = json.loads(capsys.readouterr().out)
    assert calls == [{"si_cl1_symbols": elf, "si_cl1_image": image}]
    assert plan["environment"]["QBOX_APOLLO_FULL_SI_CL1_IMAGE"] == str(image)
    assert plan["environment"]["QBOX_ZEPHYR_ENTRY"] == str(0x140000004)
    assert image.read_bytes() == b"fixture"
    assert not out.exists()


def test_invalid_integrated_elf_rejected_before_provider(tmp_path, monkeypatch):
    elf = tmp_path / "custom.elf"
    elf.write_bytes(b"bad")
    elf.with_suffix(".bin").write_bytes(b"bad")
    monkeypatch.setattr(sys, "argv", ["run_qbox_zephyr.py", "--elf", str(elf), "--dry-run"])
    with pytest.raises(ValueError, match="ELF64"):
        launcher.main()


def test_supervisor_requires_guest_marker(tmp_path):
    (tmp_path / "zephyr-uart.log").touch()
    (tmp_path / "run.json").write_text(json.dumps({"command": [sys.executable, "-c", "pass"], "environment": {}}))
    assert launcher.supervise(tmp_path, 2, True) == 1
    assert json.loads((tmp_path / "result.json").read_text())["boot_marker_observed"] is False


def test_supervisor_observes_uart_and_reaps_child(tmp_path):
    uart = tmp_path / "zephyr-uart.log"
    uart.touch()
    markers = boot_output()
    code = f"from pathlib import Path; import time; Path({str(uart)!r}).write_bytes({markers!r}); time.sleep(30)"
    (tmp_path / "run.json").write_text(json.dumps({"command": [sys.executable, "-c", code], "environment": {}}))
    assert launcher.supervise(tmp_path, 2, True) == 0
    result = json.loads((tmp_path / "result.json").read_text())
    assert result["boot_marker_observed"] is True
    assert result["qbox_returncode"] is not None


def test_boot_marker_requires_all_cpus():
    assert not launcher.boot_complete(launcher.BOOT_MARKER)
    assert not launcher.boot_complete(boot_output().replace(b"CPU: 3", b"CPU: 0"))
    assert not launcher.boot_complete(boot_output().replace(launcher.SHELL_PROMPT, b""))
    assert launcher.boot_complete(boot_output().replace(b"uart:", b"\x1b[32muart:"))


@pytest.mark.parametrize("timeout", ["nan", "inf", "-inf", "-1"])
def test_invalid_timeout_rejected_before_artifact_lookup(monkeypatch, timeout):
    monkeypatch.setattr(sys, "argv", ["run_qbox_zephyr.py", "--timeout=" + timeout])
    with pytest.raises(SystemExit) as error:
        launcher.main()
    assert error.value.code == 2


def test_fatal_after_prompt_is_failure(tmp_path):
    (tmp_path / "zephyr-uart.log").write_bytes(boot_output() + b"\nZEPHYR FATAL ERROR")
    (tmp_path / "run.json").write_text(json.dumps({
        "command": [sys.executable, "-c", "import time; time.sleep(30)"], "environment": {}}))
    assert launcher.supervise(tmp_path, 2, True) == 1
    assert json.loads((tmp_path / "result.json").read_text())["status"] == "FAIL"
