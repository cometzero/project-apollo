#!/usr/bin/env python3
"""Own a TC397 UART peer for the lifetime of a foreground QBox runner."""

import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import select
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import time


class ConsoleBridge:
    """Feed the shell FIFO and record bytes actually received from its socket."""

    def __init__(self, path, fifo, logfile):
        self.socket = socket.socket(socket.AF_UNIX)
        self.fd = None
        self.log = None
        self.pending = bytearray()
        self.input_bytes = self.output_bytes = 0
        try:
            self.log = logfile.open("wb", buffering=0)
            self.socket.connect(str(path))
            self.socket.setblocking(False)
            if not fifo.exists():
                os.mkfifo(fifo)
            if not stat.S_ISFIFO(fifo.stat().st_mode):
                raise ValueError(f"console input must be a FIFO: {fifo}")
            self.fd = os.open(fifo, os.O_RDWR | os.O_NONBLOCK)
        except Exception:
            self.close()
            raise

    def drain(self, eof_error=True):
        # Bound each pass while draining bursts of single-byte ASCLIN writes.
        for _ in range(16):
            try:
                data = self.socket.recv(65536)
            except BlockingIOError:
                break
            if not data:
                if eof_error:
                    raise RuntimeError("TC397 shell UART disconnected")
                break
            self.log.write(data)
            self.output_bytes += len(data)

    def pump(self):
        self.drain()
        # Backpressure the FIFO reader instead of accumulating unbounded input.
        if len(self.pending) < 4096:
            try:
                self.pending.extend(os.read(self.fd, 4096 - len(self.pending)))
            except BlockingIOError:
                pass
        if self.pending:
            try:
                sent = self.socket.send(self.pending)
                self.input_bytes += sent
                del self.pending[:sent]
            except BlockingIOError:
                pass

    def close(self):
        try:
            if self.fd is not None:
                # The owner stops QEMU first; retain bytes queued before its exit.
                self.drain(eof_error=False)
        finally:
            self.socket.close()
            if self.fd is not None:
                os.close(self.fd)
                self.fd = None
            if self.log is not None:
                self.log.close()
                self.log = None


def identity(pid):
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        return int(fields[1]), fields[19], fields[0]
    except (OSError, IndexError, ValueError):
        return None


class OwnedProcesses:
    """Track only this child's descendants, with pidfds guarding PID reuse."""

    def __init__(self, process):
        self.process = process
        self.owned = {}
        self.add(process.pid, identity(process.pid))

    def add(self, pid, original):
        if original is None or pid in self.owned:
            return
        try:
            fd = os.pidfd_open(pid)
        except ProcessLookupError:
            return
        current = identity(pid)
        if current is None or current[1] != original[1]:
            os.close(fd)
            return
        self.owned[pid] = (original[1], fd)

    def discover(self):
        table = {int(path.name): identity(int(path.name))
                 for path in Path("/proc").iterdir() if path.name.isdecimal()}
        parents = {pid for pid, (start, _) in self.owned.items()
                   if table.get(pid) and table[pid][1] == start}
        while True:
            found = {pid for pid, entry in table.items()
                     if entry and entry[0] in parents and pid not in parents}
            if not found:
                break
            for pid in found:
                self.add(pid, table[pid])
            parents.update(found)

    def active(self):
        self.process.poll()
        return [pid for pid, (_, fd) in self.owned.items()
                if not select.select([fd], [], [], 0)[0]]

    def send(self, pid, signum):
        try:
            signal.pidfd_send_signal(self.owned[pid][1], signum)
        except ProcessLookupError:
            pass

    def stop(self, timeout):
        self.discover()
        forced = []
        # The canonical runner translates TERM into INT for its runtime, whose
        # finally block closes the QBox process in its separate session.
        if self.process.pid in self.active():
            self.send(self.process.pid, signal.SIGTERM)
        deadline = time.monotonic() + timeout
        while self.active() and time.monotonic() < deadline:
            self.discover()
            time.sleep(.05)
        for signum in (signal.SIGTERM, signal.SIGKILL):
            active = self.active()
            if not active:
                break
            for pid in reversed(active):
                self.send(pid, signum)
                forced.append({"pid": pid, "signal": int(signum)})
            deadline = time.monotonic() + 2
            while self.active() and time.monotonic() < deadline:
                self.discover()
                time.sleep(.05)
        residual = self.active()
        self.process.poll()
        return {"pid": self.process.pid, "owned_pids": list(self.owned),
                "returncode": self.process.returncode,
                "forced_signals": forced, "residual_pids": residual,
                "status": "FAIL" if residual else "PASS"}

    def close(self):
        for _, fd in self.owned.values():
            os.close(fd)


