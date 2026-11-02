# SPDX-License-Identifier: BSD-3-Clause
import copy
from pathlib import Path
import sys
import tempfile
import unittest

import soc_spec_policy as p


def setup():
    comparisons = [dict(id='pair', baseline='b', candidate='c', metrics=['latency'])]
    results = [dict(id='pair', status='PASS', metrics={'latency': dict(before=10, after=8, unit='ns')})]
    pair = dict(condition='nominal', comparison='pair', coordinates={'profile.cpu.clock': '1GHz'})
    for role, case in [('baseline', 'b'), ('candidate', 'c')]:
        pair[role + '_stability'] = []
        for dim in ['warmup_passes', 'frames']:
            name = case + dim
            pair[role + '_stability'].append(name)
            comparisons.append(dict(id=name, kind='convergence', baseline=case, candidate=case+'2'))
            results.append(dict(id=name, status='FAIL', changes={'workload': {dim: {}}},
                                metrics={'latency': {'status': 'PASS'}, 'dram_ratio': {'status': 'FAIL'}}))
    campaign = dict(cases=[dict(id=n) for n in ['b','c']], comparisons=comparisons)
    policy = dict(schema=1, budget=dict(max_runs=2, host_seconds=20, basis='test pilot'), execute=[],
                  assessments=[dict(id='cache', direction='lower', metric='latency', min_gain=.1,
                                    basis='hypothetical range', required_conditions=['nominal'], pairs=[pair])])
    report = dict(cases=[dict(id=n, identity={'profile': {'cpu': {'clock': '1GHz'}}}) for n in ['b','c']],
                  comparisons=results)
    return policy, campaign, report


class AssessmentTests(unittest.TestCase):
    def test_primary_and_explanatory_are_separate(self):
        policy, campaign, report = setup()
        row = p.assess(policy,campaign,report)['assessments'][0]
        self.assertEqual(row['conclusion'], 'ROBUST_IN_TESTED_CONDITIONS')
        self.assertEqual(row['product_decision'], 'UNDECIDED')
        self.assertEqual(row['pairs'][0]['gain'], .25)
        self.assertEqual(report['comparisons'][1]['status'], 'FAIL')

    def test_missing_gate_never_becomes_stable(self):
        a,b,c=setup();a['assessments'][0]['pairs'][0]['baseline_stability']=[]
        self.assertEqual(p.assess(a,b,c)['assessments'][0]['conclusion'],'INCONCLUSIVE')

    def test_coordinate_mismatch_rejects_pair(self):
        a,b,c=setup();c['cases'][1]['identity']['profile']['cpu']['clock']='2GHz'
        row=p.assess(a,b,c)['assessments'][0]['pairs'][0]
        self.assertEqual(row['status'],'INCONCLUSIVE');self.assertNotIn('gain',row)

    def test_missing_condition_cannot_support_robustness(self):
        a,b,c=setup();a['assessments'][0]['required_conditions'].append('low')
        self.assertEqual(p.assess(a,b,c)['assessments'][0]['conclusion'],'INCONCLUSIVE')

    def test_workload_change_rejected(self):
        a,b,c=setup();b['comparisons'][0]['allowed_workload_changes']=['kernel']
        with self.assertRaises(ValueError):p.validate(a,b)

    def test_duplicate_coordinates_rejected(self):
        a,b,c=setup();g=a['assessments'][0];g['required_conditions'].append('low')
        pair=copy.deepcopy(g['pairs'][0]);pair['condition']='low';g['pairs'].append(pair)
        with self.assertRaises(ValueError):p.validate(a,b)

    def test_calibration_validation_overlap_rejected(self):
        a,b,c=setup();a.update(calibration_cases=['b'],validation_cases=['b'])
        with self.assertRaises(ValueError):p.validate(a,b)

    def test_sign_reversal_at_distinct_bound_conditions(self):
        a,b,c=setup();g=a['assessments'][0];g['required_conditions'].append('low')
        pair=copy.deepcopy(g['pairs'][0]);pair.update(condition='low',comparison='pair-low',
                                                    coordinates={'profile.cpu.clock':'500MHz'})
        for role in ['baseline','candidate']:
            pair[role+'_stability']=[n+'-low' for n in pair[role+'_stability']]
        g['pairs'].append(pair)
        for definition in list(b['comparisons']):
            d=copy.deepcopy(definition);d['id']+='-low'
            d['baseline']+='-low';d['candidate']+='-low';b['comparisons'].append(d)
        for result in list(c['comparisons']):
            r=copy.deepcopy(result);r['id']+='-low'
            if r['id']=='pair-low':r['metrics']['latency']['after']=12
            c['comparisons'].append(r)
        for name in ['b-low','c-low']:
            b['cases'].append(dict(id=name))
            c['cases'].append(dict(id=name,identity={'profile':{'cpu':{'clock':'500MHz'}}}))
        row=p.assess(a,b,c)['assessments'][0]
        self.assertTrue(row['sign_reversal'])
        self.assertEqual(row['conclusion'],'CONDITIONAL')

    def test_larger_is_better_gain(self):
        a,b,c=setup();a['assessments'][0]['direction']='higher'
        self.assertAlmostEqual(p.assess(a,b,c)['assessments'][0]['pairs'][0]['gain'],-.2)

    def test_no_budget_or_boolean_budget_rejected(self):
        for val in (0,True,-1):
            a,b,c=setup();a['budget']['max_runs']=val
            with self.assertRaises(ValueError):p.validate(a,b)


