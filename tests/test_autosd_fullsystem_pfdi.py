"""PFDI artifact selection and startup contracts, without guest execution."""
import importlib.util
from pathlib import Path
import subprocess

import pytest

SOURCE = Path(__file__).resolve().parents[1] / "scripts/run/autosd_fullsystem_pfdi.py"
spec = importlib.util.spec_from_file_location("full_pfdi", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def artifacts(tmp_path):
    root = tmp_path / "tmp_baremetal/work"
    image = root / "cortexa720-poky-linux/platform-fault-detection/1.0/image"
    elf = b"\x7fELF\x02\x01" + bytes(12) + b"\xb7\x00"
    for name in ("usr/bin/pfdi-sample-app", "usr/bin/pfdi-cli", "usr/lib/libpfdi.so.1", "etc/pfdi/pfdi_test_config_0.pack"):
        path = image / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(elf)
    path = root / "apollo_qvp-poky-linux/pfdi-misc-mod/1.0/image/usr/lib/modules/test-rt/updates/pfdi_misc.ko"
    path.parent.mkdir(parents=True)
    path.write_bytes(elf)
    return image, path


def test_inputs_reject_missing_payload(tmp_path):
    with pytest.raises(ValueError, match="Expected one"):
        module.pfdi_inputs(tmp_path)


def test_inputs_record_signed_module_release_and_payload_hashes(tmp_path, monkeypatch):
    artifacts(tmp_path)
    monkeypatch.setattr(module.subprocess, "check_output", lambda *a, **k: "test-rt SMP preempt_rt aarch64")
    inputs = module.pfdi_inputs(tmp_path)
    assert len(inputs) == 5
    assert inputs["pfdi_misc.ko"]["release"] == "test-rt"
    assert inputs["libpfdi.so.1"]["target"] == "/usr/lib64/libpfdi.so.1"
    assert all(len(value["sha256"]) == 64 for value in inputs.values())


def test_inputs_reject_other_architecture(tmp_path, monkeypatch):
    image, _ = artifacts(tmp_path)
    (image / "usr/bin/pfdi-cli").write_bytes(b"not arm executable")
    monkeypatch.setattr(module.subprocess, "check_output", lambda *a, **k: "test-rt SMP")
    with pytest.raises(ValueError, match="AArch64"):
        module.pfdi_inputs(tmp_path)


def test_inputs_reject_release_mismatch(tmp_path, monkeypatch):
    artifacts(tmp_path)
    monkeypatch.setattr(module.subprocess, "check_output", lambda *a, **k: "wrong-release SMP")
    with pytest.raises(ValueError, match="disagree"):
        module.pfdi_inputs(tmp_path)


def test_service_only_full_system_and_real_calls_verified():
    assert "ConditionKernelCommandLine=apollo.fullsystem=1" in module.SERVICE
    assert "pfdi_misc pfdi_wait_timeout_ms=1000" in module.SERVICE
    assert "ExecStartPre=/usr/libexec/apollo-pfdi-check" in module.SERVICE
    assert "Restart=on-failure" in module.SERVICE
    assert "Before=multi-user.target" in module.SERVICE
    assert "-m single" in module.CHECK
    assert "for cpu in 0 1 2 3" in module.CHECK
    assert "PFDI Online" in module.CHECK and " OK" in module.CHECK
    assert "failed" in module.CHECK
    subprocess.run(["sh", "-n"], input=module.CHECK, text=True, check=True)


def test_install_does_not_start_smc_on_ap_only_and_preserves_failure(tmp_path, monkeypatch):
    artifacts(tmp_path)
    monkeypatch.setattr(module.subprocess, "check_output", lambda *a, **k: "test-rt SMP")
    commands = module.install_commands(module.pfdi_inputs(tmp_path), "/var/tmp/owned")
    command = "; ".join(commands)
    for required in ("uname -r", "sha256sum -c", "restorecon", "--list /usr/bin/pfdi-sample-app", "systemctl restart"):
        assert required in command
    assert "grep -qw apollo.fullsystem=1 /proc/cmdline" in command
    assert "modules-load.d" not in command
    assert "|| true" not in command
    assert "rm " not in command
    subprocess.run(["sh", "-n"], input=command, text=True, check=True)
    prepared = "; ".join(module.install_commands(module.pfdi_inputs(tmp_path), "/var/tmp/owned", prepare_only=True))
    assert "INSTALLED_NOT_STARTED" in prepared
    assert "systemctl restart" not in prepared
    assert "systemctl enable" in prepared
