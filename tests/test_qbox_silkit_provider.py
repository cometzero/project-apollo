"""Yocto provider paths and host library isolation for SIL Kit."""
import importlib.util
import json
import os
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("qbox_silkit", Path(__file__).resolve().parents[1] / "scripts/run/qbox_silkit.py")
silkit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(silkit)


def test_custom_deploy_manifest_and_environment(tmp_path, monkeypatch):
    for key in ("QBOX_SILKIT_BINARY", "QBOX_SILKIT_REGISTRY_BINARY", "QBOX_SILKIT_LIBRARY_PATH"):
        monkeypatch.delenv(key, raising=False)
    deploy = tmp_path / "custom/deploy/images/apollo-qvp"
    deploy.mkdir(parents=True)
    binary = tmp_path / "native sysroot/vmcu-silkit"
    binary.parent.mkdir()
    binary.write_text("#!/bin/sh\nexit 0\n")
    binary.chmod(0o755)
    manifest = deploy.parent.parent / "vmcu-silkit-native/vmcu-silkit-native.json"
    manifest.parent.mkdir()
    manifest.write_text(json.dumps({"executable": str(binary), "registry_executable": str(binary),
                                    "library_path": ["/native/lib", "/native/lib64"]}))
    assert silkit.provider(deploy) == (str(binary), str(binary), "/native/lib:/native/lib64")
    monkeypatch.setenv("LD_LIBRARY_PATH", "/qemu/lib")
    assert silkit.environment("/silkit/lib")["LD_LIBRARY_PATH"] == "/silkit/lib:/qemu/lib"
    assert os.environ["LD_LIBRARY_PATH"] == "/qemu/lib"
    monkeypatch.setenv("QBOX_SILKIT_LIBRARY_PATH", "/override/lib")
    assert silkit.provider(deploy)[2] == "/override/lib"


def test_missing_manifest_and_explicit_external_registry(tmp_path, monkeypatch):
    for key in ("QBOX_SILKIT_BINARY", "QBOX_SILKIT_REGISTRY_BINARY", "QBOX_SILKIT_LIBRARY_PATH", "DEPLOY_DIR"):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(ValueError, match="provider missing"):
        silkit.provider(tmp_path)
    assert silkit.provider(tmp_path, dry_run=True)[0].endswith("vmcu-silkit")
    binary = tmp_path / "custom participant"
    binary.write_text("#!/bin/sh\nexit 0\n")
    binary.chmod(0o755)
    monkeypatch.setenv("QBOX_SILKIT_BINARY", str(binary))
    assert silkit.provider(tmp_path, external=True)[0] == str(binary)
    with pytest.raises(ValueError, match="provider missing"):
        silkit.provider(tmp_path)
    monkeypatch.setenv("QBOX_SILKIT_REGISTRY_BINARY", str(binary))
    assert silkit.provider(tmp_path)[:2] == (str(binary), str(binary))


@pytest.mark.parametrize("content", [[], {}, {"executable": 42}])
def test_malformed_manifest_rejected(tmp_path, monkeypatch, content):
    for key in ("QBOX_SILKIT_BINARY", "QBOX_SILKIT_REGISTRY_BINARY"):
        monkeypatch.delenv(key, raising=False)
    deploy = tmp_path / "deploy/images/apollo-qvp"
    deploy.mkdir(parents=True)
    manifest = deploy.parent.parent / "vmcu-silkit-native/vmcu-silkit-native.json"
    manifest.parent.mkdir()
    manifest.write_text(json.dumps(content))
    with pytest.raises(ValueError, match="Invalid SIL Kit provider"):
        silkit.provider(deploy)
