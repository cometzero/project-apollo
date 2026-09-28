"""Selected destructive demos must never manufacture prerequisites."""
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import selectors
import time

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("demo_cases", ROOT / "autosd/customization/demo-guest.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


@pytest.mark.parametrize("selection", [f"S{i:02d}" for i in range(1, 7)])
def test_selection_exact(selection):
    selected = demo.selected_cases(selection)
    assert len(selected) == 1
    assert selected[0][0].startswith(selection + "-")
    assert demo.selected_cases("all") == demo.CASES


@pytest.mark.parametrize("selection", ["S02", "S03", "S04", "S05", "S06"])
def test_failed_precondition_does_not_execute_case(tmp_path, monkeypatch, selection, capsys):
    calls = []
    def fake(name, command, output, timeout):
        calls.append((name, command))
        return {"id": name, "status": "FAIL", "returncode": 1}
    monkeypatch.setattr(demo, "run_case", fake)
    monkeypatch.setattr(sys, "argv", ["demo", "--allow-disruptive-demo", "--case", selection,
                                     "--out", str(tmp_path / "out")])
    assert demo.main() == 1
    assert len(calls) == 1 and calls[0][0] == selection + "-precheck"
    assert "systemctl restart" not in calls[0][1]
    assert "unlink" not in calls[0][1]
    assert json.loads((tmp_path / "out/results.json").read_text())[0]["status"] == "BLOCKED"
    assert '"event": "case-start"' in capsys.readouterr().out


def test_selected_fault_leaves_latch_without_recovery(tmp_path, monkeypatch):
    calls = []
    def fake(name, *args):
        calls.append(name)
        return {"id": name, "status": "PASS", "returncode": 0}
    monkeypatch.setattr(demo, "run_case", fake)
    monkeypatch.setattr(sys, "argv", ["demo", "--allow-disruptive-demo", "--case", "S04",
                                     "--out", str(tmp_path / "out")])
    assert demo.main() == 0
    assert calls == ["S04-precheck", "S04-adas-fault"]
    assert json.loads((tmp_path / "out/results.json").read_text())[0]["guest_state"] == "FAULT_LATCHED"


def test_full_suite_order_unchanged(tmp_path, monkeypatch):
    calls = []
    def fake(name, *args):
        calls.append(name)
        return {"id": name, "status": "PASS", "returncode": 0}
    monkeypatch.setattr(demo, "run_case", fake)
    monkeypatch.setattr(sys, "argv", ["demo", "--allow-disruptive-demo", "--out", str(tmp_path / "out")])
    assert demo.main() == 0
    assert calls == [name for name, _ in demo.CASES]


def test_recovery_requires_explicit_disruptive_guard(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["demo", "--case", "S06", "--out", str(tmp_path / "out")])
    with pytest.raises(SystemExit):
        demo.main()
    assert not (tmp_path / "out").exists()


def test_guest_output_tees_before_process_exits(tmp_path):
    harness = (
        f"import runpy; from pathlib import Path; m=runpy.run_path({str(ROOT / 'autosd/customization/demo-guest.py')!r}); "
        f"m['run_case']('stream', 'set +x; printf LIVE; printf STDERR >&2; sleep 2', Path({str(tmp_path)!r}), 5)"
    )
    with subprocess.Popen([sys.executable, "-c", harness], stdout=subprocess.PIPE) as child:
        received = b""
        with selectors.DefaultSelector() as selector:
            selector.register(child.stdout, selectors.EVENT_READ)
            deadline = time.monotonic() + 1.5
            while b"LIVESTDERR" not in received and time.monotonic() < deadline:
                if selector.select(.1):
                    received += child.stdout.read1(4096)
        assert b"LIVE" in received and b"STDERR" in received
        assert child.poll() is None, "output must be visible before command completion"
        assert "LIVE" in (tmp_path / "stream.log").read_text()
        remainder = child.communicate(timeout=5)[0]
        assert b"END rc=0" in remainder


def test_guest_trace_and_nonzero_exit_preserved(tmp_path, capsys):
    result = demo.run_case("failure", "bash -c 'echo nested-output; test 1 = 2'", tmp_path, 5)
    live = capsys.readouterr().out
    assert result["returncode"] == 1
    assert result["status"] == "FAIL"
    assert "nested-output" in live and "test 1 = 2" in live
    assert "END rc=1" in live
    assert (tmp_path / "failure.log").read_text() in live


def test_guest_timeout_is_visible(tmp_path, capsys):
    result = demo.run_case("timeout", "sleep 5", tmp_path, .1)
    assert result["returncode"] == 124
    assert "END rc=124" in capsys.readouterr().out
