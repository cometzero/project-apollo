"""Exercise QEMU stdio supervision without requiring a full guest boot."""

import importlib.util
import fcntl
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest


RUN_DIR = Path(__file__).resolve().parents[1] / "scripts/run"
sys.path.insert(0, str(RUN_DIR))
SPEC = importlib.util.spec_from_file_location("qemu_linux", RUN_DIR / "run_qemu_linux.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)
sys.path.pop(0)


def fake_guest(tmp_path, source, *, bsp=True):
    for name in ("linux-uart.log", "linux-uart.in"):
        (tmp_path / name).touch()
    (tmp_path / "launch.json").write_text(json.dumps({
        "command": [sys.executable, "-u", "-c", source],
        "environment": {}, "bsp": bsp, "cpus": 4,
    }))


@pytest.mark.parametrize("bsp", [True, False])
def test_supervisor_waits_for_actual_smoke_response(tmp_path, bsp):
    prompt = "NEXIOS_BSP_INITRAMFS_FAILED\nnexios-bsp-failed# " if bsp else "apollo-qvp login: "
    fake_guest(tmp_path, f"""
import sys, time
sys.stdout.write({prompt!r}); sys.stdout.flush()
sys.stdin.readline()
sys.stdout.write('root@apollo-qvp:~# '); sys.stdout.flush()
command = sys.stdin.readline()
assert 'test -b /dev/vda' in command
assert '-eq 4' in command
sys.stdout.write(command); sys.stdout.flush()
time.sleep(.1)
sys.stdout.write('QEMU_LINUX_SMOKE_DONE\\n'); sys.stdout.flush()
time.sleep(20)
""", bsp=bsp)
    assert runner.supervise(tmp_path, 3, True) == 0
    result = json.loads((tmp_path / "result.json").read_text())
    assert result["status"] == "PASS"
    assert result["bsp_selftest"] == ("FAIL" if bsp else "NOT_APPLICABLE")


def test_echoed_probe_is_not_success(tmp_path):
    fake_guest(tmp_path, """
import sys, time
print('NEXIOS_BSP_INITRAMFS_READY\\nnexios-bsp# ', end='', flush=True)
sys.stdin.readline()
print(sys.stdin.readline(), flush=True)
time.sleep(20)
""")
    assert runner.supervise(tmp_path, .4, True) == 124
    assert json.loads((tmp_path / "result.json").read_text())["status"] == "TIMEOUT"


def test_panic_fails_and_stderr_is_separate(tmp_path):
    fake_guest(tmp_path, """
import sys, time
print('QEMU diagnostic', file=sys.stderr, flush=True)
print('Kernel panic - not syncing: test', flush=True)
time.sleep(20)
""")
    assert runner.supervise(tmp_path, 3, True) == 1
    assert "QEMU diagnostic" in (tmp_path / "qemu.log").read_text()
    assert "QEMU diagnostic" not in (tmp_path / "linux-uart.log").read_text()


def test_monitor_transport_is_logged_separately(tmp_path):
    fake_guest(tmp_path, """
import socket, sys, time
monitor = socket.socket(fileno=int(sys.argv[1]))
monitor.sendall(b'(qemu) ')
assert monitor.recv(4096) == b'info status\\n'
monitor.sendall(b'VM status: running\\n(qemu) ')
print('nexios-bsp# ', end='', flush=True)
time.sleep(20)
""")
    plan_file = tmp_path / "launch.json"
    plan = json.loads(plan_file.read_text())
    plan["command"].append("@MONITOR_FD@")
    plan_file.write_text(json.dumps(plan))
    (tmp_path / "qemu-monitor.in").write_bytes(b"info status\n")
    assert runner.supervise(tmp_path, .5, False) == 0
    assert b"VM status: running" in (tmp_path / "qemu-monitor.log").read_bytes()
    assert b"VM status" not in (tmp_path / "linux-uart.log").read_bytes()


@pytest.mark.parametrize("bsp", [True, False])
def test_plan_selects_matching_images_without_writes(tmp_path, bsp):
    for name in ("Image", "qemu", "nexios-bsp-initramfs-apollo-qvp.cpio.gz",
                 "nexios-initramfs-image-apollo-qvp.cpio.gz",
                 "nexios-bsp-initramfs-apollo-qvp.wic", "nexios-image-apollo-qvp.wic"):
        (tmp_path / name).touch()
    args = runner.parser().parse_args([
        "--qemu", str(tmp_path / "qemu"), "--deploy-dir", str(tmp_path),
        *(["--bsp"] if bsp else []),
    ])
    out = tmp_path / "private"
    plan = runner.make_plan(args, out)
    assert not out.exists()
    assert plan["source_rootfs"].endswith(
        ("nexios-bsp-initramfs" if bsp else "nexios-image") + "-apollo-qvp.wic")
    assert "apollo-qvp" in plan["command"]
    assert "rdinit=/init" in plan["command"][plan["command"].index("-append") + 1] if bsp else True
    assert "virtio-blk-device,drive=rootfs,bus=virtio-mmio-bus.0" in plan["command"]


@pytest.mark.parametrize("mode", ["regular", "ostree"])
def test_autosd_plan_and_explicit_overrides(tmp_path, mode):
    for name in ("Image", "qemu", "autosd.raw", "autosd.initrd", "override"):
        (tmp_path / name).touch()
    manifest = tmp_path / "autosd.json"
    manifest.write_text(json.dumps({
        "rootfs": str(tmp_path / "autosd.raw"), "initrd": str(tmp_path / "autosd.initrd"),
        "bootargs": "console=ttyAMA0 root=UUID=test", "mode": mode,
    }))
    cli = ["--autosd", str(manifest), "--qemu", str(tmp_path / "qemu"),
           "--deploy-dir", str(tmp_path)]
    plan = runner.make_plan(runner.parser().parse_args(cli), tmp_path / "out")
    assert plan["kernel"] == str(tmp_path / "Image")
    assert plan["source_rootfs"] == str(tmp_path / "autosd.raw")
    assert plan["initrd"] == str(tmp_path / "autosd.initrd")
    assert plan["autosd_mode"] == mode
    plan = runner.make_plan(runner.parser().parse_args(cli + [
        "--kernel", str(tmp_path / "override"), "--initrd", str(tmp_path / "override"),
        "--rootfs", str(tmp_path / "override"), "--bootargs", "custom",
    ]), tmp_path / "out")
    assert plan["kernel"] == plan["initrd"] == plan["source_rootfs"] == str(tmp_path / "override")
    assert plan["command"][plan["command"].index("-append") + 1] == "custom"


@pytest.mark.parametrize("mode", ["regular", "ostree"])
def test_autosd_password_login_and_smoke(tmp_path, mode):
    fake_guest(tmp_path, f"""
import sys, time
print('localhost login: ', end='', flush=True)
assert sys.stdin.readline() == 'root\\n'
print('Password: ', end='', flush=True)
assert sys.stdin.readline() == 'password\\n'
print('[root@localhost ~]# ', end='', flush=True)
command = sys.stdin.readline()
assert '/etc/os-release' in command and 'autosd' in command
assert ('ostree admin status' in command) == {mode == 'ostree'}
assert ('/run/ostree-booted' in command) == {mode == 'ostree'}
assert '-eq 4' in command and 'dd if=/dev/vda' in command
print(command, flush=True)
time.sleep(.1)
print('QEMU_LINUX_SMOKE_DONE', flush=True)
time.sleep(20)
""", bsp=False)
    path = tmp_path / "launch.json"
    plan = json.loads(path.read_text())
    plan["autosd_mode"] = mode
    path.write_text(json.dumps(plan))
    assert runner.supervise(tmp_path, 3, True) == 0
    result = json.loads((tmp_path / "result.json").read_text())
    assert result["smoke_completed"]
    assert result["autosd_mode"] == mode
    assert "no OTA or secure boot qualification" in result["qualification"]


@pytest.mark.parametrize("efi,service,disk_success", [(True, True, True), (False, True, True),
                                                    (True, False, True), (True, True, False)])
def test_uki_supervisor_requires_efi_evidence(tmp_path, monkeypatch, efi, service, disk_success):
    monkeypatch.setitem(sys.modules, "autosd_disk", SimpleNamespace(inspect_disk=lambda path: {
        "bootctl": {"valid": True, "slots": [{"successful_boot": int(disk_success), "tries_remaining": 0}]}}))
    fake_guest(tmp_path, f"""
import sys, time
print('U-Boot\\n=> ', end='', flush=True)
assert sys.stdin.readline() == 'fatload virtio 0:1 0x90000000 /EFI/BOOT/BOOTAA64.EFI && bootefi 0x90000000 ${{fdtcontroladdr}}\\n'
print('localhost login: ', end='', flush=True)
assert sys.stdin.readline() == 'root\\n'
print('Password: ', end='', flush=True)
assert sys.stdin.readline() == 'password\\n'
print('[root@localhost ~]# ', end='', flush=True)
command = sys.stdin.readline()
assert 'test -d /sys/firmware/efi' in command
assert 'systemctl is-active --quiet ukiboot-set-success.service' in command
print(command, flush=True)
if {efi}:
    print('APOLLO_EFI_BOOTED', flush=True)
if {service}:
    print('APOLLO_UKIBOOT_SLOT=0', flush=True)
print('QEMU_LINUX_SMOKE_DONE', flush=True)
time.sleep(20)
""", bsp=False)
    path = tmp_path / "launch.json"
    plan = json.loads(path.read_text())
    plan.update(autosd_mode="regular", uki={"source": "test.efi", "prepared_disk": {"test": True}, "boot_command":
        "fatload virtio 0:1 0x90000000 /EFI/BOOT/BOOTAA64.EFI && bootefi 0x90000000 ${fdtcontroladdr}\n"})
    path.write_text(json.dumps(plan))
    expected = (0 if disk_success else 1) if efi and service else 124
    assert runner.supervise(tmp_path, 1, True) == expected
    result = json.loads((tmp_path / "result.json").read_text())
    assert result["efi_boot_observed"] == efi
    assert result["ukiboot_service"] == ("PASS" if service else "NOT_OBSERVED")


def test_uki_rejects_non_autosd_mode(tmp_path):
    args = runner.parser().parse_args(["--uki", "test.efi"])
    with pytest.raises(ValueError, match="requires --autosd"):
        runner.make_plan(args, tmp_path)


def native_args(tmp_path, monkeypatch, extra=()):
    for name in ("qemu", "u-boot-apollo-qemu.bin", "native.raw"):
        (tmp_path / name).touch()
    monkeypatch.setitem(sys.modules, "autosd_uki", SimpleNamespace(
        inspect_uki=lambda *args: pytest.fail("native mode must not inspect a host UKI")))
    monkeypatch.setitem(sys.modules, "autosd_disk", SimpleNamespace(
        inspect_disk=lambda path: {"partitions": {"efi": {"index": 1}}}))
    return runner.parser().parse_args([
        "--native-autosd-disk", str(tmp_path / "native.raw"),
        "--qemu", str(tmp_path / "qemu"), "--deploy-dir", str(tmp_path), *extra])


def test_native_plan_needs_no_manifest_kernel_initrd_or_bls(tmp_path, monkeypatch):
    args = native_args(tmp_path, monkeypatch)
    out = tmp_path / "out"
    plan = runner.make_plan(args, out)
    assert plan["autosd_mode"] == "ostree"
    assert plan["kernel"] is plan["initrd"] is None
    assert plan["uki"]["native_slots"] is True
    assert plan["uki"]["loader_files"] == {}
    assert plan["uki"]["payload_policy"] == "preserve-native-slots-and-bootctl"
    assert plan["command"][plan["command"].index("-kernel") + 1].endswith("u-boot-apollo-qemu.bin")
    assert "-initrd" not in plan["command"] and "-append" not in plan["command"]
    assert not out.exists()


def test_native_esp_override_is_explicit(tmp_path, monkeypatch):
    for name in ("ukibootaa64.efi", "slot_a.addon.efi", "slot_b.addon.efi"):
        (tmp_path / name).touch()
    args = native_args(tmp_path, monkeypatch, ["--ukiboot-dir", str(tmp_path),
                                            "--native-autosd-mode", "regular"])
    plan = runner.make_plan(args, tmp_path / "out")
    assert plan["autosd_mode"] == "regular"
    assert set(plan["uki"]["loader_files"]) == {"loader", "addon_a", "addon_b"}


@pytest.mark.parametrize("option", ["--uki", "--kernel", "--initrd", "--rootfs", "--dtb", "--bootargs"])
def test_native_mode_rejects_payload_overrides(tmp_path, monkeypatch, option):
    args = native_args(tmp_path, monkeypatch, [option, "override"])
    with pytest.raises(ValueError, match="cannot be combined"):
        runner.make_plan(args, tmp_path / "out")


def test_native_main_only_prepares_private_copy(tmp_path, monkeypatch):
    source = tmp_path / "native.raw"
    source.write_bytes(b"native slots and control")
    out = tmp_path / "out"
    plan = {"source_rootfs": str(source), "reused_disk": False,
            "uki": {"native_slots": True, "loader_files": {}}}
    calls = []
    def prepare_native(disk, **kwargs):
        assert disk == out / "rootfs.wic"
        assert disk.read_bytes() == source.read_bytes()
        calls.append((disk, kwargs))
        return {"payload_policy": "preserve-native-slots-and-bootctl"}
    monkeypatch.setattr(sys, "argv", ["launcher", "--headless", "--out-dir", str(out)])
    monkeypatch.setattr(runner, "make_plan", lambda *args: plan)
    monkeypatch.setattr(runner, "supervise", lambda *args, **kwargs: 0)
    monkeypatch.setitem(sys.modules, "autosd_uki", SimpleNamespace(
        prepare_uki=lambda *args: pytest.fail("native slots must not be rebuilt")))
    monkeypatch.setitem(sys.modules, "autosd_disk", SimpleNamespace(
        prepare_native_disk=prepare_native,
        prepare_disk=lambda *args: pytest.fail("native slots must not be replaced")))
    assert runner.main() == 0
    assert len(calls) == 1
    assert source.read_bytes() == b"native slots and control"
    assert not (out / "autosd.efi").exists()


def test_uboot_requires_uki(tmp_path):
    args = runner.parser().parse_args(["--uboot", "u-boot.bin"])
    with pytest.raises(ValueError, match="--uboot requires --uki"):
        runner.make_plan(args, tmp_path)


def test_uki_plan_uses_firmware_not_direct_linux(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "autosd_uki", SimpleNamespace(inspect_uki=lambda path: {"sha256": "test"}))
    monkeypatch.setitem(sys.modules, "autosd_disk", SimpleNamespace(inspect_disk=lambda path: {"partitions": {"efi": {"index": 1}}}))
    for name in ("source.efi", "u-boot-apollo-qemu.bin", "qemu", "disk.raw", "initrd",
                 "ukibootaa64.efi", "slot_a.addon.efi", "slot_b.addon.efi"):
        (tmp_path / name).touch()
    manifest = tmp_path / "autosd.json"
    manifest.write_text(json.dumps({"mode": "regular", "rootfs": str(tmp_path / "disk.raw"),
        "initrd": str(tmp_path / "initrd"), "bootargs": "console=ttyAMA0 root=test"}))
    args = runner.parser().parse_args(["--autosd", str(manifest), "--uki", str(tmp_path / "source.efi"),
        "--qemu", str(tmp_path / "qemu"), "--deploy-dir", str(tmp_path)])
    out = tmp_path / "out"
    plan = runner.make_plan(args, out)
    command = plan["command"]
    assert command[command.index("-kernel") + 1] == str(tmp_path / "u-boot-apollo-qemu.bin")
    assert "-initrd" not in command and "-append" not in command
    assert not any(arg.startswith("loader,file=") for arg in command)
    assert "fatload virtio 0:1" in plan["uki"]["boot_command"]
    assert plan["boot_method"] == "ukiboot-efi"
    assert plan["uki"]["bootargs"].endswith("efi=runtime")
    assert not out.exists()
    args.memory = "256M"
    with pytest.raises(ValueError, match="at least 1 GiB"):
        runner.make_plan(args, out)
    args.memory = "4080M"
    args.bootargs = "androidboot.slot_suffix=_b"
    with pytest.raises(ValueError, match="UKIBoot must select"):
        runner.make_plan(args, out)
    args.bootargs = None
    args.kernel = tmp_path / "Image"
    with pytest.raises(ValueError, match="cannot be combined"):
        runner.make_plan(args, out)


def prepared_run(tmp_path, monkeypatch):
    previous = tmp_path / "previous"
    previous.mkdir()
    disk = previous / "rootfs.wic"
    disk.write_bytes(b"updated slot payload must survive")
    original = tmp_path / "original.raw"
    original.touch()
    geometry = {"disk_size": 32, "sector_size": 512, "partitions": {"efi": {"index": 1}}}
    monkeypatch.setitem(sys.modules, "autosd_disk", SimpleNamespace(inspect_disk=lambda path: geometry.copy()))
    plan = {"boot_method": "ukiboot-efi", "autosd_mode": "regular",
            "disk_path": str(disk), "uki": {"prepared_disk": geometry.copy()}}
    (previous / "launch.json").write_text(json.dumps(plan))
    (previous / "result.json").write_text('{"status": "PASS"}')
    return previous, disk, {"mode": "regular", "rootfs": str(original)}, plan


def test_reuse_accepts_completed_prepared_disk_without_mutating_payload(tmp_path, monkeypatch):
    previous, disk, manifest, _ = prepared_run(tmp_path, monkeypatch)
    before = disk.read_bytes()
    assert runner.validate_reused_disk(previous, manifest)[0] == disk
    assert disk.read_bytes() == before


def test_native_plan_reuses_disk_without_external_uki(tmp_path, monkeypatch):
    previous, disk, manifest, _ = prepared_run(tmp_path, monkeypatch)
    for name in ("qemu", "u-boot-apollo-qemu.bin"):
        (tmp_path / name).touch()
    args = runner.parser().parse_args([
        "--native-autosd-disk", manifest["rootfs"], "--native-autosd-mode", "regular",
        "--reuse-autosd-disk", str(previous), "--qemu", str(tmp_path / "qemu"),
        "--deploy-dir", str(tmp_path)])
    plan = runner.make_plan(args, tmp_path / "out")
    assert plan["reused_disk"] is True
    assert plan["disk_path"] == str(disk)
    assert plan["kernel"] is plan["initrd"] is None
    assert plan["uki"]["native_slots"] is True
    args.ukiboot_dir = tmp_path
    with pytest.raises(ValueError, match="cannot replace ESP"):
        runner.make_plan(args, tmp_path / "out")


@pytest.mark.parametrize("invalid", ["original", "symlink", "hardlink", "incomplete", "mode", "geometry"])
def test_reuse_rejects_unproven_or_nonprivate_disk(tmp_path, monkeypatch, invalid):
    previous, disk, manifest, plan = prepared_run(tmp_path, monkeypatch)
    if invalid == "original":
        manifest["rootfs"] = str(disk)
    elif invalid == "symlink":
        disk.unlink()
        disk.symlink_to(manifest["rootfs"])
    elif invalid == "hardlink":
        runner.os.link(disk, tmp_path / "alias")
    elif invalid == "incomplete":
        (previous / "result.json").unlink()
    elif invalid == "mode":
        manifest["mode"] = "ostree"
    else:
        plan["uki"]["prepared_disk"]["disk_size"] += 1
        (previous / "launch.json").write_text(json.dumps(plan))
    with pytest.raises(ValueError):
        runner.validate_reused_disk(previous, manifest)


def test_reuse_requires_uki(tmp_path):
    args = runner.parser().parse_args(["--reuse-autosd-disk", str(tmp_path)])
    with pytest.raises(ValueError, match="requires --autosd and --uki"):
        runner.make_plan(args, tmp_path / "out")


def test_reuse_main_never_copies_or_rewrites_disk(tmp_path, monkeypatch):
    disk = tmp_path / "rootfs.wic"
    disk.write_bytes(b"preserved slots")
    out = tmp_path / "new-run"
    plan = {"reused_disk": True, "disk_path": str(disk), "uki": {"prepared_disk": {"yes": True}}}
    monkeypatch.setattr(sys, "argv", ["launcher", "--headless", "--out-dir", str(out)])
    monkeypatch.setattr(runner, "make_plan", lambda args, output: plan)
    monkeypatch.setattr(runner, "supervise", lambda *args, **kwargs: 0)
    monkeypatch.setattr(runner.subprocess, "run", lambda *args, **kwargs: pytest.fail("unexpected disk copy"))
    monkeypatch.setitem(sys.modules, "autosd_uki", SimpleNamespace(prepare_uki=lambda *args: pytest.fail("unexpected UKI rewrite")))
    monkeypatch.setitem(sys.modules, "autosd_disk", SimpleNamespace(prepare_disk=lambda *args: pytest.fail("unexpected slot rewrite")))
    assert runner.main() == 0
    assert disk.read_bytes() == b"preserved slots"
    assert not (out / "rootfs.wic").exists()


def test_supervisor_rejects_disk_locked_by_other_launcher(tmp_path):
    disk = tmp_path / "rootfs.wic"
    disk.touch()
    (tmp_path / "launch.json").write_text(json.dumps({"disk_path": str(disk), "reused_disk": True}))
    with disk.open("rb") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(ValueError, match="already used"):
            runner.supervise(tmp_path, 1, False)


def test_uki_reboot_resends_firmware_command_and_relogs_in(tmp_path):
    fake_guest(tmp_path, """
import sys, time
for boot in range(2):
    # Deliberately split the firmware banner across reads.
    print('\\nU-Bo', end='', flush=True)
    time.sleep(.05)
    print('ot 2025.10\\n=> ', end='', flush=True)
    assert sys.stdin.readline() == 'bootefi test\\n'
    print('localhost login: ', end='', flush=True)
    assert sys.stdin.readline() == 'root\\n'
    print('Password: ', end='', flush=True)
    assert sys.stdin.readline() == 'password\\n'
    print('[root@localhost ~]# ', end='', flush=True)
    time.sleep(.1)
""", bsp=False)
    path = tmp_path / "launch.json"
    plan = json.loads(path.read_text())
    plan.update(autosd_mode="regular", uki={"boot_command": "bootefi test\n"})
    path.write_text(json.dumps(plan))
    assert runner.supervise(tmp_path, 3, False) == 0
    result = json.loads((tmp_path / "result.json").read_text())
    assert result["firmware_boots_observed"] == 2
    assert not result["smoke_completed"]


def test_reboot_drops_previous_boot_success(tmp_path):
    fake_guest(tmp_path, """
import sys, time
print('U-Boot 2025.10\\n=> ', end='', flush=True)
sys.stdin.readline()
print('[root@localhost ~]# ', end='', flush=True)
time.sleep(.1)
print('\\nU-Boot 2025.10\\n=> ', end='', flush=True)
sys.stdin.readline()
time.sleep(20)
""", bsp=False)
    path = tmp_path / "launch.json"
    plan = json.loads(path.read_text())
    plan.update(autosd_mode="regular", uki={"boot_command": "bootefi test\n"})
    path.write_text(json.dumps(plan))
    assert runner.supervise(tmp_path, .5, False) == 124
    assert not json.loads((tmp_path / "result.json").read_text())["login_observed"]
