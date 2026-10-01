"""Pure fixtures: audio PASS must not hide PFDI timeout or RCU stall evidence."""

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/test'))
from qbox_audio_health import assess_audio_guest_health, assess_pfdi_timeouts


TIMEOUT = 'PFDI pfdi_pe_run_exec_fn timed out on CPU 3'


@pytest.mark.parametrize('text,status,starts,before,during', [
    pytest.param(
        'boot\nAUDIO_DT_BEGIN\nQBOX_AUDIO_DONE=0\n',
        'NO_FAILURE_OBSERVED', [2], [], [], id='normal'),
    pytest.param(
        f'boot\n{TIMEOUT}\n',
        'NOT_RUN', [], [2], [], id='no-marker'),
    pytest.param(
        f'{TIMEOUT}\nAUDIO_DT_BEGIN\nQBOX_AUDIO_DONE=0\n',
        'NO_FAILURE_OBSERVED', [2], [1], [], id='pre-suite-failure'),
    pytest.param(
        f'AUDIO_DT_BEGIN\n{TIMEOUT}\nQBOX_AUDIO_DONE=0\n',
        'FAIL', [1], [], [2], id='during-suite-failure'),
    pytest.param(
        f'{TIMEOUT}\r\nAUDIO_DT_BEGIN\r\n{TIMEOUT}\r\n',
        'FAIL', [2], [1], [3], id='crlf'),
    pytest.param(
        f'{TIMEOUT}\nAUDIO_DT_BEGIN\n{TIMEOUT}\n'
        'QBOX_AUDIO_ITERATION_END=1 rc=0\nAUDIO_DT_BEGIN\n'
        f'QBOX_AUDIO_DONE=0\n{TIMEOUT}\n',
        'FAIL', [2, 5], [1], [3, 7], id='repeat-keeps-earlier-failure'),
])
def test_timeout_scope_and_line_references(text, status, starts, before, during):
    result = assess_pfdi_timeouts(text)

    assert result['status'] == status
    assert result['suite_start_line'] == (starts[0] if starts else None)
    assert result['suite_start_lines'] == starts
    assert result['pre_suite_timeout_count'] == len(before)
    assert result['timeout_count'] == len(during)
    assert [event['line'] for event in result['pre_suite_timeouts']] == before
    assert [event['line'] for event in result['timeouts']] == during
    for event in result['pre_suite_timeouts'] + result['timeouts']:
        assert event['cpu'] == 3
        assert event['text'] == TIMEOUT


def test_echoed_commands_and_embedded_markers_do_not_start_suite():
    text = '\n'.join([
        'root:~# echo AUDIO_DT_BEGIN',
        'echo AUDIO_DT_BEGIN',
        'AUDIO_DT_BEGINNING',
        'log: AUDIO_DT_BEGIN',
        TIMEOUT,
    ])
    result = assess_pfdi_timeouts(text)

    assert result['status'] == 'NOT_RUN'
    assert result['suite_start_lines'] == []
    assert result['timeout_count'] == 0
    assert result['pre_suite_timeouts'][0]['line'] == 5


def test_kernel_timestamp_cpu_and_original_line_are_preserved():
    message = '[  72.125000] PFDI pfdi_pe_run_exec_fn timed out on CPU 0'
    result = assess_pfdi_timeouts(f'AUDIO_DT_BEGIN\n{message}\n')

    assert result['status'] == 'FAIL'
    assert result['timeouts'] == [{'line': 2, 'cpu': 0, 'text': message}]


def test_timeout_without_cpu_still_fails_without_inventing_cpu():
    message = 'PFDI pfdi_pe_run_exec_fn timed out'
    result = assess_pfdi_timeouts(f'AUDIO_DT_BEGIN\n{message}')

    assert result['status'] == 'FAIL'
    assert result['timeouts'] == [{'line': 2, 'cpu': None, 'text': message}]


def test_other_timeouts_and_quoted_commands_are_not_pfdi_failures():
    text = '\n'.join([
        'AUDIO_DT_BEGIN',
        'I2S playback timed out',
        'PFDI another_function timed out on CPU 0',
        f'echo "{TIMEOUT}"',
    ])

    result = assess_pfdi_timeouts(text)
    assert result['status'] == 'NO_FAILURE_OBSERVED'
    assert result['timeout_count'] == 0


def test_empty_console_is_not_run():
    result = assess_pfdi_timeouts('')

    assert result['status'] == 'NOT_RUN'
    assert result['suite_start_line'] is None
    assert result['timeout_count'] == result['pre_suite_timeout_count'] == 0


