# SPDX-License-Identifier: MIT
"""Exercise the real tmux UI with a bounded fake simulator."""
import os
from pathlib import Path
import pty
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

import run_linux


@unittest.skipUnless(shutil.which("tmux"), "tmux is required")
class TmuxTests(unittest.TestCase):
    def test_uart_platform_log_and_f12_cleanup(self):
        session = f"gem5-test-{os.getpid()}"
        client = None
        master = slave = None
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            out = root / "output with spaces"
            fake = root / "fake-gem5"
            fake.write_text('''#!/usr/bin/env python3
import os, pathlib, socket, sys, time
args = dict(a[2:].split('=', 1) for a in sys.argv[1:] if a.startswith('--') and '=' in a)
out = pathlib.Path(args['outdir']).parent
(out / 'child.pid').write_text(str(os.getpid()))
print('GEM5_PLATFORM_READY', flush=True)
with socket.socket() as server:
    server.bind(('127.0.0.1', int(args['terminal-port'])))
    server.listen()
    connection, _ = server.accept()
    with connection:
        connection.sendall(b'UART_READY\\r\\n')
        data = connection.recv(1024)
        (out / 'input.txt').write_bytes(data)
        connection.sendall(b'UART_ECHO:' + data)
        time.sleep(60)
''')
            fake.chmod(0o755)
            archive = bytearray()
            run_linux.cpio_entry(archive, "TRAILER!!!", mode=0)
            initrd = root / "initrd"
            initrd.write_bytes(archive)
            fixture = root / "fixture"
            fixture.write_text("fixture")
            argv = [sys.executable, str(Path(run_linux.__file__)),
                    "--gem5", str(fake), "--kernel", str(fixture),
                    "--rootfs", str(fixture), "--profile", str(fixture),
                    "--bootloader", str(fixture), "--initrd", str(initrd),
                    "--out-dir", str(out), "--session", session,
                    "--no-attach", "--timeout", "40"]

            def wait_for(predicate):
                deadline = time.monotonic() + 15
                while time.monotonic() < deadline:
                    if predicate():
                        return
                    time.sleep(.1)
                self.fail("tmux condition timed out")

            def has_session():
                return subprocess.run(["tmux", "has-session", "-t", "=" + session],
                                      capture_output=True).returncode == 0

            try:
                subprocess.run(argv, check=True, capture_output=True, timeout=15)
                wait_for(lambda: (out / "uart.log").exists() and
                         b"UART_READY" in (out / "uart.log").read_bytes())
                panes = subprocess.check_output(
                    ["tmux", "list-panes", "-t", session, "-F", "#{pane_id}"],
                    text=True).splitlines()
                self.assertEqual(len(panes), 3)
                wait_for(lambda: "GEM5_PLATFORM_READY" in subprocess.check_output(
                    ["tmux", "capture-pane", "-p", "-t", panes[1]], text=True))
                subprocess.run(["tmux", "send-keys", "-t", panes[0], "hello-gem5", "Enter"], check=True)
                wait_for(lambda: (out / "input.txt").exists())
                self.assertEqual((out / "input.txt").read_bytes(), b"hello-gem5\n")
                pid = int((out / "child.pid").read_text())
                master, slave = pty.openpty()
                client = subprocess.Popen(["tmux", "attach-session", "-t", session],
                                          stdin=slave, stdout=slave, stderr=slave,
                                          env={**os.environ, "TERM": "xterm-256color"})
                wait_for(lambda: subprocess.check_output(
                    ["tmux", "display-message", "-p", "-t", session, "#{session_attached}"],
                    text=True).strip() == "1")
                os.write(master, b"\x1b[24~")  # xterm F12, without prefix
                wait_for(lambda: not has_session())
                wait_for(lambda: not Path(f"/proc/{pid}").exists())
                self.assertIn(b"UART_ECHO:hello-gem5", (out / "uart.log").read_bytes())
            finally:
                subprocess.run(["tmux", "kill-session", "-t", "=" + session], capture_output=True)
                if client:
                    client.wait(timeout=5)
                for fd in (master, slave):
                    if fd is not None:
                        os.close(fd)
