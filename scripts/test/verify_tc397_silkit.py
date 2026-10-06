#!/usr/bin/env python3
"""Exercise a real TC397 Zephyr CAN driver through official SIL Kit participants.

The standalone run uses the explicit VehicleRestbus echo fixture. It does not
qualify SI0 control, physical CAN timing, or a physical CAN acknowledgement slot.
All processes and artifacts belong to this invocation; an existing output
directory is never reused.
"""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/run"))
from qbox_silkit import provider, environment


def digest(path):
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def events(path):
    found = []
    if path.exists():
        for line in path.read_text(errors="replace").splitlines():
            try:
                found.append(json.loads(line))
            except json.JSONDecodeError:
                # The producer may currently be writing its final line.
                continue
    return found


class Probe:
    def __init__(self, args, result):
        self.args, self.result = args, result
        self.out = args.out_dir
        self.deadline = time.monotonic() + args.timeout
        self.children, self.logs, self.sockets = {}, [], []
        self.console = bytearray()
        self.qmp_stream = None

    def remaining(self, limit=3):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("overall probe deadline expired")
        return min(remaining, limit)

    def alive(self):
        for name, item in self.children.items():
            if item["expected_alive"] and item["process"].poll() is not None:
                raise RuntimeError(f"{name} exited early: {item['process'].returncode}")

    def start(self, name, command):
        log = (self.out / f"{name}.log").open("xb")
        self.logs.append(log)
        argv = [str(value) for value in command]
        self.result["commands"].append({"name": name, "argv": argv})
        process = subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=subprocess.STDOUT,
                                   env=environment(self.args.sil_kit_library_path) if name != "qemu" else None)
        self.children[name] = {"process": process, "expected_alive": True}
        return process

    def stop(self, name):
        item = self.children[name]
        item["expected_alive"] = False
        process = item["process"]
        if process.poll() is None:
            process.terminate()
        code = process.wait(timeout=self.remaining(5))
        if code != 0:
            raise RuntimeError(f"{name} did not stop gracefully: {code}")

    def wait(self, description, predicate):
        while True:
            self.alive()
            try:
                self.remaining()
            except TimeoutError as error:
                raise TimeoutError(f"waiting for {description}") from error
            answer = predicate()
            if answer:
                return answer
            time.sleep(min(0.02, self.remaining()))

    def wait_event(self, name, event):
        return self.wait(f"{name}:{event}", lambda: next(
            (row for row in events(self.out / f"{name}.jsonl")
             if row.get("event") == event), None))

    def connect(self, path):
        while True:
            self.alive()
            sock = socket.socket(socket.AF_UNIX)
            sock.settimeout(self.remaining())
            try:
                sock.connect(str(path))
                self.sockets.append(sock)
                return sock
            except (FileNotFoundError, ConnectionRefusedError):
                sock.close()
                time.sleep(min(0.02, self.remaining()))

    def qmp(self, command):
        self.qmp_socket.settimeout(self.remaining())
        self.qmp_stream.write(json.dumps({"execute": command}).encode() + b"\n")
        self.qmp_stream.flush()
        while True:
            raw = self.qmp_stream.readline()
            if not raw:
                raise RuntimeError("QMP closed")
            reply = json.loads(raw)
            with (self.out / "qmp.jsonl").open("a") as log:
                log.write(json.dumps({"command": command, "reply": reply}) + "\n")
            if "error" in reply:
                raise RuntimeError(f"QMP {command}: {reply['error']}")
            if "return" in reply:
                return reply["return"]

    def console_wait(self, pattern, offset=0):
        # Require a complete line: UART packets can split inside counters/errno.
        expression = re.compile(pattern + r"[^\r\n]*\r?\n")
        while True:
            self.alive()
            match = expression.search(self.console[offset:].decode(errors="replace"))
            if match:
                return match.group(0).strip()
            self.shell.settimeout(self.remaining(0.1))
            try:
                chunk = self.shell.recv(4096)
            except socket.timeout:
                continue
            if not chunk:
                raise RuntimeError(f"console closed while waiting for {pattern}")
            self.console.extend(chunk)
            with (self.out / "shell.log").open("ab") as log:
                log.write(chunk)

    def cli(self, command, expected):
        offset = len(self.console)
        self.result["console_commands"].append(command)
        self.shell.settimeout(self.remaining())
        self.shell.sendall(command.encode() + b"\n")
        return self.console_wait(expected, offset)

    def check(self, name, condition=True):
        if not condition:
            raise AssertionError(name)
        self.result["checks"][name] = "PASS"

    def can_status(self):
        line = self.cli("vmcu-cli can status", "VMCU_CAN_STATUS")
        match = re.search(r"state=(\d+) rx=(\d+) tx=(\d+) tx_errors=(\d+)", line)
        if not match:
            raise RuntimeError(f"invalid CAN status: {line}")
        self.result["guest_status"].append(line)
        return tuple(int(value) for value in match.groups())

    def run(self):
        args = self.args
        self.result["artifacts"] = {
            name: {"path": str(path), "sha256": digest(path)}
            for name, path in (("qemu", args.qemu), ("firmware", args.firmware),
                               ("participant", args.participant), ("registry", args.registry))
        }
        with tempfile.TemporaryDirectory(prefix="tc397-silkit-") as tmp:
            # A short Unix socket directory avoids AF_UNIX path length limits.
            self.result["socket_directory"] = tmp
            with socket.socket() as reservation:
                reservation.bind(("127.0.0.1", 0))
                port = reservation.getsockname()[1]
            self.start("qemu", [args.qemu, "-M", "KIT_AURIX_TC397B_TRB",
                "-display", "none", "-monitor", "none", "-S", "-kernel", args.firmware,
                "-serial", "null", "-serial", f"unix:{tmp}/shell,server=on,wait=off",
                "-serial", "null", "-qmp", f"unix:{tmp}/qmp,server=on,wait=off",
                "-chardev", f"socket,id=can,host=127.0.0.1,port={port},server=on,wait=off",
                "-global", "tc397-can.chardev=can"])
            self.shell = self.connect(Path(tmp) / "shell")
            self.qmp_socket = self.connect(Path(tmp) / "qmp")
            self.qmp_stream = self.qmp_socket.makefile("rwb")
            if "QMP" not in json.loads(self.qmp_stream.readline()):
                raise RuntimeError("invalid QMP greeting")
            self.qmp("qmp_capabilities")
            self.start("registry", [args.registry, "-u", "silkit://127.0.0.1:0",
                       "-g", self.out / "registry.yaml", "-l", "warn"])

            def registry_uri():
                path = self.out / "registry.yaml"
                match = re.search(r"silkit://127\.0\.0\.1:\d+",
                                  path.read_text() if path.exists() else "")
                return match.group(0) if match else None

            uri = self.wait("registry configuration", registry_uri)
            self.result["registry_uri"] = uri
            base = [args.participant, "--registry-uri", uri, "--duration-ms",
                    str(math.ceil(args.timeout + 10) * 1000)]
            self.start("restbus", base + ["--role", "restbus", "--echo-fixture",
                       "--require-peer", "TC397CanBridge", "--events", self.out / "restbus.jsonl"])
            bridge = base + ["--role", "bridge", "--qemu-endpoint", f"127.0.0.1:{port}",
                             "--require-peer", "VehicleRestbus"]
            self.start("bridge", bridge + ["--events", self.out / "bridge.jsonl"])
            for name in ("bridge", "restbus"):
                self.wait_event(name, "participant_ready")
                self.wait_event(name, "peer_running")
            self.check("official-registry-real-CAN-participants")
            self.qmp("cont")
            self.console_wait("VMCU_CAN_INIT result=PASS")
            self.check("actual-zephyr-MCAN-initialization")
            self.cli("vmcu-cli can trace on", "VMCU_CAN_TRACE on")
            classic = bytes(range(8)).hex()
            self.cli(f"vmcu-cli can send 0x123 0 {classic}",
                     f"VMCU_CAN_RX id=0x321 flags=0x0 dlc=8 data={classic}")
            self.check("classic-guest-to-restbus-and-RX-IRQ")
            fd = bytes(range(64)).hex()
            self.cli(f"vmcu-cli can send 0x1abcde 13 {fd}",
                     f"VMCU_CAN_RX id=0x1abcdf flags=0xd dlc=15 data={fd}")
            self.check("extended-FD64-BRS-guest-roundtrip")
            self.check("guest-RX-and-TX-interrupt-callbacks", self.can_status() == (0, 2, 2, 0))

            self.stop("bridge")
            self.wait("guest BUS_OFF after disconnect", lambda: self.can_status()[0] == 3)
            self.check("disconnect-visible-guest-BUS-OFF")
            failed = self.cli("vmcu-cli can send 0x123 0 0102", "VMCU_CAN_SEND")
            # Embedded libc errno values need not equal Linux host errno values.
            self.check("disconnected-send-fails", re.search(r"errno=-[1-9][0-9]*", failed))
            self.start("bridge-reconnect", bridge + ["--events", self.out / "bridge-reconnect.jsonl"])
            self.wait_event("bridge-reconnect", "participant_ready")
            self.wait_event("bridge-reconnect", "peer_running")
            self.wait_event("bridge-reconnect", "controller_stopped")
            self.cli("vmcu-cli can restart", "VMCU_CAN_RESTART errno=0")
            self.cli("vmcu-cli can send 0x123 0 deadbeef",
                     "VMCU_CAN_RX id=0x321 flags=0x0 dlc=4 data=deadbeef")
            self.check("guest-controller-restart-and-recovery", self.can_status() == (0, 3, 3, 1))

            def callback_evidence():
                ack = events(self.out / "bridge.jsonl") + events(self.out / "bridge-reconnect.jsonl")
                received = events(self.out / "restbus.jsonl")
                expected = [(0x123, 0, classic), (0x1abcde, 13, fd), (0x123, 0, "deadbeef")]
                return all(
                    any(row.get("event") == "silkit_ack" and row.get("status") == 1 and
                        (row.get("id"), row.get("flags"), row.get("data")) == sample for row in ack)
                    and any(row.get("event") == "silkit_rx" and
                            (row.get("id"), row.get("flags"), row.get("data")) == sample
                            for row in received) for sample in expected)

            self.wait("actual SDK callbacks and restbus reception", callback_evidence)
            self.check("actual-SDK-ACK-and-remote-reception-evidence")

    def cleanup(self):
        errors = []
        if self.qmp_stream is not None:
            try:
                self.qmp_stream.close()
            except OSError as error:
                errors.append(f"QMP close: {error}")
        for sock in self.sockets:
            try:
                sock.close()
            except OSError as error:
                errors.append(f"socket close: {error}")
        for item in self.children.values():
            process = item["process"]
            if process.poll() is None:
                process.terminate()
        deadline = time.monotonic() + 5
        forced = []
        for name, item in reversed(list(self.children.items())):
            process = item["process"]
            try:
                process.wait(timeout=max(0.01, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                forced.append(name)
                process.kill()
                process.wait(timeout=3)
        self.result["cleanup"] = {
            "status": "PASS" if not forced and not errors else "FAIL",
            "forced_kills": forced, "errors": errors,
            "processes": {name: {"pid": item["process"].pid,
                                 "returncode": item["process"].returncode}
                          for name, item in self.children.items()},
        }
        for log in self.logs:
            log.close()
        if forced or errors:
            raise RuntimeError(f"process cleanup: forced={forced}, errors={errors}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True, help="new evidence directory")
    parser.add_argument("--qemu", type=Path, required=True,
                        help="tricore_executable from the qemu-apollo-native manifest")
    deploy = Path(os.environ.get("DEPLOY_DIR", str(
        Path(os.environ.get("YOCTO_BUILD_DIR", ROOT / "build")) /
        "tmp_baremetal/deploy/images" / os.environ.get("MACHINE", "apollo-qvp"))))
    parser.add_argument("--firmware", type=Path, default=Path(os.environ.get(
        "QBOX_TC397_FIRMWARE", deploy / "zephyr-vmcu-tc397.elf")))
    parser.add_argument("--participant", type=Path, default=None)
    parser.add_argument("--registry", type=Path, default=None)
    parser.add_argument("--timeout", type=float, default=45,
                        help="overall exercise deadline in seconds, followed by bounded cleanup")
    args = parser.parse_args()
    try:
        binary, registry, args.sil_kit_library_path = provider(
            deploy, args.participant, args.registry)
    except (ValueError, OSError, TypeError) as error:
        parser.error(str(error))
    args.participant, args.registry = Path(binary), Path(registry)
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be finite and positive")
    for name in ("out_dir", "qemu", "firmware", "participant", "registry"):
        setattr(args, name, getattr(args, name).resolve())
    try:
        args.out_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        parser.error("--out-dir already exists; refusing to overwrite evidence")
    result = {"status": "FAIL", "passed": False, "checks": {}, "commands": [],
              "console_commands": [], "guest_status": [], "timeout_seconds": args.timeout,
              "scope": "standalone real Zephyr CAN/SIL Kit; no SI0/AP actuation qualification",
              "runner_sha256": digest(Path(__file__))}
    probe = Probe(args, result)
    start = time.monotonic()
    try:
        probe.run()
        result.update(status="PASS", passed=True)
    except Exception as error:
        result["error"] = f"{type(error).__name__}: {error}"
    finally:
        try:
            probe.cleanup()
        except Exception as error:
            result.update(status="FAIL", passed=False, cleanup_error=str(error))
        result["elapsed_seconds"] = time.monotonic() - start
        (args.out_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": len(result["checks"]),
                      "result": str(args.out_dir / "result.json"), "error": result.get("error")}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
