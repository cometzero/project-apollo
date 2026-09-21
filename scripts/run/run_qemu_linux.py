#!/usr/bin/env python3
"""Boot Apollo Yocto or BSP Linux on the standalone QEMU Apollo machine."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import select
import shutil
import signal
import socket
import subprocess
import sys
import time

from run_qbox_linux import ROOT, console, required, start_tmux


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bsp", action="store_true", help="use BSP initramfs and boot/misc WIC")
    p.add_argument("--build-dir", type=Path, default=ROOT / "build")
    p.add_argument("--deploy-dir", type=Path)
    p.add_argument("--provider", type=Path, help="qemu-apollo-native deployment manifest")
    p.add_argument("--qemu", type=Path, help="override standalone qemu-system-aarch64")
    p.add_argument("--kernel", type=Path)
    p.add_argument("--initrd", type=Path)
    p.add_argument("--rootfs", type=Path)
    p.add_argument("--dtb", type=Path, help="override the machine-generated device tree")
    p.add_argument("--cpus", type=int, choices=range(1, 17), default=4)
    p.add_argument("--memory", default="4080M", help="Apollo DRAM size, default 4080M")
    p.add_argument("--bootargs", help="replace the default Linux command line")
    p.add_argument("--netdev", default="user,id=net0,hostfwd=tcp:127.0.0.1:2222-:22",
                   help="QEMU netdev using id=net0; use user,id=net0 for no host forwarding")
    p.add_argument("--out-dir", type=Path)
    p.add_argument("--session", default="qemu-linux")
    p.add_argument("--headless", action="store_true")
    p.add_argument("--no-attach", action="store_true")
    p.add_argument("--timeout", type=float, default=0, help="deadline in seconds; 0 means unlimited")
    p.add_argument("--exit-after-pass", action="store_true", help="exit after CPU and disk smoke checks")
    p.add_argument("--dry-run", action="store_true", help="print the plan without writing files")
    return p


def make_plan(args: argparse.Namespace, out: Path) -> dict:
    build = args.build_dir.absolute()
    deploy = (args.deploy_dir or build / "tmp_baremetal/deploy/images/apollo-qvp").absolute()
    environment = {}
    provider = args.provider or build / "tmp_baremetal/deploy/qemu-apollo-native/qemu-apollo-native.json"
    if args.qemu:
        executable = required(args.qemu, "QEMU executable")
    else:
        if not provider.is_file():
            raise ValueError(f"missing {provider}; build with ./yocto_build.sh --keep-conf qemu-apollo-native")
        manifest = json.loads(provider.read_text())
        executable = required(Path(manifest["executable"]), "QEMU executable")
        library_path = manifest.get("library_path", [])
        environment["LD_LIBRARY_PATH"] = ":".join(library_path) if isinstance(library_path, list) else library_path
    image = "nexios-bsp-initramfs" if args.bsp else "nexios-image"
    initrd_name = "nexios-bsp-initramfs" if args.bsp else "nexios-initramfs-image"
    kernel = required(args.kernel or deploy / "Image", "Linux Image")
    initrd = required(args.initrd or deploy / f"{initrd_name}-apollo-qvp.cpio.gz", "initramfs")
    disk = required(args.rootfs or deploy / f"{image}-apollo-qvp.wic", "WIC disk")
    bootargs = args.bootargs or "console=ttyAMA0 earlycon=pl011,0x1a400000 " + (
        "rdinit=/init" if args.bsp else "rootwait root=PARTLABEL=rootro_a ro"
    )
    command = [str(executable), "-machine", "apollo-qvp", "-accel", "tcg",
               "-smp", str(args.cpus), "-m", args.memory, "-display", "none",
               "-chardev", "socket,id=hmp,fd=@MONITOR_FD@",
               "-mon", "chardev=hmp,mode=readline",
               "-chardev", "stdio,id=uart,signal=off",
               "-serial", "chardev:uart", "-kernel", str(kernel), "-initrd", str(initrd),
               "-append", bootargs,
               "-drive", f"if=none,id=rootfs,format=raw,file={str(out / 'rootfs.wic').replace(',', ',,')}",
               "-device", "virtio-blk-device,drive=rootfs,bus=virtio-mmio-bus.0",
               "-netdev", args.netdev,
               "-device", "virtio-net-device,netdev=net0,bus=virtio-mmio-bus.1,mac=52:54:00:12:34:56",
               "-device", "virtio-rng-device,bus=virtio-mmio-bus.2"]
    if args.dtb:
        command += ["-dtb", str(required(args.dtb, "DTB"))]
    return {"command": command, "environment": environment, "bsp": args.bsp,
            "cpus": args.cpus, "source_rootfs": str(disk), "kernel": str(kernel),
            "initrd": str(initrd), "provider": str(provider) if not args.qemu else None,
            "layout": "Linux UART 70%; QEMU monitor and interactive shell 15% each"}


def supervise(out: Path, timeout: float, exit_after_pass: bool, *, echo_uart: bool = False) -> int:
    """Bridge QEMU stdio to the same persistent UART files as the tmux console."""
    plan = json.loads((out / "launch.json").read_text())
    started = time.monotonic()
    passed = login_sent = probe_sent = False
    bsp_selftest = "NOT_OBSERVED" if plan["bsp"] else "NOT_APPLICABLE"
    status, rc = "FAIL", 1
    (out / "qemu-monitor.in").touch(exist_ok=True)
    monitor, monitor_child = socket.socketpair()
    with monitor, monitor_child, (out / "qemu.log").open("ab", buffering=0) as log, \
         (out / "linux-uart.log").open("ab", buffering=0) as uart, \
         (out / "linux-uart.in").open("rb") as user_input, \
         (out / "qemu-monitor.log").open("ab", buffering=0) as monitor_log, \
         (out / "qemu-monitor.in").open("rb") as monitor_input:
        # A socketpair avoids TCP ports and UNIX pathname-length limits.
        command = [arg.replace("@MONITOR_FD@", str(monitor_child.fileno()))
                   for arg in plan["command"]]
        plan["executed_command"] = command
        (out / "launch.json").write_text(json.dumps(plan, indent=2) + "\n")
        child = subprocess.Popen(command, cwd=ROOT,
                                 env={**os.environ, **plan["environment"]},
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=log, start_new_session=True, bufsize=0,
                                 pass_fds=(monitor_child.fileno(),))
        monitor_child.close()
        monitor.setblocking(False)
        monitor_pending = b""
        monitor_open = True
        (out / "qemu.pid").write_text(str(child.pid) + "\n")

        def interrupted(_signum: int, _frame: object) -> None:
            raise KeyboardInterrupt

        old_handlers = {sig: signal.signal(sig, interrupted)
                        for sig in (signal.SIGTERM, signal.SIGHUP)}
        observed = b""
        try:
            while True:
                ready, writable, _ = select.select(
                    [child.stdout, *([monitor] if monitor_open else [])],
                    [monitor] if monitor_pending and monitor_open else [], [], 0.05)
                if monitor in ready:
                    data = monitor.recv(65536)
                    monitor_log.write(data)
                    monitor_open = bool(data)
                if monitor in writable:
                    monitor_pending = monitor_pending[monitor.send(monitor_pending):]
                if monitor_open:
                    monitor_pending += monitor_input.read(4096)
                if child.stdout in ready:
                    data = os.read(child.stdout.fileno(), 65536)
                    uart.write(data)
                    if echo_uart and data:
                        sys.stdout.buffer.write(data)
                        sys.stdout.buffer.flush()
                    observed = (observed + data)[-65536:]
                if plan["bsp"]:
                    if b"NEXIOS_BSP_INITRAMFS_FAILED" in observed:
                        bsp_selftest = "FAIL"
                    elif b"NEXIOS_BSP_INITRAMFS_READY" in observed and bsp_selftest != "FAIL":
                        bsp_selftest = "PASS"
                if b"Kernel panic - not syncing:" in observed:
                    break
                prompt = re.search(rb"(?:nexios-bsp(?:-failed)?#|root@[^\r\n]*[#>]|~ #)\s*$", observed)
                boot_ready = prompt if plan["bsp"] else re.search(rb"(?:apollo-qvp|nexios)[^\r\n]* login:\s*$", observed)
                if prompt or boot_ready:
                    if not exit_after_pass:
                        passed = True
                    elif not login_sent:
                        child.stdin.write(b"\n" if plan["bsp"] or prompt else b"root\n")
                        login_sent = True
                if exit_after_pass and login_sent and prompt and not probe_sent:
                    # Split the marker so the echoed command cannot satisfy it.
                    child.stdin.write((
                        "uname -a && "
                        f"test \"$(grep -c '^processor' /proc/cpuinfo)\" -eq {plan['cpus']} && "
                        "test -b /dev/vda && dd if=/dev/vda of=/dev/null bs=512 count=8 && "
                        "printf 'QEMU_LINUX_%s\\n' SMOKE_DONE\n"
                    ).encode())
                    probe_sent = True
                if probe_sent and b"QEMU_LINUX_SMOKE_DONE" in observed:
                    passed, status, rc = True, "PASS", 0
                    break
                if child.poll() is not None:
                    rc = child.returncode or (0 if passed else 1)
                    status = "PASS" if passed and rc == 0 else "FAIL"
                    break
                pending = user_input.read(4096)
                if pending:
                    child.stdin.write(pending)
                if timeout and time.monotonic() - started >= timeout:
                    status, rc = ("PASS", 0) if passed else ("TIMEOUT", 124)
                    break
        except KeyboardInterrupt:
            status, rc = ("PASS", 0) if passed else ("STOPPED", 130)
        except BrokenPipeError:
            status, rc = "FAIL", 1
        finally:
            for sig, handler in old_handlers.items():
                signal.signal(sig, handler)
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
            child.stdin.close()
            child.stdout.close()
            monitor.close()
            (out / "result.json").write_text(json.dumps({
                "status": status, "login_observed": passed, "bsp_selftest": bsp_selftest,
                "returncode": rc, "elapsed_seconds": time.monotonic() - started,
                "smoke_completed": bool(probe_sent and passed),
                "qualification": "Standalone QEMU AP boot only; not full BSP qualification",
            }, indent=2) + "\n")
    return rc


def main() -> int:
    if len(sys.argv) > 2 and sys.argv[1] == "console":
        return console(Path(sys.argv[2]))
    if len(sys.argv) > 2 and sys.argv[1] == "monitor":
        return console(Path(sys.argv[2]), "qemu-monitor.log", "qemu-monitor.in")
    if len(sys.argv) > 2 and sys.argv[1] == "supervise":
        return supervise(Path(sys.argv[2]), float(sys.argv[3]), bool(int(sys.argv[4])))
    args = parser().parse_args()
    if args.timeout < 0:
        raise ValueError("--timeout must be non-negative")
    out = (args.out_dir or args.build_dir / "qemu-apollo-qvp" /
           (time.strftime("%Y%m%d-%H%M%S") + f"-{os.getpid()}")).absolute()
    plan = make_plan(args, out)
    print(json.dumps(plan, indent=2), flush=True)
    if args.dry_run:
        return 0
    if not args.headless and not shutil.which("tmux"):
        raise ValueError("tmux is required; use --headless otherwise")
    out.mkdir(parents=True, exist_ok=False)
    for name in ("linux-uart.log", "linux-uart.in", "qemu.log", "qemu-monitor.log", "qemu-monitor.in"):
        (out / name).touch()
    subprocess.run(["cp", "--reflink=auto", "--sparse=always", plan["source_rootfs"],
                    str(out / "rootfs.wic")], check=True)
    (out / "launch.json").write_text(json.dumps(plan, indent=2) + "\n")
    if args.headless:
        return supervise(out, args.timeout, args.exit_after_pass, echo_uart=True)
    start_tmux(args, out, script=Path(__file__).resolve(), program="QEMU",
               log_name="qemu.log", key_prefix="qemu-linux-",
               bottom_command=[sys.executable, str(Path(__file__).resolve()), "monitor", str(out)])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"run_qemu_linux: {error}", file=sys.stderr)
        raise SystemExit(1)
