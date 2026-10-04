"""Monitor enrichment stays read-only, cached and outside the log thread."""
from pathlib import Path
import sys
import threading

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/run'))
import qbox_stats_monitor as stats


@pytest.fixture
def monitor(monkeypatch):
    monkeypatch.setattr(stats, 'process_identity', lambda *args, **kwargs: (1, 77))
    obj = stats.StatsMonitor(42, {'host': '127.0.0.1', 'port': 18080,
                               'domains': [{'domain_id': 'ap', 'qmp_biflow': 'platform.ap_qmp'}]}, 5)
    monkeypatch.setattr(obj._collector, '_get', lambda path: {'sc_time_stamp': 12.5})
    monkeypatch.setattr(obj._diagnostics, 'query',
                        lambda domain, command: {'result': [{'thread-id': 43}]})
    return obj


def test_unavailable_recovers_without_republishing_stale_time(monitor, monkeypatch):
    monitor._sample()
    assert monitor.snapshot()['sim_time'] == 12.5

    def unavailable(path):
        raise OSError('not ready')

    monkeypatch.setattr(monitor._collector, '_get', unavailable)
    monitor._sample()
    sample = monitor.snapshot()
    assert sample['sim_time'] is None
    assert sample['monotonic'] is None
    assert 'not ready' in sample['error']
    monkeypatch.setattr(monitor._collector, '_get', lambda path: {'sc_time_stamp': 15.})
    monitor._sample()
    assert monitor.snapshot()['sim_time'] == 15.
    assert monitor.snapshot()['error'] is None


def test_qmp_cache_refreshes_when_tid_identity_changes(monitor, monkeypatch):
    queries = []
    def query(domain, command):
        queries.append((domain, command))
        return {'result': [{'thread-id': 43}, {'thread-id': 43}]}
    monkeypatch.setattr(monitor._diagnostics, 'query', query)
    monitor._sample()
    monitor._sample()
    assert queries == [('ap', 'query-cpus-fast')]
    assert monitor.snapshot()['domain_threads'] == {'ap': [43]}
    monkeypatch.setattr(monitor, '_identity', lambda tid: 88)
    monitor._sample()
    assert len(queries) == 2
    monitor._refresh_at = 0
    monitor._sample()
    assert len(queries) == 3


def test_snapshot_is_copy_and_stops_without_waiting_interval(monitor, monkeypatch):
    sampled = threading.Event()
    def get(path):
        assert threading.current_thread().name == 'qbox-stats-monitor'
        sampled.set()
        return {'sc_time_stamp': 9.}
    monkeypatch.setattr(monitor._collector, '_get', get)
    monitor.start()
    assert sampled.wait(1)
    monitor.close()
    assert not monitor._thread.is_alive()
    value = monitor.snapshot()
    value['domain_threads']['fake'] = [999]
    assert 'fake' not in monitor.snapshot()['domain_threads']


def test_qmp_failure_preserves_simulation_and_drops_old_mapping(monitor, monkeypatch):
    monitor._sample()
    monitor._refresh_at = 0
    def fail(*args):
        raise OSError('QMP unavailable')
    monkeypatch.setattr(monitor._diagnostics, 'query', fail)
    monitor._sample()
    sample = monitor.snapshot()
    assert sample['sim_time'] == 12.5
    assert sample['domain_threads'] == {}
    assert sample['error'] == 'QMP unavailable'
