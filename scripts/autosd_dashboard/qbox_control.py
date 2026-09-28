"""Owned full-system monitor control and destructive runtime qualification."""
import http.client
import json
import math
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re
import time

import watchdog_scenarios as watchdog


def _clock(collector):
    value = collector._get('/sc_time').get('sc_time_stamp')
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value < 0:
        raise ValueError('Invalid simulation clock')
    return value


def _cpu_times(collector):
    """Absolute QK local_time, normalized to exact decimal nanoseconds."""
    values = collector._get('/qk_status')
    if not isinstance(values, list) or not values:
        raise ValueError('CPU quantum-keeper observations are unavailable')
    units = {'fs': Decimal('.000001'), 'ps': Decimal('.001'), 'ns': Decimal(1),
             'us': Decimal(1000), 'ms': Decimal(1000000), 's': Decimal(1000000000)}
    result = {}
    for value in values:
        if not isinstance(value, dict) or not isinstance(value.get('name'), str):
            raise ValueError('Malformed CPU quantum-keeper observation')
        name = value['name']
        match = re.fullmatch(r'([0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)\s+(fs|ps|ns|us|ms|s)',
                             str(value.get('local_time', '')))
        if not name or name in result or match is None:
            raise ValueError('Missing or duplicate CPU time observation')
        try:
            result[name] = str((Decimal(match[1]) * units[match[2]]).normalize())
        except InvalidOperation as exc:
            raise ValueError('Invalid CPU time observation') from exc
    return result


def control(collector, action):
    """One mutation attempt; timeouts never trigger a mutation retry."""
    if action not in ('pause', 'resume'):
        raise ValueError('Unsupported monitor control')
    if collector.manifest.get('backend') != 'qbox-full':
        raise ValueError('Control requires the full-system profile')
    # The collector verifies process identity, launcher ancestry and socket
    # ownership for every read. Do this immediately before opening control.
    _clock(collector)
    endpoint = collector.endpoint
    conn = http.client.HTTPConnection(endpoint['host'], endpoint['port'], timeout=min(2, collector.timeout))
    result = {'status': 'UNKNOWN', 'action': action, 'run_id': collector.run_id}
    try:
        conn.request('GET', '/pause' if action == 'pause' else '/continue',
                     headers={'Connection': 'close', 'Accept': 'application/json'})
        response = conn.getresponse()
        # No response body is necessary for state verification. In particular,
        # a slow body cannot retain this control connection indefinitely.
        if response.status != 200:
            result['error'] = 'Monitor returned HTTP %d; action state unconfirmed' % response.status
            return result
    except (OSError, http.client.HTTPException) as exc:
        result['error'] = str(exc)
        return result
    finally:
        conn.close()
    try:
        state = collector._get('/sc_suspended')
        expected = action == 'pause'
        if state.get('monitor_paused') is not expected:
            raise ValueError('Explicit monitor pause state does not match request')
        before = _clock(collector)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            time.sleep(.1)
            after = _clock(collector)
            if action == 'pause':
                if after != before:
                    raise ValueError('Simulation time advanced while paused')
                break
            if after > before:
                break
        else:
            raise ValueError('Simulation time did not advance after resume')
        result.update(status='PASS', monitor_paused=expected,
                      sim_before_s=before, sim_after_s=after)
    except Exception as exc:
        result['error'] = str(exc)
    return result


