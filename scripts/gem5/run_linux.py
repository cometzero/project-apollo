#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Boot Apollo Yocto Linux on the AP-only gem5 CHI model."""

import argparse
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import select
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "hsoc-stack/tools/gem5"


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--build-dir", type=Path, default=ROOT / "build")
    p.add_argument("--deploy-dir", type=Path)
    p.add_argument("--gem5", type=Path)
    p.add_argument("--kernel", type=Path)
    p.add_argument("--initrd", type=Path)
    p.add_argument("--rootfs", type=Path)
    p.add_argument("--bootloader", type=Path, help="override deployed gem5 PSCI firmware")
    p.add_argument("--benchmark", type=Path, help="override deployed apollo-bench binary")
    p.add_argument("--bsp", action="store_true")
    snapshot = p.add_mutually_exclusive_group()
    snapshot.add_argument("--checkpoint", type=Path, help="save a booted initramfs snapshot to a new directory, then exit")
    snapshot.add_argument("--resume", type=Path, help="resume a saved initramfs snapshot and run the selected workload")
    p.add_argument("--cpus", type=int, choices=(4, 16), default=4)
    p.add_argument("--channels", type=int, choices=(4, 8, 16), default=16)
    p.add_argument("--interleave-bytes", type=int, choices=(64, 512, 1024), default=64,
                   help="DRAM channel stripe; Home-node stripe remains 64 bytes")
    p.add_argument("--profile", type=Path, default=SOURCE / "configs/zena_cmn/profiles/a720ae_documented.yaml")
    p.add_argument("--workload", choices=("boot", "smoke", "cache", "dram", "dram-multicore", "command"), default="boot")
    p.add_argument("--workers", type=int, choices=(1, 4, 8, 16),
                   help="dram-multicore pinned workers (default: --cpus)")
    p.add_argument("--memory-mode", choices=("read", "copy", "triad"),
                   help="dram-multicore operation (default: read)")
    commands = p.add_mutually_exclusive_group()
    commands.add_argument("--command", help="guest shell command for --workload command (runs in initramfs)")
    commands.add_argument("--command-file", type=Path, help="host shell script for --workload command, delivered through readfile")
    p.add_argument("--size-kib", type=int,
                   help="working set in KiB; dram-multicore uses this size per array (read 1, copy 2, triad 3)")
    p.add_argument("--passes", type=int, default=2)
    p.add_argument("--bootargs", help="replace Linux command line")
    p.add_argument("--out-dir", type=Path)
    p.add_argument("--timeout", type=float, default=7200, help="host deadline in seconds (default: 7200)")
    p.add_argument("--max-ticks", type=int, default=10**15)
    p.add_argument("--headless", action="store_true", help="log UART without forwarding stdin")
    p.add_argument("--session", default="apollo-gem5", help="tmux session name")
    p.add_argument("--no-attach", action="store_true", help="create tmux session without attaching")
    p.add_argument("--direct", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--dry-run", action="store_true", help="print resolved inputs without building or running")
    return p


def required(path):
    path = path.resolve()
    if not path.is_file():
        raise ValueError(f"missing file: {path}")
    return path


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(args):
    deploy = (args.deploy_dir or args.build_dir / "tmp_baremetal/deploy/images/apollo-qvp").resolve()
    image = "nexios-bsp-initramfs" if args.bsp else "nexios-image"
    initrd = "nexios-bsp-initramfs" if args.bsp else "nexios-gem5-initramfs"
    native = deploy.parent.parent / "gem5-native"
    binary = args.gem5 or native / "gem5.opt"
    if not args.gem5 and not binary.is_file():
        binary = SOURCE / "build/ARM/gem5.opt"
    firmware = args.bootloader or deploy / "gem5" / f"zena_css{args.cpus}.elf"
    benchmark = args.benchmark
    if args.bsp and benchmark is None:
        benchmark = deploy / "gem5/apollo-bench"
    try:
        firmware = required(firmware)
        benchmark = required(benchmark) if benchmark and args.workload in ("cache", "dram") else None
    except ValueError as exc:
        raise ValueError(f"{exc}; build with ./yocto_build.sh --keep-conf gem5-apollo-guest") from exc
    return {
        "bootloader": str(firmware),
        "benchmark": str(benchmark) if benchmark else None,
        "gem5": str(required(binary)),
        "kernel": str(required(args.kernel or deploy / "Image")),
        "initrd": str(required(args.initrd or deploy / f"{initrd}-apollo-qvp.cpio.gz")),
        "rootfs": str(required(args.rootfs or deploy / f"{image}-apollo-qvp.wic")) if args.rootfs or args.bsp else None,
        "profile": str(required(args.profile)),
        "native_manifest": str(native / "gem5-native.json") if binary.resolve() == (native / "gem5.opt").resolve() and (native / "gem5-native.json").is_file() else None,
    }


def cpio_entry(archive, name, data=b"", mode=0o100755):
    encoded = name.encode() + b"\0"
    fields = (1, mode, 0, 0, 1, 0, len(data), 0, 0, 0, 0, len(encoded), 0)
    archive.extend(b"070701" + b"".join(f"{value:08x}".encode() for value in fields))
    archive.extend(encoded)
    archive.extend(b"\0" * (-len(archive) % 4))
    archive.extend(data)
    archive.extend(b"\0" * (-len(archive) % 4))


def prepare_initrd(base, out, args, benchmark=None):
    data = base.read_bytes()
    if data.startswith(b"\x1f\x8b"):
        data = gzip.decompress(data)
    if not data.startswith((b"070701", b"070702")):
        raise ValueError("initrd must be a newc CPIO archive, optionally gzip compressed")
    (out / "guest-init.sh").write_text("")
    if args.workload != "boot":
        overlay = bytearray()
        if args.workload in ("cache", "dram"):
            if benchmark:
                cpio_entry(overlay, "apollo-bench" if args.bsp else "usr/bin/apollo-bench", required(Path(benchmark)).read_bytes())
            command = ["/apollo-bench" if args.bsp else "/usr/bin/apollo-bench", "--mode", args.workload, "--passes", str(args.passes)]
            if args.size_kib:
                command += ["--size-kib", str(args.size_kib)]
            command = shlex.join(command)
        elif args.workload == "dram-multicore":
            mode = args.memory_mode or "read"
            command = shlex.join([
                "/usr/bin/apollo-memory-bench", "--mode", "stream" if mode == "triad" else mode,
                "--kernel", "neon" if mode == "read" else "scalar",
                "--workers", str(args.workers or args.cpus), "--passes", str(args.passes),
                "--array-mib", str((args.size_kib or 65536) // 1024),
                "--initialize-before-switch",
            ])
        elif args.workload == "smoke":
            command = "echo APOLLO_SMOKE=PASS"
        else:
            command = (args.command_file.read_text() if getattr(args, "command_file", None)
                       else args.command)
        mounts = "mount -t proc proc /proc || exit 1\nmount -t sysfs sysfs /sys || exit 1\nmount -t devtmpfs devtmpfs /dev || exit 1" if args.bsp else ""
        disk_check = "test -b /dev/vda && dd if=/dev/vda of=/dev/null bs=512 count=8" if args.rootfs or args.bsp else ":"
        script = f'''#!/bin/sh
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
{mounts}
exec </dev/console >/dev/console 2>&1
shutdown_guest() {{
    sync
    if command -v poweroff >/dev/null 2>&1; then
        poweroff -f
    else
        # The minimal BusyBox package omits poweroff; use the kernel handler.
        echo o > /proc/sysrq-trigger
    fi
}}
echo APOLLO_ONLINE=$(cat /sys/devices/system/cpu/online)
uname -a
if ! {{ test "$(grep -c '^processor' /proc/cpuinfo)" = "{args.cpus}" &&
        {disk_check}; }}; then
    echo APOLLO_WORKLOAD_EXIT=1
    shutdown_guest
    exit 1
fi
( {command}
)
status=$?
echo APOLLO_WORKLOAD_EXIT=$status
shutdown_guest
while :; do sleep 1; done
'''
        (out / "guest-init.sh").write_text(script)
        if args.bsp:
            cpio_entry(overlay, "apollo-init", script.encode())
        if overlay:
            cpio_entry(overlay, "TRAILER!!!", mode=0)
            overlay.extend(b"\0" * (-len(overlay) % 512))
            data += overlay
    target = out / "initrd.cpio"
    target.write_bytes(data)
    return target


def checkpoint_contract(inputs, initrd, args, bootargs):
    return {
        "schema": 1,
        "sha256": {name: sha256(inputs[name]) for name in ("gem5", "kernel", "bootloader", "profile")},
        "initrd_sha256": sha256(initrd),
        "configuration_sha256": {path.name: sha256(path) for path in sorted((SOURCE / "configs/zena_cmn").glob("*.py"))},
        "cpus": args.cpus, "channels": args.channels,
        "interleave_bytes": args.interleave_bytes, "bootargs": bootargs,
    }


def validate_checkpoint(path, contract):
    metadata = json.loads((path / "apollo-checkpoint.json").read_text())
    if metadata.get("status") != "COMPLETE" or not (path / "m5.cpt").is_file():
        raise ValueError("checkpoint is incomplete")
    if json.loads((path / "launcher.json").read_text()) != contract:
        raise ValueError("checkpoint inputs changed: use the original gem5, kernel, initramfs and configuration")


def run(command, env, out, port, args):
    started = time.monotonic()
    connection = None
    timed_out = False
    observed = b""
    panic_started = None
    milestones = {}
    with (out / "gem5.log").open("wb") as log, (out / "uart.log").open("wb") as uart:
        child = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        try:
            while child.poll() is None:
                if panic_started is not None and time.monotonic() - panic_started >= 2:
                    break
                if time.monotonic() - started >= args.timeout:
                    timed_out = True
                    break
                if connection is None:
                    try:
                        connection = socket.create_connection(("127.0.0.1", port), timeout=0.1)
                        connection.setblocking(False)
                    except OSError:
                        time.sleep(0.1)
                        continue
                readers = [connection]
                if not args.headless and sys.stdin.isatty():
                    readers.append(sys.stdin)
                ready, _, _ = select.select(readers, [], [], 0.1)
                if connection in ready:
                    try:
                        chunk = connection.recv(65536)
                    except ConnectionResetError:
                        chunk = b""
                    if chunk:
                        observed = (observed + chunk)[-65536:]
                        for name, marker in (
                            ("first_uart", b""),
                            ("linux_start", b"Booting Linux on physical CPU"),
                            ("initramfs_ready", b"NEXIOS_GEM5_INITRAMFS_READY"),
                        ):
                            if name not in milestones and marker in observed:
                                milestones[name] = time.monotonic() - started
                                (out / "boot-timings.json").write_text(json.dumps(milestones, indent=2) + "\n")
                        uart.write(chunk)
                        uart.flush()
                        sys.stdout.buffer.write(chunk)
                        sys.stdout.buffer.flush()
                        if b"NEXIOS_GEM5_INITRAMFS_FAILED" in observed:
                            break
                        if b"Kernel panic - not syncing" in observed:
                            if panic_started is None:
                                panic_started = time.monotonic()
                            if b"\n" in observed.split(b"Kernel panic - not syncing", 1)[1]:
                                break
                        if args.headless and args.workload == "boot" and (
                            b"login:" in observed or b"nexios-bsp#" in observed or b"nexios-gem5#" in observed
                        ):
                            break
                    else:
                        connection.close()
                        connection = None
                if sys.stdin in ready and connection is not None:
                    try:
                        connection.sendall(os.read(sys.stdin.fileno(), 4096))
                    except BrokenPipeError:
                        connection.close()
                        connection = None
        finally:
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
            if connection is not None:
                connection.close()
    return child.returncode, timed_out, time.monotonic() - started


def main():
    p = parser()
    args = p.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0 or args.max_ticks <= 0:
        p.error("timeout and max-ticks must be finite and positive")
    if not 1 <= args.passes <= 1024 or (args.size_kib is not None and not 1 <= args.size_kib <= 262144):
        p.error("passes must be 1..1024 and size-kib must be 1..262144")
    if args.workers is not None and (args.workload != "dram-multicore" or args.workers > args.cpus):
        p.error("--workers requires dram-multicore and must not exceed --cpus")
    if args.memory_mode is not None and args.workload != "dram-multicore":
        p.error("--memory-mode requires --workload dram-multicore")
    if args.workload == "dram-multicore":
        if args.bsp or args.benchmark:
            p.error("dram-multicore requires the gem5 initramfs without a benchmark override")
        if args.passes not in (1, 2, 4, 8) or (args.size_kib is not None and args.size_kib % 1024):
            p.error("dram-multicore requires passes 1|2|4|8 and size-kib in whole MiB")
    if (args.workload == "command") != bool(args.command or args.command_file):
        p.error("--workload command requires --command or --command-file, and vice versa")
    if args.command_file and not args.command_file.is_file():
        p.error("--command-file must name an existing file")
    if (args.checkpoint or args.resume) and (args.bsp or args.rootfs or args.benchmark):
        p.error("checkpoint/resume requires the diskless gem5 initramfs without a benchmark override")
    if args.checkpoint and args.workload != "boot":
        p.error("--checkpoint requires --workload boot; select a workload with --resume")
    if args.checkpoint and args.checkpoint.exists():
        p.error("checkpoint destination already exists; choose a new directory")
    inputs = resolve(args)
    if args.dry_run:
        print(json.dumps({"inputs": inputs, "cpus": args.cpus, "channels": args.channels,
                          "interleave_bytes": args.interleave_bytes, "workload": args.workload,
                          "memory_mode": (args.memory_mode or "read") if args.workload == "dram-multicore" else None,
                          "workers": args.workers or args.cpus if args.workload == "dram-multicore" else None}, indent=2))
        return 0
    out = (args.out_dir or ROOT / "build/qbox-apollo-qvp/gem5" / time.strftime("%Y%m%d-%H%M%S")).resolve()
    if not args.headless and not args.direct:
        if not shutil.which("tmux"):
            raise ValueError("tmux is required; use --headless otherwise")
        if out.exists():
            raise ValueError(f"output directory already exists: {out}")
        sys.path.insert(0, str(ROOT / "scripts/run"))
        from run_qbox_linux import start_tmux
        start_tmux(
            args, out, program="gem5", log_name="gem5.log", key_prefix="gem5-linux-",
            console_command=[sys.executable, str(Path(__file__).resolve()),
                             *sys.argv[1:], "--direct", "--out-dir", str(out)],
        )
        return 0
    out.mkdir(parents=True, exist_ok=False)
    print(f"gem5 output: {out}", flush=True)
    firmware = Path(inputs["bootloader"])
    initrd = prepare_initrd(Path(inputs["initrd"]), out, args, inputs["benchmark"])
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    bootargs = args.bootargs or "console=ttyAMA0,115200 earlycon=pl011,0x1a400000"
    if not args.bootargs or args.workload != "boot" or args.checkpoint or args.resume:
        bootargs += " rdinit=/apollo-init" if args.bsp and args.workload != "boot" else " rdinit=/init"
    if args.checkpoint or args.resume:
        bootargs += " gem5.checkpoint=1"
    command = [inputs["gem5"], "--listener-mode=on", f"--outdir={out / 'm5out'}", str(SOURCE / "configs/zena_cmn/run_fs.py"),
               f"--kernel={inputs['kernel']}", f"--bootloader={firmware}", f"--initrd={initrd}",
               f"--profile={inputs['profile']}", f"--cpus={args.cpus}", f"--channels={args.channels}", f"--terminal-port={port}",
               f"--interleave-bytes={args.interleave_bytes}",
               f"--max-ticks={args.max_ticks}", f"--command-line={bootargs}"]
    if inputs["rootfs"]:
        command.append(f"--disk-image={inputs['rootfs']}")
    if not args.bsp:
        command.append(f"--readfile={out / 'guest-init.sh'}")
    contract = None
    if args.checkpoint or args.resume:
        contract = checkpoint_contract(inputs, initrd, args, bootargs)
        if args.resume:
            validate_checkpoint(args.resume.resolve(), contract)
            command.append(f"--restore={args.resume.resolve()}")
        else:
            command.append(f"--checkpoint-dir={args.checkpoint.resolve()}")
    env = os.environ.copy()
    if inputs["native_manifest"]:
        metadata = json.loads(Path(inputs["native_manifest"]).read_text())
        env["LD_LIBRARY_PATH"] = os.pathsep.join(metadata["library_path"])
        env["PYTHONHOME"] = metadata["python_home"]
    manifest = {"inputs": inputs, "command": command, "workload": args.workload,
                "interleave_bytes": args.interleave_bytes,
                "memory_mode": (args.memory_mode or "read") if args.workload == "dram-multicore" else None,
                "model": "UNCALIBRATED_PROXY", "rootfs_access": "read-only base with in-memory COW" if inputs["rootfs"] else "none",
                "gem5_sha256": sha256(inputs["gem5"]),
                "guest_initrd_sha256": sha256(initrd),
                "bootloader_sha256": sha256(firmware),
                "benchmark_sha256": sha256(inputs["benchmark"]) if inputs["benchmark"] else None,
                "gem5_revision": subprocess.check_output(["git", "-C", str(SOURCE), "rev-parse", "HEAD"], text=True).strip(),
                "gem5_worktree_dirty": bool(subprocess.check_output(
                    ["git", "-C", str(SOURCE), "status", "--porcelain"], text=True))}
    (out / "launch.json").write_text(json.dumps(manifest, indent=2) + "\n")
    rc, timed_out, elapsed = run(command, env, out, port, args)
    terminal = out / "m5out/system.platform.terminal"
    # gem5's terminal file also retains bytes emitted before the socket connected.
    serial = terminal if terminal.is_file() else out / "uart.log"
    text = serial.read_text(errors="replace")
    result = {"status": "FAIL", "returncode": rc, "timeout": timed_out, "host_seconds": elapsed,
              "qualification": "UNCALIBRATED_AP_MODEL", "workload": args.workload}
    if args.checkpoint:
        evidence = out / "m5out/exit.json"
        if rc == 0 and not timed_out and evidence.is_file() and json.loads(evidence.read_text()).get("status") == "CHECKPOINT_SAVED":
            metadata = args.checkpoint / "apollo-checkpoint.json"
            if metadata.is_file() and json.loads(metadata.read_text()).get("status") == "COMPLETE" and (args.checkpoint / "m5.cpt").is_file():
                temporary = args.checkpoint / "launcher.json.tmp"
                temporary.write_text(json.dumps(contract, indent=2) + "\n")
                temporary.replace(args.checkpoint / "launcher.json")
                result.update(status="CHECKPOINT_SAVED", checkpoint=str(args.checkpoint.resolve()))
    elif args.workload == "dram-multicore" and rc == 0 and not timed_out and "APOLLO_WORKLOAD_EXIT=0" in text:
        from benchmark import summarize_multicore
        try:
            result["measurement"] = summarize_multicore(
                out / "m5out", serial, workers=args.workers or args.cpus,
                size_bytes=(args.size_kib or 65536) * 1024,
                passes=args.passes, channels=args.channels, mode=args.memory_mode or "read")
            result["status"] = "PASS"
        except (ValueError, KeyError, OSError) as exc:
            result["measurement_error"] = str(exc)
    elif args.workload in ("cache", "dram") and rc == 0 and not timed_out:
        from benchmark import summarize
        try:
            result["measurement"] = summarize(
                out / "m5out", serial, mode=args.workload, passes=args.passes,
                size_bytes=(args.size_kib or (32 if args.workload == "cache" else 65536)) * 1024)
            result["status"] = "PASS"
        except (ValueError, KeyError, OSError) as exc:
            result["measurement_error"] = str(exc)
    elif args.workload in ("smoke", "command") and rc == 0 and not timed_out and "APOLLO_WORKLOAD_EXIT=0" in text:
        result["status"] = "PASS"
    elif args.workload == "boot" and (rc == 0 or timed_out or (args.headless and rc == -15)) and ("login:" in text or "nexios-bsp#" in text or "nexios-gem5#" in text) and "Kernel panic" not in text:
        result["status"] = "BOOT_OBSERVED"
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(out), **result}, indent=2))
    return 0 if result["status"] in ("PASS", "BOOT_OBSERVED", "CHECKPOINT_SAVED") else 1


def stop_requested(signum, frame):
    # Unwind run() so tmux session teardown also reaps the simulator.
    raise KeyboardInterrupt


if __name__ == "__main__":
    signal.signal(signal.SIGHUP, stop_requested)
    signal.signal(signal.SIGTERM, stop_requested)
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        sys.exit(f"gem5 launcher: {exc}")
    except KeyboardInterrupt:
        sys.exit(130)
