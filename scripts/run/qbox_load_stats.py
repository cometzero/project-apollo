"""Low-cost host accounting for launcher-owned QBox processes.

CPU percentages describe the preceding wall-clock interval; 100% is one host
logical CPU. Domain figures, when available, cover vCPU threads only.
"""
import argparse
import math
import os
from pathlib import Path
import time


def positive_interval(value):
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError('stats interval must be a finite positive number') from exc
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError('stats interval must be a finite positive number')
    return number


def add_arguments(parser):
    parser.add_argument('--stats', action='store_true',
                        help='log QBox load every 5 seconds (enables monitor and QMP)')
    parser.add_argument('--stats-interval', type=positive_interval, metavar='SECONDS',
                        help='load reporting interval (implies --stats, monitor and QMP)')


def interval_from_args(args):
    interval = getattr(args, 'stats_interval', None)
    return interval if interval is not None else (5.0 if getattr(args, 'stats', False) else None)


def read_stat(path):
    raw = path.read_text()
    fields = raw[raw.rindex(')') + 2:].split()
    return {'comm': raw[raw.index('(') + 1:raw.rindex(')')],
            'user': int(fields[11]), 'system': int(fields[12]),
            'start': int(fields[19]), 'rss': int(fields[21])}


def snapshot(pid, proc_root=Path('/proc')):
    base = proc_root / str(pid)
    process = read_stat(base / 'stat')
    threads = {}
    incomplete = False
    for task in (base / 'task').iterdir():
        try:
            threads[int(task.name)] = read_stat(task / 'stat')
        except (OSError, ValueError, IndexError):
            incomplete = True  # Threads can disappear during enumeration.
    return {'time': time.monotonic(), 'process': process, 'threads': threads,
            'incomplete': incomplete}


def summarize(before, after, pid, ticks_per_second):
    if before['process']['start'] != after['process']['start']:
        raise ValueError('process identity changed')
    elapsed = after['time'] - before['time']
    if elapsed <= 0:
        raise ValueError('host clock did not advance')
    scale = 100.0 / ticks_per_second / elapsed
    user = after['process']['user'] - before['process']['user']
    system = after['process']['system'] - before['process']['system']
    if user < 0 or system < 0:
        raise ValueError('CPU counters moved backwards')
    groups = {'main': 0.0, 'tcg': 0.0, 'other': 0.0}
    thread_cost = {}
    partial = before['incomplete'] or after['incomplete']
    if before['threads'].keys() != after['threads'].keys():
        partial = True
    for tid, end in after['threads'].items():
        start = before['threads'].get(tid)
        if start is None or start['start'] != end['start']:
            partial = True
            continue
        ticks = end['user'] + end['system'] - start['user'] - start['system']
        if ticks < 0:
            partial = True
            continue
        cost = ticks * scale
        thread_cost[tid] = cost
        role = 'main' if tid == pid else ('tcg' if end['comm'].endswith('/TCG') else 'other')
        groups[role] += cost
    return {'dt': elapsed, 'cpu': (user + system) * scale,
            'usr': user * scale, 'sys': system * scale, **groups,
            'thread_cost': thread_cost, 'partial': partial,
            'threads': len(after['threads']),
            'rss': after['process']['rss'] * os.sysconf('SC_PAGE_SIZE') / 1048576}


class LoadStats:
    """Called by the log owner; never writes guest input or changes VM state."""
    def __init__(self, pid, interval, monitor=None):
        self.pid, self.interval = pid, interval
        self.before = None
        self.started = time.monotonic()
        self.next_due = self.started + (interval or 5)
        self.hz = os.sysconf('SC_CLK_TCK')
        self.monitor = None
        self.domain_ids = [d["domain_id"] for d in (monitor or {}).get("domains", [])]
        if interval is not None:
            try:
                self.before = snapshot(pid)
            except (OSError, ValueError, IndexError):
                pass
            if monitor and monitor.get('enabled'):
                from qbox_stats_monitor import StatsMonitor
                self.monitor = StatsMonitor(pid, monitor, interval)
                self.monitor.start()

    def poll(self):
        now = time.monotonic()
        if self.interval is None or now < self.next_due:
            return []
        # Skip missed deadlines rather than emitting bursts after a slow probe.
        self.next_due = now + self.interval
        prefix = f"[{int(now - self.started)}s] "
        try:
            after = snapshot(self.pid)
            if self.before is None:
                self.before = after
                return [prefix + 'CPU warming-up']
            value = summarize(self.before, after, self.pid, self.hz)
            self.before = after
        except (OSError, ValueError, IndexError) as exc:
            return [prefix + f'CPU unavailable ({exc})']
        domains = ""
        if self.monitor:
            mappings = self.monitor.snapshot().get('domain_threads', {})
            names = {'ap': 'AP', 'rse': 'RSE', 'si-cl0': 'SI0', 'si-cl1': 'SI1'}
            active = set(self.domain_ids) | mappings.keys()
            ordered = [name for name in names if name in active]
            ordered.extend(sorted(active - names.keys()))
            fields = []
            seen = set()
            for domain in ordered:
                tids = mappings.get(domain, [])
                label = names.get(domain, domain)
                if not tids or seen.intersection(tids) or any(t not in value['thread_cost'] for t in tids):
                    fields.append(f'{label} N/A')
                else:
                    fields.append(f"{label} {sum(value['thread_cost'][t] for t in tids):.1f}")
                seen.update(tids)
            if fields:
                domains = ' [' + ' '.join(fields) + ']'
        return [prefix + f"CPU {value['cpu']:.1f}% (main {value['main']:.1f}% | "
                f"vCPU {value['tcg']:.1f}%{domains} | other {value['other']:.1f}%) "
                f"RSS {value['rss']:.0f}M threads={value['threads']}"]

    def close(self):
        if self.monitor:
            self.monitor.close()


def drain_output(pipe, log):
    """Copy available bytes; a single runner owns simulator and stats writes."""
    for _ in range(16):
        try:
            data = os.read(pipe.fileno(), 65536)
        except BlockingIOError:
            break
        if not data:
            break
        log.write(data)
