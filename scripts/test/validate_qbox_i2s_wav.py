#!/usr/bin/env python3
"""Compare actual aplay/arecord WAV transfers through the QBox guest."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import shlex
import struct
import subprocess
import time
import wave


def make_wav(path, frames, seed):
    rng = random.Random(seed)
    pcm = b''.join(struct.pack('<hh', rng.randint(1, 32767),
                               -rng.randint(1, 32767)) for _ in range(frames))
    with wave.open(str(path), 'wb') as output:
        output.setparams((2, 2, 48000, 0, 'NONE', 'not compressed'))
        output.writeframes(pcm)


def read_wav(path):
    with wave.open(str(path), 'rb') as source:
        return ((source.getnchannels(), source.getsampwidth(), source.getframerate()),
                source.readframes(source.getnframes()))


def compare_wav(source, capture, period):
    params, expected = read_wav(source)
    actual_params, actual = read_wav(capture)
    first = next((i for i in range(min(len(expected), len(actual)) // 4)
                  if expected[i*4:i*4+4] != actual[i*4:i*4+4]), None)
    return dict(passed=params == actual_params == (2, 2, 48000) and actual == expected,
                expected_frames=len(expected)//4, captured_frames=len(actual)//4,
                first_mismatch_frame=first,
                zero_frames=sum(actual[i:i+4] == b'\0'*4 for i in range(0, len(actual), 4)),
                matching_periods=sum(actual[i:i+period*4] == expected[i:i+period*4]
                                     for i in range(0, len(expected), period*4)),
                expected_sha256=hashlib.sha256(expected).hexdigest(),
                captured_sha256=hashlib.sha256(actual).hexdigest())


def pcm_errors(log):
    """Do not accept a recovered XRUN just because the eventual WAV matches."""
    return [line for line in log.splitlines()
            if re.search(r'(?:overrun!!!|underrun!!!|state\s*:\s*XRUN|'
                         r'(?:read|write) error:)', line)]


def pcm_setup(log, period, buffer, avail_min=0):
    """Require the negotiated hardware setup, not ALSA's requested sizes."""
    expected = dict(format='S16_LE', channels='2', rate='48000',
                    period_size=str(period), buffer_size=str(buffer),
                    avail_min=str(avail_min or period))
    actual = {key: sorted(set(re.findall(r'^\s*' + key + r'\s*:\s*(\S+)\s*$',
                                        log, re.MULTILINE)))
              for key in expected}
    return dict(passed=all(actual[key] == [value] for key, value in expected.items()),
                expected=expected, actual=actual)


