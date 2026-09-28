"""Monitor collection: real loopback HTTP, identity, bounds and session semantics."""
import importlib.util
import json
import os
from pathlib import Path
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

PATH = Path(__file__).resolve().parents[1] / 'scripts/autosd_dashboard/qbox_monitor.py'
spec = importlib.util.spec_from_file_location('qbox_monitor', PATH)
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)


@pytest.fixture
def endpoint():
    responses = {'/sc_time': {'sc_time_stamp': 1.25}, '/sc_suspended': {'sc_suspended': False},
                 '/qk_status': [{'name': 'top.ap.cpu0.qk', 'state': 'RUNNING',
                                 'local_time': '1251 ms', 'quantum_time': '1 ms'}],
                 '/mcips_plugin_status': [], '/api/v1/objects': {'schema_version': 1, 'objects': []},
                 '/api/v1/injection/capabilities': (403, {'error': 'mutation-disabled'})}
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            requests.append(self.path)
            value = responses.get(self.path, (404, {}))
            status, value = value if isinstance(value, tuple) else (200, value)
            if callable(value):
                value = value()
            body = value if isinstance(value, bytes) else json.dumps(value).encode()
            self.send_response(status)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
            except BrokenPipeError:
                pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    manifest = {'run_id': 'run-A', 'backend': 'qbox-full',
                'monitor': {'host': '127.0.0.1', 'port': server.server_port,
                            'owner_pid': os.getpid(), 'owner_start_ticks': monitor.process_identity(os.getpid())[1]},
                'domains': [{'domain_id': 'ap', 'qemu_instance_path': 'top.ap',
                             'cpu_object_paths': ['top.ap.cpu0']}]}
    yield manifest, responses, requests
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def test_collection_units_optional_disabled_cache_and_rate(endpoint, monkeypatch, tmp_path):
    manifest, responses, requests = endpoint
    collector = monitor.QBoxMonitorCollector(manifest, evidence_dir=tmp_path)
    first = collector.sample()
    assert first['status'] == 'ONLINE'
    assert first['sim_time_ns'] == 1250000000
    assert first['speed_ratio'] is None
    cpu = first['domains'][0]['cpus'][0]
    assert cpu['local_time_ns'] == 1251000000
    assert cpu['quantum_offset_ns'] == 1000000
    assert 'not CPU utilization' in cpu['state_semantics']
    assert collector.capabilities()['features']['injection']['available'] is False
    assert '403' in collector.capabilities()['features']['injection']['reason']
    before = len(requests)
    for _ in range(3):
        assert collector.snapshot()['sample_seq'] == 1
        collector.sample()
    assert len(requests) == before
    responses['/sc_time']['sc_time_stamp'] = 2.25
    assert collector.sample(force=True)['speed_ratio'] > 0
    assert requests.count('/api/v1/objects') == 1
    assert len((tmp_path / 'simulator.jsonl').read_text().splitlines()) == 2
    collector._last_success -= 10
    assert collector.snapshot()['status'] == 'STALE'


@pytest.mark.parametrize('value,reason', [((503, {}), '503'), (b'not json', 'JSON'),
                                          ({'sc_time_stamp': -1}, 'timestamp'),
                                          ({'sc_time_stamp': float('nan')}, 'timestamp'),
                                          ({'sc_time_stamp': True}, 'timestamp')])
def test_protocol_failure_and_backoff(endpoint, value, reason):
    manifest, responses, requests = endpoint
    collector = monitor.QBoxMonitorCollector(manifest)
    responses['/sc_time'] = value
    result = collector.sample()
    assert result['status'] == 'OFFLINE'
    assert reason in result['error']
    collector.sample()
    assert len(requests) == 1


def test_response_limit_timeout_and_measurement_barrier(endpoint):
    manifest, responses, requests = endpoint
    collector = monitor.QBoxMonitorCollector(manifest, max_body=32, timeout=.05)
    assert collector.sample(measurement_active=True)['sample_seq'] == 0
    assert requests == []
    responses['/sc_time'] = b'x' * 33
    assert 'body limit' in collector.sample()['error']
    responses['/sc_time'] = lambda: (time.sleep(.2) or {})
    started = time.monotonic()
    assert collector.sample(force=True)['status'] == 'OFFLINE'
    assert time.monotonic() - started < 1


