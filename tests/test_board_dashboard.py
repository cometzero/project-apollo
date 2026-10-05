"""Session isolation and bounded transport contracts for the Yocto dashboard."""
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/autosd_dashboard"))
from board_io import log_page, save
from yocto_board import Board, BoardError
from vmcu import Vmcu
import yocto_board
import yocto_board


def test_cursor_utf8_append_and_run_isolation(tmp_path):
    path = tmp_path / "tc397-uart.log"
    path.write_bytes("한".encode()[:2])
    first = log_page(tmp_path, "run-a", "tc397")
    assert first["text"] == ""
    path.write_bytes("한글\n".encode())
    next_page = log_page(tmp_path, "run-a", "tc397", first["next_cursor"])
    assert next_page["text"] == "한글\n"
    with pytest.raises(ValueError, match="stale"):
        log_page(tmp_path, "run-b", "tc397", next_page["next_cursor"])
    assert log_page(tmp_path, "run-a", "tc397", next_page["next_cursor"])["text"] == ""


def test_cursor_rotation_and_path_restriction(tmp_path):
    path = tmp_path / "tc397-uart.log"
    path.write_text("one\n")
    page = log_page(tmp_path, "r", "tc397")
    path.rename(tmp_path / "old.log")
    path.write_text("two\n")
    new = log_page(tmp_path, "r", "tc397", page["next_cursor"])
    assert new["gap"] and new["text"] == "two\n"
    with pytest.raises(KeyError):
        log_page(tmp_path, "r", "../../etc/passwd")
    path.unlink()
    path.symlink_to(tmp_path / "old.log")
    with pytest.raises(ValueError, match="symlink"):
        log_page(tmp_path, "r", "tc397")


@pytest.fixture
def board(tmp_path):
    spec = tmp_path / "spec.json"
    save(spec, {"command": ["python3", "runner.py"], "out_dir": str(tmp_path / "session"),
                "stats_interval": 2, "bsp": True, "vmcu": True})
    app = Board(spec)
    yield app
    app.close()


def test_job_idempotency_and_stale_run(board, monkeypatch):
    monkeypatch.setattr(board, "_execute", lambda job: {"verified": True})
    payload = {"action": "board.start", "args": {}, "run_id": None, "request_id": "request-1"}
    first = board.start_job(payload)
    deadline = time.monotonic() + 2
    while board.active_job and time.monotonic() < deadline:
        time.sleep(.01)
    again = board.start_job(payload)
    assert first["id"] == again["id"] and again["status"] == "PASS"
    with pytest.raises(BoardError) as error:
        board.start_job(dict(payload, action="board.restart"))
    assert error.value.status == 409
    with pytest.raises(BoardError) as error:
        board.start_job(dict(payload, request_id="r2", run_id="old"))
    assert error.value.status == 409


def test_disruptive_confirmation_and_typed_actions(board):
    with pytest.raises(BoardError, match="confirm_disruptive"):
        board.start_job({"action": "board.restart", "args": {}, "run_id": None, "request_id": "r"})
    with pytest.raises(BoardError):
        board.start_job({"action": "shell", "args": {"command": "true"}, "run_id": None, "request_id": "r"})


def test_stats_do_not_reuse_another_run(board, tmp_path):
    board.directory, board.run_id = tmp_path, "current"
    row = {"run_id": "previous", "sample_monotonic": time.monotonic(), "seq": 1}
    (tmp_path / "stats.jsonl").write_text(json.dumps(row) + "\n")
    assert board.stats()["status"] == "WARMING_UP"
    row.update(run_id="current", sample_monotonic=time.monotonic() - 20, cpu_pct=125)
    (tmp_path / "stats.jsonl").write_text(json.dumps(row) + "\n")
    result = board.stats()
    assert result["status"] == "STALE" and result["latest"]["cpu_pct"] == 125


@pytest.mark.parametrize("op,arg", [(True, 0), (8, 0), (1, 1), (3, 9), (4, 11)])
def test_vehicle_args_rejected_before_transport(tmp_path, op, arg):
    with pytest.raises(ValueError):
        Vmcu(tmp_path).vehicle_command(op, arg)


def test_registered_qvp_profiles_use_actual_registry(board):
    profiles = [x for x in board.catalog() if x["id"].startswith("qvp.")]
    assert len(profiles) == 11
    assert all(x["mode"] == "fresh-run" and x["disruptive"] for x in profiles)
    assert not any(x["id"] == "qvp.hipc" for x in profiles)


