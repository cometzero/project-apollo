#!/usr/bin/env python3
"""Bounded DMA-350/I2S register tests using production QEMU TCG and qtest I/O."""

import argparse
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import time


class Monitor:
    def __init__(self, path, process, log):
        self.socket = socket.socket(socket.AF_UNIX)
        self.socket.settimeout(5)
        deadline = time.monotonic() + 10
        while True:
            try:
                self.socket.connect(str(path))
                break
            except (FileNotFoundError, ConnectionRefusedError):
                if process.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError("QEMU monitor failed to start")
                time.sleep(0.05)
        self.stream = self.socket.makefile("rwb", buffering=0)
        self.log = log

    def send(self, text):
        self.log.write("> " + text + "\n")
        self.stream.write((text + "\n").encode())

    def line(self):
        line = self.stream.readline().decode().strip()
        self.log.write("< " + line + "\n")
        if not line:
            raise RuntimeError("QEMU monitor disconnected")
        return line

    def qmp(self, command):
        self.send(json.dumps({"execute": command}))
        while True:
            response = json.loads(self.line())
            if "error" in response:
                raise RuntimeError(response)
            if "return" in response:
                return response["return"]

    def io(self, command):
        self.send(command)
        response = self.line()
        if not response.startswith("OK"):
            raise RuntimeError(response)
        return response[2:].strip()

    def read(self, address):
        return int(self.io(f"readl {address:#x}"), 16)

    def write(self, address, value):
        self.io(f"writel {address:#x} {value:#x}")

    def close(self):
        self.stream.close()
        self.socket.close()


