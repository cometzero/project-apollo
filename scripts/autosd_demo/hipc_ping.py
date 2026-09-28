#!/usr/bin/env python3
"""Three bounded AP-initiated ICMP round trips; not SI-initiated qualification."""
import argparse
import json
import os
import select
import socket
import struct
import time


def checksum(data):
    if len(data) & 1:
        data += b"\0"
    total = sum(struct.unpack("!%dH" % (len(data) // 2), data))
    while total >> 16:
        total = (total & 0xffff) + (total >> 16)
    return (~total) & 0xffff


def echo_request(identifier, sequence, payload):
    header = struct.pack("!BBHHH", 8, 0, 0, identifier, sequence)
    return struct.pack("!BBHHH", 8, 0, checksum(header + payload),
                       identifier, sequence) + payload


def valid_reply(packet, peer, source, identifier, sequence, payload):
    if len(packet) < 28 or packet[0] >> 4 != 4:
        return False
    ihl = (packet[0] & 15) * 4
    length = struct.unpack_from("!H", packet, 2)[0]
    if ihl < 20 or length != len(packet) or length < ihl + 8:
        return False
    # Reject fragments; kernel normally reassembles them before raw delivery.
    if struct.unpack_from("!H", packet, 6)[0] & 0x3fff:
        return False
    if packet[9] != socket.IPPROTO_ICMP or checksum(packet[:ihl]) != 0:
        return False
    if packet[12:16] != socket.inet_aton(peer) or packet[16:20] != socket.inet_aton(source):
        return False
    message = packet[ihl:]
    kind, code, _, got_id, got_seq = struct.unpack_from("!BBHHH", message)
    return (kind == 0 and code == 0 and got_id == identifier and
            got_seq == sequence and checksum(message) == 0 and
            message[8:] == payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interface", default="ethsi1.200")
    parser.add_argument("--source", default="192.168.1.2")
    parser.add_argument("--peer", default="192.168.1.1")
    parser.add_argument("--timeout", type=float, default=5.0,
                        help="Monotonic receive deadline per packet (0 < seconds <= 30)")
    args = parser.parse_args()
    if not 0 < args.timeout <= 30:
        parser.error("timeout must be in (0, 30]")
    identifier = os.getpid() & 0xffff
    nonce = os.urandom(16)
    results = []
    report = {"status": "FAIL", "qualification": "AP-initiated ICMP request and SI reply only",
              "interface": args.interface, "source": args.source, "peer": args.peer,
              "boot_id": open("/proc/sys/kernel/random/boot_id").read().strip(),
              "packets": results}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as channel:
            channel.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE,
                               args.interface.encode() + b"\0")
            channel.bind((args.source, 0))
            channel.setblocking(False)
            for sequence in range(1, 4):
                payload = b"apollo-hipc-echo:" + nonce + struct.pack("!H", sequence)
                request = echo_request(identifier, sequence, payload)
                start = time.monotonic()
                sent = channel.sendto(request, (args.peer, 0))
                if sent != len(request):
                    raise OSError("short ICMP send")
                deadline = start + args.timeout
                entry = {"sequence": sequence, "status": "TIMEOUT"}
                while time.monotonic() < deadline:
                    ready, _, _ = select.select([channel], [], [], max(0, deadline - time.monotonic()))
                    if not ready:
                        break
                    try:
                        packet, address = channel.recvfrom(65535)
                    except BlockingIOError:
                        continue
                    if address[0] == args.peer and valid_reply(packet, args.peer, args.source,
                                                               identifier, sequence, payload):
                        entry = {"sequence": sequence, "status": "PASS",
                                 "rtt_ms_guest_monotonic": round((time.monotonic() - start) * 1000, 3)}
                        break
                results.append(entry)
                print(json.dumps({"event": "icmp-result", **entry}), flush=True)
            if all(entry["status"] == "PASS" for entry in results):
                report["status"] = "PASS"
    except OSError as error:
        report["error"] = str(error)
    print(json.dumps(report, sort_keys=True), flush=True)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

