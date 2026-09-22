#!/usr/bin/env python3
"""Boot Apollo Yocto or BSP Linux on the standalone QEMU Apollo machine."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import select
import shutil
import signal
import socket
import stat
import subprocess
import sys
import time

from run_qbox_linux import AutoSDConsole, ROOT, autosd_manifest, console, required, start_tmux


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    images = p.add_mutually_exclusive_group()
    images.add_argument("--bsp", action="store_true", help="use BSP initramfs and boot/misc WIC")
    images.add_argument("--autosd", type=Path, help="prepared AutoSD image JSON manifest")
    images.add_argument("--native-autosd-disk", type=Path,
                        help="raw AutoSD AIB disk: boot EFI without replacing native UKI slots")
    p.add_argument("--native-autosd-mode", choices=("regular", "ostree"),
                   help="native disk userspace smoke contract (default: ostree)")
    p.add_argument("--build-dir", type=Path, default=ROOT / "build")
    p.add_argument("--deploy-dir", type=Path)
    p.add_argument("--provider", type=Path, help="qemu-apollo-native deployment manifest")
    p.add_argument("--qemu", type=Path, help="override standalone qemu-system-aarch64")
    p.add_argument("--kernel", type=Path)
    p.add_argument("--uki", type=Path, help="adapt a Yocto UKI and boot through AutoSD UKIBoot A/B slots")
    p.add_argument("--uboot", type=Path, help="standalone Apollo EFI firmware for UKI boot")
    p.add_argument("--ukiboot-dir", type=Path,
                   help="UKIBoot loader/addons; native mode replaces ESP files only when explicitly supplied")
    p.add_argument("--initrd", type=Path)
    p.add_argument("--rootfs", type=Path)
    p.add_argument("--reuse-autosd-disk", type=Path, metavar="PREVIOUS_OUT_DIR",
                   help="boot a completed UKIBoot run's private disk in place without rewriting slots")
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
    native = args.native_autosd_disk is not None
    efi = bool(args.uki or native)
    if native and any((args.uki, args.kernel, args.initrd, args.rootfs, args.dtb, args.bootargs)):
        raise ValueError("--native-autosd-disk cannot be combined with UKI/kernel/initrd/rootfs/DTB/bootargs overrides")
    if args.native_autosd_mode and not native:
        raise ValueError("--native-autosd-mode requires --native-autosd-disk")
    if native and args.reuse_autosd_disk and args.ukiboot_dir:
        raise ValueError("reused native disks cannot replace ESP files; omit --ukiboot-dir")
    autosd = ({"mode": args.native_autosd_mode or "ostree",
               "rootfs": str(required(args.native_autosd_disk, "native AutoSD raw disk"))}
              if native else autosd_manifest(args.autosd))
    if args.reuse_autosd_disk and (not efi or not autosd or args.rootfs or args.initrd or args.bootargs):
        raise ValueError("--reuse-autosd-disk requires --autosd and --uki (or --native-autosd-disk), without rootfs/initrd/bootargs overrides")
    if args.uki and (not autosd or args.kernel or args.dtb):
        raise ValueError("--uki requires --autosd and cannot be combined with --kernel or --dtb")
    if args.uboot and not efi:
        raise ValueError("--uboot requires --uki or --native-autosd-disk")
    if args.ukiboot_dir and not efi:
        raise ValueError("--ukiboot-dir requires --uki or --native-autosd-disk")
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
    kernel = (required(args.uboot or deploy / "u-boot-apollo-qemu.bin", "standalone U-Boot") if native else
              required(args.uki or args.kernel or deploy / "Image", "UKI" if args.uki else "Linux Image"))
    initrd = (None if native else required(args.initrd or (Path(autosd["initrd"]) if autosd else
              deploy / f"{initrd_name}-apollo-qvp.cpio.gz"), "initramfs"))
    disk = required(args.rootfs or (Path(autosd["rootfs"]) if autosd else deploy / f"{image}-apollo-qvp.wic"), "rootfs disk")
    bootargs = args.bootargs or autosd.get("bootargs") or "console=ttyAMA0 earlycon=pl011,0x1a400000 " + (
        "rdinit=/init" if args.bsp else "rootwait root=PARTLABEL=rootro_a ro"
    )
    if args.uki and not any(word.startswith("efi=") for word in bootargs.split()):
        # PREEMPT_RT disables runtime services by default. UKI userspace needs
        # EFI variables; enabling these services does not qualify RT latency.
        bootargs += " efi=runtime"
    command = [str(executable), "-machine", "apollo-qvp", "-accel", "tcg",
               "-smp", str(args.cpus), "-m", args.memory, "-display", "none",
               "-chardev", "socket,id=hmp,fd=@MONITOR_FD@",
               "-mon", "chardev=hmp,mode=readline",
               "-chardev", "stdio,id=uart,signal=off",
               "-serial", "chardev:uart", "-kernel", str(kernel),
               *([] if native else ["-initrd", str(initrd), "-append", bootargs]),
               "-drive", f"if=none,id=rootfs,format=raw,file={str(out / 'rootfs.wic').replace(',', ',,')}",
               "-device", "virtio-blk-device,drive=rootfs,bus=virtio-mmio-bus.0",
               "-netdev", args.netdev,
               "-device", "virtio-net-device,netdev=net0,bus=virtio-mmio-bus.1,mac=52:54:00:12:34:56",
               "-device", "virtio-rng-device,bus=virtio-mmio-bus.2"]
    if args.dtb:
        command += ["-dtb", str(required(args.dtb, "DTB"))]
    uki = None
    if efi:
        from autosd_disk import inspect_disk
        if any(word.startswith("androidboot.slot_suffix=") for word in bootargs.split()):
            raise ValueError("UKIBoot must select the slot; remove androidboot.slot_suffix from bootargs")
        memory = re.fullmatch(r"([0-9]+)([KkMmGgTt]?)", args.memory)
        if not memory or int(memory[1]) * {"K": 1024, "M": 1024**2,
                "G": 1024**3, "T": 1024**4, "": 1024**2}[memory[2].upper()] < 1024**3:
            raise ValueError("EFI boot requires at least 1 GiB RAM (for example --memory 1024M)")
        source = None
        if not native:
            from autosd_uki import inspect_uki
            source = inspect_uki(kernel)
            virtual_end = max((section["rva"] + max(section["size"], section["raw_size"])
                               for section in source.get("sections", {}).values()), default=0)
            if max(kernel.stat().st_size, virtual_end) + initrd.stat().st_size + 65536 > 256 * 1024**2:
                raise ValueError("UKI plus AutoSD initrd exceeds the 256 MiB loader safety limit")
        firmware = required(args.uboot or deploy / "u-boot-apollo-qemu.bin", "standalone U-Boot (build u-boot-apollo-qemu)")
        loader_dir = args.ukiboot_dir or deploy
        loader_files = {key: str(required(loader_dir / name, "UKIBoot artifact (build ./yocto_build.sh --keep-conf ukiboot)"))
                        for key, name in (("loader", "ukibootaa64.efi"), ("addon_a", "slot_a.addon.efi"),
                                          ("addon_b", "slot_b.addon.efi"))} if not native or args.ukiboot_dir else {}
        disk_info = inspect_disk(disk)
        index = command.index("-kernel")
        command[index:index + (2 if native else 6)] = ["-kernel", str(firmware)]
        uki = {"source": None if native else str(kernel), "output": None if native else str(out / "autosd.efi"),
               "native_slots": native,
               "firmware": str(firmware), "firmware_sha256": hashlib.sha256(firmware.read_bytes()).hexdigest(),
               "bootargs": None if native else bootargs, "source_metadata": source,
               "loader_files": loader_files, "source_disk": disk_info,
               "boot_command": "setenv bootargs; "
                   f"fatload virtio 0:{disk_info['partitions']['efi']['index']} 0x90000000 /EFI/BOOT/BOOTAA64.EFI "
                   "&& bootefi 0x90000000 ${fdtcontroladdr}\n"}
        if native:
            uki["payload_policy"] = "preserve-native-slots-and-bootctl"
    reused_disk = None
    if args.reuse_autosd_disk:
        reused_disk, prepared = validate_reused_disk(args.reuse_autosd_disk, autosd)
        uki["prepared_disk"] = prepared
        uki["source_disk"] = prepared
        uki["preparation_evidence"] = str(args.reuse_autosd_disk.absolute() / "launch.json")
        uki["boot_command"] = ("setenv bootargs; "
            f"fatload virtio 0:{prepared['partitions']['efi']['index']} 0x90000000 /EFI/BOOT/BOOTAA64.EFI "
            "&& bootefi 0x90000000 ${fdtcontroladdr}\n")
        uki["payload_policy"] = "preserve existing on-disk slots and ESP; no payload installed"
        drive = command.index("-drive") + 1
        command[drive] = f"if=none,id=rootfs,format=raw,file={str(reused_disk).replace(',', ',,')}"
    return {"command": command, "environment": environment, "bsp": args.bsp,
            "autosd_mode": autosd.get("mode"),
            "boot_method": "ukiboot-efi" if uki else "direct-linux",
            "uki": uki,
            "disk_path": str(reused_disk or out / "rootfs.wic"),
            "reused_disk": bool(reused_disk),
            "cpus": args.cpus, "source_rootfs": str(reused_disk or disk), "kernel": str(kernel) if not reused_disk and not native else None,
            "initrd": str(initrd) if initrd else None, "provider": str(provider) if not args.qemu else None,
            "layout": "Linux UART 70%; QEMU monitor and interactive shell 15% each"}


def validate_reused_disk(previous: Path, autosd: dict) -> tuple[Path, dict]:
    """Accept only a completed launcher's private copy; OTA may change slot bytes."""
    from autosd_disk import inspect_disk
    previous = previous.absolute()
    disk = previous / "rootfs.wic"
    info = disk.lstat()
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1
            or disk.resolve() != disk or disk.samefile(autosd["rootfs"])):
        raise ValueError("reuse requires an owned, non-linked private disk, not the original image")
    plan = json.loads((previous / "launch.json").read_text())
    if not (previous / "result.json").is_file():
        raise ValueError("reuse requires a completed previous run")
    prepared = (plan.get("uki") or {}).get("prepared_disk")
    if (plan.get("boot_method") != "ukiboot-efi" or plan.get("autosd_mode") != autosd["mode"]
            or not prepared or plan.get("reused_disk")
            or Path(plan.get("disk_path", str(disk))) != disk):
        raise ValueError("previous run does not identify a matching prepared UKIBoot disk")
    current = inspect_disk(disk)
    if any(current[key] != prepared[key] for key in ("disk_size", "sector_size", "partitions")):
        raise ValueError("prepared disk GPT no longer matches previous launch evidence")
    # Slot hashes in preparation evidence are historical after OTA. Report
    # current geometry/control and retain provenance separately in launch.json.
    return disk, current


