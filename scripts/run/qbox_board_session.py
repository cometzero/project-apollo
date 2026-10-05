#!/usr/bin/env python3
"""Own one foreground Yocto board run, including its optional TC397 companion.

Only a trusted, local launcher creates the specification. This is not a web
command endpoint. Every run uses a fresh directory and tracked process identity.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

from qbox_tc397 import OwnedProcesses, identity, write_json


UART_INPUTS = {
    'QBOX_RDASPEN_UART_READ_FILE': 'rse-uart-input.fifo',
    'QBOX_APOLLO_FULL_SI_CL0_UART_READ_FILE': 'si-cl0-uart-input.fifo',
    'QBOX_APOLLO_FULL_SI_CL1_UART_READ_FILE': 'si-cl1-uart-input.fifo',
    'QBOX_RDASPEN_SECURE_UART_READ_FILE': 'secure-uart-input.fifo',
    'QBOX_RDASPEN_PRIMARY_UART_READ_FILE': 'primary-uart-input.fifo',
}


def replace_option(command, option, value):
    """Replace every form, so a trailing override cannot escape the run dir."""
    result, index = [], 0
    while index < len(command):
        arg = command[index]
        if arg == option:
            if index + 1 == len(command):
                raise ValueError(f'{option} requires a value')
            index += 2
        elif arg.startswith(option + '='):
            index += 1
        else:
            result.append(arg)
            index += 1
    return [*result, option, str(value)]


def child_command(spec, output):
    command = replace_option(spec['command'], '--out-dir', output)
    if not spec.get('vmcu'):
        return command
    wrapper = [sys.executable, str(Path(__file__).with_name('qbox_tc397.py')),
               '--qemu', spec['tc397_qemu'], '--firmware', spec['tc397_firmware'],
               '--out-dir', str(output)]
    if spec.get('silkit'):
        wrapper.append('--sil-kit')
        if spec.get('silkit_registry'):
            wrapper += ['--sil-kit-registry', spec['silkit_registry']]
        if spec.get('silkit_allow_actuation'):
            wrapper.append('--sil-kit-allow-actuation')
        if spec.get('silkit_echo_fixture'):
            wrapper.append('--sil-kit-echo-fixture')
    return [*wrapper, '--', *command]


def prepare_inputs(output, env, command):
    """Keep FIFOs open even without tmux; profile transports own their pipes."""
    if any(arg == '--validation-profile' or arg.startswith('--validation-profile=')
           for arg in command):
        # A fresh profile must not inherit another run's interactive inputs.
        for variable in UART_INPUTS:
            env.pop(variable, None)
        return []
    handles = []
    try:
        for variable, filename in UART_INPUTS.items():
            path = output / filename
            # Never unlink a previous run's FIFO or an unrelated file.
            os.mkfifo(path, 0o600)
            handles.append(os.open(path, os.O_RDWR | os.O_NONBLOCK))
            env[variable] = str(path)
    except Exception:
        for fd in handles:
            os.close(fd)
        raise
    return handles


def run_session(spec, output, run_id):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'board-session.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if (output / 'board-session.json').exists():
            raise ValueError('run directory already has board evidence; use a fresh run_id')
        return _run(spec, output, run_id)


def interrupt_profile(owner, output, run_id, timeout=8):
    """Let the finite runtime write its interrupted profile/cleanup result.

    Its outer canonical launcher has no TERM forwarding in finite mode. Signal
    only the identity-verified runtime through the already owned pidfd; never
    trust a PID from an old or unrelated board manifest.
    """
    try:
        launch = json.loads((output / 'board-launch.json').read_text())
        owner.discover()
        pid = launch.get('runtime_pid')
        if launch.get('run_id') != run_id or pid not in owner.owned:
            return {'status': 'SKIP', 'reason': 'runtime_not_owned'}
        start, _ = owner.owned[pid]
        if str(launch.get('runtime_start_ticks')) != str(start):
            return {'status': 'SKIP', 'reason': 'runtime_identity_changed'}
        owner.send(pid, signal.SIGINT)
        deadline = time.monotonic() + timeout
        while owner.process.poll() is None and time.monotonic() < deadline:
            owner.discover()
            time.sleep(.05)
        return {'status': 'SENT', 'pid': pid, 'signal': int(signal.SIGINT),
                'child_exited': owner.process.poll() is not None}
    except (OSError, ValueError, TypeError) as exc:
        return {'status': 'SKIP', 'reason': str(exc)}


def _run(spec, output, run_id):
    received_signal = 0

    def request_stop(signum, _frame):
        nonlocal received_signal
        received_signal = signum

    previous = {sig: signal.signal(sig, request_stop)
                for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)}
    started = time.monotonic()
    state = {'schema_version': 1, 'run_id': run_id, 'status': 'PREPARING',
             'supervisor_pid': os.getpid(), 'owner_uid': os.getuid(),
             'supervisor_start_ticks': identity(os.getpid())[1],
             'started_monotonic': started, 'cleanup': None}
    path = output / 'board-session.json'
    write_json(path, state)
    owner, descriptors = None, []
    code = 1
    try:
        env = os.environ.copy()
        env.update(spec.get('env', {}))
        env.update(QBOX_DASHBOARD_RUN_ID=run_id, QBOX_MANAGED_SESSION='1',
                   QBOX_SESSION_OWNER_UID=str(os.getuid()), QBOX_SESSION_OUT_DIR=str(output),
                   QBOX_APOLLO_MONITOR_BIND_ADDRESS='127.0.0.1')
        command = child_command(spec, output)
        descriptors = prepare_inputs(output, env, spec['command'])
        with tempfile.TemporaryDirectory(prefix='qbox-board-qmp-') as qmp_dir, \
                (output / 'board-runner.log').open('wb') as log:
            env['QBOX_APOLLO_QMP_DIR'] = qmp_dir
            if received_signal:
                raise InterruptedError('board startup interrupted')
            child = subprocess.Popen(command, cwd=spec['cwd'], env=env,
                                     stdin=subprocess.DEVNULL, stdout=log,
                                     stderr=subprocess.STDOUT, start_new_session=True)
            owner = OwnedProcesses(child)
            state.update(status='RUNNING', child_pid=child.pid,
                         child_start_ticks=identity(child.pid)[1], command=command)
            write_json(path, state)
            while child.poll() is None and not received_signal:
                owner.discover()
                state['owned_processes'] = [{'pid': pid, 'start_ticks': start}
                                            for pid, (start, _) in owner.owned.items()]
                state['observed_monotonic'] = time.monotonic()
                write_json(path, state)
                time.sleep(.25)
            state['status'] = 'STOPPING'
            write_json(path, state)
            if received_signal and any(arg == '--validation-profile' or arg.startswith('--validation-profile=')
                                       for arg in spec['command']):
                state['profile_interrupt'] = interrupt_profile(owner, output, run_id)
            state['cleanup'] = owner.stop(30)
            code = 0 if received_signal else child.returncode
            if state['cleanup']['status'] != 'PASS':
                code = 1
            state['status'] = 'STOPPED' if code == 0 else 'FAILED'
    except Exception as exc:
        state.update(status='FAILED', error=str(exc))
        print(f'Board session: {exc}', file=sys.stderr)
    finally:
        if owner is not None:
            if state['cleanup'] is None:
                state['cleanup'] = owner.stop(30)
            owner.close()
        for fd in descriptors:
            os.close(fd)
        state.update(returncode=code, signal=received_signal,
                     stopped_monotonic=time.monotonic())
        write_json(path, state)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    return code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--launch-spec', type=Path, required=True)
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args(argv)
    spec = json.loads(args.launch_spec.read_text())
    if not isinstance(spec.get('command'), list) or not spec['command']:
        parser.error('launch specification requires command argv')
    return run_session(spec, args.out_dir, args.run_id)


if __name__ == '__main__':
    raise SystemExit(main())
