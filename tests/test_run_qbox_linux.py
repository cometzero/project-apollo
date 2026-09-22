"""Exercise the direct-Linux supervisor and tmux geometry without QBox."""

import importlib.util
import argparse
import json
from pathlib import Path
import subprocess
import sys
import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/run/run_qbox_linux.py"
SPEC = importlib.util.spec_from_file_location("qbox_linux_runner", SCRIPT)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def test_autosd_and_bsp_are_mutually_exclusive():
    with pytest.raises(SystemExit):
        runner.parser().parse_args(["--bsp", "--autosd", "manifest.json"])


@pytest.mark.parametrize("changes", [{"mode": "invalid"}, {"rootfs": "relative.raw"},
                                     {"initrd": None}, {"bootargs": ""}])
def test_autosd_manifest_rejects_invalid_fields(tmp_path, changes):
    manifest = {"mode": "regular", "rootfs": "/disk.raw", "initrd": "/initrd",
                "bootargs": "console=ttyAMA0"}
    manifest.update(changes)
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        runner.autosd_manifest(path)


def test_autosd_console_does_not_repeat_credentials_or_probe():
    console = runner.AutoSDConsole("ostree", 4, "QBOX_LINUX")
    for prompt, reply in [(b"localhost login: ", b"root\n"),
                          (b"Password: ", b"password\n")]:
        assert console.respond(prompt, True) == reply
        assert console.respond(prompt, True) == b""
    probe = console.respond(b"[root@localhost ~]# ", True)
    assert b"ostree admin status" in probe
    assert b"rpm-ostree" not in probe
    assert b"erofs" not in probe
    assert b'test "$(findmnt -n -o FSTYPE -T /)" = overlay &&' in probe
    assert b"losetup -a;" in probe
    assert b"findmnt -T" in probe and b"getenforce; systemctl --failed --no-pager;" in probe
    assert b"QBOX_LINUX_SMOKE_DONE" not in probe
    assert console.respond(b"[root@localhost ~]# ", True) == b""


def test_prepare_keeps_initramfs_bytes_without_overlay(monkeypatch, tmp_path):
    helper = SCRIPT.parents[2] / "hsoc-stack/tools/qbox-platform/platforms/apollo/linux-boot/prepare.py"
    spec = importlib.util.spec_from_file_location("linux_boot_prepare", helper)
    prepare = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prepare)
    commands = []

    def command(*args):
        commands.append(args)
        return ""

    monkeypatch.setattr(prepare, "command", command)
    kernel = tmp_path / "Image"
    kernel.write_bytes(b"\0" * 56 + b"ARM\x64" + b"\0" * 4)
    dtb = tmp_path / "source.dtb"
    dtb.write_bytes(b"test dtb")
    initrd = tmp_path / "bsp.cpio.gz"
    original = b"original initramfs bytes"
    initrd.write_bytes(original)
    output = tmp_path / "boot"
    result = prepare.prepare(argparse.Namespace(
        kernel=kernel, dtb=dtb, initrd=initrd, output_dir=output,
        bootargs="rdinit=/init", cpus=4, disk=False,
    ))
    assert result["initrd"] == str(initrd.resolve())
    assert initrd.read_bytes() == original
    assert not (output / "linux-initramfs.cpio.gz").exists()
    for node in ("/soc/si_remoteproc", "/soc/si_remoteproc/si-cl1"):
        assert any(call[-3:] == (node, "status", "okay") for call in commands)


def test_prepare_firmware_entry_and_no_external_initrd(monkeypatch, tmp_path):
    import struct
    helper = SCRIPT.parents[2] / "hsoc-stack/tools/qbox-platform/platforms/apollo/linux-boot/prepare.py"
    spec = importlib.util.spec_from_file_location("efi_boot_prepare", helper)
    prepare = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prepare)
    commands = []
    monkeypatch.setattr(prepare, "command", lambda *args: commands.append(args) or "")
    firmware = tmp_path / "u-boot.bin"
    header = bytearray(64)
    header[56:60] = b"ARM\x64"
    struct.pack_into("<Q", header, 8, 0x80000)
    firmware.write_bytes(header)
    dtb = tmp_path / "source.dtb"
    dtb.write_bytes(b"test dtb")
    args = argparse.Namespace(kernel=firmware, dtb=dtb, initrd=None, output_dir=tmp_path / "boot",
                              bootargs="", cpus=4, disk=True, firmware=True)
    result = prepare.prepare(args)
    assert result["addresses"]["kernel"] == 0x80080000
    assert any("BOOT_ENTRY=2148007936" in call for call in commands)
    assert result["initrd"] is None
    args.initrd = dtb
    with pytest.raises(ValueError, match="embeds initrd"):
        prepare.prepare(args)


