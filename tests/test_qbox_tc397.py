"""TC397 companion shell transport and owned-process lifecycle regressions."""

import importlib.util
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run/qbox_tc397.py"
SPEC = importlib.util.spec_from_file_location("qbox_tc397", SCRIPT)
companion = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(companion)


@pytest.mark.parametrize("filename", ["disconnected:tcp:0.0.0.0:2345,server=on",
                                      "disconnected:tcp:127.0.0.1:0,server=on"])
def test_endpoint_rejects_non_loopback_or_unbound_port(filename):
    with pytest.raises(RuntimeError):
        companion.endpoint_from_chardev([{"label": "tc397_uart", "filename": filename}])


FAKE_QEMU = r'''#!/usr/bin/env python3
import json, os, socket, struct, sys, time, zlib
from pathlib import Path
args = sys.argv[1:]
config = json.loads(Path(args[args.index('-kernel') + 1]).read_text())
if config.get('startup_exit'):
    sys.exit(17)
if config.get('startup_hang'):
    time.sleep(60)
qmp_path = args[args.index('-qmp') + 1].split(',')[0].removeprefix('unix:')
options = [args[i+1] for i, arg in enumerate(args) if arg == '-chardev']
logfile = options[0].split('logfile=', 1)[1].split(',')[0]
assert 'logfile=' not in options[1]
has_can = any('id=tc397can,' in option for option in options)
console_path = options[1].split('path=', 1)[1].split(',')[0]
console_server = socket.socket(socket.AF_UNIX)
console_server.bind(console_path)
console_server.listen()
listeners = {}
for label in ('tc397_uart', 'tc397_safety', 'tc397gpio') + (('tc397can',) if has_can else ()):
    listener = socket.socket()
    listener.bind(('127.0.0.1', 0))
    listener.listen()
    listeners[label] = listener
qmp = socket.socket(socket.AF_UNIX)
qmp.bind(qmp_path)
qmp.listen()
client, _ = qmp.accept()
with client, client.makefile('rwb') as stream:
    stream.write(b'{"QMP":{}}\n')
    stream.flush()
    for _ in range(2):
        command = json.loads(stream.readline())['execute']
        reply = {}
        if command == 'query-chardev':
            reply = [{'label':label, 'filename':
                'disconnected:tcp:127.0.0.1:%d,server=on' % listener.getsockname()[1]}
                for label, listener in listeners.items()]
        stream.write(json.dumps({'return':reply}).encode() + b'\n')
        stream.flush()
assert '-S' in args
if '-S' in args:
    # The console must already be connected before CPU release.
    console_server.settimeout(.2)
    console, _ = console_server.accept()
    # SIL Kit additionally requires both participants' ready events.
    client, _ = qmp.accept()
    with client, client.makefile('rwb') as stream:
        stream.write(b'{"QMP":{}}\n')
        stream.flush()
        for _ in range(2):
            command = json.loads(stream.readline())['execute']
            if command == 'cont':
                for filename in (('tc397-can.jsonl', 'vehicle-can.jsonl') if has_can else ()):
                    path = Path(logfile).parent / filename
                    assert 'peer_running' in path.read_text()
                (Path(logfile).parent / 'qemu-resumed').write_text('yes')
            stream.write(b'{"return":{}}\n')
            stream.flush()
console.setblocking(False)
console.sendall(b'test shell ready\n')
started = time.monotonic()
with open(logfile, 'ab', buffering=0) as raw:
    while True:
        if config.get('crash_after') and time.monotonic() - started > config['crash_after']:
            sys.exit(19)
        head = struct.pack('<2sBBHBBIIII', b'\xa5\x5a', 1, 4, 28, 2, 0, 0, 1, 0, 100)
        raw.write(head + struct.pack('<I', zlib.crc32(head)))
        try:
            data = console.recv(4096)
            if data:
                console.sendall(b'test shell received: ' + data)
        except BlockingIOError:
            pass
        time.sleep(.05)
'''


