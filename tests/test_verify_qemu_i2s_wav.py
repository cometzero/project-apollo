"""Exercise the generated WAV shell with real child processes and fake ALSA."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

import pytest


@pytest.fixture
def verify(monkeypatch):
    scripts = Path(__file__).resolve().parents[1] / "scripts/test"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location("verify_wav_test", scripts / "verify_qemu_i2s_wav.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FAKE_AUDIO = r'''
import json, os, pathlib, signal, sys, time

tool = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
root = pathlib.Path(os.environ["FAKE_ROOT"])
scenario = os.environ["FAKE_SCENARIO"]
if tool == "ip":
    sys.exit(0)
if tool == "wget":
    pathlib.Path(args[args.index("-O") + 1]).write_bytes(b"test-wave-data")
    sys.exit(0)
if tool == "timeout":
    index = 2 if args[0] == "-k" else 0
    args[index] = "0.5" if args[index] == "5" else "1.5"
    if scenario == "playback_timeout" and args[index + 1] == "aplay":
        args[index] = "0.5"
    os.execv(os.environ["REAL_TIMEOUT"], ["timeout", *args])
if "--version" in args:
    print("fake ALSA 1.2.13")
    sys.exit(0)
if "-l" in args:
    for card, base in ((0, "30200000"), (1, "30210000")):
        device = 0 if tool == "aplay" else 1
        print(f"card {card}: {base} [I2S], device {device}: stereo")
    sys.exit(0)
with (root / "calls.jsonl").open("a") as output:
    output.write(json.dumps({"tool": tool, "args": args}) + "\n")
(root / f"{tool}.pid").write_text(str(os.getpid()))

def terminate(signum, frame):
    (root / f"{tool}.terminated").touch()
    sys.exit(128 + signum)

signal.signal(signal.SIGTERM, terminate)
if tool == "arecord":
    if scenario == "prepare_failure":
        sys.exit(17)
    card, device = args[args.index("-D") + 1][3:].split(",")
    status = root / "asound" / f"card{card}" / f"pcm{device}c" / "sub0/status"
    status.parent.mkdir(parents=True, exist_ok=True)
    if scenario != "missing_status":
        state = "PREPARED" if scenario == "not_running" else "RUNNING"
        status.write_text(f"state: {state}\n")
    pathlib.Path(args[-1]).write_bytes(b"test-wave-data")
    while True:
        if (root / "play_started").exists():
            if scenario == "capture_failure":
                sys.exit(7)
            if scenario == "capture_finishes_first":
                sys.exit(0)
        if (root / "play_finished").exists() and scenario == "success":
            sys.exit(0)
        time.sleep(0.01)
else:
    status_files = list((root / "asound").glob("card*/pcm*c/sub0/status"))
    assert status_files and "RUNNING" in status_files[0].read_text()
    (root / "play_started").touch()
    if scenario == "playback_failure":
        sys.exit(9)
    if scenario in ("capture_failure", "playback_timeout", "outer_signal"):
        time.sleep(30)
    time.sleep(0.15)
    (root / "play_finished").touch()
'''


@pytest.fixture
def generated_case(tmp_path, verify):
    binary = tmp_path / "bin"
    binary.mkdir()
    implementation = binary / "fake-audio"
    implementation.write_text(f"#!{sys.executable}\n" + FAKE_AUDIO)
    implementation.chmod(0o755)
    for command in ("ip", "wget", "timeout", "aplay", "arecord"):
        (binary / command).symlink_to(implementation)
    guest = tmp_path / "guest"
    guest.mkdir()
    interrupts = tmp_path / "interrupts"
    interrupts.write_text("")
    script = verify.guest_script(12345, 96000)
    script = script.replace("/tmp/", str(guest) + "/")
    script = script.replace("/proc/asound/", str(tmp_path / "asound") + "/")
    script = script.replace("/proc/interrupts", str(interrupts))
    # One direction isolates lifecycle checks from a second command pair.
    script = script.replace('run_case reverse "$tx1" "$rx0"\n', "")
    path = tmp_path / "case.sh"
    path.write_text(script)
    environment = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ["PATH"],
                       REAL_TIMEOUT=shutil.which("timeout"), FAKE_ROOT=str(tmp_path))
    return path, environment, tmp_path


def run_case(generated_case, scenario):
    path, environment, root = generated_case
    result = subprocess.run(["sh", str(path)], env=dict(environment, FAKE_SCENARIO=scenario),
                            text=True, capture_output=True, timeout=8)
    for pid_file in root.glob("*.pid"):
        with pytest.raises(ProcessLookupError):
            os.kill(int(pid_file.read_text()), 0)
    return result


@pytest.mark.parametrize("scenario", ["success", "capture_finishes_first"])
def test_ready_capture_and_exact_command_policy(generated_case, scenario):
    result = run_case(generated_case, scenario)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "WAV_READY=forward rc=0 " in result.stdout
    assert "WAV_EXIT=forward playback=0 capture=0" in result.stdout
    calls = [json.loads(line) for line in (generated_case[2] / "calls.jsonl").read_text().splitlines()]
    playback = next(call["args"] for call in calls if call["tool"] == "aplay")
    capture = next(call["args"] for call in calls if call["tool"] == "arecord")
    assert "--fatal-errors" in playback and "--fatal-errors" in capture
    assert "--period-size=4096" in playback and "--buffer-size=16384" in playback
    assert "--period-size=1024" in capture and "--buffer-size=16384" in capture
    assert capture[capture.index("-s") + 1] == "96000"


@pytest.mark.parametrize("scenario", ["missing_status", "not_running"])
def test_readiness_timeout_skips_playback_and_reaps_recorder(generated_case, scenario):
    result = run_case(generated_case, scenario)
    assert result.returncode != 0
    assert "WAV_READY=forward rc=124 " in result.stdout
    assert "WAV_PLAYBACK_SKIPPED=forward reason=capture-not-ready" in result.stdout
    assert "WAV_EXIT=forward playback=125 capture=143" in result.stdout
    assert not (generated_case[2] / "aplay.pid").exists()


def test_capture_prepare_failure_preserves_exit_status(generated_case):
    result = run_case(generated_case, "prepare_failure")
    assert result.returncode != 0
    assert "WAV_READY=forward rc=1 " in result.stdout
    assert "WAV_EXIT=forward playback=125 capture=17" in result.stdout


@pytest.mark.parametrize("scenario,marker", [
    ("playback_failure", "WAV_EXIT=forward playback=9 capture=143"),
    ("capture_failure", "WAV_EXIT=forward playback=143 capture=7"),
    ("playback_timeout", "WAV_EXIT=forward playback=124 capture=143"),
    ("capture_timeout", "WAV_EXIT=forward playback=0 capture=124"),
])
def test_first_error_and_timeout_keep_status_and_cleanup(generated_case, scenario, marker):
    result = run_case(generated_case, scenario)
    assert result.returncode != 0
    assert marker in result.stdout, result.stdout + result.stderr
    assert "WAV_DATA_BEGIN=forward" in result.stdout
    assert "WAV_DATA_END=forward" in result.stdout


def test_outer_signal_cleans_up_both_children(generated_case):
    path, environment, root = generated_case
    child = subprocess.Popen(["sh", str(path)], env=dict(environment, FAKE_SCENARIO="outer_signal"),
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + 5
        while not (root / "play_started").exists():
            assert child.poll() is None
            assert time.monotonic() < deadline
            time.sleep(0.01)
        child.send_signal(signal.SIGTERM)
        assert child.wait(timeout=5) == 143
        for pid_file in root.glob("*.pid"):
            with pytest.raises(ProcessLookupError):
                os.kill(int(pid_file.read_text()), 0)
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()


def test_generated_shell_and_uart_injection(verify, tmp_path):
    script = verify.guest_script(12345, 96000)
    subprocess.run(["sh", "-n"], input=script, text=True, check=True)
    # This substitution is shared by both QBox harnesses.
    subprocess.run(["sh", "-n"], input=script.replace("aplay -D", "aplay -N -D"),
                   text=True, check=True)
    injection = verify.guest_injection("printf 'injection-ok\\n'\nexit 7\n")
    assert max(map(len, injection.splitlines())) < 1024
    result = subprocess.run(["sh"], input=injection.replace("/tmp/", str(tmp_path) + "/"),
                            text=True, capture_output=True, check=True)
    assert "injection-ok\nWAV_DONE=7\n" == result.stdout
    assert max(map(len, verify.guest_injection(script).splitlines())) < 1024
