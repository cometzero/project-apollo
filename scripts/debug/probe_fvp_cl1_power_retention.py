#!/usr/bin/env python3
"""Bounded CL1 power prerequisite survey, not a suspend/resume test.

Attach only to an owned disposable Iris model. The optional destructive power
cycle requests ordinary PPU OFF/ON, never forces acknowledgement or restores a
model snapshot. This sacrifices guest execution; it does NOT qualify retained
Zephyr context or cache/device quiescence. The caller owns process cleanup.
"""
import argparse
import json
from pathlib import Path
import signal
import sys
import time


PHYSICAL = 'Physical Memory (Secure)'


def power_cycle(model, cl0, gates, bases, result, access):
    """Sacrificial hardware probe. Ordinary documented PPU policy writes only."""
    cycle = result['power_cycle'] = {'status': 'FAIL', 'samples': [], 'ppu_access': access,
        'context_resume_passed': False, 'cache_quiescence_proven': False}
    # Stop management firmware as well so it cannot overwrite direct policy
    # requests or trigger PFDI recovery while the guest is deliberately broken.
    cl0_enabled = cl0.get_execution_state()
    cl0.set_execution_state(False)
    scratch = 0x1407fffc0
    original = None

    def read(addr):
        return int.from_bytes(cl0.read_memory(addr, memory_space=PHYSICAL,
                                             size=4, count=1), 'little')

    def policy(base, mode):
        value = (read(base) & ~0x10f) | mode
        if access == 'resource':
            index = next(i for i, (_, addr) in enumerate(bases) if addr == base)
            name = 'cluster' if index == 0 else f'core{index - 1}'
            ppu = model.get_target('component.RD_ASD.css.smb.si.cluster1.DSU.PPU_' + name)
            ppu.write_register('Default.PPU_PWPR', value)
        else:
            cl0.write_memory(base, value, memory_space=PHYSICAL, size=4, count=1,
                             do_side_effects=True)
        result['ppu_writes'] += 1

    def wait_state(targets, mode, phase):
        deadline = time.monotonic() + 8
        while True:
            states = {name: read(base + 8) for name, base in targets}
            cycle['samples'].append({'phase': phase, 'pwsr': states,
                'simulation_time': model.client.irisCall().simulationTime_get(instId=1)})
            if all((state & 0x10f) == mode for state in states.values()):
                return True
            if time.monotonic() >= deadline:
                return False
            # With per-instance execution gates the SDK's CPU run event can
            # remain unset while simulation time advances. Poll time directly.
            model.client.irisCall().simulationTime_run(instId=1)
            time.sleep(0.1)
            model.client.irisCall().simulationTime_stop(instId=1)
            stop_deadline = time.monotonic() + 5
            while model.client.irisCall().simulationTime_get(instId=1)['running']:
                if time.monotonic() >= stop_deadline:
                    raise TimeoutError('simulation time failed to stop')
                time.sleep(0.01)

    try:
        # Backup through CL0's physical bus, not a CL1 dirty cache. This is
        # deliberately NOT asserted to be unused guest memory.
        original = bytes(cl0.read_memory(scratch, memory_space=PHYSICAL, size=1, count=64))
        marker = bytes(value ^ 0xa5 for value in original)
        cycle['scratch'] = {'address': hex(scratch), 'original': original.hex(),
                            'marker': marker.hex(), 'ownership': 'sacrificial-backed-up'}
        cl0.write_memory(scratch, bytearray(marker), memory_space=PHYSICAL, size=1, count=64)
        result['memory_writes'] += 1
        if bytes(cl0.read_memory(scratch, memory_space=PHYSICAL, size=1, count=64)) != marker:
            raise RuntimeError('bus marker readback mismatch before power transition')
        for _, base in bases[1:]:
            policy(base, 0)
        cycle['cores_off'] = wait_state(bases[1:], 0, 'cores_off')
        if not cycle['cores_off']:
            raise RuntimeError('core PWSR did not acknowledge OFF; cluster OFF not requested')
        policy(bases[0][1], 0)
        cycle['cluster_off'] = wait_state(bases[:1], 0, 'cluster_off')
        if not cycle['cluster_off']:
            raise RuntimeError('cluster PWSR did not acknowledge OFF')
        cycle['off_pc'] = [cpu.get_pc() for cpu, _ in gates]
        policy(bases[0][1], 8)
        cycle['cluster_on'] = wait_state(bases[:1], 8, 'cluster_on')
        if not cycle['cluster_on']:
            raise RuntimeError('cluster PWSR did not acknowledge ON')
        for _, base in bases[1:]:
            policy(base, 8)
        cycle['cores_on'] = wait_state(bases[1:], 8, 'cores_on')
        if not cycle['cores_on']:
            raise RuntimeError('core PWSR did not acknowledge ON')
        cycle['on_pc_execution_gated'] = [cpu.get_pc() for cpu, _ in gates]
        observed = bytes(cl0.read_memory(scratch, memory_space=PHYSICAL, size=1, count=64))
        cycle['scratch']['after_on'] = observed.hex()
        cycle['scratch_retained'] = observed == marker
        cycle['status'] = 'PASS' if cycle['scratch_retained'] else 'FAIL'
    except Exception as exc:
        cycle['error'] = repr(exc)
    finally:
        # Best effort ordinary ON recovery only; do not run the sacrificed OS.
        try:
            for _, base in bases:
                policy(base, 8)
            cycle['cleanup_on'] = wait_state(bases, 8, 'cleanup_on')
            if original is not None and cycle['cleanup_on']:
                cl0.write_memory(scratch, bytearray(original), memory_space=PHYSICAL, size=1, count=64)
                result['memory_writes'] += 1
                cycle['scratch_backup_restored'] = bytes(cl0.read_memory(
                    scratch, memory_space=PHYSICAL, size=1, count=64)) == original
        except Exception as exc:
            cycle['cleanup_error'] = str(exc)
            # Bus PWPR writes can be unsupported even though the untouched
            # domains are still ON. Restore the memory backup in that case.
            if original is not None:
                try:
                    if all((read(base + 8) & 0xf) == 8 for _, base in bases):
                        cl0.write_memory(scratch, bytearray(original), memory_space=PHYSICAL,
                                         size=1, count=64)
                        result['memory_writes'] += 1
                        cycle['scratch_backup_restored'] = bytes(cl0.read_memory(
                            scratch, memory_space=PHYSICAL, size=1, count=64)) == original
                except Exception as restore_error:
                    cycle['scratch_restore_error'] = str(restore_error)
        cl0.set_execution_state(cl0_enabled)
    result['power_off_test'] = cycle['status']
    result['status'] = cycle['status']
    result['reason'] = 'Sacrificial PPU/SRAM capability test only; Zephyr context resume NOT_TESTED.'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iris-python', type=Path, required=True)
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=120)
    parser.add_argument('--disposable-power-cycle', action='store_true',
                        help='DESTRUCTIVE: sacrifice this owned guest with PPU OFF/ON requests')
    parser.add_argument('--ppu-access', choices=('bus', 'resource'), default='bus',
                        help='PWPR access route; both modes poll actual bus PWSR acknowledgement')
    args = parser.parse_args()
    if not 1 <= args.timeout <= 300 or not args.iris_python.is_dir():
        parser.error('valid Iris Python directory and timeout 1..300 required')
    sys.path.insert(0, str(args.iris_python))
    from iris.debug import Model

    def deadline(_signum, _frame):
        raise TimeoutError('probe wall-clock deadline')

    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(args.timeout)
    result = {'status': 'NOT_TESTED', 'context_resume_passed': False,
              'power_off_test': 'NOT_TESTED', 'memory_writes': 0,
              'ppu_writes': 0, 'execution_gates_restored': False,
              'reason': 'No validated four-core cache/device quiescence, '
                        'retained-memory contract or reset resume trampoline.',
              'cpus': [], 'ppu': [], 'endpoint': f'localhost:{args.port}'}
    model = None
    gates = []

    def attempt(call):
        try:
            return {'value': call()}
        except Exception as exc:
            return {'error': str(exc)}

    try:
        model = Model.NewNetworkModel('localhost', args.port,
                                      timeoutInMs=10000, synchronous=False)
        model.stop(timeout=10)
        result['simulation_time'] = model.client.irisCall().simulationTime_get(instId=1)
        prefix = 'component.RD_ASD.css.smb.si.'
        result['model_ppu_instances'] = [n for n in model.instance_infos
                                       if prefix in n and 'PPU' in n]
        for i in range(4):
            cpu = model.get_target(prefix + f'cluster1.cpu{i}')
            enabled = cpu.get_execution_state()
            gates.append((cpu, enabled))
            cpu.set_execution_state(False)
            result['cpus'].append({
                'core': i, 'pc': cpu.get_pc(), 'execution_was_enabled': enabled,
                'execution_gated': not cpu.get_execution_state(),
                'registers': {r: attempt(lambda r=r: cpu.read_register(r))
                              for r in ('X0', 'X19', 'SP', 'CPSR', 'SCTLR_EL1')}})
        cl0 = model.get_target(prefix + 'cluster0.cpu0')
        # CL0 address view, from RD-Aspen si0 config_ppu_v1.c / si0_mmap.h.
        bases = [('cluster1', 0x28810000)] + [
            (f'core{i}', 0x28840000 + i * 0x100000) for i in range(4)]
        for name, base in bases:
            result['ppu'].append({'name': name, 'base': hex(base),
                'registers': {name: attempt(lambda offset=offset: int.from_bytes(
                    cl0.read_memory(base + offset, memory_space='Physical Memory (Secure)', size=4, count=1),
                    'little')) for name, offset in (
                        ('PWPR', 0), ('PWSR', 8), ('DISR', 0x10),
                        ('IDR0', 0xfb0), ('IDR1', 0xfb4))}})
        # Read-only baseline: this is NOT an allocation or a retention test.
        result['llram_baseline'] = {'address': '0x1407fffc0', 'bytes': 64,
            **attempt(lambda: gates[0][0].read_memory(
                0x1407fffc0, memory_space='Physical Memory (Secure)', size=1, count=64).hex())}
        result['ppu_reads_completed'] = all(
            'value' in value for ppu in result['ppu']
            for value in ppu['registers'].values())
        result['survey_completed'] = (result['ppu_reads_completed'] and
                                      'value' in result['llram_baseline'])
        if args.disposable_power_cycle:
            if not result['survey_completed']:
                raise RuntimeError('power cycle requires successful baseline reads')
            power_cycle(model, cl0, gates, bases, result, args.ppu_access)
    except Exception as exc:
        result['survey_completed'] = False
        result['error'] = str(exc)
    finally:
        signal.alarm(0)
        result['restore_results'] = [attempt(lambda cpu=cpu, enabled=enabled:
            cpu.set_execution_state(enabled)) for cpu, enabled in gates]
        result['execution_gates_restored'] = (len(gates) == 4 and all(
            'error' not in item for item in result['restore_results']))
        if model is not None:
            result['disconnect'] = attempt(model.release)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, default=str) + '\n')
    print(json.dumps(result, indent=2, default=str))
    # Survey completion is not power-off or context resume success.
    passed = result.get('survey_completed') and result['execution_gates_restored']
    if args.disposable_power_cycle:
        passed = passed and result['power_off_test'] == 'PASS'
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
