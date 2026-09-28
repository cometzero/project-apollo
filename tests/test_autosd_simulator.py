"""Session/measurement isolation around the single simulator supervisor."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def setup(monkeypatch, tmp_path):
    directory = Path(__file__).resolve().parents[1] / 'scripts/autosd_dashboard'
    monkeypatch.syspath_prepend(str(directory))
    spec = importlib.util.spec_from_file_location('simulator_test', directory / 'simulator.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    simulator = module.Simulator(SimpleNamespace(qbox_diagnostics=True))
    context = {'run_id': 'run-A', 'backend': 'qbox-full', 'running': True,
               'blocked': False, 'pid': 123, 'feature_session': 1,
               'directory': tmp_path, 'domain_boot': {'domains': []}, 'guest': {}}
    simulator.context = lambda: dict(context)
    simulator.key = 'run-A'

    class Collector:
        calls = 0
        sample_seq = 1
        manifest = {'domains': []}

        def sample(self):
            self.calls += 1
            return {'status': 'ONLINE', 'sample_seq': self.sample_seq, 'run_id': 'run-A'}

        def capabilities(self):
            return {'features': {}}

        def objects(self, parent):
            self.calls += 1
            return {'object': parent}

    collector = Collector()
    simulator.collector = collector
    return module, simulator, context, collector


def test_new_run_clears_value_history_and_collector_even_while_blocked(setup):
    _, simulator, context, _ = setup
    simulator.value = {'status': 'ONLINE', 'sim_time_ns': 1234}
    simulator.history.append({'sample_seq': 1})
    simulator.events.append({'seq': 1})
    simulator.diagnostic_client = object()
    context.update(run_id='run-B', blocked=True)
    assert simulator.snapshot()['status'] == 'WAITING'
    simulator.tick()
    assert simulator.value['status'] == 'WAITING'
    assert 'sim_time_ns' not in simulator.value
    assert simulator.collector is None
    assert simulator.diagnostic_client is None
    assert not simulator.history and not simulator.events


def test_history_deduplicates_cached_sample_and_barrier_skips_traffic(setup):
    _, simulator, context, collector = setup
    simulator.tick()
    simulator.tick()
    assert len(simulator.history) == 1
    collector.sample_seq = 2
    simulator.tick()
    assert len(simulator.history) == 2
    context['blocked'] = True
    simulator.tick()
    assert collector.calls == 3
    assert simulator.snapshot()['status'] == 'DEFERRED'
    context.update(blocked=False, running=False)
    assert simulator.snapshot()['status'] == 'OFFLINE'
    assert simulator.snapshot()['historical'] is True


def test_objects_rechecks_context_after_acquiring_io_lock(setup):
    _, simulator, context, collector = setup
    class BarrierLock:
        def acquire(self, blocking=False):
            context['blocked'] = True
            return True
        def release(self):
            pass
    simulator.io_lock = BarrierLock()
    with pytest.raises(ValueError, match='measurement'):
        simulator.objects()
    assert collector.calls == 0


def test_diagnostics_client_cached_and_stale_response_rejected(setup, monkeypatch):
    module, simulator, context, collector = setup
    created = []
    class Client:
        def __init__(self, owner):
            assert owner is collector
            created.append(self)
        def query(self, domain, command):
            assert domain == 'ap'
            return {'command': command}
    monkeypatch.setattr(module, 'QBoxDiagnostics', Client)
    assert simulator.diagnostics('ap')['command'] == 'query-status'
    assert simulator.diagnostics('ap', 'query-version')['command'] == 'query-version'
    assert len(created) == 1
    def delayed(*args):
        context['feature_session'] = 2
        return {'command': 'query-status'}
    created[0].query = delayed
    with pytest.raises(ValueError, match='session changed'):
        simulator.diagnostics('ap')


def test_late_sample_cannot_update_new_epoch(setup):
    _, simulator, context, collector = setup
    def delayed():
        context['feature_session'] = 2
        return {'sample_seq': 99, 'status': 'ONLINE'}
    collector.sample = delayed
    simulator.tick()
    assert simulator.value['status'] == 'OFFLINE'
    assert not simulator.history


def test_qemu_unsupported_and_guest_boot_event_is_distinct(setup):
    _, simulator, context, _ = setup
    context['guest'] = {'status': 'ONLINE', 'boot_id': 'guest-A'}
    simulator.tick()
    context['guest']['boot_id'] = 'guest-B'
    simulator.tick()
    assert [event['details']['boot_id'] for event in simulator.events] == ['guest-A', 'guest-B']
    assert all(event['run_id'] == 'run-A' for event in simulator.events)
    context['backend'] = 'qemu'
    assert simulator.snapshot()['status'] == 'UNSUPPORTED'


def test_model_log_tail_incremental_partial_rotation_and_timestamps(setup):
    _, simulator, context, _ = setup
    path = context['directory'] / 'vm/qbox-platform.log'
    path.parent.mkdir()
    path.write_text('Info: model: {"schema":"qbox-injection-trace/v1","event":"applied",'
                    '"id":1,"applied_sim_time_ns":123}\n'
                    'platform.ap_watchdog ws0=1 ws1=0 sc_time=2 us\npartial')
    simulator.tick()
    assert [event['sim_time_ns'] for event in simulator.events] == [123, 2000]
    assert all(event['source'] == 'model-log' for event in simulator.events)
    simulator.tick()
    assert len(simulator.events) == 2
    path.write_text('rotated\n')
    simulator.tick()
    assert simulator.events[-1]['kind'] == 'log-gap'


def test_diagnostics_requires_explicit_opt_in(setup):
    _, simulator, _, _ = setup
    simulator.app.qbox_diagnostics = False
    with pytest.raises(ValueError, match='opt-in'):
        simulator.diagnostics('ap')


def test_busy_io_never_waits_or_queries(setup):
    _, simulator, _, collector = setup
    class HeldLock:
        def acquire(self, blocking=True):
            assert blocking is False, 'I/O lock must never wait'
            return False
        def release(self):
            pytest.fail('must not release another owner lock')
    simulator.io_lock = HeldLock()
    with pytest.raises(ValueError, match='busy'):
        simulator.objects()
    with pytest.raises(ValueError, match='busy'):
        simulator.diagnostics('ap')
    simulator.tick()
    assert collector.calls == 0


def test_accepted_sample_epoch_sidecar_and_cached_sample_keep_old_epoch(setup):
    _, simulator, context, collector = setup
    context['guest'] = {'boot_id': 'guest-A'}
    context['domain_boot'] = {'domains': [{'id': 'ap', 'boot_epoch': 1}]}
    simulator.tick()
    context['feature_session'] = 2
    context['guest']['boot_id'] = 'guest-B'
    context['domain_boot']['domains'][0]['boot_epoch'] = 2
    simulator.tick()
    assert simulator.value['feature_session'] == 1
    collector.sample_seq = 2
    simulator.tick()
    assert simulator.value['feature_session'] == 2
    assert simulator.value['guest_boot_id'] == 'guest-B'
    assert simulator.value['domain_epochs']['ap'] == 2
    records = [json.loads(line) for line in (context['directory'] / 'simulator-session.jsonl').read_text().splitlines()]
    assert [record['feature_session'] for record in records] == [1, 2]


def test_post_action_drain_works_when_vm_stopped_without_network(setup):
    _, simulator, context, collector = setup
    path = context['directory'] / 'vm/qbox-platform.log'
    path.parent.mkdir()
    path.write_text('platform.ap_watchdog ws0=1 ws1=1 sc_time=3 us\n')
    context['running'] = False
    result = simulator.finish_evidence({'id': 'shutdown-job', 'log_session': 'run-A'})
    assert result['status'] == 'OFFLINE'
    assert result['events'][0]['sim_time_ns'] == 3000
    assert result['synchronous_post_action_sample'] is False
    assert collector.calls == 0
    context['run_id'] = 'run-B'
    assert simulator.finish_evidence({'id': 'old-job', 'log_session': 'run-A'})['status'] == 'STALE_SESSION'


def test_post_reset_log_session_does_not_replace_vm_run_identity(setup):
    _, simulator, _, _ = setup
    result = simulator.finish_evidence({'id': 'reboot-job', 'log_session': 'reboot-job',
                                       'vm_run_id': 'run-A'})
    assert result['run_id'] == 'run-A'
    assert result['status'] != 'STALE_SESSION'


def test_evidence_disk_failure_keeps_live_snapshot(setup, monkeypatch):
    _, simulator, context, _ = setup
    context['guest'] = {'status': 'ONLINE', 'boot_id': 'guest-A'}
    original = Path.open
    def reject_writes(path, mode='r', *args, **kwargs):
        if mode in ('a', 'w'):
            raise OSError('disk full')
        return original(path, mode, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', reject_writes)
    simulator.tick()
    snapshot = simulator.snapshot()
    assert snapshot['status'] == 'ONLINE'
    assert snapshot['evidence_warning'] == 'disk full'
    assert snapshot['event_storage_dropped'] == 1
    assert snapshot['events'][0]['kind'] == 'guest-boot'


def test_freshness_uses_monotonic_not_wall_clock(setup, monkeypatch):
    module, simulator, _, _ = setup
    simulator.value = {'status': 'ONLINE', 'last_success_at': 10000,
                       'last_success_monotonic': 10}
    monkeypatch.setattr(module.time, 'time', lambda: 1)
    monkeypatch.setattr(module.time, 'monotonic', lambda: 20)
    snapshot = simulator.snapshot()
    assert snapshot['age_ms'] == 10000
    assert snapshot['status'] == 'STALE'
