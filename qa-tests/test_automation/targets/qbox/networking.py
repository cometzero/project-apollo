# SPDX-License-Identifier: MIT
"""Live QBox UART/SSH adapter for the sw-ref-stack manager interface.

Ports are stable local handles, not TCP ports. AP and SSH return guest exit
codes; firmware consoles return response status (0/1), not a firmware exit
code. All transports reserve 124 for a deadline and 125 for a lost transport.
"""
from __future__ import annotations

import errno
import json
import logging
import math
import os
from pathlib import Path
import re
import shlex
import socket
import stat
import threading
import time
import uuid

from test_automation.utils.networking_base import BaseNetworkManager


LOGS = {
    "rse": "qbox-rse.log", "si_cl0": "qbox-safety-island-cl0.log",
    "si_cl1": "qbox-safety-island-cl1.log", "secure": "qbox-secure-console.log",
    "ap": "qbox-primary-console.log", "ssh": "qbox-ssh.log",
}
FIFOS = {
    "rse": "rse-uart-input.fifo", "si_cl0": "si-cl0-uart-input.fifo",
    "si_cl1": "si-cl1-uart-input.fifo", "secure": "secure-uart-input.fifo",
    "ap": "primary-uart-input.fifo",
}
SI1_PROMPT = r"(?m)(?:^|\n)(?:(?:uart:)?~\$\s*)+$"
AP_SHELL = r"(?m)(?:^|\n)(?:root@apollo-qvp[^\n]*[#>]|\S+ #)\s*$"
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
logger = logging.getLogger(__name__)


def _clean(text):
    return ANSI.sub("", text).replace("\r", "")


def positive_timeout(value):
    timeout = float(value)
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Timeout must be finite and positive")
    return timeout


