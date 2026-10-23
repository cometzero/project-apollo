"""Exercise QEMU stdio supervision without requiring a full guest boot."""

import importlib.util
import fcntl
import json
from pathlib import Path
import sys
import subprocess

import pytest


RUN_DIR = Path(__file__).resolve().parents[1] / "scripts/run"
sys.path.insert(0, str(RUN_DIR))
SPEC = importlib.util.spec_from_file_location("qemu_linux", RUN_DIR / "run_qemu_linux.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)
sys.path.pop(0)


@pytest.fixture(autouse=True)
def saturn_dtb(tmp_path):
    source = '/dts-v1/; / { chosen { bootargs = "console=ttyAMA0,115200 mem=4064M nr_cpus=4 rdinit=/init"; }; };'
    path = tmp_path / "apollo-qvp-saturn-v.dtb"
    subprocess.run(["dtc", "-I", "dts", "-O", "dtb", "-o", str(path)],
                   input=source, text=True, check=True)
    return path


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


def test_supervisor_rejects_disk_locked_by_other_launcher(tmp_path):
    disk = tmp_path / "rootfs.wic"
    disk.touch()
    (tmp_path / "launch.json").write_text(json.dumps({"disk_path": str(disk)}))
    with disk.open("rb") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(ValueError, match="already used"):
            runner.supervise(tmp_path, 1, False)


@pytest.mark.parametrize("mode", ["dma", "pio"])
def test_i2s_mode_selects_machine_dt(tmp_path, mode):
    for name in ("Image", "qemu", "nexios-bsp-initramfs-apollo-qvp.cpio.gz",
                 "nexios-bsp-initramfs-apollo-qvp.wic"):
        (tmp_path / name).touch()
    args = runner.parser().parse_args([
        "--bsp", "--qemu", str(tmp_path / "qemu"),
        "--deploy-dir", str(tmp_path), "--i2s-mode", mode,
    ])
    plan = runner.make_plan(args, tmp_path / "private")
    machine = plan["command"][plan["command"].index("-machine") + 1]
    assert machine == ("apollo-qvp,i2s-dma=off" if mode == "pio" else "apollo-qvp")
    args.dtb = tmp_path / "external.dtb"
    args.dtb.write_bytes((tmp_path / "apollo-qvp-saturn-v.dtb").read_bytes())
    override = runner.make_plan(args, tmp_path / "private")
    assert override["command"][-2:] == ["-dtb", str(args.dtb)]


@pytest.mark.parametrize("cpus", [1, 4, 16])
def test_saturn_input_is_unchanged_and_cpu_count_is_forwarded(tmp_path, saturn_dtb, cpus):
    for name in ("Image", "qemu", "nexios-bsp-initramfs-apollo-qvp.cpio.gz",
                 "nexios-bsp-initramfs-apollo-qvp.wic"):
        (tmp_path / name).touch()
    before = saturn_dtb.read_bytes()
    args = runner.parser().parse_args([
        "--bsp", "--qemu", str(tmp_path / "qemu"), "--deploy-dir", str(tmp_path),
        "--cpus", str(cpus),
    ])
    plan = runner.make_plan(args, tmp_path / "out")
    assert plan["command"][-2:] == ["-dtb", str(saturn_dtb)]
    assert f"nr_cpus={cpus}" in plan["bootargs"].split()
    assert "mem=4064M" in plan["bootargs"].split()
    assert saturn_dtb.read_bytes() == before
    args.bootargs = "console=ttyAMA0 custom=1"
    assert runner.make_plan(args, tmp_path / "out")["bootargs"] == args.bootargs


@pytest.mark.parametrize("bsp", [True, False])
@pytest.mark.parametrize("cpus", [4, 16])
def test_plan_uses_manifest_population_without_legacy_dtb(tmp_path, saturn_dtb, bsp, cpus):
    image = "nexios-bsp-initramfs" if bsp else "nexios-image"
    initrd = "nexios-bsp-initramfs" if bsp else "nexios-initramfs-image"
    for name in ("Image", "qemu", f"{image}-apollo-qvp.wic", f"{initrd}-apollo-qvp.cpio.gz"):
        (tmp_path / name).touch()
    saturn_dtb.unlink()
    selected = tmp_path / f"selected-{cpus}.dtb"
    source = '/dts-v1/; / { chosen { bootargs = "console=ttyAMA0 nr_cpus=4"; }; cpus { '
    source += " ".join(f'cpu@{cpu:x} {{ device_type = "cpu"; }};' for cpu in range(cpus))
    source += ' }; };'
    subprocess.run(["dtc", "-I", "dts", "-O", "dtb", "-o", str(selected)],
                   input=source, text=True, capture_output=True, check=True)
    (tmp_path / f"{image}-apollo-qvp.qboxconf").write_text(json.dumps({
        "images": {"dtb": selected.name}, "env": {"QBOX_APOLLO_NUM_CPUS": str(cpus)},
    }))
    args = runner.parser().parse_args([
        "--qemu", str(tmp_path / "qemu"), "--deploy-dir", str(tmp_path),
        *(["--bsp"] if bsp else []),
    ])
    plan = runner.make_plan(args, tmp_path / "out")
    assert plan["source_dtb"] == str(selected)
    assert plan["cpus"] == cpus
    assert f"nr_cpus={cpus}" in plan["bootargs"]
    assert not (tmp_path / "out").exists()

@pytest.mark.parametrize("option", ['--autosd', '--uki', '--uboot', '--ukiboot-dir', '--native-autosd-disk', '--native-autosd-mode', '--reuse-autosd-disk'])
def test_removed_autosd_options_are_rejected(option):
    with pytest.raises(SystemExit) as error:
        runner.parser().parse_args([option, "unused"])
    assert error.value.code == 2
