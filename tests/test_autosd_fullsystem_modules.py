"""Private guest module deployment contracts, without host or guest writes."""
import importlib.util
import json
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[1] / "scripts/run/autosd_fullsystem_modules.py"
spec = importlib.util.spec_from_file_location("full_modules", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture_modules(tmp_path, releases=("test-rt", "test-rt")):
    for (name, recipe), release in zip(module.MODULES.items(), releases):
        path = tmp_path / f"tmp_baremetal/work/apollo_qvp-poky-linux/{recipe}/1.0/image/usr/lib/modules/{release}/updates/{name}.ko"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"trusted-test-module")


def test_inputs_require_both_unambiguous_builds(tmp_path):
    with pytest.raises(ValueError, match="Expected one built"):
        module.module_inputs(tmp_path)


def test_inputs_record_actual_hash_and_vermagic(tmp_path, monkeypatch):
    fixture_modules(tmp_path)
    monkeypatch.setattr(module.subprocess, "check_output", lambda *a, **k: "test-rt SMP preempt_rt aarch64")
    modules = module.module_inputs(tmp_path)
    assert len(modules) == 2
    assert all(len(item["sha256"]) == 64 for item in modules.values())
    assert all(item["release"] == "test-rt" for item in modules.values())


def test_mixed_module_vermagic_rejected(tmp_path, monkeypatch):
    fixture_modules(tmp_path, ("one", "two"))
    monkeypatch.setattr(module.subprocess, "check_output", lambda args, **k: Path(args[-1]).parent.parent.name + " SMP aarch64")
    with pytest.raises(ValueError, match="different kernels"):
        module.module_inputs(tmp_path)


def test_module_path_must_match_vermagic(tmp_path, monkeypatch):
    fixture_modules(tmp_path)
    monkeypatch.setattr(module.subprocess, "check_output", lambda *a, **k: "other-release SMP")
    with pytest.raises(ValueError, match="disagree"):
        module.module_inputs(tmp_path)


def test_install_is_guarded_and_preserves_usr_merge(tmp_path, monkeypatch):
    fixture_modules(tmp_path)
    monkeypatch.setattr(module.subprocess, "check_output", lambda *a, **k: "test-rt SMP")
    command = module.install_command(module.module_inputs(tmp_path), "/var/tmp/owned")
    for required in ('uname -r', 'test "$ID" = autosd', "sha256sum -c", "restorecon", "depmod", "modprobe virtio_rpmsg_bus", "modprobe arm_si_rproc", "modprobe rpmsg_net"):
        assert required in command
    assert "/usr/lib/modules/test-rt/updates" in command
    assert "apollo-fullsystem.conf" in command
    assert "timeout -k 5s 120s" in command
    assert "rm " not in command


def test_failure_persists_evidence_without_ssh(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "module_inputs", lambda _: (_ for _ in ()).throw(ValueError("missing artifact")))
    monkeypatch.setattr(module.paramiko, "SSHClient", lambda: pytest.fail("must not connect"))
    result = module.provision(2244, tmp_path, tmp_path)
    assert result["status"] == "FAIL"
    assert json.loads((tmp_path / "modules.json").read_text())["error"] == "missing artifact"


def test_endpoint_gate_and_prepare_only(tmp_path, monkeypatch):
    import subprocess
    fixture_modules(tmp_path)
    monkeypatch.setattr(module.subprocess, "check_output", lambda *a, **k: "test-rt SMP")
    modules = module.module_inputs(tmp_path)
    normal = module.install_command(modules, "/var/tmp/owned")
    prepared = module.install_command(modules, "/var/tmp/owned", prepare_only=True)
    assert "HIPC_NETDEV_NOT_READY" in normal
    assert "HIPC_NETDEV_NOT_READY" not in prepared
    gate = module.endpoint_ready_command()
    assert '/sys/class/net/ethsi1/ifindex' in gate
    assert '/sys/bus/rpmsg/devices/*' in gate
    assert 'rpmsg_netdev' in gate
    assert '"$attempts" -lt 30' in gate
    assert 'ethsi1/device/driver' not in gate
    assert 'ip link' not in gate
    subprocess.run(["sh", "-n"], input=gate, text=True, check=True)


@pytest.mark.parametrize("state", ["absent", "wrong-driver", "healthy"])
def test_endpoint_gate_executes_fail_closed(tmp_path, state):
    import subprocess
    sysroot = tmp_path / "sys"
    if state != "absent":
        netdev = sysroot / "class/net/ethsi1"
        netdev.mkdir(parents=True)
        (netdev / "ifindex").write_text("4\n")
        endpoint = sysroot / "bus/rpmsg/devices/virtio0.ethsi1.-1.1024"
        endpoint.mkdir(parents=True)
        (endpoint / "name").write_text("ethsi1\n")
        (endpoint / "driver").symlink_to("/drivers/" + ("rpmsg_netdev" if state == "healthy" else "wrong"))
    gate = module.endpoint_ready_command().replace("/sys/", str(sysroot) + "/")
    result = subprocess.run(["sh", "-c", "set -eu; sleep() { :; }; " + gate],
                            text=True, capture_output=True, timeout=5)
    assert (result.returncode == 0) == (state == "healthy")
    if state == "healthy":
        assert "HIPC_ENDPOINT_READY" in result.stdout
    else:
        assert "HIPC_NETDEV_NOT_READY" in result.stderr


@pytest.mark.parametrize("port", [22, -1, 65536])
def test_invalid_private_port(tmp_path, port):
    assert module.provision(port, tmp_path, tmp_path)["status"] == "FAIL"
