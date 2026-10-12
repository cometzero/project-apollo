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
    (builder / "vm").mkdir()
    (builder / "vm/result.json").write_text(json.dumps({"status": "POWERED_OFF", "poweroff_observed": True}))
    (builder / "launch.json").write_text(json.dumps({"command": ["/project/run_qbox_autosd.sh",
        "--out-dir", str(builder / "vm"), "--rootfs", "original", "--scratch-disk", "scratch"]}))
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
    def popen(command, **kwargs):
        assert command[0] == "/project/run_qbox_autosd.sh"
        assert command[command.index("--out-dir") + 1] == str(output / "vm")
        assert command[command.index("--rootfs") + 1] == str(builder / "vm/rootfs.wic")
        assert command[command.index("--scratch-disk") + 1] == str(builder / "vm/efi-capsule.img")
        return Process()
    monkeypatch.setattr(module.subprocess, "Popen", popen)
    assert module.main() == 0
    assert (old / "builder-uart.log").read_text() == "old evidence"
    assert (output / "builder-uart.log").is_file()
    assert (output / "launcher.pid").read_text() == "123456789\n"
