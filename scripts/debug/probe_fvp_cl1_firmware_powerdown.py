#!/usr/bin/env python3
"""Cold-load an isolated CL1 ELF and qualify its real PWRDN/WFI handshake.

Owned disposable FVP only, initially stopped at simulation time zero. This
replaces the RSE-loaded CL1 application at its first reset instruction. Initial
PC setup is a debugger ELF bootstrap, never context resume. The caller owns
the bounded launcher and must terminate it after this destructive experiment.
"""
import argparse
import hashlib
import json
from pathlib import Path
import signal
import socket
import struct
import subprocess
import sys
import time

from probe_fvp_cl1_power_retention import PHYSICAL


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iris-python', type=Path, required=True)
    p.add_argument('--elf', type=Path, required=True)
    p.add_argument('--port', type=int, required=True)
    p.add_argument('--uart-port', type=int, default=5002)
    p.add_argument('--cl0-uart-port', type=int, default=5001)
    p.add_argument('--ppu-access', choices=('scp-call', 'scp-cli', 'resource'), default='scp-call')
    p.add_argument('--scp-elf', type=Path, default=Path(__file__).resolve().parents[2] /
                   'build/tmp_baremetal/deploy/images/apollo-fvp/si0_ramfw.elf')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--timeout', type=int, default=240)
    args = p.parse_args()
    if not 30 <= args.timeout <= 500:
        p.error('timeout must be 30..500 seconds')
    elf = args.elf.read_bytes()
    if elf[:6] != b'\x7fELF\x02\x01':
        p.error('expected little-endian ELF64')
    entry = struct.unpack_from('<Q', elf, 24)[0]
    if not 0x140000000 <= entry < 0x140800000:
        p.error('ELF entry must be in CL1 LLRAM')
    sys.path.insert(0, str(args.iris_python))
    from iris.debug import Model

    result = {'status': 'FAIL', 'context_resume_passed': False,
              'initial_bootstrap_only': True, 'samples': [],
              'elf': str(args.elf.resolve()), 'elf_sha256': hashlib.sha256(elf).hexdigest(),
              'elf_entry': entry, 'uart': '', 'cl0_uart': '', 'ppu_writes': [],
              'ppu_access': args.ppu_access}
    model = uart = None
    cl0_uart = None
    cl0 = None
    cl0_enabled = None
    breakpoints = []
    cpus = []

    def timeout(_signum, _frame):
        raise TimeoutError('overall firmware powerdown deadline')

    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(args.timeout)
    try:
        model = Model.NewNetworkModel('localhost', args.port,
                                      timeoutInMs=10000, synchronous=False)
        call = model.client.irisCall()

        def stopped():
            call.simulationTime_stop(instId=1)
            deadline = time.monotonic() + 10
            while call.simulationTime_get(instId=1)['running']:
                if time.monotonic() > deadline:
                    raise TimeoutError('simulation stop timeout')
                time.sleep(.01)

        def advance(seconds=.1):
            call.simulationTime_run(instId=1)
            time.sleep(seconds)
            stopped()

        def uart_drain():
            while True:
                try:
                    data = uart.recv(8192)
                    if not data:
                        return
                    result['uart'] += data.decode('utf-8', errors='replace')
                except (BlockingIOError, socket.timeout):
                    return

        stopped()
        now = call.simulationTime_get(instId=1)
        result['initial_time'] = now
        if now['ticks'] != 0:
            raise RuntimeError('must attach before initial simulation run')
        prefix = 'component.RD_ASD.css.smb.si.'
        cpus = [model.get_target(prefix + f'cluster1.cpu{i}') for i in range(4)]
        cl0 = model.get_target(prefix + 'cluster0.cpu0')
        for cpu in cpus:
            bp = cpu.add_bpt_prog(0x140000000)
            breakpoints.append((cpu, bp.number))
        model.run(blocking=True, timeout=90)
        result['preload_pcs'] = [cpu.get_pc() for cpu in cpus]
        if 0x140000000 not in result['preload_pcs']:
            raise RuntimeError('did not hit CL1 initial reset entry')
        # RSE firmware loading has finished for this cluster. Do not boot the
        # original application, which would overwrite the sample's state.
        cpus[0].load_application(str(args.elf.resolve()))
        for cpu in cpus:
            cpu.write_register('PC', entry)
        result['bootstrap_pcs'] = [cpu.get_pc() for cpu in cpus]
        for cpu, bp in breakpoints:
            cpu.remove_bpt(bp)
        breakpoints.clear()
        uart = socket.create_connection(('127.0.0.1', args.uart_port), timeout=5)
        uart.setblocking(False)
        boot_deadline = time.monotonic() + 45
        while 'CL1_POWERDOWN_PROBE_READY' not in result['uart']:
            if time.monotonic() >= boot_deadline:
                raise TimeoutError('isolated app banner not observed')
            advance(.2)
            uart_drain()
        result['application_booted'] = True
        # Baseline VBAR_EL2 is zero. Catch the first EL2 exception before an
        # unmapped vector instruction overwrites ESR/ELR with a nested fault.
        for cpu in cpus:
            for vector in (0x200, 0x400):
                bp = cpu.add_bpt_prog(vector)
                breakpoints.append((cpu, bp.number))
        def cli_drain():
            while True:
                try:
                    data = cl0_uart.recv(8192)
                    if not data:
                        return
                    result['cl0_uart'] += data.decode('utf-8', errors='replace')
                except (BlockingIOError, socket.timeout):
                    return

        def cli_command(command):
            cli_drain()
            begin = len(result['cl0_uart'])
            cl0_uart.setblocking(True)
            cl0_uart.settimeout(5)
            cl0_uart.sendall(command.encode() + b'\r\n')
            cl0_uart.setblocking(False)
            deadline = time.monotonic() + 8
            while True:
                advance(.05)
                cli_drain()
                response = result['cl0_uart'][begin:]
                if response.endswith('> '):
                    return response
                if time.monotonic() >= deadline:
                    raise TimeoutError(f'CL0 CLI command did not return: {command}')

        if args.ppu_access == 'scp-cli':
            cl0_uart = socket.create_connection(('127.0.0.1', args.cl0_uart_port), timeout=5)
            cl0_uart.sendall(b'\x05')
            cl0_uart.setblocking(False)
            deadline = time.monotonic() + 15
            while '[CLI_DEBUGGER_MODULE] Entering CLI' not in result['cl0_uart']:
                if time.monotonic() >= deadline:
                    raise TimeoutError('CL0 Ctrl-E debugger CLI entry timeout')
                advance(.1)
                cli_drain()
            # Normal CLI blocks the SCP event queue, not CPU execution. This
            # isolates PFDI dispatch while executing stock writemem STRs.
            result['cl0_cli_blocks_event_queue'] = True
        else:
            cl0_enabled = cl0.get_execution_state()
            cl0.set_execution_state(False)
            result['cl0_gated_for_pfdi_isolation'] = True
        # All CL1 cores continue executing actual firmware, never debug-gated.
        uart.setblocking(True)
        uart.settimeout(5)
        uart.sendall(b'cl1_powerdown\r\n')
        uart.setblocking(False)
        bases = [('cluster', 0x28810000)] + [
            (f'core{i}', 0x28840000 + i * 0x100000) for i in range(4)]

        def read(address):
            return int.from_bytes(cl0.read_memory(address, memory_space=PHYSICAL,
                                                  size=4, count=1), 'little')

        def scp_call(base, mode, redistributor=False):
            """Execute stock SCP instructions; restore debugger-call state only."""
            source = args.scp_elf.read_bytes()
            symbols = subprocess.check_output(['nm', str(args.scp_elf)], text=True)
            function = 'set_redistributor_power' if redistributor else 'ppu_v1_request_power_mode'
            address = next(int(line.split()[0], 16) for line in symbols.splitlines()
                           if line.split()[-1] == function)
            code_size = 0x6c if redistributor else 0x50
            after_offset = 0x40 if redistributor else 0x44
            phoff = struct.unpack_from('<Q', source, 32)[0]
            phsize, phnum = struct.unpack_from('<HH', source, 54)
            code = None
            for i in range(phnum):
                typ, _, offset, va, _, filesz, _, _ = struct.unpack_from(
                    '<IIQQQQQQ', source, phoff + i * phsize)
                if typ == 1 and va <= address and address + code_size <= va + filesz:
                    code = source[offset + address - va:offset + address - va + code_size]
            # This explicit instruction contract prevents running an unknown
            # binary layout with hardcoded after-store/return checkpoints.
            expected = bytes.fromhex('612600b9') if redistributor else bytes.fromhex('036000b9410000b9')
            if code is None or code[0x3c:after_offset] != expected:
                raise RuntimeError(f'unsupported SCP function layout: {function} STR contract')
            actual = bytes(cl0.read_memory(address, memory_space=PHYSICAL, size=1, count=len(code)))
            if actual != code:
                raise RuntimeError('running SCP function differs from supplied ELF')
            saved = {r: cl0.read_register(r) for r in
                     [f'X{i}' for i in range(31)] + ['SP', 'PC', 'CPSR']}
            if not 0x120000100 < saved['SP'] < 0x121000000:
                raise RuntimeError('CL0 stack is outside expected private SRAM')
            scratch = (saved['SP'] - 256) & ~15
            backup = bytes(cl0.read_memory(scratch, memory_space=PHYSICAL, size=1, count=256))
            context = scratch + 64
            record = {'function': address, 'saved_pc': saved['PC'], 'saved_sp': saved['SP'],
                      'function_name': function,
                      'scp_elf_sha256': hashlib.sha256(source).hexdigest(),
                      'function_bytes_verified': True, 'mode': mode, 'ppu_base': base,
                      'restoration_scope': 'debugger function call only, not suspend context'}
            result.setdefault('scp_calls', []).append(record)
            local_bps = []
            try:
                cl0.write_memory(context, bytearray(struct.pack('<QQ', base, 0x28880000)),
                                 memory_space=PHYSICAL, size=1, count=16)
                cl0.write_register('CPSR', saved['CPSR'] | 0x3c0)
                cl0.write_register('X0', base if redistributor else context)
                cl0.write_register('X1', mode)
                cl0.write_register('X30', saved['PC'])
                cl0.write_register('PC', address)
                after_store = cl0.add_bpt_prog(address + after_offset)
                local_bps.append(after_store.number)
                cl0.set_execution_state(True)
                model.run(blocking=True, timeout=10)
                record['after_store_pc'] = cl0.get_pc()
                if record['after_store_pc'] != address + after_offset:
                    raise RuntimeError(f'stock SCP did not retire {function} register STR')
                record['register_after_str'] = read(base + 0x24 if redistributor else base)
                if not redistributor:
                    record['pwpr_after_str'] = record['register_after_str']
                cl0.remove_bpt(after_store.number)
                local_bps.clear()
                ret = cl0.add_bpt_prog(saved['PC'])
                local_bps.append(ret.number)
                model.run(blocking=True, timeout=10)
                record['return_pc'] = cl0.get_pc()
                record['return_code'] = cl0.read_register('X0')
                if record['return_pc'] != saved['PC'] or record['return_code'] != 0:
                    raise RuntimeError('stock SCP call failed to return successfully')
            finally:
                stopped()
                cl0.set_execution_state(False)
                for bp in local_bps:
                    cl0.remove_bpt(bp)
                cl0.write_memory(scratch, bytearray(backup), memory_space=PHYSICAL, size=1, count=256)
                for register, value in saved.items():
                    cl0.write_register(register, value)
                record['debug_call_state_restored'] = all(
                    cl0.read_register(register) == value for register, value in saved.items())
                record['scratch_restored'] = bytes(cl0.read_memory(
                    scratch, memory_space=PHYSICAL, size=1, count=256)) == backup

        def snapshot(phase):
            sample = {'phase': phase, 'time': call.simulationTime_get(instId=1),
                      'pwsr': {name: read(base + 8) for name, base in bases}}
            result['samples'].append(sample)
            return sample['pwsr']

        def policy(name, base, mode):
            value = (read(base) & ~0x10f) | mode
            if args.ppu_access == 'scp-call':
                scp_call(base, mode)
                response = None
            elif args.ppu_access == 'scp-cli':
                # Match ppu_v1_write_ppu_reg: AE key unlock immediately before
                # each protected PPU write. Stock CLI performs actual CPU STR.
                cli_command('writemem 0x28880060 4 0xba')
                response = cli_command(f'writemem {base:#x} 4 {value:#x}')
            else:
                ppu = model.get_target(prefix + 'cluster1.DSU.PPU_' + name)
                ppu.write_register('Default.PPU_PWPR', value)
                response = None
            result['ppu_writes'].append({'name': name, 'mode': mode,
                                          'pwpr_readback': read(base),
                                          'cli_response': response})

        advance(.5)
        uart_drain()
        if args.ppu_access == 'resource' and any(cpu.get_pc() in (0x200, 0x400) for cpu in cpus):
            raise RuntimeError('EL2 exception during firmware powerdown; inspect final ESR/ELR')
        result['firmware_command_armed'] = 'CL1_PDOWN_ARMED' in result['uart']
        if not result['firmware_command_armed']:
            raise RuntimeError('sample did not acknowledge destructive shell command')
        result['post_command_power_registers'] = []
        for cpu in (cpus if args.ppu_access == 'resource' else []):
            try:
                result['post_command_power_registers'].append({
                    'pc': cpu.get_pc(),
                    'pwrdn': cpu.read_register('IMP_CPUPWRCTLR_EL1')})
            except Exception as exc:
                result['post_command_power_registers'].append({'error': str(exc)})
        # No requirement to read powered-off CPU registers: dynamic OFF can
        # already have occurred after actual firmware PWRDN/WFI.
        snapshot('firmware_pwrdown')
        if args.ppu_access == 'scp-call':
            result['redistributors'] = []
            for i in range(4):
                base = 0x30060000 + i * 0x20000
                affinity = read(base + 12)
                waker = read(base + 0x14)
                pwrr = read(base + 0x24)
                record = {'base': base, 'affinity': affinity,
                          'waker': waker, 'pwrr_before': pwrr}
                result['redistributors'].append(record)
                if affinity != 0x10000 + i * 0x100 or (waker & 6) != 6 or pwrr & 2:
                    raise RuntimeError('CL1 view-0 affinity/sleep/RDAG guard failed')
                scp_call(base, 0, redistributor=True)
                record['pwrr_after'] = read(base + 0x24)
                if not record['pwrr_after'] & 1:
                    raise RuntimeError('redistributor RDPD did not acknowledge')
        for name, base in bases[1:]:
            policy(name, base, 0)
        deadline = time.monotonic() + 12
        while True:
            states = snapshot('cores_off')
            if all((states[f'core{i}'] & 0x10f) == 0 for i in range(4)):
                result['cores_off'] = True
                break
            if time.monotonic() >= deadline:
                raise TimeoutError('firmware PWRDN + PPU request did not reach core OFF')
            advance()
        policy(*bases[0], 0)
        deadline = time.monotonic() + 12
        while (snapshot('cluster_off')['cluster'] & 0x10f) != 0:
            if time.monotonic() >= deadline:
                raise TimeoutError('cluster OFF timeout')
            advance()
        result['cluster_off'] = True
        result['status'] = 'PASS'
        result['scope'] = 'firmware PWRDN/WFI plus observed core/cluster OFF only'
        # Leave the sacrificial cluster OFF for the caller to inspect. A fresh
        # image is required for any subsequent context-resume implementation.
    except Exception as exc:
        result['error'] = repr(exc)
    finally:
        signal.alarm(0)
        if model:
            try:
                model.stop(timeout=10)
                result['final_cpu_state'] = []
                for cpu in (cpus if result['status'] != 'PASS' else []):
                    values = {}
                    for register in ('PC', 'IMP_CPUPWRCTLR_EL1', 'ESR_EL1',
                                     'ELR_EL1', 'ESR_EL2', 'ELR_EL2',
                                     'CPSR', 'CNTHCTL_EL2', 'CNTV_CTL_EL0'):
                        try:
                            values[register] = cpu.read_register(register)
                        except Exception as exc:
                            values[register] = {'error': str(exc)}
                    result['final_cpu_state'].append(values)
                if cl0:
                    symbols = subprocess.check_output(['nm', str(args.elf)], text=True)
                    for line in symbols.splitlines():
                        parts = line.split()
                        if len(parts) == 3 and parts[2] in (
                                'cl1_gic_waker', 'cl1_gic_sleep_state', 'cl1_gic_ctlr',
                                'cl1_gic_enabled_before', 'cl1_gic_enabled_after',
                                'cl1_gic_pending_before', 'cl1_gic_pending_after'):
                            address = int(parts[0], 16)
                            raw = bytes(cl0.read_memory(address, memory_space=PHYSICAL,
                                                        size=4, count=4))
                            result[parts[2]] = [int.from_bytes(raw[i:i+4], 'little')
                                               for i in range(0, 16, 4)]
                        if len(parts) == 3 and parts[2] == 'cl1_powerdown_ready_mask':
                            address = int(parts[0], 16)
                            result['ready_mask_address'] = address
                            try:
                                result['ready_mask'] = int.from_bytes(cl0.read_memory(
                                    address, memory_space=PHYSICAL, size=8, count=1), 'little')
                            except Exception as exc:
                                result['ready_mask_read_error'] = str(exc)
                for cpu, bp in breakpoints:
                    cpu.remove_bpt(bp)
                if cl0 is not None and cl0_enabled is not None:
                    cl0.set_execution_state(cl0_enabled)
                result['model_left_paused'] = True
            except Exception as exc:
                result['cleanup_error'] = repr(exc)
            try:
                model.release()
            except Exception as exc:
                result['disconnect_error'] = repr(exc)
        if uart:
            uart.close()
        if cl0_uart:
            cl0_uart.close()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, default=str) + '\n')
    print(json.dumps(result, indent=2, default=str))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
