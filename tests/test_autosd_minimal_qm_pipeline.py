"""Reproducibility and non-destructive boundaries of the minimal QM pipeline."""
import importlib.util
import io
import json
from pathlib import Path
import tarfile
from types import SimpleNamespace

import pytest


@pytest.fixture
def module():
    source = Path(__file__).resolve().parents[1] / "scripts/autosd_demo/build_minimal_qm.py"
    spec = importlib.util.spec_from_file_location("minimal_qm_pipeline", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def args(module, tmp_path, *extra):
    return module.resolve(module.parser().parse_args([
        "--work-dir", str(tmp_path / "work"), "--output", str(tmp_path / "prepared"),
        "--build-dir", str(tmp_path / "build"), *extra]))


def test_dry_run_never_creates_files(module, tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(module, "preflight", lambda *_: pytest.fail("dry-run preflight"))
    monkeypatch.setattr(module.subprocess, "Popen", lambda *_a, **_k: pytest.fail("started VM"))
    assert module.main(["--dry-run", "--work-dir", str(tmp_path / "work"),
                        "--output", str(tmp_path / "prepared")]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert "builder" in plan["commands"]
    assert list(tmp_path.iterdir()) == []


def test_build_directory_controls_default_inputs_and_outputs(module, tmp_path):
    config = module.resolve(module.parser().parse_args(["--build-dir", str(tmp_path)]))
    assert config.manifest == tmp_path / "autosd/regular.json"
    assert config.output == tmp_path / "autosd/demo-minimal-qm-prepared"
    assert config.work_dir.parent == tmp_path / "autosd"


def test_existing_image_skips_only_builder(module, tmp_path):
    config = args(module, tmp_path, "--image", str(tmp_path / "source.qcow2"))
    plan = module.plan(config)
    assert "builder" not in plan["commands"]
    assert {"prepare", "qemu", "modules", "qbox"} <= plan["commands"].keys()
    assert plan["image"] == str(tmp_path / "source.qcow2")


def test_full_output_discoverable_and_private_disk(module, tmp_path):
    config = args(module, tmp_path)
    assert config.qbox_out_dir.parent == config.build_dir / "qbox-apollo-qvp"
    commands = module.plan(config)["commands"]
    command = commands["qbox"]
    assert command[command.index("--rootfs") + 1] == str(config.work_dir / "qemu/rootfs.wic")
    assert "--headless" in command
    assert "--prepare-only" in commands["modules"]
    assert commands["builder"][commands["builder"].index("--manifest") + 1] == str(config.manifest)


@pytest.mark.parametrize("extra", [["--boot-timeout", "0"], ["--build-timeout", "-1"],
                                  ["--qbox-port", "2226"], ["--builder-port", "22"]])
def test_invalid_configuration(module, tmp_path, extra):
    with pytest.raises(ValueError):
        args(module, tmp_path, *extra)


@pytest.mark.parametrize("field", ["work_dir", "output", "qbox_out_dir"])
def test_existing_outputs_refused(module, tmp_path, field):
    config = args(module, tmp_path)
    path = getattr(config, field)
    path.mkdir(parents=True)
    with pytest.raises(ValueError, match="overwrite"):
        module.preflight(config)


@pytest.mark.parametrize("missing", ["u-boot-apollo-qemu.bin",
    "efi-capsule-update-disk-image-apollo-qvp.img", "nexios-bsp-initramfs-apollo-qvp.qboxconf",
    "fsck.fat", "mcopy", "mdir"])
def test_missing_boot_prerequisite_fails_before_mutation(module, tmp_path, monkeypatch, missing):
    config = args(module, tmp_path, "--image", str(tmp_path / "source.qcow2"))
    # All existing dependencies are represented read-only; the selected required
    # artifact/tool alone is absent. No child or output may be created.
    monkeypatch.setattr(module.Path, "is_file", lambda self: self.name != missing)
    monkeypatch.setattr(module.shutil, "which", lambda name: None if name == missing else "/usr/bin/" + name)
    monkeypatch.setattr(module.subprocess, "Popen", lambda *a, **k: pytest.fail("started VM"))
    with pytest.raises(ValueError, match=missing.replace(".", r"\.")):
        module.Pipeline(config).run()
    assert not config.work_dir.exists()
    assert not config.output.exists()
    assert not config.qbox_out_dir.exists()


def test_module_archive_release_and_hash(module, tmp_path):
    archive = tmp_path / "modules.tgz"
    with tarfile.open(archive, "w:gz") as target:
        info = tarfile.TarInfo("lib/modules/6.18-rt/kernel/example.ko")
        info.size = 4
        target.addfile(info, io.BytesIO(b"test"))
    assert module.module_release(archive) == "6.18-rt"
    assert len(module.sha256(archive)) == 64


def test_guest_verifies_efi_qm_slot_and_kernel(module, tmp_path, monkeypatch):
    pipeline = module.Pipeline(args(module, tmp_path))
    seen = []
    monkeypatch.setattr(module, "module_release", lambda _: "6.18-rt")
    monkeypatch.setattr(pipeline, "guest", lambda *a, **k: seen.append((a, k)))
    pipeline.verify_guest("guest", 2224)
    command = seen[0][0][2]
    assert "test -d /sys/firmware/efi" in command
    assert "uname -r" in command and "6.18-rt" in command
    assert "qm_guest_check.sh" in command
    assert "ukibootctl dump" in command and "ukibootctl get-active" in command
    assert "bootctl partition is invalid" in command


def test_shutdown_does_not_kill_foreign_process(module, tmp_path, monkeypatch):
    pipeline = module.Pipeline(args(module, tmp_path))
    (pipeline.args.work_dir / "qemu").mkdir(parents=True)
    (pipeline.args.work_dir / "qemu/linux-uart.log").write_text("reboot: Power down\n")
    calls = []
    monkeypatch.setattr(pipeline, "guest", lambda *a, **k: calls.append(a))
    owned = SimpleNamespace(wait=lambda timeout: 0)
    pipeline.shutdown("qemu", owned, 2224)
    assert calls[0][1] == 2224
    assert "systemctl poweroff" in calls[0][2]


def test_shutdown_requires_guest_poweroff_marker(module, tmp_path, monkeypatch):
    pipeline = module.Pipeline(args(module, tmp_path))
    (pipeline.args.work_dir / "qemu").mkdir(parents=True)
    (pipeline.args.work_dir / "qemu/linux-uart.log").write_text("login: root\n")
    monkeypatch.setattr(pipeline, "guest", lambda *a, **k: None)
    with pytest.raises(RuntimeError, match="poweroff marker"):
        pipeline.shutdown("qemu", SimpleNamespace(wait=lambda timeout: 0), 2224)


def test_failure_reports_owned_live_process_without_kill(module, tmp_path, monkeypatch):
    config = args(module, tmp_path, "--image", str(tmp_path / "source.qcow2"))
    config.image.write_bytes(b"image")
    pipeline = module.Pipeline(config)
    owned = SimpleNamespace(pid=123, poll=lambda: None)
    pipeline.processes.append(("owned", owned))
    monkeypatch.setattr(module, "preflight", lambda _: None)
    monkeypatch.setattr(pipeline, "provenance", lambda: {})
    def fail(*a, **k):
        raise RuntimeError("test failure")
    monkeypatch.setattr(pipeline, "command", fail)
    with pytest.raises(RuntimeError, match="test failure"):
        pipeline.run()
    report = json.loads((config.work_dir / "result.json").read_text())
    assert report["status"] == "FAIL"
    assert report["live_owned_launchers"] == [{"name": "owned", "pid": 123}]


def test_customization_is_opt_in_and_requires_runtime(module, tmp_path):
    assert "customization-bundle" not in module.plan(args(module, tmp_path))["commands"]
    assert module.plan(args(module, tmp_path))["rt_tools"] is False
    with pytest.raises(ValueError, match="crun-binary"):
        args(module, tmp_path, "--customize")
    config = args(module, tmp_path, "--customize", "--crun-binary", str(tmp_path / "crun"))
    plan = module.plan(config)
    assert plan["customize"]
    assert "--crun-binary" in plan["commands"]["customization-bundle"]
    assert "--rt-tools" in plan["commands"]["customization-bundle"]
    assert plan["rt_tools"] is True


def test_builder_override_requires_digest(module, tmp_path):
    with pytest.raises(ValueError, match="SHA256"):
        args(module, tmp_path, "--builder-image", "quay.io/example:latest")
    with pytest.raises(ValueError, match="official AIB"):
        args(module, tmp_path, "--builder-image", "quay.io/example@sha256:" + "a" * 64)
    value = "quay.io/centos-sig-automotive/automotive-image-builder@sha256:" + "a" * 64
    assert module.plan(args(module, tmp_path, "--builder-image", value))["builder_image"] == value


def test_customize_uses_existing_payloads(module, tmp_path, monkeypatch):
    config = args(module, tmp_path, "--customize", "--crun-binary", str(tmp_path / "crun"))
    config.work_dir.mkdir()
    bundle = config.work_dir / "customization-bundle"
    bundle.mkdir()
    (bundle / "example").write_text("example")
    pipeline = module.Pipeline(config)
    calls = []
    monkeypatch.setattr(pipeline, "command", lambda *a, **k: None)
    monkeypatch.setattr(pipeline, "guest", lambda *a, **k: calls.append((a, k)))
    pipeline.customize()
    assert len(calls) == 6
    stages = [call[0][0] for call in calls]
    assert stages.index("customization-rt-packages") < stages.index("customization-install")
    assert stages[-1] == "qemu-rt-readiness"
    for _, keywords in calls:
        for local, _ in keywords.get("uploads", []):
            assert local.is_file()


def test_rt_readiness_checks_guest_and_propagates_failure(module, tmp_path, monkeypatch):
    pipeline = module.Pipeline(args(module, tmp_path))
    calls = []
    def guest(*pos, **kw):
        calls.append((pos, kw))
        raise RuntimeError("RT prerequisite absent")
    monkeypatch.setattr(pipeline, "guest", guest)
    with pytest.raises(RuntimeError, match="RT prerequisite absent"):
        pipeline.verify_rt("qbox-rt-readiness", 2244)
    pos, kw = calls[0]
    assert pos == ("qbox-rt-readiness", 2244, "bash /root/prepare-rt-guest.sh check")
    assert kw["uploads"][0][0].is_file()


@pytest.mark.parametrize("receipt,expected", [
    ({"status": "POWERED_OFF", "passed": True, "poweroff_observed": True, "domains": {"status": "PASS"}}, "PASS"),
    ({"status": "POWERED_OFF", "passed": True, "poweroff_observed": False, "domains": {"status": "PASS"}}, "FAIL"),
    ({"status": "POWERED_OFF", "passed": True, "poweroff_observed": True, "domains": {"status": "FAIL"}}, "FAIL"),
    ({"status": "UNEXPECTED_EXIT", "passed": True, "poweroff_observed": True, "domains": {"status": "PASS"}}, "FAIL"),
])
def test_run_requires_complete_full_system_receipt(module, tmp_path, monkeypatch, receipt, expected):
    config = args(module, tmp_path, "--image", str(tmp_path / "source.qcow2"))
    config.image.write_bytes(b"qcow2")
    pipeline = module.Pipeline(config)
    monkeypatch.setattr(module, "preflight", lambda _: None)
    monkeypatch.setattr(pipeline, "provenance", lambda: {})
    monkeypatch.setattr(pipeline, "command", lambda *a, **k: None)
    monkeypatch.setattr(pipeline, "wait_ssh", lambda *a: None)
    monkeypatch.setattr(pipeline, "bootstrap_qemu_ssh", lambda *a: None)
    monkeypatch.setattr(pipeline, "install_modules", lambda *a: None)
    monkeypatch.setattr(pipeline, "verify_guest", lambda *a: None)
    monkeypatch.setattr(pipeline, "shutdown", lambda *a: None)
    def start(name):
        if name == "qbox":
            config.qbox_out_dir.mkdir(parents=True)
            (config.qbox_out_dir / "modules.json").write_text('{"status":"PASS"}')
            (config.qbox_out_dir / "domains.json").write_text('{"status":"PASS"}')
            (config.qbox_out_dir / "result.json").write_text(json.dumps(receipt))
        return SimpleNamespace(poll=lambda: None)
    monkeypatch.setattr(pipeline, "start", start)
    if expected == "FAIL":
        with pytest.raises(RuntimeError, match="evidence failed"):
            pipeline.run()
    else:
        pipeline.run()
    assert json.loads((config.work_dir / "result.json").read_text())["status"] == expected


@pytest.mark.parametrize("extra", [
    ["--builder-archive", "builder.tar"],
    ["--image", "image.qcow2", "--builder-archive", "builder.tar"],
    ["--image", "image.qcow2", "--builder-image",
     "quay.io/centos-sig-automotive/automotive-image-builder@sha256:" + "a" * 64],
])
def test_archive_requires_digest_and_rejects_skipped_builder(module, tmp_path, extra):
    with pytest.raises(ValueError):
        args(module, tmp_path, *extra)


def test_archive_upload_hash_and_exact_digest_command(module, tmp_path, monkeypatch):
    archive = tmp_path / "builder.oci.tar"
    archive.write_bytes(b"test archive")
    digest_image = "quay.io/centos-sig-automotive/automotive-image-builder@sha256:" + "a" * 64
    config = args(module, tmp_path, "--builder-archive", str(archive), "--builder-image", digest_image)
    pipeline = module.Pipeline(config)
    seen = []
    monkeypatch.setattr(pipeline, "guest", lambda *a, **kw: seen.append((a, kw)))
    pipeline.build_guest_image()
    command = seen[0][0][2]
    assert module.sha256(archive) in command
    assert "sha256sum -c - && bash /root/builder_guest.sh " + digest_image in command
    assert command.endswith(" /root/aib-builder.oci.tar")
    assert (archive, "/root/aib-builder.oci.tar") in seen[0][1]["uploads"]
    assert "pull" not in command
    assert pipeline.plan["builder_archive"] == str(archive)


def test_archive_provenance_records_input_hash(module, tmp_path, monkeypatch):
    archive = tmp_path / "builder.oci.tar"
    digest_image = "quay.io/centos-sig-automotive/automotive-image-builder@sha256:" + "a" * 64
    config = args(module, tmp_path, "--builder-archive", str(archive), "--builder-image", digest_image)
    pipeline = module.Pipeline(config)
    monkeypatch.setattr(module, "sha256", lambda path: "hash-of-" + Path(path).name)
    monkeypatch.setattr(module.subprocess, "check_output", lambda *a, **kw: "source-sha\n")
    assert pipeline.provenance()["files"][str(archive)] == "hash-of-builder.oci.tar"


@pytest.mark.parametrize("outcome", ["PASS", "FAIL", "echo-only"])
def test_uart_bootstrap_requires_actual_marker(module, tmp_path, monkeypatch, outcome):
    config = args(module, tmp_path)
    pipeline = module.Pipeline(config)
    directory = config.work_dir / "qemu"
    directory.mkdir(parents=True)
    uart = directory / "linux-uart.log"
    uart.write_text("[root@autosd ~]# ")
    uart_in = directory / "linux-uart.in"
    uart_in.touch()
    monkeypatch.setattr(module.uuid, "uuid4", lambda: SimpleNamespace(hex="testtoken"))
    clock = [0]
    monkeypatch.setattr(module.time, "monotonic", lambda: clock[0])
    def advance(_seconds):
        clock[0] += 600
        with uart.open("a") as stream:
            # Include the complete command echo. It must never be sufficient.
            stream.write(uart_in.read_text())
            if outcome != "echo-only":
                stream.write("\r\nAPOLLO_SSH_BOOTSTRAP_testtoken_" + outcome + "\r\n")
    monkeypatch.setattr(module.time, "sleep", advance)
    process = SimpleNamespace(poll=lambda: None)
    if outcome == "PASS":
        pipeline.bootstrap_qemu_ssh(process)
    else:
        with pytest.raises((RuntimeError, TimeoutError)):
            pipeline.bootstrap_qemu_ssh(process)
    report = json.loads((config.work_dir / "qemu-ssh-bootstrap.json").read_text())
    assert report["status"] == ("PASS" if outcome == "PASS" else "FAIL")
    command = uart_in.read_text()
    assert "openssh-server iproute" in command
    assert "PermitRootLogin yes" in command and "PasswordAuthentication yes" in command
    assert "systemctl is-active --quiet sshd" in command
    assert "APOLLO_SSH_BOOTSTRAP_testtoken_PASS" not in command


def test_uart_bootstrap_rejects_dead_launcher(module, tmp_path):
    config = args(module, tmp_path)
    config.work_dir.mkdir()
    pipeline = module.Pipeline(config)
    with pytest.raises(RuntimeError, match="QEMU exited"):
        pipeline.bootstrap_qemu_ssh(SimpleNamespace(poll=lambda: 1))
    assert json.loads((config.work_dir / "qemu-ssh-bootstrap.json").read_text())["status"] == "FAIL"


def test_uart_bootstrap_root_prompt_deadline(module, tmp_path, monkeypatch):
    config = args(module, tmp_path, "--boot-timeout", "1")
    config.work_dir.mkdir()
    pipeline = module.Pipeline(config)
    clock = [0]
    monkeypatch.setattr(module.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(module.time, "sleep", lambda _: clock.__setitem__(0, 2))
    with pytest.raises(TimeoutError, match="deadline"):
        pipeline.bootstrap_qemu_ssh(SimpleNamespace(poll=lambda: None))
    assert not (config.work_dir / "qemu/linux-uart.in").exists()
