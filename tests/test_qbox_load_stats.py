"""Interval accounting, process identity and runner-owned log integration."""
import argparse
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/run'))
import qbox_load_stats as stats
import run_qbox_linux as linux


def sample(at, user, system):
    main = {'start': 10, 'comm': 'platforms-vp', 'user': user, 'system': system, 'rss': 100}
    return {'time': at, 'process': main, 'threads': {42: main.copy()}, 'incomplete': False}


def test_interval_cpu_and_thread_churn():
    before, after = sample(10, 100, 20), sample(15, 250, 70)
    value = stats.summarize(before, after, 42, 100)
    assert value['cpu'] == 40
    assert value['usr'] == 30
    assert value['sys'] == 10
    assert value['main'] == 40
    assert not value['partial']
    after['threads'][43] = {'start': 13, 'comm': 'CPU 0/TCG', 'user': 100, 'system': 0}
    assert stats.summarize(before, after, 42, 100)['partial']
    before['threads'][43] = {'start': 12, 'comm': 'CPU 0/TCG', 'user': 1, 'system': 0}
    value = stats.summarize(before, after, 42, 100)
    assert value['partial'] and value['tcg'] == 0
    after['process']['start'] += 1
    with pytest.raises(ValueError, match='identity'):
        stats.summarize(before, after, 42, 100)


def test_tcg_and_other_are_distinct():
    before, after = sample(10, 0, 0), sample(15, 0, 0)
    for obj, ticks in ((before, 0), (after, 100)):
        obj['threads'][43] = {'start': 20, 'comm': 'ALL CPUs/TCG', 'user': ticks, 'system': 0}
        obj['threads'][44] = {'start': 20, 'comm': 'qemu-iothread', 'user': ticks, 'system': 0}
    value = stats.summarize(before, after, 42, 100)
    assert value['tcg'] == 20 and value['other'] == 20


def test_disabled_has_no_proc_reads(monkeypatch):
    monkeypatch.setattr(stats, 'snapshot', lambda pid: pytest.fail('disabled stats read /proc'))
    sampler = stats.LoadStats(42, None)
    assert sampler.poll() == []
    sampler.close()


def test_default_window_and_no_catchup_burst(monkeypatch):
    clock = [100.]
    monkeypatch.setattr(stats.time, 'monotonic', lambda: clock[0])
    monkeypatch.setattr(stats, 'snapshot', lambda pid: sample(clock[0], int(clock[0]), 0))
    sampler = stats.LoadStats(42, 5)
    clock[0] = 104.9
    assert not sampler.poll()
    clock[0] = 105.
    assert sampler.poll()[0].startswith('[5s] CPU ')
    clock[0] = 130.
    assert sampler.poll()[0].startswith('[30s] CPU ')
    assert not sampler.poll()


@pytest.mark.parametrize('args, expected', [([], None), (['--stats'], 5), (['--stats-interval', '.5'], .5)])
def test_cli(args, expected):
    parser = argparse.ArgumentParser()
    stats.add_arguments(parser)
    assert stats.interval_from_args(parser.parse_args(args)) == expected


@pytest.mark.parametrize('value', ['0', '-1', 'nan', 'inf', 'bogus'])
def test_invalid_interval(value):
    parser = argparse.ArgumentParser()
    stats.add_arguments(parser)
    with pytest.raises(SystemExit):
        parser.parse_args(['--stats-interval', value])


def test_direct_supervisor_logs_stats_until_timeout(tmp_path):
    for name in ('linux-uart.log', 'linux-uart.in'):
        (tmp_path / name).touch()
    code = "import time; print('native-output', flush=True); time.sleep(30)"
    (tmp_path / 'launch.json').write_text(json.dumps({
        'command': [sys.executable, '-c', code], 'environment': {},
        'pass_marker': 'nexios-bsp#', 'bsp': True, 'stats_interval': .1}))
    assert linux.supervise(tmp_path, .5, False) == 124
    log = (tmp_path / 'qbox.log').read_text()
    assert 'native-output' in log
    assert log.count('CPU ') >= 2
    assert 'vCPU ' in log and 'threads=' in log


def test_shutdown_drains_large_native_output(tmp_path):
    for name in ('linux-uart.log', 'linux-uart.in'):
        (tmp_path / name).touch()
    code = """
import signal, sys, time
def stop(*args):
    sys.stdout.write('X' * 262144 + '\\nshutdown-complete\\n')
    sys.stdout.flush()
    sys.exit(0)
signal.signal(signal.SIGTERM, stop)
print('ready', flush=True)
time.sleep(30)
"""
    (tmp_path / 'launch.json').write_text(json.dumps({
        'command': [sys.executable, '-c', code], 'environment': {},
        'pass_marker': 'nexios-bsp#', 'bsp': True, 'stats_interval': .1}))
    assert linux.supervise(tmp_path, .5, False) == 124
    log = (tmp_path / 'qbox.log').read_text()
    assert 'X' * 262144 in log
    assert 'shutdown-complete' in log


def test_compact_domain_output(monkeypatch):
    from types import SimpleNamespace
    clock = [100.]
    monkeypatch.setattr(stats.time, 'monotonic', lambda: clock[0])
    monkeypatch.setattr(stats, 'snapshot', lambda pid: sample(clock[0], 0, 0))
    sampler = stats.LoadStats(42, 5)
    sampler.monitor = SimpleNamespace(snapshot=lambda: {'domain_threads': {
        'rse': [2], 'si-cl1': [4], 'ap': [1], 'si-cl0': [3]}})
    value = {'cpu': 16., 'main': 2.8, 'tcg': 10.7, 'other': 2.6,
             'rss': 2276, 'threads': 28, 'partial': True,
             'thread_cost': {1: 7.8, 2: .2, 3: 1.5, 4: 1.2}}
    monkeypatch.setattr(stats, 'summarize', lambda *args: value)
    clock[0] = 105.
    assert sampler.poll() == [
        '[5s] CPU 16.0% (main 2.8% | vCPU 10.7% [AP 7.8 RSE 0.2 SI0 1.5 SI1 1.2] | other 2.6%) RSS 2276M threads=28']
    del value['thread_cost'][1]
    clock[0] = 110.
    assert '[AP N/A RSE 0.2 SI0 1.5 SI1 1.2]' in sampler.poll()[0]
