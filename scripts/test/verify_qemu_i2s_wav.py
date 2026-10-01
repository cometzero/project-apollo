#!/usr/bin/env python3
"""Compare aplay WAV -> cross-wired I2S -> arecord WAV on Apollo QEMU."""

import argparse
import base64
import functools
import hashlib
import http.server
import json
import math
from pathlib import Path
import re
import struct
import subprocess
import threading
import time
import wave

from verify_qemu_i2s import ROOT, interrupt_counts


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def pcm(path):
    with wave.open(str(path), 'rb') as stream:
        params = (stream.getframerate(), stream.getnchannels(),
                  stream.getsampwidth(), stream.getnframes())
        return params, stream.readframes(stream.getnframes())


def guest_script(port, frames):
    return f'''#!/bin/sh
set -eu
ip link set eth0 up
ip addr replace 10.0.2.15/24 dev eth0
wget -q -O /tmp/source.wav http://10.0.2.2:{port}/source.wav
sha256sum /tmp/source.wav
aplay --version
arecord --version
mode=pio
if test -e /sys/bus/platform/devices/30200000.i2s/of_node/dmas; then mode=dma; fi
echo WAV_MODE=$mode
pcm() {{
    "$1" -l | sed -n "/$2/s/^card \\([0-9][0-9]*\\):.*device \\([0-9][0-9]*\\):.*/hw:\\1,\\2/p" | head -n 1
}}
tx0=$(pcm aplay 30200000)
rx0=$(pcm arecord 30200000)
tx1=$(pcm aplay 30210000)
rx1=$(pcm arecord 30210000)
test -n "$tx0" && test -n "$rx0" && test -n "$tx1" && test -n "$rx1"
echo WAV_IRQ_BEFORE
cat /proc/interrupts
echo WAV_IRQ_END
recorder=
player=
cleanup_audio() {{
    for audio_pid in "$player" "$recorder"; do
        test -z "$audio_pid" || kill "$audio_pid" 2>/dev/null || :
    done
    for audio_pid in "$player" "$recorder"; do
        test -z "$audio_pid" || wait "$audio_pid" 2>/dev/null || :
    done
    player=
    recorder=
}}
trap cleanup_audio 0
trap 'exit 130' INT
trap 'exit 143' TERM
run_case() {{
    name=$1 tx=$2 rx=$3
    capture_card=${{rx#hw:}}
    capture_device=${{capture_card#*,}}
    capture_card=${{capture_card%%,*}}
    capture_status=/proc/asound/card$capture_card/pcm${{capture_device}}c/sub0/status
    played=125 recorded=125 ready=125
    echo "WAV_CASE=$name playback=$tx capture=$rx"
    rm -f /tmp/$name.wav
    : > /tmp/$name-play.log
    timeout -k 2 60 arecord -N --fatal-errors -D "$rx" -t wav -f S16_LE -r 48000 -c 2 \\
        --period-size=1024 --buffer-size=16384 -s {frames} \\
        /tmp/$name.wav > /tmp/$name-record.log 2>&1 &
    recorder=$!
    if timeout -k 2 5 sh -c '
        while kill -0 "$2" 2>/dev/null; do
            if grep -q "^state:[[:space:]]*RUNNING$" "$1" 2>/dev/null; then
                exit 0
            fi
            sleep 0.05
        done
        exit 1
    ' sh "$capture_status" "$recorder"; then ready=0; else ready=$?; fi
    echo "WAV_READY=$name rc=$ready status=$capture_status"
    if test "$ready" -eq 0; then
        timeout -k 2 60 aplay -D "$tx" --fatal-errors --period-size=4096 --buffer-size=16384 \\
            /tmp/source.wav > /tmp/$name-play.log 2>&1 &
        player=$!
        while kill -0 "$player" 2>/dev/null; do
            if test -n "$recorder" && ! kill -0 "$recorder" 2>/dev/null; then
                if wait "$recorder"; then recorded=0; else recorded=$?; fi
                recorder=
                if test "$recorded" -ne 0; then
                    echo "WAV_PLAYBACK_CANCELLED=$name reason=capture-failed"
                    kill "$player" 2>/dev/null || :
                    break
                fi
            fi
            sleep 0.05
        done
        if wait "$player"; then played=0; else played=$?; fi
        player=
    else
        echo "WAV_PLAYBACK_SKIPPED=$name reason=capture-not-ready"
    fi
    if test -n "$recorder"; then
        if test "$played" -ne 0; then
            echo "WAV_CAPTURE_CANCELLED=$name reason=playback-not-successful"
            kill "$recorder" 2>/dev/null || :
        fi
        if wait "$recorder"; then recorded=0; else recorded=$?; fi
        recorder=
    fi
    cat /tmp/$name-play.log /tmp/$name-record.log
    echo "WAV_EXIT=$name playback=$played capture=$recorded"
    echo WAV_DATA_BEGIN=$name
    if test -f /tmp/$name.wav; then base64 /tmp/$name.wav; fi
    echo WAV_DATA_END=$name
    test "$ready" -eq 0 && test "$played" -eq 0 && test "$recorded" -eq 0
}}
run_case forward "$tx0" "$rx1"
run_case reverse "$tx1" "$rx0"
echo WAV_IRQ_AFTER
cat /proc/interrupts
echo WAV_IRQ_END
'''