def test_evidence_quota_stops_owned_writer_without_truncation(board, tmp_path, monkeypatch):
    class Writer:
        def __init__(self): self.signals = []
        def poll(self): return None
        def send_signal(self, number): self.signals.append(number)
    proc = Writer()
    board.directory, board.run_id, board.proc = tmp_path, "quota-run", proc
    log = tmp_path / "tc397-uart.log"
    log.write_text("preserve this evidence")
    (tmp_path / "disk.wic").write_bytes(b"0" * 1024)
    monkeypatch.setattr(yocto_board, "EVIDENCE_LIMIT", 20)
    board._check_quota(board._generation())
    assert board.run_abort.is_set() and board.lifecycle == "FAILED"
    assert len(proc.signals) == 1 and log.read_text() == "preserve this evidence"
    board.proc = None


def test_session_job_history_is_bounded(board, monkeypatch):
    monkeypatch.setattr(yocto_board, "JOB_LIMIT", 0)
    with pytest.raises(BoardError) as error:
        board.start_job({"action": "board.start", "args": {}, "run_id": None, "request_id": "over-limit"})
    assert error.value.status == 429


@pytest.mark.parametrize("cleanup,expected", [("PASS", "BLOCKED"), ("FAIL", "FAIL")])
def test_profile_blocked_is_preserved_without_hiding_cleanup_failure(board, monkeypatch, cleanup, expected):
    def blocked(job):
        job["result"] = {"profile": {"verdict": "BLOCKED"},
                         "session": {"cleanup": {"status": cleanup, "residual_pids": []}}}
        raise RuntimeError("runtime prerequisite unavailable")
    monkeypatch.setattr(board, "_execute", blocked)
    job = {"id": "blocked-job", "action": "qvp.cpuidle"}
    board._run_job(job)
    assert job["status"] == expected


@pytest.fixture
def quiet_board(board):
    """Deterministically interleave observations without starting any model."""
    board.close_event.set()
    board.worker.join(timeout=2)
    board.close_event.clear()
    yield board
    # Tests use fake process objects only; never ask cleanup to signal them.
    board.proc = None


def test_old_boot_markers_cannot_qualify_new_generation(quiet_board, tmp_path, monkeypatch):
    app = quiet_board
    app.run_id, app.directory, app.lifecycle = "old", tmp_path / "old", "BOOTING"
    app.directory.mkdir()
    markers = [m for group in yocto_board.CHILD_REQUIRED_MARKERS.values() for m in group]
    markers += list(yocto_board.SI_CL0_REQUIRED_MARKERS.values())
    markers += list(yocto_board.SI_CL1_REQUIRED_MARKERS.values())
    markers += ["NEXIOS_BSP_INITRAMFS_READY", "VMCU_INIT result=PASS"]
    def switch_run(_):
        app.run_id, app.directory = "new", tmp_path / "new"
        app.domains = [{"id": "new-domain"}]
        return "\n".join(markers)
    monkeypatch.setattr(yocto_board, "tail", switch_run)
    assert app._observe_boot() is False
    assert app.lifecycle == "BOOTING" and app.domains == [{"id": "new-domain"}]
    assert app.boot_evidence == {}
    assert not (tmp_path / "old/dashboard-boot.json").exists()


def test_old_monitor_cannot_attach_to_new_generation(quiet_board, tmp_path, monkeypatch):
    app = quiet_board
    app.run_id, app.directory, app.lifecycle = "old", tmp_path / "old", "RUNNING"
    app.proc = SimpleNamespace(pid=42)
    class Collector:
        def __init__(self, manifest, **kwargs):
            assert manifest["run_id"] == "old"
            self.sampled = False
            app.run_id, app.directory = "new", tmp_path / "new"
        def sample(self):
            self.sampled = True
            pytest.fail("stale monitor must not sample")
    monkeypatch.setattr(yocto_board, "load", lambda _: {"pid": 43, "start_ticks": 10})
    monkeypatch.setattr(yocto_board, "process_identity", lambda _: (1, 10))
    monkeypatch.setattr(yocto_board, "QBoxMonitorCollector", Collector)
    monkeypatch.setattr(yocto_board, "QBoxDiagnostics", lambda *args, **kwargs: object())
    app._observe_monitor()
    assert app.collector is None and app.diagnostics is None


def test_optional_monitor_diagnostics_wait_for_boot(quiet_board, tmp_path, monkeypatch):
    app = quiet_board
    app.run_id, app.directory, app.lifecycle = "boot", tmp_path, "BOOTING"
    app.proc = SimpleNamespace(pid=42)
    monkeypatch.setattr(yocto_board, "load", lambda _: pytest.fail("boot must not start diagnostics"))
    app._observe_monitor()
    assert app.collector is None


