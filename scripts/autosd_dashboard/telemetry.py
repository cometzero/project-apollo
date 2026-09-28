"""Bounded, read-only monitoring for a private localhost AutoSD VM."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shlex
import threading
import time

import paramiko

_previous = {}
_lock = threading.Lock()


def rates(current, previous):
    result = []
    same_boot = previous and current.get('boot_id') == previous.get('boot_id')
    for name, ticks in current.get('cpu_ticks', {}).items():
        old = previous.get('cpu_ticks', {}).get(name) if same_boot else None
        usage = None
        if old and len(old) == len(ticks):
            delta = [a - b for a, b in zip(ticks, old)]
            total = sum(delta)
            if total > 0 and min(delta) >= 0:
                usage = round(100 * (total - delta[3] - delta[4]) / total, 2)
        result.append({'id': name, 'utilization_pct': usage})
    elapsed = current.get('guest_monotonic', 0) - previous.get('guest_monotonic', 0) if same_boot else 0
    old_units = {s['id']: s for s in previous.get('subsystems', [])} if same_boot else {}
    for unit in current.get('subsystems', []):
        unit['cpu_cores'] = None
        try:
            if unit.get('cgroup') != old_units[unit['id']].get('cgroup'):
                continue
            def usage(s):
                return int(dict(line.split() for line in s['metrics']['cpu.stat'].splitlines())['usage_usec'])
            delta = usage(unit) - usage(old_units[unit['id']])
            if elapsed > 0 and delta >= 0:
                unit['cpu_cores'] = round(delta / (elapsed * 1000000), 3)
        except (KeyError, TypeError, ValueError, AttributeError):
            pass
    return result


def collect(port):
    """Caller must invoke only while its explicitly owned VM is running."""
    stamp = datetime.now(timezone.utc).isoformat()
    client = paramiko.SSHClient()
    # Disposable loopback-only image, same trust boundary as guest_exec.py.
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect('127.0.0.1', port=port, username='root', password='password',
                       look_for_keys=False, allow_agent=False, timeout=3,
                       banner_timeout=5, auth_timeout=5)
        script = Path(__file__).with_name('guest_monitor.py').read_text()
        channel = client.get_transport().open_session(timeout=5)
        channel.exec_command('python3 -c ' + shlex.quote(script))
        data = bytearray()
        deadline = time.monotonic() + 15
        while not channel.exit_status_ready() or channel.recv_ready():
            if channel.recv_ready():
                data.extend(channel.recv(65536))
                if len(data) > 1024 * 1024:
                    raise ValueError('Telemetry exceeded 1 MiB')
            elif time.monotonic() > deadline:
                raise TimeoutError('Telemetry command deadline exceeded')
            else:
                time.sleep(.05)
        if channel.recv_exit_status() != 0:
            raise RuntimeError('Guest telemetry command failed')
        value = json.loads(data)
        with _lock:
            value['cpus'] = rates(value, _previous.get(port, {}))
            _previous[port] = value
        value.update(status='ONLINE', collected_at=stamp)
        return value
    except Exception as error:
        with _lock:
            _previous.pop(port, None)
        return {'status': 'UNAVAILABLE', 'collected_at': stamp, 'error': str(error),
                'cpus': [], 'subsystems': []}
    finally:
        client.close()
