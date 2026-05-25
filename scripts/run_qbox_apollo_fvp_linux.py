#!/usr/bin/env python3
"""Build or run Apollo FVP primary-compute Linux on the QBox Apollo platform."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time


REQUIRED_TARGETS = [
    "platforms-vp",
    "router",
    "keep_alive",
    "gs_memory",
    "loader",
    "char_backend_stdio",
    "uart-pl011",
    "arm_gicv3",
    "arm_gicv3_its",
    "global_peripheral_initiator",
    "cpu_arm_cortexA720AE",
    "virtio_mmio_blk",
    "virtio_mmio_net",
    "virtio_mmio_rng",
    "pl031",
    "sbsa_gwdt",
]

PASS_PATTERNS = [
    "Booting Linux on physical CPU",
]
LOGIN_PATTERNS = [
    "Reached target Multi-User System",
    "apollo-fvp login:",
    "root@apollo-fvp",
]
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\a]*(?:\a|\x1b\\)")
FAIL_PATTERNS = [
    "Kernel panic",
    "Unable to mount root fs",
    "No working init found",
]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    print("+ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def ensure_qbox_targets(root: Path, jobs: int) -> None:
    cmd = [
        "cmake",
        "--build",
        str(root / "tools/qbox/build"),
        "--target",
        *REQUIRED_TARGETS,
        "--parallel",
        str(jobs),
    ]
    run(cmd, cwd=root)


def compile_dtb(root: Path, dts: Path, dtb: Path) -> None:
    dtc = shutil.which("dtc")
    if not dtc:
        raise RuntimeError("dtc not found; install device-tree-compiler")
    dtb.parent.mkdir(parents=True, exist_ok=True)
    run([dtc, "-I", "dts", "-O", "dtb", "-o", str(dtb), str(dts)], cwd=root)


def copy_disk(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    cp = shutil.which("cp")
    if cp:
        run([cp, "--reflink=auto", "--sparse=always", str(src), str(dst)], cwd=dst.parent)
        return
    shutil.copy2(src, dst)


def prepare_extra_disks(out_dir: Path, size_mib: int) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    size_bytes = size_mib * 1024 * 1024
    disks = [
        out_dir / "apollo-extra-blk1.raw",
        out_dir / "apollo-extra-blk2.raw",
        out_dir / "apollo-extra-blk3.raw",
    ]
    for disk in disks:
        if not disk.exists():
            with disk.open("wb") as handle:
                handle.truncate(size_bytes)
    return disks


def qbox_env(
    root: Path, args: argparse.Namespace, disk: Path, extra_disks: list[Path]
) -> dict[str, str]:
    env = os.environ.copy()
    lib_paths = [
        root / "tools/qbox/build",
        root / "tools/qbox/build/_deps/libqemu-build/qemu-prefix/lib",
    ]
    current = env.get("LD_LIBRARY_PATH")
    if current:
        lib_paths.append(Path(current))
    env["LD_LIBRARY_PATH"] = ":".join(str(path) for path in lib_paths)
    env["QBOX_APOLLO_KERNEL"] = str(args.kernel.resolve())
    env["QBOX_APOLLO_DTB"] = str(args.dtb.resolve())
    env["QBOX_APOLLO_ROOTFS"] = str(disk.resolve())
    for index, extra_disk in enumerate(extra_disks, start=1):
        env[f"QBOX_APOLLO_EXTRA_BLK{index}"] = str(extra_disk.resolve())
    env["QBOX_APOLLO_ACCEL"] = args.accel
    env["QBOX_APOLLO_NETDEV"] = args.netdev
    return env


def stop_process(proc: subprocess.Popen[bytes], *, process_group: bool = True) -> None:
    if proc.poll() is not None:
        return
    if process_group:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
    else:
        proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        if process_group:
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
        proc.wait(timeout=5)


def evaluate(text: str) -> tuple[bool, dict[str, object]]:
    clean_text = ANSI_RE.sub("", text).replace("\r", "")
    pass_hits = {pattern: pattern in clean_text for pattern in PASS_PATTERNS}
    login_hits = {pattern: pattern in clean_text for pattern in LOGIN_PATTERNS}
    fail_hits = {pattern: pattern in clean_text for pattern in FAIL_PATTERNS}
    passed = all(pass_hits.values()) and any(login_hits.values()) and not any(
        fail_hits.values()
    )
    return passed, {
        "pass_patterns": pass_hits,
        "login_patterns": login_hits,
        "fail_patterns": fail_hits,
        "log_bytes": len(text.encode("utf-8", errors="replace")),
    }


def run_qbox(
    root: Path, args: argparse.Namespace, disk: Path, extra_disks: list[Path]
) -> tuple[int, dict[str, object]]:
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "qbox-apollo-fvp.log"
    summary_path = out_dir / "summary.txt"
    result_path = out_dir / "result.json"
    cmd = [
        str((root / "tools/qbox/build/platforms-vp").resolve()),
        "-l",
        str(args.conf.resolve()),
    ]
    env = qbox_env(root, args, disk, extra_disks)

    print(f"log: {log_path}", flush=True)
    print("+ " + " ".join(cmd), flush=True)
    start = time.monotonic()
    text = ""
    timed_out = False
    interrupted = False
    process_group = not args.interactive
    proc = subprocess.Popen(
        cmd,
        cwd=root,
        env=env,
        stdin=None if args.interactive else subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=process_group,
    )

    try:
        with log_path.open("w", encoding="utf-8", errors="replace", buffering=1) as log:
            assert proc.stdout is not None
            os.set_blocking(proc.stdout.fileno(), False)
            while args.timeout <= 0 or time.monotonic() - start < args.timeout:
                try:
                    chunk = os.read(proc.stdout.fileno(), 65536)
                except BlockingIOError:
                    chunk = b""
                if chunk:
                    decoded = chunk.decode("utf-8", errors="replace")
                    log.write(decoded)
                    text += decoded
                    if args.interactive:
                        sys.stdout.write(decoded)
                        sys.stdout.flush()
                    passed, status = evaluate(text)
                    if passed and not args.interactive:
                        stop_process(proc, process_group=process_group)
                        break
                    if any(status["fail_patterns"].values()) and not args.interactive:
                        stop_process(proc, process_group=process_group)
                        break
                    continue
                if proc.poll() is not None:
                    break
                time.sleep(0.1)
            else:
                timed_out = True
                stop_process(proc, process_group=process_group)
    except KeyboardInterrupt:
        interrupted = True
        stop_process(proc, process_group=process_group)
    finally:
        stop_process(proc, process_group=process_group)

    duration_s = time.monotonic() - start
    passed, status = evaluate(text)
    status["timeout_s"] = args.timeout if timed_out and not passed else None
    status["interrupted"] = interrupted
    status["duration_s"] = round(duration_s, 3)
    status["command"] = cmd
    status["log_path"] = str(log_path)
    status["kernel"] = str(args.kernel.resolve())
    status["dtb"] = str(args.dtb.resolve())
    status["disk"] = str(disk.resolve())
    status["extra_disks"] = [str(path.resolve()) for path in extra_disks]
    status["passed"] = passed

    result_path.write_text(
        json.dumps(status, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lines = [
        f"passed: {passed}",
        f"duration_s: {duration_s:.3f}",
        f"log: {log_path}",
        f"kernel: {args.kernel.resolve()}",
        f"dtb: {args.dtb.resolve()}",
        f"disk: {disk.resolve()}",
        "extra_disks:",
        *[f"  - {path.resolve()}" for path in extra_disks],
        "pass_patterns:",
    ]
    for pattern, hit in status["pass_patterns"].items():
        lines.append(f"  - {pattern}: {hit}")
    lines.append("login_patterns:")
    for pattern, hit in status["login_patterns"].items():
        lines.append(f"  - {pattern}: {hit}")
    lines.append("fail_patterns:")
    for pattern, hit in status["fail_patterns"].items():
        lines.append(f"  - {pattern}: {hit}")
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(out_dir)
    print(summary_path)
    print(result_path)
    if interrupted and not passed:
        return 130, status
    return 0 if passed else 1, status


def parse_args() -> argparse.Namespace:
    root = workspace_root()
    parser = argparse.ArgumentParser(
        description="Prepare QBox Apollo support and boot Apollo Linux headlessly."
    )
    parser.add_argument(
        "--conf",
        type=Path,
        default=root / "tools/qbox/platforms/apollo-fvp/conf.lua",
    )
    parser.add_argument(
        "--dts",
        type=Path,
        default=root
        / "tools/qbox/platforms/apollo-fvp/apollo-fvp-primary-compute.dts",
    )
    parser.add_argument(
        "--dtb",
        type=Path,
        default=root / "build/qbox-apollo-fvp/apollo-fvp-primary-compute.dtb",
    )
    parser.add_argument(
        "--kernel",
        type=Path,
        default=root / "build/tmp_baremetal/deploy/images/apollo-fvp/Image",
    )
    parser.add_argument(
        "--disk",
        type=Path,
        default=root
        / "build/tmp_baremetal/deploy/images/apollo-fvp/baremetal-image-apollo-fvp.wic",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "build/qbox-apollo-fvp" / timestamp(),
    )
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    parser.add_argument("--accel", default="tcg")
    parser.add_argument("--netdev", default="type=user,hostfwd=tcp::2222-:22")
    parser.add_argument(
        "--extra-disk-size-mib",
        type=int,
        default=64,
        help="Sparse size for the three additional Apollo virtio block disks.",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Do not build required QBox targets before running.",
    )
    parser.add_argument(
        "--skip-dtb",
        action="store_true",
        help="Do not compile the Apollo QBox device tree before running.",
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="Build QBox targets and compile the DTB, then exit without running.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Print UART output to this terminal and pass stdin to the guest.",
    )
    parser.add_argument(
        "--no-copy-disk",
        action="store_true",
        help="Attach --disk directly instead of copying it into --out-dir.",
    )
    return parser.parse_args()


def main() -> int:
    root = workspace_root()
    args = parse_args()
    args.conf = args.conf.resolve()
    args.dts = args.dts.resolve()
    args.dtb = args.dtb.resolve()
    args.kernel = args.kernel.resolve()
    args.disk = args.disk.resolve()
    args.out_dir = args.out_dir.resolve()
    if args.extra_disk_size_mib <= 0:
        print("error: --extra-disk-size-mib must be positive", file=sys.stderr)
        return 2

    required_paths = [
        (args.conf, "QBox config"),
        (args.dts, "device tree source"),
    ]
    if not args.build_only:
        required_paths.extend(
            [
                (args.kernel, "kernel image"),
                (args.disk, "disk image"),
            ]
        )

    for path, label in required_paths:
        if not path.exists():
            print(f"error: {label} not found: {path}", file=sys.stderr)
            return 2

    try:
        if not args.skip_build:
            ensure_qbox_targets(root, args.jobs)
        if not args.skip_dtb:
            compile_dtb(root, args.dts, args.dtb)
        if args.build_only:
            print(args.dtb)
            return 0
        disk = args.disk
        if not args.no_copy_disk:
            disk = args.out_dir / args.disk.name
            copy_disk(args.disk, disk)
        extra_disks = prepare_extra_disks(args.out_dir, args.extra_disk_size_mib)
        rc, _status = run_qbox(root, args, disk, extra_disks)
        return rc
    except subprocess.CalledProcessError as exc:
        print(f"error: command failed with exit code {exc.returncode}", file=sys.stderr)
        return exc.returncode
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
