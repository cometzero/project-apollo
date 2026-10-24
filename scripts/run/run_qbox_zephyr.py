#!/usr/bin/env python3
"""Boot the standalone Apollo SI CL1 Zephyr ELF using the Yocto QBox provider."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import math
import os
import re
from pathlib import Path
import signal
import struct
import subprocess
import sys
import time

from run_qbox_linux import ROOT, console, provider_environment, required, start_tmux

BASE = 0x140000000
SIZE = 8 * 1024 * 1024
BOOT_MARKER = b"SI_CL1_BOOT_RESULT status=PASS cpu_mask=f counter_hz=100000000"


def boot_complete(uart: bytes) -> bool:
    cpus = set(re.findall(rb"SI_CL1_BOOT_CPU cpu=([0-3])(?:\s|$)", uart))
    return cpus == {b"0", b"1", b"2", b"3"} and BOOT_MARKER in uart


def elf_payload(path: Path) -> tuple[int, bytes]:
    """Extract ELF64 little-endian AArch64 PT_LOAD bytes without a host toolchain."""
    data = path.read_bytes()
    if len(data) < 64 or data[:6] != b"\x7fELF\x02\x01":
        raise ValueError("expected a little-endian ELF64 image")
    if struct.unpack_from("<H", data, 18)[0] != 183:
        raise ValueError("expected an AArch64 ELF image")
    entry, phoff = struct.unpack_from("<QQ", data, 24)
    entsize, count = struct.unpack_from("<HH", data, 54)
    if entsize < 56 or phoff + entsize * count > len(data):
        raise ValueError("invalid ELF program header table")
    payload = bytearray()
    executable_entry = False
    for index in range(count):
        kind, flags, offset, vaddr, paddr, filesz, memsz, _ = struct.unpack_from(
            "<IIQQQQQQ", data, phoff + index * entsize)
        if kind != 1 or memsz == 0:
            continue
        if filesz > memsz or offset + filesz > len(data):
            raise ValueError("invalid ELF segment size")
        if paddr < BASE or paddr + memsz > BASE + SIZE:
            raise ValueError("ELF load segment is outside CL1 LLRAM")
        if flags & 1 and vaddr <= entry < vaddr + memsz:
            executable_entry = True
        end = paddr - BASE + filesz
        if len(payload) < end:
            payload.extend(b"\0" * (end - len(payload)))
        payload[paddr - BASE:end] = data[offset:offset + filesz]
    if not payload or not executable_entry or not BASE <= entry < BASE + SIZE:
        raise ValueError("ELF entry is not in executable CL1 LLRAM")
    return entry, bytes(payload)


def supervise(out: Path, timeout: float, exit_after_pass: bool) -> int:
    plan = json.loads((out / "run.json").read_text())
    interrupted = False
    def stop(_signum, _frame):
        nonlocal interrupted
        interrupted = True
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, stop)
    started = time.monotonic()
    booted = False
    status, rc = "ERROR", 1
    with (out / "qbox.log").open("wb") as log:
        child = subprocess.Popen(plan["command"], env={**os.environ, **plan["environment"]},
                                 stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                 cwd=ROOT, start_new_session=True)
        (out / "qbox.pid").write_text(str(child.pid) + "\n")
        try:
            while True:
                uart = (out / "zephyr-uart.log").read_bytes()
                booted = booted or boot_complete(uart)
                if interrupted:
                    status, rc = "INTERRUPTED", 130
                    break
                if booted and exit_after_pass:
                    status, rc = "PASS", 0
                    break
                if child.poll() is not None:
                    status, rc = ("PASS", 0) if booted and child.returncode == 0 else ("FAIL", 1)
                    break
                if timeout and time.monotonic() - started >= timeout:
                    status, rc = ("PASS", 0) if booted else ("TIMEOUT", 124)
                    break
                time.sleep(0.1)
        finally:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
    result = {"status": status, "boot_marker_observed": booted,
              "scope": "Zephyr standalone boot only; not benchmark or hardware qualification",
              "qbox_returncode": child.returncode, "elapsed_seconds": time.monotonic() - started}
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)
    return rc


def main() -> int:
    if len(sys.argv) > 2 and sys.argv[1] == "console":
        return console(Path(sys.argv[2]), "zephyr-uart.log", "zephyr-uart.in")
    if len(sys.argv) > 2 and sys.argv[1] == "supervise":
        return supervise(Path(sys.argv[2]), float(sys.argv[3]), bool(int(sys.argv[4])))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build")
    parser.add_argument("--deploy-dir", type=Path)
    parser.add_argument("--qboxconf", type=Path)
    parser.add_argument("--elf", type=Path)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--session", default="qbox-zephyr")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--no-attach", action="store_true")
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--exit-after-pass", action="store_true", help="stop after all four guest boot CPU markers and final boot result")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--platform-param", action="append", default=[])
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout < 0:
        parser.error("--timeout must be finite and nonnegative (0 disables timeout)")
    deploy = args.deploy_dir or args.build_dir / "tmp_baremetal/deploy/images/apollo-qvp"
    elf = required(args.elf or deploy / "zephyr-si-cl1-boot.elf", "Zephyr ELF")
    entry, payload = elf_payload(elf)
    default_conf = deploy / "nexios-bsp-initramfs-apollo-qvp.qboxconf"
    if not default_conf.exists():
        default_conf = deploy / "nexios-image-apollo-qvp.qboxconf"
    conf = required(args.qboxconf or default_conf, "QBox provider")
    env = provider_environment(conf, args.build_dir.absolute())
    executable = required(Path(env["QBOXCONF_EXE"]), "QBox executable")
    out = (args.out_dir or ROOT / "build/qbox-apollo-qvp/zephyr" / datetime.now().strftime("%Y%m%d-%H%M%S-%f")).absolute()
    command = [str(executable), "-l", str(ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-zephyr.lua")]
    for param in args.platform_param:
        command.extend(["-p", param])
    launch_env = {"LD_LIBRARY_PATH": env["QBOXCONF_LD_LIBRARY_PATH"],
        "QBOX_ZEPHYR_ENTRY": str(entry),
        "QBOX_APOLLO_FULL_SI_CL1_IMAGE": str(out / "zephyr.bin"),
        "QBOX_APOLLO_FULL_SI_CL1_LOG": str(out / "zephyr-uart.log"),
        "QBOX_APOLLO_FULL_SI_CL1_UART_READ_FILE": str(out / "zephyr-uart.in")}
    plan = {"command": command, "environment": launch_env, "elf": str(elf),
            "entry": hex(entry), "qboxconf": str(conf), "pass_marker": BOOT_MARKER.decode()}
    print(json.dumps(plan, indent=2), flush=True)
    if args.dry_run:
        return 0
    out.mkdir(parents=True, exist_ok=False)
    (out / "run.json").write_text(json.dumps(plan, indent=2) + "\n")
    (out / "zephyr.bin").write_bytes(payload)
    for name in ("zephyr-uart.log", "zephyr-uart.in", "qbox.log"):
        (out / name).touch()
    if args.headless:
        return supervise(out, args.timeout, args.exit_after_pass)
    start_tmux(args, out, script=Path(__file__).resolve(), program="QBox Zephyr", key_prefix="qbox-zephyr-")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