def endpoint_from_chardev(devices, label="tc397_uart"):
    for device in devices:
        if device.get("label") != label:
            continue
        match = re.fullmatch(r"disconnected:tcp:127\.0\.0\.1:(\d+),server=on",
                             device.get("filename", ""))
        if match and 0 < int(match[1]) <= 65535:
            return "127.0.0.1:" + match[1]
    raise RuntimeError(f"QMP did not report the TC397 loopback listener: {label}")


def wait_endpoint(path, process, timeout, stopped, with_can=False, resume=False):
    """Use QMP readiness; probing the UART would consume its one connection."""
    deadline = time.monotonic() + timeout
    with socket.socket(socket.AF_UNIX) as sock:
        while True:
            if stopped():
                raise InterruptedError("startup interrupted")
            if process.poll() is not None:
                raise RuntimeError(f"TC397 exited during startup ({process.returncode})")
            if time.monotonic() >= deadline:
                raise TimeoutError("TC397 QMP startup timed out")
            try:
                sock.connect(str(path))
                break
            except (FileNotFoundError, ConnectionRefusedError):
                time.sleep(.05)
        sock.settimeout(.2)
        pending = bytearray()

        def receive():
            while True:
                if stopped():
                    raise InterruptedError("startup interrupted")
                if time.monotonic() >= deadline:
                    raise TimeoutError("TC397 QMP response timed out")
                if b"\n" in pending:
                    line, _, rest = pending.partition(b"\n")
                    pending[:] = rest
                    return json.loads(line)
                try:
                    chunk = sock.recv(4096)
                except socket.timeout:
                    continue
                if not chunk:
                    raise RuntimeError("TC397 QMP closed during startup")
                pending.extend(chunk)
                if len(pending) > 65536:
                    raise RuntimeError("TC397 QMP response exceeded size limit")

        if "QMP" not in receive():
            raise RuntimeError("invalid TC397 QMP greeting")
        for command in ("qmp_capabilities", "cont" if resume else "query-chardev"):
            sock.sendall(json.dumps({"execute": command}).encode() + b"\n")
            while True:
                response = receive()
                if "error" in response:
                    raise RuntimeError(f"TC397 QMP {command}: {response['error']}")
                if "return" in response:
                    break
        if resume:
            return None
        labels = ("tc397_uart", "tc397_safety", "tc397gpio")
        if with_can:
            labels += ("tc397can",)
        return {label: endpoint_from_chardev(response["return"], label)
                for label in labels}


