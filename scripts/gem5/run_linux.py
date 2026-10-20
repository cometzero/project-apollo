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
    p.add_argument("--bootloader", type=Path)
    p.add_argument("--bsp", action="store_true")
    p.add_argument("--cpus", type=int, choices=(4, 8, 16), default=4)
    p.add_argument("--channels", type=int, choices=(4, 8, 16), default=16)
    p.add_argument("--profile", type=Path, default=SOURCE / "configs/zena_cmn/profiles/a720ae_documented.yaml")
    p.add_argument("--workload", choices=("boot", "smoke", "cache", "dram", "command"), default="boot")
    p.add_argument("--command", help="guest shell command for --workload command (runs in initramfs)")
    p.add_argument("--size-kib", type=int)
    p.add_argument("--passes", type=int, default=2)
    p.add_argument("--bootargs", help="replace Linux command line")
    p.add_argument("--out-dir", type=Path)
    p.add_argument("--timeout", type=float, default=7200, help="host deadline in seconds (default: 7200)")
    p.add_argument("--max-ticks", type=int, default=10**15)
    p.add_argument("--headless", action="store_true", help="log UART without forwarding stdin")
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
    initrd = "nexios-bsp-initramfs" if args.bsp else "nexios-initramfs-image"
    native = deploy.parent.parent / "gem5-native"
    binary = args.gem5 or native / "gem5.opt"
    if not args.gem5 and not binary.is_file():
        binary = SOURCE / "build/ARM/gem5.opt"
    return {
        "gem5": str(required(binary)),
        "kernel": str(required(args.kernel or deploy / "Image")),
        "initrd": str(required(args.initrd or deploy / f"{initrd}-apollo-qvp.cpio.gz")),
        "rootfs": str(required(args.rootfs or deploy / f"{image}-apollo-qvp.wic")),
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


def prepare_initrd(base, out, args):
    data = base.read_bytes()
    if data.startswith(b"\x1f\x8b"):
        data = gzip.decompress(data)
    if not data.startswith((b"070701", b"070702")):
        raise ValueError("initrd must be a newc CPIO archive, optionally gzip compressed")
    if args.workload != "boot":
        overlay = bytearray()
        if args.workload in ("cache", "dram"):
            from benchmark import build_benchmark
            binary = build_benchmark(SOURCE, out / "guest")
            cpio_entry(overlay, "apollo-bench", binary.read_bytes())
            command = ["/apollo-bench", "--mode", args.workload, "--passes", str(args.passes)]
            if args.size_kib:
                command += ["--size-kib", str(args.size_kib)]
            command = shlex.join(command)
        elif args.workload == "smoke":
            command = "echo APOLLO_SMOKE=PASS"
        else:
            command = args.command
        script = f'''#!/bin/sh
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
mount -t proc proc /proc || exit 1
mount -t sysfs sysfs /sys || exit 1
mount -t devtmpfs devtmpfs /dev || exit 1
exec </dev/console >/dev/console 2>&1
echo APOLLO_ONLINE=$(cat /sys/devices/system/cpu/online)
uname -a
if ! {{ test "$(grep -c '^processor' /proc/cpuinfo)" = "{args.cpus}" &&
        test -b /dev/vda &&
        dd if=/dev/vda of=/dev/null bs=512 count=8; }}; then
    echo APOLLO_WORKLOAD_EXIT=1
    poweroff -f
    exit 1
fi
( {command}
)
status=$?
echo APOLLO_WORKLOAD_EXIT=$status
sync
poweroff -f
while :; do sleep 1; done
'''
        (out / "guest-init.sh").write_text(script)
        cpio_entry(overlay, "apollo-init", script.encode())
        cpio_entry(overlay, "TRAILER!!!", mode=0)
        overlay.extend(b"\0" * (-len(overlay) % 512))
        data += overlay
    target = out / "initrd.cpio"
    target.write_bytes(data)
    return target


def run(command, env, out, port, args):
    started = time.monotonic()
    connection = None
    timed_out = False
    observed = b""
    panic_started = None
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
                        uart.write(chunk)
                        uart.flush()
                        sys.stdout.buffer.write(chunk)
                        sys.stdout.buffer.flush()
                        if b"Kernel panic - not syncing" in observed:
                            if panic_started is None:
                                panic_started = time.monotonic()
                            if b"\n" in observed.split(b"Kernel panic - not syncing", 1)[1]:
                                break
                        if args.headless and args.workload == "boot" and (
                            b"login:" in observed or b"nexios-bsp#" in observed
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
    if (args.workload == "command") != bool(args.command):
        p.error("--workload command requires --command, and vice versa")
    inputs = resolve(args)
    if args.dry_run:
        print(json.dumps({"inputs": inputs, "cpus": args.cpus, "channels": args.channels, "workload": args.workload}, indent=2))
        return 0
    out = (args.out_dir or ROOT / "build/qbox-apollo-qvp/gem5" / time.strftime("%Y%m%d-%H%M%S")).resolve()
    out.mkdir(parents=True, exist_ok=False)
    print(f"gem5 output: {out}", flush=True)
    firmware = args.bootloader
    if firmware is None:
        firmware = out / "firmware" / f"zena_css{args.cpus}.elf"
        subprocess.run(["make", "-C", str(SOURCE / "system/arm/bootloader/zena_css"), f"BUILDDIR={firmware.parent}", str(firmware)], check=True)
    firmware = required(firmware)
    initrd = prepare_initrd(Path(inputs["initrd"]), out, args)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    bootargs = args.bootargs or "console=ttyAMA0,115200 earlycon=pl011,0x1a400000 lpj=1000000"
    if args.workload != "boot":
        bootargs += " rdinit=/apollo-init"
    elif not args.bootargs:
        bootargs += " rdinit=/init" if args.bsp else " rootwait root=PARTLABEL=rootro_a ro"
    command = [inputs["gem5"], "--listener-mode=on", f"--outdir={out / 'm5out'}", str(SOURCE / "configs/zena_cmn/run_fs.py"),
               f"--kernel={inputs['kernel']}", f"--bootloader={firmware}", f"--initrd={initrd}", f"--disk-image={inputs['rootfs']}",
               f"--profile={inputs['profile']}", f"--cpus={args.cpus}", f"--channels={args.channels}", f"--terminal-port={port}",
               f"--max-ticks={args.max_ticks}", f"--command-line={bootargs}"]
    env = os.environ.copy()
    if inputs["native_manifest"]:
        metadata = json.loads(Path(inputs["native_manifest"]).read_text())
        env["LD_LIBRARY_PATH"] = os.pathsep.join(metadata["library_path"])
        env["PYTHONHOME"] = metadata["python_home"]
    manifest = {"inputs": inputs, "command": command, "workload": args.workload,
                "model": "UNCALIBRATED_PROXY", "rootfs_access": "read-only base with in-memory COW",
                "gem5_sha256": sha256(inputs["gem5"]),
                "guest_initrd_sha256": sha256(initrd),
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
    if args.workload in ("cache", "dram") and rc == 0 and not timed_out:
        from benchmark import summarize
        try:
            result["measurement"] = summarize(out / "m5out", serial)
            result["status"] = "PASS"
        except (ValueError, KeyError, OSError) as exc:
            result["measurement_error"] = str(exc)
    elif args.workload in ("smoke", "command") and rc == 0 and not timed_out and "APOLLO_WORKLOAD_EXIT=0" in text:
        result["status"] = "PASS"
    elif args.workload == "boot" and (rc == 0 or timed_out or (args.headless and rc == -15)) and ("login:" in text or "nexios-bsp#" in text) and "Kernel panic" not in text:
        result["status"] = "BOOT_OBSERVED"
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(out), **result}, indent=2))
    return 0 if result["status"] in ("PASS", "BOOT_OBSERVED") else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        sys.exit(f"gem5 launcher: {exc}")
    except KeyboardInterrupt:
        sys.exit(130)
