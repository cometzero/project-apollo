#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Bounded campaign execution and paired model exploration; never silicon qualification."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import time

import soc_spec as s


def validate(policy, campaign):
    s.require(policy.get('schema') == 1, 'unsupported policy schema')
    budget = policy['budget']
    s.require(type(budget['max_runs']) is int and budget['max_runs'] > 0,
              'max_runs must be positive integer')
    s.require(s.finite(budget['host_seconds'], positive=True), 'invalid host budget')
    s.require(isinstance(budget.get('basis'), str) and budget['basis'], 'missing pilot/budget basis')
    cases = {c['id']: c for c in campaign['cases']}
    s.require(len(cases) == len(campaign['cases']), 'duplicate case')
    comparisons = {c['id']: c for c in campaign.get('comparisons', [])}
    s.require(len(comparisons) == len(campaign.get('comparisons', [])), 'duplicate comparison')
    pending = policy.get('execute', [])
    s.require(len(set(pending)) == len(pending) and set(pending) <= cases.keys(), 'invalid execute cases')
    s.require(len(pending) <= budget['max_runs'], 'planned runs exceed budget')
    for name in pending:
        c = cases[name]
        for field in ('argv', 'verification_argv'):
            s.require(isinstance(c.get(field), list) and c[field]
                      and all(isinstance(x, str) and x for x in c[field]), 'missing command argv')
        s.require(s.finite(c.get('timeout_seconds'), positive=True), 'missing run timeout')
    groups = policy.get('assessments', [])
    s.require(len({g['id'] for g in groups}) == len(groups), 'duplicate assessment')
    for g in groups:
        s.require(g['direction'] in ('higher', 'lower'), 'invalid metric direction')
        s.require(s.finite(g['min_gain']), 'invalid minimum meaningful gain')
        s.require(g.get('basis'), 'missing uncertainty basis')
        required = g['required_conditions']
        s.require(required and len(set(required)) == len(required), 'invalid required conditions')
        pairs = g['pairs']
        coordinates = [s.json_digest(p.get('coordinates', {})) for p in pairs]
        s.require(len(set(coordinates)) == len(coordinates), 'duplicate uncertainty coordinates')
        s.require(len({p['condition'] for p in pairs}) == len(pairs), 'duplicate paired condition')
        s.require(not pairs or all(set(p['coordinates']) == set(pairs[0]['coordinates']) for p in pairs),
                  'uncertainty axes differ across pairs')
        for p in pairs:
            s.require(p['condition'] in required, 'unexpected condition')
            c = comparisons[p['comparison']]
            s.require(c.get('kind', 'comparison') == 'comparison', 'pair is not a hardware comparison')
            s.require(not c.get('allowed_workload_changes'), 'paired workload must be identical')
            s.require(set(c.get('allowed_inputs_changes', [])) <= {'profile', 'readfile'},
                      'paired executable inputs must be identical')
            s.require(g['metric'] in c['metrics'], 'pair lacks primary metric')
            s.require(p.get('coordinates'), 'missing resolved uncertainty coordinates')
            for role in ('baseline', 'candidate'):
                gates = p.get(role + '_stability', [])
                for gate in gates:
                    q = comparisons[gate]
                    s.require(q.get('kind') == 'convergence' and c[role] in (q['baseline'], q['candidate']),
                              'stability gate must include paired case')
    calibration = policy.get('calibration_cases', [])
    validation = policy.get('validation_cases', [])
    s.require(set(calibration) <= cases.keys() and set(validation) <= cases.keys(), 'unknown workload role')
    s.require(not set(calibration) & set(validation), 'calibration and validation overlap')
    return cases


