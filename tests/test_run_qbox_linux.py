"""Exercise the direct-Linux supervisor and tmux geometry without QBox."""

import importlib.util
import argparse
import json
from pathlib import Path
import subprocess
import sys
import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/run/run_qbox_linux.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("qbox_linux_runner", SCRIPT)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


@pytest.mark.parametrize("initrd_size", [23, 4097])
def test_prepare_keeps_initramfs_bytes_without_overlay(monkeypatch, tmp_path, initrd_size):
    helper = SCRIPT.parents[2] / "hsoc-stack/tools/qbox-platform/platforms/apollo/linux-boot/prepare.py"
    spec = importlib.util.spec_from_file_location("linux_boot_prepare", helper)
    prepare = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prepare)
    commands = []

    def command(*args):
        commands.append(args)
        return "rdinit=/init" if args[0] == "fdtget" else ""

    monkeypatch.setattr(prepare, "command", command)
    kernel = tmp_path / "Image"
    kernel.write_bytes(b"\0" * 56 + b"ARM\x64" + b"\0" * 4)
    dtb = tmp_path / "source.dtb"
    dtb.write_bytes(b"test dtb")
    initrd = tmp_path / "bsp.cpio.gz"
    original = b"x" * initrd_size
    initrd.write_bytes(original)
    output = tmp_path / "boot"
    result = prepare.prepare(argparse.Namespace(
        kernel=kernel, dtb=dtb, initrd=initrd, output_dir=output,
        bootargs="rdinit=/init",
    ))
    assert result["addresses"]["boot_stub"] == 0x000f0000
    assert result["initrd"] == str(initrd.resolve())
    assert initrd.read_bytes() == original
    assert not (output / "linux-initramfs.cpio.gz").exists()
    edits = [call for call in commands if call[0] == "fdtput"]
    assert edits == []
    assert any(f"INITRD_SIZE={initrd_size}" in call for call in commands)
    assert any("INITRD_START=2415919104" in call for call in commands)
    assert (output / "linux.dtb").read_bytes() == dtb.read_bytes()
    assert not any("-r" in call for call in commands)


def make_plan(tmp_path, program):
    for name in ("linux-uart.log", "linux-uart.in"):
        (tmp_path / name).touch()
    (tmp_path / "launch.json").write_text(
        json.dumps(
            {
                "command": [sys.executable, "-c", program, str(tmp_path)],
                "environment": {"QBOX_RDASPEN_ROOTFS": str(tmp_path / "source.wic")},
                "pass_marker": "nexios-bsp(?:-failed)?#",
                "bsp": True,
            }
        )
    )


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


