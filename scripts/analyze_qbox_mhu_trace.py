#!/usr/bin/env python3
"""Summarize QBox MHUv3 trace logs and pair request/response doorbells."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
import json
from pathlib import Path
import re
from typing import Any


KV_RE = re.compile(r"(\w+)=([^\s]+)")
SC_TIME_RE = re.compile(r"\bsc_time=(\d+)\s*(ns|us|ms|s)?\b")


def parse_sc_time(line: str, value: str | None) -> int:
    match = SC_TIME_RE.search(line)
    if match:
        raw = int(match.group(1))
        unit = match.group(2) or "ns"
        scale = {
            "ns": 1,
            "us": 1_000,
            "ms": 1_000_000,
            "s": 1_000_000_000,
        }[unit]
        return raw * scale
    if value and value.isdigit():
        return int(value)
    return 0


def parse_trace(
    path: Path,
    request_pair: str,
    response_pair: str,
    channel: str,
    value_prefix: str,
) -> dict[str, Any]:
    counts: Counter[tuple[str, str]] = Counter()
    first_last: dict[tuple[str, str], list[int]] = {}
    requests: list[tuple[str, int, int, str]] = []
    responses: list[tuple[str, int, int, str]] = []
    line_count = 0

    with path.open(encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, 1):
            line_count = line_no
            kv = dict(KV_RE.findall(line))
            event = kv.get("event")
            pair = kv.get("pair")
            if event and pair:
                key = (pair, event)
                counts[key] += 1
                sc_time = parse_sc_time(line, kv.get("sc_time"))
                first_last.setdefault(key, [line_no, sc_time, line_no, sc_time])
                first_last[key][2] = line_no
                first_last[key][3] = sc_time

            if event != "postbox-doorbell-write":
                continue
            if kv.get("channel") != channel:
                continue
            value = kv.get("value")
            if not value or not value.startswith(value_prefix):
                continue
            sc_time = parse_sc_time(line, kv.get("sc_time"))
            item = (value, sc_time, line_no, line.rstrip("\n"))
            if pair == request_pair:
                requests.append(item)
            elif pair == response_pair:
                responses.append(item)

    response_by_value: dict[str, deque[tuple[str, int, int, str]]] = defaultdict(deque)
    for item in responses:
        response_by_value[item[0]].append(item)

    paired: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    for value, req_sc, req_line, req_text in requests:
        queue = response_by_value.get(value)
        while queue and queue[0][1] < req_sc:
            queue.popleft()
        if not queue:
            missing.append(
                {
                    "value": value,
                    "request_line": req_line,
                    "request_sc_time_ns": req_sc,
                    "request_text": req_text,
                }
            )
            continue
        _, resp_sc, resp_line, resp_text = queue.popleft()
        paired.append(
            {
                "value": value,
                "request_line": req_line,
                "request_sc_time_ns": req_sc,
                "response_line": resp_line,
                "response_sc_time_ns": resp_sc,
                "latency_ns": resp_sc - req_sc,
                "response_text": resp_text,
            }
        )

    latencies = [item["latency_ns"] for item in paired]
    return {
        "trace": str(path),
        "line_count": line_count,
        "pairing": {
            "request_pair": request_pair,
            "response_pair": response_pair,
            "channel": channel,
            "value_prefix": value_prefix,
            "requests": len(requests),
            "responses": len(responses),
            "paired": len(paired),
            "missing": len(missing),
            "latency_ns": {
                "min": min(latencies) if latencies else None,
                "max": max(latencies) if latencies else None,
                "last": latencies[-1] if latencies else None,
            },
            "last_requests": [
                {"value": value, "line": line_no, "sc_time_ns": sc_time}
                for value, sc_time, line_no, _ in requests[-12:]
            ],
            "last_responses": [
                {"value": value, "line": line_no, "sc_time_ns": sc_time}
                for value, sc_time, line_no, _ in responses[-12:]
            ],
            "last_paired": paired[-12:],
            "missing_requests": missing,
        },
        "event_counts": [
            {
                "pair": pair,
                "event": event,
                "count": count,
                "first_line": first_last[(pair, event)][0],
                "first_sc_time_ns": first_last[(pair, event)][1],
                "last_line": first_last[(pair, event)][2],
                "last_sc_time_ns": first_last[(pair, event)][3],
            }
            for (pair, event), count in sorted(counts.items())
        ],
    }


def write_summary(result: dict[str, Any]) -> str:
    pairing = result["pairing"]
    latency = pairing["latency_ns"]
    lines = [
        f"trace: {result['trace']}",
        f"line_count: {result['line_count']}",
        (
            "pairing: "
            f"{pairing['request_pair']} -> {pairing['response_pair']} "
            f"channel={pairing['channel']} prefix={pairing['value_prefix']}"
        ),
        (
            "requests/responses: "
            f"{pairing['requests']}/{pairing['responses']} "
            f"paired={pairing['paired']} missing={pairing['missing']}"
        ),
        (
            "latency_ns: "
            f"min={latency['min']} max={latency['max']} last={latency['last']}"
        ),
        "last_paired:",
    ]
    for item in pairing["last_paired"]:
        lines.append(
            "  - "
            f"value={item['value']} "
            f"req_line={item['request_line']} "
            f"req_sc={item['request_sc_time_ns']} "
            f"resp_line={item['response_line']} "
            f"resp_sc={item['response_sc_time_ns']} "
            f"latency_ns={item['latency_ns']}"
        )
    if pairing["missing_requests"]:
        lines.append("missing_requests:")
        for item in pairing["missing_requests"]:
            lines.append(
                "  - "
                f"value={item['value']} "
                f"line={item['request_line']} "
                f"sc={item['request_sc_time_ns']}"
            )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze QBox MHUv3 trace logs and pair AP/RSE doorbells."
    )
    parser.add_argument("trace", type=Path, help="Path to mhuv3-trace.log")
    parser.add_argument("--json-out", type=Path, help="Optional JSON output path")
    parser.add_argument("--summary-out", type=Path, help="Optional text summary output path")
    parser.add_argument("--request-pair", default="ap_s_to_rse")
    parser.add_argument("--response-pair", default="rse_to_ap_s")
    parser.add_argument("--channel", default="1")
    parser.add_argument("--value-prefix", default="0x800")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = parse_trace(
        path=args.trace,
        request_pair=args.request_pair,
        response_pair=args.response_pair,
        channel=args.channel,
        value_prefix=args.value_prefix,
    )
    summary = write_summary(result)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(summary, encoding="utf-8")
    print(summary, end="")
    return 0 if result["pairing"]["missing"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