def guest_injection(script):
    """Keep every UART input line below the Linux canonical input limit."""
    encoded = base64.b64encode(script.encode()).decode()
    lines = [': > /tmp/wav-test.b64']
    lines.extend(f"printf '%s' '{encoded[offset:offset + 768]}' >> /tmp/wav-test.b64"
                 for offset in range(0, len(encoded), 768))
    lines.append("base64 -d /tmp/wav-test.b64 > /tmp/wav-test.sh && "
                 "sh /tmp/wav-test.sh; rc=$?; printf 'WAV_%s=%s\\n' DONE \"$rc\"")
    return '\n'.join(lines) + '\n'


def run_mode(args, output, mode, port):
    out = output / mode
    script = guest_script(port, args.frames)
    (output / f'{mode}-guest.sh').write_text(script)
    injection = guest_injection(script)
    command = [str(ROOT / 'run_qemu_linux.sh'), '--bsp', '--headless',
               '--i2s-mode', mode, '--netdev', 'user,id=net0',
               '--timeout', str(args.timeout), '--out-dir', str(out)]
    manifest = json.loads((ROOT / 'build/tmp_baremetal/deploy/qemu-apollo-native/qemu-apollo-native.json').read_text())
    binary_hash = digest(manifest['executable'])
    started = time.monotonic()
    sent = False
    with (output / f'{mode}-launcher.log').open('wb') as log:
        child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        try:
            while child.poll() is None and time.monotonic() - started < args.timeout + 10:
                uart = out / 'linux-uart.log'
                text = uart.read_text(errors='replace').replace('\r', '') if uart.exists() else ''
                if not sent and re.search(r'nexios-bsp(?:-failed)?#\s*$', text):
                    with (out / 'linux-uart.in').open('a') as stream:
                        stream.write(injection)
                    sent = True
                if re.search(r'^WAV_DONE=\d+$', text, re.MULTILINE):
                    break
                time.sleep(0.2)
        finally:
            if child.poll() is None:
                child.terminate()
            try:
                child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
    uart = out / 'linux-uart.log'
    text = uart.read_text(errors='replace').replace('\r', '') if uart.exists() else ''
    source_params, source_pcm = pcm(output / 'source.wav')
    results = []
    for name in ('forward', 'reverse'):
        result = {'direction': name, 'status': 'FAIL'}
        match = re.search(rf'^WAV_DATA_BEGIN={name}\n(.*?)^WAV_DATA_END={name}$',
                          text, re.MULTILINE | re.DOTALL)
        if match:
            try:
                path = out / f'{name}.wav'
                path.write_bytes(base64.b64decode(''.join(match[1].split()), validate=True))
                params, data = pcm(path)
                same = params == source_params and data == source_pcm
                commands_ok = bool(re.search(rf'^WAV_EXIT={name} playback=0 capture=0$', text, re.MULTILINE))
                result.update(status='PASS' if same and commands_ok else 'FAIL',
                              audio_params=params, frames_compared=len(data) // 4,
                              pcm_sha256=hashlib.sha256(data).hexdigest(),
                              wav_sha256=digest(path), exact_pcm_match=same,
                              exact_wav_file_match=path.read_bytes() == (output / 'source.wav').read_bytes(),
                              command_exit_success=commands_ok)
            except (ValueError, EOFError, wave.Error) as error:
                result['error'] = str(error)
        results.append(result)
    snapshots = {}
    for name in ('BEFORE', 'AFTER'):
        match = re.search(rf'^WAV_IRQ_{name}\n(.*?)^WAV_IRQ_END$', text, re.MULTILINE | re.DOTALL)
        snapshots[name] = interrupt_counts(match[1]) if match else {}
    deltas = {irq: value - snapshots['BEFORE'].get(irq, 0)
              for irq, value in snapshots['AFTER'].items()}
    irqs_ok = all(deltas.get(irq, 0) > 0 for irq in (('390',) if mode == 'dma' else ('388', '389')))
    done = bool(re.search(r'^WAV_DONE=0$', text, re.MULTILINE))
    actual_mode = bool(re.search(rf'^WAV_MODE={mode}$', text, re.MULTILINE))
    result = {'mode': mode, 'status': 'PASS' if done and actual_mode and irqs_ok and all(r['status'] == 'PASS' for r in results) else 'FAIL',
              'cases': results, 'interrupt_deltas': deltas, 'mode_verified': actual_mode,
              'source_params': source_params, 'source_pcm_sha256': hashlib.sha256(source_pcm).hexdigest(),
              'qemu_sha256': binary_hash, 'command': command, 'guest_completed': done,
              'elapsed_seconds': time.monotonic() - started}
    if (out / 'launch.json').exists():
        plan = json.loads((out / 'launch.json').read_text())
        result['artifact_sha256'] = {key: digest(plan[key]) for key in ('kernel', 'initrd', 'source_rootfs')}
    (output / f'{mode}-result.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--frames', type=int, default=96000)
    parser.add_argument('--timeout', type=float, default=240)
    args = parser.parse_args()
    if args.frames <= 0 or args.timeout <= 0:
        parser.error('frames and timeout must be positive')
    output = args.out_dir.absolute()
    output.mkdir(parents=True, exist_ok=False)
    serve = output / 'http'
    serve.mkdir()
    # Different stereo tones; compare without sample trimming or alignment.
    data = b''.join(struct.pack('<hh',
                    int(18000 * math.sin(2 * math.pi * 997 * n / 48000)),
                    int(14000 * math.cos(2 * math.pi * 1499 * n / 48000)))
                    for n in range(args.frames))
    with wave.open(str(output / 'source.wav'), 'wb') as wav:
        wav.setparams((2, 2, 48000, args.frames, 'NONE', 'not compressed'))
        wav.writeframes(data)
    (serve / 'source.wav').write_bytes((output / 'source.wav').read_bytes())
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(serve))
    with http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            results = [run_mode(args, output, mode, server.server_port) for mode in ('dma', 'pio')]
        finally:
            server.shutdown()
            thread.join()
    summary = {'status': 'PASS' if all(r['status'] == 'PASS' for r in results) else 'FAIL',
               'source_wav_sha256': digest(output / 'source.wav'), 'results': results}
    (output / 'result.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    return 0 if summary['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
