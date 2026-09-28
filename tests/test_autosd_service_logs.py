"""Guest service log bounds and read-only command contracts, without a VM."""
import importlib.util
from pathlib import Path
import subprocess

import pytest

PATH = Path(__file__).resolve().parents[1] / "scripts/autosd_dashboard/service_logs.py"
spec = importlib.util.spec_from_file_location("autosd_service_logs", PATH)
logs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logs)


class Channel:
    def __init__(self, data=b"guest output\n", code=0, done=True):
        self.data, self.code, self.done = data, code, done
        self.closed = False

    def settimeout(self, value):
        self.timeout = value

    def set_combine_stderr(self, value):
        self.combined = value

    def exec_command(self, command):
        self.command = command

    def recv_ready(self):
        return bool(self.data)

    def recv(self, size):
        value, self.data = self.data[:size], self.data[size:]
        return value

    def exit_status_ready(self):
        return self.done

    def recv_exit_status(self):
        return self.code

    def close(self):
        self.closed = True


class Client:
    def __init__(self, channel):
        self.channel, self.closed = channel, False

    def set_missing_host_key_policy(self, policy):
        pass

    def connect(self, host, **options):
        self.host, self.options = host, options

    def get_transport(self):
        return self

    def open_session(self, timeout):
        return self.channel

    def close(self):
        self.closed = True


def install(monkeypatch, channel):
    client = Client(channel)
    monkeypatch.setattr(logs.paramiko, "SSHClient", lambda: client)
    return client


def test_success_merges_stderr_and_uses_loopback(monkeypatch):
    channel = Channel()
    client = install(monkeypatch, channel)
    result = logs.collect(2244, "safety")
    assert result["status"] == "OK"
    assert result["text"] == "guest output\n"
    assert result["collected_at"]
    assert client.host == "127.0.0.1"
    assert client.options["port"] == 2244
    assert client.options["allow_agent"] is False
    assert channel.combined is True
    assert channel.closed and client.closed


@pytest.mark.parametrize("source", ["invalid", "root; reboot", "../root", "", None, []])
def test_invalid_source_never_connects(monkeypatch, source):
    monkeypatch.setattr(logs.paramiko, "SSHClient", lambda: pytest.fail("SSH invoked"))
    with pytest.raises(ValueError, match="Unknown"):
        logs.collect(2244, source)


@pytest.mark.parametrize("code,status", [(1, "ERROR"), (124, "TIMEOUT")])
def test_errors_preserve_guest_output(monkeypatch, code, status):
    install(monkeypatch, Channel(b"guest error\n", code=code))
    result = logs.collect(2244, "adas")
    assert result["status"] == status
    assert "guest error" in result["text"]
    assert f"exit {code}" in result["text"]


def test_empty_output_is_explicit(monkeypatch):
    install(monkeypatch, Channel(b""))
    result = logs.collect(2244, "qm")
    assert result["status"] == "EMPTY"
    assert result["text"] == "[no guest output]\n"


def test_output_size_bound(monkeypatch):
    channel = Channel(b"x" * (logs.MAX_OUTPUT + 10000))
    client = install(monkeypatch, channel)
    result = logs.collect(2244, "root")
    assert result["status"] == "TRUNCATED"
    assert result["text"].startswith("x" * logs.MAX_OUTPUT)
    assert len(result["text"]) < logs.MAX_OUTPUT + 100
    assert len(channel.data) == 9999
    assert channel.closed and client.closed


def test_deadline_with_continuous_output(monkeypatch):
    channel = Channel(b"x" * 65536, done=False)
    install(monkeypatch, channel)
    clock = iter([0, 1, 16])
    monkeypatch.setattr(logs.time, "monotonic", lambda: next(clock))
    result = logs.collect(2244, "root")
    assert result["status"] == "TIMEOUT"
    assert result["text"].startswith("x" * 16384)
    assert channel.closed


def test_deadline_with_no_output(monkeypatch):
    channel = Channel(b"", done=False)
    install(monkeypatch, channel)
    clock = iter([0, 1, 16])
    monkeypatch.setattr(logs.time, "monotonic", lambda: next(clock))
    monkeypatch.setattr(logs.time, "sleep", lambda seconds: None)
    assert logs.collect(2244, "root")["status"] == "TIMEOUT"


def test_connection_failure_is_visible_and_closed(monkeypatch):
    client = install(monkeypatch, Channel())
    def fail(*args, **kwargs):
        raise OSError("connection refused")
    monkeypatch.setattr(client, "connect", fail)
    result = logs.collect(2244, "root")
    assert result["status"] == "UNAVAILABLE"
    assert "connection refused" in result["text"]
    assert client.closed


def test_static_read_only_sources():
    assert {s["id"] for s in logs.SOURCES} == set(logs.COMMANDS)
    for source in logs.COMMANDS:
        command = logs.command_for(source)
        assert command.startswith("timeout -k 1s 15s sh -c ")
        assert "[no output]" in command
        assert "[exit %s]" in command
        assert all(verb not in command for verb in ["systemctl start", "systemctl stop", " reboot", " rm "])
    assert "podman logs --tail 80 apollo-adas" in logs.command_for("adas")
    assert "podman exec qm podman logs --tail 80 apollo-qm-container" in logs.command_for("qm-container")
    assert "/run/apollo-qm/heartbeat" in logs.command_for("qm-app")


def test_shell_wrapper_reports_every_command_and_retains_failure(monkeypatch):
    # Synthetic read-only commands exercise quoting and result aggregation.
    monkeypatch.setitem(logs.COMMANDS, "fixture", (
        "printf 'guest message\\n'", "printf 'guest error\\n' >&2; false", "true"))
    result = subprocess.run(["sh", "-c", logs.command_for("fixture")],
                            capture_output=True, text=True, timeout=5)
    assert result.returncode == 1
    assert "guest message\n[exit 0]" in result.stdout
    assert "guest error\n[exit 1]" in result.stdout
    assert "$ true\n[no output]\n[exit 0]" in result.stdout


@pytest.mark.parametrize("source,container", [("adas", "apollo-adas"), ("qm-container", "apollo-qm-container")])
def test_scratch_container_heartbeat_snapshot(source, container):
    command = logs.COMMANDS[source][-1]
    assert "heartbeat file snapshot; not application stdout" in command
    assert "tail -c 4096" in command
    assert "/proc/$pid/root/run/heartbeat" in command
    assert container in command
    assert (command.startswith("podman exec qm sh -c ")) == (source == "qm-container")
    assert "No running container PID" in command
    subprocess.run(["sh", "-n", "-c", logs.command_for(source)], check=True)