@pytest.mark.parametrize("marker", ["Kernel panic - not syncing: test", "LINUX_BOOT_FDT_FAILED"])
def test_boot_failure_fails_without_waiting_for_timeout(tmp_path, marker):
    make_plan(
        tmp_path,
        "import pathlib, sys, time; "
        "(pathlib.Path(sys.argv[1])/'linux-uart.log').write_text("
        f"{marker!r}); time.sleep(30)",
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
    monkeypatch.setattr(runner.subprocess, "check_output",
                        lambda *a, **kw: "console=ttyAMA0,115200 mem=4064M nr_cpus=4 rdinit=/init")
    for name in (
        "Image",
        "apollo-qvp-saturn-v.dtb",
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


@pytest.mark.parametrize("copy_disk", [False, True])
@pytest.mark.parametrize("bsp", [False, True])
def test_disk_selection_and_copy(monkeypatch, tmp_path, capsys, copy_disk, bsp):
    arguments = make_deploy(monkeypatch, tmp_path)
    arguments.remove("--dry-run")
    out = tmp_path / "run"
    arguments += ["--headless", "--out-dir", str(out)]
    if bsp:
        arguments.append("--bsp")
    if copy_disk:
        arguments.append("--copy-disk")
    source = tmp_path / (("nexios-bsp-initramfs" if bsp else "nexios-image") +
                         "-apollo-qvp.wic")
    source.write_bytes(b"original disk")

    def output(command, **kwargs):
        if command[0] == "fdtget":
            return "console=ttyAMA0 nr_cpus=4"
        assert command[1].endswith("/linux-boot/prepare.py")
        return json.dumps({"boot_stub": str(out / "boot.bin"),
                           "dtb": str(out / "linux.dtb"), "initrd": None})

    monkeypatch.setattr(runner.subprocess, "check_output", output)
    monkeypatch.setattr(runner, "supervise", lambda *a, **kw: 0)
    monkeypatch.setattr(sys, "argv", arguments)
    assert runner.main() == 0
    plan = json.loads((out / "launch.json").read_text())
    selected = out / "rootfs.wic" if copy_disk else source
    assert plan["environment"]["QBOX_RDASPEN_ROOTFS"] == str(selected)
    assert plan["copy_disk"] is copy_disk
    assert (out / "rootfs.wic").exists() is copy_disk
    assert selected.read_bytes() == b"original disk"
    assert source.read_bytes() == b"original disk"

def test_product_uses_verity_initramfs_and_readonly_slot(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(sys, "argv", make_deploy(monkeypatch, tmp_path))
    assert runner.main() == 0
    plan = json.loads(capsys.readouterr().out)
    env = plan["environment"]
    assert env["QBOX_LINUX_INITRD"] == str(
        tmp_path / "nexios-initramfs-image-apollo-qvp.cpio.gz"
    )
    assert plan["bootargs"].endswith("rootwait root=PARTLABEL=rootro_a ro")
    assert plan["source_rootfs"] == str(tmp_path / "nexios-image-apollo-qvp.wic")


@pytest.mark.parametrize("selection", ["canonical", "manifest", "explicit"])
def test_dtb_selection_preserves_override_and_manifest_priority(
    monkeypatch, tmp_path, capsys, selection,
):
    argv = make_deploy(monkeypatch, tmp_path)
    canonical = tmp_path / "apollo-qvp-saturn-v.dtb"
    legacy = tmp_path / "apollo-qvp.dtb"
    legacy.symlink_to(canonical.name)
    explicit = tmp_path / "profile.dtb"
    explicit.touch()
    environment = runner.provider_environment(None, None)
    if selection != "canonical":
        environment["QBOXCONF_IMAGE_AP_DTB"] = str(legacy)
    monkeypatch.setattr(runner, "provider_environment", lambda *args: environment)
    if selection == "explicit":
        argv += ["--dtb", str(explicit)]
    monkeypatch.setattr(sys, "argv", argv)

    assert runner.main() == 0
    selected = json.loads(capsys.readouterr().out)["source_dtb"]
    assert selected == str({"canonical": canonical, "manifest": legacy, "explicit": explicit}[selection])


@pytest.mark.parametrize("configured,requested,explicit", [
    (4, None, None), (16, None, None), (4, 16, None), (4, 16, 16), (4, 16, 4),
])
def test_direct_model_and_selected_dtb_populations_must_match(
    monkeypatch, tmp_path, capsys, configured, requested, explicit,
):
    argv = make_deploy(monkeypatch, tmp_path)
    population = explicit if explicit is not None else configured
    dtb = tmp_path / "selected.dtb"
    source = '/dts-v1/; / { cpus { ' + " ".join(
        f'cpu@{cpu:x} {{ device_type = "cpu"; }};' for cpu in range(population)
    ) + ' }; };'
    subprocess.run(["dtc", "-I", "dts", "-O", "dtb", "-o", str(dtb)],
                   input=source, text=True, capture_output=True, check=True)
    environment = runner.provider_environment(None, None)
    environment.update(QBOXCONF_IMAGE_AP_DTB=str(dtb), QBOXCONF_APOLLO_NUM_CPUS=str(configured))
    monkeypatch.setattr(runner, "provider_environment", lambda *args: environment)
    if requested is not None:
        argv += ["--cpus", str(requested)]
    if explicit is not None:
        argv += ["--dtb", str(dtb)]
    monkeypatch.setattr(sys, "argv", argv)
    expected = requested or configured
    if expected != population:
        with pytest.raises(ValueError, match="image manifest selects|describes .* CPUs"):
            runner.main()
    else:
        assert runner.main() == 0
        plan = json.loads(capsys.readouterr().out)
        assert plan["environment"]["QBOX_APOLLO_NUM_CPUS"] == str(expected)


def test_dashboard_ssh_is_pinned_to_loopback(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(sys, "argv", make_deploy(monkeypatch, tmp_path) + ["--ssh-port", "2245"])
    assert runner.main() == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["environment"]["QBOX_APOLLO_NETDEV"] == "type=user,hostfwd=tcp:127.0.0.1:2245-:22"


@pytest.mark.parametrize("port", ["22", "65536", "-1"])
def test_invalid_ssh_port_rejected(monkeypatch, tmp_path, port):
    monkeypatch.setattr(sys, "argv", make_deploy(monkeypatch, tmp_path) + ["--ssh-port", port])
    with pytest.raises(ValueError, match="ssh-port"):
        runner.main()


def test_guest_poweroff_releases_owned_simulator(tmp_path):
    make_plan(tmp_path, """
import pathlib, sys, time
p = pathlib.Path(sys.argv[1])
with (p/'linux-uart.log').open('a') as stream:
    stream.write('reboot: Power down\\n')
time.sleep(30)
""")
    assert runner.supervise(tmp_path, 2, False) == 0
    result = json.loads((tmp_path / "result.json").read_text())
    assert result["status"] == "POWERED_OFF"
    assert result["poweroff_observed"] is True
    assert result["login_observed"] is False


def test_bsp_keeps_its_original_initramfs_and_init(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(sys, "argv", make_deploy(monkeypatch, tmp_path) + ["--bsp"])
    assert runner.main() == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["environment"]["QBOX_LINUX_INITRD"] == str(
        tmp_path / "nexios-bsp-initramfs-apollo-qvp.cpio.gz"
    )
    assert plan["bootargs"] == (
        "console=ttyAMA0,115200 mem=4064M nr_cpus=4 rdinit=/init"
    )
    assert plan["source_rootfs"] == str(tmp_path / "nexios-bsp-initramfs-apollo-qvp.wic")
    assert plan["environment"]["QBOX_RDASPEN_ROOTFS"] == plan["source_rootfs"]
    assert plan["copy_disk"] is False
    assert "root=" not in plan["bootargs"]


def test_bsp_cpu_override_preserves_dtb_defaults(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(sys, "argv", make_deploy(monkeypatch, tmp_path) +
                        ["--bsp", "--cpus", "2"])
    assert runner.main() == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["bootargs"] == (
        "console=ttyAMA0,115200 mem=4064M nr_cpus=2 rdinit=/init"
    )

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


@pytest.mark.parametrize("options", [["--stats"], ["--stats-interval", "2"]])
def test_stats_enable_monitor_and_qmp(monkeypatch, tmp_path, capsys, options):
    monkeypatch.setattr(sys, "argv", make_deploy(monkeypatch, tmp_path) + options)
    assert runner.main() == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["monitor"]["enabled"]
    assert plan["qmp_enabled"]
    assert plan["environment"]["QBOX_APOLLO_MONITOR"] == "true"

@pytest.mark.parametrize("option", ['--autosd', '--uki', '--uboot', '--ukiboot-dir'])
def test_removed_autosd_options_are_rejected(option):
    with pytest.raises(SystemExit) as error:
        runner.parser().parse_args([option, "unused"])
    assert error.value.code == 2
