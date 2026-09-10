#!/usr/bin/env python3
"""Correlate guest byte comparisons with actual AP DMA-350 bus operations."""
import argparse
import json
from pathlib import Path
import re


TRACE = re.compile(
    r"(?:ap_dma350|dma350_0) (copy|fill) channel=(0x[0-9a-f]+) "
    r"source=(0x[0-9a-f]+) dest=(0x[0-9a-f]+) bytes=(0x[0-9a-f]+) "
    r"src_trigger=(-?\d+) dest_trigger=(-?\d+) status=(\w+)"
)


def evaluate(guest_log: str, host_log: str) -> dict:
    operations = []
    for match in TRACE.finditer(host_log):
        kind, channel, source, dest, size, src_trigger, dst_trigger, status = match.groups()
        operations.append(dict(kind=kind, channel=int(channel, 16),
                               source=int(source, 16), dest=int(dest, 16),
                               bytes=int(size, 16), src_trigger=int(src_trigger),
                               dst_trigger=int(dst_trigger), status=status))
    errors = []
    if not re.search(r"APOLLO_DMA350\|result=0\|", guest_log):
        errors.append("guest validation did not finish successfully")
    if "APOLLO_DMA350|topology=dedicated|channels=8|status=PASS" not in guest_log:
        errors.append("missing eight-channel dedicated topology evidence")
    if "APOLLO_DMA350|interrupt=shared|specifiers=8|lines=1|hwirq=311|status=PASS" not in guest_log:
        errors.append("missing single combined non-secure interrupt evidence")
    if any(op["status"] == "error" for op in operations):
        errors.append("AP DMA-350 reported a transfer error")
    dedicated = {0x30160060: (0, 1), 0x30170060: (2, 3),
                 0x301A0000: (4, 5), 0x301B0000: (6, 7)}
    pio_fifos = {0x30100010 + i * 0x10000 for i in range(6)} | {
        0x30180060, 0x30190060, 0x301C0000, 0x301D0000}
    for op in operations:
        if op["source"] in pio_fifos or op["dest"] in pio_fifos:
            errors.append("DMA accessed a PIO-only peripheral")
        if op["channel"] >= 8:
            errors.append("DMA operation used a non-existent dedicated channel")
        for receive, trigger_key, address_key in (
            (False, "dst_trigger", "dest"), (True, "src_trigger", "source")
        ):
            request = op[trigger_key]
            if request >= 0 and (
                op[address_key] not in dedicated
                or request != dedicated[op[address_key]][int(receive)]
                or op["channel"] != request
            ):
                errors.append("DMA operation violated dedicated channel/FIFO mapping")

    def transferred(address: int, request: int, receive: bool, minimum: int) -> int:
        address_key = "source" if receive else "dest"
        trigger_key = "src_trigger" if receive else "dst_trigger"
        return sum(op["bytes"] for op in operations
                   if op[address_key] == address and op[trigger_key] == request
                   and op["status"] in ("done", "stopped", "disabled")
                   and op["bytes"] >= minimum)

    memory = [op for op in operations if op["src_trigger"] == -1
              and op["dst_trigger"] == -1 and op["status"] == "done"
              and op["bytes"] > 0 and op["dest"] >= 0x80000000]
    if not memory or not re.search(r"APOLLO_DMA350\|memory=.*\|status=PASS", guest_log):
        errors.append("missing successful memory DMA evidence")
    if {op["kind"] for op in memory} != {"copy", "fill"}:
        errors.append("memory DMA must cover both memcpy and memset")

    ports = []
    for kind, count, base, register, first_request, minimum in (
        ("spi", 2, 0x30160000, 0x60, 0, 1),
        ("uart", 2, 0x301A0000, 0, 4, 1),
    ):
        for port in range(count):
            address = base + port * 0x10000 + register
            tx = transferred(address, first_request + 2 * port, False, minimum)
            rx = transferred(address, first_request + 2 * port + 1, True, minimum)
            if not tx or not rx:
                errors.append(f"{kind}{port}: missing DMA TX/RX bus evidence")
            if kind != "uart":
                for length in (64, 4099):
                    if not re.search(rf"APOLLO_DMA350\|{kind}={port}\|bytes={length}\|.*status=PASS", guest_log):
                        errors.append(f"{kind}{port}: missing {length}-byte guest comparison")
                if kind == "spi" and (tx < 4099 or rx < 4099):
                    errors.append(f"spi{port}: insufficient DMA data for long transfer")
                if not re.search(rf"APOLLO_DMA350\|spi={port}\|bytes=4099\|vmalloc=1\|status=PASS", guest_log):
                    errors.append(f"spi{port}: missing vmalloc scatter-gather comparison")
                # The AP kernel uses 4K pages. Aligned vmalloc 4099-byte
                # buffers exercise at least a 4096-byte + 3-byte SG pair.
                for receive, request in ((False, 2 * port), (True, 2 * port + 1)):
                    sizes = {op["bytes"] for op in operations
                             if op["source" if receive else "dest"] == address
                             and op["src_trigger" if receive else "dst_trigger"] == request
                             and op["status"] == "done"}
                    if not {4096, 3} <= sizes:
                        errors.append(f"spi{port}: missing completed SG command pair, receive={receive}")
            else:
                peer = port ^ 1
                source = f"{base + port * 0x10000:x}"
                target = f"{base + peer * 0x10000:x}"
                for length in (17, 128, 512, 4099):
                    if not re.search(rf"APOLLO_DMA350\|uart={source}->{target}\|bytes={length}\|.*\|status=PASS", guest_log):
                        errors.append(f"uart{port}: missing {length}-byte guest comparison")
            ports.append(dict(kind=kind, port=port, tx_bytes=tx, rx_bytes=rx))
    return dict(status="FAIL" if errors else "PASS", errors=errors,
                memory_operations=len(memory), operations=len(operations), ports=ports)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guest-log", required=True, type=Path)
    parser.add_argument("--qbox-log", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = evaluate(args.guest_log.read_text(errors="replace"),
                      args.qbox_log.read_text(errors="replace"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
