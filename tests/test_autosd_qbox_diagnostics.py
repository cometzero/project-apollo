"""QMP bridge correlation, read-only policy and receive bounds."""
import importlib.util
import json
from pathlib import Path
import socket
import time

import pytest

PATH = Path(__file__).resolve().parents[1] / 'scripts/autosd_dashboard/qbox_diagnostics.py'
spec = importlib.util.spec_from_file_location('qbox_diagnostics', PATH)
diagnostics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostics)


class Collector:
    manifest = {'domains': [{'domain_id': 'ap', 'qmp_biflow': 'platform.ap_qmp.qmp_socket'}]}
    endpoint = {'host': '127.0.0.1', 'port': 12345}
    run_id = 'run-A'
    checked = False

    def _get(self, path):
        assert path == '/biflows'
        self.checked = True
        return {'biflows': ['platform.ap_qmp.qmp_socket']}


class Connection:
    def __init__(self, mode='normal'):
        self.mode = mode
        self.closed = False
        self.sent = None

    def send(self, value):
        self.sent = json.loads(value)
        assert self.sent['execute'] in diagnostics.QBoxDiagnostics.COMMANDS
        request_id = self.sent['id']
        lines = [{'QMP': {}}, {'id': 'old-run', 'return': {}}, {'event': 'RESET'},
                 {'id': request_id, 'return': {'status': 'running'}}]
        if self.mode == 'error':
            lines[-1] = {'id': request_id, 'error': {'class': 'GenericError', 'desc': 'failure'}}
        payload = b''.join(json.dumps(line).encode() + b'\r\n' for line in lines)
        self.chunks = [payload[:17], payload[17:]]

    def settimeout(self, value):
        assert value > 0

    def recv(self):
        if self.mode == 'malformed':
            return b'invalid JSON\n'
        if self.mode == 'closed':
            return b''
        if self.mode == 'large':
            return b'x' * 2048
        return self.chunks.pop(0)

    def shutdown(self):
        self.closed = True


def test_correlates_fragmented_response_ignores_replay_events(monkeypatch):
    collector = Collector()
    connections = []

    def connect(url, **kwargs):
        assert collector.checked
        assert url == 'ws://127.0.0.1:12345/biflow/platform.ap_qmp.qmp_socket'
        assert kwargs['redirect_limit'] == 0
        connection = Connection()
        connections.append(connection)
        return connection

    monkeypatch.setattr(diagnostics.websocket, 'create_connection', connect)
    helper = diagnostics.QBoxDiagnostics(collector)
    first = helper.query('ap')
    second = helper.query('ap', 'query-version')
    assert first['ignored_messages'] == 3
    assert first['result'] == {'status': 'running'}
    assert first['request_id'] != second['request_id']
    assert first['coherent_snapshot'] is False
    assert all(connection.closed for connection in connections)


@pytest.mark.parametrize('mode,reason', [('malformed', 'JSON'), ('closed', 'closed'),
                                       ('large', 'byte limit'), ('error', 'command failed')])
def test_failure_closes_connection_releases_domain_lock(monkeypatch, mode, reason):
    connection = Connection(mode)
    monkeypatch.setattr(diagnostics.websocket, 'create_connection', lambda *args, **kwargs: connection)
    helper = diagnostics.QBoxDiagnostics(Collector(), max_bytes=1024)
    with pytest.raises(diagnostics.DiagnosticError, match=reason):
        helper.query('ap')
    assert connection.closed
    assert helper.locks['ap'].acquire(blocking=False)