def write_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def supervise(args):
    output = args.out_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    # Refuse simultaneous writers before touching a previous run's evidence.
    with (output / "tc397.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return run(args, output)


def run(args, output):
    stop_signal = 0

    def stop_requested(signum, frame):
        nonlocal stop_signal
        stop_signal = signum

    previous = {sig: signal.signal(sig, stop_requested)
                for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
    started = time.monotonic()
    status = {"status": "STARTING", "supervisor_pid": os.getpid(),
              "qbox_command": args.command, "cleanup": []}
    status_path = output / "tc397-status.json"
    console = None
    silkit = None
    owners = []
    code = 1
    write_json(status_path, status)
    with tempfile.TemporaryDirectory(prefix="qbox-tc397-") as scratch, \
            (output / "tc397-supervisor.log").open("w", buffering=1) as supervisor_log, \
            (output / "tc397-qemu.log").open("wb") as qemu_log:
        raw_path = output / "tc397-link-tx.bin"
        raw_path.write_bytes(b"")
        uart_log = output / "tc397-uart.log"
        uart_log.write_bytes(b"")

        def message(text):
            supervisor_log.write(f"[host +{time.monotonic() - started:.3f}s] {text}\n")

        try:
            qmp = Path(scratch) / "qmp.sock"
            console_path = Path(scratch) / "console.sock"
            # char.c logs TX writes only (not RX), including fatal/disconnected
            # backend writes. No timestamp bytes may enter the raw wire log.
            logfile = str(raw_path).replace(",", ",,")
            command = [str(args.qemu.resolve()), "-M", "KIT_AURIX_TC397B_TRB",
                       "-S", "-display", "none", "-monitor", "none", "-chardev",
                       "socket,id=tc397_uart,host=127.0.0.1,port=0,server=on,"
                       f"wait=off,logfile={logfile},logappend=off",
                       "-serial", "chardev:tc397_uart",
                       "-chardev", f"socket,id=tc397_console,path={console_path},"
                       "server=on,wait=off", "-serial", "chardev:tc397_console",
                       "-chardev", "socket,id=tc397_safety,host=127.0.0.1,port=0,"
                       "server=on,wait=off,logfile=" +
                       str(output / "tc397-safety-tx.bin").replace(",", ",,") +
                       ",logappend=off", "-serial", "chardev:tc397_safety",
                       "-chardev", "socket,id=tc397gpio,host=127.0.0.1,port=0,"
                       "server=on,wait=off", "-global",
                       "tricore-port.chardev=tc397gpio", "-qmp",
                       f"unix:{qmp},server=on,wait=off", "-kernel",
                       str(args.firmware.resolve())]
            if args.sil_kit:
                command += ["-chardev", "socket,id=tc397can,host=127.0.0.1,"
                            "port=0,server=on,wait=off", "-global", "tc397-can.chardev=tc397can"]
            status["qemu_command"] = command
            message("Starting TC397 Zephyr; ASCLIN0 AP, ASCLIN1 shell, ASCLIN2 SI0, PORT0 GPIO.")
            qemu_env = os.environ.copy()
            if qemu_env.get("QBOX_TC397_LIBRARY_PATH"):
                qemu_env["LD_LIBRARY_PATH"] = qemu_env["QBOX_TC397_LIBRARY_PATH"]
            mcu = subprocess.Popen(command, env=qemu_env, stdout=qemu_log,
                                   stderr=subprocess.STDOUT, start_new_session=True)
            owners.append(OwnedProcesses(mcu))
            status["tc397_pid"] = mcu.pid
            write_json(status_path, status)
            endpoints = wait_endpoint(qmp, mcu, args.startup_timeout,
                                     lambda: stop_signal, with_can=args.sil_kit)
            endpoint = endpoints["tc397_uart"]
            status.update(uart_endpoint=endpoint,
                          safety_endpoint=endpoints["tc397_safety"],
                          gpio_endpoint=endpoints["tc397gpio"])
            console = ConsoleBridge(console_path, output / "tc397-uart-input.fifo", uart_log)
            status["console_fifo"] = str(output / "tc397-uart-input.fifo")
            message(f"ASCLIN0 listening on {endpoint}; raw TX: {raw_path}")
            if args.sil_kit:
                from qbox_silkit import SilKit
                silkit = SilKit(args, output, owners, OwnedProcesses, lambda: stop_signal)
                status["sil_kit"] = silkit.metadata
                silkit.start(endpoints["tc397can"])
                write_json(status_path, status)
                message("SIL Kit registry and CAN participants ready.")
            wait_endpoint(qmp, mcu, args.startup_timeout, lambda: stop_signal, resume=True)
            message("Console receiver connected; TC397 CPU resumed.")
            if stop_signal:
                raise InterruptedError("startup interrupted")
            env = dict(os.environ, QBOX_APOLLO_VMCU_UART_ENDPOINT=endpoint,
                       QBOX_APOLLO_VMCU_SAFETY_ENDPOINT=endpoints["tc397_safety"],
                       QBOX_APOLLO_VMCU_GPIO_ENDPOINT=endpoints["tc397gpio"])
            child = subprocess.Popen(args.command, env=env, start_new_session=True)
            owners.append(OwnedProcesses(child))
            status.update(status="RUNNING", qbox_pid=child.pid)
            write_json(status_path, status)
            next_discovery = 0
            while True:
                if stop_signal:
                    status["status"], code = "INTERRUPTED", 128 + stop_signal
                    break
                if mcu.poll() is not None:
                    # tmux F12 signals descendants as well as this supervisor;
                    # allow its simultaneous shutdown request to be delivered.
                    time.sleep(.05)
                    if stop_signal:
                        continue
                    raise RuntimeError(f"TC397 exited unexpectedly ({mcu.returncode})")
                console.pump()
                if silkit:
                    silkit.check()
                if child.poll() is not None:
                    code = child.returncode
                    code = code if code >= 0 else 128 - code
                    status["status"] = "EXITED" if code == 0 else "FAILED"
                    break
                if time.monotonic() >= next_discovery:
                    for owner in owners:
                        owner.discover()
                    next_discovery = time.monotonic() + .5
                time.sleep(.05)
        except InterruptedError:
            status["status"], code = "INTERRUPTED", 128 + stop_signal
        except Exception as error:
            status.update(status="FAILED", error=str(error))
            message(f"ERROR: {error}")
            print(f"TC397 companion: {error}", file=sys.stderr)
        finally:
            for owner in reversed(owners):
                try:
                    receipt = owner.stop(args.shutdown_timeout)
                    status["cleanup"].append(receipt)
                    if receipt["status"] != "PASS":
                        status["status"], code = "CLEANUP_FAILED", 1
                except Exception as error:
                    status["cleanup"].append({"status": "FAIL", "error": str(error)})
                    status["status"], code = "CLEANUP_FAILED", 1
                finally:
                    owner.close()
            if console is not None:
                console.close()
            if silkit is not None:
                silkit.close()
            status.update(returncode=code, signal=stop_signal,
                          elapsed_s=time.monotonic() - started,
                          link_tx_bytes=raw_path.stat().st_size,
                          console_input_bytes=console.input_bytes if console else 0,
                          console_output_bytes=console.output_bytes if console else 0)
            message(f"Stopped: {status['status']} (exit={code})")
            write_json(status_path, status)
            for sig, handler in previous.items():
                signal.signal(sig, handler)
    return code


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qemu", type=Path, required=True)
    parser.add_argument("--firmware", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--startup-timeout", type=float, default=15)
    parser.add_argument("--shutdown-timeout", type=float, default=30)
    from qbox_silkit import add_arguments, validate
    add_arguments(parser)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.command[:1] == ["--"]:
        args.command.pop(0)
    if not args.command:
        parser.error("a foreground QBox command is required after --")
    if args.startup_timeout <= 0 or args.shutdown_timeout <= 0:
        parser.error("timeouts must be positive")
    if not args.qemu.is_file() or not os.access(args.qemu, os.X_OK):
        parser.error(f"QEMU executable unavailable: {args.qemu}")
    if not args.firmware.is_file():
        parser.error(f"TC397 firmware unavailable: {args.firmware}")
    validate(args, parser)
    try:
        return supervise(args)
    except (OSError, RuntimeError) as error:
        print(f"TC397 companion: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
