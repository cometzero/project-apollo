"""Rootless appliance reconstruction contracts."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def helper():
    path = Path(__file__).resolve().parents[1] / "scripts/autosd_demo/prepare_host_tools.py"
    spec = importlib.util.spec_from_file_location("prepare_host_tools", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_installed_version(helper, monkeypatch):
    monkeypatch.setattr(helper, "run", lambda command: SimpleNamespace(stdout="installed 1.2"))
    assert helper.installed_version("example") == "1.2"


def test_removed_package_rejected(helper, monkeypatch):
    monkeypatch.setattr(helper, "run", lambda command: SimpleNamespace(stdout="config-files 1.2"))
    with pytest.raises(RuntimeError, match="not installed"):
        helper.installed_version("example")


def test_missing_prerequisite_does_not_create_output(helper, monkeypatch, tmp_path):
    image = tmp_path / "input.raw"
    image.touch()
    output = tmp_path / "tools"
    monkeypatch.setattr(helper.shutil, "which", lambda name: None)
    with pytest.raises(RuntimeError, match="sudo apt-get install"):
        helper.prepare(output, image)
    assert not output.exists()


def test_download_extracts_only_selected_package(helper, monkeypatch, tmp_path):
    commands = []
    def run(command, **kwargs):
        commands.append(command)
        if command[:2] == ["apt-get", "download"]:
            (kwargs["cwd"] / "guestfish_test.deb").write_bytes(b"test")
    monkeypatch.setattr(helper, "run", run)
    receipt = helper.extract_package("guestfish=1.2", tmp_path)
    assert commands[0] == ["apt-get", "download", "guestfish=1.2"]
    assert commands[1][:2] == ["dpkg-deb", "-x"]
    assert receipt["sha256"] == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"


def test_ambiguous_download_is_rejected(helper, monkeypatch, tmp_path):
    destination = tmp_path / "packages/guestfish"
    destination.mkdir(parents=True)
    (destination / "old.deb").touch()
    (destination / "new.deb").touch()
    monkeypatch.setattr(helper, "run", lambda *args, **kwargs: None)
    with pytest.raises(RuntimeError, match="Expected one"):
        helper.extract_package("guestfish", tmp_path)
