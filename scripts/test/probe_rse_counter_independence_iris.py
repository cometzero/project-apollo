#!/usr/bin/env python3
"""Destructive register experiment on an explicitly disposable RSE FVP only.

Attach after boot, leave the simulation stopped, and discard the instance after
collecting evidence. Never use on a session whose firmware state must survive.
"""
import argparse
import json
from pathlib import Path
import sys
import time
import traceback


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iris-python', type=Path, required=True)
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sample-wall-seconds', type=float, default=0.05)
    parser.add_argument('--disposable', action='store_true', required=True)
    args = parser.parse_args()
    if not 0 < args.sample_wall_seconds <= 5:
        parser.error('--sample-wall-seconds must be in (0, 5]')
    sys.path.insert(0, str(args.iris_python))
    from iris.debug import Model
    model = Model.NewNetworkModel('localhost', args.port, synchronous=False)
    result = {'scope': 'disposable FVP register experiment; not firmware qualification',
              'samples': {}, 'checks': {}}
    try:
        model.stop(timeout=30)
        cpu = model.get_target('component.RD_ASD.css.smb.rseil.rse.cpu')

        def read(address):
            return int.from_bytes(cpu.read_memory(address, memory_space='SP',
                                  size=4, count=1), 'little')

        def write(address, value):
            cpu.write_memory(address, value, memory_space='SP', size=4, count=1,
                             do_side_effects=True)

        def snap(name):
            sample = {'time': dict(model.client.irisCall().simulationTime_get(instId=1)),
                      'pc': cpu.get_pc(), 'timers': [], 'systick': []}
            for i in range(4):
                base = 0x58000000 + 0x1000 * i
                sample['timers'].append({
                    'count': read(base) | read(base + 4) << 32,
                    'cval': read(base + 0x20) | read(base + 0x24) << 32,
                    'tval': read(base + 0x28), 'control': read(base + 0x2c),
                    'freq': read(base + 0x10)})
            for base in (0xe000e010, 0xe002e010):
                sample['systick'].append(dict(zip(('ctrl', 'load', 'value', 'calib'),
                    (read(base + offset) for offset in (0, 4, 8, 12)))))
            result['samples'][name] = sample
            print(name, json.dumps(sample), flush=True)
            return sample

        def advance():
            model.run(blocking=False, timeout=30)
            time.sleep(args.sample_wall_seconds)
            model.stop(timeout=30)

        initial = snap('booted')
        result['lsc_access'] = {}
        for address in (0x5015a000, 0x5015b008):
            try:
                result['lsc_access'][hex(address)] = read(address)
            except Exception as error:
                result['lsc_access'][hex(address)] = {'status': 'UNSUPPORTED', 'error': str(error)}
        advance()
        progressed = snap('progressed')
        result['checks']['shared_counter_observation'] = (
            len({t['count'] for t in initial['timers']}) == 1 and
            len({t['count'] for t in progressed['timers']}) == 1 and
            progressed['timers'][0]['count'] > initial['timers'][0]['count'])
        # Quiesce firmware without stopping simulation time. This is debugger
        # execution gating, not an architectural clock/power/reset experiment.
        cpu.set_execution_state(False)
        before = snap('cpu_gated')
        compare = before['timers'][3]['cval'] ^ 0x1212345678
        write(0x58003020, compare & 0xffffffff)
        write(0x58003024, compare >> 32)
        after = snap('timer3_compare_changed')
        result['checks']['separate_compare_state'] = (
            after['timers'][3]['cval'] == compare and
            all(a['count'] == b['count'] for a, b in zip(before['timers'], after['timers'])) and
            all(before['timers'][i]['cval'] == after['timers'][i]['cval'] for i in range(3)))
        for base, load in ((0xe000e010, 0xffffff), (0xe002e010, 0x7fffff)):
            write(base, 0)
            write(base + 4, load)
            write(base + 8, 0)
        configured = snap('systick_configured')
        result['checks']['systick_state_separate'] = (
            [s['load'] for s in configured['systick']] == [0xffffff, 0x7fffff] and
            all(s['value'] == 0 for s in configured['systick']) and
            configured['timers'] == after['timers'])
        for source in (0, 1):
            for base in (0xe000e010, 0xe002e010):
                write(base, 0)
                write(base + 8, 0)
                write(base, 1 | source << 2)  # ENABLE, no TICKINT
            snap(f'clksource_{source}_before')
            advance()
            sample = snap(f'clksource_{source}_after')
            result['checks'][f'clksource_{source}_readback'] = all(
                (s['ctrl'] & 7) == (1 | source << 2) for s in sample['systick'])
            # Measure after the initial reload, with modulo-wrap protection.
            advance()
            end = snap(f'clksource_{source}_steady')
            seconds = (end['time']['ticks'] - sample['time']['ticks']) / end['time']['tickHz']
            result.setdefault('rates', {})[str(source)] = {
                'simulation_seconds': seconds,
                'timer_hz': (end['timers'][0]['count'] - sample['timers'][0]['count']) / seconds,
                'systick_modulo_hz': [((a['value'] - b['value']) % (a['load'] + 1)) / seconds
                                     for a, b in zip(sample['systick'], end['systick'])],
                'warning': 'SysTick rate ambiguous if one or more full periods elapsed.'}
        result['limitations'] = [
            'Equal TIMER counts support shared CNTVALUEB but do not inspect FVP internal state.',
            'CPU execution gating may affect SysTick; not proof of hardware clock gating.',
            'No reset, IRQ handler delivery, or cycle-accurate clock-frequency qualification.',
            'Register writes are not restored; discard this disposable model.']
    except Exception as error:
        result['error'] = repr(error)
        result['traceback'] = traceback.format_exc()
    finally:
        model.release()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    return 1 if 'error' in result or not all(result['checks'].values()) else 0


if __name__ == '__main__':
    raise SystemExit(main())
