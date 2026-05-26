#!/usr/bin/env python3
"""Summarize QBox CC3XX trace logs, especially PKA opcode traffic."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
from typing import Any


TRACE_RE = re.compile(
    r"(?P<name>\S*cc3xx)\s+"
    r"(?P<command>dbg_)?(?P<rw>read|write)\s+"
    r"offset=0x(?P<offset>[0-9a-fA-F]+)\s+"
    r"len=0x(?P<len>[0-9a-fA-F]+)\s+"
    r"value=0x(?P<value>[0-9a-fA-F]+)"
)

PKA_OPCODE_OFFSET = 0x80

PKA_OP_NAMES = {
    0x04: "ADD_INC",
    0x05: "SUB_DEC_NEG",
    0x06: "MODADD_MODINC",
    0x07: "MODSUB_MODDEC_MODNEG",
    0x08: "AND_TST0_CLR0",
    0x09: "OR_COPY_SET0",
    0x0A: "XOR_FLIP0_INVERT_COMPARE",
    0x0C: "SHR0",
    0x0D: "SHR1",
    0x0E: "SHL0",
    0x0F: "SHL1",
    0x10: "MULLOW",
    0x11: "MODMUL",
    0x13: "MODEXP",
    0x14: "DIV",
    0x15: "MODINV",
    0x17: "MULHIGH",
    0x1B: "REDUCTION",
}


def decode_pka_opcode(value: int, line_no: int) -> dict[str, Any]:
    op = (value >> 27) & 0x1F
    return {
        "line": line_no,
        "value": f"0x{value:08x}",
        "op": op,
        "op_name": PKA_OP_NAMES.get(op, f"UNKNOWN_{op:#x}"),
        "size": (value >> 24) & 0x7,
        "lhs_immediate": bool((value >> 23) & 0x1),
        "lhs": (value >> 18) & 0x1F,
        "rhs_immediate": bool((value >> 17) & 0x1),
        "rhs": (value >> 12) & 0x1F,
        "discard_result": bool((value >> 11) & 0x1),
        "result": (value >> 6) & 0x1F,
    }


def parse_trace(path: Path, trace_limit: int | None) -> dict[str, Any]:
    trace_entries = 0
    offset_counts: Counter[tuple[str, int]] = Counter()
    pka_op_counts: Counter[int] = Counter()
    first_pka_opcodes: list[dict[str, Any]] = []
    last_pka_opcodes: list[dict[str, Any]] = []
    line_count = 0

    with path.open(encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, 1):
            line_count = line_no
            match = TRACE_RE.search(line)
            if not match:
                continue

            trace_entries += 1
            rw = match.group("rw")
            offset = int(match.group("offset"), 16)
            value = int(match.group("value"), 16)
            offset_counts[(rw, offset)] += 1

            if rw == "write" and offset == PKA_OPCODE_OFFSET:
                decoded = decode_pka_opcode(value, line_no)
                pka_op_counts[decoded["op"]] += 1
                if len(first_pka_opcodes) < 20:
                    first_pka_opcodes.append(decoded)
                last_pka_opcodes.append(decoded)
                if len(last_pka_opcodes) > 20:
                    last_pka_opcodes.pop(0)

    return {
        "trace": str(path),
        "line_count": line_count,
        "trace_entries": trace_entries,
        "trace_limit": trace_limit,
        "trace_limit_reached": trace_limit is not None and trace_entries >= trace_limit,
        "offset_counts": [
            {
                "command": rw,
                "offset": f"0x{offset:x}",
                "count": count,
            }
            for (rw, offset), count in offset_counts.most_common()
        ],
        "pka_opcode_count": sum(pka_op_counts.values()),
        "pka_op_counts": [
            {
                "op": op,
                "op_name": PKA_OP_NAMES.get(op, f"UNKNOWN_{op:#x}"),
                "count": count,
            }
            for op, count in sorted(pka_op_counts.items())
        ],
        "first_pka_opcodes": first_pka_opcodes,
        "last_pka_opcodes": last_pka_opcodes,
    }


def write_summary(result: dict[str, Any]) -> str:
    lines = [
        f"trace: {result['trace']}",
        f"line_count: {result['line_count']}",
        f"trace_entries: {result['trace_entries']}",
        f"trace_limit: {result['trace_limit']}",
        f"trace_limit_reached: {result['trace_limit_reached']}",
        f"pka_opcode_count: {result['pka_opcode_count']}",
        "pka_op_counts:",
    ]
    for item in result["pka_op_counts"]:
        lines.append(f"  - {item['op_name']} ({item['op']}): {item['count']}")

    lines.append("offset_counts_top:")
    for item in result["offset_counts"][:16]:
        lines.append(f"  - {item['command']} {item['offset']}: {item['count']}")

    lines.append("last_pka_opcodes:")
    for item in result["last_pka_opcodes"]:
        lines.append(
            "  - "
            f"line={item['line']} value={item['value']} "
            f"op={item['op_name']} size={item['size']} "
            f"lhs={item['lhs']}{'i' if item['lhs_immediate'] else ''} "
            f"rhs={item['rhs']}{'i' if item['rhs_immediate'] else ''} "
            f"discard={item['discard_result']} result={item['result']}"
        )

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze QBox CC3XX trace logs and decode PKA opcodes."
    )
    parser.add_argument("trace", type=Path, help="Path to qbox-platform.log")
    parser.add_argument("--trace-limit", type=int, help="Expected CC3XX trace limit")
    parser.add_argument("--json-out", type=Path, help="Optional JSON output path")
    parser.add_argument("--summary-out", type=Path, help="Optional text summary output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = parse_trace(args.trace, args.trace_limit)
    summary = write_summary(result)

    if args.json_out:
        args.json_out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if args.summary_out:
        args.summary_out.write_text(summary)
    if not args.json_out and not args.summary_out:
        print(summary, end="")

    return 1 if result["pka_opcode_count"] == 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