class ExecutionTests(unittest.TestCase):
    def test_timeout_kills_only_owned_group_and_records_remaining(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source';source.write_text('pinned')
            a,b,_=setup();a['assessments']=[];a['execute']=['b','c'];a['pins']={'source':p.s.digest(source)}
            for case in b['cases']:
                case.update(run=case['id'],config_verification=case['id']+'.json',timeout_seconds=.05,
                            argv=[sys.executable,'-c','import time; time.sleep(5)'],
                            verification_argv=[sys.executable,'-c','raise SystemExit(0)'])
            result=p.execute(a,b,root,root/'out')
            self.assertEqual([r['execution_status'] for r in result['cases']],['TIMEOUT','NOT_RUN'])
            self.assertLess(result['elapsed_host_seconds'],3)

    def test_nonzero_launch_does_not_run_verifier_or_next_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source';source.write_text('pinned')
            a,b,_=setup();a['assessments']=[];a['execute']=['b','c'];a['pins']={'source':p.s.digest(source)}
            for case in b['cases']:
                case.update(run=case['id'],config_verification=case['id']+'.json',timeout_seconds=1,
                            argv=[sys.executable,'-c','raise SystemExit(3)'],verification_argv=['true'])
            result=p.execute(a,b,root,root/'out')
            self.assertEqual([r['execution_status'] for r in result['cases']],['FAIL','NOT_RUN'])
            self.assertFalse((root/'out/1-verify.log').exists())

    def test_existing_artifact_and_changed_pin_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source';source.write_text('pinned')
            a,b,_=setup();a['assessments']=[];a['execute']=['b'];a['pins']={'source':p.s.digest(source)}
            b['cases'][0].update(run='run',config_verification='v.json',timeout_seconds=1,
                                argv=['true'],verification_argv=['true'])
            (root/'run').mkdir()
            with self.assertRaises(ValueError):p.execute(a,b,root,root/'out')
            (root/'run').rmdir();source.write_text('changed')
            with self.assertRaises(ValueError):p.execute(a,b,root,root/'out')
            self.assertFalse((root/'out').exists())

    def test_command_success_does_not_imply_measurement_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source';source.write_text('pin')
            a,b,_=setup();a['assessments']=[];a['execute']=['b'];a['pins']={'source':p.s.digest(source)}
            b['cases'][0].update(run='run',config_verification='v.json',timeout_seconds=1,
                                argv=['true'],verification_argv=['true'])
            result=p.execute(a,b,root,root/'out')
            self.assertEqual(result['cases'][0]['execution_status'],'ERROR')


if __name__=='__main__':unittest.main()
