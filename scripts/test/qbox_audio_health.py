"""Read-only PFDI timeout and RCU stall evidence from audio guest consoles."""

import re


_TIMEOUT = re.compile(
    r'^\s*(?:\[\s*\d+(?:\.\d+)?\]\s*)?'
    r'PFDI\s+pfdi_pe_run_exec_fn\s+timed out\b'
    r'(?:\s+on CPU\s+(\d+)\b)?'
)
_RCU_STALL = re.compile(
    r'^\s*(?:\[\s*\d+(?:\.\d+)?\]\s*)?(?:rcu:\s*)?'
    r'INFO:\s+rcu_(?:preempt|sched|bh)\s+'
    r'(?:self-detected stall on CPU\b|detected stalls on CPUs/tasks\b)'
)
_SCOPE = (
    'first standalone AUDIO_DT_BEGIN through end of console; counts are log '
    'matches, not unique events (replayed dmesg can repeat a message)'
)


def assess_pfdi_timeouts(console_text):
    """Separate pre-suite failures from failures after the first real marker.

    Line references are one-based console lines. Only a standalone
    AUDIO_DT_BEGIN row starts the observed interval; an echoed shell command
    or script containing that text does not. Repeated markers do not reset the
    interval, which extends through the end of the supplied console.

    Absence of a timeout is NO_FAILURE_OBSERVED, never positive deadline PASS.
    The function neither checks PFDI liveness nor modifies any log or archive.
    Counts represent matching log rows, not unique timeout events; repeated
    dmesg output can contain the same event more than once.
    """
    starts = []
    before = []
    during = []
    for number, raw_line in enumerate(console_text.split('\n'), 1):
        line = raw_line.rstrip('\r')
        if line.strip() == 'AUDIO_DT_BEGIN':
            starts.append(number)
            continue
        match = _TIMEOUT.match(line)
        if match is None:
            continue
        entry = {
            'line': number,
            'cpu': int(match.group(1)) if match.group(1) is not None else None,
            'text': line,
        }
        (during if starts else before).append(entry)

    if not starts:
        status = 'NOT_RUN'
    elif during:
        status = 'FAIL'
    else:
        status = 'NO_FAILURE_OBSERVED'
    return {
        'status': status,
        'suite_start_line': starts[0] if starts else None,
        'suite_start_lines': starts,
        'timeout_count': len(during),
        'timeouts': during,
        'pre_suite_timeout_count': len(before),
        'pre_suite_timeouts': before,
        'scope': _SCOPE,
    }


def assess_audio_guest_health(console_text):
    """Fail on observed PFDI timeout or RCU stall after audio suite start.

    Only the RCU detected-stalls and self-detected-stall report headers are
    matched, not general RCU initialization or priority-boosting information.
    Counts are matching log rows, not unique events. No observed failure does
    not establish deadline success, suite completion, or full guest health.
    """
    pfdi = assess_pfdi_timeouts(console_text)
    start = pfdi['suite_start_line']
    before = []
    during = []
    for number, raw_line in enumerate(console_text.split('\n'), 1):
        line = raw_line.rstrip('\r')
        if _RCU_STALL.match(line) is None:
            continue
        entry = {'line': number, 'text': line}
        (during if start is not None and number > start else before).append(entry)

    rcu_status = ('NOT_RUN' if start is None else
                  'FAIL' if during else 'NO_FAILURE_OBSERVED')
    rcu = {
        'status': rcu_status,
        'suite_start_line': start,
        'suite_start_lines': pfdi['suite_start_lines'],
        'stall_count': len(during),
        'stalls': during,
        'pre_suite_stall_count': len(before),
        'pre_suite_stalls': before,
        'scope': _SCOPE,
    }
    status = ('NOT_RUN' if start is None else
              'FAIL' if 'FAIL' in (pfdi['status'], rcu_status) else
              'NO_FAILURE_OBSERVED')
    return {'status': status, 'pfdi_timeouts': pfdi, 'rcu_stalls': rcu}


def apply_audio_checks(result, console_text):
    """Do not let command success hide XRUN or guest failure messages."""
    result['xrun_messages'] = re.findall(
        r'^.*(?:underrun!!!|overrun!!!|Broken pipe).*$', console_text, re.M)
    if result['xrun_messages']:
        result['status'] = 'FAIL'
    result['audio_status'] = result.get('status', 'NOT_ASSESSED')
    result['guest_health'] = assess_audio_guest_health(console_text)
    if result['guest_health']['status'] == 'FAIL':
        result['status'] = 'FAIL'
    return result
