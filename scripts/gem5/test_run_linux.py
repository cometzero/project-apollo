# SPDX-License-Identifier: MIT
"""No simulator or build required: exercise launcher inputs and CPIO overlay."""

import contextlib
import gzip
import io
import json
import os
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

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
    def test_image_command_requires_collector_success(self):
        for marker, error, expected in ((True, False, "PASS"),
                                         (True, True, "FAIL"),
                                         (False, False, "PASS")):
            with self.subTest(marker=marker, error=error), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                archive = bytearray()
                run_linux.cpio_entry(archive, "TRAILER!!!", mode=0)
                base = root / "initrd"
                base.write_bytes(archive)
                inputs = {name: str(base) for name in
                          ("gem5", "kernel", "bootloader", "profile", "initrd")}
                inputs.update(benchmark=None, rootfs=None, native_manifest=None)
                out = root / "run"

                def execute(*args):
                    (out / "m5out").mkdir()
                    (out / "m5out/system.platform.terminal").write_text(
                        ('APOLLO_IMAGE_RESULT {}\n' if marker else '') +
                        'APOLLO_WORKLOAD_EXIT=0\n')
                    return 0, False, 1.0

                collector = Mock(return_value={"validated": True},
                                 side_effect=ValueError("invalid image ROI") if error else None)
                with patch.object(sys, "argv", ["run_linux.py", "--headless",
                        "--workload", "command", "--command", "true",
                        "--out-dir", str(out)]), \
                        patch("run_linux.resolve", return_value=inputs), \
                        patch("run_linux.native_model_sources", return_value={str(base): "source-hash"}), \
                        patch("run_linux.run", side_effect=execute), \
                        patch.dict(sys.modules, {"image_summary": SimpleNamespace(summarize_image=collector)}), \
                        contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(run_linux.main(), int(expected == "FAIL"))
                result = json.loads((out / "result.json").read_text())
                self.assertEqual(result["status"], expected)
                self.assertEqual(collector.call_count, int(marker))
                self.assertEqual("measurement" in result, marker and not error)
                manifest = json.loads((out / "launch.json").read_text())
                self.assertEqual(manifest["readfile_sha256"], run_linux.sha256(out / "guest-init.sh"))
                self.assertEqual(manifest["original_kernel_sha256"], run_linux.sha256(base))
                self.assertEqual(manifest["profile_sha256"], run_linux.sha256(base))
                self.assertEqual(manifest["model_sources_schema"], 1)
                self.assertEqual(manifest["model_sources_sha256"], {str(base): "source-hash"})

    def test_power_arguments_reject_incomplete_or_invalid_inputs(self):
        for argv in (["--power-profile", "missing"],
                     ["--power-profile", "a", "--thermal-profile", "b"],
                     ["--power-interval-us", "nan"],
                     ["--power-interval-us", "0"],
                     ["--temperature-mc", "150001"],
                     ["--power-control", "--bsp"],
                     ["--power-control", "--workload", "cache"]):
            with self.subTest(argv=argv), patch.object(sys, "argv", ["run_linux.py", *argv]):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                    run_linux.main()
                self.assertEqual(caught.exception.code, 2)

    def test_power_contract_binds_profiles_and_sampling(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "profile.json"
            profile.write_text('{"qualification":"SYNTHETIC"}')
            args = run_linux.parser().parse_args([
                "--power-control", "--power-profile", str(profile),
                "--thermal-profile", str(profile)])
            original = run_linux.power_contract(args)
            args.power_interval_us = 50
            self.assertNotEqual(original, run_linux.power_contract(args))
            args.power_interval_us = 100
            self.assertEqual(original, run_linux.power_contract(args))
            profile.write_text('{"qualification":"UNCALIBRATED"}')
            self.assertNotEqual(original, run_linux.power_contract(args))

    def test_multicore_command_preserves_snapshot_initrd(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = bytearray()
            run_linux.cpio_entry(archive, "TRAILER!!!", mode=0)
            (root / "base").write_bytes(archive)
            args = run_linux.parser().parse_args([
                "--workload", "dram-multicore", "--cpus", "16", "--passes", "1",
                "--interleave-bytes", "512"])
            output = run_linux.prepare_initrd(root / "base", root, args)
            self.assertEqual(output.read_bytes(), archive)
            self.assertIn(
                "/usr/bin/apollo-memory-bench --mode read --kernel neon "
                "--workers 16 --passes 1 --array-mib 64 --initialize-before-switch",
                (root / "guest-init.sh").read_text())
            for mode, guest_mode, kernel in (
                ("read", "read", "neon"), ("copy", "copy", "scalar"),
                ("triad", "stream", "scalar"),
            ):
                args.memory_mode, args.size_kib = mode, 32768
                output = run_linux.prepare_initrd(root / "base", root, args)
                self.assertEqual(output.read_bytes(), archive)
                self.assertIn(
                    f"--mode {guest_mode} --kernel {kernel} "
                    "--workers 16 --passes 1 --array-mib 32 --initialize-before-switch",
                    (root / "guest-init.sh").read_text())

    def test_command_file_preserves_snapshot_initrd(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = bytearray()
            run_linux.cpio_entry(archive, "TRAILER!!!", mode=0)
            base = root / "base"
            base.write_bytes(archive)
            script = root / "command.sh"
            script.write_text("echo 'literal $value'\nprintf '%s\\n' done\n")
            args = run_linux.parser().parse_args([
                "--workload", "command", "--command-file", str(script)])
            output = run_linux.prepare_initrd(base, root, args)
            self.assertEqual(output.read_bytes(), bytes(archive))
            self.assertIn(script.read_text(), (root / "guest-init.sh").read_text())
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    run_linux.parser().parse_args([
                        "--command", "true", "--command-file", str(script)])

    def test_native_environment_follows_selected_binary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            deploy = root / "images/apollo-qvp"
            native = root / "gem5-native"
            source = root / "source"
            for folder in (deploy, native, source / "build/ARM"):
                folder.mkdir(parents=True)
            for name in ("Image", "nexios-gem5-initramfs-apollo-qvp.cpio.gz",
                         "profile"):
                (deploy / name).touch()
            (deploy / "gem5").mkdir()
            (deploy / "gem5/zena_css4.elf").touch()
            (native / "gem5.opt").touch()
            (native / "gem5-native.json").write_text("{}")
            (source / "build/ARM/gem5.opt").touch()
            args = run_linux.parser().parse_args([
                "--deploy-dir", str(deploy), "--profile", str(deploy / "profile"),
                "--gem5", str(native / "gem5.opt"),
            ])
            self.assertIsNotNone(run_linux.resolve(args)["native_manifest"])
            self.assertIsNone(run_linux.resolve(args)["rootfs"])
            previous = Path.cwd()
            try:
                os.chdir(deploy)
                args.deploy_dir = Path(".")
                self.assertIsNotNone(run_linux.resolve(args)["native_manifest"])
            finally:
                os.chdir(previous)
                args.deploy_dir = deploy
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
            peer.sendall(b"NEXIOS_GEM5_INITRAMFS_READY\\n nexios-gem5# ")
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
                self.assertTrue((Path(directory) / "boot-timings.json").is_file())
                self.assertEqual(len(children), 1)
                self.assertIsNotNone(children[0].returncode)
                with self.assertRaises(ChildProcessError):
                    os.waitpid(children[0].pid, os.WNOHANG)

    def test_supervisor_callback_stops_child_without_uart_or_timeout(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            # No server will connect; the file predicate must still be polled.
            child_script = "import pathlib,time; pathlib.Path('" + str(out / "ready") + "').touch(); time.sleep(30)"
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                port = listener.getsockname()[1]
            rc, timed_out, elapsed = run_linux.run(
                [sys.executable, "-c", child_script], os.environ.copy(), out, port,
                SimpleNamespace(timeout=0, headless=True, workload="zephyr"),
                stop_when=lambda: (out / "ready").exists(),
            )
            self.assertEqual(rc, -15)
            self.assertFalse(timed_out)
            self.assertLess(elapsed, 3)

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
                    self.assertEqual(data, archive)
                    self.assertNotIn("etc/gem5-workload.sh", files)
                    script = (root / "guest-init.sh").read_text()
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
            with patch("run_linux.subprocess.run", side_effect=AssertionError("runtime build")):
                output = run_linux.prepare_initrd(base, root, args, binary)
            files = {name: content for name, _, content
                     in entries(output.read_bytes())}
            self.assertEqual(files["usr/bin/apollo-bench"], binary.read_bytes())
            self.assertIn(
                b"/usr/bin/apollo-bench --mode dram --passes 4 --size-kib 65536",
                (root / "guest-init.sh").read_bytes(),
            )

    @patch("run_linux.native_model_sources", return_value={"custom_dram.py": "original"})
    def test_checkpoint_contract_rejects_changed_inputs_and_partial_save(self, model_sources):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = {}
            for name in ("gem5", "kernel", "bootloader", "profile", "initrd"):
                path = root / name
                path.write_bytes(name.encode())
                inputs[name] = str(path)
            args = run_linux.parser().parse_args([])
            contract = run_linux.checkpoint_contract(inputs, root / "initrd", args, "bootargs")
            (root / "m5.cpt").touch()
            (root / "apollo-checkpoint.json").write_text('{"status":"COMPLETE"}')
            (root / "launcher.json").write_text(json.dumps(contract))
            run_linux.validate_checkpoint(root, contract)
            self.assertEqual(contract["schema"], 3)
            self.assertIn("configs/zena_cmn/profiles/default.yaml", contract["configuration_sha256"])
            historical = dict(contract, schema=2)
            (root / "launcher.json").write_text(json.dumps(historical))
            with self.assertRaisesRegex(ValueError, "inputs changed"):
                run_linux.validate_checkpoint(root, contract)
            (root / "launcher.json").write_text(json.dumps(contract))
            model_sources.return_value = {"custom_dram.py": "changed"}
            changed = run_linux.checkpoint_contract(inputs, root / "initrd", args, "bootargs")
            with self.assertRaisesRegex(ValueError, "inputs changed"):
                run_linux.validate_checkpoint(root, changed)
            model_sources.return_value = {"custom_dram.py": "original"}
            original_hash = run_linux.sha256
            with patch("run_linux.sha256", side_effect=lambda path:
                       "changed" if str(path).endswith("profiles/default.yaml") else original_hash(path)):
                changed = run_linux.checkpoint_contract(inputs, root / "initrd", args, "bootargs")
            with self.assertRaisesRegex(ValueError, "inputs changed"):
                run_linux.validate_checkpoint(root, changed)
            args.interleave_bytes = 512
            changed = run_linux.checkpoint_contract(inputs, root / "initrd", args, "bootargs")
            with self.assertRaisesRegex(ValueError, "inputs changed"):
                run_linux.validate_checkpoint(root, changed)
            args.interleave_bytes = 64
            (root / "kernel").write_bytes(b"changed")
            changed = run_linux.checkpoint_contract(inputs, root / "initrd", args, "bootargs")
            with self.assertRaisesRegex(ValueError, "inputs changed"):
                run_linux.validate_checkpoint(root, changed)
            (root / "m5.cpt").unlink()
            with self.assertRaisesRegex(ValueError, "incomplete"):
                run_linux.validate_checkpoint(root, contract)

    def test_model_sources_bind_shared_files_and_imported_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs = {name: str(root / name) for name in
                      ("gem5", "kernel", "bootloader", "profile", "initrd")}
            for filename in inputs.values():
                Path(filename).write_text("fixture")
            # A dependency may live outside configs/zena_cmn and the native
            # Python package may be outside the gem5 checkout entirely.
            dependencies = [root / name for name in
                            ("configs/ruby/CHI_config.py",
                             "configs/topologies/CustomMesh.py",
                             "native/site-packages/yaml/__init__.py")]
            for dependency in dependencies:
                dependency.parent.mkdir(parents=True, exist_ok=True)
                dependency.write_text("original")

            def oracle(*args, **kwargs):
                return {"source_hashes": {str(path): run_linux.sha256(path)
                                          for path in dependencies}}

            args = run_linux.parser().parse_args([])
            fake_parameters = SimpleNamespace(load_parameters=Mock(return_value={}))
            with patch.dict(sys.modules, {
                    "zena_cmn.parameters": fake_parameters,
                    "verify_config": SimpleNamespace(expected_memory=oracle)}), \
                    patch.object(sys, "path", list(sys.path)):
                sources = run_linux.native_model_sources(inputs, args)
                for relative in ("configs/zena_cmn/run_fs.py",
                                 "configs/zena_cmn/profiles/default.yaml",
                                 "configs/example/arm/zena_css.py",
                                 "configs/example/arm/zena_css_models.py"):
                    path = (run_linux.SOURCE / relative).resolve()
                    self.assertEqual(sources[str(path)], run_linux.sha256(path))
                self.assertNotIn(inputs["profile"], sources)
                self.assertTrue(all(str(Path(path).resolve()) == path for path in sources))
                contract = run_linux.checkpoint_contract(inputs, inputs["initrd"], args, "bootargs")
                (root / "m5.cpt").touch()
                (root / "apollo-checkpoint.json").write_text('{"status":"COMPLETE"}')
                (root / "launcher.json").write_text(json.dumps(contract))
                for dependency in dependencies:
                    with self.subTest(dependency=dependency):
                        dependency.write_text("changed")
                        changed = run_linux.checkpoint_contract(inputs, inputs["initrd"], args, "bootargs")
                        with self.assertRaisesRegex(ValueError, "inputs changed"):
                            run_linux.validate_checkpoint(root, changed)
                        dependency.write_text("original")

    def test_checkpoint_rejects_embedded_python_override_before_resolution(self):
        for option in ("--checkpoint", "--resume"):
            for value in ("true", "TRUE", "yes", "YeS"):
                with self.subTest(option=option, value=value), \
                        patch.dict(os.environ, {"M5_OVERRIDE_PY_SOURCE": value}), \
                        patch.object(sys, "argv", ["run_linux.py", option, "/unused"]), \
                        patch("run_linux.resolve") as resolve, \
                        contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as caught:
                        run_linux.main()
                    self.assertEqual(caught.exception.code, 2)
                    resolve.assert_not_called()
                    with self.assertRaisesRegex(ValueError, "M5_OVERRIDE_PY_SOURCE"):
                        run_linux.checkpoint_contract({}, None, None, "")
        # These spellings do not enable the native importer's override mode.
        for value in ("false", "no", "1", " true", "yes ", ""):
            with self.subTest(value=value), patch.dict(os.environ, {"M5_OVERRIDE_PY_SOURCE": value}):
                self.assertFalse(run_linux.checkpoint_source_override())

    def test_native_export_captures_oracle_before_passive_fs_import(self):
        class Value:
            def __init__(self, value):
                self.value = value

            def config_value(self):
                return self.value

        instances = []

        class DRAM:
            devices_per_rank = Value(1)
            _params = {"latency": None}

            def __init__(self, **kwargs):
                self.latency = Value(7)
                instances.append(self)

        class Controller(DRAM):
            pass

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile, output = root / "profile.json", root / "expected.json"
            profile.write_text(json.dumps({"memory": {
                "custom_module": "fixture_dram", "custom_class": "FixtureDRAM",
                "preserve_device_geometry": True}}))
            fixture_paths = [root / name for name in ("CHI_config.py", "CustomMesh.py", "yaml.py")]
            for path in fixture_paths:
                path.write_text("fixture source")
            m5 = ModuleType("m5")
            m5.ticks = SimpleNamespace(setGlobalFrequency=Mock(), fixGlobalFrequency=Mock())
            m5.instantiate = Mock(side_effect=AssertionError("must not instantiate"))
            m5.simulate = Mock(side_effect=AssertionError("must not simulate"))

            def imported(name):
                if name == "fixture_dram":
                    return SimpleNamespace(FixtureDRAM=DRAM)
                self.assertEqual(name, "zena_cmn.run_fs")
                self.assertEqual(len(instances), 2)
                for instance in instances:
                    instance.latency.value = 999  # Backend cannot change the captured oracle.
                for index, path in enumerate(fixture_paths):
                    sys.modules[f"fixture_fs_dependency_{index}"] = SimpleNamespace(__file__=str(path))
                return SimpleNamespace()

            exporter = run_linux.SOURCE / "scripts/zena_cmn/export_expected_memory.py"
            with patch.dict(sys.modules, {
                    "m5": m5, "m5.objects": SimpleNamespace(DRAMInterface=DRAM, MemCtrl=Controller),
                    "m5.proxy": SimpleNamespace(isproxy=lambda value: False)}), \
                    patch("importlib.import_module", side_effect=imported) as imports, \
                    patch.object(sys, "path", list(sys.path)), \
                    patch.object(sys, "argv", [str(exporter), str(profile), str(output)]):
                runpy.run_path(str(exporter), run_name="__m5_main__")
            exported = json.loads(output.read_text())
            self.assertEqual(exported["dram"], {"latency": 7})
            self.assertEqual(exported["controller"], {"latency": 7})
            self.assertEqual([call.args[0] for call in imports.call_args_list],
                             ["fixture_dram", "zena_cmn.run_fs"])
            for path in fixture_paths:
                self.assertEqual(exported["source_hashes"][str(path)], run_linux.sha256(path))
            m5.instantiate.assert_not_called()
            m5.simulate.assert_not_called()

    def test_warmup_options_are_delivered_only_to_supported_workloads(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = bytearray()
            run_linux.cpio_entry(archive, "TRAILER!!!", mode=0)
            base = root / "base"
            base.write_bytes(archive)
            for mode in ("cache", "dram", "dram-multicore"):
                args = run_linux.parser().parse_args(["--workload", mode, "--warmup-passes", "2"])
                run_linux.prepare_initrd(base, root, args)
                self.assertIn("--warmup-passes 2", (root / "guest-init.sh").read_text())
        with patch("sys.argv", ["run_linux.py", "--warmup-passes", "2"]), self.assertRaises(SystemExit):
            run_linux.main()

    def test_legacy_bsp_still_overlays_init(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = bytearray()
            run_linux.cpio_entry(archive, "TRAILER!!!", mode=0)
            (root / "base").write_bytes(archive)
            args = run_linux.parser().parse_args(["--bsp", "--workload", "smoke"])
            result = run_linux.prepare_initrd(root / "base", root, args)
            files = {name: content for name, _, content in entries(result.read_bytes())}
            self.assertIn(b"APOLLO_SMOKE=PASS", files["apollo-init"])

    def test_workload_shutdown_with_and_without_poweroff(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = bytearray()
            run_linux.cpio_entry(archive, "TRAILER!!!", mode=0)
            (root / "base").write_bytes(archive)
            args = run_linux.parser().parse_args(["--workload", "smoke"])
            run_linux.prepare_initrd(root / "base", root, args)
            script = (root / "guest-init.sh").read_text()
            shutdown = script[script.index("shutdown_guest() {"):script.index("echo APOLLO_ONLINE=")]
            shutdown = shutdown.replace("/proc/sysrq-trigger", str(root / "sysrq"))
            for name, body in (("sync", "echo sync >> calls"), ("poweroff", "echo poweroff \"$@\" >> calls")):
                tool = root / name
                tool.write_text("#!/bin/sh\n" + body + "\n")
                tool.chmod(0o755)
            for available in (True, False):
                if not available:
                    (root / "poweroff").unlink()
                subprocess.run(["/bin/sh", "-c", shutdown + "\nshutdown_guest"],
                               cwd=root, env={"PATH": str(root)}, check=True)
                self.assertEqual((root / "calls").read_text(),
                                 "sync\npoweroff -f\n" if available else "sync\n")
                (root / "calls").unlink()
                if not available:
                    self.assertEqual((root / "sysrq").read_text(), "o\n")

    def test_explicit_inputs_and_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            argv = ["--deploy-dir", str(root)]
            for name in ("gem5", "kernel", "initrd", "rootfs", "profile", "bootloader"):
                target = root / f"{name} with spaces"
                target.write_bytes(b"fixture")
                argv.extend([f"--{name}", str(target)])
            inputs = run_linux.resolve(run_linux.parser().parse_args(argv))
            self.assertEqual(Path(inputs["kernel"]), root / "kernel with spaces")
            self.assertIsNone(inputs["native_manifest"])
            args = run_linux.parser().parse_args(argv + ["--workload", "cache"])
            self.assertIsNone(run_linux.resolve(args)["benchmark"])
            args.benchmark = root / "benchmark with spaces"
            args.benchmark.write_bytes(b"prebuilt benchmark")
            with patch("run_linux.subprocess.run", side_effect=AssertionError("runtime build")):
                self.assertEqual(run_linux.resolve(args)["benchmark"], str(args.benchmark))
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
            ["--cpus", "8"],
            ["--interleave-bytes", "128"],
            ["--workers", "4"],
            ["--memory-mode", "read"],
            ["--workload", "cache", "--memory-mode", "copy"],
            ["--workload", "dram-multicore", "--memory-mode", "stream"],
            ["--workload", "dram-multicore", "--workers", "16"],
            ["--workload", "dram-multicore", "--passes", "3"],
            ["--workload", "dram-multicore", "--size-kib", "1025"],
            ["--workload", "dram-multicore", "--bsp"],
            ["--checkpoint", "/new", "--workload", "smoke"],
            ["--checkpoint", "/new", "--bsp"],
            ["--resume", "/saved", "--rootfs", "/disk"],
            ["--checkpoint", "/new", "--resume", "/saved"],
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
