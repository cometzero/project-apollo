#!/usr/bin/env python3
"""Bounded local dashboard qualification. Mutations require an explicit action."""
import argparse
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlsplit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8765')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--action', choices=['boot', 'health', 'monitor-mhu', 'monitor-qualify',
                        'mixed-criticality', 'mixed-criticality-mc01', 'mixed-criticality-mc02', 'mixed-criticality-mc03',
                        'rt-r02', 'watchdog-wd01', 'reboot', 'pause', 'resume', 'shutdown'])
    parser.add_argument('--confirm-disruptive', action='store_true')
    parser.add_argument('--backend', choices=('qemu', 'qbox', 'qbox-full'),
                        help='Select backend while powered off; requires --action boot')
    parser.add_argument('--timeout', type=float, default=1200)
    args = parser.parse_args()
    if args.backend and args.action != 'boot':
        parser.error('--backend requires --action boot')
    origin = urlsplit(args.url)
    if origin.hostname not in ('localhost', '127.0.0.1') or origin.scheme != 'http':
        parser.error('Only local managed dashboard URLs allowed')
    args.out.mkdir(parents=True, exist_ok=True)

    def call(path, payload=None, token=None):
        request = Request(args.url + path, data=json.dumps(payload).encode() if payload is not None else None,
                          headers={'Content-Type': 'application/json', 'Origin': args.url,
                                   'X-CSRF-Token': token or ''})
        deadline = time.monotonic() + 5
        while True:
            try:
                with urlopen(request, timeout=20) as response:
                    return json.load(response)
            except HTTPError as error:
                body = error.read().decode('utf-8', errors='replace')
                # Only bounded read-only collector contention is retried.
                # Never retry submitted lifecycle/scenario mutations.
                if (payload is None and error.code == 503 and 'Simulator busy;' in body
                        and time.monotonic() < deadline):
                    time.sleep(.25)
                    continue
                raise RuntimeError('HTTP %d: %s' % (error.code, body)) from error

    state = call('/api/state')
    if args.backend and state['vm']['backend'] != args.backend:
        if state['vm']['running']:
            raise RuntimeError('Power off before changing backend; no mutation issued')
        call('/api/backend', {'backend': args.backend}, state['csrf_token'])
        state = call('/api/state')
    if args.action:
        if args.action == 'boot' and state['vm']['running']:
            job_id = state['vm']['boot_job']
        else:
            idle_deadline = time.monotonic() + args.timeout
            while any(item['status'] == 'RUNNING' and item['action'] != 'boot' for item in state['jobs']):
                if time.monotonic() >= idle_deadline:
                    raise TimeoutError('Previous job did not finish; no mutation issued')
                time.sleep(3)
                state = call('/api/state')
            result = call('/api/jobs', {'action': args.action, 'confirm_disruptive': args.confirm_disruptive},
                          state['csrf_token'])
            job_id = result['job']['id'] if 'job' in result else result['id']
        deadline = time.monotonic() + args.timeout
        previous = None
        while time.monotonic() < deadline:
            state = call('/api/state')
            job = next(item for item in state['jobs'] if item['id'] == job_id)
            status = (job.get('phase'), job['status'])
            if status != previous:
                print(json.dumps({'action': args.action, 'job_id': job_id, 'progress': status}), flush=True)
                previous = status
            if args.action == 'boot':
                ready = state.get('monitoring', {}).get('status') == 'ONLINE'
                health = next((item for item in reversed(state['jobs']) if item['action'] == 'health'
                               and item.get('feature_session') == state['feature_session']), state.get('feature_health'))
                # Boot readiness is established by dashboard's Feature rows, not process existence.
                ready = ready and (health or {}).get('status') == 'PASS'
                if ready:
                    break
            elif job['status'] != 'RUNNING':
                break
            if job['status'] in ('FAIL', 'TIMEOUT', 'UNSUPPORTED'):
                break
            time.sleep(3)
        else:
            raise TimeoutError('Dashboard qualification deadline exceeded')
        (args.out / (args.action + '.json')).write_text(json.dumps({'job': job, 'state': state}, indent=2))
        if (args.action == 'boot' and not ready) or (args.action != 'boot' and job['status'] != 'PASS'):
            raise RuntimeError('Scenario did not PASS: ' + job['status'])
    else:
        results = {'state': state, 'snapshot': call('/api/simulator/snapshot'),
                   'capabilities': call('/api/simulator/capabilities'),
                   'objects': call('/api/simulator/objects?parent=platform')}
        domains = ['rse', 'si-cl0', 'si-cl1', 'ap'] if state['vm']['backend'] == 'qbox-full' else ['ap']
        results['qmp'] = {domain: {command: call('/api/simulator/qmp?domain=' + domain + '&command=' + command)
                         for command in ('query-status', 'query-cpus-fast', 'query-version')} for domain in domains}
        (args.out / 'observation.json').write_text(json.dumps(results, indent=2))
        assert results['snapshot']['status'] == 'ONLINE', results['snapshot']
        for domain, responses in results['qmp'].items():
            assert responses['query-status']['result']['running'], (domain, responses)
            assert len(responses['query-cpus-fast']['result']) > 0, domain
            assert 'qemu' in responses['query-version']['result'], domain
        observed = {domain['domain_id'] for domain in results['snapshot']['domains'] if domain['cpus']}
        assert observed == set(domains), ('missing QK domain observations', observed)
        print('Observation and read-only QMP: PASS', flush=True)


if __name__ == '__main__':
    main()
