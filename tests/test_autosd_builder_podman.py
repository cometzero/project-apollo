"""Host builder privilege, isolation, archive and failure contracts."""
import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def module(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts/autosd_demo"))
    return importlib.import_module("builder_podman")


@pytest.mark.parametrize("rootless,code", [("true", 0), ("", 1)])
def test_preflight_rejects_rootless_or_missing_sudo(module, monkeypatch, rootless, code):
    monkeypatch.setattr(module.subprocess, "run", lambda *a, **k:
                        SimpleNamespace(returncode=code, stdout=rootless, stderr="denied"))
    with pytest.raises(RuntimeError, match="Rootful Podman"):
        module.preflight()


@pytest.mark.parametrize("fail", [False, True])
@pytest.mark.parametrize("rootless", [False, True])
def test_build_no_vm_archive_no_pull_and_owned_cleanup(module, tmp_path, monkeypatch, fail, rootless):
    manifest = tmp_path / "source.yml"
    manifest.write_text("name: test")
    archive = tmp_path / "builder.tar"
    archive.write_bytes(b"archive")
    args = SimpleNamespace(manifest=manifest, work_dir=tmp_path / "work", archive=archive, rootless=rootless,
        image="quay.io/centos-sig-automotive/automotive-image-builder@sha256:" + "a" * 64, timeout=10)
    monkeypatch.setattr(module, "preflight", lambda *_: None)
    monkeypatch.setattr(module.os, "geteuid", lambda: 0)
    monkeypatch.setattr(module, "native_architecture", lambda: "amd64")
    monkeypatch.setattr(module.subprocess, "check_output", lambda *a, **k: "amd64\n")
    calls = []
    def run(command, **kwargs):
        calls.append(command)
        if "--entrypoint" in command:
            if fail:
                raise module.subprocess.TimeoutExpired(command, 10)
            for name in ("minimal_qm.aarch64.qcow2", "minimal_qm.osbuild.json"):
                (args.work_dir / name).write_bytes(b"result")
    monkeypatch.setattr(module.subprocess, "run", run)
    if fail:
        with pytest.raises(module.subprocess.TimeoutExpired):
            module.build(args)
        assert not (args.work_dir / "minimal_qm.sha256").exists()
    else:
        module.build(args)
        assert (args.work_dir / "minimal_qm.sha256").read_text().startswith(module.sha256(args.work_dir / "minimal_qm.aarch64.qcow2"))
    assert not any("pull" in command for command in calls)
    command = next(command for command in calls if "--entrypoint" in command)
    assert "--privileged" in command and "--pull=never" in command
    assert command[command.index("--platform") + 1] == "linux/amd64"
    assert ("/dev:/dev" in command) != rootless
    assert "exec python3 /native_build.py" in command[-3]
    assert ("--rootless" in command[-3]) == rootless
    assert command[-3].index("bwrap --unshare-pid") < command[-3].index("exec python3")
    if rootless:
        assert all("sudo" not in call and "chown" not in call for call in calls)
    assert calls[-1] == ["podman", "rm", "--force", "--ignore", command[command.index("--name") + 1]]


def test_existing_output_refused_before_privileges(module, tmp_path, monkeypatch):
    monkeypatch.setattr(module, "preflight", lambda: pytest.fail("unexpected privilege call"))
    args = SimpleNamespace(work_dir=tmp_path, manifest=tmp_path / "missing",
        image="quay.io/centos-sig-automotive/automotive-image-builder@sha256:" + "a" * 64)
    with pytest.raises(ValueError, match="must be new"):
        module.build(args)


def test_foreign_builder_rejected_before_container_start(module, tmp_path, monkeypatch):
    manifest = tmp_path / "source.yml"
    manifest.write_text("name: test")
    args = SimpleNamespace(work_dir=tmp_path / "work", manifest=manifest, rootless=False,
        archive=tmp_path / "builder.tar", timeout=10,
        image="quay.io/centos-sig-automotive/automotive-image-builder@sha256:" + "a" * 64)
    monkeypatch.setattr(module, "native_architecture", lambda: "amd64")
    monkeypatch.setattr(module, "preflight", lambda *_: None)
    monkeypatch.setattr(module.subprocess, "check_output", lambda *a, **k: "arm64\n")
    calls = []
    monkeypatch.setattr(module.subprocess, "run", lambda command, **k: calls.append(command))
    with pytest.raises(ValueError, match="Expected native amd64"):
        module.build(args)
    assert not args.work_dir.exists()
    assert not any("run" in command for command in calls)
