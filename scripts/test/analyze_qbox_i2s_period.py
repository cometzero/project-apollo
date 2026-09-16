#!/usr/bin/env python3
"""Summarize guest kprobe durations; this is not a WAV pass/fail verdict."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import statistics


def summarize(trace):
    events = Counter()
    pending = {}
    durations = {'irq': [], 'program': [], 'receive': [], 'trigger': []}
    unmatched = 0
    for line in trace.splitlines():
        match = re.search(r'\S+-(\d+)\s+\[\d+\].*?\s(\d+\.\d+): (\w+):', line)
        if not match:
            continue
        pid, timestamp, event = match.groups()
        timestamp = float(timestamp)
        events[event] += 1
        for kind in durations:
            stack = pending.setdefault((pid, kind), [])
            if event == kind + '_enter':
                stack.append(timestamp)
            elif event == kind + '_exit':
                if stack:
                    durations[kind].append((timestamp - stack.pop()) * 1000)
                else:
                    unmatched += 1
    result = {}
    for kind, values in durations.items():
        values.sort()
        result[kind] = (dict(count=len(values), min_ms=min(values),
                            median_ms=statistics.median(values),
                            p95_ms=values[int(.95 * (len(values) - 1))],
                            max_ms=max(values)) if values else dict(count=0))
    return dict(events=dict(events), durations=result,
                unmatched_exits=unmatched,
                unmatched_entries=sum(map(len, pending.values())))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace', type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.trace.read_text()), indent=2))
