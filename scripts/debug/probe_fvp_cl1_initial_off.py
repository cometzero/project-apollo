#!/usr/bin/env python3
"""Bounded read-only PPU sampler for opt-in CL1 initial-OFF isolation.

Never gates individual CPUs or writes power state. Global debug pauses perturb
timing; sampled OFF does not prove continuous OFF or AP context restoration.
The caller owns launch, guest suspend stimulus, and model shutdown.
"""
import argparse
import json
import hashlib
import subprocess
from pathlib import Path
import sys
import time


def ppu_state(sample, name):
    value = sample['ppu'].get(name, {}).get('pwsr')
    return None if value is None else value & 0xf


class ComputeCycle:
    """Require a booted CPU before accepting all physical compute PPUs OFF."""
    def __init__(self):
        self.boot_seen = False
        self.off_seen = False
        self.resumed = False

    def observe(self, sample):
        if not sample.get('qualified'):
            return None
        sys_on = ppu_state(sample, 'ap_sys0') == 8
        core_on = ppu_state(sample, 'ap_core0_0') == 8
        if sys_on and core_on:
            if self.off_seen:
                self.resumed = True
                return 'after'
            self.boot_seen = True
            return 'before'
        names = [f'ap_cluster{i}' for i in range(4)] + [
            f'ap_core{i}_{j}' for i in range(4) for j in range(4)]
        if self.boot_seen and sys_on and all(ppu_state(sample, n) == 0 for n in names):
            self.off_seen = True
            return 'compute_off'
        return None


