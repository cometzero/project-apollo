"""Read-only, bounded QMP requests over a managed monitor's biflow bridge.

The native QMP component negotiates capabilities. Its replay buffer can contain
old replies and handshake messages, so only the newly generated request ID counts.
"""
import json
import re
import threading
import time
from urllib.parse import quote
import uuid

try:
    import websocket
except ImportError:
    websocket = None


class DiagnosticError(RuntimeError):
    pass


if websocket is not None:
    class BoundedWebSocket(websocket.WebSocket):
        """Bound all frames together, including fragmented messages and ping spam."""
        def __init__(self, *args, deadline, max_bytes, **kwargs):
            self.deadline = deadline
            self.remaining_bytes = max_bytes
            super().__init__(*args, **kwargs)

        def _recv(self, bufsize):
            remaining = self.deadline - time.monotonic()
            if remaining <= 0:
                raise DiagnosticError('QMP response deadline exceeded')
            if self.remaining_bytes <= 0:
                raise DiagnosticError('QMP response byte limit exceeded')
            self.settimeout(remaining)
            data = super()._recv(min(bufsize, self.remaining_bytes))
            self.remaining_bytes -= len(data)
            return data


class QBoxDiagnostics:
    COMMANDS = frozenset(('query-status', 'query-cpus-fast', 'query-version'))

    def __init__(self, collector, *, timeout=2, max_bytes=1024 * 1024):
        self.collector = collector
        self.timeout = max(.01, float(timeout))
        self.max_bytes = max(256, int(max_bytes))
        domains = collector.manifest.get('domains', collector.manifest.get('monitor', {}).get('domains', []))
        self.domains = {item['domain_id']: dict(item) for item in domains if item.get('qmp_biflow')}
        self.locks = {domain: threading.Lock() for domain in self.domains}

    def query(self, domain, command='query-status'):
        if command not in self.COMMANDS:
            raise DiagnosticError('QMP command is not read-only allowlisted')
        if domain not in self.domains:
            raise DiagnosticError('QMP domain is unavailable')
        if websocket is None:
            raise DiagnosticError('websocket-client is not installed')
        biflow = self.domains[domain]['qmp_biflow']
        if not isinstance(biflow, str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,512}', biflow):
            raise DiagnosticError('invalid QMP biflow mapping')
        lock = self.locks[domain]
        if not lock.acquire(blocking=False):
            raise DiagnosticError('QMP domain query already in progress')
        connection = None
        try:
            # Includes owner start-time, launcher ancestry and listening-socket
            # checks. Never create a websocket for an unverified endpoint.
            discovered = self.collector._get('/biflows')
            names = discovered.get('biflows') if isinstance(discovered, dict) else None
            if not isinstance(names, list) or any(not isinstance(name, str) for name in names):
                raise DiagnosticError('invalid monitor biflow discovery response')
            if biflow not in names:
                routed = biflow + '.qmp_socket_router'
                if routed not in names:
                    raise DiagnosticError('configured QMP biflow is not present in owned monitor')
                biflow = routed
            endpoint = self.collector.endpoint
            request_id = 'dashboard-' + uuid.uuid4().hex
            deadline = time.monotonic() + self.timeout
            url = 'ws://127.0.0.1:%d/biflow/%s' % (endpoint['port'], quote(biflow, safe=''))
            connection = websocket.create_connection(
                url, timeout=self.timeout, class_=BoundedWebSocket,
                deadline=deadline, max_bytes=self.max_bytes, http_no_proxy=['127.0.0.1'],
                redirect_limit=0)
            connection.send(json.dumps({'execute': command, 'id': request_id}) + '\r\n')
            pending = b''
            ignored = 0
            first_line = True
            replay_prefix_discarded_bytes = 0
            while time.monotonic() < deadline:
                connection.settimeout(max(.001, deadline - time.monotonic()))
                data = connection.recv()
                if not data:
                    raise DiagnosticError('QMP bridge closed before response')
                pending += data.encode('utf-8') if isinstance(data, str) else data
                if len(pending) > self.max_bytes:
                    raise DiagnosticError('QMP response byte limit exceeded')
                while b'\n' in pending:
                    line, pending = pending.split(b'\n', 1)
                    if not line.strip():
                        continue
                    try:
                        value = json.loads(line)
                    except (ValueError, UnicodeDecodeError) as exc:
                        # Monitor replays a byte-limited ring, not whole JSON
                        # records. Only its first nonempty line may be a cut
                        # prefix. Never discard a malformed current-ID reply.
                        if first_line and request_id.encode() not in line:
                            first_line = False
                            ignored += 1
                            replay_prefix_discarded_bytes = len(line)
                            continue
                        raise DiagnosticError('invalid QMP response JSON') from exc
                    first_line = False
                    if not isinstance(value, dict) or value.get('id') != request_id:
                        ignored += 1
                        continue
                    if 'error' in value:
                        raise DiagnosticError('QMP command failed: ' + json.dumps(value['error']))
                    if 'return' not in value:
                        raise DiagnosticError('QMP matching response has no result')
                    return {'schema_version': 1, 'run_id': self.collector.run_id,
                            'domain_id': domain, 'command': command, 'request_id': request_id,
                            'result': value['return'], 'ignored_messages': ignored,
                            'replay_prefix_discarded_bytes': replay_prefix_discarded_bytes,
                            'host_observed_at': time.time(), 'coherent_snapshot': False}
            raise DiagnosticError('QMP response deadline exceeded')
        except DiagnosticError:
            raise
        except Exception as exc:
            raise DiagnosticError('QMP transport: ' + str(exc)) from exc
        finally:
            try:
                if connection is not None:
                    # No close-handshake wait: failed queries remain bounded.
                    connection.shutdown()
            finally:
                lock.release()