def test_identity_change_and_foreign_listener_never_requested(endpoint):
    manifest, _, requests = endpoint
    manifest['monitor']['owner_start_ticks'] += 1
    assert 'identity changed' in monitor.QBoxMonitorCollector(manifest).sample()['error']
    assert requests == []
    manifest['monitor']['owner_pid'] = os.getppid()
    manifest['monitor']['owner_start_ticks'] = monitor.process_identity(os.getppid())[1]
    manifest['launcher_pid'] = os.getpid()
    manifest['launcher_start_ticks'] = monitor.process_identity(os.getpid())[1]
    assert 'outside managed launcher' in monitor.QBoxMonitorCollector(manifest).sample()['error']
    assert requests == []


def test_foreign_socket_fake_proc(tmp_path):
    (tmp_path / 'net').mkdir()
    (tmp_path / 'net/tcp').write_text('header\n 0: 0100007F:1234 0:0 0A 0 0 0 0 0 777\n')
    owner = tmp_path / '42'
    owner.mkdir()
    (owner / 'fd').mkdir()
    (owner / 'stat').write_text('42 (owner with spaces) S 1 ' + '0 ' * 17 + '123 0')
    assert monitor.process_identity(42, tmp_path) == (1, 123)
    with pytest.raises(monitor.MonitorError, match='outside'):
        monitor.verify_listener('127.0.0.1', 0x1234, 42, 123, tmp_path)
    (owner / 'fd/3').symlink_to('socket:[777]')
    monitor.verify_listener('127.0.0.1', 0x1234, 42, 123, tmp_path)


def test_read_only_paths_time_regression_evidence_and_metadata(endpoint, tmp_path):
    manifest, responses, requests = endpoint
    collector = monitor.QBoxMonitorCollector(manifest, evidence_dir=tmp_path, evidence_quota=1)
    collector.sample()
    assert collector.snapshot()['evidence_dropped'] == 1
    responses['/sc_time']['sc_time_stamp'] = .5
    assert collector.sample(force=True)['speed_ratio'] is None
    with pytest.raises(monitor.MonitorError, match='allowlisted'):
        collector._get('/pause')
    with pytest.raises(monitor.MonitorError, match='invalid object'):
        collector.objects('../pause')
    assert collector.objects()['schema_version'] == 1
    assert '/object/' not in requests
    other = monitor.QBoxMonitorCollector(dict(manifest, run_id='run-B'))
    assert other.snapshot()['sample_seq'] == 0
    assert other.sample()['speed_ratio'] is None
    assert collector.snapshot()['run_id'] == 'run-A'


@pytest.mark.parametrize('value,expected', [('1.25 us', 1250), ('100 ps', 0), ('-1 ns', None),
                                          ('nan s', None), ('1 bananas', None)])
def test_systemc_time_parsing(value, expected):
    assert monitor.time_string_ns(value) == expected


def test_kernel_suspension_is_not_user_pause(endpoint):
    manifest, responses, _ = endpoint
    collector = monitor.QBoxMonitorCollector(manifest)
    responses['/sc_suspended'] = {'sc_suspended': True}
    assert collector.sample()['status'] == 'ONLINE'
    responses['/sc_suspended']['monitor_paused'] = True
    result = collector.sample(force=True)
    assert result['status'] == 'PAUSED'
    assert result['sc_suspended'] is True


def test_optional_transient_discovery_retries_after_backoff_only(endpoint):
    manifest, responses, requests = endpoint
    responses['/api/v1/objects'] = (503, {})
    collector = monitor.QBoxMonitorCollector(manifest)
    collector.sample(force=True)
    assert collector.snapshot()['status'] == 'ONLINE'
    responses['/api/v1/objects'] = {'schema_version': 1, 'objects': []}
    collector.sample(force=True)
    assert requests.count('/api/v1/objects') == 1
    collector._discovery_retry_at['metadata'] = 0
    collector.sample(force=True)
    assert requests.count('/api/v1/objects') == 2
    assert collector.capabilities()['features']['metadata']['available'] is True
    assert requests.count('/api/v1/injection/capabilities') == 1
    assert collector.snapshot()['last_success_monotonic'] > 0
