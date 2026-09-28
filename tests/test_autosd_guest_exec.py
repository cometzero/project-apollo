from pathlib import Path
import sys
import json

import pytest

pytest.importorskip("paramiko")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.autosd_demo.guest_exec import parse_downloads
from scripts.autosd_demo import guest_exec


def test_remaining_budget(monkeypatch):
    monkeypatch.setattr(guest_exec.time, "monotonic", lambda: 8)
    assert guest_exec.remaining(10, 30) == 2
    assert guest_exec.remaining(10, 1) == 1
    with pytest.raises(TimeoutError):
        guest_exec.remaining(8)


def test_exec_request_event_wait_is_released_on_deadline():
    import threading
    import time
    closed = threading.Event()

    class Channel:
        def close(self):
            closed.set()
    def blocked_request():
        assert closed.wait(1), "request was not interrupted"
        raise RuntimeError("channel closed")
    started = time.monotonic()
    with pytest.raises(TimeoutError, match="request exceeded"):
        guest_exec.bounded_request(Channel(), started + .05, 60, blocked_request)
    assert closed.is_set()
    assert time.monotonic() - started < 1


def test_continuous_output_cannot_bypass_deadline(tmp_path, monkeypatch):
    clock = [0]
    monkeypatch.setattr(guest_exec.time, "monotonic", lambda: clock[0])

    class Channel:
        closed = False
        def settimeout(self, seconds):
            assert 0 < seconds <= 3
        def set_combine_stderr(self, value):
            pass
        def exec_command(self, command):
            pass
        def recv_ready(self):
            return True
        def recv(self, size):
            clock[0] += 1
            return b"continuous output\n"
        def exit_status_ready(self):
            pytest.fail("always-ready output must not reach exit status")
        def close(self):
            self.closed = True

    channel = Channel()

    class Client:
        def set_missing_host_key_policy(self, policy):
            pass
        def connect(self, *args, **kwargs):
            assert kwargs["timeout"] == 3
        def get_transport(self):
            return self
        def open_session(self, timeout):
            assert timeout <= 3
            return channel
        def close(self):
            pass

    monkeypatch.setattr(guest_exec.paramiko, "SSHClient", Client)
    out = tmp_path / "run"
    monkeypatch.setattr(sys, "argv", ["guest_exec.py", "--command", "stream",
                                     "--out", str(out), "--timeout", "3"])
    assert guest_exec.main() == 124
    assert channel.closed
    assert json.loads((out / "result.json").read_text())["status"] == "TIMEOUT"
    assert (out / "console.log").read_text().count("continuous output") == 3


def test_sftp_channel_request_is_bounded_and_closed(monkeypatch):
    monkeypatch.setattr(guest_exec.time, "monotonic", lambda: 5)

    class Channel:
        closed = False
        def settimeout(self, value):
            assert value == 2
        def invoke_subsystem(self, name):
            assert name == "sftp"
            raise TimeoutError("subsystem stalled")
        def close(self):
            self.closed = True

    channel = Channel()
    class Client:
        def get_transport(self):
            return self
        def open_session(self, timeout):
            assert timeout == 2
            return channel
    with pytest.raises(TimeoutError, match="subsystem stalled"):
        guest_exec.open_transfer(Client(), 7, 60)
    assert channel.closed


@pytest.mark.parametrize("download", [False, True])
def test_sftp_stream_progress_obeys_total_deadline(monkeypatch, download):
    clock = [0]
    monkeypatch.setattr(guest_exec.time, "monotonic", lambda: clock[0])
    timeouts = []
    class Transfer:
        def get_channel(self):
            return self
        def settimeout(self, value):
            timeouts.append(value)
        def put(self, source, destination, callback):
            clock[0] = 1
            callback(1, 3)
            clock[0] = 3
            callback(3, 3)
        def get(self, source, destination, callback, prefetch):
            assert prefetch is False
            self.put(source, destination, callback)
    with pytest.raises(TimeoutError):
        guest_exec.transfer_file(Transfer(), 2, 30, "source", "dest", download=download)
    assert timeouts == [2, 1]


def test_download_names_are_scoped_to_new_output_directory():
    assert parse_downloads(["/var/tmp/evidence.tar.gz:evidence.tar.gz"]) == [
        ("/var/tmp/evidence.tar.gz", "evidence.tar.gz")
    ]


@pytest.mark.parametrize("item", [
    "missing-separator", "/remote:../escape", "/remote:/absolute", "/remote:.",
    "/remote:..", "/remote:console.log", "/remote:result.json", "/remote:", ":name",
])
def test_download_rejects_paths_and_reserved_outputs(item):
    with pytest.raises(ValueError):
        parse_downloads([item])


def test_download_rejects_duplicate_names():
    with pytest.raises(ValueError, match="Duplicate"):
        parse_downloads(["/first:same.tar", "/second:same.tar"])
