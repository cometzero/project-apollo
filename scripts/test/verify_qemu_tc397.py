#!/usr/bin/env python3
"""Build and exercise the TC397 CPU0 functional subset using real guest code."""

import argparse
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import time


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "build/qbox-apollo-qvp/tc397-minimal/validation"
SOURCE = ROOT / "hsoc-stack/tools/qemu/tests/tcg/tricore/tc397"
CHECKS = (
    "reset-state", "cpu-reset-state", "dspr-alias", "pspr-alias", "flash-alias",
    "flash-readonly", "stm-counter", "global-mask", "pipn-readonly",
    "priority-threshold",
    "pending-low-priority", "source-disable", "source-reenable",
    "priority-zero-masked", "priority-order", "stm-five-irqs",
    "stm-disable", "uart-rx-irq-wait", "uart-tx-echo",
)


def digest(path):
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def connect(path, child, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if child.poll() is not None:
            raise RuntimeError(f"QEMU exited with status {child.returncode}")
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(str(path))
            sock.settimeout(timeout)
            return sock
        except (FileNotFoundError, ConnectionRefusedError):
            sock.close()
            time.sleep(0.05)
    raise TimeoutError(f"socket did not appear: {path}")


class QMP:
    def __init__(self, sock, log):
        self.stream = sock.makefile("rwb")
        self.log = log
        greeting = self.receive()
        if "QMP" not in greeting:
            raise RuntimeError(f"invalid QMP greeting: {greeting}")
        self.execute("qmp_capabilities")

    def receive(self):
        raw = self.stream.readline()
        if not raw:
            raise RuntimeError("QMP connection closed")
        value = json.loads(raw)
        self.log.write(json.dumps({"receive": value}) + "\n")
        self.log.flush()
        return value

    def execute(self, command):
        value = {"execute": command}
        self.log.write(json.dumps({"send": value}) + "\n")
        self.log.flush()
        self.stream.write(json.dumps(value).encode() + b"\n")
        self.stream.flush()
        while True:
            response = self.receive()
            if "error" in response:
                raise RuntimeError(f"QMP {command}: {response['error']}")
            if "return" in response:
                return response["return"]


def receive_until(sock, needle, data, log, child, timeout):
    deadline = time.monotonic() + timeout
    while needle not in data:
        if b"TC397:FAIL:" in data:
            raise RuntimeError("guest firmware reported FAIL (see serial.log)")
        if child.poll() is not None:
            raise RuntimeError(f"QEMU exited with status {child.returncode}")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(f"waiting for {needle.decode().strip()}")
        sock.settimeout(min(remaining, 0.5))
        try:
            chunk = sock.recv(4096)
        except socket.timeout:
            continue
        if not chunk:
            raise RuntimeError("UART connection closed")
        data += chunk
        log.write(chunk)
        log.flush()
    return data


def run(args, result):
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    firmware = output / "tc397-minimal.elf"
    cc = args.cc.resolve()
    qemu = args.qemu.resolve()
    compile_command = [
        str(cc), "-mtc162", "-Os", "-ffreestanding", "-fno-builtin",
        "-nostdlib", "-msmall=1", "-mabs=1", "-Wall", "-Wextra", "-Werror",
        "-Wl,-T," + str(SOURCE / "link.ld"), "-Wl,--build-id=none",
        "-o", str(firmware), str(SOURCE / "boot.S"),
        str(SOURCE / "firmware.c"),
    ]
    result["build_command"] = compile_command
    with (output / "firmware-build.log").open("wb") as log:
        subprocess.run(compile_command, stdout=log, stderr=subprocess.STDOUT,
                       check=True, timeout=60)
    result["firmware_build"] = "PASS"
    result["provenance"] = {
        "qemu": {"path": str(qemu), "sha256": digest(qemu)},
        "firmware": {
            "path": str(firmware), "sha256": digest(firmware),
            "elf_entry": hex(int.from_bytes(
                firmware.read_bytes()[24:28], "little")),
        },
        "sources": {name: digest(SOURCE / name)
                    for name in ("boot.S", "firmware.c", "link.ld")},
        "compiler": subprocess.check_output(
            [str(cc), "--version"], text=True, timeout=10).splitlines()[0],
        "runner_sha256": digest(Path(__file__).resolve()),
    }
    with tempfile.TemporaryDirectory(prefix="tc397-") as scratch:
        scratch = Path(scratch)
        qmp_path = scratch / "qmp.sock"
        uart_path = scratch / "uart.sock"
        command = [
            str(qemu), "-M", "KIT_AURIX_TC397B_TRB", "-display", "none",
            "-monitor", "none", "-chardev",
            f"socket,id=uart,path={uart_path},server=on,wait=off",
            "-serial", "chardev:uart", "-qmp",
            f"unix:{qmp_path},server=on,wait=off", "-S",
            "-kernel", str(firmware),
        ]
        result["qemu_command"] = command
        with (output / "qemu.log").open("wb") as qemu_log, \
                (output / "serial.log").open("wb") as serial_log, \
                (output / "qmp.jsonl").open("w") as qmp_log:
            child = subprocess.Popen(command, stdout=qemu_log,
                                     stderr=subprocess.STDOUT)
            try:
                with connect(qmp_path, child, args.timeout) as qmp_socket, \
                        connect(uart_path, child, args.timeout) as uart_socket:
                    qmp = QMP(qmp_socket, qmp_log)
                    qmp.execute("cont")
                    for cycle in range(2):
                        data = receive_until(
                            uart_socket, b"TC397:READY:RX\n", b"", serial_log,
                            child, args.timeout)
                        # Ensure firmware reaches WAIT before external RX.
                        time.sleep(0.05)
                        uart_socket.sendall(b"V")
                        data = receive_until(
                            uart_socket, b"TC397:DONE\n", data, serial_log,
                            child, args.timeout)
                        text = data.decode("ascii", errors="replace")
                        lines = text.splitlines()
                        checks = {name: "PASS" if f"TC397:PASS:{name}" in lines
                                  else "FAIL" for name in CHECKS}
                        checks["boot"] = ("PASS" if "TC397:BOOT" in lines
                                          else "FAIL")
                        checks["host-rx-echo"] = (
                            "PASS" if "TC397:ECHO:V" in lines else "FAIL")
                        if "TC397:FAIL:" in text:
                            raise RuntimeError("guest reported failure")
                        result["cycles"].append({
                            "name": "cold-boot" if cycle == 0 else "qmp-reset",
                            "checks": checks,
                        })
                        if any(value != "PASS" for value in checks.values()):
                            raise RuntimeError("missing guest checks")
                        if cycle == 0:
                            qmp.execute("system_reset")
                    qmp.execute("quit")
                    child.wait(timeout=5)
                    if child.returncode != 0:
                        raise RuntimeError(f"QEMU exit {child.returncode}")
            finally:
                if child.poll() is None:
                    child.terminate()
                    try:
                        child.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        child.kill()
                        child.wait(timeout=5)
    result["status"] = "PASS"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qemu", type=Path, required=True)
    parser.add_argument("--cc", type=Path, default=ROOT / (
        "build/qbox-apollo-qvp/tc397-minimal/toolchain/bin/tricore-gcc"))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=float, default=10,
                        help="Seconds per bounded guest phase")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    result = {
        "schema": "tc397-minimal-functional-v1", "status": "FAIL",
        "firmware_build": "FAIL", "cycles": [],
        "limitations": {
            "zephyr-mcal-vendor-firmware": "SKIP",
            "multicore-can-spi-ethernet-scu-pmic": "UNSUPPORTED",
            "lockstep-smu-watchdog-safety-timing-parity": "UNSUPPORTED",
            "apollo-qbox-integration": "SKIP",
        },
    }
    try:
        run(args, result)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        result["error"] = str(error)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "result.json").write_text(
        json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"],
                      "result": str((args.output / "result.json").resolve()),
                      "error": result.get("error")}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