@pytest.mark.parametrize('message', [
    'rcu: INFO: rcu_preempt self-detected stall on CPU',
    'rcu: INFO: rcu_preempt detected stalls on CPUs/tasks:',
    '[  99.125000] rcu: INFO: rcu_sched detected stalls on CPUs/tasks:',
    'INFO: rcu_bh detected stalls on CPUs/tasks:',
])
def test_rcu_stall_header_fails_even_after_audio_success_marker(message):
    result = assess_audio_guest_health(
        f'AUDIO_DT_BEGIN\r\nQBOX_AUDIO_DONE=0\r\n{message}\r\n')

    assert result['status'] == 'FAIL'
    assert result['pfdi_timeouts']['status'] == 'NO_FAILURE_OBSERVED'
    assert result['rcu_stalls']['status'] == 'FAIL'
    assert result['rcu_stalls']['stall_count'] == 1
    assert result['rcu_stalls']['stalls'] == [{'line': 3, 'text': message}]


def test_pfdi_timeout_alone_fails_guest_health():
    result = assess_audio_guest_health(f'AUDIO_DT_BEGIN\n{TIMEOUT}')

    assert result['status'] == 'FAIL'
    assert result['pfdi_timeouts']['timeout_count'] == 1
    assert result['rcu_stalls']['status'] == 'NO_FAILURE_OBSERVED'


def test_ordinary_rcu_information_is_not_a_stall():
    text = '\n'.join([
        'rcu: Preemptible hierarchical RCU implementation.',
        'AUDIO_DT_BEGIN',
        'rcu: RCU priority boosting: priority 1 delay 500 ms.',
        'rcu: Hierarchical SRCU implementation.',
        'echo "rcu: INFO: rcu_preempt detected stalls on CPUs/tasks:"',
        'QBOX_AUDIO_DONE=0',
    ])
    result = assess_audio_guest_health(text)

    assert result['status'] == 'NO_FAILURE_OBSERVED'
    assert result['rcu_stalls']['stall_count'] == 0
    assert result['pfdi_timeouts']['timeout_count'] == 0


@pytest.mark.parametrize('marker,status', [
    ('echo AUDIO_DT_BEGIN', 'NOT_RUN'),
    ('AUDIO_DT_BEGIN', 'NO_FAILURE_OBSERVED'),
])
def test_pre_suite_failures_remain_separate(marker, status):
    stall = 'rcu: INFO: rcu_preempt self-detected stall on CPU'
    result = assess_audio_guest_health(f'{TIMEOUT}\n{stall}\n{marker}')

    assert result['status'] == status
    assert result['pfdi_timeouts']['pre_suite_timeout_count'] == 1
    assert result['rcu_stalls']['pre_suite_stall_count'] == 1
    assert result['rcu_stalls']['pre_suite_stalls'][0]['line'] == 2
    assert result['pfdi_timeouts']['timeout_count'] == 0
    assert result['rcu_stalls']['stall_count'] == 0


def test_repeated_markers_and_replayed_messages_do_not_erase_failure():
    stall = 'rcu: INFO: rcu_preempt detected stalls on CPUs/tasks:'
    text = f'AUDIO_DT_BEGIN\n{TIMEOUT}\n{stall}\nAUDIO_DT_BEGIN\n{stall}\n'
    result = assess_audio_guest_health(text)

    assert result['status'] == 'FAIL'
    assert result['pfdi_timeouts']['timeout_count'] == 1
    assert result['rcu_stalls']['suite_start_lines'] == [1, 4]
    assert result['rcu_stalls']['stall_count'] == 2
    assert [item['line'] for item in result['rcu_stalls']['stalls']] == [3, 5]
    assert 'not unique events' in result['rcu_stalls']['scope']
    assert 'not unique events' in result['pfdi_timeouts']['scope']


@pytest.mark.parametrize('message,audio_status,overall', [
    ('', 'PASS', 'PASS'),
    ('overrun!!! (at least 1 ms long)', 'FAIL', 'FAIL'),
    ('underrun!!!', 'FAIL', 'FAIL'),
    ('write failed: Broken pipe', 'FAIL', 'FAIL'),
    (TIMEOUT, 'PASS', 'FAIL'),
    ('rcu: INFO: rcu_preempt detected stalls on CPUs/tasks:', 'PASS', 'FAIL'),
])
def test_audio_success_does_not_hide_failures(message, audio_status, overall):
    from qbox_audio_health import apply_audio_checks

    result = apply_audio_checks(
        {'status': 'PASS'}, f'AUDIO_DT_BEGIN\n{message}\nQBOX_AUDIO_DONE=0\n')
    assert result['audio_status'] == audio_status
    assert result['status'] == overall


def test_health_check_cannot_upgrade_audio_failure():
    from qbox_audio_health import apply_audio_checks

    result = apply_audio_checks({'status': 'FAIL'}, 'AUDIO_DT_BEGIN\n')
    assert result['status'] == result['audio_status'] == 'FAIL'
