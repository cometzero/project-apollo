#!/usr/bin/env python3
"""Build or run RD-Aspen FVP primary-compute Linux on the QBox RD-Aspen platform."""

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
    "qemu_gpex",
    "arm_gicv3",
    "arm_gicv3_its",
    "arm_smmuv3",
    "mmu720ae",
    "mhu320ae",
    "mhuv3_rproc_stub",
    "ras_ffh_stub",
    "qemu_hexagon_qtimer",
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
    "fvp-rd-aspen login:",
    "root@fvp-rd-aspen",
]
PROBE_DONE_MARKER = "__QBOX_PROBE_DONE__"
POST_LOGIN_PROBE_COMMANDS = [
    "uname -a",
    "modprobe -v arm_si_rproc timeout=500; echo arm_si_rproc_modprobe_rc:$?",
    "for d in /sys/class/remoteproc/remoteproc*; do [ -f $d/state ] && [ \"$(cat $d/state)\" = detached ] && echo attach > $d/state 2>/dev/null || true; done",
    "modprobe -v rpmsg_ns; echo rpmsg_ns_modprobe_rc:$?",
    "modprobe -v virtio_rpmsg_bus; echo virtio_rpmsg_bus_modprobe_rc:$?",
    "modprobe -v rpmsg_net; echo rpmsg_net_modprobe_rc:$?",
    "dmesg | grep -Ei 'gic|its|pl011|ttyAMA|watchdog|rtc|virtio|rng|eth|30060000|30080000|scmi|mhu|smmu|remoteproc|rpmsg|pfdi|hipc|ras|pmu|dsu|timer' || true",
    "ls -l /sys/bus/virtio/devices || true",
    "find /sys/bus/platform/devices -maxdepth 1 -type l | grep -E '1a400000|1a420000|300d0000|300[234568]0000|208[048]|400[25be]0000|1c0000000|ffa00000|1a810000' || true",
    "ls -d /sys/bus/event_source/devices/arm_dsu_* 2>/dev/null || true",
    "for d in /sys/class/remoteproc/remoteproc*; do [ -f $d/name ] && echo remoteproc_state:$(cat $d/name):$(cat $d/state); done",
    "ip link show || true",
    "cat /proc/interrupts | grep -E 'uart-pl011|virtio|rtc-pl031|arch_timer|GIC|ITS|gwdt|smmu|ras|estatus|mhu|scmi|remoteproc' || true",
    "lsmod | grep -Ei 'virtio|rng|pfdi|hipc|rpmsg|remoteproc|scmi|mhu|smmu' || true",
    "modprobe -v openvswitch; echo openvswitch_modprobe_rc:$?",
    "modprobe -v pfdi_misc; echo pfdi_misc_modprobe_rc:$?",
    "cat /proc/modules | grep -Ei 'openvswitch|pfdi|hipc|rpmsg|remoteproc|scmi|mhu|smmu' || true",
    "systemctl is-system-running || true",
    "systemctl --failed --no-pager || true",
    "systemctl status systemd-modules-load.service --no-pager -l || true",
    "journalctl -u systemd-modules-load.service --no-pager -n 80 || true",
]
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\a]*(?:\a|\x1b\\)")
FAIL_PATTERNS = [
    "Kernel panic",
    "Unable to mount root fs",
    "No working init found",
]
DRIVER_PATTERNS = {
    "gicv3": [
        r"GICv3:.*Distributor",
        r"GICv3:.*redistributor",
    ],
    "pl011_uart": [
        r"ttyAMA0 at MMIO",
        r"1a400000\.serial",
    ],
    "sbsa_gwdt": [
        r"sbsa-gwdt .*1a420000\.watchdog|SBSA Generic Watchdog",
    ],
    "armv7_timer_mem": [
        r"arch_timer_mmio: mmio timer running|arch_mem_timer|1a810000\.timer",
    ],
    "ras_ffh": [
        r"Registered estatus provider",
        r"ffa00000\.ras-ffh",
    ],
    "dsu_pmu": [
        r"arm_dsu_0|dsu-pmu-0",
    ],
    "mhuv3_scmi": [
        r"arm-mhuv3-mailbox|40020000\.mhu|40050000\.mhu",
        r"SCMI Protocol v",
    ],
    "si_remoteproc": [
        r"arm_si_rproc_modprobe_rc:0|arm-si-rproc|si-rproc",
        r"remoteproc_state:si-cl1:(attached|running)|remoteproc remoteproc",
    ],
    "rpmsg": [
        r"virtio_rpmsg_bus_modprobe_rc:0|virtio_rpmsg_bus",
        r"rpmsg_net_modprobe_rc:0|rpmsg_net",
    ],
    "rtc_pl031": [
        r"rtc-pl031",
        r"300d0000\.rtc",
    ],
    "virtio_blk": [
        r"virtio_blk",
        r"\bvda:",
    ],
    "virtio_net": [
        r"virtio_net",
        r"30060000\.virtio-net",
        r"\beth0:",
    ],
    "virtio_rng": [
        r"virtio_rng|30080000\.virtio-rng|random:.*virtio",
    ],
    "smmu_v3": [
        r"arm-smmu-v3",
        r"iommu@1c0000000|1c0000000\.iommu",
        r"ias .* oas .*features",
    ],
}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


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
        out_dir / "rd-aspen-extra-blk1.raw",
        out_dir / "rd-aspen-extra-blk2.raw",
        out_dir / "rd-aspen-extra-blk3.raw",
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
    env["QBOX_RDASPEN_KERNEL"] = str(args.kernel.resolve())
    env["QBOX_RDASPEN_DTB"] = str(args.dtb.resolve())
    env["QBOX_RDASPEN_ROOTFS"] = str(disk.resolve())
    for index, extra_disk in enumerate(extra_disks, start=1):
        env[f"QBOX_RDASPEN_EXTRA_BLK{index}"] = str(extra_disk.resolve())
    env["QBOX_RDASPEN_ACCEL"] = args.accel
    env["QBOX_RDASPEN_NETDEV"] = args.netdev
    env["QBOX_RDASPEN_SMMU_BACKEND"] = args.smmu_backend
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
    driver_hits = {
        name: all(re.search(pattern, clean_text, re.IGNORECASE) for pattern in patterns)
        for name, patterns in DRIVER_PATTERNS.items()
    }
    passed = all(pass_hits.values()) and any(login_hits.values()) and not any(
        fail_hits.values()
    ) and all(driver_hits.values())
    return passed, {
        "pass_patterns": pass_hits,
        "login_patterns": login_hits,
        "fail_patterns": fail_hits,
        "driver_patterns": driver_hits,
        "log_bytes": len(text.encode("utf-8", errors="replace")),
    }


