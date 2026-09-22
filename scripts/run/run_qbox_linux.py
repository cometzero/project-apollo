#!/usr/bin/env python3
"""Launch the Apollo AP Linux platform using deployed Yocto artifacts."""

from __future__ import annotations

import argparse
import hashlib
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


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    images = p.add_mutually_exclusive_group()
    images.add_argument(
        "--bsp", action="store_true", help="boot the BSP initramfs with its BSP WIC disk"
    )
    images.add_argument("--autosd", type=Path, help="prepared AutoSD image JSON manifest")
    p.add_argument("--build-dir", type=Path, default=ROOT / "build")
    p.add_argument("--deploy-dir", type=Path)
    p.add_argument("--qboxconf", type=Path)
    p.add_argument("--kernel", type=Path)
    p.add_argument("--uki", type=Path, help="first-boot-only AutoSD UKIBoot/EFI using a Yocto UKI")
    p.add_argument("--uboot", type=Path, help="Apollo standalone U-Boot firmware for --uki")
    p.add_argument("--ukiboot-dir", type=Path, help="deployed UKIBoot loader and slot addons")
    p.add_argument("--dtb", type=Path)
    p.add_argument("--initrd", type=Path)
    p.add_argument("--rootfs", type=Path)
    p.add_argument("--cpus", type=int, choices=range(1, 17), default=4)
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


def autosd_manifest(path: Path | None) -> dict:
    if path is None:
        return {}
    manifest = json.loads(required(path, "AutoSD manifest").read_text())
    if not isinstance(manifest, dict) or manifest.get("mode") not in ("regular", "ostree"):
        raise ValueError("AutoSD manifest mode must be regular or ostree")
    for name in ("rootfs", "initrd"):
        value = manifest.get(name)
        if not isinstance(value, str) or not Path(value).is_absolute():
            raise ValueError(f"AutoSD manifest {name} must be an absolute path")
    if not isinstance(manifest.get("bootargs"), str) or not manifest["bootargs"].strip():
        raise ValueError("AutoSD manifest requires bootargs")
    return manifest


