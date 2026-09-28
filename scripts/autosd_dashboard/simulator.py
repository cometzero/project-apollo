"""Session-scoped QBox observation; independent from the guest SSH sampler."""
from collections import deque
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import json
import re
from pathlib import Path
import threading
import time

from qbox_monitor import QBoxMonitorCollector, process_identity, time_string_ns
from qbox_diagnostics import QBoxDiagnostics


def load(path):
    try:
        value = json.loads(path.read_text())
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


class Simulator:
    def __init__(self, app):
        self.app = app
        self.lock = threading.RLock()
        self.io_lock = threading.Lock()
        self.collector = None
        self.diagnostic_client = None
        self.key = None
        self.history = deque(maxlen=120)
        self.events = deque(maxlen=500)
        self.sequence = 0
        self.event_storage_dropped = 0
        self.previous_domains = {}
        self.previous_guest = None
        self.log_cursor = None
        self.log_offset = 0
        self.log_pending = b''
        self.value = {"status": "OFFLINE", "cpus": [], "domains": []}

    def context(self):
        app = self.app
        with app.lock:
            boot = next((j for j in app.jobs if j['id'] == app.vm_job), None)
            active = next((j for j in app.jobs if j['id'] == app.active), {})
            return {"run_id": app.vm_job, "backend": app.backend,
                    "running": app.running(), "pid": getattr(app.vm_process, 'pid', None) if app.running() else None,
                    "blocked": active.get('action') in app.simulator_barriers or app.vm_paused,
                    "feature_session": app.feature_session,
                    "directory": Path(boot['evidence_path']) if boot else None,
                    "domain_boot": app.domain_boot(), "guest": dict(app.monitoring)}

    def snapshot(self):
        context = self.context()
        with self.lock:
            if self.key != context['run_id'] or context['backend'] == 'qemu':
                return {"status": "UNSUPPORTED" if context['backend'] == 'qemu' else "WAITING",
                        "run_id": context['run_id'], "cpus": [], "domains": [], "history": [], "events": []}
            value = dict(self.value)
            value['last_sample_feature_session'] = value.get('feature_session')
            value['feature_session'] = context['feature_session']
            if value.get('last_success_monotonic') is not None:
                value['age_ms'] = max(0, (time.monotonic() - value['last_success_monotonic']) * 1000)
                if value.get('status') == 'ONLINE' and value['age_ms'] > 6000:
                    value['status'] = 'STALE'
            if not context['running']:
                value.update(status='OFFLINE', historical=True)
            elif getattr(self.app, 'vm_paused', False):
                value.update(status='PAUSED', reason='Explicit SystemC Pause; last observation retained')
            elif context['blocked']:
                value.update(status='DEFERRED', reason='Measurement or lifecycle barrier')
            value.update(history=list(self.history), events=list(self.events), run_id=self.key,
                         event_storage_dropped=self.event_storage_dropped)
            return value

    def finish_evidence(self, job):
        """Drain a bounded model-log batch after the action barrier is released.

        No endpoint traffic is issued here. Retained simulator measurements are
        explicitly last-known, not proof of post-action synchronous readiness.
        """
        context = self.context()
        expected_run = job.get('vm_run_id', job.get('log_session'))
        if expected_run != context['run_id']:
            return {'status': 'STALE_SESSION', 'run_id': expected_run,
                    'observation_provenance': 'job run is no longer current'}
        with self.lock:
            if self.key == expected_run and context['directory'] is not None:
                self.model_log_events(context)
        result = self.snapshot()
        if result.get('run_id') != expected_run:
            return {'status': 'STALE_SESSION', 'run_id': expected_run}
        result.update(job_id=job['id'], observation_provenance='last-known simulator sample; bounded post-action model-log drain',
                      synchronous_post_action_sample=False)
        return result

    def capabilities(self):
        context = self.context()
        with self.lock:
            if self.collector and self.key == context['run_id'] and context['running']:
                value = self.collector.capabilities()
                features = value['features']
                qualified = getattr(self.app, 'qbox_pause_run', None) == self.key
                features['pause'] = {'available': qualified, 'qualified': qualified,
                                     'reason': 'current run qualification PASS' if qualified else 'run qualification required'}
                features['qmp'] = {'available': bool(getattr(self.app, 'qbox_diagnostics', False)),
                                   'qualified': False, 'reason': 'read-only; each domain response verified on demand'}
                return value
        return {"status": "UNSUPPORTED" if context['backend'] == 'qemu' else 'WAITING',
                "run_id": context['run_id'], "pause": {"available": False, "qualified": False},
                "injection": {"available": False, "qualified": False}}

    def event(self, context, kind, details, *, source='dashboard-observation', sim_time_ns=None):
        self.sequence += 1
        event = {"seq": self.sequence, "run_id": self.key, "source": source,
                 "kind": kind, "observed_at": datetime.now(timezone.utc).isoformat(),
                 "host_monotonic": time.monotonic(), "details": details}
        if sim_time_ns is not None:
            event['sim_time_ns'] = sim_time_ns
        self.events.append(event)
        path = context['directory'] / 'simulator-events.jsonl'
        line = json.dumps(event) + '\n'
        try:
            if (path.stat().st_size if path.exists() else 0) + len(line.encode()) <= 8 * 1024 * 1024:
                with path.open('a') as stream:
                    stream.write(line)
            else:
                self.event_storage_dropped += 1
        except OSError as error:
            self.value['evidence_warning'] = str(error)
            self.event_storage_dropped += 1

    def model_log_events(self, context):
        """Incremental bounded tail of this run's fixed platform log only."""
        path = context['directory'] / 'vm/qbox-platform.log'
        if not path.exists():
            path = context['directory'] / 'vm/full-system/qbox-platform.log'
        try:
            info = path.stat()
            identity = (info.st_dev, info.st_ino)
            if ((self.log_cursor is not None and identity != self.log_cursor)
                    or info.st_size < self.log_offset):
                self.log_offset = 0
                self.log_pending = b''
                self.event(context, 'log-gap', {'reason': 'platform log replaced or truncated'})
            self.log_cursor = identity
            with path.open('rb') as stream:
                stream.seek(self.log_offset)
                chunk = stream.read(256 * 1024)
                self.log_offset = stream.tell()
        except OSError:
            return
        lines = (self.log_pending + chunk).split(b'\n')
        self.log_pending = lines.pop()
        if len(self.log_pending) > 64 * 1024:
            self.log_pending = b''
            self.event(context, 'log-gap', {'reason': 'platform log line exceeds limit'})
        accepted = 0
        for raw in lines:
            line = raw.decode('utf-8', errors='replace')
            value = None
            start = line.find('{"schema":"qbox-injection-trace/v1"')
            if start >= 0:
                try:
                    value, _ = json.JSONDecoder().raw_decode(line[start:])
                except ValueError:
                    continue
                kind = 'injection-' + str(value.get('event', 'unknown'))
                stamp = value.get('sim_time_ns', value.get('cleared_sim_time_ns',
                                  value.get('applied_sim_time_ns', value.get('requested_sim_time_ns'))))
            else:
                match = re.search(r'([\w.]*watchdog[\w.]*) ws0=([01]) ws1=([01]) sc_time=(.+)$', line)
                if match:
                    value = {'model': match[1], 'ws0': int(match[2]), 'ws1': int(match[3]),
                             'sim_time_raw': match[4], 'precision': 'producer-text'}
                    stamp = time_string_ns(match[4])
                    kind = 'watchdog-stage'
            if value is not None:
                accepted += 1
                if accepted > 128:
                    continue
                self.event(context, kind, value, source='model-log', sim_time_ns=stamp)
        if accepted > 128:
            self.event(context, 'log-gap', {'reason': 'model event batch limit', 'dropped': accepted - 128})

    @contextmanager
    def try_io(self, *, required=True):
        acquired = self.io_lock.acquire(blocking=False)
        if not acquired and required:
            raise ValueError('Simulator busy; another query or scenario owns monitor I/O')
        try:
            yield acquired
        finally:
            if acquired:
                self.io_lock.release()

    def objects(self, parent=''):
        with self.try_io():
            context = self.context()
            if not context['running'] or context['blocked']:
                raise ValueError('Simulator unavailable or measurement/control in progress')
            with self.lock:
                collector = self.collector if self.key == context['run_id'] else None
            if not collector:
                raise ValueError('Monitor not ready')
            result = collector.objects(parent)
            after = self.context()
            if (after['run_id'] != context['run_id'] or after['blocked']
                    or not after['running'] or after['feature_session'] != context['feature_session']):
                raise ValueError('Simulator session changed')
            return result

    def diagnostics(self, domain, command='query-status'):
        if not getattr(self.app, 'qbox_diagnostics', False):
            raise ValueError('QMP diagnostics disabled; requires launch opt-in')
        with self.try_io():
            context = self.context()
            if not context['running'] or context['blocked']:
                raise ValueError('Simulator unavailable or measurement/control in progress')
            with self.lock:
                collector = self.collector if self.key == context['run_id'] else None
                if collector is None:
                    raise ValueError('Monitor not ready')
                if self.diagnostic_client is None:
                    self.diagnostic_client = QBoxDiagnostics(collector)
                client = self.diagnostic_client
            result = client.query(domain, command)
            after = self.context()
            if (after['run_id'] != context['run_id'] or after['blocked']
                    or not after['running'] or after['feature_session'] != context['feature_session']):
                raise ValueError('Simulator session changed')
            return result

    def tick(self):
        context = self.context()
        if context['backend'] == 'qemu' or not context['run_id']:
            return
        with self.lock:
            if self.key != context['run_id']:
                self.key = context['run_id']
                self.collector = None
                self.diagnostic_client = None
                self.value = {"status": "WAITING", "run_id": self.key, "cpus": [], "domains": []}
                self.history.clear()
                self.events.clear()
                self.previous_domains.clear()
                self.previous_guest = None
                self.log_cursor = None
                self.log_offset = 0
                self.log_pending = b''
                self.sequence = 0
                self.event_storage_dropped = 0
            if not context['running'] or context['blocked']:
                return
            collector = self.collector
        if collector is None:
            directory = context['directory'] / 'vm'
            manifest = load(directory / 'launch.json')
            runtime = load(directory / 'monitor-runtime.json')
            monitor = dict(manifest.get('monitor', {}))
            monitor.update(host=runtime.get('host'), port=runtime.get('port'),
                           owner_pid=runtime.get('pid'), owner_start_ticks=runtime.get('start_ticks'))
            if runtime.get('status') != 'READY':
                with self.lock:
                    self.value = {"status": "WAITING", "reason": runtime.get('error', 'Monitor startup'),
                                  "cpus": [], "domains": []}
                return
            manifest.update(run_id=context['run_id'], backend=context['backend'], monitor=monitor,
                            domains=monitor.get('domains', manifest.get('domains', [])))
            # Anchor ownership to the launcher owned by this dashboard, not a cached PID alone.
            manifest['launcher_pid'] = context['pid']
            manifest['launcher_start_ticks'] = process_identity(context['pid'])[1]
            collector = QBoxMonitorCollector(manifest, evidence_dir=context['directory'])
            with self.lock:
                if self.key != context['run_id']:
                    return
                self.collector = collector
        with self.try_io(required=False) as acquired:
            if not acquired:
                return
            current = self.context()
            if current['blocked'] or current['run_id'] != context['run_id'] or not current['running']:
                return
            sample = collector.sample()
        after = self.context()
        if (after['run_id'] != context['run_id'] or not after['running'] or after['blocked']
                or after['feature_session'] != context['feature_session']):
            return
        with self.lock:
            sample = deepcopy(sample)
            is_new = not self.history or self.history[-1].get('sample_seq') != sample.get('sample_seq')
            # Raw collector records remain in simulator.jsonl; this sidecar ties
            # accepted sequence IDs to the independently observed boot epochs.
            epoch_context = after if is_new else None
            prior = self.history[-1] if not is_new else {}
            sample['feature_session'] = epoch_context['feature_session'] if is_new else prior.get('feature_session')
            sample['guest_boot_id'] = epoch_context['guest'].get('boot_id') if is_new else prior.get('guest_boot_id')
            sample['guest_boot_id_source'] = 'guest-ssh-observation'
            epochs = ({row['id']: row.get('boot_epoch')
                       for row in (after['domain_boot'] or {}).get('domains', []) if row.get('id')}
                      if is_new else prior.get('domain_epochs', {}))
            sample['domain_epochs'] = epochs
            for domain in sample.get('domains', []):
                domain_id = domain.get('domain_id')
                if domain_id in epochs:
                    domain.update(boot_epoch=epochs[domain_id], epoch_source='firmware-log-observation')
            self.value = sample
            self.model_log_events(after)
            if is_new:
                self.history.append(dict(sample))
                sidecar = context['directory'] / 'simulator-session.jsonl'
                record = {key: sample.get(key) for key in ('run_id', 'sample_seq', 'feature_session',
                           'guest_boot_id', 'guest_boot_id_source', 'domain_epochs')}
                record['domain_epoch_source'] = 'firmware-log-observation'
                line = json.dumps(record) + '\n'
                try:
                    if (sidecar.stat().st_size if sidecar.exists() else 0) + len(line.encode()) <= 8 * 1024 * 1024:
                        with sidecar.open('a') as stream:
                            stream.write(line)
                    else:
                        self.value['session_evidence_dropped'] = True
                except OSError as error:
                    self.value['evidence_warning'] = str(error)
                    self.value['session_evidence_dropped'] = True
            try:
                (context['directory'] / 'simulator-capabilities.json').write_text(json.dumps(collector.capabilities()) + '\n')
            except OSError as error:
                self.value['evidence_warning'] = str(error)
            for domain in (after['domain_boot'] or {}).get('domains', []):
                identity = (domain.get('boot_epoch'), domain.get('status'))
                if self.previous_domains.get(domain['id']) != identity:
                    self.event(after, 'domain-boot', domain)
                    self.previous_domains[domain['id']] = identity
            guest = after['guest']
            if guest.get('status') == 'ONLINE' and guest.get('boot_id') != self.previous_guest:
                self.event(after, 'guest-boot', {'boot_id': guest.get('boot_id')})
                self.previous_guest = guest.get('boot_id')

    def run(self):
        while not self.app.monitor_stop.is_set():
            try:
                self.tick()
            except Exception as error:
                with self.lock:
                    self.value = {"status": "ERROR", "error": str(error), "cpus": [], "domains": []}
            self.app.monitor_stop.wait(2)
