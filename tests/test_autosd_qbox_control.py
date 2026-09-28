import io
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/autosd_dashboard'))
import qbox_control as control


class Collector:
    manifest = {'backend': 'qbox-full'}
    endpoint = {'host': '127.0.0.1', 'port': 18080}
    timeout = 1
    run_id = 'run'

    def __init__(self, times=(1, 1, 1), paused=True):
        self.times = iter(times)
        self.paused = paused

    def _get(self, path):
        if path == '/qk_status':
            return [{'name': 'platform.cpu.qk', 'local_time': '1 ms'}]
        return {'monitor_paused': self.paused} if path == '/sc_suspended' else {'sc_time_stamp': next(self.times)}


def connection(monkeypatch):
    value = Mock()
    value.getresponse.return_value.status = 200
    monkeypatch.setattr(control.http.client, 'HTTPConnection', lambda *a, **kw: value)
    monkeypatch.setattr(control.time, 'sleep', lambda _: None)
    return value


def test_verified_pause_and_resume(monkeypatch):
    conn = connection(monkeypatch)
    assert control.control(Collector(), 'pause')['status'] == 'PASS'
    assert control.control(Collector((1, 1, 2), False), 'resume')['status'] == 'PASS'
    assert [call.args[1] for call in conn.request.call_args_list] == ['/pause', '/continue']


def test_timeout_mutation_never_retried(monkeypatch):
    conn = connection(monkeypatch)
    conn.getresponse.side_effect = TimeoutError('timeout')
    assert control.control(Collector(), 'pause')['status'] == 'UNKNOWN'
    assert conn.request.call_count == 1


def test_moving_pause_is_unknown(monkeypatch):
    connection(monkeypatch)
    assert control.control(Collector((1, 1, 2)), 'pause')['status'] == 'UNKNOWN'


def test_owner_rejected_before_mutation(monkeypatch):
    conn = connection(monkeypatch)
    collector = Collector()
    collector._get = Mock(side_effect=ValueError('wrong owner'))
    with pytest.raises(ValueError, match='wrong owner'):
        control.control(collector, 'pause')
    conn.request.assert_not_called()


def test_qualification_requires_watchdog_proof(monkeypatch, tmp_path):
    app = SimpleNamespace(backend='qbox-full', vm_job='run', running=lambda: True,
                          simulator=SimpleNamespace(collector=Collector()), persist=lambda j: None,
                          qbox_pause_run=None)
    monkeypatch.setattr(control, 'control', lambda *a: {'status': 'PASS'})
    monkeypatch.setattr(control, '_clock', lambda _: 1)
    monkeypatch.setattr(control.time, 'sleep', lambda _: None)
    monkeypatch.setattr(control.watchdog, 'boot_snapshot', lambda *a: {'status': 'ONLINE', 'boot_id': 'old'})
    monkeypatch.setattr(control.watchdog, 'run_command', lambda *a, **kw: 0)
    monkeypatch.setattr(control.watchdog, 'expiry', lambda *a: {'status': 'FAIL'})
    job = {'id': 'qualification', 'evidence_path': str(tmp_path)}
    assert control.run(app, job, io.BytesIO())['status'] == 'FAIL'
    assert app.qbox_pause_run is None
    def expiry(_app, original_job, _log, wd_directory, remote):
        assert original_job is job
        assert original_job['evidence_path'] == str(tmp_path)
        assert wd_directory == tmp_path / 'watchdog'
        return {'status': 'PASS', 'after': {'boot_id': 'new'}}
    monkeypatch.setattr(control.watchdog, 'expiry', expiry)
    result = control.run(app, job, io.BytesIO())
    assert result['status'] == 'PASS' and len(result['cycles']) == 10
    assert app.qbox_pause_run == 'run' and result['after_boot_id'] == 'new'
    assert (tmp_path / 'qualification.json').is_file()