class AutoSDConsole:
    """Respond once per login stage; never accept an echoed probe as success."""

    def __init__(self, mode: str, cpus: int, marker: str):
        self.mode, self.cpus, self.marker = mode, cpus, marker
        self.login_sent = self.password_sent = self.probe_sent = False
        self.ready = False

    def respond(self, observed: bytes, probe: bool) -> bytes:
        prompt = re.search(rb"(?:\[root@[^\r\n]*\]#|root@[^\r\n]*#)\s*$", observed)
        self.ready = bool(prompt)
        if prompt and probe and not self.probe_sent:
            self.probe_sent = True
            # Composefs detaches its EROFS backing mount after creating the
            # overlay; /proc/mounts need not expose that backing filesystem.
            ostree = ("test -e /run/ostree-booted && ostree admin status && "
                      "test \"$(findmnt -n -o FSTYPE -T /)\" = overlay && "
                      if self.mode == "ostree" else "")
            return (
                "for path in / /usr /sysroot; do findmnt -T \"$path\"; done; "
                "losetup -a; getenforce; systemctl --failed --no-pager; "
                "uname -a && cat /etc/os-release && "
                "(. /etc/os-release; test \"$ID\" = autosd) && "
                f"test \"$(grep -c '^processor' /proc/cpuinfo)\" -eq {self.cpus} && "
                "test -b /dev/vda && dd if=/dev/vda of=/dev/null bs=512 count=8 && "
                f"{ostree}printf '{self.marker}_%s\\n' SMOKE_DONE\n"
            ).encode()
        if not self.login_sent and re.search(rb"[^\r\n]+ login:\s*$", observed):
            self.login_sent = True
            return b"root\n"
        if self.login_sent and not self.password_sent and re.search(rb"Password:\s*$", observed):
            self.password_sent = True
            return b"password\n"
        return b""


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
    autosd = (AutoSDConsole(plan["autosd_mode"], int(plan["environment"].get("QBOX_APOLLO_NUM_CPUS", "1")),
                           "QBOX_LINUX") if plan.get("autosd_mode") else None)
    started = time.monotonic()
    passed = False
    login_sent = False
    probe_sent = False
    firmware_started = efi_observed = False
    booted_slot = None
    firmware_boots = 0
    banner_tail = b""
    bsp_selftest = "NOT_OBSERVED" if plan["bsp"] else "NOT_APPLICABLE"
    status = "FAIL"
    rc = 1
    with (out / "qbox.log").open("ab", buffering=0) as log:
        def report(message: str) -> None:
            log.write(f"[runner {time.monotonic() - started:.1f}s] {message}\n".encode())

        report("Starting QBox: " + shlex.join(plan["command"]))
        child = subprocess.Popen(
            plan["command"],
            env={**os.environ, **plan["environment"]},
            cwd=ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )

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
                    chunk = uart.read()
                    if echo_uart and chunk:
                        sys.stdout.buffer.write(chunk)
                        sys.stdout.buffer.flush()
                    observed = (observed + chunk)[-65536:]
                    if plan.get("uki"):
                        banners = banner_tail + chunk
                        matches = list(re.finditer(rb"(?:^|\n)U-Boot(?: |\r?\n)", banners))
                        banner_tail = (banners[matches[-1].end():] if matches else banners)[-7:]
                        firmware_boots += len(matches)
                        if firmware_boots > 1:
                            report("EFI restart is unsupported: SystemC whole-platform reset is not wired")
                            passed, status, rc = False, "UNSUPPORTED_REBOOT", 1
                            break
                        if not firmware_started and re.search(rb"(?:^|\n)=>\s*$", observed):
                            with (out / "linux-uart.in").open("ab") as uart_in:
                                uart_in.write(plan["uki"]["boot_command"].encode())
                            firmware_started = True
                    if plan["bsp"]:
                        previous_selftest = bsp_selftest
                        if b"NEXIOS_BSP_INITRAMFS_FAILED" in observed:
                            bsp_selftest = "FAIL"
                        elif b"NEXIOS_BSP_INITRAMFS_READY" in observed and bsp_selftest != "FAIL":
                            bsp_selftest = "PASS"
                        if bsp_selftest != previous_selftest:
                            report(f"BSP selftest: {bsp_selftest}")
                    if exit_after_pass and b"Kernel panic - not syncing:" in observed:
                        break
                    if autosd:
                        response = autosd.respond(observed, exit_after_pass)
                        if response:
                            if plan.get("uki") and autosd.probe_sent:
                                response = (b"for attempt in $(seq 1 60); do "
                                    b"systemctl is-active --quiet ukiboot-set-success.service && break; "
                                    b"systemctl is-failed --quiet ukiboot-set-success.service && break; sleep 1; done; "
                                    b"journalctl -b -u ukiboot-set-success.service --no-pager; "
                                    b"test -d /sys/firmware/efi && printf 'APOLLO_%s\\n' EFI_BOOTED && "
                                    b"systemctl is-active --quiet ukiboot-set-success.service && "
                                    b"ukibootctl dump && slot=$(ukibootctl get-booted) && "
                                    b"test \"$slot\" = \"$(ukibootctl get-active)\" && "
                                    b"printf 'APOLLO_UKIBOOT_%s=%s\\n' SLOT \"$slot\" && " + response)
                            with (out / "linux-uart.in").open("ab") as uart_in:
                                uart_in.write(response)
                        login_sent, probe_sent = autosd.login_sent, autosd.probe_sent
                        if autosd.ready and not exit_after_pass:
                            passed = True
                    ready = not autosd and (
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
                        and not autosd
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
                    if re.search(rb"(?:^|\n)APOLLO_EFI_BOOTED\r?\n", observed):
                        efi_observed = True
                    slot_match = re.search(rb"(?:^|\n)APOLLO_UKIBOOT_SLOT=([01])\r?\n", observed)
                    if slot_match:
                        booted_slot = int(slot_match[1])
                    if (probe_sent and b"QBOX_LINUX_SMOKE_DONE" in observed
                            and (not plan.get("uki") or (efi_observed and booted_slot is not None))):
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
            for sig, handler in old.items():
                signal.signal(sig, handler)
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
            bootctl = None
            if plan.get("uki"):
                from autosd_disk import inspect_disk
                try:
                    bootctl = inspect_disk(out / "rootfs.wic")["bootctl"]
                    if exit_after_pass and passed:
                        slot = bootctl["slots"][booted_slot] if booted_slot is not None else {}
                        if not (bootctl["valid"] and slot.get("successful_boot") == 1
                                and slot.get("tries_remaining") == 0):
                            passed, status, rc = False, "FAIL", 1
                except (OSError, ValueError) as error:
                    bootctl = {"error": str(error)}
                    passed, status, rc = False, "FAIL", 1
            (out / "result.json").write_text(
                json.dumps(
                    {
                        "status": status,
                        "login_observed": passed,
                        "bsp_selftest": bsp_selftest,
                        "autosd_mode": plan.get("autosd_mode"),
                        "boot_method": "ukiboot-efi" if plan.get("uki") else "direct-linux",
                        "efi_boot_observed": efi_observed,
                        "ukiboot_slot": booted_slot,
                        "bootctl": bootctl,
                        "efi_reboot_support": "NOT_IMPLEMENTED" if plan.get("uki") else "NOT_APPLICABLE",
                        "returncode": rc,
                        "elapsed_seconds": time.monotonic() - started,
                        "qualification": ("AutoSD AP boot only; no OTA or secure boot qualification; other domains are mocks"
                                          if autosd else "AP Linux boot only; other domains are mocks"),
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
        shlex.join([sys.executable, str(script), "console", str(out)]),
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
        tmux("select-pane", "-t", top)
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
    autosd = autosd_manifest(args.autosd)
    if args.uki and (not autosd or args.kernel or args.initrd):
        raise ValueError("--uki requires --autosd without --kernel or --initrd")
    if (args.uboot or args.ukiboot_dir) and not args.uki:
        raise ValueError("--uboot and --ukiboot-dir require --uki")
    if args.timeout < 0:
        raise ValueError("--timeout must be non-negative")
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
    kernel = required((args.uboot or deploy / "u-boot-apollo-qemu.bin") if args.uki
                      else (args.kernel or deploy / "Image"), "Apollo U-Boot" if args.uki else "Linux Image")
    dtb = required(
        args.dtb or Path(env.get("QBOXCONF_IMAGE_AP_DTB") or deploy / "apollo-qvp.dtb"),
        "Linux DTB",
    )
    initrd_image = "nexios-bsp-initramfs" if args.bsp else "nexios-initramfs-image"
    initrd = required(
        args.initrd or (Path(autosd["initrd"]) if autosd else deploy / f"{initrd_image}-apollo-qvp.cpio.gz"),
        "BSP initramfs" if args.bsp else "Yocto dm-verity initramfs",
    )
    rootfs = required(
        args.rootfs or (Path(autosd["rootfs"]) if autosd else deploy / f"{image}-apollo-qvp.wic"),
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
    bootargs = args.bootargs or autosd.get("bootargs") or "console=ttyAMA0 earlycon=pl011,0x1a400000 " + (
        "rdinit=/init" if args.bsp else "rootwait root=PARTLABEL=rootro_a ro"
    )
    uki = None
    if args.uki:
        from autosd_uki import inspect_uki
        from autosd_disk import inspect_disk
        source = required(args.uki, "UKI")
        source_metadata = inspect_uki(source)
        virtual_end = max(section["rva"] + max(section["size"], section["raw_size"])
                          for section in source_metadata["sections"].values())
        if max(source.stat().st_size, virtual_end) + initrd.stat().st_size + 65536 > 256 * 1024**2:
            raise ValueError("UKI plus initrd exceeds the 256 MiB loader safety limit")
        if any(word.startswith("androidboot.slot_suffix=") for word in bootargs.split()):
            raise ValueError("UKIBoot must select the slot, not bootargs")
        if not any(word.startswith("efi=") for word in bootargs.split()):
            bootargs += " efi=runtime"
        loader_dir = args.ukiboot_dir or deploy
        loader_files = {key: str(required(loader_dir / name, "UKIBoot artifact"))
                        for key, name in (("loader", "ukibootaa64.efi"), ("addon_a", "slot_a.addon.efi"),
                                          ("addon_b", "slot_b.addon.efi"))}
        disk_info = inspect_disk(rootfs)
        uki = {"source": str(source), "source_metadata": source_metadata,
               "output": str(out / "autosd.efi"), "bootargs": bootargs,
               "firmware": str(kernel), "firmware_sha256": hashlib.sha256(kernel.read_bytes()).hexdigest(),
               "loader_files": loader_files, "source_disk": disk_info,
               "boot_command": "setenv bootargs; "
                   f"fatload virtio 0:{disk_info['partitions']['efi']['index']} 0x90000000 /EFI/BOOT/BOOTAA64.EFI "
                   "&& bootefi 0x90000000 ${fdtcontroladdr}\n"}
    launch_env = {
        "QBOX_RDASPEN_ENABLE_AP_CPUS": "true",
        "QBOX_RDASPEN_HOST_MEMORY_DMI": "true",
        "LD_LIBRARY_PATH": env["QBOXCONF_LD_LIBRARY_PATH"],
        "QBOX_APOLLO_NUM_CPUS": str(args.cpus),
        "QBOX_LINUX_KERNEL": str(kernel),
        "QBOX_LINUX_DTB": str(out / "linux-boot/linux.dtb"),
        "QBOX_LINUX_INITRD": str(initrd) if initrd and not uki else "",
        "QBOX_LINUX_FIRMWARE": "true" if uki else "false",
        "QBOX_LINUX_BOOT_STUB": str(out / "linux-boot/boot.bin"),
        "QBOX_LINUX_BOOTARGS": bootargs,
        "QBOX_RDASPEN_ROOTFS": str(out / "rootfs.wic") if rootfs else "",
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
        "command": command,
        "environment": launch_env,
        "qboxconf": str(qboxconf),
        "source_dtb": str(dtb),
        "source_rootfs": str(rootfs) if rootfs else None,
        "bsp": args.bsp,
        "autosd_mode": autosd.get("mode"),
        "uki": uki,
        "pass_marker": "nexios-bsp(?:-failed)?#" if args.bsp else "apollo-qvp login:",
        "layout": "Linux UART 70%; QBox log and interactive shell 15% each",
    }
    print(json.dumps(plan, indent=2), flush=True)
    if args.dry_run:
        return 0
    if not args.headless and not shutil.which("tmux"):
        raise ValueError("tmux is required; use --headless otherwise")
    out.mkdir(parents=True, exist_ok=False)
    for name in ("linux-uart.log", "linux-uart.in", "qbox.log"):
        (out / name).touch()
    if rootfs:
        subprocess.run(
            [
                "cp",
                "--reflink=auto",
                "--sparse=always",
                str(rootfs),
                str(out / "rootfs.wic"),
            ],
            check=True,
        )
    if uki:
        from autosd_uki import prepare_uki
        from autosd_disk import prepare_disk
        uki["prepared_metadata"] = prepare_uki(Path(uki["source"]), initrd,
                                                bootargs, Path(uki["output"]))
        uki["prepared_disk"] = prepare_disk(out / "rootfs.wic", Path(uki["output"]),
                                            **{key: Path(value) for key, value in uki["loader_files"].items()})
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
        "--cpus",
        str(args.cpus),
    ]
    if uki:
        prepare.append("--firmware")
    elif initrd:
        prepare.extend(["--initrd", str(initrd)])
    if rootfs:
        prepare.append("--disk")
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
