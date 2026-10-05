"""Dashboard launch resolution, FIFO ownership, and bounded child teardown."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest

from test_run_qbox_yocto_sh import (
    ROOT, SCRIPT, QBOX_YOCTO_ENV_OVERRIDES, create_qboxconf,
    create_yocto_tree, touch_file,
)

sys.path.insert(0, str(ROOT / 'scripts/run'))
import qbox_board_session as session


def fixture_env(tmp_path, bsp):
    build, deploy, *_ = create_yocto_tree(tmp_path, machine='apollo-qvp')
    name = 'nexios-bsp-initramfs' if bsp else 'nexios-image'
    create_qboxconf(build, deploy, basename=name)
    touch_file(deploy / f'{name}-apollo-qvp.wic')
    env = os.environ.copy()
    for key in (*QBOX_YOCTO_ENV_OVERRIDES, 'QBOX_APOLLO_VMCU_UART_ENDPOINT'):
        env.pop(key, None)
    env.update(MACHINE='apollo-qvp', YOCTO_BUILD_DIR=str(build),
               OUT_DIR=str(tmp_path / 'out'), SSH_PORT='24988',
               QBOX_RUNTIME_INJECTION_RUN_TOKEN='never-persist-this')
    return env


@pytest.mark.parametrize('options,bsp,vmcu,silkit,interval', [
    ([], False, False, False, None),
    (['--bsp', '--stats'], True, True, False, 5),
    (['--bsp', '--sil-kit', '--stats-interval', '2.5'], True, True, True, 2.5),
    (['--bsp', '--no-vmcu'], True, False, False, None),
])
def test_dashboard_dry_run_resolves_headless_spec_without_files(tmp_path, options, bsp, vmcu, silkit, interval):
    result = subprocess.run([str(SCRIPT), '--dashboard', '--dry-run', *options],
                            cwd=ROOT, env=fixture_env(tmp_path, bsp),
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    payload = result.stdout.split('Dashboard resolved launch specification (no bind/boot/files):\n')[1]
    spec = json.JSONDecoder().raw_decode(payload)[0]
    assert spec['bsp'] == bsp and spec['vmcu'] == vmcu and spec['silkit'] == silkit
    assert spec['stats_interval'] == interval
    assert spec['command'][1].endswith('run_qbox_apollo_fvp_full.py')
    for flag in ('--monitor', '--foreground-runtime', '--keep-running-after-pass', '--no-post-login-probe'):
        assert flag in spec['command']
    assert spec['command'][spec['command'].index('--timeout') + 1] == '0'
    assert 'headless:      1' in result.stdout
    assert 'never-persist-this' not in result.stdout
    assert not (tmp_path / 'out').exists()


def test_dashboard_writes_private_spec_then_executes_server(tmp_path):
    env = fixture_env(tmp_path, False)
    shim = tmp_path / 'python-server-intercept'
    shim.write_text(
        f'#!{sys.executable}\n'
        'import json, os, sys\n'
        "if len(sys.argv) > 1 and sys.argv[1].endswith('/board_server.py'):\n"
        "    print('INTERCEPTED_SERVER=' + json.dumps(sys.argv[1:]))\n"
        'else:\n'
        f'    os.execv({sys.executable!r}, [{sys.executable!r}, *sys.argv[1:]])\n')
    shim.chmod(0o755)
    env['PYTHON'] = str(shim)
    result = subprocess.run(
        [str(SCRIPT), '--dashboard', '--stats', '--dashboard-listen', '127.0.0.1',
         '--dashboard-port', '28765'],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    path = tmp_path / 'out/dashboard-launch-spec.json'
    spec = json.loads(path.read_text())
    assert path.stat().st_mode & 0o777 == 0o600
    assert path.parent.stat().st_mode & 0o777 == 0o700
    assert spec['stats_interval'] == 5 and not spec['bsp']
    assert spec['command'][1].endswith('/run_qbox_apollo_fvp_full.py')
    assert 'never-persist-this' not in path.read_text()
    server_args = json.loads(result.stdout.split('INTERCEPTED_SERVER=')[1])
    assert server_args[server_args.index('--launch-spec') + 1] == str(path)
    assert server_args[server_args.index('--port') + 1] == '28765'
    assert not (tmp_path / 'out/board-session.json').exists()


@pytest.mark.parametrize('options,message', [
    (['--timeout', '1'], 'boot-timeout'),
    (['--debug', 'linux'], 'conflicts'),
    (['--exit-after-pass'], 'persistent'),
    (['--dashboard-port', '0'], 'range'),
    (['--dashboard-boot-timeout', 'nan'], 'finite positive'),
    (['--', '--tmux-layout', 'default'], 'conflicts'),
])
def test_dashboard_rejects_conflicts_before_side_effects(options, message):
    result = subprocess.run([str(SCRIPT), '--dashboard', '--dry-run', *options],
                            cwd=ROOT, capture_output=True, text=True, timeout=10)
    assert result.returncode != 0 and message in result.stderr
    assert 'Stopping' not in result.stdout


def test_profile_owns_its_fifos(tmp_path):
    env = {name: '/another-run/' + filename for name, filename in session.UART_INPUTS.items()}
    assert session.prepare_inputs(tmp_path, env, ['runner', '--validation-profile', 'example']) == []
    assert not env and not list(tmp_path.iterdir())


def test_regular_session_fifo_lifetime_and_conflict(tmp_path):
    env = {}
    handles = session.prepare_inputs(tmp_path, env, ['runner'])
    try:
        assert len(handles) == 5
        for variable, filename in session.UART_INPUTS.items():
            assert env[variable] == str(tmp_path / filename)
            assert (tmp_path / filename).is_fifo()
        with pytest.raises(FileExistsError):
            session.prepare_inputs(tmp_path, {}, ['runner'])
    finally:
        for fd in handles:
            os.close(fd)


def test_session_terminates_owned_child_and_leaves_unrelated_process(tmp_path):
    output = tmp_path / 'run'
    spec_path = tmp_path / 'spec.json'
    spec_path.write_text(json.dumps({'command': [sys.executable, '-c',
        "import time; print('ready', flush=True); time.sleep(90)"],
        'cwd': str(ROOT), 'vmcu': False, 'env': {}}))
    unrelated = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(90)'])
    proc = subprocess.Popen([sys.executable, str(ROOT / 'scripts/run/qbox_board_session.py'),
                             '--launch-spec', str(spec_path), '--out-dir', str(output),
                             '--run-id', 'owned-run'])
    try:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if (output / 'board-runner.log').exists() and 'ready' in (output / 'board-runner.log').read_text():
                break
            time.sleep(.05)
        else:
            pytest.fail('session child did not start')
        proc.send_signal(signal.SIGTERM)
        assert proc.wait(timeout=8) == 0
        state = json.loads((output / 'board-session.json').read_text())
        assert state['run_id'] == 'owned-run' and state['status'] == 'STOPPED'
        assert state['cleanup']['status'] == 'PASS'
        assert not state['cleanup']['residual_pids']
        assert unrelated.poll() is None
        assert not Path(f"/proc/{state['child_pid']}").exists()
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
        unrelated.terminate()
        unrelated.wait()


def test_profile_cancel_interrupts_owned_runtime_for_final_result(tmp_path):
    output = tmp_path / 'run'
    spec_path = tmp_path / 'spec.json'
    code = """