@pytest.mark.parametrize("efi,slot,success", [(True, True, True), (False, True, True),
                                            (True, False, True), (True, True, False)])
def test_efi_supervisor_requires_firmware_and_slot_evidence(tmp_path, monkeypatch, efi, slot, success):
    from types import SimpleNamespace
    monkeypatch.setitem(sys.modules, "autosd_disk", SimpleNamespace(inspect_disk=lambda path: {
        "bootctl": {"valid": True, "slots": [{"successful_boot": int(success), "tries_remaining": 0}]}}))
    make_plan(tmp_path, f"""
import pathlib, sys, time
p = pathlib.Path(sys.argv[1])
def output(text):
    with (p/'linux-uart.log').open('a') as stream: stream.write(text)
def wait_for(text):
    while text not in (p/'linux-uart.in').read_text(): time.sleep(.01)
output('U-Boot 2025.10\\n=> ')
wait_for('bootefi test\\n')
output('\\n[root@localhost ~]# ')
wait_for('SMOKE_DONE')
assert 'ukibootctl get-booted' in (p/'linux-uart.in').read_text()
if {efi}: output('\\nAPOLLO_EFI_BOOTED\\n')
if {slot}: output('\\nAPOLLO_UKIBOOT_SLOT=0\\n')
output('\\nQBOX_LINUX_SMOKE_DONE\\n')
time.sleep(30)
""")
    path = tmp_path / "launch.json"
    plan = json.loads(path.read_text())
    plan.update(bsp=False, autosd_mode="regular", uki={"boot_command": "bootefi test\n"})
    path.write_text(json.dumps(plan))
    expected = (0 if success else 1) if efi and slot else 124
    assert runner.supervise(tmp_path, 1, True) == expected
    result = json.loads((tmp_path / "result.json").read_text())
    assert result["efi_reboot_support"] == "NOT_IMPLEMENTED"


