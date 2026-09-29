"""Portable AIB builder input, isolation and evidence contracts."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def launcher():
    path = Path(__file__).resolve().parents[1] / "scripts/autosd_demo/builder_launch.py"
    spec = importlib.util.spec_from_file_location("builder_launch", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def inputs(tmp_path):
    paths = {}
    for name in ("rootfs", "initrd", "kernel", "qemu"):
        paths[name] = tmp_path / name
        paths[name].write_bytes(name.encode())
    manifest = tmp_path / "regular.json"
    manifest.write_text(json.dumps({"mode": "regular", "rootfs": str(paths["rootfs"]),
                                   "initrd": str(paths["initrd"]),
                                   "bootargs": "root=UUID=test console=ttyAMA0 slub_debug=FPZ rcupdate.rcu_expedited=1 rcupdate.rcu_normal_after_boot=0"}))
    return ["--manifest", str(manifest), "--kernel", str(paths["kernel"]),
            "--qemu", str(paths["qemu"]), "--work-dir", str(tmp_path / "output")]


def test_dry_run_is_nonmutating(launcher, inputs, tmp_path, capsys):
    assert launcher.main(inputs + ["--dry-run", "--ssh-port", "2236"]) == 0
    plan = json.loads(capsys.readouterr().out)
    command = plan["command"]
    assert not (tmp_path / "output").exists()
    assert "user,id=net0,hostfwd=tcp:127.0.0.1:2236-:22" in command
    assert "virtio-blk-device,drive=scratch,bus=virtio-mmio-bus.2" in command
    assert "@MONITOR_FD@" not in str(command)
    assert "slub_debug" not in str(command)
    assert "rcupdate.rcu_expedited" not in str(command)
    assert command[command.index("-append") + 1] == "root=UUID=test console=ttyAMA0"


def test_refuse_existing_output(launcher, inputs, tmp_path):
    (tmp_path / "output").mkdir()
    evidence = tmp_path / "output/uart.log"
    evidence.write_text("preserve")
    with pytest.raises(SystemExit, match="already exists"):
        launcher.main(inputs)
    assert evidence.read_text() == "preserve"


def test_rootfs_override(launcher, inputs, tmp_path):
    disk = tmp_path / "custom.raw"
    disk.touch()
    plan = launcher.make_plan(launcher.parser().parse_args(inputs + ["--rootfs", str(disk)]))
    assert plan["source_rootfs"] == str(disk)


def test_custom_build_and_deploy_defaults(launcher, inputs, tmp_path):
    build = tmp_path / "custom-build"
    deploy = tmp_path / "custom-deploy"
    (build / "autosd").mkdir(parents=True)
    deploy.mkdir()
    (build / "autosd/regular.json").write_text((tmp_path / "regular.json").read_text())
    (deploy / "Image").write_bytes(b"deploy-kernel")
    provider = build / "tmp_baremetal/deploy/qemu-apollo-native"
    provider.mkdir(parents=True)
    (provider / "qemu-apollo-native.json").write_text(json.dumps({
        "executable": str(tmp_path / "qemu"), "library_path": ["/custom/lib"]}))
    args = launcher.parser().parse_args(["--build-dir", str(build), "--deploy-dir", str(deploy),
                                        "--work-dir", str(tmp_path / "output")])
    plan = launcher.make_plan(args)
    assert plan["manifest"] == str(build / "autosd/regular.json")
    assert plan["kernel"] == str(deploy / "Image")
    assert plan["environment"]["LD_LIBRARY_PATH"] == "/custom/lib"
    assert plan["provider"] == str(provider / "qemu-apollo-native.json")


@pytest.mark.parametrize("port", [0, 65536, -1])
def test_invalid_port(launcher, inputs, port):
    with pytest.raises(SystemExit, match="SSH port"):
        launcher.main(inputs + ["--ssh-port", str(port)])


def test_reject_live_source_by_fd(launcher, tmp_path):
    source = tmp_path / "source.raw"
    source.touch()
    process = tmp_path / "proc/123"
    (process / "fd").mkdir(parents=True)
    (process / "cmdline").write_bytes(b"qemu-system-aarch64\0-drive\0file=alias.raw")
    (process / "fd/4").symlink_to(source)
    with pytest.raises(ValueError, match="Source VM is running"):
        launcher.assert_source_inactive(source, tmp_path / "proc")


def test_capacity_check_before_writes(launcher, inputs, tmp_path, monkeypatch):
    monkeypatch.setattr(launcher.shutil, "disk_usage", lambda path: SimpleNamespace(free=31 * 1024**3))
    with pytest.raises(SystemExit, match="32 GiB"):
        launcher.main(inputs)
    assert not (tmp_path / "output").exists()


def test_launch_records_environment_and_private_inputs(launcher, inputs, tmp_path, monkeypatch):
    monkeypatch.setattr(launcher.shutil, "disk_usage", lambda path: SimpleNamespace(free=33 * 1024**3))
    class Socket:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def bind(self, address):
            assert address == ("127.0.0.1", 2226)

    monkeypatch.setattr(launcher.socket, "socket", Socket)
    monkeypatch.setattr(launcher.subprocess, "run", lambda cmd, **kw: launcher.shutil.copyfile(cmd[-2], cmd[-1]))
    monkeypatch.setattr(launcher.subprocess, "Popen", lambda *a, **kw: SimpleNamespace(pid=12345, wait=lambda: 0))
    assert launcher.main(inputs) == 0
    output = tmp_path / "output"
    assert (output / "rootfs.wic").read_bytes() == b"rootfs"
    assert (output / "scratch.raw").stat().st_size == 24 * 1024**3
    assert (output / "qemu.pid").read_text() == "12345\n"
    plan = json.loads((output / "launch.json").read_text())
    assert "environment" in plan
    assert len(plan["kernel_sha256"]) == 64
    assert (output / "uart.log").exists()
