#!/usr/bin/env python3
"""Exercise real TC397 CAN/SIL Kit and SI-controlled AP services on Apollo BSP."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import struct
import subprocess
import time
from verify_qbox_zephyr_vmcu import ROOT, TMUX_RUNNER, read, wait_for, validate_boot_result


def fifo(path, command):
    fd = os.open(path, os.O_WRONLY | os.O_NONBLOCK)
    try:
        os.write(fd, (command + "\n").encode())
    finally:
        os.close(fd)


def events(path):
    result = []
    for line in path.read_text().splitlines() if path.exists() else []:
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return result


def event_wait(path, predicate, offset=0, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for item in events(path)[offset:]:
            if predicate(item):
                return item
        time.sleep(.1)
    raise TimeoutError(f"Missing CAN event in {path}")


def qmp(path, command):
    with socket.socket(socket.AF_UNIX) as sock:
        sock.settimeout(5)
        sock.connect(str(path))
        stream = sock.makefile("rwb", buffering=0)
        assert "QMP" in json.loads(stream.readline())
        for cmd in ("qmp_capabilities", command):
            stream.write(json.dumps({"execute": cmd}).encode() + b"\n")
            while True:
                reply = json.loads(stream.readline())
                if "error" in reply:
                    raise RuntimeError(reply)
                if "return" in reply:
                    break


def processes(parent):
    table = {}
    for path in Path('/proc').iterdir():
        if not path.name.isdecimal():
            continue
        try:
            fields = (path / 'stat').read_text().rsplit(')', 1)[1].split()
            table[int(path.name)] = (int(fields[1]), fields[19], (path / 'exe').resolve().name)
        except OSError:
            continue
    children = {parent}
    while True:
        found = {pid for pid, (ppid, _, _) in table.items() if ppid in children}
        if found <= children:
            break
        children |= found
    return {pid: table[pid][1:] for pid in children if pid in table and table[pid][2] == 'platforms-vp'}


def execute(args, result):
    out = args.out_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    session = f"apollo-qbox-vmcu-services-{os.getpid()}"
    command = [str(ROOT / 'run_qbox_yocto.sh'), '--bsp', '--sil-kit',
               '--sil-kit-allow-actuation', '--sil-kit-echo-fixture', '--no-attach',
               '--multi-session', '--copy-disks', '--no-persistent-rse-state',
               '--session', session, '--out-dir', str(out), '--timeout', str(args.timeout)]
    checks = result['checks']
    result.update(command=command, session=session)
    uart, primary = out / 'tc397-uart.log', out / 'qbox-primary-console.log'
    vehicle = out / 'vehicle-can.jsonl'
    env = dict(os.environ, LINES='60', COLUMNS='180')
    for name in ('UART', 'SAFETY', 'GPIO'):
        env.pop(f'QBOX_APOLLO_VMCU_{name}_ENDPOINT', None)
    with (out / 'launcher.log').open('w') as log:
        try:
            subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                           timeout=60, check=True)
            wait_for(uart, 'VMCU_CAN_INIT result=PASS', timeout=40)
            wait_for(primary, 'NEXIOS_BSP_INITRAMFS_READY', timeout=120)
            wait_for(uart, r'VMCU_STATE source=SI0_PFDI state=RUN fault=NONE[^\n]*\n', timeout=60)
            status = json.loads((out / 'tc397-status.json').read_text())
            initial = processes(status['qbox_pid'])
            assert initial, 'No managed QBox runtime process found'
            result['runtime_processes'] = initial
            checks['boot-and-real-can-init'] = 'PASS'

            def cli(command, pattern, timeout=15):
                offset = len(read(uart))
                fifo(out / 'tc397-uart-input.fifo', 'vmcu-cli ' + command)
                line = wait_for(uart, pattern + r'[^\n]*\n', offset, timeout)
                checks['cli:' + command] = line.strip()
                return line

            def rpc(command, op, value=None):
                pattern = rf'VMCU_RPC peer=(SI0|AP) operation={op}[^\n]*result=OK'
                if value is not None:
                    pattern += rf' value=0x{value:08x}'
                return cli(command, pattern)

            def telemetry(predicate=lambda data: True, offset=0, timeout=15):
                return event_wait(vehicle, lambda e: e.get('event') == 'silkit_rx' and
                                  e.get('id') == 0x510 and predicate(bytes.fromhex(e['data'])),
                                  offset, timeout)

            def vehicle_command(op, arg=0):
                offset = len(events(vehicle))
                fifo(out / 'vehicle-can.in', f'command {op} {arg}')
                sent = event_wait(vehicle, lambda e: e.get('event') == 'silkit_tx' and
                                  e.get('id') == 0x600 and len(bytes.fromhex(e['data'])) == 24 and
                                  bytes.fromhex(e['data'])[1] == op and
                                  struct.unpack_from('<I', bytes.fromhex(e['data']), 16)[0] == arg,
                                  offset)
                request = bytes.fromhex(sent['data'])
                item = event_wait(vehicle, lambda e: e.get('event') == 'silkit_rx' and
                                  e.get('id') == 0x601 and len(bytes.fromhex(e['data'])) == 24 and
                                  bytes.fromhex(e['data'])[:2] == request[:2] and
                                  bytes.fromhex(e['data'])[4:16] == request[4:16],
                                  offset)
                payload = bytes.fromhex(item['data'])
                assert payload[2] == 0, item
                checks.setdefault('vehicle-commands', []).append(item)
                return struct.unpack_from('<I', payload, 16)[0]

            tele = telemetry(lambda b: b[1] == 2 and struct.unpack_from('<I', b, 8)[0] != 0)
            original_epoch, original_cookie = struct.unpack_from('<II', bytes.fromhex(tele['data']), 4)
            rpc('apollo ping', 1)
            rpc('safety ping', 1)
            cli('can trace on', 'VMCU_CAN_TRACE on')
            for ident, response_id, flags, payload in (
                    (0x123, 0x321, 0, bytes(range(8))),
                    (0x1abcde, 0x1abcdf, 13, bytes(range(64)))):
                offset = len(read(uart))
                cli(f'can send {ident:#x} {flags} {payload.hex()}', 'VMCU_CAN_SEND[^\n]*errno=0')
                wait_for(uart, rf'VMCU_CAN_RX id={response_id:#x} flags={flags:#x}[^\n]*data={payload.hex()}', offset)
            cli('can status', r'VMCU_CAN_STATUS state=0 rx=[1-9][0-9]* tx=[1-9][0-9]* tx_errors=0 rx_drops=0')
            checks['classic-extended-FD64-real-driver-IRQ-roundtrip'] = 'PASS'
            cli('can trace off', 'VMCU_CAN_TRACE off')
            assert vehicle_command(1) == 2
            vehicle_command(2)
            rails = [vehicle_command(3, rail) for rail in range(9)]
            assert all(value & 0x80000000 and value & 0x7fffffff for value in rails), rails
            faults = [vehicle_command(4, index) for index in range(11)]
            assert all(value <= 255 for value in faults)
            checks['pmic-programmed-rail-readback'] = rails
            checks['pmic-live-status-bytes'] = faults
            si = read(out / 'qbox-safety-island-cl0.log')
            assert 'policy=preserve' in si and 'probe=PASS' in si, si[-3000:]

            # Reset only the MCU: SI epoch and AP process stay alive, RPC cursors persist.
            before = len(events(vehicle))
            qmp_option = status['qemu_command'][status['qemu_command'].index('-qmp') + 1]
            mark = len(read(uart))
            qmp(qmp_option.split('unix:', 1)[1].split(',', 1)[0], 'system_reset')
            wait_for(uart, 'VMCU_INIT result=PASS', mark, timeout=20)
            tele = telemetry(lambda b: b[1] == 2 and struct.unpack_from('<I', b, 8)[0]
                             not in (0, original_cookie), before, timeout=25)
            epoch, cookie = struct.unpack_from('<II', bytes.fromhex(tele['data']), 4)
            assert epoch == original_epoch and cookie != original_cookie
            rpc('apollo ping', 1)
            rpc('safety ping', 1)
            vehicle_command(2)
            checks['mcu-reset-session-repair'] = {'epoch': epoch, 'before': original_cookie, 'after': cookie}

            if args.inject_pfdi_timeout:
                mark = len(read(uart))
                can_mark = len(events(vehicle))
                ap_mark = len(read(primary))
                fifo(out / 'primary-uart-input.fifo',
                     'kill -STOP $(pidof pfdi-sample-app); echo VMCU_PFDI_STOPPED')
                wait_for(primary, r'\nVMCU_PFDI_STOPPED', ap_mark, timeout=10)
                result['injected_pfdi_timeout'] = True
                wait_for(uart, 'state=DEGRADED fault=PFDI_FAULT', mark, timeout=80)
                fault_telemetry = telemetry(lambda b: b[1] == 4 and b[2] == 2 and
                                           struct.unpack_from('<H', b, 20)[0] != 0,
                                           can_mark, timeout=15)
                checks['real-PFDI-fault-through-CAN'] = fault_telemetry

            # A commanded AP reset uses the existing RSE reload path; it must re-enter Linux/PFDI.
            boot_before = len(read(primary))
            mcu_before = len(read(uart))
            vehicle_command(5)
            wait_for(primary, 'NEXIOS_BSP_INITRAMFS_READY', boot_before, timeout=100)
            wait_for(uart, r'VMCU_STATE source=SI0_PFDI state=RUN fault=NONE', mcu_before, timeout=45)
            rpc('recover status', 11, 5)
            rpc('apollo ping', 1)
            checks['AP-recovery-RSE-reload-Linux-PFDI'] = 'PASS'

            for cycle in range(args.power_cycles):
                si_before = len(read(out / 'qbox-safety-island-cl0.log'))
                mcu_before = len(read(uart))
                can_before = len(events(vehicle))
                vehicle_command(6)
                wait_for(out / 'qbox-safety-island-cl0.log', 'AP cores OFF verified', si_before, timeout=20)
                rpc('power status', 13, 3)
                cli('gpio status', r'VMCU_GPIO[^\n]*SOC_PWR_REQ=1 IST_DONE_N=0 SOC_RESET_N=1 MCU_SOC_WAKE=0')
                wait_for(uart, 'VMCU_STATE source=SI0_PFDI state=OFF fault=NONE', mcu_before, timeout=15)
                rpc('safety ping', 1)
                # State and MCU timer must continue while AP cores remain off.
                tele_off = telemetry(lambda b: b[1] == 3, offset=can_before, timeout=15)
                time.sleep(5.5)
                rpc('power status', 13, 3)
                boot_before = len(read(primary))
                mcu_before = len(read(uart))
                vehicle_command(7)
                wait_for(primary, 'NEXIOS_BSP_INITRAMFS_READY', boot_before, timeout=100)
                wait_for(uart, 'VMCU_STATE source=SI0_PFDI state=RUN fault=NONE', mcu_before, timeout=45)
                rpc('power status', 13, 0)
                rpc('apollo ping', 1)
                checks[f'graceful-AP-off-wake-cycle-{cycle + 1}'] = {'status': 'PASS', 'off_telemetry': tele_off}
            assert processes(status['qbox_pid']) == initial, 'QBox process restarted'
            assert json.loads((out / 'tc397-status.json').read_text())['tc397_pid'] == status['tc397_pid']
            checks['same-QBox-and-MCU-processes'] = 'PASS'
            faults_seen = set(re.findall(r'state=DEGRADED fault=(\w+)', read(uart)))
            expected_faults = {'PFDI_FAULT'} if args.inject_pfdi_timeout else set()
            assert faults_seen == expected_faults, f'Unexpected safety faults: {faults_seen}'
            checks['no-spurious-safety-faults-during-control'] = 'PASS'
            result['status'] = 'PASS'
        finally:
            cleanup = subprocess.run([str(TMUX_RUNNER), '--stop-session', session], cwd=ROOT,
                                     env=dict(os.environ, OUT_DIR=str(out)), stdout=log,
                                     stderr=subprocess.STDOUT, timeout=45)
            result['stop_returncode'] = cleanup.returncode
            status_path = out / 'tc397-status.json'
            if status_path.exists():
                result['companion'] = json.loads(status_path.read_text())
                receipts = result['companion'].get('cleanup', [])
                if not receipts or any(item['status'] != 'PASS' for item in receipts):
                    raise RuntimeError('Managed process cleanup incomplete')
            if cleanup.returncode:
                raise RuntimeError('tmux cleanup failed')
            if result['status'] == 'PASS':
                result['boot'] = json.loads((out / 'result.json').read_text())
                validate_boot_result(result['boot'], result.get('injected_pfdi_timeout', False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=600)
    parser.add_argument('--power-cycles', type=int, default=2)
    parser.add_argument('--inject-pfdi-timeout', action='store_true',
                        help='Stop the real AP PFDI agent, verify CAN fault, then recover AP')
    args = parser.parse_args()
    if args.out_dir.exists() or args.timeout < 1 or not 1 <= args.power_cycles <= 3:
        parser.error('new output directory, positive timeout and 1..3 power cycles required')
    result = {'status': 'FAIL', 'checks': {}, 'unsupported': [
        'PMIC rail gating / PGOOD sequencing', 'SC7/full SoC cold poweroff',
        'CAN bit timing/arbitration/transceiver/physical ACK', 'deterministic cross-process FTTI']}
    start = time.monotonic()
    try:
        execute(args, result)
    except (OSError, ValueError, AssertionError, RuntimeError, subprocess.SubprocessError) as error:
        result.update(status='FAIL', error=str(error))
    result['elapsed_s'] = time.monotonic() - start
    args.out_dir.mkdir(parents=True, exist_ok=True)
    result['source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (args.out_dir / 'vmcu-services-result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'error': result.get('error'), 'out_dir': str(args.out_dir)}))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