@pytest.mark.parametrize('unknown_action', ['pause', 'resume'])
def test_qualification_preserves_unknown_for_recovery(monkeypatch, tmp_path, unknown_action):
    app = SimpleNamespace(backend='qbox-full', vm_job='run', running=lambda: True,
                          simulator=SimpleNamespace(collector=Collector()), persist=lambda j: None,
                          qbox_pause_run=None)
    calls = []
    def fake_control(_collector, action):
        calls.append(action)
        return {'status': 'UNKNOWN' if action == unknown_action else 'PASS'}
    monkeypatch.setattr(control, 'control', fake_control)
    monkeypatch.setattr(control, '_clock', lambda _: 1)
    monkeypatch.setattr(control.time, 'sleep', lambda _: None)
    monkeypatch.setattr(control.watchdog, 'boot_snapshot', lambda *a: {'status': 'ONLINE', 'boot_id': 'old'})
    result = control.run(app, {'id': 'qualification', 'evidence_path': str(tmp_path)}, io.BytesIO())
    assert result['status'] == 'UNKNOWN' and result['pause_state_unknown'] is True
    assert calls.count(unknown_action) == 1
    assert app.qbox_pause_run is None


@pytest.mark.parametrize('cleanup_status', ['PASS', 'UNKNOWN'])
def test_failed_paused_read_records_cleanup_state(monkeypatch, tmp_path, cleanup_status):
    app = SimpleNamespace(backend='qbox-full', vm_job='run', running=lambda: True,
                          simulator=SimpleNamespace(collector=Collector()), persist=lambda j: None,
                          qbox_pause_run=None)
    calls = []
    def fake_control(_collector, action):
        calls.append(action)
        return {'status': 'PASS' if action == 'pause' else cleanup_status}
    monkeypatch.setattr(control, 'control', fake_control)
    monkeypatch.setattr(control, '_clock', Mock(side_effect=ValueError('snapshot lost')))
    monkeypatch.setattr(control.watchdog, 'boot_snapshot', lambda *a: {'status': 'ONLINE', 'boot_id': 'old'})
    result = control.run(app, {'id': 'qualification', 'evidence_path': str(tmp_path)}, io.BytesIO())
    assert calls == ['pause', 'resume']
    assert result['pause_state_unknown'] == (cleanup_status == 'UNKNOWN')
    assert result['status'] == ('UNKNOWN' if cleanup_status == 'UNKNOWN' else 'FAIL')


def test_cpu_time_unit_normalization():
    collector = Collector()
    collector._get = lambda _: [{'name': 'cpu', 'local_time': '1000 us'}]
    first = control._cpu_times(collector)
    collector._get = lambda _: [{'name': 'cpu', 'local_time': '1 ms'}]
    assert first == control._cpu_times(collector)


def test_freerunning_cpu_rejects_pause_qualification(monkeypatch, tmp_path):
    app = SimpleNamespace(backend='qbox-full', vm_job='run', running=lambda: True,
                          simulator=SimpleNamespace(collector=Collector()), persist=lambda j: None,
                          qbox_pause_run=None)
    calls = []
    def fake_control(_collector, action):
        calls.append(action)
        return {'status': 'PASS'}
    monkeypatch.setattr(control, 'control', fake_control)
    monkeypatch.setattr(control, '_clock', lambda _: 1)
    monkeypatch.setattr(control, '_cpu_times', Mock(side_effect=[{'cpu': '1'}, {'cpu': '2'}]))
    monkeypatch.setattr(control.time, 'sleep', lambda _: None)
    monkeypatch.setattr(control.watchdog, 'boot_snapshot', lambda *a: {'status': 'ONLINE', 'boot_id': 'old'})
    result = control.run(app, {'id': 'qualification', 'evidence_path': str(tmp_path)}, io.BytesIO())
    assert result['status'] == 'FAIL' and 'CPU local time advanced' in result['error']
    assert calls == ['pause', 'resume'] and app.qbox_pause_run is None