def test_exited_old_process_does_not_fail_new_lifecycle(quiet_board, tmp_path, monkeypatch):
    app = quiet_board
    app.run_id, app.directory, app.lifecycle = "old", tmp_path, "RUNNING"
    class OneTick:
        first = True
        def wait(self, _):
            if self.first:
                self.first = False
                return False
            return True
    def exited():
        app.run_id, app.lifecycle = "new", "BOOTING"
        app.proc = SimpleNamespace(returncode=None)
        return 1
    app.proc = SimpleNamespace(poll=exited, returncode=1)
    with monkeypatch.context() as context:
        context.setattr(app, "close_event", OneTick())
        app.monitor()
    assert app.lifecycle == "BOOTING" and app.error is None


@pytest.mark.parametrize("cleanup", [None, {}, {"status": "FAIL"}])
def test_stop_requires_explicit_cleanup_pass(quiet_board, tmp_path, cleanup):
    app = quiet_board
    app.directory = tmp_path
    app.proc = SimpleNamespace(poll=lambda: 1, returncode=1)
    save(tmp_path / "board-session.json", {"cleanup": cleanup})
    with pytest.raises(RuntimeError, match="cleanup did not report PASS"):
        app._stop()
    assert app.lifecycle == "FAILED"


def test_vmcu_observation_age_uses_server_clock(quiet_board, monkeypatch):
    app = quiet_board
    app.vmcu_status = {"state": "RUN", "observed_monotonic": 92.5}
    monkeypatch.setattr(yocto_board.time, "monotonic", lambda: 100.0)
    assert app.state()["vmcu_status"]["observation_age_s"] == 7.5
    assert "observation_age_s" not in app.vmcu_status
    app.vmcu_status = {"status": "UNAVAILABLE"}
    assert app.state()["vmcu_status"]["observation_age_s"] is None


@pytest.mark.parametrize("errno,state,passes", [(0, 0, True), (-5, 0, False), (0, 3, False)])
def test_can_restart_checks_reply_and_controller_state(quiet_board, monkeypatch, errno, state, passes):
    calls = []
    class FakeVmcu:
        def __init__(self, *args): pass
        def cli(self, command, pattern):
            calls.append(command)
            return f"VMCU_CAN_RESTART errno={errno}" if command == "can restart" else f"VMCU_CAN_STATUS state={state}"
    monkeypatch.setattr(yocto_board, "Vmcu", FakeVmcu)
    if passes:
        result = quiet_board._execute({"action": "vmcu.can.restart"})
        assert result["status"]["state"] == "0"
    else:
        with pytest.raises(RuntimeError, match="CAN restart"):
            quiet_board._execute({"action": "vmcu.can.restart"})
    assert calls == (["can restart", "can status"] if errno == 0 else ["can restart"])


@pytest.mark.parametrize("failure", [None, "canonical", "cleanup", "residual", "session-code", "process-code"])
def test_profile_success_requires_runner_and_cleanup(quiet_board, tmp_path, monkeypatch, failure):
    app = quiet_board
    app.directory, app.run_id = tmp_path, "run"
    app.proc = SimpleNamespace(poll=lambda: 0, returncode=1 if failure == "process-code" else 0)
    result = {"passed": failure != "canonical", "verdict": "pass", "validation_profile": {"verdict": "PASS"}}
    session = {"returncode": 1 if failure == "session-code" else 0,
               "cleanup": {"status": "FAIL" if failure == "cleanup" else "PASS",
                           "residual_pids": [99] if failure == "residual" else []}}
    save(tmp_path / "result.json", result)
    save(tmp_path / "board-session.json", session)
    monkeypatch.setattr(app, "_stop", lambda: None)
    monkeypatch.setattr(app, "_launch", lambda _: None)
    job = {"action": "qvp.profile"}
    if failure is None:
        assert app._execute(job)["profile"]["verdict"] == "PASS"
    else:
        with pytest.raises(RuntimeError, match="did not pass"):
            app._execute(job)
        assert job["result"]["profile"]["verdict"] == "PASS"


def test_qualification_requires_success_in_current_run(quiet_board):
    app = quiet_board
    app.run_id = "current"
    app.jobs = [{"id": "old", "run_id": "old", "action": "vmcu.status", "status": "PASS"},
                {"id": "failed", "run_id": "current", "action": "vmcu.ap.ping", "status": "FAIL"},
                {"id": "passed", "run_id": "current", "action": "vmcu.safety.ping", "status": "PASS"}]
    rows = {row["id"]: row for row in app.catalog()}
    assert not rows["vmcu.status"]["qualified"]
    assert not rows["vmcu.ap.ping"]["qualified"]
    assert rows["vmcu.safety.ping"]["qualification"] == {
        "run_id": "current", "job_id": "passed", "scope": "successful action in this run; functional QVP only"}