def test_disallowed_domain_command_busy_and_ownership(monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail('no connection should be created')
    monkeypatch.setattr(diagnostics.websocket, 'create_connection', unexpected)
    collector = Collector()
    helper = diagnostics.QBoxDiagnostics(collector)
    for command in ('stop', 'human-monitor-command', 'qmp_capabilities', 'quit'):
        with pytest.raises(diagnostics.DiagnosticError, match='allowlisted'):
            helper.query('ap', command)
    with pytest.raises(diagnostics.DiagnosticError, match='unavailable'):
        helper.query('rse')
    helper.locks['ap'].acquire()
    with pytest.raises(diagnostics.DiagnosticError, match='in progress'):
        helper.query('ap')
    helper.locks['ap'].release()
    def reject(path):
        raise RuntimeError('owner process identity changed')
    collector._get = reject
    with pytest.raises(diagnostics.DiagnosticError, match='identity changed'):
        helper.query('ap')


def test_wire_limit_and_deadline_apply_before_full_frame_received():
    left, right = socket.socketpair()
    connection = diagnostics.BoundedWebSocket(deadline=time.monotonic() + 1, max_bytes=16)
    connection.sock = left
    try:
        # Server declares a huge frame, then supplies only bounded payload.
        right.sendall(b'\x81\x7f' + (2**32).to_bytes(8, 'big') + b'x' * 32)
        with pytest.raises(diagnostics.DiagnosticError, match='byte limit'):
            connection.recv()
        connection.deadline = time.monotonic() - 1
        with pytest.raises(diagnostics.DiagnosticError, match='deadline'):
            connection._recv(1)
    finally:
        left.close()
        right.close()


def test_router_alias_requires_exact_discovered_name(monkeypatch):
    collector = Collector()
    collector._get = lambda path: {'biflows': ['platform.ap_qmp.qmp_socket.qmp_socket_router']}
    seen = []
    def connect(url, **kwargs):
        seen.append(url)
        return Connection()
    monkeypatch.setattr(diagnostics.websocket, 'create_connection', connect)
    helper = diagnostics.QBoxDiagnostics(collector)
    assert helper.query('ap')['result']['status'] == 'running'
    assert seen == ['ws://127.0.0.1:12345/biflow/platform.ap_qmp.qmp_socket.qmp_socket_router']
    collector._get = lambda path: {'biflows': ['platform.ap_qmp.qmp_socket.qmp_socket_router.foreign']}
    with pytest.raises(diagnostics.DiagnosticError, match='not present'):
        helper.query('ap')
    assert len(seen) == 1


def test_exact_biflow_preferred_when_both_present(monkeypatch):
    collector = Collector()
    collector._get = lambda path: {'biflows': ['platform.ap_qmp.qmp_socket',
                                              'platform.ap_qmp.qmp_socket.qmp_socket_router']}
    def connect(url, **kwargs):
        assert url.endswith('/platform.ap_qmp.qmp_socket')
        return Connection()
    monkeypatch.setattr(diagnostics.websocket, 'create_connection', connect)
    assert diagnostics.QBoxDiagnostics(collector).query('ap')['result']['status'] == 'running'


def test_truncated_replay_prefix_is_ignored_only_before_first_record(monkeypatch):
    class ReplayConnection(Connection):
        def send(self, value):
            super().send(value)
            self.chunks.insert(0, b'old-ring-tail","id":"old-id"}\r\n')
    connection = ReplayConnection()
    monkeypatch.setattr(diagnostics.websocket, 'create_connection', lambda *args, **kwargs: connection)
    result = diagnostics.QBoxDiagnostics(Collector()).query('ap')
    assert result['result']['status'] == 'running'
    assert result['ignored_messages'] == 4
    assert result['replay_prefix_discarded_bytes'] > 0


@pytest.mark.parametrize('matching', [True, False])
def test_malformed_current_or_nonprefix_record_never_passes(monkeypatch, matching):
    class BadConnection(Connection):
        def send(self, value):
            super().send(value)
            bad = b'{"id":"' + self.sent['id'].encode() + b'",INVALID}\n'
            if matching:
                self.chunks.insert(0, bad)
            else:
                self.chunks.insert(0, b'{"event":"RESET"}\ninvalid later replay\n')
    connection = BadConnection()
    monkeypatch.setattr(diagnostics.websocket, 'create_connection', lambda *args, **kwargs: connection)
    with pytest.raises(diagnostics.DiagnosticError, match='JSON'):
        diagnostics.QBoxDiagnostics(Collector()).query('ap')
