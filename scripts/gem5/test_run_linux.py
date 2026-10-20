# SPDX-License-Identifier: MIT
"""No simulator or build required: exercise launcher inputs and CPIO overlay."""

import contextlib
import gzip
import io
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import run_linux


def entries(data):
    """Independent newc reader, including concatenated archives."""
    records = []
    offset = 0
    while offset < len(data):
        if data[offset] == 0:
            offset += 1
            continue
        if data[offset:offset + 6] != b"070701":
            raise AssertionError("invalid newc magic")
        header = data[offset + 6:offset + 110]
        fields = [int(header[i:i + 8], 16) for i in range(0, 104, 8)]
        length, name_length = fields[6], fields[11]
        start = offset + 110
        name = data[start:start + name_length - 1].decode()
        if data[start + name_length - 1] != 0:
            raise AssertionError("missing name terminator")
        start = (start + name_length + 3) & ~3
        content = data[start:start + length]
        if len(content) != length:
            raise AssertionError("truncated data")
        records.append((name, fields[1], content))
        offset = (start + length + 3) & ~3
    return records


class LauncherTests(unittest.TestCase):
    def test_native_environment_follows_selected_binary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deploy = root / "images/apollo-qvp"
            native = root / "gem5-native"
            source = root / "source"
            for folder in (deploy, native, source / "build/ARM"):
                folder.mkdir(parents=True)
            for name in ("Image", "nexios-initramfs-image-apollo-qvp.cpio.gz",
                         "nexios-image-apollo-qvp.wic", "profile"):
                (deploy / name).touch()
            (native / "gem5.opt").touch()
            (native / "gem5-native.json").write_text("{}")
            (source / "build/ARM/gem5.opt").touch()
            args = run_linux.parser().parse_args([
                "--deploy-dir", str(deploy), "--profile", str(deploy / "profile"),
                "--gem5", str(native / "gem5.opt"),
            ])
            self.assertIsNotNone(run_linux.resolve(args)["native_manifest"])
            args.gem5 = None
            (native / "gem5.opt").unlink()
            with patch("run_linux.SOURCE", source):
                self.assertIsNone(run_linux.resolve(args)["native_manifest"])

    def test_socket_supervisor_reaps_exit_timeout_and_panic(self):
        child_script = """
import socket, struct, sys, time
port, mode = int(sys.argv[1]), sys.argv[2]
with socket.socket() as listener:
    listener.bind(("127.0.0.1", port))
    listener.listen(1)
    peer, _ = listener.accept()
    with peer:
        peer.sendall(b"UART_READY\\n")
        if mode.startswith("panic"):
            peer.sendall(b"Kernel panic - ")
            time.sleep(.05)
            peer.sendall(b"not syncing:")
            time.sleep(.05)
            if mode == "panic":
                peer.sendall(b" test\\n")
            time.sleep(30)
        elif mode == "boot":
            peer.sendall(b"nexios login: ")
            time.sleep(30)
        elif mode == "timeout":
            time.sleep(30)
        else:
            time.sleep(.1)
            peer.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                            struct.pack("ii", 1, 0))
    time.sleep(.1)
"""
        original_popen = subprocess.Popen
        for mode in ("exit", "timeout", "panic", "panic_stall", "boot"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                with socket.socket() as listener:
                    listener.bind(("127.0.0.1", 0))
                    port = listener.getsockname()[1]
                children = []

                def spawn(*args, **kwargs):
                    child = original_popen(*args, **kwargs)
                    children.append(child)
                    return child

                args = SimpleNamespace(
                    timeout=.7 if mode == "timeout" else 3, headless=True,
                    workload="boot" if mode == "boot" else "smoke",
                )
                with patch("run_linux.subprocess.Popen", side_effect=spawn):
                    with patch("run_linux.sys.stdout",
                               SimpleNamespace(buffer=io.BytesIO())):
                        rc, timed_out, elapsed = run_linux.run(
                            [sys.executable, "-c", child_script, str(port), mode],
                            os.environ.copy(), Path(directory), port, args,
                        )
                self.assertEqual(timed_out, mode == "timeout")
                self.assertEqual(rc, 0 if mode == "exit" else -15)
                self.assertLess(elapsed, 3)
                self.assertIn(b"UART_READY\n",
                              (Path(directory) / "uart.log").read_bytes())
                if mode == "panic":
                    self.assertIn(b"not syncing: test\n",
                                  (Path(directory) / "uart.log").read_bytes())
                self.assertEqual(len(children), 1)
                self.assertIsNotNone(children[0].returncode)
                with self.assertRaises(ChildProcessError):
                    os.waitpid(children[0].pid, os.WNOHANG)

    def test_overlay_roundtrip_preserves_base(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = bytearray()
            run_linux.cpio_entry(archive, "init", b"#!/bin/sh\noriginal\n")
            run_linux.cpio_entry(archive, "odd-length", b"abcde")
            run_linux.cpio_entry(archive, "TRAILER!!!", mode=0)
            for compressed in (False, True):
                with self.subTest(compressed=compressed):
                    original = gzip.compress(archive) if compressed else bytes(archive)
                    base = root / "base.cpio"
                    base.write_bytes(original)
                    args = run_linux.parser().parse_args([
                        "--workload", "command", "--command",
                        "printf '%s\\n' 'literal $HOME and spaces'",
                    ])
                    output = run_linux.prepare_initrd(base, root, args)
                    self.assertEqual(base.read_bytes(), original)
                    data = output.read_bytes()
                    self.assertTrue(data.startswith(archive))
                    files = {name: (mode, content)
                             for name, mode, content in entries(data)}
                    self.assertEqual(files["init"][1], b"#!/bin/sh\noriginal\n")
                    self.assertEqual(files["odd-length"][1], b"abcde")
                    self.assertEqual(files["apollo-init"][0], 0o100755)
                    script = files["apollo-init"][1].decode()
                    self.assertIn(args.command, script)
                    self.assertIn("APOLLO_WORKLOAD_EXIT=$status", script)

    def test_boot_archive_unchanged_and_invalid_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = root / "base"
            archive = bytearray()
            run_linux.cpio_entry(archive, "TRAILER!!!", mode=0)
            base.write_bytes(gzip.compress(archive))
            args = run_linux.parser().parse_args([])
            output = run_linux.prepare_initrd(base, root, args)
            self.assertEqual(output.read_bytes(), archive)
            base.write_bytes(b"not a CPIO archive")
            with self.assertRaises(ValueError):
                run_linux.prepare_initrd(base, root, args)

    def test_benchmark_overlay_uses_binary_and_cli_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = root / "base"
            archive = bytearray()
            run_linux.cpio_entry(archive, "TRAILER!!!", mode=0)
            base.write_bytes(archive)
            binary = root / "fake-binary"
            binary.write_bytes(b"\x7fELF fake test data")
            args = run_linux.parser().parse_args([
                "--workload", "dram", "--size-kib", "65536", "--passes", "4",
            ])
            with patch("benchmark.build_benchmark", return_value=binary):
                output = run_linux.prepare_initrd(base, root, args)
            files = {name: content for name, _, content
                     in entries(output.read_bytes())}
            self.assertEqual(files["apollo-bench"], binary.read_bytes())
            self.assertIn(
                b"/apollo-bench --mode dram --passes 4 --size-kib 65536",
                files["apollo-init"],
            )

    def test_explicit_inputs_and_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            argv = []
            for name in ("gem5", "kernel", "initrd", "rootfs", "profile"):
                target = root / f"{name} with spaces"
                target.write_bytes(b"fixture")
                argv.extend([f"--{name}", str(target)])
            inputs = run_linux.resolve(run_linux.parser().parse_args(argv))
            self.assertEqual(Path(inputs["kernel"]), root / "kernel with spaces")
            self.assertIsNone(inputs["native_manifest"])
            (root / "kernel with spaces").unlink()
            with self.assertRaisesRegex(ValueError, "missing file"):
                run_linux.resolve(run_linux.parser().parse_args(argv))

    def test_argument_validation_precedes_input_resolution(self):
        for arguments in (
            ["--workload", "command"],
            ["--command", "echo no"],
            ["--passes", "0"],
            ["--size-kib", "-1"],
            ["--timeout", "0"],
            ["--timeout", "nan"],
            ["--timeout", "inf"],
            ["--passes", "1025"],
            ["--size-kib", "262145"],
            ["--max-ticks", "0"],
            ["--cpus", "3"],
        ):
            with self.subTest(arguments=arguments):
                with patch("sys.argv", ["run_linux.py", *arguments]):
                    with patch("run_linux.resolve") as resolve:
                        with contextlib.redirect_stderr(io.StringIO()):
                            with self.assertRaises(SystemExit) as error:
                                run_linux.main()
                        self.assertEqual(error.exception.code, 2)
                        resolve.assert_not_called()


if __name__ == "__main__":
    unittest.main()