@pytest.fixture
def launch(tmp_path):
    qemu = tmp_path / "fake-qemu"
    qemu.write_text(FAKE_QEMU)
    qemu.chmod(0o755)
    firmware = tmp_path / "firmware.json"
    output = tmp_path / "output"
    processes = []

    def start(command, config=None, env=None, options=()):
        firmware.write_text(json.dumps(config or {}))
        process = subprocess.Popen(
            [sys.executable, str(SCRIPT), "--qemu", str(qemu),
             "--firmware", str(firmware), "--out-dir", str(output),
             "--startup-timeout", "2", "--shutdown-timeout", ".2", *options, "--", *command],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        processes.append(process)
        return process, output

    yield start
    for process in processes:
        if process.poll() is None:
            process.terminate()
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()


def result(process, output, expected=0):
    stdout, stderr = process.communicate(timeout=8)
    assert process.returncode == expected, (stdout, stderr)
    value = json.loads((output / "tc397-status.json").read_text())
    assert value["cleanup"]
    assert all(receipt["status"] == "PASS" and not receipt["residual_pids"]
               for receipt in value["cleanup"])
    return value


def wait_file(path):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if path.exists() and path.stat().st_size:
            return
        time.sleep(.02)
    pytest.fail(f"file not written: {path}")


def test_normal_exit_preserves_environment_and_shell_log(launch, tmp_path):
    env = dict(os.environ, QBOX_MANAGED_SESSION="test-session",
               QBOX_SESSION_OWNER=str(os.getuid()))
    received = tmp_path / "env.json"
    code = ("import json,os,time;from pathlib import Path;"
            f"Path({str(received)!r}).write_text(json.dumps(dict(os.environ)));"
            "time.sleep(.2)")
    process, output = launch([sys.executable, "-c", code], env=env)
    value = result(process, output)
    child_env = json.loads(received.read_text())
    assert child_env["QBOX_MANAGED_SESSION"] == "test-session"
    assert child_env["QBOX_SESSION_OWNER"] == str(os.getuid())
    assert child_env["QBOX_APOLLO_VMCU_UART_ENDPOINT"] == value["uart_endpoint"]
    assert child_env["QBOX_APOLLO_VMCU_SAFETY_ENDPOINT"] == value["safety_endpoint"]
    assert child_env["QBOX_APOLLO_VMCU_GPIO_ENDPOINT"] == value["gpio_endpoint"]
    assert len({value[k] for k in ("uart_endpoint", "safety_endpoint", "gpio_endpoint")}) == 3
    assert value["console_output_bytes"] == (output / "tc397-uart.log").stat().st_size
    assert value["console_output_bytes"] > 0
    assert (output / "qemu-resumed").exists()
    text = (output / "tc397-uart.log").read_text()
    assert "test shell ready" in text
    assert "[host" not in text and "type=STATUS" not in text
    assert (output / "tc397-link-tx.bin").stat().st_size >= 28


def test_child_launch_failure_stops_mcu(launch):
    process, output = launch(["/no-such-tc397-test-runner"])
    value = result(process, output, 1)
    assert value["status"] == "FAILED"
    assert len(value["cleanup"]) == 1


def test_qemu_startup_failure_never_launches_child(launch, tmp_path):
    marker = tmp_path / "not-launched"
    process, output = launch(
        [sys.executable, "-c", f"open({str(marker)!r}, 'w').close()"],
        {"startup_exit": True})
    value = result(process, output, 1)
    assert "startup" in value["error"]
    assert not marker.exists()


def escaped_child(marker):
    return ("import subprocess,sys,time;from pathlib import Path;"
            "child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'],"
            "start_new_session=True);"
            f"Path({str(marker)!r}).write_text(str(child.pid));time.sleep(60)")


def assert_descendant_cleaned(value, marker):
    pid = int(marker.read_text())
    assert any(pid in entry["owned_pids"] for entry in value["cleanup"])
    state = companion.identity(pid)
    assert state is None or state[2] == "Z"


@pytest.mark.parametrize("signum", [signal.SIGINT, signal.SIGTERM, signal.SIGHUP])
def test_signals_stop_separate_session_descendant(launch, tmp_path, signum):
    marker = tmp_path / "descendant.pid"
    process, output = launch([sys.executable, "-c", escaped_child(marker)])
    wait_file(marker)
    process.send_signal(signum)
    value = result(process, output, 128 + signum)
    assert value["status"] == "INTERRUPTED"
    assert_descendant_cleaned(value, marker)


def test_mcu_crash_cleans_runner_without_touching_unrelated_process(launch, tmp_path):
    marker = tmp_path / "descendant.pid"
    unrelated = subprocess.Popen([sys.executable, "-c", "import time;time.sleep(60)"],
                                 start_new_session=True)
    try:
        process, output = launch([sys.executable, "-c", escaped_child(marker)],
                                 {"crash_after": .7})
        value = result(process, output, 1)
        # Socket EOF can be observed just before waitpid reports QEMU's exit.
        assert ("unexpectedly" in value["error"] or
                value["error"] == "TC397 shell UART disconnected")
        assert_descendant_cleaned(value, marker)
        assert unrelated.poll() is None
    finally:
        unrelated.terminate()
        unrelated.wait(timeout=5)


def test_console_fifo_round_trip(launch, tmp_path):
    fifo = tmp_path / "output/tc397-uart-input.fifo"
    code = ("import os,time;"
            f"fd=os.open({str(fifo)!r},os.O_WRONLY);"
            "os.write(fd,b'vmcu-cli status\\n');os.close(fd);time.sleep(.3)")
    process, output = launch([sys.executable, "-c", code])
    value = result(process, output)
    assert "test shell received: vmcu-cli status" in (output / "tc397-uart.log").read_text()
    assert value["console_input_bytes"] == len(b"vmcu-cli status\n")


def test_console_refuses_regular_file(launch, tmp_path):
    output = tmp_path / "output"
    output.mkdir()
    (output / "tc397-uart-input.fifo").write_text("keep me")
    marker = tmp_path / "not-launched"
    process, _ = launch([sys.executable, "-c", f"open({str(marker)!r}, 'w').close()"])
    value = result(process, output, 1)
    assert "must be a FIFO" in value["error"]
    assert not marker.exists()
    assert (output / "tc397-uart-input.fifo").read_text() == "keep me"


FAKE_SILKIT = r'''#!/usr/bin/env python3
import json, os, signal, sys, time
from pathlib import Path
args = sys.argv[1:]
signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
if '-g' in args:
    Path(args[args.index('-g') + 1]).write_text("Middleware:\n  RegistryUri: 'silkit://127.0.0.1:34567'\n")
    if os.environ.get('SILKIT_TEST_CRASH') == 'registry':
        time.sleep(.4)
        sys.exit(21)
else:
    role = args[args.index('--role') + 1]
    if os.environ.get('SILKIT_TEST_NO_READY') == role:
        time.sleep(10)
    path = Path(args[args.index('--events') + 1])
    path.write_text(''.join(json.dumps({'event': e}) + '\n'
                            for e in ('participant_ready', 'peer_running', 'controller_stopped')))
    if os.environ.get('SILKIT_TEST_CRASH') == role:
        time.sleep(.4)
        sys.exit(21)
    if role == 'restbus':
        import select
        while True:
            if select.select([sys.stdin], [], [], .1)[0]:
                line = os.read(0, 1024)
                if line:
                    with path.open('a') as f:
                        f.write(json.dumps({'event': 'input', 'data': line.decode()}) + '\n')
while True:
    time.sleep(.1)
'''


@pytest.fixture
def silkit_options(tmp_path):
    binary = tmp_path / 'fake-silkit'
    binary.write_text(FAKE_SILKIT)
    binary.chmod(0o755)
    return ['--sil-kit', '--sil-kit-binary', str(binary),
            '--sil-kit-registry-binary', str(binary)]


def test_silkit_ready_before_cpu_and_fifo_command(launch, silkit_options):
    process, output = launch([sys.executable, '-c', 'import time;time.sleep(1)'],
                             options=silkit_options)
    wait_file(output / 'qemu-resumed')
    with (output / 'vehicle-can.in').open('w') as fifo:
        fifo.write('status\n')
    value = result(process, output)
    kit = value['sil_kit']
    assert kit['status'] == 'READY'
    assert kit['external_registry'] is False
    assert kit['registry_uri'] == 'silkit://127.0.0.1:34567'
    assert len(value['cleanup']) == 5
    assert all(entry['returncode'] == 0 for entry in kit['processes'])
    assert 'status' in (output / 'vehicle-can.jsonl').read_text()
    assert '-S' in value['qemu_command']


@pytest.mark.parametrize('role', ['registry', 'bridge', 'restbus'])
def test_silkit_participant_failure_stops_all(launch, silkit_options, role):
    process, output = launch([sys.executable, '-c', 'import time;time.sleep(10)'],
                             options=silkit_options,
                             env=dict(os.environ, SILKIT_TEST_CRASH=role))
    value = result(process, output, 1)
    assert f'{role} exited unexpectedly (21)' in value['error']
    assert len(value['cleanup']) == 5


def test_silkit_readiness_timeout_never_resumes_or_starts_qbox(launch, silkit_options, tmp_path):
    marker = tmp_path / 'qbox-started'
    process, output = launch([sys.executable, '-c', f"open({str(marker)!r}, 'w').close()"],
                             options=silkit_options,
                             env=dict(os.environ, SILKIT_TEST_NO_READY='restbus'))
    value = result(process, output, 1)
    assert 'readiness timed out' in value['error']
    assert not marker.exists()
    assert not (output / 'qemu-resumed').exists()
    assert len(value['cleanup']) == 4


def test_external_silkit_registry_is_not_owned(launch, silkit_options):
    process, output = launch([sys.executable, '-c', 'import time;time.sleep(.2)'],
                             options=silkit_options + ['--sil-kit-registry', 'silkit://example.test:8500',
                                                      '--sil-kit-allow-actuation', '--sil-kit-echo-fixture'])
    value = result(process, output)
    kit = value['sil_kit']
    assert kit['external_registry'] is True
    assert kit['registry_uri'] == 'silkit://example.test:8500'
    assert len(value['cleanup']) == 4
    roles = {entry['role']: entry for entry in kit['processes']}
    assert set(roles) == {'bridge', 'restbus'}
    assert '--allow-actuation' in roles['restbus']['command']
    assert '--echo-fixture' in roles['restbus']['command']


def test_console_backpressure_logs_only_received_bytes_and_drains_on_close(tmp_path):
    path = tmp_path / 'console.sock'
    log = tmp_path / 'console.log'
    with socket.socket(socket.AF_UNIX) as server:
        server.bind(str(path))
        server.listen()
        bridge = companion.ConsoleBridge(path, tmp_path / 'console.in', log)
        peer, _ = server.accept()
        with peer:
            peer.setblocking(False)
            peer.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024)
            payload = bytes(range(256)) * 32
            sent = retries = 0
            while sent < len(payload):
                try:
                    sent += peer.send(payload[sent:sent + 1])
                except BlockingIOError:
                    # ASCLIN retries this same byte. It must not appear twice.
                    retries += 1
                    bridge.pump()
            assert retries > 0
            peer.shutdown(socket.SHUT_WR)
            bridge.close()
            bridge.close()  # Resource cleanup remains idempotent.
        assert log.read_bytes() == payload
        assert bridge.output_bytes == len(payload)
