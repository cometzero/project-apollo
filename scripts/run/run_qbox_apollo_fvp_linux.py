#!/usr/bin/env python3
"""Build or run Apollo FVP primary-compute Linux on the QBox Apollo platform."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
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
from typing import TypedDict


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
DEFAULT_LOCAL_BOOTARGS = (
    "console=ttyAMA0,115200 earlycon=pl011,0x1A400000 "
    "root=/dev/ram0 rw rdinit=/init loglevel=7 "
    "cpuidle.governor=menu maxcpus=16 mem=4064M"
)
PRIMARY_VIRTIO_BLOCK_NODE = "/soc/virtio@30020000"
HOSTFWD_TCP_RE = re.compile(r"(?:^|,)hostfwd=tcp:[^:,]*:(\d+)-")
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\a]*(?:\a|\x1b\\)")
FAIL_PATTERNS = [
    "Kernel panic",
    "Unable to mount root fs",
    "No working init found",
]


@dataclass(frozen=True)
class LocalBuildArtifacts:
    kernel: Path
    initramfs: Path
    disk: Path
    dtb: Path


class DebugEnvError(ValueError):
    pass


class EvalStatus(TypedDict, total=False):
    pass_patterns: dict[str, bool]
    login_patterns: dict[str, bool]
    fail_patterns: dict[str, bool]
    log_bytes: int
    timeout_s: int | None
    interrupted: bool
    duration_s: float
    command: list[str]
    log_path: str
    kernel: str
    dtb: str
    base_dtb: str
    dt_overlay: str | None
    initramfs: str | None
    bootargs: str
    initramfs_addr: str
    disk: str | None
    extra_disks: list[str]
    passed: bool


def resolve_local_build_artifacts(local_build_dir: Path) -> LocalBuildArtifacts:
    boot_dir = local_build_dir / "deploy/boot"
    return LocalBuildArtifacts(
        kernel=boot_dir / "Image",
        initramfs=boot_dir / "initramfs.cpio.gz",
        disk=boot_dir / "apollo-fvp-local-disk.img",
        dtb=boot_dir / "apollo-fvp.dtb",
    )


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def qbox_build_dir(root: Path) -> Path:
    default_dir = root / "build/local-apollo-fvp/work/qbox-platform"
    return Path(
        os.environ.get(
            "QBOX_PLATFORM_BUILD_DIR",
            os.environ.get("QBOX_BUILD_DIR", str(default_dir)),
        )
    ).resolve()


def timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    print("+ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def ensure_qbox_targets(root: Path, jobs: int) -> None:
    cmd = [
        "cmake",
        "--build",
        str(qbox_build_dir(root)),
        "--target",
        *REQUIRED_TARGETS,
        "--parallel",
        str(jobs),
    ]
    run(cmd, cwd=root)


def initramfs_range(initramfs: Path, load_addr: int) -> tuple[int, int]:
    size = initramfs.stat().st_size
    return load_addr, load_addr + size


def dts_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def direct_boot_overlay_dts(
    *,
    bootargs: str,
    initrd_start: int,
    initrd_end: int,
    primary_disk_enabled: bool = True,
) -> str:
    fragments = [
        "/dts-v1/;",
        "/plugin/;",
        "",
        "/ {",
        "\tfragment@0 {",
        '\t\ttarget-path = "/chosen";',
        "\t\t__overlay__ {",
        f'\t\t\tbootargs = "{dts_escape(bootargs)}";',
        f"\t\t\tlinux,initrd-start = <0x{initrd_start:x}>;",
        f"\t\t\tlinux,initrd-end = <0x{initrd_end:x}>;",
        "\t\t};",
        "\t};",
    ]
    if not primary_disk_enabled:
        fragments.extend(
            [
                "",
                "\tfragment@1 {",
                f'\t\ttarget-path = "{PRIMARY_VIRTIO_BLOCK_NODE}";',
                "\t\t__overlay__ {",
                '\t\t\tstatus = "disabled";',
                "\t\t};",
                "\t};",
            ]
        )
    fragments.append("};")
    return "\n".join(fragments) + "\n"


def prepare_direct_boot_dtb(
    root: Path,
    base_dtb: Path,
    dtb: Path,
    *,
    bootargs: str,
    initramfs: Path,
    initramfs_addr: int,
    primary_disk_enabled: bool = True,
) -> tuple[Path, Path]:
    dtc = shutil.which("dtc")
    if not dtc:
        raise RuntimeError("dtc not found; install device-tree-compiler")
    fdtoverlay = shutil.which("fdtoverlay")
    if not fdtoverlay:
        raise RuntimeError("fdtoverlay not found; install device-tree-compiler")

    dtb.parent.mkdir(parents=True, exist_ok=True)
    overlay_dts = dtb.with_suffix(".overlay.dts")
    overlay_dtbo = dtb.with_suffix(".overlay.dtbo")
    initrd_start, initrd_end = initramfs_range(initramfs, initramfs_addr)
    overlay_dts.write_text(
        direct_boot_overlay_dts(
            bootargs=bootargs,
            initrd_start=initrd_start,
            initrd_end=initrd_end,
            primary_disk_enabled=primary_disk_enabled,
        ),
        encoding="utf-8",
    )
    run(
        [dtc, "-@", "-I", "dts", "-O", "dtb", "-o", str(overlay_dtbo), str(overlay_dts)],
        cwd=root,
    )
    run([fdtoverlay, "-i", str(base_dtb), "-o", str(dtb), str(overlay_dtbo)], cwd=root)
    return overlay_dts, overlay_dtbo


def copy_disk(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    cp = shutil.which("cp")
    if cp:
        run([cp, "--reflink=auto", "--sparse=always", str(src), str(dst)], cwd=dst.parent)
        return
    shutil.copy2(src, dst)


def env_enabled(value: str | None) -> bool:
    return value is not None and value.lower() in {"1", "true", "yes", "on"}


def parse_env_port(name: str, env: dict[str, str]) -> int:
    raw = env.get(name, "0")
    try:
        port = int(raw, 10)
    except ValueError as exc:
        raise DebugEnvError(f"{name} must be an integer TCP port") from exc
    if port < 0 or port > 65535:
        raise DebugEnvError(f"{name} must be in range 0..65535")
    return port


def parse_env_int(name: str, env: dict[str, str], default: int) -> int:
    raw = env.get(name, str(default))
    try:
        return int(raw, 10)
    except ValueError as exc:
        raise DebugEnvError(f"{name} must be an integer") from exc


def netdev_hostfwd_tcp_ports(netdev: str) -> set[int]:
    return {int(match) for match in HOSTFWD_TCP_RE.findall(netdev)}


def path_is_under(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def validate_debug_env(args: argparse.Namespace, env: dict[str, str]) -> None:
    num_cpus = parse_env_int("QBOX_APOLLO_NUM_CPUS", env, 16)
    if num_cpus < 1 or num_cpus > 16:
        raise DebugEnvError("QBOX_APOLLO_NUM_CPUS must be in range 1..16")

    gdb_base = parse_env_port("QBOX_APOLLO_GDB_PORT_BASE", env)
    if gdb_base != 0:
        raise DebugEnvError(
            "QBOX_APOLLO_GDB_PORT_BASE is unsupported for Apollo direct boot; "
            "use QBOX_APOLLO_GDB_CPU_INDEX with QBOX_APOLLO_GDB_PORT"
        )

    gdb_cpu_index = parse_env_int("QBOX_APOLLO_GDB_CPU_INDEX", env, -1)
    if gdb_cpu_index < -1 or gdb_cpu_index >= num_cpus:
        raise DebugEnvError("QBOX_APOLLO_GDB_CPU_INDEX must be -1 or in CPU range")

    gdb_port = parse_env_port("QBOX_APOLLO_GDB_PORT", env)
    if gdb_port == 0:
        if gdb_cpu_index != -1:
            raise DebugEnvError(
                "QBOX_APOLLO_GDB_PORT must be nonzero when "
                "QBOX_APOLLO_GDB_CPU_INDEX is set"
            )
        return
    if gdb_cpu_index == -1:
        raise DebugEnvError(
            "QBOX_APOLLO_GDB_CPU_INDEX must be set when QBOX_APOLLO_GDB_PORT is nonzero"
        )

    gdb_ports = {gdb_port}
    hostfwd_ports = netdev_hostfwd_tcp_ports(args.netdev)
    collision = sorted(gdb_ports & hostfwd_ports)
    if collision:
        joined = ", ".join(str(port) for port in collision)
        raise DebugEnvError(f"GDB port collides with --netdev hostfwd TCP port: {joined}")


def prepare_debug_outputs(args: argparse.Namespace, env: dict[str, str]) -> None:
    if not env_enabled(env.get("QBOX_APOLLO_PC_TRACE")):
        return
    trace_file = env.get("QBOX_APOLLO_PC_TRACE_FILE")
    if not trace_file:
        return
    out_dir = args.out_dir.resolve()
    path = Path(trace_file).resolve()
    if not path_is_under(path, out_dir):
        raise DebugEnvError("QBOX_APOLLO_PC_TRACE_FILE must resolve under --out-dir")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()


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
    root: Path, args: argparse.Namespace, disk: Path | None, extra_disks: list[Path]
) -> dict[str, str]:
    env = os.environ.copy()
    build_dir = qbox_build_dir(root)
    lib_paths = [
        build_dir,
        build_dir / "_deps/libqemu-build/qemu-prefix/lib",
    ]
    current = env.get("LD_LIBRARY_PATH")
    if current:
        lib_paths.append(Path(current))
    env["LD_LIBRARY_PATH"] = ":".join(str(path) for path in lib_paths)
    env["QBOX_APOLLO_KERNEL"] = str(args.kernel.resolve())
    env["QBOX_APOLLO_DTB"] = str(args.dtb.resolve())
    if getattr(args, "initramfs", None):
        env["QBOX_APOLLO_INITRAMFS"] = str(args.initramfs.resolve())
    else:
        env.pop("QBOX_APOLLO_INITRAMFS", None)
    if disk is not None:
        env["QBOX_APOLLO_ROOTFS"] = str(disk.resolve())
    else:
        env.pop("QBOX_APOLLO_ROOTFS", None)
    for index, extra_disk in enumerate(extra_disks, start=1):
        env[f"QBOX_APOLLO_EXTRA_BLK{index}"] = str(extra_disk.resolve())
    env["QBOX_APOLLO_ACCEL"] = args.accel
    env["QBOX_APOLLO_NETDEV"] = args.netdev
    env.setdefault("QBOX_APOLLO_NUM_CPUS", "16")
    if env_enabled(env.get("QBOX_APOLLO_PC_TRACE")):
        env["QBOX_APOLLO_PC_TRACE"] = "true"
        trace_out_dir = getattr(args, "out_dir", root / "build/qbox-apollo-fvp")
        env.setdefault(
            "QBOX_APOLLO_PC_TRACE_FILE",
            str((trace_out_dir / "cpu-pc-trace.log").resolve()),
        )
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


def evaluate(text: str) -> tuple[bool, EvalStatus]:
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
    root: Path, args: argparse.Namespace, disk: Path | None, extra_disks: list[Path]
) -> tuple[int, EvalStatus]:
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "qbox-apollo-fvp.log"
    summary_path = out_dir / "summary.txt"
    result_path = out_dir / "result.json"
    cmd = [
        str((qbox_build_dir(root) / "platforms-vp").resolve()),
        "-l",
        str(args.conf.resolve()),
    ]
    env = qbox_env(root, args, disk, extra_disks)
    validate_debug_env(args, env)
    prepare_debug_outputs(args, env)

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
    status["base_dtb"] = str(args.base_dtb.resolve())
    status["dt_overlay"] = (
        str(args.dt_overlay.resolve()) if getattr(args, "dt_overlay", None) else None
    )
    status["initramfs"] = str(args.initramfs.resolve()) if args.initramfs else None
    status["bootargs"] = args.bootargs
    status["initramfs_addr"] = f"0x{args.initramfs_addr:x}"
    status["disk"] = str(disk.resolve()) if disk is not None else None
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
        f"base_dtb: {args.base_dtb.resolve()}",
        f"dt_overlay: {args.dt_overlay.resolve() if args.dt_overlay else None}",
        f"initramfs: {args.initramfs.resolve() if args.initramfs else None}",
        f"bootargs: {args.bootargs}",
        f"initramfs_addr: 0x{args.initramfs_addr:x}",
        f"disk: {disk.resolve() if disk is not None else None}",
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
        default=root / "tools/qbox-platform/platforms/apollo/apollo-pc.lua",
    )
    parser.add_argument(
        "--base-dtb",
        type=Path,
        help="Base Apollo DTB. Defaults to <local-build-dir>/deploy/boot/apollo-fvp.dtb.",
    )
    parser.add_argument(
        "--dtb",
        type=Path,
        default=root / "build/qbox-apollo-fvp/apollo-fvp-direct.dtb",
    )
    parser.add_argument("--kernel", type=Path)
    parser.add_argument("--disk", type=Path)
    parser.add_argument(
        "--local-build-dir",
        type=Path,
        default=root / "build/local-apollo-fvp",
    )
    parser.add_argument(
        "--qbox-build-dir",
        type=Path,
        help=(
            "QBox CMake build directory. Defaults to "
            "<local-build-dir>/work/qbox-platform."
        ),
    )
    parser.add_argument("--initramfs", type=Path)
    parser.add_argument("--bootargs", default=DEFAULT_LOCAL_BOOTARGS)
    parser.add_argument(
        "--initramfs-addr",
        type=lambda value: int(value, 0),
        default=0x94000000,
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
        help="Do not prepare the Apollo direct-boot overlay DTB before running.",
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="Build QBox targets and prepare the DTB, then exit without running.",
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
    explicit_disk = any(
        arg == "--disk" or arg.startswith("--disk=") for arg in sys.argv[1:]
    )
    args = parse_args()
    args.conf = args.conf.resolve()
    args.dtb = args.dtb.resolve()
    args.local_build_dir = args.local_build_dir.resolve()
    if args.qbox_build_dir is not None:
        resolved_qbox_build_dir = str(args.qbox_build_dir.resolve())
        os.environ["QBOX_PLATFORM_BUILD_DIR"] = resolved_qbox_build_dir
        os.environ["QBOX_BUILD_DIR"] = resolved_qbox_build_dir
    elif "QBOX_PLATFORM_BUILD_DIR" not in os.environ and "QBOX_BUILD_DIR" not in os.environ:
        resolved_qbox_build_dir = str(
            (args.local_build_dir / "work/qbox-platform").resolve()
        )
        os.environ["QBOX_PLATFORM_BUILD_DIR"] = resolved_qbox_build_dir
        os.environ["QBOX_BUILD_DIR"] = resolved_qbox_build_dir
    artifacts = resolve_local_build_artifacts(args.local_build_dir)
    if args.kernel is None:
        args.kernel = artifacts.kernel
    if args.initramfs is None:
        args.initramfs = artifacts.initramfs
    if args.disk is None:
        args.disk = artifacts.disk
    if args.base_dtb is None:
        args.base_dtb = artifacts.dtb
    args.kernel = args.kernel.resolve()
    args.initramfs = args.initramfs.resolve() if args.initramfs else None
    args.disk = args.disk.resolve() if args.disk else None
    args.base_dtb = args.base_dtb.resolve()
    args.out_dir = args.out_dir.resolve()
    args.dt_overlay = None
    if args.extra_disk_size_mib <= 0:
        print("error: --extra-disk-size-mib must be positive", file=sys.stderr)
        return 2

    required_paths = [
        (args.conf, "QBox config"),
    ]
    if args.skip_dtb:
        required_paths.append((args.dtb, "prepared device tree blob"))
    else:
        required_paths.extend(
            [
                (args.base_dtb, "base device tree blob"),
                (args.initramfs, "initramfs image"),
            ]
        )
    if not args.build_only:
        required_paths.extend(
            [
                (args.kernel, "kernel image"),
            ]
        )
        if args.skip_dtb:
            required_paths.append((args.initramfs, "initramfs image"))

    for path, label in required_paths:
        if path is None or not path.exists():
            print(f"error: {label} not found: {path}", file=sys.stderr)
            return 2
    if explicit_disk and args.disk is not None and not args.disk.exists():
        print(f"error: disk image not found: {args.disk}", file=sys.stderr)
        return 2
    disk_available = args.disk is not None and args.disk.exists()

    try:
        if not args.skip_build:
            ensure_qbox_targets(root, args.jobs)
        if not args.skip_dtb:
            overlay_dts, _overlay_dtbo = prepare_direct_boot_dtb(
                root,
                args.base_dtb,
                args.dtb,
                bootargs=args.bootargs,
                initramfs=args.initramfs,
                initramfs_addr=args.initramfs_addr,
                primary_disk_enabled=disk_available,
            )
            args.dt_overlay = overlay_dts
        if args.build_only:
            print(args.dtb)
            return 0
        disk = args.disk if disk_available else None
        if disk is not None and not args.no_copy_disk:
            disk = args.out_dir / disk.name
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
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
