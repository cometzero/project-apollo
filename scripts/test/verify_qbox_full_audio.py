#!/usr/bin/env python3
"""Run DMA350, I2S PCM and aplay/arecord checks via full-system run_qbox_yocto.sh --bsp."""

import argparse
import base64
import functools
import http.server
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import struct
import subprocess
import threading
import time
import wave
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "run"))
from autosd_uki import inspect_uki

from verify_qemu_i2s import ROOT, assess
from verify_qemu_i2s_wav import digest, guest_script, pcm


def guest_suite(port):
    return f'''#!/bin/sh
set -eu
ip link set eth0 up
ip addr replace 10.0.2.15/24 dev eth0
for file in memory.sh pcm.sh wav.sh; do
    success=0
    for attempt in 1 2 3 4 5; do
        wget -q -O /tmp/$file http://10.0.2.2:{port}/$file && success=1 && break
        sleep 1
    done
    test "$success" -eq 1 || exit 1
done
echo AUDIO_DT_BEGIN
for base in 30200000 30210000; do
    path=/sys/firmware/devicetree/base/soc/i2s@$base
    test -d "$path" || exit 1
    if test -f "$path/dmas"; then selected=dma; else selected=pio; fi
    echo "AUDIO_DT=$base mode=$selected"
    test "$selected" = __MODE__ || exit 1
done
echo AUDIO_DT_END
set +e
timeout 180 sh /tmp/memory.sh
memory_rc=$?
echo DMA350_MEMORY_EXIT=$memory_rc
echo QEMU_I2S_IRQ_BEFORE
cat /proc/interrupts
echo QEMU_I2S_IRQ_END
timeout 180 sh /tmp/pcm.sh
pcm_rc=$?
echo QEMU_I2S_IRQ_AFTER
cat /proc/interrupts
echo QEMU_I2S_IRQ_END
echo QEMU_I2S_DONE=$pcm_rc
timeout 180 sh /tmp/wav.sh
wav_rc=$?
echo WAV_DONE=$wav_rc
test "$memory_rc" -eq 0 && test "$pcm_rc" -eq 0 && test "$wav_rc" -eq 0
'''


def prepare_disk(args, out, mode):
    """Patch only unsigned UKI DT sections in a private GPT boot WIC copy.

    The partition offset matches the BSP WIC/runner contract. Both A/B UKIs
    are updated because firmware boot-control state chooses the slot.
    """
    disk = out / 'audio-boot.wic'
    source_hash = digest(args.rootfs)
    subprocess.run(['cp', '--reflink=auto', '--sparse=always', str(args.rootfs), str(disk)], check=True)
    image = str(disk) + '@@1048576'
    evidence = {'source': str(args.rootfs), 'source_sha256': source_hash,
                'private_disk': str(disk), 'mode': mode, 'slots': []}
    for slot in ('a', 'b'):
        esp = f'::/EFI/Linux/{slot}-slot/auto-ad-nexios-{slot}.efi'
        uki = out / f'{slot}.efi'
        subprocess.run(['mcopy', '-i', image, esp, str(uki)], check=True)
        before = inspect_uki(uki)
        section = before['sections']['.dtb']
        raw = bytearray(uki.read_bytes())
        tree = out / f'{slot}.dtb'
        tree.write_bytes(raw[section['offset']:section['offset'] + section['size']])
        if mode == 'pio':
            for base in ('30200000', '30210000'):
                for prop in ('dmas', 'dma-names'):
                    subprocess.run(['fdtput', '-d', str(tree), f'/soc/i2s@{base}', prop], check=True)
            data = tree.read_bytes()
            if len(data) > section['raw_size']:
                raise ValueError('Modified DT exceeds original UKI section capacity')
            start = section['offset']
            raw[start:start + section['raw_size']] = data.ljust(section['raw_size'], b'\0')
            uki.write_bytes(raw)
            subprocess.run(['mcopy', '-o', '-i', image, str(uki), esp], check=True)
        after = inspect_uki(uki)
        for name in before['sections']:
            if name != '.dtb' and before['sections'][name]['sha256'] != after['sections'][name]['sha256']:
                raise ValueError('Unexpected non-DT UKI payload change')
        evidence['slots'].append({'slot': slot, 'original': before, 'prepared': after,
                                  'dtb': str(tree), 'dtb_sha256': digest(tree)})
    if digest(args.rootfs) != source_hash:
        raise ValueError('Source WIC changed while preparing test disk')
    evidence['prepared_sha256'] = digest(disk)
    (out / 'disk-preparation.json').write_text(json.dumps(evidence, indent=2) + '\n')
    return disk, evidence