def test_efi_reboot_is_explicitly_unsupported(tmp_path, monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setitem(sys.modules, "autosd_disk", SimpleNamespace(inspect_disk=lambda path: {
        "bootctl": {"valid": True}}))
    make_plan(tmp_path, """
import pathlib, sys, time
p = pathlib.Path(sys.argv[1])
with (p/'linux-uart.log').open('a') as stream:
    stream.write('U-Boot 2025.10\\n=> ')
while 'bootefi test' not in (p/'linux-uart.in').read_text(): time.sleep(.01)
with (p/'linux-uart.log').open('a') as stream:
    stream.write('\\nU-Boot 2025.10\\n=> ')
time.sleep(30)
""")
    path = tmp_path / "launch.json"
    plan = json.loads(path.read_text())
    plan.update(bsp=False, autosd_mode="regular", uki={"boot_command": "bootefi test\n"})
    path.write_text(json.dumps(plan))
    assert runner.supervise(tmp_path, 3, False) == 1
    assert json.loads((tmp_path / "result.json").read_text())["status"] == "UNSUPPORTED_REBOOT"


def make_plan(tmp_path, program):
    for name in ("linux-uart.log", "linux-uart.in"):
        (tmp_path / name).touch()
    (tmp_path / "launch.json").write_text(
        json.dumps(
            {
                "command": [sys.executable, "-c", program, str(tmp_path)],
                "environment": {},
                "pass_marker": "nexios-bsp(?:-failed)?#",
                "bsp": True,
            }
        )
    )


def test_autosd_supervisor_password_and_ostree_probe(tmp_path):
    make_plan(tmp_path, """
import pathlib, sys, time
p = pathlib.Path(sys.argv[1])
def wait_for(value):
    while value not in (p/'linux-uart.in').read_text():
        time.sleep(.01)
def output(value):
    with (p/'linux-uart.log').open('a') as stream:
        stream.write(value)
output('localhost login: ')
wait_for('root\\n')
output('\\nPassword: ')
wait_for('password\\n')
output('\\n[root@localhost ~]# ')
wait_for('SMOKE_DONE')
command = (p/'linux-uart.in').read_text()
assert 'ostree admin status' in command and '/run/ostree-booted' in command
assert 'dd if=/dev/vda' in command and '-eq 4' in command
output('\\nQBOX_LINUX_SMOKE_DONE\\n')
time.sleep(30)
""")
    path = tmp_path / "launch.json"
    plan = json.loads(path.read_text())
    plan.update(bsp=False, autosd_mode="ostree", environment={"QBOX_APOLLO_NUM_CPUS": "4"})
    path.write_text(json.dumps(plan))
    assert runner.supervise(tmp_path, 5, True) == 0
    result = json.loads((tmp_path / "result.json").read_text())
    assert result["status"] == "PASS"
    assert result["autosd_mode"] == "ostree"
    assert "no OTA or secure boot qualification" in result["qualification"]


@pytest.mark.parametrize("failed", [False, True])
@pytest.mark.parametrize("disk", [False, True])
def test_smoke_waits_for_guest_command_response(tmp_path, failed, disk):
    make_plan(
        tmp_path,
        """
import pathlib, sys, time
p = pathlib.Path(sys.argv[1])
(p/'linux-uart.log').write_text('BSP_MARKER\\nBSP_PROMPT ')
while b'SMOKE_DONE' not in (p/'linux-uart.in').read_bytes():
    time.sleep(.01)
with (p/'linux-uart.log').open('a') as f:
    f.write('Linux test\\nprocessor : 0\\nQBOX_LINUX_SMOKE_DONE\\n')
time.sleep(30)
""".replace("BSP_MARKER", "NEXIOS_BSP_INITRAMFS_FAILED" if failed else "NEXIOS_BSP_INITRAMFS_READY")
        .replace("BSP_PROMPT", "nexios-bsp-failed#" if failed else "nexios-bsp#"),
    )
    plan_path = tmp_path / "launch.json"
    plan = json.loads(plan_path.read_text())
    plan["source_rootfs"] = "bsp.wic" if disk else None
    plan_path.write_text(json.dumps(plan))
    assert runner.supervise(tmp_path, 5, True) == 0
    assert json.loads((tmp_path / "result.json").read_text())["status"] == "PASS"
    assert json.loads((tmp_path / "result.json").read_text())["bsp_selftest"] == (
        "FAIL" if failed else "PASS"
    )
    assert b"uname -a && cat /proc/cpuinfo" in (tmp_path / "linux-uart.in").read_bytes()
    assert (b"dd if=/dev/vda" in (tmp_path / "linux-uart.in").read_bytes()) == disk


def test_kernel_panic_fails_without_waiting_for_timeout(tmp_path):
    make_plan(
        tmp_path,
        "import pathlib, sys, time; "
        "(pathlib.Path(sys.argv[1])/'linux-uart.log').write_text("
        "'Kernel panic - not syncing: test'); time.sleep(30)",
    )
    assert runner.supervise(tmp_path, 5, True) == 1
    assert json.loads((tmp_path / "result.json").read_text())["status"] == "FAIL"


def test_no_uart_marker_times_out(tmp_path):
    make_plan(tmp_path, "import time; time.sleep(30)")
    assert runner.supervise(tmp_path, 0.2, True) == 124
    assert json.loads((tmp_path / "result.json").read_text())["status"] == "TIMEOUT"


def test_tmux_geometry_and_console_selection(monkeypatch, tmp_path):
    calls = []
    sourced = []

    def output(command, **kwargs):
        calls.append(command)
        if command[1] == "list-keys":
            return "bind-key -T root MouseDown1Pane select-pane -t ="
        if command[1] == "source-file":
            sourced.append(kwargs["input"])
        return "%1" if command[1] == "new-session" else "%2"

    monkeypatch.setattr(runner.subprocess, "check_output", output)
    monkeypatch.setattr(
        runner.subprocess, "run", lambda *a, **kw: subprocess.CompletedProcess(a, 1)
    )
    args = runner.parser().parse_args(["--no-attach"])
    runner.start_tmux(args, tmp_path)
    splits = [c for c in calls if c[1] == "split-window"]
    assert splits[0][2:6] == ["-v", "-l", "30%", "-P"]
    assert splits[1][2:5] == ["-h", "-l", "50%"]
    assert ["tmux", "select-pane", "-t", "%1"] in calls
    assert sourced == ["bind-key -T qbox-linux-1 MouseDown1Pane select-pane -t =\n"]
    assert ["tmux", "bind-key", "-T", "qbox-linux-1", "F12", "kill-session"] in calls
    assert ["tmux", "set-option", "-t", "qbox-linux", "mouse", "on"] in calls
    assert [
        "tmux", "set-option", "-t", "qbox-linux", "key-table", "qbox-linux-1"
    ] in calls


def test_tmux_layout_failure_cleans_up_new_session(monkeypatch, tmp_path):
    calls = []

    def output(command, **kwargs):
        if command[1] == "new-session":
            return "%1"
        raise subprocess.CalledProcessError(1, command)

    def run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 1)

    monkeypatch.setattr(runner.subprocess, "check_output", output)
    monkeypatch.setattr(runner.subprocess, "run", run)
    args = runner.parser().parse_args(["--no-attach", "--session", "new-test-session"])
    with pytest.raises(subprocess.CalledProcessError):
        runner.start_tmux(args, tmp_path)
    assert calls[-1] == ["tmux", "kill-session", "-t", "=new-test-session"]


