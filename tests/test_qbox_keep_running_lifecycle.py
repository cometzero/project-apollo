from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from unittest.mock import Mock

import pytest


RUNNER = Path(__file__).resolve().parents[1] / "scripts/run/run_qbox_apollo_fvp_full.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("keep_running_runner", RUNNER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def configure_runner(module, tmp_path, monkeypatch, *, keep=True, build=False):
    args = argparse.Namespace(
        out_dir=tmp_path, qbox_build_dir=tmp_path, timer_probe=False,
        build_only=build, live_trace=False, si_cl0_command=None,
        keep_running_after_pass=keep, timeout=1,
    )
    monkeypatch.setattr(module, "child_command", lambda *_: ["dummy-child"])
    monkeypatch.setattr(module, "clear_run_outputs", lambda *_: None)
    monkeypatch.setattr(module, "full_system_child_environment", lambda *_: {})
    artifacts = {"si_cl0_image": tmp_path, "si_cl1_image": tmp_path}
    return args, artifacts


def test_keep_running_child_has_independent_session(tmp_path, monkeypatch):
    module = load_runner()
    args, artifacts = configure_runner(module, tmp_path, monkeypatch)
    popen = Mock()
    wait = Mock(return_value=0)
    monkeypatch.setattr(module.subprocess, "Popen", popen)
    monkeypatch.setattr(module, "wait_for_keep_running_child_pass", wait)
    assert module.run_child(args, artifacts) == (0, ["dummy-child"])
    assert popen.call_args.kwargs["start_new_session"] is True
    wait.assert_called_once_with(args, popen.return_value, ["dummy-child"])


@pytest.mark.parametrize("keep,build", [(False, False), (True, True)])
def test_other_runs_remain_synchronous(tmp_path, monkeypatch, keep, build):
    module = load_runner()
    args, artifacts = configure_runner(
        module, tmp_path, monkeypatch, keep=keep, build=build
    )
    run = Mock(return_value=argparse.Namespace(returncode=7))
    monkeypatch.setattr(module.subprocess, "run", run)
    assert module.run_child(args, artifacts)[0] == 7
    assert "start_new_session" not in run.call_args.kwargs


def test_keep_running_timeout_still_terminates_child(tmp_path, monkeypatch):
    module = load_runner()
    args = argparse.Namespace(out_dir=tmp_path, timeout=1)
    proc = Mock()
    proc.poll.return_value = None
    proc.wait.side_effect = [subprocess.TimeoutExpired("child", 10), -9]
    monkeypatch.setattr(module, "read_json", lambda *_: {})
    monkeypatch.setattr(module, "synthesize_keep_running_child_status", lambda *_a, **_k: {})
    result = Mock()
    monkeypatch.setattr(module, "write_keep_running_child_result", result)
    monkeypatch.setattr(module.time, "monotonic", Mock(side_effect=[0, 2]))
    assert module.wait_for_keep_running_child_pass(args, proc, ["child"]) == -9
    proc.terminate.assert_called_once()
    proc.kill.assert_called_once()
    assert result.call_args.kwargs["blocker"] == "child_keep_running_timeout"


@pytest.mark.skipif(os.name != "posix", reason="POSIX process-group lifecycle")
def test_logging_survives_launcher_exit_and_group_cleanup(tmp_path):
    # Exercise run_child with a real logger process, without requiring a VM.
    # The gate makes the logged event occur strictly after launcher cleanup.
    logger = """
import os, pathlib, sys, time
p = pathlib.Path(sys.argv[1])
(p / 'logger.pid').write_text(str(os.getpid()))
deadline = time.monotonic() + 10
while not (p / 'gate').exists() and time.monotonic() < deadline:
    time.sleep(0.01)
if (p / 'gate').exists():
    (p / 'runtime.log').write_text('post-launcher event\\n')
"""
    parent = """
import importlib.util, pathlib, sys, time
spec = importlib.util.spec_from_file_location('lifecycle_test', sys.argv[1])
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
m = t.load_runner()
class Patch:
    def setattr(self, obj, name, value): setattr(obj, name, value)
p = pathlib.Path(sys.argv[2])
args, artifacts = t.configure_runner(m, p, Patch())
m.child_command = lambda *_: [sys.executable, '-c', sys.argv[3], str(p)]
def ready(*_):
    deadline = time.monotonic() + 5
    while not (p / 'logger.pid').exists():
        if time.monotonic() >= deadline: raise RuntimeError('logger not ready')
        time.sleep(0.01)
    return 0
m.wait_for_keep_running_child_pass = ready
assert m.run_child(args, artifacts)[0] == 0
"""
    proc = subprocess.Popen(
        [sys.executable, "-c", parent, __file__, str(tmp_path), logger],
        start_new_session=True, stdout=subprocess.DEVNULL,
    )
    logger_pid = None
    try:
        assert proc.wait(timeout=10) == 0
        logger_pid = int((tmp_path / "logger.pid").read_text())
        assert os.getsid(logger_pid) == logger_pid
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        (tmp_path / "gate").touch()
        deadline = time.monotonic() + 5
        while not (tmp_path / "runtime.log").exists():
            assert time.monotonic() < deadline, "logger lost after launcher exit"
            time.sleep(0.01)
        assert (tmp_path / "runtime.log").read_text() == "post-launcher event\n"
    finally:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=5)
        if logger_pid is not None:
            try:
                os.kill(logger_pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