import json, os, signal, sys, time
from pathlib import Path
out = Path(sys.argv[sys.argv.index('--out-dir') + 1])
ticks = Path(f'/proc/{os.getpid()}/stat').read_text().rsplit(')', 1)[1].split()[19]
(out / 'board-launch.json').write_text(json.dumps({
    'run_id': os.environ['QBOX_DASHBOARD_RUN_ID'], 'runtime_pid': os.getpid(),
    'runtime_start_ticks': ticks}))
def interrupted(*unused):
    (out / 'profile-result.json').write_text('interrupted; cleanup complete')
    sys.exit(0)
signal.signal(signal.SIGINT, interrupted)
print('profile-ready', flush=True)
time.sleep(90)
"""
    spec_path.write_text(json.dumps({'command': [sys.executable, '-c', code,
                                                '--validation-profile', 'fixture'],
                                     'cwd': str(ROOT), 'vmcu': False, 'env': {}}))
    proc = subprocess.Popen([sys.executable, str(ROOT / 'scripts/run/qbox_board_session.py'),
                             '--launch-spec', str(spec_path), '--out-dir', str(output),
                             '--run-id', 'profile-cancel'])
    try:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if (output / 'board-runner.log').exists() and 'profile-ready' in (output / 'board-runner.log').read_text():
                break
            time.sleep(.05)
        else:
            pytest.fail('profile child did not start')
        proc.terminate()
        assert proc.wait(timeout=8) == 0
        assert (output / 'profile-result.json').read_text() == 'interrupted; cleanup complete'
        state = json.loads((output / 'board-session.json').read_text())
        assert state['profile_interrupt']['status'] == 'SENT'
        assert state['profile_interrupt']['child_exited']
        assert state['cleanup']['status'] == 'PASS'
        assert not state['cleanup']['forced_signals']
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()


def test_profile_interrupt_rejects_foreign_or_reused_pid(tmp_path):
    from types import SimpleNamespace
    owner = SimpleNamespace(discover=lambda: None, owned={12: ('90', None)},
                            send=lambda *args: pytest.fail('foreign PID signalled'))
    path = tmp_path / 'board-launch.json'
    for launch, reason in [
        ({'run_id': 'previous', 'runtime_pid': 12, 'runtime_start_ticks': '90'}, 'runtime_not_owned'),
        ({'run_id': 'now', 'runtime_pid': 13, 'runtime_start_ticks': '90'}, 'runtime_not_owned'),
        ({'run_id': 'now', 'runtime_pid': 12, 'runtime_start_ticks': '91'}, 'runtime_identity_changed'),
    ]:
        path.write_text(json.dumps(launch))
        assert session.interrupt_profile(owner, tmp_path, 'now')['reason'] == reason