def run(app, job, log):
    """Qualify the current owned run. Caller holds simulator.io_lock."""
    directory = Path(job['evidence_path'])
    directory.mkdir(parents=True, exist_ok=True)
    result = {'kind': 'monitor-qualification', 'status': 'FAIL', 'cycles': []}
    app.qbox_pause_run = None
    vm_job = app.vm_job
    collector = app.simulator.collector
    paused = False
    try:
        if (app.backend != 'qbox-full' or not app.running() or collector is None
                or collector.run_id != vm_job):
            raise ValueError('Qualification requires the current owned full-system monitor')
        before = watchdog.boot_snapshot(app, directory / 'before-boot', log)
        if before.get('status') != 'ONLINE':
            raise ValueError('Guest boot ID unavailable')
        result['before_boot_id'] = before['boot_id']
        for cycle in range(10):
            if app.vm_job != vm_job or not app.running():
                raise ValueError('Owned run changed during qualification')
            job['phase'] = 'Pause/Resume %d/10' % (cycle + 1)
            app.persist(job)
            row = {'cycle': cycle + 1}
            result['cycles'].append(row)
            row['pause'] = control(collector, 'pause')
            paused = row['pause']['status'] == 'PASS'
            if not paused:
                result['pause_state_unknown'] = row['pause']['status'] == 'UNKNOWN'
                raise ValueError('Pause state unknown; inspect and explicitly resume')
            start = _clock(collector)
            cpu_start = _cpu_times(collector)
            held = time.monotonic()
            time.sleep(2)
            stop = _clock(collector)
            cpu_stop = _cpu_times(collector)
            row.update(hold_wall_s=time.monotonic() - held, sim_paused_start_s=start,
                       sim_paused_end_s=stop, cpu_local_time_start_ns=cpu_start,
                       cpu_local_time_end_ns=cpu_stop)
            if start != stop:
                raise ValueError('Simulation advanced during two-second pause')
            if cpu_start != cpu_stop:
                raise ValueError('CPU local time advanced or CPU topology changed during pause')
            row['resume'] = control(collector, 'resume')
            if row['resume']['status'] != 'PASS':
                result['pause_state_unknown'] = row['resume']['status'] == 'UNKNOWN'
                paused = False  # Unknown completion: never automatically retry.
                raise ValueError('Resume state unknown')
            paused = False
            log.write((json.dumps(row) + '\n').encode())
        after = watchdog.boot_snapshot(app, directory / 'after-cycles-boot', log)
        if after.get('boot_id') != before['boot_id']:
            raise ValueError('Guest rebooted during Pause/Resume qualification')
        remote = '/var/tmp/apollo-monitor-' + job['id']
        uploads = [(watchdog.ROOT / 'autosd/customization/check-guest.sh', remote + '-health.sh'),
                   (watchdog.ROOT / 'scripts/autosd_demo/check_hipc_link.sh', remote + '-hipc.sh'),
                   (watchdog.ROOT / 'scripts/autosd_demo/hipc_ping.py', remote + '-ping.py')]
        code = watchdog.run_command(app, directory / 'health-hipc', log,
                                    'set -e; bash ' + remote + '-health.sh; bash ' + remote + '-hipc.sh ' + remote + '-ping.py',
                                    uploads, timeout=300)
        result['health_hipc_returncode'] = code
        if code:
            raise ValueError('Post-resume Automotive health/HIPC failed')
        wd_directory = directory / 'watchdog'
        wd_directory.mkdir(exist_ok=True)
        # Pass the original job so phase/log-session updates and persist() use
        # its original evidence_path. The expiry helper accepts a separate
        # artifact directory and does not dispatch through dashboard.start().
        row = watchdog.expiry(app, job, log, wd_directory, remote + '-wd04')
        result['watchdog'] = {'kind': 'watchdog', 'status': row['status'],
                              'scenarios': [row], 'timeline': row.get('timeline', [])}
        result['after_boot_id'] = row.get('after', {}).get('boot_id')
        (wd_directory / 'scenarios.json').write_text(json.dumps(result['watchdog'], indent=2) + '\n')
        if (result['watchdog'].get('status') != 'PASS' or not result['after_boot_id']
                or result['after_boot_id'] == before['boot_id']):
            raise ValueError('WS1 reset and recovery qualification failed')
        if app.vm_job != vm_job or not app.running():
            raise ValueError('Owned run changed during watchdog qualification')
        result['status'] = 'PASS'
        app.qbox_pause_run = vm_job
    except Exception as exc:
        result['error'] = str(exc)
    finally:
        # Only a confirmed pause followed by a failed read/check is released;
        # an uncertain mutation is never sent again automatically.
        if paused:
            try:
                result['cleanup_resume'] = control(collector, 'resume')
            except Exception as exc:
                result['cleanup_resume'] = {'status': 'UNKNOWN', 'error': str(exc)}
            result['pause_state_unknown'] = result['cleanup_resume']['status'] != 'PASS'
        if result.get('pause_state_unknown'):
            result['status'] = 'UNKNOWN'
        job['phase'] = '완료 · ' + result['status']
        app.persist(job)
        (directory / 'qualification.json').write_text(json.dumps(result, indent=2) + '\n')
    return result