def coordinate(record, path):
    value = record['identity']
    s.require(path.split('.')[0] in ('profile', 'canonical_config'), 'coordinate must bind effective hardware')
    for key in path.split('.'):
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def assess(policy, campaign, report):
    validate(policy, campaign)
    cases = {c['id']: c for c in report['cases']}
    comparisons = {c['id']: c for c in report['comparisons']}
    definitions = {c['id']: c for c in campaign.get('comparisons', [])}
    results = []
    calibration = [cases[n] for n in policy.get('calibration_cases', [])]
    validation = [cases[n] for n in policy.get('validation_cases', [])]
    families = lambda rows: {(r.get('workload', {}).get('kind'), r.get('workload', {}).get('kernel'),
                              r.get('workload', {}).get('benchmark')) for r in rows}
    independent = ('PASS_DISTINCT_KERNELS' if calibration and validation
                   and all(s.case_ready(r) for r in calibration + validation)
                   and not families(calibration) & families(validation) else 'NOT_ESTABLISHED')
    for group in policy.get('assessments', []):
        rows = []
        design_signatures = set()
        for pair in group['pairs']:
            row = dict(condition=pair['condition'], status='INCONCLUSIVE')
            try:
                definition = definitions[pair['comparison']]
                compared = comparisons[pair['comparison']]
                s.require(compared['status'] == 'PASS',
                          'pair lacks valid comparable raw evidence: ' + compared.get('reason', compared['status']))
                for role in ('baseline', 'candidate'):
                    for path, expected in pair['coordinates'].items():
                        actual = coordinate(cases[definition[role]], path)
                        s.require(type(actual) is type(expected) and actual == expected,
                                  'uncertainty coordinate mismatch: ' + role + ':' + path)
                changes = compared.get('changes', {})
                reference = cases[definition['baseline']]
                identity = reference['identity']
                design_signatures.add(s.json_digest(dict(
                    profile=changes.get('profile'), config=changes.get('config'),
                    workload=reference.get('workload'),
                    sources=identity.get('model_sources_sha256'),
                    inputs={k:v for k,v in identity.get('inputs', {}).items()
                            if k not in ('profile', 'readfile')})))
                values = compared['metrics'][group['metric']]
                a, b = values['before'], values['after']
                s.require(s.finite(a, positive=True) and s.finite(b, positive=True), 'nonpositive primary metric')
                row['gain'] = b / a - 1 if group['direction'] == 'higher' else a / b - 1
                row['unit'] = values['unit']
                row['baseline'] = a
                row['candidate'] = b
                stable = True
                counter_states = {}
                for role in ('baseline', 'candidate'):
                    gates = pair.get(role + '_stability', [])
                    dimensions = set()
                    for gate in gates:
                        result = comparisons[gate]
                        dimensions.update(result.get('changes', {}).get('workload', {}))
                        primary = result.get('metrics', {}).get(group['metric'], {})
                        stable &= primary.get('status') == 'PASS'
                        counter_states[gate] = {k: v.get('status', 'UNDECIDED')
                                               for k, v in result.get('metrics', {}).items()
                                               if k != group['metric']}
                    stable &= 'warmup_passes' in dimensions and bool(dimensions & {'passes', 'frames'})
                row.update(status='STABLE_PRIMARY' if stable else 'OBSERVED_ONLY',
                           explanatory_counter_status=counter_states)
            except (ValueError, KeyError, TypeError, IndexError) as exc:
                row['reason'] = str(exc)
            rows.append(row)
        complete = ({r['condition'] for r in rows} == set(group['required_conditions'])
                    and all(r['status'] == 'STABLE_PRIMARY' for r in rows)
                    and len(design_signatures) == 1)
        gains = [r['gain'] for r in rows if 'gain' in r]
        conclusion = 'INCONCLUSIVE'
        if complete:
            conclusion = ('ROBUST_IN_TESTED_CONDITIONS' if all(x >= group['min_gain'] for x in gains)
                          else 'CONDITIONAL' if any(x >= group['min_gain'] for x in gains)
                          else 'NO_MEANINGFUL_GAIN_IN_TESTED_CONDITIONS')
        results.append(dict(id=group['id'], conclusion=conclusion, pairs=rows,
                            same_design_and_workload_across_conditions=len(design_signatures) == 1,
                            sign_reversal=min(gains) < 0 < max(gains) if gains else False,
                            missing_conditions=sorted(set(group['required_conditions']) - {r['condition'] for r in rows}),
                            independent_validation=independent,
                            model_credibility='NOT_ESTABLISHED', product_decision='UNDECIDED'))
    return dict(schema=1, qualification='MODEL_EXPLORATION_NOT_SILICON', assessments=results)


def pins(policy, base):
    s.require(policy.get('pins'), 'execution requires frozen source/input pins')
    for path, expected in policy['pins'].items():
        s.require(s.digest(base / path) == expected, 'changed pinned input: ' + path)