def make_deploy(monkeypatch, tmp_path):
    for name in (
        "Image",
        "apollo-qvp.dtb",
        "platforms-vp",
        "platform.lua",
        "nexios-image-apollo-qvp.qboxconf",
        "nexios-image-apollo-qvp.wic",
        "nexios-initramfs-image-apollo-qvp.cpio.gz",
        "nexios-bsp-initramfs-apollo-qvp.qboxconf",
        "nexios-bsp-initramfs-apollo-qvp.cpio.gz",
        "nexios-bsp-initramfs-apollo-qvp.wic",
    ):
        (tmp_path / name).touch()
    monkeypatch.setattr(
        runner,
        "provider_environment",
        lambda *a: {
            "QBOXCONF_EXE": str(tmp_path / "platforms-vp"),
            "QBOXCONF_LD_LIBRARY_PATH": "",
        },
    )
    return [
        str(SCRIPT),
        "--dry-run",
        "--deploy-dir",
        str(tmp_path),
        "--conf",
        str(tmp_path / "platform.lua"),
    ]


def test_product_uses_verity_initramfs_and_readonly_slot(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(sys, "argv", make_deploy(monkeypatch, tmp_path))
    assert runner.main() == 0
    plan = json.loads(capsys.readouterr().out)
    env = plan["environment"]
    assert env["QBOX_LINUX_INITRD"] == str(
        tmp_path / "nexios-initramfs-image-apollo-qvp.cpio.gz"
    )
    assert env["QBOX_LINUX_BOOTARGS"].endswith("rootwait root=PARTLABEL=rootro_a ro")
    assert plan["source_rootfs"] == str(tmp_path / "nexios-image-apollo-qvp.wic")


def test_bsp_keeps_its_original_initramfs_and_init(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(sys, "argv", make_deploy(monkeypatch, tmp_path) + ["--bsp"])
    assert runner.main() == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["environment"]["QBOX_LINUX_INITRD"] == str(
        tmp_path / "nexios-bsp-initramfs-apollo-qvp.cpio.gz"
    )
    assert plan["environment"]["QBOX_LINUX_BOOTARGS"].endswith(
        "rdinit=/init"
    )
    assert plan["source_rootfs"] == str(tmp_path / "nexios-bsp-initramfs-apollo-qvp.wic")
    assert plan["environment"]["QBOX_RDASPEN_ROOTFS"].endswith("/rootfs.wic")
    assert "root=" not in plan["environment"]["QBOX_LINUX_BOOTARGS"]


def test_bsp_disk_override(monkeypatch, tmp_path, capsys):
    arguments = make_deploy(monkeypatch, tmp_path)
    disk = tmp_path / "custom.wic"
    disk.touch()
    monkeypatch.setattr(sys, "argv", arguments + ["--bsp", "--rootfs", str(disk)])
    assert runner.main() == 0
    assert json.loads(capsys.readouterr().out)["source_rootfs"] == str(disk)


def test_bsp_missing_disk_does_not_fall_back_to_product(monkeypatch, tmp_path):
    arguments = make_deploy(monkeypatch, tmp_path)
    (tmp_path / "nexios-bsp-initramfs-apollo-qvp.wic").unlink()
    monkeypatch.setattr(sys, "argv", arguments + ["--bsp"])
    with pytest.raises(ValueError, match="missing BSP WIC disk"):
        runner.main()


def test_product_initrd_override_wins(monkeypatch, tmp_path, capsys):
    arguments = make_deploy(monkeypatch, tmp_path)
    override = tmp_path / "custom.cpio.gz"
    override.touch()
    monkeypatch.setattr(sys, "argv", arguments + ["--initrd", str(override)])
    assert runner.main() == 0
    assert json.loads(capsys.readouterr().out)["environment"][
        "QBOX_LINUX_INITRD"
    ] == str(override)