def run_qbox(
    root: Path, args: argparse.Namespace, disk: Path, extra_disks: list[Path]
) -> tuple[int, dict[str, object]]:
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "qbox-fvp-rd-aspen.log"
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
    sent_login = False
    sent_probe = False
    probe_complete = False
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
                    clean_text = ANSI_RE.sub("", text).replace("\r", "")
                    if (
                        args.post_login_probe
                        and not args.interactive
                        and proc.stdin is not None
                    ):
                        if not sent_login and "fvp-rd-aspen login:" in clean_text:
                            proc.stdin.write((args.login_user + "\n").encode())
                            proc.stdin.flush()
                            sent_login = True
                        if (
                            sent_login
                            and not sent_probe
                            and re.search(
                                r"root@fvp-rd-aspen:[^\n]*[#>]\s*$",
                                clean_text,
                                re.MULTILINE,
                            )
                        ):
                            probe = [
                                "echo __QBOX_PROBE_START__",
                                *POST_LOGIN_PROBE_COMMANDS,
                                f"echo {PROBE_DONE_MARKER}",
                            ]
                            proc.stdin.write(("\n".join(probe) + "\n").encode())
                            proc.stdin.flush()
                            sent_probe = True
                        probe_complete = PROBE_DONE_MARKER in clean_text
                    if args.interactive:
                        sys.stdout.write(decoded)
                        sys.stdout.flush()
                    passed, status = evaluate(text)
                    if (
                        passed
                        and not args.interactive
                        and (not args.post_login_probe or probe_complete)
                    ):
                        stop_process(proc, process_group=process_group)
                        break
                    if args.post_login_probe and probe_complete and not args.interactive:
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
    status["post_login_probe"] = args.post_login_probe
    status["probe_complete"] = probe_complete
    status["duration_s"] = round(duration_s, 3)
    status["smmu_backend"] = args.smmu_backend
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
        f"smmu_backend: {args.smmu_backend}",
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
    lines.append("driver_patterns:")
    for name, hit in status["driver_patterns"].items():
        lines.append(f"  - {name}: {hit}")
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
        description="Prepare QBox RD-Aspen support and boot RD-Aspen Linux headlessly."
    )
    parser.add_argument(
        "--conf",
        type=Path,
        default=root / "tools/qbox/platforms/fvp-rd-aspen/conf.lua",
    )
    parser.add_argument(
        "--dts",
        type=Path,
        default=root
        / "tools/qbox/platforms/fvp-rd-aspen/fvp-rd-aspen-primary-compute.dts",
    )
    parser.add_argument(
        "--dtb",
        type=Path,
        default=root / "build/qbox-fvp-rd-aspen/fvp-rd-aspen-primary-compute.dtb",
    )
    parser.add_argument(
        "--kernel",
        type=Path,
        default=root / "build/tmp_baremetal/deploy/images/fvp-rd-aspen/Image",
    )
    parser.add_argument(
        "--disk",
        type=Path,
        default=root
        / "build/tmp_baremetal/deploy/images/fvp-rd-aspen/baremetal-image-fvp-rd-aspen.wic",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "build/qbox-fvp-rd-aspen" / timestamp(),
    )
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    parser.add_argument("--accel", default="tcg")
    parser.add_argument("--netdev", default="type=user,hostfwd=tcp::2222-:22")
    parser.add_argument(
        "--smmu-backend",
        choices=["qemu-arm-smmuv3", "systemc-mmu720ae"],
        default="systemc-mmu720ae",
        help="SMMU backend used by the RD-Aspen Lua platform.",
    )
    parser.add_argument(
        "--extra-disk-size-mib",
        type=int,
        default=64,
        help="Sparse size for the three additional RD-Aspen virtio block disks.",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Do not build required QBox targets before running.",
    )
    parser.add_argument(
        "--skip-dtb",
        action="store_true",
        help="Do not compile the RD-Aspen QBox device tree before running.",
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
        "--post-login-probe",
        action="store_true",
        help="Log in on the serial console and run driver evidence commands.",
    )
    parser.add_argument("--login-user", default="root")
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