def supervise(out: Path, timeout: float, exit_after_pass: bool, *, echo_uart: bool = False) -> int:
    """Hold a launcher lock throughout execution; QEMU also locks its raw image."""
    plan = json.loads((out / "launch.json").read_text())
    disk = Path(plan.get("disk_path", str(out / "rootfs.wic")))
    if disk.exists():
        fd = os.open(disk, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise ValueError("disk is already used by another launcher") from error
            return _supervise(out, timeout, exit_after_pass, echo_uart=echo_uart)
    if plan.get("reused_disk"):
        raise ValueError("prepared disk disappeared before launch")
    return _supervise(out, timeout, exit_after_pass, echo_uart=echo_uart)


def _supervise(out: Path, timeout: float, exit_after_pass: bool, *, echo_uart: bool = False) -> int:
    """Bridge QEMU stdio to the same persistent UART files as the tmux console."""
    plan = json.loads((out / "launch.json").read_text())
    autosd = (AutoSDConsole(plan["autosd_mode"], plan["cpus"], "QEMU_LINUX")
              if plan.get("autosd_mode") else None)
    started = time.monotonic()
    passed = login_sent = probe_sent = firmware_started = efi_observed = False
    booted_slot = None
    firmware_boots = 0
    boot_history = []
    banner_tail = b""
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
                    # Scan only new bytes plus a bounded partial banner, not the
                    # retained console history. A reboot invalidates old PASS.
                    banners = banner_tail + data
                    match = list(re.finditer(rb"(?:^|\n)U-Boot(?: |\r?\n)", banners))
                    banner_tail = (banners[match[-1].end():] if match else banners)[-7:]
                    if plan.get("uki") and match:
                        if firmware_boots:
                            boot_history.append({"firmware_boot": firmware_boots, "login_observed": passed,
                                                 "efi_boot_observed": efi_observed, "ukiboot_slot": booted_slot,
                                                 "ended_by": "firmware restart"})
                        firmware_boots += len(match)
                        passed = login_sent = probe_sent = firmware_started = efi_observed = False
                        booted_slot = None
                        autosd = AutoSDConsole(plan["autosd_mode"], plan["cpus"], "QEMU_LINUX")
                        observed = banners[match[-1].start():]
                if plan["bsp"]:
                    if b"NEXIOS_BSP_INITRAMFS_FAILED" in observed:
                        bsp_selftest = "FAIL"
                    elif b"NEXIOS_BSP_INITRAMFS_READY" in observed and bsp_selftest != "FAIL":
                        bsp_selftest = "PASS"
                if b"Kernel panic - not syncing:" in observed:
                    break
                if plan.get("uki") and not firmware_started and re.search(rb"(?:^|\n)=>\s*$", observed):
                    child.stdin.write(plan["uki"]["boot_command"].encode())
                    firmware_started = True
                prompt = re.search(rb"(?:nexios-bsp(?:-failed)?#|root@[^\r\n]*[#>]|~ #)\s*$", observed)
                boot_ready = prompt if plan["bsp"] else re.search(rb"(?:apollo-qvp|nexios)[^\r\n]* login:\s*$", observed)
                if autosd:
                    response = autosd.respond(observed, exit_after_pass)
                    if response:
                        if plan.get("uki") and autosd.probe_sent:
                            response = (b"for attempt in $(seq 1 60); do "
                                        b"systemctl is-active --quiet ukiboot-set-success.service && break; "
                                        b"systemctl is-failed --quiet ukiboot-set-success.service && break; sleep 1; done; "
                                        b"journalctl -b -u ukiboot-set-success.service --no-pager; "
                                        b"test -d /sys/firmware/efi && printf 'APOLLO_%s\\n' EFI_BOOTED && "
                                        b"grep -Eq '(^| )androidboot.slot_suffix=_[ab]( |$)' /proc/cmdline && "
                                        b"systemctl is-active --quiet ukiboot-set-success.service && "
                                        b"ukibootctl dump && slot=$(ukibootctl get-booted) && "
                                        b"test \"$slot\" = \"$(ukibootctl get-active)\" && "
                                        b"printf 'APOLLO_UKIBOOT_%s=%s\\n' SLOT \"$slot\" && "
                                        + response)
                        child.stdin.write(response)
                    login_sent, probe_sent = autosd.login_sent, autosd.probe_sent
                    if autosd.ready and not exit_after_pass:
                        passed = True
                elif prompt or boot_ready:
                    if not exit_after_pass:
                        passed = True
                    elif not login_sent:
                        child.stdin.write(b"\n" if plan["bsp"] or prompt else b"root\n")
                        login_sent = True
                if b"APOLLO_EFI_BOOTED\r\n" in observed or b"APOLLO_EFI_BOOTED\n" in observed:
                    efi_observed = True
                slot_match = re.search(rb"(?:^|\n)APOLLO_UKIBOOT_SLOT=([01])\r?\n", observed)
                if slot_match:
                    booted_slot = int(slot_match[1])
                if not autosd and exit_after_pass and login_sent and prompt and not probe_sent:
                    # Split the marker so the echoed command cannot satisfy it.
                    child.stdin.write((
                        "uname -a && "
                        f"test \"$(grep -c '^processor' /proc/cpuinfo)\" -eq {plan['cpus']} && "
                        "test -b /dev/vda && dd if=/dev/vda of=/dev/null bs=512 count=8 && "
                        "printf 'QEMU_LINUX_%s\\n' SMOKE_DONE\n"
                    ).encode())
                    probe_sent = True
                if probe_sent and b"QEMU_LINUX_SMOKE_DONE" in observed and (not plan.get("uki") or (efi_observed and booted_slot is not None)):
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
            bootctl = None
            if (plan.get("uki") or {}).get("prepared_disk"):
                from autosd_disk import inspect_disk
                try:
                    bootctl = inspect_disk(Path(plan.get("disk_path", str(out / "rootfs.wic"))))["bootctl"]
                    if exit_after_pass and passed:
                        slot_state = bootctl["slots"][booted_slot] if booted_slot is not None else {}
                        if not (bootctl["valid"] and slot_state.get("successful_boot") == 1
                                and slot_state.get("tries_remaining") == 0):
                            passed, status, rc = False, "FAIL", 1
                except (OSError, ValueError) as error:
                    bootctl = {"error": str(error)}
                    passed, status, rc = False, "FAIL", 1
            (out / "result.json").write_text(json.dumps({
                "status": status, "login_observed": passed, "bsp_selftest": bsp_selftest,
                "returncode": rc, "elapsed_seconds": time.monotonic() - started,
                "smoke_completed": bool(probe_sent and passed),
                "autosd_mode": plan.get("autosd_mode"),
                "efi_boot_observed": efi_observed,
                "ukiboot_slot": booted_slot,
                "firmware_boots_observed": firmware_boots,
                "boot_history": boot_history + ([{"firmware_boot": firmware_boots,
                    "login_observed": passed, "efi_boot_observed": efi_observed,
                    "ukiboot_slot": booted_slot, "ended_by": status}] if firmware_boots else []),
                "bootctl": bootctl,
                "ukiboot_service": "PASS" if booted_slot is not None else ("NOT_OBSERVED" if plan.get("uki") else "NOT_APPLICABLE"),
                "boot_method": plan.get("boot_method", "direct-linux"),
                "qualification": ("AutoSD AP boot only; no OTA or secure boot qualification"
                                  if autosd else "Standalone QEMU AP boot only; not full BSP qualification"),
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
    if plan.get("uki") and not plan["reused_disk"] and not plan["uki"].get("native_slots"):
        from autosd_uki import prepare_uki
        plan["uki"]["prepared_metadata"] = prepare_uki(
            Path(plan["uki"]["source"]), Path(plan["initrd"]),
            plan["uki"]["bootargs"], Path(plan["uki"]["output"]))
        plan["uki"]["size"] = Path(plan["uki"]["output"]).stat().st_size
    for name in ("linux-uart.log", "linux-uart.in", "qemu.log", "qemu-monitor.log", "qemu-monitor.in"):
        (out / name).touch()
    if not plan["reused_disk"]:
        subprocess.run(["cp", "--reflink=auto", "--sparse=always", plan["source_rootfs"],
                        str(out / "rootfs.wic")], check=True)
    if plan.get("uki") and not plan["reused_disk"]:
        from autosd_disk import prepare_disk, prepare_native_disk
        overrides = {key: Path(value) for key, value in plan["uki"]["loader_files"].items()}
        plan["uki"]["prepared_disk"] = (
            prepare_native_disk(out / "rootfs.wic", **overrides) if plan["uki"].get("native_slots") else
            prepare_disk(out / "rootfs.wic", Path(plan["uki"]["output"]), **overrides))
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
