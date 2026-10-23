#!/usr/bin/env python3
"""Launch the Apollo AP Linux platform using deployed Yocto artifacts."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import select
import shlex
import shutil
import signal
import subprocess
import sys
import termios
import time
import tty

ROOT = Path(__file__).resolve().parents[2]
from qbox_load_stats import LoadStats, add_arguments as add_stats_arguments, interval_from_args, drain_output
from qbox_monitor_manifest import monitor_plan, monitor_environment, preflight as monitor_preflight, update_runtime, prepare_qmp
from qbox_dtb import resolve_cpu_count


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    add_stats_arguments(p)
    p.add_argument(
        "--bsp", action="store_true", help="boot the BSP initramfs with its BSP WIC disk"
    )
    p.add_argument("--build-dir", type=Path, default=ROOT / "build")
    p.add_argument("--deploy-dir", type=Path)
    p.add_argument("--qboxconf", type=Path)
    p.add_argument("--kernel", type=Path)
    p.add_argument("--dtb", type=Path)
    p.add_argument("--initrd", type=Path)
    p.add_argument("--rootfs", type=Path)
    p.add_argument("--copy-disk", action="store_true",
                   help="copy the disk into the run directory (default: use the source disk)")
    p.add_argument("--ssh-port", type=int,
                   help="forward loopback TCP port to guest SSH through user networking")
    p.add_argument("--cpus", type=int, choices=range(1, 17),
                   help="AP CPUs (default: image manifest, or 4 for legacy inputs)")
    p.add_argument("--monitor", action="store_true", help="enable read-only loopback monitor")
    p.add_argument("--monitor-port", type=int, help="monitor TCP port (implies --monitor)")
    p.add_argument("--qmp", action="store_true", help="opt in to AP QMP biflow (implies monitor)")
    p.add_argument(
        "--conf",
        type=Path,
        default=ROOT
        / "hsoc-stack/tools/qbox-platform/platforms/apollo/apollo-qvp-linux.lua",
    )
    p.add_argument("--bootargs", help="replace the default Linux command line")
    p.add_argument("--out-dir", type=Path)
    p.add_argument("--session", default="qbox-linux")
    p.add_argument("--headless", action="store_true")
    p.add_argument("--no-attach", action="store_true")
    p.add_argument(
        "--timeout",
        type=float,
        default=0,
        help="headless deadline in seconds (0: unlimited)",
    )
    p.add_argument(
        "--exit-after-pass",
        action="store_true",
        help="headless: exit when the login/BSP marker is observed",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="resolve inputs and print launch plan without writing files",
    )
    p.add_argument("--platform-param", action="append", default=[])
    p.add_argument("--log-level", type=int, choices=range(10), default=4,
                   help="QBox global logging level (4: INFO; module overrides still apply)")
    p.add_argument("--domain-trace", action=argparse.BooleanOptionalAction, default=False,
                   help="log Linux mock MHU/SCMI/SI activity (default: disabled)")
    return p


def provider_environment(conf: Path, build: Path) -> dict[str, str]:
    # Reuse the full-system launcher's provider/path trust checks.
    script = 'set -eu; source "$1"; YOCTO_BUILD_DIR="$3"; values=$(read_qboxconf_shell_assignments "$2"); set -a; eval "$values"; env -0'
    result = subprocess.run(
        [
            "bash",
            "-c",
            script,
            "qboxconf",
            str(ROOT / "scripts/run/qbox_qboxconf_common.sh"),
            str(conf),
            str(build),
        ],
        check=True,
        stdout=subprocess.PIPE,
    )
    return dict(
        item.decode().split("=", 1) for item in result.stdout.split(b"\0") if item
    )


def required(path: Path, label: str) -> Path:
    path = path.absolute()
    if not path.is_file():
        raise ValueError(f"missing {label}: {path}")
    return path


def console(out: Path, log_name: str = "linux-uart.log", input_name: str = "linux-uart.in") -> int:
    """Poll the existing char_backend_file output; append raw UART input."""
    original = termios.tcgetattr(sys.stdin.fileno())
    try:
        tty.setraw(sys.stdin.fileno())
        with (
            (out / log_name).open("rb") as reader,
            (out / input_name).open("ab", buffering=0) as writer,
        ):
            while True:
                data = reader.read(65536)
                if data:
                    os.write(sys.stdout.fileno(), data)
                ready, _, _ = select.select([sys.stdin], [], [], 0.02)
                if ready:
                    data = os.read(sys.stdin.fileno(), 4096)
                    if not data:
                        return 0
                    writer.write(data)
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, original)


def supervise(out: Path, timeout: float, exit_after_pass: bool, *, echo_uart: bool = False) -> int:
    plan = json.loads((out / "launch.json").read_text())
    started = time.monotonic()
    passed = False
    login_sent = False
    probe_sent = False
    bsp_selftest = "NOT_OBSERVED" if plan["bsp"] else "NOT_APPLICABLE"
    status = "FAIL"
    poweroff_observed = False
    rc = 1
    with (out / "qbox.log").open("ab", buffering=0) as log:
        def report(message: str) -> None:
            log.write(f"[runner {time.monotonic() - started:.1f}s] {message}\n".encode())

        report("Starting QBox: " + shlex.join(plan["command"]))
        child = subprocess.Popen(
            plan["command"],
            env={**os.environ, **plan["environment"]},
            cwd=ROOT,
            stdout=subprocess.PIPE if plan.get("stats_interval") is not None else log,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )

        stats = LoadStats(child.pid, plan.get("stats_interval"), plan.get("monitor"))
        if child.stdout is not None:
            os.set_blocking(child.stdout.fileno(), False)

        def interrupted(_signum: int, _frame: object) -> None:
            raise KeyboardInterrupt

        old = {
            sig: signal.signal(sig, interrupted)
            for sig in (signal.SIGTERM, signal.SIGHUP)
        }
        try:
            with (out / "linux-uart.log").open("rb") as uart:
                observed = b""
                while child.poll() is None:
                    if child.stdout is not None:
                        drain_output(child.stdout, log)
                    for line in stats.poll():
                        log.write(("\n" + line + "\n").encode())
                    update_runtime(plan.get("monitor", {}), child.pid, plan.get("run_id", out.name))
                    chunk = uart.read()
                    if echo_uart and chunk:
                        sys.stdout.buffer.write(chunk)
                        sys.stdout.buffer.flush()
                    observed = (observed + chunk)[-65536:]
                    if re.search(rb"(?:^|\n)(?:\[[^\]\r\n]+\]\s*)?reboot: Power down\r?\n", observed):
                        # Linux completed its normal shutdown; release this
                        # owned simulator rather than waiting for its deadline.
                        poweroff_observed = True
                        status, rc = "POWERED_OFF", 0
                        report("Guest poweroff observed; stopping owned QBox process")
                        break
                    if plan["bsp"]:
                        previous_selftest = bsp_selftest
                        if b"NEXIOS_BSP_INITRAMFS_FAILED" in observed:
                            bsp_selftest = "FAIL"
                        elif b"NEXIOS_BSP_INITRAMFS_READY" in observed and bsp_selftest != "FAIL":
                            bsp_selftest = "PASS"
                        if bsp_selftest != previous_selftest:
                            report(f"BSP selftest: {bsp_selftest}")
                    if exit_after_pass and any(marker in observed for marker in (
                            b"Kernel panic - not syncing:", b"LINUX_BOOT_FDT_FAILED")):
                        break
                    ready = (
                        re.search(rb"nexios-bsp(?:-failed)?#\s*$", observed)
                        if plan["bsp"] else plan["pass_marker"].encode() in observed
                    )
                    if ready:
                        if not passed and not login_sent:
                            report("Linux console ready; UART saved to linux-uart.log")
                        if not exit_after_pass:
                            passed = True
                        elif not login_sent:
                            with (out / "linux-uart.in").open("ab") as uart_in:
                                uart_in.write(b"\n" if plan["bsp"] else b"root\n")
                            login_sent = True
                    if (
                        exit_after_pass
                        and login_sent
                        and not probe_sent
                        and re.search(
                            rb"(?:nexios-bsp(?:-failed)?#|root@[^\r\n]*[#>]|~ #)\s*$", observed
                        )
                    ):
                        cpus = int(plan["environment"].get("QBOX_APOLLO_NUM_CPUS", "1"))
                        disk_probe = (
                            "test -b /dev/vda && dd if=/dev/vda of=/dev/null bs=512 count=8 && "
                            if plan.get("source_rootfs") else ""
                        )
                        with (out / "linux-uart.in").open("ab") as uart_in:
                            uart_in.write(
                                (
                                    "uname -a && cat /proc/cpuinfo && "
                                    f"test \"$(grep -c '^processor' /proc/cpuinfo)\" -eq {cpus} && "
                                    f"{disk_probe}"
                                    "printf 'QBOX_LINUX_%s\\n' SMOKE_DONE\n"
                                ).encode()
                            )
                        probe_sent = True
                    if probe_sent and b"QBOX_LINUX_SMOKE_DONE" in observed:
                        report("CPU and disk smoke check: PASS")
                        passed, status, rc = True, "PASS", 0
                        break
                    if timeout and time.monotonic() - started >= timeout:
                        report(f"Timeout reached ({timeout:g}s); stopping QBox")
                        status, rc = ("PASS", 0) if passed else ("TIMEOUT", 124)
                        break
                    time.sleep(0.1)
                else:
                    rc = child.returncode or (0 if passed else 1)
                    status = "PASS" if passed and rc == 0 else "FAIL"
        except KeyboardInterrupt:
            status, rc = ("PASS", 0) if passed else ("STOPPED", 130)
        finally:
            stats.close()
            for sig, handler in old.items():
                signal.signal(sig, handler)
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                if child.stdout is not None:
                    # A terminating simulator may still emit more than a pipe
                    # buffer of logs. Keep consuming until exit or the deadline.
                    deadline = time.monotonic() + 5
                    while child.poll() is None and time.monotonic() < deadline:
                        drain_output(child.stdout, log)
                        time.sleep(.02)
                try:
                    child.wait(timeout=0 if child.stdout is not None else 5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
            if child.stdout is not None:
                drain_output(child.stdout, log)
                child.stdout.close()
            (out / "result.json").write_text(
                json.dumps(
                    {
                        "status": status,
                        "login_observed": passed,
                        "poweroff_observed": poweroff_observed,
                        "bsp_selftest": bsp_selftest,
                        "returncode": rc,
                        "elapsed_seconds": time.monotonic() - started,
                        "qualification": "AP Linux boot only; other domains are mocks",
                    },
                    indent=2,
                )
                + "\n"
            )
            report(f"Stopped: status={status} returncode={rc} bsp_selftest={bsp_selftest}")
    return rc


def start_tmux(
    args: argparse.Namespace, out: Path, *, script: Path | None = None,
    program: str = "QBox", log_name: str = "qbox.log", key_prefix: str = "qbox-linux-",
    bottom_command: list[str] | None = None,
    console_command: list[str] | None = None,
) -> None:
    def tmux(*values: str) -> str:
        return subprocess.check_output(["tmux", *values], text=True).strip()

    if (
        subprocess.run(
            ["tmux", "has-session", "-t", "=" + args.session],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    ):
        raise ValueError(
            f"tmux session {args.session!r} already exists; attach or choose --session NAME"
        )
    script = script or Path(__file__).resolve()
    top = tmux(
        "new-session",
        "-d",
        "-P",
        "-F",
        "#{pane_id}",
        "-s",
        args.session,
        "-x",
        "160",
        "-y",
        "50",
        "-c",
        str(ROOT),
        shlex.join(console_command or [sys.executable, str(script), "console", str(out)]),
    )
    try:
        # Key bindings are server-wide; copy root into a session-private table
        # so F12 does not replace bindings belonging to other tmux sessions.
        key_table = key_prefix + top.removeprefix("%")
        bindings = tmux("list-keys", "-T", "root")
        bindings = re.sub(
            r"(?m)^(bind-key\b[^\n]*?) -T root(?=\s)",
            rf"\1 -T {key_table}",
            bindings,
        )
        subprocess.check_output(
            ["tmux", "source-file", "-"], input=bindings + "\n", text=True
        )
        tmux("bind-key", "-T", key_table, "F12", "kill-session")
        tmux("set-option", "-t", args.session, "key-table", key_table)
        tmux("set-option", "-t", args.session, "mouse", "on")
        bottom = tmux(
            "split-window",
            "-v",
            "-l",
            "30%",
            "-P",
            "-F",
            "#{pane_id}",
            "-t",
            top,
            "-c",
            str(ROOT),
            shlex.join(bottom_command or ["tail", "-n", "+1", "-F", str(out / log_name)]),
        )
        tmux("split-window", "-h", "-l", "50%", "-t", bottom, "-c", str(ROOT))
        if console_command is not None:
            tmux("set-window-option", "-t", top, "remain-on-exit", "on")
            tmux("set-window-option", "-t", top, "pane-border-status", "top")
            tmux("select-pane", "-t", top, "-T", f"{program} UART")
            tmux("select-pane", "-t", bottom, "-T", f"{program} platform log")
        tmux("select-pane", "-t", top)
        if console_command is None:
            command = shlex.join(
                [
                    sys.executable,
                    str(script),
                    "supervise",
                    str(out),
                    str(args.timeout),
                    str(int(args.exit_after_pass)),
                ]
            )
            # Keep the supervisor in the session so killing that session stops its child.
            tmux("new-window", "-d", "-t", args.session, "-n", "supervisor", command)
    except (OSError, subprocess.CalledProcessError):
        # new-session succeeded here; never clean up a pre-existing session.
        subprocess.run(
            ["tmux", "kill-session", "-t", "=" + args.session],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        raise
    print(f"tmux attach-session -t {shlex.quote(args.session)}", flush=True)
    print(f"F12: stop {program} and close this session; mouse: select panes.", flush=True)
    if not args.no_attach:
        subprocess.run(["tmux", "attach-session", "-t", args.session], check=True)


def main() -> int:
    if len(sys.argv) > 2 and sys.argv[1] == "console":
        return console(Path(sys.argv[2]))
    if len(sys.argv) > 2 and sys.argv[1] == "supervise":
        return supervise(Path(sys.argv[2]), float(sys.argv[3]), bool(int(sys.argv[4])))
    args = parser().parse_args()
    if args.timeout < 0:
        raise ValueError("--timeout must be non-negative")
    if args.ssh_port is not None and not 1024 <= args.ssh_port <= 65535:
        raise ValueError("--ssh-port must be 1024..65535")
    deploy = (
        args.deploy_dir or args.build_dir / "tmp_baremetal/deploy/images/apollo-qvp"
    ).absolute()
    image = "nexios-bsp-initramfs" if args.bsp else "nexios-image"
    default_qboxconf = deploy / f"{image}-apollo-qvp.qboxconf"
    provider_fallback = deploy / "nexios-bsp-initramfs-apollo-qvp.qboxconf"
    if not default_qboxconf.exists() and provider_fallback.exists():
        default_qboxconf = provider_fallback
    qboxconf = required(args.qboxconf or default_qboxconf, "qboxconf")
    env = provider_environment(qboxconf, args.build_dir.absolute())
    kernel = required(args.kernel or deploy / "Image", "Linux Image")
    dtb = required(
        args.dtb or Path(env.get("QBOXCONF_IMAGE_AP_DTB") or deploy / "apollo-qvp-saturn-v.dtb"),
        "Linux DTB",
    )
    configured_cpus = env.get("QBOXCONF_APOLLO_NUM_CPUS")
    args.cpus = resolve_cpu_count(
        args.cpus, int(configured_cpus) if configured_cpus else None,
        dtb, explicit_dtb=args.dtb is not None,
    )
    initrd_image = "nexios-bsp-initramfs" if args.bsp else "nexios-initramfs-image"
    initrd = required(
        args.initrd or deploy / f"{initrd_image}-apollo-qvp.cpio.gz",
        "BSP initramfs" if args.bsp else "Yocto dm-verity initramfs",
    )
    rootfs = required(
        args.rootfs or deploy / f"{image}-apollo-qvp.wic",
        "BSP WIC disk" if args.bsp else "Yocto rootfs disk",
    )
    conf = required(args.conf, "Linux platform Lua")
    executable = required(Path(env["QBOXCONF_EXE"]), "QBox executable")
    out = (
        args.out_dir
        or ROOT
        / "build/qbox-apollo-qvp"
        / ("linux-" + time.strftime("%Y%m%d-%H%M%S") + f"-{os.getpid()}")
    ).absolute()
    disk = out / "rootfs.wic" if args.copy_disk else rootfs
    bootargs = args.bootargs
    if not bootargs:
        bootargs = subprocess.check_output(
            ["fdtget", str(dtb), "/chosen", "bootargs"], text=True,
        ).strip()
        if not args.bsp:
            bootargs += " rootwait root=PARTLABEL=rootro_a ro"
        # The selected DT and model population were checked above.
        bootargs = re.sub(r"\bnr_cpus=\d+\b", f"nr_cpus={args.cpus}", bootargs)
    stats_enabled = interval_from_args(args) is not None
    monitor = monitor_plan(args.monitor or args.qmp or stats_enabled, args.monitor_port, out, cpus=args.cpus)
    launch_env = {
        **monitor_environment(monitor),
        "QBOX_RDASPEN_ENABLE_AP_CPUS": "true",
        "QBOX_RDASPEN_HOST_MEMORY_DMI": "true",
        "LD_LIBRARY_PATH": env["QBOXCONF_LD_LIBRARY_PATH"],
        "QBOX_APOLLO_NUM_CPUS": str(args.cpus),
        "QBOX_LINUX_KERNEL": str(kernel),
        "QBOX_LINUX_DTB": str(out / "linux-boot/linux.dtb"),
        "QBOX_LINUX_INITRD": str(initrd),
        "QBOX_LINUX_BOOT_STUB": str(out / "linux-boot/boot.bin"),
        "QBOX_RDASPEN_ROOTFS": str(disk),
        "QBOX_APOLLO_NETDEV": (f"type=user,hostfwd=tcp:127.0.0.1:{args.ssh_port}-:22"
                              if args.ssh_port is not None else os.environ.get("QBOX_APOLLO_NETDEV",
                                  os.environ.get("QBOX_RDASPEN_NETDEV", "type=user,hostfwd=tcp::2222-:22"))),
        "QBOX_RDASPEN_PRIMARY_CONSOLE_LOG": str(out / "linux-uart.log"),
        "QBOX_RDASPEN_PRIMARY_UART_READ_FILE": str(out / "linux-uart.in"),
        "QBOX_RDASPEN_MHU_TRACE": "true" if args.domain_trace else "false",
        "QBOX_RDASPEN_MHU_TRACE_FILE": str(out / "qbox.log"),
        "QBOX_RDASPEN_MHU_TRACE_LIMIT": os.environ.get("QBOX_RDASPEN_MHU_TRACE_LIMIT", "256"),
    }
    command = [str(executable), "-l", str(conf), "-p", f"log_level={args.log_level}"]
    # Like the full-system tmux runner, flush output promptly to its log pane.
    if shutil.which("stdbuf"):
        command = [shutil.which("stdbuf"), "-oL", "-eL", *command]
    for value in args.platform_param:
        command.extend(["-p", value])
    plan = {
        "schema_version": 1, "run_id": out.name, "backend": "qbox", "monitor": monitor,
        "stats_interval": interval_from_args(args),
        "qmp_enabled": args.qmp or stats_enabled,
        "command": command,
        "environment": launch_env,
        "qboxconf": str(qboxconf),
        "source_dtb": str(dtb),
        "source_rootfs": str(rootfs),
        "copy_disk": args.copy_disk,
        "bootargs": bootargs,
        "bsp": args.bsp,
        "pass_marker": "nexios-bsp(?:-failed)?#" if args.bsp else "apollo-qvp login:",
        "layout": "Linux UART 70%; QBox log and interactive shell 15% each",
    }
    print(json.dumps(plan, indent=2), flush=True)
    if args.dry_run:
        return 0
    monitor_preflight(monitor)
    prepare_qmp(plan)
    if not args.headless and not shutil.which("tmux"):
        raise ValueError("tmux is required; use --headless otherwise")
    out.mkdir(parents=True, exist_ok=False)
    for name in ("linux-uart.log", "linux-uart.in", "qbox.log"):
        (out / name).touch()
    if args.copy_disk:
        subprocess.run(
            [
                "cp",
                "--reflink=auto",
                "--sparse=always",
                str(rootfs),
                str(disk),
            ],
            check=True,
        )
    # Boot payload helper is shared with the platform's direct-boot tests.
    helper = (
        ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/linux-boot/prepare.py"
    )
    prepare = [
        sys.executable,
        str(helper),
        "--kernel",
        str(kernel),
        "--dtb",
        str(dtb),
        "--output-dir",
        str(out / "linux-boot"),
        "--bootargs",
        bootargs,
    ]
    prepare.extend(["--initrd", str(initrd)])
    payload = json.loads(subprocess.check_output(prepare, text=True))
    launch_env["QBOX_LINUX_BOOT_STUB"] = payload["boot_stub"]
    launch_env["QBOX_LINUX_DTB"] = payload["dtb"]
    launch_env["QBOX_LINUX_INITRD"] = payload["initrd"] or ""
    (out / "launch.json").write_text(json.dumps(plan, indent=2) + "\n")
    if args.headless:
        return supervise(out, args.timeout, args.exit_after_pass, echo_uart=True)
    start_tmux(args, out)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"run_qbox_linux: {error}", file=sys.stderr)
        raise SystemExit(1)