def exercise(io, qmp, results):

    def check(name, condition, **evidence):
        results.append({"test": name, "status": "PASS" if condition else "FAIL", **evidence})
        if not condition:
            raise AssertionError(results[-1])

    def advance():
        qmp.qmp("cont")
        time.sleep(0.02)
        qmp.qmp("stop")

    for base in (0x30200000, 0x30210000):
        check(f"i2s-{base:x}-identity", io.read(base + 0x1fc) == 0x445701a0)
        # Disabled serializer: 17 complete stereo frames exceed the 16-entry FIFO.
        for frame in range(17):
            io.write(base + 0x20, 0x12340000 + frame)
            io.write(base + 0x24, 0x56780000 + frame)
        status = io.read(base + 0x38)
        check(f"i2s-{base:x}-overflow", bool(status & 0x20), isr=status)
        check(f"i2s-{base:x}-overflow-read-clear", io.read(base + 0x44) == 1 and
              not (io.read(base + 0x38) & 0x20))
        io.write(base + 0x18, 1)
        check(f"i2s-{base:x}-fifo-flush", bool(io.read(base + 0x38) & 0x10))

    for source, destination in ((0x30200000, 0x30210000), (0x30210000, 0x30200000)):
        for base in (source, destination):
            io.write(base, 0)
            io.write(base + 4, 0)
            io.write(base + 8, 0)
            io.write(base, 1)
        frames = [(0x1234 + n, 0x5678 + n) for n in range(4)]
        io.write(destination + 0x28, 1)
        io.write(destination + 4, 1)
        for left, right in frames:
            io.write(source + 0x20, left)
            io.write(source + 0x24, right)
        io.write(source + 0x2c, 1)
        io.write(source + 8, 1)
        io.write(source + 0x0c, 1)
        advance()
        captured = [(io.read(destination + 0x20), io.read(destination + 0x24))
                    for _ in frames]
        check(f"i2s-{source:x}-to-{destination:x}-frames", captured == frames,
              expected=frames, captured=captured)
        check(f"i2s-{destination:x}-rx-empty", not (io.read(destination + 0x38) & 1))
    for base in (0x30200000, 0x30210000):
        io.write(base, 0)

    for base, intid in ((0x31000000, 311), (0x31010000, 390)):
        channel = base + 0x1000
        pending = 0x20800000 + 0x200 + (intid // 32) * 4
        mask = 1 << (intid % 32)
        check(f"dma-{base:x}-identity", io.read(base + 0xfc8) == 0x3a00043b)
        data = bytes((n * 73 + 19) & 255 for n in range(256))
        io.io(f"write 0x81000000 {len(data)} 0x{data.hex()}")
        io.io(f"memset 0x81001000 {len(data)} 0")
        io.write(base + 0x20c, 1)  # Combined interrupt output used by the board.
        io.write(channel + 8, 3)  # DONE and ERR interrupt enables.
        io.write(channel + 0x0c, 0x202)  # 32-bit, source/destination copy.
        io.write(channel + 0x10, 0x81000000)
        io.write(channel + 0x18, 0x81001000)
        io.write(channel + 0x20, (64 << 16) | 64)
        io.write(channel + 0x30, 0x10001)
        io.write(channel, 1)
        advance()
        copied = bytes.fromhex(io.io("read 0x81001000 256").removeprefix("0x"))
        status = io.read(channel + 4)
        check(f"dma-{base:x}-memcpy", copied == data and bool(status & 1),
              status_register=status, source_sha256=hashlib.sha256(data).hexdigest(),
              destination_sha256=hashlib.sha256(copied).hexdigest())
        check(f"dma-{base:x}-irq-assert", bool(io.read(pending) & mask))
        io.write(channel + 4, 1 << 16)
        check(f"dma-{base:x}-irq-clear", not (io.read(pending) & mask))
        # Unsupported transfer width must terminate and assert ERR, not copy data.
        io.write(channel + 0x0c, 0x207)
        io.write(channel, 1)
        check(f"dma-{base:x}-config-error", bool(io.read(channel + 4) & 2) and
              io.read(channel + 0x90) != 0 and bool(io.read(pending) & mask))
        io.write(channel, 2)
        check(f"dma-{base:x}-channel-clear", io.read(channel + 4) == 0 and
              io.read(channel + 0x90) == 0 and not (io.read(pending) & mask))
        # Keep a channel active waiting for an unused trigger; the Linux driver
        # changes interrupt enables before requesting STOP during termination.
        io.write(channel + 0x0c, (1 << 25) | 0x202)
        io.write(channel + 0x4c, 0xa07)
        io.write(channel + 0x10, 0x81000000)
        io.write(channel + 0x18, 0x81001000)
        io.write(channel + 0x20, 0x10001)
        io.write(channel, 1)
        io.write(channel + 8, 0xb)
        io.write(channel, 8)
        status = io.read(channel + 4)
        check(f"dma-{base:x}-active-intren-stop", bool(status & 8) and
              bool(io.read(pending) & mask), status_register=status)
        io.write(channel, 2)
        # A transfer targeting its own command register must report a bus error
        # without recursive channel-state mutation or a host crash.
        io.write(channel + 8, 3)
        io.write(channel + 0x0c, 0x202)
        io.write(channel + 0x10, 0x81000000)
        io.write(channel + 0x18, channel)
        io.write(channel + 0x20, 0x10001)
        io.write(channel, 1)
        advance()
        error = io.read(channel + 0x90)
        check(f"dma-{base:x}-self-target-bus-error", bool(io.read(channel + 4) & 2) and
              bool(error & (1 << 17)) and bool(io.read(pending) & mask), error_register=error)
        io.write(channel, 2)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qemu", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=False)
    result = {"status": "FAIL", "tests": []}
    with tempfile.TemporaryDirectory(prefix="apollo-qtest-") as temp, \
         (args.out_dir / "qemu.log").open("wb") as stderr, \
         (args.out_dir / "protocol.log").open("w") as log:
        temp = Path(temp)
        kernel = args.out_dir / "spin.bin"
        kernel.write_bytes(bytes.fromhex("00000014"))  # AArch64 b .
        command = [str(args.qemu.resolve()), "-machine", "apollo-qvp", "-accel", "tcg",
                   "-smp", "1", "-m", "256M", "-display", "none", "-serial", "null",
                   "-S", "-kernel", str(kernel.resolve()),
                   "-qtest", f"unix:{temp}/qtest,server=on,wait=off",
                   "-qmp", f"unix:{temp}/qmp,server=on,wait=off"]
        result["command"] = command
        with args.qemu.open("rb") as binary:
            result["qemu_sha256"] = hashlib.file_digest(binary, "sha256").hexdigest()
        process = subprocess.Popen(command, stdout=stderr, stderr=stderr)
        io = qmp = None
        try:
            io = Monitor(temp / "qtest", process, log)
            qmp = Monitor(temp / "qmp", process, log)
            qmp.line()
            qmp.qmp("qmp_capabilities")
            exercise(io, qmp, result["tests"])
            result["status"] = "PASS"
        except (AssertionError, OSError, RuntimeError, ValueError) as error:
            result["error"] = str(error)
        finally:
            for monitor in (io, qmp):
                if monitor:
                    monitor.close()
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    (args.out_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return result["status"] != "PASS"


if __name__ == "__main__":
    raise SystemExit(main())