def transport_failure(args, results, case, guest_case, iteration, direction,
                      started, phase, error):
    """Keep completed cases and an explicit failure even if SCP stops responding."""
    def decoded(value):
        return value.decode(errors='replace') if isinstance(value, bytes) else (value or '')
    (case / f'{phase}.log').write_text(decoded(error.stdout) + decoded(error.stderr))
    results.append(dict(passed=False, iteration=iteration, direction=direction,
                        error='host_transport_failure_guest_cleanup_required',
                        phase=phase, detail=str(error), guest_directory=guest_case,
                        elapsed_seconds=time.monotonic() - started,
                        host_timeout_seconds=args.host_timeout))
    (args.out_dir / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(results[-1]), flush=True)
    return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--rounds', type=int, default=5)
    parser.add_argument('--frames', type=int, default=196608)
    parser.add_argument('--period', type=int, default=1024)
    parser.add_argument('--buffer', type=int, default=2048)
    parser.add_argument('--avail-min-frames', type=int, default=0,
                        help='requested poll threshold; verify actual ALSA value (0 uses period)')
    io_mode = parser.add_mutually_exclusive_group()
    io_mode.add_argument('--nonblock', action='store_true', default=False,
                         help='stress nonblocking partial I/O and fixed poll thresholds')
    io_mode.add_argument('--blocking', dest='nonblock', action='store_false',
                         help='use normal aplay/arecord blocking I/O (default)')
    parser.add_argument('--blocking-playback', action='store_true',
                        help='keep capture mode but use blocking playback writes')
    parser.add_argument('--cpu', type=int,
                        help='pin PCM processes to one guest CPU using taskset')
    parser.add_argument('--rt-priority', type=int, default=0,
                        help='chrt SCHED_FIFO priority for PCM processes (0 disables)')
    parser.add_argument('--fail-fast', action='store_true')
    parser.add_argument('--host-timeout', type=int, default=110,
                        help='wall-clock SSH command deadline for slower virtual clocks')
    parser.add_argument('--guest-timeout', type=int, default=45,
                        help='guest-clock deadline for each aplay/arecord process')
    parser.add_argument('--direction', choices=['both', '0to1', '1to0'], default='both')
    parser.add_argument('--port', type=int, default=8022)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--user', default='root')
    args = parser.parse_args()
    if min(args.rounds, args.frames, args.period, args.buffer) <= 0:
        parser.error('rounds, frames, period and buffer must be positive')
    if args.host_timeout <= 0:
        parser.error('host-timeout must be positive')
    if args.guest_timeout <= 0:
        parser.error('guest-timeout must be positive')
    if not 0 <= args.rt_priority <= 99:
        parser.error('rt-priority must be between 0 and 99')
    if args.cpu is not None and args.cpu < 0:
        parser.error('cpu must be nonnegative')
    if not 0 <= args.avail_min_frames <= args.buffer:
        parser.error('avail-min-frames must be between 0 and buffer size')
    args.out_dir.mkdir(parents=True, exist_ok=True)
    options = ['-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=no',
               '-o', 'UserKnownHostsFile=/dev/null', '-o', 'ConnectTimeout=5']
    target = f'{args.user}@{args.host}'
    ssh = ['ssh', *options, '-p', str(args.port), target]
    scp = ['scp', '-O', *options, '-P', str(args.port)]
    remote = subprocess.check_output(ssh + ['mktemp -d /tmp/i2s-wav.XXXXXX'],
                                     text=True, timeout=args.host_timeout).strip()
    if not remote.startswith('/tmp/i2s-wav.') or any(c.isspace() for c in remote):
        raise RuntimeError(f'unexpected guest directory: {remote!r}')
    results = []
    for iteration in range(1, args.rounds + 1):
        for direction, tx, rx, card in [('0to1', 'hw:0,0', 'hw:1,1', 1),
                                        ('1to0', 'hw:1,0', 'hw:0,1', 0)]:
            if args.direction not in ['both', direction]:
                continue
            case = args.out_dir / f'{iteration:02d}-{direction}'
            case.mkdir()
            started = time.monotonic()
            guest_case = f'{remote}/{case.name}'
            try:
                subprocess.run(ssh + [f'mkdir {shlex.quote(guest_case)}'],
                               check=True, capture_output=True, timeout=args.host_timeout)
                make_wav(case / 'source.wav', args.frames, f'{iteration}-{direction}')
                subprocess.run(scp + [str(case/'source.wav'), f'{target}:{guest_case}/source.wav'],
                               check=True, capture_output=True, timeout=args.host_timeout)
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as error:
                return transport_failure(args, results, case, guest_case, iteration,
                                         direction, started, 'setup', error)
            io_mode = '-N' if args.nonblock else ''
            playback_mode = '' if args.blocking_playback else io_mode
            scheduler = f'chrt -f {args.rt_priority}' if args.rt_priority else ''
            if args.cpu is not None:
                scheduler = f'taskset -c {args.cpu} {scheduler}'
            avail = (f'--avail-min={(args.avail_min_frames * 1000000 + 47999) // 48000}'
                     if args.avail_min_frames else '')
            tx_card = tx.split(':')[1].split(',')[0]
            script = f'''set -u
cd {shlex.quote(guest_case)}
for status in /proc/asound/card{tx_card}/pcm0p/sub0/status /proc/asound/card{card}/pcm1c/sub0/status; do
    if test "$(cat "$status")" != closed; then
        echo "WAV_DEVICE_BUSY $status"
        exit 4
    fi
done
timeout {args.guest_timeout} {scheduler} arecord {io_mode} {avail} -D {rx} --dump-hw-params -v -t wav -f S16_LE -r 48000 -c 2 --period-size={args.period} --buffer-size={args.buffer} -s {args.frames} capture.wav >arecord.log 2>&1 &
capture=$!
count=0
ready=0
while test "$count" -lt 1000; do
    state=
    IFS= read -r state < /proc/asound/card{card}/pcm1c/sub0/status
    case "$state" in
        'state: RUNNING') ready=1; break ;;
    esac
    kill -0 "$capture" 2>/dev/null || break
    count=$((count+1))
    sleep 0.001
done
if test "$ready" -ne 1; then
    kill "$capture" 2>/dev/null || true
    wait "$capture" || true
    echo WAV_CAPTURE_NOT_RUNNING
    exit 3
fi
timeout {args.guest_timeout} {scheduler} aplay {playback_mode} {avail} -D {tx} --dump-hw-params -v --period-size={args.period} --buffer-size={args.buffer} source.wav >aplay.log 2>&1
play_rc=$?
echo WAV_AFTER_PLAYBACK_CAPTURE_STATUS
cat /proc/asound/card{card}/pcm1c/sub0/status
wait "$capture"
capture_rc=$?
echo "WAV_EXIT aplay=$play_rc arecord=$capture_rc"
test "$play_rc" -eq 0 && test "$capture_rc" -eq 0
'''
            (case / 'command.sh').write_text(script)
            try:
                run = subprocess.run(ssh + ['sh', '-s'], input=script, text=True,
                                     capture_output=True, timeout=args.host_timeout)
            except subprocess.TimeoutExpired as error:
                # A host timeout does not prove that the guest PCM processes
                # exited. Preserve evidence and stop rather than overlap cases.
                def decoded(value):
                    return value.decode(errors='replace') if isinstance(value, bytes) else (value or '')
                (case / 'ssh.log').write_text(decoded(error.stdout) + decoded(error.stderr))
                results.append(dict(passed=False, iteration=iteration, direction=direction,
                                    error='host_timeout_guest_cleanup_required',
                                    guest_directory=guest_case,
                                    elapsed_seconds=time.monotonic() - started,
                                    host_timeout_seconds=args.host_timeout))
                (args.out_dir/'results.json').write_text(json.dumps(results, indent=2)+'\n')
                print(json.dumps(results[-1]), flush=True)
                return 1
            (case / 'ssh.log').write_text(run.stdout + run.stderr)
            # One remote glob keeps all three artifacts in one SCP session.
            # Do not fetch source.wav: the host-side reference must stay intact.
            try:
                copy = subprocess.run(scp + [f'{target}:{guest_case}/[ac]*', str(case)],
                                      capture_output=True, text=True, timeout=args.host_timeout)
            except subprocess.TimeoutExpired as error:
                return transport_failure(args, results, case, guest_case, iteration,
                                         direction, started, 'copy', error)
            (case / 'copy.log').write_text(copy.stdout + copy.stderr)
            try:
                result = compare_wav(case/'source.wav', case/'capture.wav', args.period)
            except (OSError, EOFError, wave.Error) as error:
                result = dict(passed=False, error=str(error))
            result.update(iteration=iteration, direction=direction, command_exit=run.returncode,
                          elapsed_seconds=time.monotonic() - started,
                          copy_exit=copy.returncode, period_frames=args.period,
                          buffer_frames=args.buffer, nonblock=args.nonblock,
                          playback_nonblock=args.nonblock and not args.blocking_playback,
                          cpu=args.cpu,
                          host_timeout_seconds=args.host_timeout,
                          guest_timeout_seconds=args.guest_timeout,
                          rt_priority=args.rt_priority, avail_min_frames=args.avail_min_frames)
            result['pcm_errors'] = {
                name: pcm_errors((case / name).read_text(errors='replace'))
                for name in ['aplay.log', 'arecord.log'] if (case / name).exists()
            }
            result['pcm_setup'] = {
                name: pcm_setup((case / name).read_text(errors='replace'),
                                args.period, args.buffer, args.avail_min_frames)
                for name in ['aplay.log', 'arecord.log'] if (case / name).exists()
            }
            result['passed'] &= (run.returncode == 0 and copy.returncode == 0
                                 and not any(result['pcm_errors'].values())
                                 and len(result['pcm_setup']) == 2
                                 and all(setup['passed'] for setup in result['pcm_setup'].values()))
            results.append(result)
            print(json.dumps(result), flush=True)
            (args.out_dir/'results.json').write_text(json.dumps(results, indent=2)+'\n')
            if args.fail_fast and not result['passed']:
                return 1
    return 0 if all(item['passed'] for item in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
