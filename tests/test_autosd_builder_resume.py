"""Preserve old builder evidence when resuming into a selected directory."""
import importlib.util
import json
from pathlib import Path


def test_resume_selected_output(tmp_path, monkeypatch):
    source = Path(__file__).resolve().parents[1] / "scripts/autosd_demo/ota_builder_resume.py"
    spec = importlib.util.spec_from_file_location("builder_resume", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    builder, old, output = (tmp_path / name for name in ("builder", "old", "new"))
    builder.mkdir()
    old.mkdir()
    (old / "builder-uart.log").write_text("old evidence")
    (builder / "launch.json").write_text(json.dumps({"command": ["fake-qemu"]}))
    previous = tmp_path / "build/autosd/demo-regular-session"
    previous.mkdir(parents=True)
    (previous / "launch.json").write_text('{"environment": {}}')
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "BUILDER", builder)
    monkeypatch.setattr(module, "WORK", old)
    monkeypatch.setattr("sys.argv", ["resume", "--out", str(output)])

    class Socket:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def bind(self, address):
            assert address == ("127.0.0.1", 2226)

    class Process:
        pid = 123456789

        def wait(self):
            return 0

    monkeypatch.setattr(module.socket, "socket", Socket)
    monkeypatch.setattr(module.subprocess, "Popen", lambda *args, **kwargs: Process())
    assert module.main() == 0
    assert (old / "builder-uart.log").read_text() == "old evidence"
    assert (output / "builder-uart.log").is_file()
    assert (output / "qemu.pid").read_text() == "123456789\n"
