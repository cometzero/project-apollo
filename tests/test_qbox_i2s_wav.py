import importlib.util
from pathlib import Path
import wave
import json
import subprocess
import sys
import shutil
import pytest


path = Path(__file__).resolve().parents[1] / 'scripts/test/validate_qbox_i2s_wav.py'
spec = importlib.util.spec_from_file_location('i2s_wav', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_wav_comparison_rejects_tail_loss_and_zero_period(tmp_path):
    source = tmp_path / 'source.wav'
    capture = tmp_path / 'capture.wav'
    module.make_wav(source, 4096, 'regression')
    params, pcm = module.read_wav(source)
    for data, passed, first in [(pcm, True, None), (pcm[:-4096], False, None),
                                (pcm[:8192] + bytes(8192), False, 2048)]:
        with wave.open(str(capture), 'wb') as output:
            output.setparams((*params, 0, 'NONE', 'not compressed'))
            output.writeframes(data)
        result = module.compare_wav(source, capture, 1024)
        assert result['passed'] is passed
        assert result['first_mismatch_frame'] == first
        assert result['captured_frames'] == len(data) // 4


def test_wrong_rate_is_not_a_pcm_match(tmp_path):
    source = tmp_path / 'source.wav'
    capture = tmp_path / 'capture.wav'
    module.make_wav(source, 1024, 'rate')
    _, pcm = module.read_wav(source)
    with wave.open(str(capture), 'wb') as output:
        output.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))
        output.writeframes(pcm)
    assert not module.compare_wav(source, capture, 1024)['passed']


def test_recovered_xrun_is_still_an_error():
    assert module.pcm_errors('Recording WAVE\nstate: RUNNING\n') == []
    assert len(module.pcm_errors('overrun!!! (at least 1 ms long)\n'
                                 '  state       : XRUN\n')) == 2
    assert module.pcm_errors('underrun!!!')[0] == 'underrun!!!'
    assert module.pcm_errors('arecord: pcm_read: read error: Input/output error')
    assert module.pcm_errors('aplay: playback drain error: Connection timed out')


def test_host_timeout_records_failure_and_stops_cases(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['validate_qbox_i2s_wav.py',
                                     '--out-dir', str(tmp_path), '--host-timeout', '900'])
    monkeypatch.setattr(module.subprocess, 'check_output',
                        lambda *args, **kwargs: '/tmp/i2s-wav.test\n')
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        assert kwargs['timeout'] == 900
        if 'input' in kwargs:
            raise subprocess.TimeoutExpired(command, 900, output=b'partial log\n')
        return subprocess.CompletedProcess(command, 0, '', '')

    monkeypatch.setattr(module.subprocess, 'run', run)
    assert module.main() == 1
    results = json.loads((tmp_path / 'results.json').read_text())
    assert len(results) == 1
    assert results[0]['passed'] is False
    assert results[0]['error'] == 'host_timeout_guest_cleanup_required'
    assert results[0]['guest_directory'] == '/tmp/i2s-wav.test/01-0to1'
    assert (tmp_path / '01-0to1/ssh.log').read_text() == 'partial log\n'
    assert len(calls) == 3
    assert not (tmp_path / '01-1to0').exists()


def test_negotiated_pcm_setup_must_match_requested_ring():
    log = ('Its setup is:\n  format : S16_LE\n  channels : 2\n'
           '  rate : 48000\n  buffer_size : 2048\n  period_size : 1024\n'
           '  avail_min : 1024\n')
    assert module.pcm_setup(log, 1024, 2048)['passed']
    assert not module.pcm_setup(log.replace('2048', '4096'), 1024, 2048)['passed']
    assert not module.pcm_setup(log + '  buffer_size : 4096\n', 1024, 2048)['passed']
    assert not module.pcm_setup('', 1024, 2048)['passed']
    # alsa-lib clamps a requested sub-period threshold; it is not a distinct
    # one-frame wakeup experiment even if the requested CLI option was valid.
    assert not module.pcm_setup(log, 1024, 2048, 1)['passed']


@pytest.mark.parametrize('phase', ['setup', 'copy'])
def test_scp_timeout_is_a_recorded_failure(tmp_path, monkeypatch, phase):
    monkeypatch.setattr(sys, 'argv', ['validate_qbox_i2s_wav.py', '--out-dir', str(tmp_path)])
    monkeypatch.setattr(module.subprocess, 'check_output',
                        lambda *args, **kwargs: '/tmp/i2s-wav.test\n')

    def run(command, **kwargs):
        download = command[-2].endswith('/[ac]*')
        if command[0] == 'scp' and download == (phase == 'copy'):
            raise subprocess.TimeoutExpired(command, 110, stderr=b'transfer stalled\n')
        return subprocess.CompletedProcess(command, 0, '', '')

    monkeypatch.setattr(module.subprocess, 'run', run)
    assert module.main() == 1
    results = json.loads((tmp_path / 'results.json').read_text())
    assert len(results) == 1 and not results[0]['passed']
    assert results[0]['phase'] == phase
    assert (tmp_path / f'01-0to1/{phase}.log').read_text() == 'transfer stalled\n'
    assert not (tmp_path / '01-1to0').exists()


def test_case_collects_logs_and_capture_without_overwriting_source(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['validate_qbox_i2s_wav.py', '--out-dir', str(tmp_path),
                                     '--rounds', '1', '--direction', '0to1', '--frames', '4096',
                                     ])
    monkeypatch.setattr(module.subprocess, 'check_output',
                        lambda *args, **kwargs: '/tmp/i2s-wav.test\n')
    downloads = []

    def run(command, **kwargs):
        if command[0] == 'scp' and command[-2].endswith('/[ac]*'):
            downloads.append(command[-2])
            case = Path(command[-1])
            shutil.copyfile(case / 'source.wav', case / 'capture.wav')
            log = ('format : S16_LE\nchannels : 2\nrate : 48000\n'
                   'period_size : 1024\nbuffer_size : 2048\navail_min : 1024\n')
            for name in ['aplay.log', 'arecord.log']:
                (case / name).write_text(log)
        return subprocess.CompletedProcess(command, 0, 'WAV_EXIT aplay=0 arecord=0\n', '')

    monkeypatch.setattr(module.subprocess, 'run', run)
    assert module.main() == 0
    assert downloads == ['root@127.0.0.1:/tmp/i2s-wav.test/01-0to1/[ac]*']
    results = json.loads((tmp_path / 'results.json').read_text())
    assert results[0]['passed']
    assert results[0]['matching_periods'] == 4
    assert results[0]['nonblock'] is False
