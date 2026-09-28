"""Bounded, read-only QBox monitor collection, independent of guest SSH.

The caller owns scheduling. One collector belongs to one immutable run identity;
cached reads never perform network I/O. No monitor mutation endpoint is exposed.
"""
from copy import deepcopy
from decimal import Decimal, InvalidOperation
import http.client
import json
import math
from pathlib import Path
import re
import threading
import time
from urllib.parse import quote


class MonitorError(RuntimeError):
    pass


def process_identity(pid, proc_root=Path('/proc')):
    """Return parent/start ticks without confusing spaces in comm with fields."""
    fields = (proc_root / str(int(pid)) / 'stat').read_text().rsplit(')', 1)[1].split()
    return int(fields[1]), int(fields[19])


def verify_listener(host, port, owner_pid, owner_start_ticks, proc_root=Path('/proc')):
    """Require every matching listener to belong to the anchored process tree.

    Checking /proc/net/tcp plus fd socket inodes also rejects a same-port foreign
    process after the original child exits. This requires a shared PID/net namespace.
    """
    if host != '127.0.0.1' or not 1 <= int(port) <= 65535:
        raise MonitorError('monitor endpoint must be IPv4 loopback')
    try:
        if process_identity(owner_pid, proc_root)[1] != int(owner_start_ticks):
            raise MonitorError('monitor owner process identity changed')
        inodes = set()
        for row in (proc_root / 'net/tcp').read_text().splitlines()[1:]:
            fields = row.split()
            address, hex_port = fields[1].split(':')
            if int(hex_port, 16) == int(port) and fields[3] == '0A':
                if address != '0100007F':
                    raise MonitorError('monitor listener is not bound to loopback')
                inodes.add(fields[9])
        if not inodes:
            raise MonitorError('monitor listener is not ready')
        owned = set()
        for entry in proc_root.iterdir():
            if not entry.name.isdigit():
                continue
            try:
                pid, visited = int(entry.name), set()
                while pid != int(owner_pid) and pid > 1 and pid not in visited:
                    visited.add(pid)
                    pid = process_identity(pid, proc_root)[0]
                if pid != int(owner_pid):
                    continue
                for fd in (entry / 'fd').iterdir():
                    try:
                        match = re.fullmatch(r'socket:\[(\d+)\]', str(fd.readlink()))
                        if match:
                            owned.add(match[1])
                    except OSError:
                        continue
            except (OSError, ValueError, IndexError):
                continue
        if not inodes <= owned:
            raise MonitorError('monitor listener is outside the managed process tree')
        if process_identity(owner_pid, proc_root)[1] != int(owner_start_ticks):
            raise MonitorError('monitor owner changed during verification')
    except (OSError, ValueError, IndexError) as exc:
        raise MonitorError('monitor process ownership unavailable') from exc


def time_string_ns(value):
    """SystemC's local_time is absolute; quantum_time is the offset from now."""
    match = re.fullmatch(r'([0-9.eE+\-]+)\s*(fs|ps|ns|us|ms|s)', str(value))
    if not match:
        return None
    try:
        number = Decimal(match[1]) * {'fs': Decimal('.000001'), 'ps': Decimal('.001'),
                                     'ns': 1, 'us': 1000, 'ms': 1000000, 's': 1000000000}[match[2]]
        return int(number) if number.is_finite() and number >= 0 else None
    except (InvalidOperation, ValueError, OverflowError):
        return None