def run_mode(args, output, serve, mode, port):
    out = output / mode
    out.mkdir()
    disk, disk_evidence = prepare_disk(args, out, mode)
    fifo = out / 'audio-input.fifo'
    os.mkfifo(fifo, 0o600)
    fifo_fd = os.open(fifo, os.O_RDWR | os.O_NONBLOCK)
    command = [str(ROOT / 'run_qbox_yocto.sh'), '--bsp', '--headless',
               '--keep-running-after-pass', '--no-persistent-rse-state', '--copy-disks',
               '--multi-session', '--qboxconf', str(args.qboxconf),
               '--rootfs', str(disk), '--out-dir', str(out), '--timeout', str(args.timeout),
               '--', '--foreground-runtime']
    (serve / 'suite.sh').write_text((serve / 'suite-template.sh').read_text().replace('__MODE__', mode))
    started = time.monotonic()
    sent = False
    injection = (f'for n in 1 2 3 4 5; do wget -q -O /tmp/audio-suite.sh http://10.0.2.2:{port}/suite.sh && break; sleep 1; done; '
                 "sh /tmp/audio-suite.sh; rc=$?; printf 'QBOX_AUDIO_%s=%s\\n' DONE \"$rc\"\n")
    injection = 'ip link set eth0 up; ip addr replace 10.0.2.15/24 dev eth0; ' + injection
    with (output / f'{mode}-launcher.log').open('wb') as log:
        child = subprocess.Popen(command, cwd=ROOT, env={**os.environ, 'QBOX_APOLLO_NETDEV': 'type=user', 'QBOX_RDASPEN_PRIMARY_UART_READ_FILE': str(fifo)},
                                 stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            while child.poll() is None and time.monotonic() - started < args.timeout + 10:
                uart = out / 'qbox-primary-console.log'
                text = uart.read_text(errors='replace').replace('\r', '') if uart.exists() else ''
                if not sent and re.search(r'nexios-bsp(?:-failed)?#\s*$', text):
                    os.write(fifo_fd, injection.encode())
                    sent = True
                if 'Kernel panic - not syncing:' in text or re.search(r'^QBOX_AUDIO_DONE=\d+$', text, re.MULTILINE):
                    break
                time.sleep(0.3)
        finally:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
    os.close(fifo_fd)
    fifo.unlink(missing_ok=True)
    uart = out / 'qbox-primary-console.log'
    text = uart.read_text(errors='replace').replace('\r', '') if uart.exists() else ''
    memory_cases = re.findall(r'^DMA350_MEMORY_PASS base=(\w+) mode=(memcpy|memset)\b.*$', text, re.MULTILINE)
    memory_ok = set(memory_cases) == {(base, kind) for base in ('31000000', '31010000') for kind in ('memcpy', 'memset')}
    memory_ok &= bool(re.search(r'^DMA350_MEMORY_EXIT=0$', text, re.MULTILINE))
    pcm_result = assess(text, mode)
    source_params, source_pcm = pcm(output / 'source.wav')
    wav_results = []
    for name in ('forward', 'reverse'):
        result = {'direction': name, 'status': 'FAIL'}
        match = re.search(rf'^WAV_DATA_BEGIN={name}\n(.*?)^WAV_DATA_END={name}$', text, re.MULTILINE | re.DOTALL)
        if match:
            try:
                path = out / f'{name}.wav'
                path.write_bytes(base64.b64decode(''.join(match[1].split()), validate=True))
                params, data = pcm(path)
                same = params == source_params and data == source_pcm
                same_file = path.read_bytes() == (output / 'source.wav').read_bytes()
                commands_ok = bool(re.search(rf'^WAV_EXIT={name} playback=0 capture=0$', text, re.MULTILINE))
                result.update(status='PASS' if same and same_file and commands_ok else 'FAIL',
                              frames=len(data)//4, exact_pcm_match=same, exact_wav_match=same_file,
                              wav_sha256=digest(path), command_exit_success=commands_ok)
            except (ValueError, EOFError, wave.Error) as error:
                result['error'] = str(error)
        wav_results.append(result)
    wav_ok = all(r['status'] == 'PASS' for r in wav_results)
    memory_status = 'PASS' if memory_ok else 'FAIL'
    if args.tests == 'wav':
        memory_ok = True
        memory_status = 'SKIP'
        pcm_result = {'status': 'SKIP'}
    if args.tests == 'memory':
        pcm_result = {'status': 'SKIP'}
        wav_results = []
        wav_ok = True
    done = bool(re.search(r'^QBOX_AUDIO_DONE=0$', text, re.MULTILINE))
    qbox_log = out / 'qbox-platform.log'
    backend_ok = qbox_log.exists() and 'Apollo QVP audio: qemu-components arm-dma350 + dw-apb-i2s' in qbox_log.read_text(errors='replace')
    result = {'mode': mode, 'status': 'PASS' if done and backend_ok and memory_ok and pcm_result['status'] in ('PASS', 'SKIP') and wav_ok else 'FAIL',
              'audio_backend_confirmed': backend_ok,
              'dma350_memory': {'status': memory_status, 'cases': memory_cases},
              'i2s_pcm': pcm_result, 'wav': wav_results, 'command': command,
              'elapsed_seconds': time.monotonic()-started, 'guest_completed': done,
              'kernel_panic': 'Kernel panic - not syncing:' in text}
    config = json.loads(args.qboxconf.read_text())
    provider = config['provider']
    paths = {'qbox': str(Path(provider['bindir']) / 'platforms-vp'),
             'libqemu': str(Path(config['sysroot']['recipe_sysroot_native']) /
                            'usr/lib/libqemu-system-aarch64.so'),
             'qboxconf': str(args.qboxconf)}
    for name in ('qemu_dma350', 'qemu_dw_apb_i2s'):
        paths[name] = str(Path(provider['module_dir']) / (name + '.so'))
    for name in ('apollo-qvp.lua', 'apollo-qvp-common.lua'):
        candidate = Path(provider['data_dir']) / 'platforms/apollo' / name
        if candidate.exists():
            paths[name] = str(candidate)
    result['audio_backend'] = 'qemu-components'
    result['artifacts'] = {key: {'path': path, 'sha256': digest(path)} for key, path in paths.items()}
    result['disk_preparation'] = disk_evidence
    result['console_logs'] = [str(path) for path in sorted(out.glob('*.log'))]
    if (out / 'result.json').exists():
        result['launcher'] = json.loads((out / 'result.json').read_text())
    (output / f'{mode}-result.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, required=True)
    deploy = ROOT / 'build/tmp_baremetal/deploy/images/apollo-qvp'
    parser.add_argument('--rootfs', type=Path, default=deploy / 'nexios-bsp-initramfs-apollo-qvp.wic')
    parser.add_argument('--qboxconf', type=Path, default=deploy / 'nexios-bsp-initramfs-apollo-qvp.qboxconf')
    parser.add_argument('--timeout', type=int, default=1800)
    parser.add_argument('--mode', choices=('dma', 'pio', 'both'), default='both')
    parser.add_argument('--tests', choices=('all', 'memory', 'wav'), default='all')
    args = parser.parse_args()
    output = args.out_dir.absolute()
    output.mkdir(parents=True, exist_ok=False)
    serve = output / 'http'
    serve.mkdir()
    data = b''.join(struct.pack('<hh', int(18000*math.sin(2*math.pi*997*n/48000)),
                              int(14000*math.cos(2*math.pi*1499*n/48000))) for n in range(96000))
    with wave.open(str(output / 'source.wav'), 'wb') as wav:
        wav.setparams((2, 2, 48000, 96000, 'NONE', 'not compressed'))
        wav.writeframes(data)
    shutil.copyfile(output / 'source.wav', serve / 'source.wav')
    shutil.copyfile(ROOT / 'scripts/test/verify_dma350_memory.sh', serve / 'memory.sh')
    pcm_script = (ROOT / 'scripts/test/verify_qbox_i2s.sh').read_text()
    pcm_script = pcm_script.replace('result=0\nwait', 'wait')
    pcm_script = pcm_script.replace('echo "I2S_DIRECTION 0->1', 'result=0\necho "I2S_DIRECTION 0->1')
    for command in ('i2s-loopback "$tx0" "$rx1"', 'i2s-loopback "$tx1" "$rx0"'):
        pcm_script = pcm_script.replace(command + '\n', command + ' || result=1\n')
    (serve / 'pcm.sh').write_text(pcm_script)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(serve))
    with http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler) as server:
        wav_script = guest_script(server.server_port, 96000).replace('aplay -D', 'aplay -N -D')
        download = f'wget -q -O /tmp/source.wav http://10.0.2.2:{server.server_port}/source.wav'
        wav_script = wav_script.replace(download, 'download_ok=0\nfor attempt in 1 2 3 4 5; do\n    ' + download + ' && download_ok=1 && break\n    sleep 1\ndone\ntest "$download_ok" -eq 1')
        wav_script = wav_script.replace('run_case forward "$tx0" "$rx1"', 'result=0\nrun_case forward "$tx0" "$rx1" || result=1')
        wav_script = wav_script.replace('run_case reverse "$tx1" "$rx0"', 'run_case reverse "$tx1" "$rx0" || result=1')
        (serve / 'wav.sh').write_text(wav_script + 'exit "$result"\n')
        suite = guest_suite(server.server_port)
        if args.tests == 'memory':
            suite = suite.split('echo QEMU_I2S_IRQ_BEFORE')[0] + 'exit "$memory_rc"\n'
        elif args.tests == 'wav':
            suite = suite.split('set +e')[0] + 'set +e\ntimeout 180 sh /tmp/wav.sh\nrc=$?\necho WAV_DONE=$rc\nexit "$rc"\n'
        (serve / 'suite-template.sh').write_text(suite)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            modes = ('dma', 'pio') if args.mode == 'both' else (args.mode,)
            results = [run_mode(args, output, serve, mode, server.server_port) for mode in modes]
        finally:
            server.shutdown()
            thread.join()
    summary = {'status': 'PASS' if all(r['status'] == 'PASS' for r in results) else 'FAIL', 'results': results}
    (output / 'result.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))
    return 0 if summary['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
