#!/usr/bin/env python3
"""Observe four real TF-A GIC context calls on a caller-owned FVP.

Install before guest suspend, with no other Iris observer controlling run/stop.
Global breakpoint stops perturb execution. Four entry hits prove calls, not
successful completion or OS context return; collect the OS witness separately.
No firmware/memory/register writes, interrupt acknowledges, or CPU gating.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

FUNCTIONS = ('gicv3_rdistif_save', 'gicv3_distif_save',
             'gicv3_distif_init_restore', 'gicv3_rdistif_init_restore')


def resolve(elf):
    command = ['gdb-multiarch', '-q', '-batch', str(elf)]
    for name in FUNCTIONS:
        command.extend(['-ex', f'disassemble /r {name}'])
    output = subprocess.run(command, capture_output=True, text=True,
                            check=True, timeout=10).stdout
    resolved = {}
    for name in FUNCTIONS:
        pattern = (rf'Dump of assembler code for function {name}:\s*'
                   r'(0x[0-9a-f]+)\s+<\+0>:\s+([0-9a-f]{8})\b')
        match = re.search(pattern, output)
        if not match:
            raise ValueError(f'cannot resolve exact function entry: {name}')
        resolved[name] = {'address': int(match[1], 16), 'opcode': int(match[2], 16)}
    if len({item['address'] for item in resolved.values()}) != len(FUNCTIONS):
        raise ValueError('function entries alias')
    return resolved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iris-python', type=Path, required=True)
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--tfa-elf', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=float, default=150)
    args = parser.parse_args()
    if not 0 < args.timeout <= 150:
        parser.error('timeout must be > 0 and <= 150 host seconds')
    result = {'status': 'NOT_TESTED', 'calls': [], 'cleanup_errors': [],
              'scope': 'debug-intrusive ordered function-entry proof only',
              'register_writes': False, 'individual_cpu_gating': False,
              'os_context_return_verified': False}
    model = None
    owned = {}
    initially_running = False
    try:
        result['symbols'] = symbols = resolve(args.tfa_elf)
        result['elf'] = str(args.tfa_elf.resolve())
        result['elf_sha256'] = hashlib.sha256(args.tfa_elf.read_bytes()).hexdigest()
        sys.path.insert(0, str(args.iris_python))
        from iris.debug import Model
        model = Model.NewNetworkModel('localhost', args.port,
                                      timeoutInMs=2000, synchronous=False)
        call = model.client.irisCall()

        def stop():
            if call.simulationTime_get(instId=1)['running']:
                call.simulationTime_stop(instId=1)
            deadline = time.monotonic() + 2
            while call.simulationTime_get(instId=1)['running']:
                if time.monotonic() >= deadline:
                    raise TimeoutError('model stop did not complete')
                time.sleep(.01)

        initially_running = bool(call.simulationTime_get(instId=1)['running'])
        result['initially_running'] = initially_running
        stop()
        cpu = model.get_target('component.RD_ASD.css.app00.cluster.cpu0')
        cl0 = model.get_target('component.RD_ASD.css.smb.si.cluster0.cpu0')
        for name, symbol in symbols.items():
            owned[name] = cpu.add_bpt_prog(symbol['address'])
        result['armed_time'] = dict(call.simulationTime_get(instId=1))
        print('GIC context breakpoints armed', flush=True)
        deadline = time.monotonic() + args.timeout
        call.simulationTime_run(instId=1)
        while owned and time.monotonic() < deadline:
            now = dict(call.simulationTime_get(instId=1))
            if now['running']:
                time.sleep(.02)
                continue
            # Never access AP registers/SRAM without physical power readback.
            ppu = {}
            for name, base in [('sys0', 0xd0021000), ('core0', 0xc1080000)]:
                ppu[name] = int.from_bytes(cl0.read_memory(
                    base + 8, memory_space='Physical Memory (Secure)',
                    size=4, count=1), 'little')
            if any(value & 0xf != 8 for value in ppu.values()):
                raise RuntimeError(f'unexpected model stop with AP not ON: {ppu}')
            pc = cpu.read_register('PC')
            name = next((name for name in owned if symbols[name]['address'] == pc), None)
            if name is None:
                raise RuntimeError(f'unowned model stop at PC {pc:#x}; not resuming it')
            opcode = int.from_bytes(cl0.read_memory(
                0xe0030000 + pc, memory_space='Physical Memory (Secure)',
                size=4, count=1), 'little')
            hit = {'function': name, 'time': now, 'PC': pc, 'ppu': ppu,
                   'X0': cpu.read_register('X0'), 'X1': cpu.read_register('X1'),
                   'opcode': opcode, 'instruction_matches_elf': opcode == symbols[name]['opcode']}
            result['calls'].append(hit)
            if not hit['instruction_matches_elf']:
                raise RuntimeError('live instruction does not match supplied ELF')
            owned[name].delete()
            del owned[name]
            print(json.dumps(hit), flush=True)
            if owned:
                call.simulationTime_run(instId=1)
        result['ordered_calls_observed'] = [hit['function'] for hit in result['calls']] == list(FUNCTIONS)
        result['status'] = 'ORDERED_CALLS_OBSERVED' if result['ordered_calls_observed'] else 'INCOMPLETE'
    except Exception as exc:
        result['status'] = 'ERROR'
        result['error'] = repr(exc)
    finally:
        if model is not None:
            try:
                stop()
            except Exception as exc:
                result['cleanup_errors'].append(repr(exc))
            for name, breakpoint in list(owned.items()):
                try:
                    breakpoint.delete()
                    del owned[name]
                except Exception as exc:
                    result['cleanup_errors'].append(f'{name}: {exc!r}')
            result['owned_breakpoints_removed'] = not owned
            try:
                if initially_running and not result['cleanup_errors'] and result['status'] != 'ERROR':
                    call.simulationTime_run(instId=1)
                result['final_running'] = bool(call.simulationTime_get(instId=1)['running'])
            except Exception as exc:
                result['cleanup_errors'].append(repr(exc))
            try:
                model.release(shutdown=False)
            except Exception as exc:
                result['cleanup_errors'].append(repr(exc))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    return 0 if result['status'] == 'ORDERED_CALLS_OBSERVED' and not result['cleanup_errors'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