def multiview_snapshot(cl0):
    """Read ownership via controller view0, not TF-A's AP view1 alias.

    Apollo si0_mmap.h and gicx00_multiview_reg.h: SPI32..991 ownership
    occupies IVIEWR[2..61]; VIEWR assigns each physical redistributor.
    No acknowledge, EOI, pending-clear, or other side-effect register reads.
    """
    controllers = {'ap': (0xd0770000, 0x80000, 0x40000, 16),
                   'si': (0x30000000, 0x40000, 0x20000, 5)}
    snapshot = {}
    for name, (base, rd_offset, stride, count) in controllers.items():
        registers = {}
        addresses = [('cfgid', base+0xf000, 8), ('ctlr_view0', base, 4)]
        view_stride = 0x800000 if name == 'ap' else 0x100000
        addresses += [(f'ctlr_view{i}', base+i*view_stride, 4) for i in range(1, 4)]
        addresses += [(f'iviewr{i}', base+0xf600+i*4, 4) for i in range(2, 62)]
        for i in range(count):
            rd = base+rd_offset+i*stride
            addresses += [(f'rd{i}_{reg}', rd+off, size) for reg, off, size in
                          [('typer', 8, 8), ('viewr', 0x2c, 4),
                           ('waker', 0x14, 4), ('pwrr', 0x24, 4)]]
        for reg, address, size in addresses:
            try:
                raw = cl0.read_memory(address, memory_space='Physical Memory (Secure)',
                                      size=size, count=1)
                registers[reg] = {'address': address, 'value': int.from_bytes(raw, 'little')}
            except Exception as exc:
                registers[reg] = {'address': address, 'error': str(exc)}
        ownership = {k: v['value'] for k, v in registers.items()
                     if (k.startswith('iviewr') or k.endswith('_viewr')) and 'value' in v}
        complete = len(ownership) == 60+count
        snapshot[name] = {'controller_cl0_base': base, 'registers': registers,
                          'ownership_complete': complete,
                          'ownership_sha256': hashlib.sha256(json.dumps(
                              ownership, sort_keys=True).encode()).hexdigest() if complete else None}
    return snapshot


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iris-python', type=Path, required=True)
    p.add_argument('--port', type=int, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--duration', type=float, default=120)
    p.add_argument('--interval', type=float, default=.5,
                   help='host seconds of simulation run between PPU observations')
    p.add_argument('--capture-ap-resume', action='store_true',
                   help='read AP registers only after observed SYS0 OFF then core ON')
    p.add_argument('--systop-on', action='store_true',
                   help='qualify compute OFF/ON with SYS0 retained ON instead')
    p.add_argument('--tfa-elf', type=Path,
                   help='matching TF-A BL31 ELF for provenance and PC symbolization')
    args = p.parse_args()
    if not 1 <= args.duration <= 500:
        p.error('duration must be 1..500 seconds')
    if not .01 <= args.interval <= 5:
        p.error('interval must be .01..5 seconds')
    if args.capture_ap_resume and (args.tfa_elf is None or not args.tfa_elf.is_file()):
        p.error('--capture-ap-resume requires matching --tfa-elf')
    sys.path.insert(0, str(args.iris_python))
    from iris.debug import Model
    result = {'status': 'NOT_TESTED', 'samples': [], 'individual_cpu_gating': False,
              'power_writes': False, 'context_resume_passed': False,
              'scope': 'sampled CL1 reset-OFF isolation, AP PPU observations only'}
    qualified = False
    last_memory_time = 0.0
    previous_sys0_state = None
    sys0_off_seen = False
    compute_cycle = ComputeCycle()
    last_mv_before = 0.0
    last_ap_capture = 0.0
    result['host_sample_interval_seconds'] = args.interval
    result['systop_on_mode'] = args.systop_on
    if args.tfa_elf:
        result['tfa_elf'] = str(args.tfa_elf.resolve())
        result['tfa_elf_sha256'] = hashlib.sha256(args.tfa_elf.read_bytes()).hexdigest()
    model = None
    try:
        model = Model.NewNetworkModel('localhost', args.port, timeoutInMs=10000,
                                      synchronous=False)
        call = model.client.irisCall()
        cl0 = model.get_target('component.RD_ASD.css.smb.si.cluster0.cpu0')
        bases = {'cl1_cluster': 0x28810000, 'ap_sys0': 0xd0021000}
        bases.update({f'cl1_core{i}': 0x28840000+i*0x100000 for i in range(4)})
        # Apollo CL0 ATW1 utility view, si0_mmap.h/config_ppu_v1.c.
        bases.update({f'ap_cluster{i}': 0xc1030000+i*0x4000000 for i in range(4)})
        bases.update({f'ap_core{i}_{j}': 0xc1080000+i*0x4000000+j*0x100000
                      for i in range(4) for j in range(4)})
        deadline = time.monotonic() + args.duration
        while time.monotonic() < deadline:
            call.simulationTime_stop(instId=1)
            stop_deadline = time.monotonic() + 10
            while call.simulationTime_get(instId=1)['running']:
                if time.monotonic() > stop_deadline:
                    raise TimeoutError('simulation stop timeout')
                time.sleep(.01)
            sample = {'time': call.simulationTime_get(instId=1), 'ppu': {}}
            for name, base in bases.items():
                try:
                    sample['ppu'][name] = {'base': base, **{
                        reg: int.from_bytes(cl0.read_memory(base+offset,
                            memory_space='Physical Memory (Secure)', size=4, count=1), 'little')
                        for reg, offset in [('pwpr', 0), ('pwsr', 8)]}}
                except Exception as exc:
                    sample['ppu'][name] = {'error': str(exc)}
            result['samples'].append(sample)
            cl1 = [v for k, v in sample['ppu'].items() if k.startswith('cl1_')]
            if not qualified and all('pwsr' in v for v in cl1) and (
                    sample['ppu']['ap_sys0'].get('pwsr', 0) & 0xf) == 8:
                qualified = True
                result['qualified_from_ticks'] = sample['time']['ticks']
            sample['qualified'] = qualified
            phase = compute_cycle.observe(sample) if args.systop_on else None
            if phase:
                sample['compute_phase'] = phase
                snapshots = result.setdefault('multiview_snapshots', {})
                if phase not in snapshots or (phase == 'before' and
                        time.monotonic()-last_mv_before >= 5):
                    snapshots[phase] = {'time': sample['time'],
                                        'controllers': multiview_snapshot(cl0)}
                    if phase == 'before':
                        last_mv_before = time.monotonic()
            # Secure AP peripheral SRAM mapped into the CL0 ATW memory view.
            # Hash observations alone are not retention proof: SYS0 must OFF.
            sys0_state = sample['ppu']['ap_sys0'].get('pwsr')
            if qualified and sys0_state is not None and (sys0_state & 0xf) == 0:
                sys0_off_seen = True
            captures = result.setdefault('ap_resume_register_samples', [])
            resume_seen = compute_cycle.resumed if args.systop_on else sys0_off_seen
            if (args.capture_ap_resume and resume_seen and sys0_state is not None
                    and (sys0_state & 0xf) == 8 and len(captures) < 3
                    and time.monotonic()-last_ap_capture >= 1
                    and (sample['ppu']['ap_core0_0'].get('pwsr', 0) & 0xf) == 8):
                registers = {'time': sample['time'], 'cores': {}}
                for i in range(4):
                    if (sample['ppu'][f'ap_core0_{i}'].get('pwsr', 0) & 0xf) != 8:
                        continue
                    cpu = model.get_target(f'component.RD_ASD.css.app00.cluster.cpu{i}')
                    values = {}
                    for name in ('PC', 'CPSR', 'ELR_EL3', 'ESR_EL3', 'FAR_EL3',
                                 'SPSR_EL3', 'VBAR_EL3', 'SCTLR_EL3', 'SCR_EL3',
                                 'ELR_EL2', 'ESR_EL2', 'ELR_EL1', 'ESR_EL1'):
                        try:
                            values[name] = cpu.read_register(name)
                        except Exception as exc:
                            values[name] = {'error': str(exc)}
                    if isinstance(values.get('PC'), int):
                        try:
                            symbol = subprocess.run(['gdb-multiarch', '-q', '-batch',
                                str(args.tfa_elf), '-ex', f"info line *{values['PC']:#x}",
                                '-ex', f"info symbol {values['PC']:#x}"],
                                capture_output=True, text=True, timeout=5)
                            values['tfa_pc_symbolization'] = symbol.stdout
                        except Exception as exc:
                            values['symbolization_error'] = str(exc)
                    registers['cores'][str(i)] = values
                captures.append(registers)
                last_ap_capture = time.monotonic()
                if args.systop_on:
                    result['multiview_snapshots']['after'] = {
                        'time': sample['time'], 'warm_capture_count': len(captures),
                        'controllers': multiview_snapshot(cl0)}
            sys0_transition = (sys0_state is not None and previous_sys0_state is not None
                               and (sys0_state & 0xf) != (previous_sys0_state & 0xf))
            previous_sys0_state = sys0_state
            if (sys0_state is not None and (sys0_state & 0xf) == 8 and
                    (not result.get('memory_samples') or sys0_transition or
                     time.monotonic()-last_memory_time >= 10)):
                memory = {'time': sample['time'], 'regions': {}}
                memory['sys0_transition'] = sys0_transition
                for name, offset, size in [('bl31', 0x4000, 0x2f000),
                                            ('mailbox', 0x1ff8, 8),
                                            ('bl2_entry', 0x82000, 64)]:
                    try:
                        data = bytearray()
                        for chunk in range(0, size, 4096):
                            data.extend(cl0.read_memory(0xe0030000+offset+chunk,
                                memory_space='Physical Memory (Secure)', size=1,
                                count=min(4096, size-chunk)))
                        memory['regions'][name] = {'cl0_address': 0xe0030000+offset,
                            'size': size, 'sha256': hashlib.sha256(data).hexdigest()}
                        if size <= 64:
                            memory['regions'][name]['bytes'] = data.hex()
                    except Exception as exc:
                        memory['regions'][name] = {'error': str(exc)}
                result.setdefault('memory_samples', []).append(memory)
                last_memory_time = time.monotonic()
            # SDK Model.run waits for an event that can be missed at startup.
            # Raw Iris request avoids that event-based false timeout.
            call.simulationTime_run(instId=1)
            time.sleep(min(args.interval, max(0, deadline-time.monotonic())))
        checked = [s for s in result['samples'] if s['qualified']]
        result['prequalification_samples'] = len(result['samples']) - len(checked)
        result['qualified_samples'] = len(checked)
        result['status'] = 'PASS' if checked and all(
            'pwsr' in v and (v['pwsr'] & 0xf) == 0
            for s in checked for k, v in s['ppu'].items() if k.startswith('cl1_')) else 'FAIL'
    except KeyboardInterrupt:
        result['status'] = 'INTERRUPTED'
        result['error'] = 'operator interrupted bounded observations'
    except Exception as exc:
        result['error'] = repr(exc)
        result['status'] = 'FAIL'
    finally:
        observed = [s for s in result['samples'] if s.get('qualified')]
        result['cl1_sampled_off'] = bool(observed) and all(
            'pwsr' in v and (v['pwsr'] & 0xf) == 0
            for s in observed for k, v in s['ppu'].items() if k.startswith('cl1_'))
        result['ap_sys0_off_sampled'] = any(
            (s['ppu']['ap_sys0'].get('pwsr', 15) & 0xf) == 0 for s in observed)
        result['retention_verdict'] = 'NOT_TESTED'
        if args.systop_on:
            result['ap_compute_off_sampled'] = compute_cycle.off_seen
            result['ap_compute_off_on_sampled'] = compute_cycle.resumed
            result['sys0_on_during_qualified_samples'] = bool(observed) and all(
                ppu_state(s, 'ap_sys0') == 8 for s in observed)
            snapshots = result.get('multiview_snapshots', {})
            result['multiview_save_restore_execution'] = 'NOT_TESTED'
            result['multiview_ownership_scope'] = (
                'Apollo SCP-supported SPI INTIDs 32..991 (IVIEWR[2..61]) and '
                '16 AP/5 SI redistributors; not all possible implemented interrupts')
            result['multiview_ownership_comparison'] = {}
            for name in ('ap', 'si'):
                hashes = [snapshots.get(phase, {}).get('controllers', {}).get(
                    name, {}).get('ownership_sha256') for phase in ('before', 'compute_off', 'after')]
                result['multiview_ownership_comparison'][name] = (
                    'NOT_TESTED' if None in hashes else
                    'UNCHANGED_SAMPLED' if len(set(hashes)) == 1 else 'CHANGED')
        if model:
            try:
                model.release()
                result['model_run_requested'] = True
            except Exception as exc:
                result['disconnect_error'] = str(exc)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'status': result['status'], 'samples': len(result['samples'])}))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