def execute(policy, campaign, base, output):
    """Serial, no retry. Only stop process groups created by this invocation."""
    cases = validate(policy, campaign)
    pins(policy, base)
    for name in policy['execute']:
        s.require(not (base / cases[name]['run']).exists(), 'run output already exists')
        s.require(cases[name].get('config_verification')
                  and not (base / cases[name]['config_verification']).exists(), 'verification output exists/missing')
    destinations = [str((base / cases[n][k]).resolve())
                    for n in policy['execute'] for k in ('run', 'config_verification')]
    s.require(len(set(destinations)) == len(destinations), 'duplicate output destination')
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    rows = []
    stop = None
    with (output / 'execution.jsonl').open('x') as ledger:
        def event(row):
            ledger.write(json.dumps(row, allow_nan=False) + '\n')
            ledger.flush()
            os.fsync(ledger.fileno())
        event(dict(state='START', policy_sha256=s.json_digest(policy), campaign_sha256=s.json_digest(campaign)))
        for name in policy['execute']:
            row = dict(id=name, execution_status='NOT_RUN')
            rows.append(row)
            remaining = policy['budget']['host_seconds'] - (time.monotonic() - started)
            if stop or remaining <= 0:
                row['reason'] = stop or 'HOST_BUDGET_EXHAUSTED'
                event(row)
                continue
            pins(policy, base)
            c = cases[name]
            for stage, argv in (('launch', c['argv']), ('verify', c['verification_argv'])):
                remaining = policy['budget']['host_seconds'] - (time.monotonic() - started)
                if remaining <= 0:
                    stop = 'HOST_BUDGET_EXHAUSTED'
                    row.update(execution_status='TIMEOUT', reason=stop)
                    break
                event(dict(state='START_COMMAND', case=name, stage=stage, argv=argv))
                with (output / (str(len(rows)) + '-' + stage + '.log')).open('x') as log:
                    try:
                        process = subprocess.Popen(argv, cwd=base, stdout=log, stderr=subprocess.STDOUT,
                                                   start_new_session=True)
                    except OSError as exc:
                        row.update(execution_status='ERROR', reason=str(exc))
                        stop = 'COMMAND_START_FAILED'
                        break
                    try:
                        code = process.wait(timeout=min(remaining, c['timeout_seconds']))
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                        row.update(execution_status='TIMEOUT', reason='command budget exhausted')
                        stop = 'TIMEOUT_NO_RETRY'
                        break
                    except BaseException:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                        event(dict(case=name, state='INTERRUPTED'))
                        raise
                row.update(execution_status='PASS' if code == 0 else 'FAIL', returncode=code)
                event(dict(case=name, stage=stage, returncode=code))
                if code != 0:
                    stop = 'COMMAND_FAILED_NO_RETRY'
                    break
            if row['execution_status'] == 'PASS':
                checked = s.inspect_run(base / c['run'], config_verification=base / c['config_verification'])
                contract = c.get('workload_contract', {})
                workload = checked.get('workload', {})
                matches = all(type(workload.get(k)) is type(v) and workload.get(k) == v
                              for k, v in contract.items())
                if not s.case_ready(checked) or not matches:
                    row.update(execution_status='ERROR', reason='raw measurement/configuration not valid')
                    stop = 'INVALID_EVIDENCE'
            event(row)
    return dict(schema=1, cases=rows, elapsed_host_seconds=time.monotonic() - started,
                qualification='EXECUTION_ONLY_NOT_PERFORMANCE_PASS')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('check', 'assess', 'run'))
    parser.add_argument('policy', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    policy = s.read_json(args.policy)
    base = args.policy.resolve().parent
    source = base / policy['campaign']
    s.require(s.digest(source) == policy['campaign_sha256'], 'campaign hash mismatch')
    campaign = s.read_json(source)
    base = source.resolve().parent
    validate(policy, campaign)
    s.require(not args.output.exists(), 'output already exists')
    if args.action == 'run':
        result = execute(policy, campaign, base, args.output)
        target = args.output / 'summary.json'
    elif args.action == 'assess':
        result = assess(policy, campaign, s.campaign_report(campaign, base))
        target = args.output
    else:
        if policy.get('execute'):
            pins(policy, base)
        result = dict(status='PASS', scope='POLICY_SCHEMA_ONLY_NOT_RUNTIME', execute=policy.get('execute', []))
        target = args.output
    result.update(policy_sha256=s.digest(args.policy), campaign_sha256=s.digest(source))
    with target.open('x') as f:
        json.dump(result, f, indent=2, allow_nan=False)
        f.write('\n')
    if args.action == 'run' and any(r['execution_status'] != 'PASS' for r in result['cases']):
        raise SystemExit(2)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        raise SystemExit(f'soc-spec-policy: {exc}')