class QBoxNetworkManager(BaseNetworkManager):
    def __init__(self, platform_config, config=None):
        self.platform_config = platform_config
        self.config = config
        self.terminal_to_port = {name: index for index, name in enumerate(LOGS, 1)}
        self.log_dir = None
        self.ssh_port = None
        self.is_running = lambda: True
        self.command_records = []
        self.command_completion_patterns = {}
        self._locks = {name: threading.Lock() for name in LOGS}
        self._connected = False
        self._ssh_transport = None

    def bind(self, log_dir, ssh_port, is_running):
        self.disconnect()
        self.log_dir = Path(log_dir)
        self.ssh_port = ssh_port
        self.is_running = is_running
        self.command_completion_patterns.clear()

    def set_log_dir(self, path):
        self.log_dir = Path(path)

    def connect(self):
        if self.log_dir is None:
            raise RuntimeError("QBox generation has not been prepared")
        self._connected = True

    def disconnect(self):
        self._connected = False
        if self._ssh_transport is not None:
            self._ssh_transport.close()
            self._ssh_transport = None

    def get_port(self, name):
        name = self.platform_config.get("port_map", {}).get(name, name)
        return self.terminal_to_port[name]

    def _domain(self, port):
        if isinstance(port, str):
            port = self.get_port(port)
        for name, handle in self.terminal_to_port.items():
            if handle == port:
                return name
        raise ValueError(f"Unknown QBox console handle: {port}")

    def log_path(self, port):
        if self.log_dir is None:
            raise RuntimeError("QBox generation has not been prepared")
        return self.log_dir / LOGS[self._domain(port)]

    def read_log(self, port):
        """Return normalized text; fresh-slice cursors use this same view."""
        try:
            return _clean(self.log_path(port).read_text(encoding="utf-8", errors="replace"))
        except FileNotFoundError:
            return ""

    def wait_for_prompt_in_log(self, port, prompt, timeout, regex=False, ignore_case=False):
        timeout = positive_timeout(timeout)
        pattern = re.compile(prompt if regex else re.escape(prompt), re.I if ignore_case else 0)
        deadline = time.monotonic() + timeout
        while True:
            if pattern.search(_clean(self.read_log(port))):
                return True
            if not self.is_running() or time.monotonic() >= deadline:
                return False
            time.sleep(min(.05, max(0, deadline - time.monotonic())))

    def _write(self, domain, payload, deadline):
        path = self.log_dir / FIFOS[domain]
        while True:
            try:
                descriptor = os.open(path, os.O_WRONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
                break
            except OSError as error:
                if error.errno not in (errno.ENOENT, errno.ENXIO):
                    raise
                if not self.is_running():
                    raise ConnectionError("QBox stopped before UART input") from error
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"UART input unavailable: {domain}") from error
                time.sleep(.02)
        try:
            if not stat.S_ISFIFO(os.fstat(descriptor).st_mode):
                raise ValueError(f"UART input is not a FIFO: {path}")
            if len(payload) > os.fpathconf(descriptor, "PC_PIPE_BUF"):
                raise ValueError("UART command exceeds atomic FIFO write size")
            while True:
                try:
                    if os.write(descriptor, payload) != len(payload):
                        raise ConnectionError("Incomplete UART command write")
                    return
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("UART input is full")
                    time.sleep(.02)
        finally:
            os.close(descriptor)

    def _capture(self, domain, cursor, complete, deadline):
        while True:
            fresh = _clean(self.read_log(domain)[cursor:])
            result = complete(fresh)
            if result is not None:
                return result
            if not self.is_running():
                return 125, fresh
            if time.monotonic() >= deadline:
                return 124, fresh
            time.sleep(min(.05, max(0, deadline - time.monotonic())))

    def _ap(self, command, deadline):
        nonce = uuid.uuid4().hex
        begin, end = "__QBOX_BEGIN_" + nonce, "__QBOX_END_" + nonce
        # Splitting marker arguments prevents the terminal's command echo from
        # containing a complete marker. A subshell isolates 'exit' and comments
        # while eval preserves the login shell's syntax (including Bash <<<).
        wire = (f"printf '\\n%s%s\\n' '__QBOX_BEGIN_' '{nonce}'; "
                f"( eval {shlex.quote(command)} ); __qbox_rc=$?; "
                f"printf '\\n%s%s:%d\\n' '__QBOX_END_' '{nonce}' \"$__qbox_rc\"\n")
        cursor = len(self.read_log("ap"))
        self._write("ap", wire.encode(), deadline)
        pattern = re.compile(rf"(?ms)^{begin}\n(.*?)^{end}:(\d+)\s*$")

        def completed(text):
            match = pattern.search(text)
            return (int(match[2]), match[1].strip()) if match else None

        return self._capture("ap", cursor, completed, deadline)

    def _firmware(self, domain, port, command, deadline):
        if re.fullmatch(r"[\x20-\x7e]{1,512}", command) is None:
            raise ValueError("Firmware commands must be 1-512 printable ASCII characters")
        cursor = len(self.read_log(domain))
        payload = command.encode() + b"\n"
        if domain == "si_cl0":
            payload = b"\x05" + payload + b"\x04"
        self._write(domain, payload, deadline)
        completion = self.command_completion_patterns.get((port, command))
        extra = re.compile(completion) if completion else None

        def completed(text):
            if domain == "si_cl0":
                start = text.find("[CLI_DEBUGGER_MODULE] Entering CLI")
                end = text.find("[CLI_DEBUGGER_MODULE] Exiting CLI", start)
                if start < 0 or end < 0:
                    return None
                # Some SCP tests queue their output and print it after Ctrl-D
                # has closed the CLI. Include that fresh output, while the
                # optional completion regex still bounds asynchronous results.
                body = text[start:].partition("\n")[2]
                body = body.replace("[CLI_DEBUGGER_MODULE] Exiting CLI", "")
            else:
                prompt = re.search(SI1_PROMPT, text)
                if prompt is None:
                    return None
                body = text[:prompt.start()]
            if extra is not None and extra.search(text) is None:
                return None
            # Echo and prompts alone do not demonstrate command execution.
            lines = [line.strip() for line in body.splitlines()]
            lines = [line for line in lines if line and line != command
                     and line not in (">", "$", "#")
                     and not line.endswith("~$ " + command)
                     and not line.endswith("> " + command)]
            error = re.search(r"CONSOLE ERROR:|unknown command|command not found|"
                              r"invalid (?:argument|command)|(?:^|\n)\s*error[: ]", body, re.I)
            return (1 if error or not lines else 0), text

        return self._capture(domain, cursor, completed, deadline)

    def _ssh(self, command, deadline):
        import paramiko

        remaining = lambda: max(.001, deadline - time.monotonic())
        transport = None
        channel = None
        watchdog = None
        chunks = []
        sock = socket.create_connection(("127.0.0.1", self.ssh_port), timeout=remaining())
        try:
            transport = paramiko.Transport(sock)
            self._ssh_transport = transport
            # Paramiko's channel request wait is not bounded by settimeout().
            # Closing the transport also bounds handshake/auth/exec requests.
            watchdog = threading.Timer(remaining(), transport.close)
            watchdog.daemon = True
            watchdog.start()
            transport.start_client(timeout=remaining())
            key = transport.get_remote_server_key()
            host = f"[127.0.0.1]:{self.ssh_port}"
            known = self.log_dir / "ssh-known-hosts"
            keys = paramiko.HostKeys()
            if known.exists():
                keys.load(str(known))
                if host in keys and not keys.check(host, key):
                    raise ConnectionError("QBox SSH host key changed within this generation")
            # Trust only this generation's local guest, never global host keys.
            if host not in keys:
                keys.add(host, key.get_name(), key)
                fd = os.open(known, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                os.close(fd)
                keys.save(str(known))
            transport.auth_timeout = remaining()
            username = self.platform_config.get("ssh_username", "root")
            password = self.platform_config.get("ssh_password", "")
            try:
                transport.auth_none(username)
            except paramiko.AuthenticationException:
                transport.auth_timeout = remaining()
                transport.auth_password(username, password)
            channel = transport.open_session(timeout=remaining())
            channel.settimeout(remaining())
            channel.exec_command(command)
            while True:
                while channel.recv_ready() and time.monotonic() < deadline:
                    chunks.append(channel.recv(65536))
                while channel.recv_stderr_ready() and time.monotonic() < deadline:
                    chunks.append(channel.recv_stderr(65536))
                if channel.exit_status_ready() and not channel.recv_ready() and not channel.recv_stderr_ready():
                    rc = channel.recv_exit_status()
                    return (rc if rc >= 0 else 125), b"".join(chunks).decode("utf-8", "replace")
                if time.monotonic() >= deadline:
                    return 124, b"".join(chunks).decode("utf-8", "replace")
                if not transport.is_active() or not self.is_running():
                    return 125, b"".join(chunks).decode("utf-8", "replace")
                time.sleep(min(.02, remaining()))
        except paramiko.SSHException as error:
            return (124 if time.monotonic() >= deadline else 125), str(error)
        finally:
            if watchdog is not None:
                watchdog.cancel()
            if channel is not None:
                channel.close()
            if transport is not None:
                transport.close()
            sock.close()
            self._ssh_transport = None

    def execute_command_with_prompt_capture(self, port, command, timeout=None):
        domain = self._domain(port)
        if domain not in ("ap", "si_cl0", "si_cl1", "ssh"):
            raise NotImplementedError(f"No command protocol for QBox console {domain}")
        if not isinstance(command, str) or not command.strip() or "\x00" in command:
            raise ValueError("Command must be a nonempty string without NUL")
        timeout = positive_timeout(timeout if timeout is not None else self.platform_config.get("command_timeout", 120))
        with self._locks[domain]:
            start = time.monotonic()
            logger.info("QBox %s command: %s", domain, command)
            try:
                if domain == "ap":
                    rc, output = self._ap(command, start + timeout)
                elif domain == "ssh":
                    rc, output = self._ssh(command, start + timeout)
                else:
                    rc, output = self._firmware(domain, self.get_port(domain), command, start + timeout)
            except (TimeoutError, socket.timeout) as error:
                rc, output = 124, str(error)
            except (ConnectionError, BrokenPipeError, OSError) as error:
                rc, output = 125, str(error)
            record = {"domain": domain, "command": command, "rc": rc, "output": output,
                      "duration_s": time.monotonic() - start,
                      "status_semantics": "guest_exit_code" if domain in ("ap", "ssh") else "firmware_response"}
            self.command_records.append(record)
            logger.info("QBox %s command rc=%d duration=%.3fs (%s)",
                        domain, rc, record["duration_s"], record["status_semantics"])
            with (self.log_dir / "commands.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record) + "\n")
            if domain == "ssh":
                with self.log_path("ssh").open("a", encoding="utf-8") as stream:
                    stream.write(output + "\n")
            return rc, output

    def run_cmd(self, port, cmd, timeout=None):
        rc, output = self.execute_command_with_prompt_capture(port, cmd, timeout)
        if rc:
            raise RuntimeError(f"Command failed rc={rc}: {cmd}\n{output}")
        return output.strip()

    def execute_simple_command(self, command, options=None, **kwargs):
        port = kwargs.get("port", self.get_port("ap"))
        timeout = kwargs.get("timeout", getattr(options, "timeout", None))
        return self.execute_command_with_prompt_capture(port, command, timeout)[0]

    def login_primary(self):
        timeout = positive_timeout(self.platform_config.get("boot_timeout", 600))
        if self.platform_config.get("image", "bsp") == "product":
            text = _clean(self.read_log("ap"))
            if not re.search(AP_SHELL, text):
                cursor = len(self.read_log("ap"))
                self._write("ap", b"root\n", time.monotonic() + timeout)
                rc, output = self._capture(
                    "ap", cursor,
                    lambda value: (0, value) if re.search(AP_SHELL, value) else None,
                    time.monotonic() + timeout,
                )
                if rc:
                    raise RuntimeError(f"QBox product login failed rc={rc}: {output}")
        # An executed nonce-marked command proves we reached a live shell.
        self.run_cmd(self.get_port("ap"), "true", timeout=timeout)