class QBoxMonitorCollector:
    def __init__(self, manifest, *, evidence_dir=None, interval=2, timeout=2,
                 max_body=1024 * 1024, max_backoff=30, evidence_quota=64 * 1024 * 1024):
        self.manifest = deepcopy(manifest)
        self.run_id = str(manifest['run_id'])
        self.endpoint = dict(manifest.get('monitor', {}))
        self.interval, self.timeout = max(.1, interval), max(.01, timeout)
        self.max_body, self.max_backoff = max_body, max_backoff
        self.evidence_dir = Path(evidence_dir) if evidence_dir else None
        self.evidence_quota = evidence_quota
        self._lock = threading.Lock()
        self._sample_lock = threading.Lock()
        self._next_sample = 0
        self._failures = 0
        self._last_success = None
        self._previous = None
        self._discovered = False
        self._discovery_retry_at = {}
        self._caps = {key: {'available': False, 'qualified': False, 'reason': 'not discovered'}
                      for key in ('status', 'metadata', 'mcips', 'injection', 'qmp', 'pause')}
        for key in ('injection', 'qmp', 'pause'):
            self._caps[key]['reason'] = 'disabled: runtime qualification required'
        self._snapshot = {'schema_version': 1, 'run_id': self.run_id, 'sample_seq': 0,
                          'backend': manifest.get('backend'), 'status': 'STARTING',
                          'sim_time_ns': None, 'domains': [], 'error': None,
                          'last_success_at': None, 'evidence_dropped': 0}

    def _get(self, path):
        allowed = {'/sc_time', '/sc_suspended', '/qk_status', '/mcips_plugin_status', '/biflows',
                   '/api/v1/injection/capabilities', '/api/v1/objects'}
        if path not in allowed and not path.startswith('/api/v1/objects/'):
            raise MonitorError('endpoint is not read-only allowlisted')
        endpoint = self.endpoint
        launcher_pid = self.manifest.get('launcher_pid')
        if launcher_pid is not None:
            try:
                expected_start = self.manifest['launcher_start_ticks']
                if process_identity(launcher_pid)[1] != int(expected_start):
                    raise MonitorError('managed launcher process identity changed')
                pid, visited = int(endpoint.get('owner_pid', 0)), set()
                while pid != int(launcher_pid) and pid > 1 and pid not in visited:
                    visited.add(pid)
                    pid = process_identity(pid)[0]
                if pid != int(launcher_pid):
                    raise MonitorError('monitor owner is outside managed launcher tree')
            except (OSError, ValueError, KeyError, IndexError) as exc:
                raise MonitorError('managed launcher identity unavailable') from exc
        verify_listener(endpoint.get('host'), endpoint.get('port', 0),
                        endpoint.get('owner_pid', 0), endpoint.get('owner_start_ticks', -1))
        conn = http.client.HTTPConnection(endpoint['host'], endpoint['port'], timeout=self.timeout)
        try:
            conn.request('GET', path, headers={'Accept': 'application/json', 'Connection': 'close'})
            response = conn.getresponse()
            if response.status != 200:
                raise MonitorError('HTTP %d: %s' % (response.status, path))
            deadline = time.monotonic() + self.timeout
            chunks, length = [], 0
            while length <= self.max_body:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise MonitorError('monitor response deadline exceeded')
                if conn.sock is not None:
                    conn.sock.settimeout(remaining)
                chunk = response.read1(min(65536, self.max_body + 1 - length))
                if not chunk:
                    break
                chunks.append(chunk)
                length += len(chunk)
            body = b''.join(chunks)
            if len(body) > self.max_body:
                raise MonitorError('monitor response exceeds body limit')
            try:
                return json.loads(body)
            except (ValueError, UnicodeDecodeError) as exc:
                raise MonitorError('invalid monitor JSON: ' + path) from exc
        except (OSError, http.client.HTTPException) as exc:
            raise MonitorError('monitor transport: ' + str(exc)) from exc
        finally:
            conn.close()

    def capabilities(self):
        with self._lock:
            return {'schema_version': 1, 'run_id': self.run_id, 'features': deepcopy(self._caps)}

    def snapshot(self):
        with self._lock:
            result = deepcopy(self._snapshot)
            age = None if self._last_success is None else (time.monotonic() - self._last_success) * 1000
            result['age_ms'] = age
            if result['status'] in ('ONLINE', 'PAUSED') and age is not None and age > self.interval * 3000:
                result['status'] = 'STALE'
            return result

    def _persist(self, snapshot):
        if self.evidence_dir is None:
            return
        try:
            self.evidence_dir.mkdir(parents=True, exist_ok=True)
            target = self.evidence_dir / 'simulator.jsonl'
            line = json.dumps(snapshot, ensure_ascii=True, allow_nan=False) + '\n'
            size = target.stat().st_size if target.exists() else 0
            if size + len(line.encode()) > self.evidence_quota:
                with self._lock:
                    self._snapshot['evidence_dropped'] += 1
                return
            with target.open('a') as stream:
                stream.write(line)
        except OSError as exc:
            with self._lock:
                self._snapshot['evidence_error'] = str(exc)

    def sample(self, *, force=False, measurement_active=False):
        """Collect once. A measurement barrier suppresses all monitor traffic."""
        if not self._sample_lock.acquire(blocking=False):
            return self.snapshot()
        try:
            now = time.monotonic()
            if measurement_active or (not force and now < self._next_sample):
                return self.snapshot()
            with self._lock:
                result = deepcopy(self._snapshot)
            result.update(sample_seq=result['sample_seq'] + 1, host_monotonic=now,
                          collected_at=time.time(), error=None, speed_ratio=None)
            try:
                raw = self._get('/sc_time')['sc_time_stamp']
                if isinstance(raw, bool) or not isinstance(raw, (float, int)) or not math.isfinite(raw) or raw < 0:
                    raise MonitorError('invalid simulation timestamp')
                suspension = self._get('/sc_suspended')
                suspended = suspension['sc_suspended']
                monitor_paused = suspension.get('monitor_paused', False)
                if not isinstance(suspended, bool) or not isinstance(monitor_paused, bool):
                    raise MonitorError('invalid suspended status')
                qks = self._get('/qk_status')
                if not isinstance(qks, list) or any(not isinstance(item, dict) for item in qks):
                    raise MonitorError('invalid quantum keeper status')
                result.update(sim_time_seconds_raw=raw, sim_time_ns=int(Decimal(str(raw)) * 1000000000),
                              status='PAUSED' if monitor_paused else 'ONLINE',
                              sc_suspended=suspended, monitor_paused=monitor_paused,
                              last_success_at=time.time(), last_success_monotonic=now)
                if self._previous is not None:
                    previous_host, previous_sim = self._previous
                    if now > previous_host and raw >= previous_sim:
                        result['speed_ratio'] = (raw - previous_sim) / (now - previous_host)
                self._previous = (now, raw)
                domains = []
                mapped = set()
                for domain in self.manifest.get('domains', []):
                    item = deepcopy(domain)
                    item.update(boot_epoch=None, epoch_source='unavailable', cpus=[])
                    for qk in qks:
                        name = str(qk.get('name', ''))
                        if any(name == p or name.startswith(p + '.') for p in domain.get('cpu_object_paths', [])):
                            cpu = deepcopy(qk)
                            cpu.update(local_time_ns=time_string_ns(qk.get('local_time')),
                                       quantum_offset_ns=time_string_ns(qk.get('quantum_time')),
                                       local_time_semantics='absolute simulation time',
                                       state_semantics='quantum keeper state; not CPU utilization')
                            item['cpus'].append(cpu)
                            mapped.add(name)
                    domains.append(item)
                result['domains'] = domains
                result['unmapped_quantum_keepers'] = [q for q in qks if q.get('name') not in mapped]
                self._caps['status'] = {'available': True, 'qualified': True, 'reason': 'read-only status'}
                if self._discovered and self._caps['mcips']['available']:
                    try:
                        result['mcips'] = self._get('/mcips_plugin_status')
                        result.pop('mcips_error', None)
                    except MonitorError as exc:
                        result['mcips'] = None
                        result['mcips_error'] = str(exc)
                # Optional endpoints cannot turn a healthy monitor OFFLINE.
                if not self._discovered or any(now >= deadline for deadline in self._discovery_retry_at.values()):
                    for feature, path in (('mcips', '/mcips_plugin_status'),
                                          ('metadata', '/api/v1/objects'),
                                          ('injection', '/api/v1/injection/capabilities')):
                        if self._discovered and now < self._discovery_retry_at.get(feature, float('inf')):
                            continue
                        try:
                            value = self._get(path)
                            self._discovery_retry_at.pop(feature, None)
                            self._caps[feature] = {'available': feature != 'injection' and bool(value),
                                                   'qualified': feature == 'metadata',
                                                   'reason': 'available' if feature != 'injection' else 'disabled: runtime qualification required'}
                            if feature == 'mcips':
                                result['mcips'] = value
                        except MonitorError as exc:
                            self._caps[feature] = {'available': False, 'qualified': False, 'reason': str(exc)}
                            # Stable unsupported/disabled responses need no retry;
                            # transient startup/transport failures recover at a
                            # bounded, low discovery rate independent of polling.
                            if 'HTTP 403:' not in str(exc) and 'HTTP 404:' not in str(exc):
                                self._discovery_retry_at[feature] = now + self.max_backoff
                            else:
                                self._discovery_retry_at.pop(feature, None)
                    self._discovered = True
                self._last_success = now
                self._failures = 0
                self._next_sample = now + self.interval
            except (MonitorError, KeyError, TypeError, ValueError) as exc:
                result.update(status='OFFLINE', error=str(exc))
                self._previous = None
                self._failures += 1
                self._next_sample = now + min(self.max_backoff, self.interval * 2 ** min(self._failures, 10))
            with self._lock:
                self._snapshot = result
            self._persist(result)
            return self.snapshot()
        finally:
            self._sample_lock.release()

    def objects(self, parent=''):
        if not isinstance(parent, str) or len(parent) > 512 or (parent and not re.fullmatch(r'[A-Za-z0-9_.\-]+', parent)):
            raise MonitorError('invalid object path')
        if not self._caps['metadata']['available']:
            raise MonitorError('metadata endpoint unavailable')
        return self._get('/api/v1/objects' + ('/' + quote(parent, safe='') if parent else ''))
