#!/usr/bin/env python3
"""Intrusive, bounded run-to-breakpoint diagnosis of a captured AP warm stall.

Attach only after the caller's separate PPU observer has identified warm resume.
Never launches/stops a process, writes registers, acknowledges interrupts, or
gates individual CPUs. Global debug stop/run perturbs every domain: advancement
under this probe is NOT normal-runtime or OS-context-resume qualification.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time


def resolve_barriers(elf):
    text = subprocess.run(
        ['gdb-multiarch', '-q', '-batch', str(elf), '-ex',
         'disassemble /r gicv3_cpuif_enable'], check=True,
        capture_output=True, text=True, timeout=10).stdout
    instructions = []
    for line in text.splitlines():
        match = re.search(r'(0x[0-9a-f]+)\s+<\+\d+>:\s+([0-9a-f]{8})\s+(\w+)\b', line)
        if match:
            instructions.append((int(match[1], 16), int(match[2], 16), match[3]))
    for index in range(len(instructions) - 2, -1, -1):
        address, opcode, mnemonic = instructions[index]
        if mnemonic == 'isb' and instructions[index + 1][2] == 'dsb':
            tail = instructions[index:]
            if tail[-1][2] != 'ret':
                raise ValueError('unexpected CPU-interface epilogue')
            return tail, text
    raise ValueError('final ISB/DSB pair not found in matching ELF')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iris-python', type=Path, required=True)
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--tfa-elf', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--warm-resume-observed', action='store_true', required=True,
                        help='caller has independently observed OFF then warm resume')
    parser.add_argument('--host-timeout', type=float, default=10)
    parser.add_argument('--sim-timeout', type=float, default=5)
    args = parser.parse_args()
    if not 0 < args.host_timeout <= 10 or not 0 < args.sim_timeout <= 5:
        parser.error('maximum per-stage timeouts: 10 host seconds, 5 simulation seconds')
    result = {'status': 'NOT_TESTED', 'stages': [], 'cleanup_errors': [],
              'scope': 'intrusive debug run-to-breakpoint; not runtime qualification',
              'warm_resume_observed_by_caller': args.warm_resume_observed,
              'register_writes': False, 'individual_cpu_gating': False,
              'interrupt_acknowledges': False, 'context_resume_passed': False}
    model = None
    breakpoint = None
    initially_running = False
    snapshot = None
    try:
        tail, disassembly = resolve_barriers(args.tfa_elf)
        result.update(tfa_elf=str(args.tfa_elf.resolve()),
                      tfa_sha256=hashlib.sha256(args.tfa_elf.read_bytes()).hexdigest(),
                      disassembly=disassembly)
        sys.path.insert(0, str(args.iris_python))
        from iris.debug import Model
        model = Model.NewNetworkModel('localhost', args.port,
                                      timeoutInMs=2000, synchronous=False)
        call = model.client.irisCall()

        def stop_raw():
            # SDK Model.stop/run wait for callback Events. A breakpoint can
            # stop immediately, before that callback is delivered. Query the
            # authoritative state instead of treating a missed Event as a hang.
            if call.simulationTime_get(instId=1)['running']:
                call.simulationTime_stop(instId=1)
            deadline = time.monotonic() + 2
            while call.simulationTime_get(instId=1)['running']:
                if time.monotonic() >= deadline:
                    raise TimeoutError('raw simulation stop did not complete')
                time.sleep(.01)

        initially_running = bool(call.simulationTime_get(instId=1)['running'])
        result['initially_running'] = initially_running
        stop_raw()
        cl0 = model.get_target('component.RD_ASD.css.smb.si.cluster0.cpu0')
        cpu = model.get_target('component.RD_ASD.css.app00.cluster.cpu0')

        def require_on():
            states = {}
            for name, base in [('sys0', 0xd0021000), ('core0', 0xc1080000)]:
                states[name] = int.from_bytes(cl0.read_memory(
                    base + 8, memory_space='Physical Memory (Secure)',
                    size=4, count=1), 'little')
            if any(value & 0xf != 8 for value in states.values()):
                raise RuntimeError(f'AP not ON; refusing AP access: {states}')
            return states

        def snapshot():
            sample = {'ppu': require_on(),
                      'time': dict(call.simulationTime_get(instId=1)), 'registers': {}}
            # HPPIR observes pending priority; do NOT read IAR or write EOIR.
            for name in ('PC', 'CPSR', 'SCR_EL3', 'SPSR_EL3', 'ELR_EL3',
                         'ESR_EL3', 'FAR_EL3', 'VBAR_EL3', 'SCTLR_EL3',
                         'ICC_SRE_EL3', 'ICC_CTLR_EL3', 'ICC_CTLR_EL1',
                         'ICC_PMR_EL1', 'ICC_RPR_EL1', 'ICC_HPPIR0_EL1',
                         'ICC_HPPIR1_EL1', 'ICC_IGRPEN0_EL1', 'ICC_IGRPEN1_EL3'):
                try:
                    sample['registers'][name] = cpu.read_register(name)
                except Exception as exc:
                    sample['registers'][name] = {'unsupported': str(exc)}
            return sample

        result['before'] = snapshot()
        expected = tail[0][0]
        if result['before']['registers']['PC'] != expected:
            raise RuntimeError(f'expected final ISB PC {expected:#x}; no execution attempted')
        # Verify all instruction bytes, not only the symbol's address. AP SRAM
        # is accessed through its secure CL0 window only after ON verification.
        for address, opcode, _ in tail:
            actual = int.from_bytes(cl0.read_memory(
                0xe0030000 + address, memory_space='Physical Memory (Secure)',
                size=4, count=1), 'little')
            if actual != opcode:
                raise RuntimeError(f'live/ELF instruction mismatch at {address:#x}')
        result['live_epilogue_matches_elf'] = True

        # First stop BEFORE DSB; next stop BEFORE RET. No instruction skipping
        # and no single-CPU step API (which may gate other CPUs implicitly).
        for target_pc, label in [(tail[1][0], 'isb_to_dsb'), (tail[-1][0], 'dsb_to_ret')]:
            stage = {'name': label, 'expected_pc': target_pc}
            result['stages'].append(stage)
            breakpoint = cpu.add_bpt_prog(target_pc)
            start = dict(call.simulationTime_get(instId=1))
            deadline = time.monotonic() + args.host_timeout
            call.simulationTime_run(instId=1)
            reason = 'HOST_TIMEOUT'
            while time.monotonic() < deadline:
                now = call.simulationTime_get(instId=1)
                if not now['running']:
                    reason = 'MODEL_STOPPED'
                    break
                if (now['ticks'] - start['ticks']) / now['tickHz'] >= args.sim_timeout:
                    reason = 'SIM_TIMEOUT'
                    break
                time.sleep(.02)
            stop_raw()
            stage['stop_reason'] = reason
            stage['after'] = snapshot()
            stage['reached_expected_pc'] = stage['after']['registers']['PC'] == target_pc
            breakpoint.delete()
            breakpoint = None
            if not stage['reached_expected_pc']:
                result['status'] = 'DID_NOT_REACH_NEXT_INSTRUCTION'
                break
        else:
            result['status'] = 'DEBUG_REACHED_RET'
    except Exception as exc:
        result['status'] = 'ERROR'
        result['error'] = repr(exc)
    finally:
        if model is not None:
            try:
                stop_raw()
                if snapshot is not None:
                    # Capture even after a run/stop RPC error, BEFORE removing
                    # our breakpoint. This distinguishes immediate hits from
                    # genuine failure to retire the barrier.
                    result['cleanup_snapshot'] = snapshot()
            except Exception as exc:
                result['cleanup_errors'].append(repr(exc))
            try:
                if breakpoint is not None:
                    breakpoint.delete()
                result['owned_breakpoint_removed'] = True
            except Exception as exc:
                result['cleanup_errors'].append(repr(exc))
            try:
                if initially_running and not result['cleanup_errors']:
                    call.simulationTime_run(instId=1)
                result['final_running'] = bool(
                    model.client.irisCall().simulationTime_get(instId=1)['running'])
            except Exception as exc:
                result['cleanup_errors'].append(repr(exc))
            try:
                model.release(shutdown=False)
            except Exception as exc:
                result['cleanup_errors'].append(repr(exc))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'output': str(args.output)}))
    return 0 if result['status'] == 'DEBUG_REACHED_RET' and not result['cleanup_errors'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
