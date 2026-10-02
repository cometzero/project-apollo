#!/usr/bin/env python3
"""Run AutoSD through the real Apollo QBox full-system firmware chain.

Only a private disk copy is modified. This is a firmware-boot integration
runner, not a replacement for the full platform qualification suite.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import select
import signal
import shutil
import subprocess
import sys
import threading
import time

from run_qbox_linux import autosd_manifest, required
from autosd_uki import inspect_uki, prepare_uki
from autosd_disk import inspect_disk, prepare_disk
from autosd_esp import check_private_esp
from qbox_monitor_manifest import monitor_plan, monitor_environment, preflight as monitor_preflight, update_runtime, prepare_qmp

ROOT = Path(__file__).resolve().parents[2]
LOGS = {
    "rse": ("rse-uart.log", "qbox-rse.log"),
    "si-cl0": ("si-cl0-uart.log", "qbox-safety-island-cl0.log"),
    "si-cl1": ("si-cl1-uart.log", "qbox-safety-island-cl1.log"),
    "ap": ("linux-uart.log", "qbox-primary-console.log"),
}
MARKERS = {
    "rse": ("Starting TF-M BL1_1", "Jumping to the first image slot",
            "Init SCMI comm to SCP succeeded", "RSE to SCP SCMI power on AP succeeded"),
    "si-cl0": ("[SI0_PLATFORM] SCP started", "[FWK] Module initialization complete!",
               "GIC-multiview configured successfully"),
    "si-cl1": ("Out of Reset (OoR) completed on CPU: 0", "Booting Zephyr OS",
               "PFDI Agent setup complete", "PFDI service ready",
               "si_net_init: Network interface configured", "RPMSG Endpoint: ATTACHED"),
    "ap": ("U-Boot", "Starting ukiboot version", "Loading UKI from partition ukiboot_",
           "Linux version", "login:"),
}
FAIL_MARKERS = {
    "rse": ("[ERR]", "[ERROR]", "ASSERT", "PANIC"),
    "si-cl0": ("PFDI monitor timeout", "PANIC", "ASSERTION FAIL",
               "Assertion failed in", "AP watchdog IRQ mask failed",
               "AP watchdog recovery enqueue failed", "AP watchdog recovery request failed",
               "AP watchdog WS1 remains pending after reset",
               "Watchdog rearm FAILED", "Watchdog rearm enqueue failed",
               "Watchdog rearm readback failed",
               "RSE recovery not completed", "RSE recovery completion enqueue failed",
               "SCP-RSE handshake failed"),
    "si-cl1": ("PFDI status timed out", "PROTOCOL_VERSION timed out",
               "PFDI Agent device not ready", "ret=-116", "ZEPHYR FATAL ERROR"),
    "ap": ("Kernel panic", "No working init found", "Unable to mount root fs",
           "bootctl partition is invalid"),
}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--autosd", type=Path,
                   help="manifest (default: BUILD/autosd/demo-minimal-qm-prepared/regular.json)")
    p.add_argument("--rootfs", type=Path)
    p.add_argument("--build-dir", type=Path, default=ROOT / "build")
    p.add_argument("--deploy-dir", type=Path)
    p.add_argument("--uki", type=Path)
    p.add_argument("--out-dir", type=Path, help="new output directory (default: timestamped build/qbox-apollo-qvp/autosd-full-*)")
    p.add_argument("--session", help="tmux session name (default: unique autosd-full-*)")
    p.add_argument("--no-attach", action="store_true", help="start the canonical tmux UI without attaching")
    p.add_argument("--ssh-port", type=int, default=2244)
    p.add_argument("--monitor", action="store_true", help="enable loopback QBox monitor")
    p.add_argument("--monitor-port", type=int, help="monitor TCP port (implies --monitor)")
    p.add_argument("--runtime-injection", action="store_true", help="opt in to full-system runtime injection")
    p.add_argument("--qmp", action="store_true", help="opt in to per-domain QMP biflows (implies monitor)")
    p.add_argument("--timeout", type=float, default=7200)
    p.add_argument("--headless", action="store_true", help="foreground file-backed runtime without tmux (dashboard mode)")
    p.add_argument("--diagnostic-boot", action="store_true",
                   help="retain manifest SLUB debug and forced expedited RCU (slower diagnostic baseline)")
    p.add_argument("--observe-native-reboot", action="store_true",
                   help="compatibility option: native reboot supervision is now always enabled")
    p.add_argument("--reset-trace", action="store_true",
                   help="opt in to Apollo reset-controller trace (also QBOX_APOLLO_RESET_TRACE=1)")
    p.add_argument("--dry-run", action="store_true", help="inspect inputs without creating output files")
    return p


def default_rootfs(build, manifest_path):
    """Reuse only matching private runs with successful full boot and poweroff.

    Active/failed runs have no successful poweroff receipt and are excluded.
    Never infer safety from disk mtime or the directory's timestamp alone.
    """
    candidates = []
    paths = list((build / "autosd/dashboard").glob("*/*/vm/launch.json"))
    paths += list((build / "qbox-apollo-qvp").glob("*/launch.json"))
    for path in paths:
        try:
            launch = json.loads(path.read_text())
            receipt = path.parent / "result.json"
            result = json.loads(receipt.read_text())
            modules = json.loads((path.parent / "modules.json").read_text())
            disk = path.parent / "rootfs.wic"
            if (launch.get("backend") == "qbox-full"
                    and Path(launch.get("autosd", "")).resolve() == manifest_path.resolve()
                    and result.get("status") == "POWERED_OFF"
                    and result.get("passed") is True
                    and result.get("poweroff_observed") is True
                    and result.get("domains", {}).get("status") == "PASS"
                    and modules.get("status") == "PASS"
                    and not modules.get("prepare_only", False)
                    and disk.is_file() and not disk.is_symlink()):
                candidates.append((receipt.stat().st_mtime_ns, str(disk), disk))
        except (OSError, ValueError, TypeError, AttributeError):
            continue
    return max(candidates)[2] if candidates else None


def make_plan(args):
    if not 1024 <= args.ssh_port <= 65535:
        raise ValueError("--ssh-port must be 1024..65535")
    if args.timeout <= 0:
        raise ValueError("--timeout must be positive")
    build = args.build_dir.absolute()
    manifest_path = args.autosd or build / "autosd/demo-minimal-qm-prepared/regular.json"
    if not manifest_path.is_file():
        raise ValueError(f"AutoSD manifest not found: {manifest_path}; prepare the image or use --autosd PATH")
    manifest = autosd_manifest(manifest_path)
    deploy = (args.deploy_dir or build / "tmp_baremetal/deploy/images/apollo-qvp").absolute()
    stamp = time.strftime("%Y%m%d-%H%M%S") + f"-{os.getpid()}"
    out = (args.out_dir or build / "qbox-apollo-qvp" / f"autosd-full-{stamp}").absolute()
    session = args.session or f"autosd-full-{stamp}"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", session):
        raise ValueError("--session must use letters, digits, underscores or hyphens")
    if args.headless and args.no_attach:
        raise ValueError("--no-attach is a tmux option; omit it with --headless")
    selected = args.rootfs
    selection = "explicit --rootfs" if selected else "manifest rootfs"
    if selected is None and args.autosd is None:
        selected = default_rootfs(build, manifest_path)
        if selected is not None:
            selection = "latest matching full-system PASS and normal poweroff"
    source = required(selected or Path(manifest["rootfs"]), "AutoSD rootfs")
    if out.exists() and any(out.iterdir()):
        raise ValueError("--out-dir must be empty; never overwrite a previous run")
    initrd = required(Path(manifest["initrd"]), "AutoSD initrd")
    uki = required(args.uki or deploy / "nexios-bsp-initramfs-a.efi", "Yocto UKI")
    bootargs = manifest["bootargs"]
    if not args.diagnostic_boot:
        # AutoSD's diagnostic defaults disable SLUB fast paths and force
        # expensive RCU IPIs even after RT boot. Use the kernel's normal RT
        # defaults; preserve an explicit reproducible diagnostic mode.
        diagnostic = {"slub_debug=FPZ", "rcupdate.rcu_expedited=1",
                      "rcupdate.rcu_normal_after_boot=0"}
        bootargs = " ".join(word for word in bootargs.split() if word not in diagnostic)
    # Gate guest services which require the real Safety Island firmware.
    bootargs += " apollo.fullsystem=1"
    if any(word.startswith("androidboot.slot_suffix=") for word in bootargs.split()):
        raise ValueError("UKIBoot must select the slot, not bootargs")
    if not any(word.startswith("efi=") for word in bootargs.split()):
        bootargs += " efi=runtime"
    if not any(word.startswith("systemd.default_device_timeout_sec=") for word in bootargs.split()):
        bootargs += " systemd.default_device_timeout_sec=180s"
    loader_files = {key: str(required(deploy / name, "UKIBoot artifact"))
                    for key, name in (("loader", "ukibootaa64.efi"),
                                      ("addon_a", "slot_a.addon.efi"),
                                      ("addon_b", "slot_b.addon.efi"))}
    command = [str(ROOT / "run_qbox_yocto.sh"), "--bsp", "--multi-session",
               "--no-persistent-rse-state", "--no-copy-disks", "--keep-running-after-pass",
               "--build-dir", str(build), "--deploy-dir", str(deploy),
               "--rootfs", str(out / "rootfs.wic"),
               "--efi-capsule-disk", str(out / "efi-capsule.img"),
               "--out-dir", str(out / "full-system"), "--timeout", str(int(args.timeout)),
               *(["--headless"] if args.headless else ["--session", session, "--no-attach"]),
               "--", "--foreground-runtime"]
    monitor = monitor_plan(args.monitor or args.runtime_injection or args.qmp, args.monitor_port, out, full=True)
    if monitor["enabled"]:
        command[1:1] = ["--monitor", "--monitor-port", str(monitor["port"])]
    monitor_env = monitor_environment(monitor)
    monitor_env["QBOX_APOLLO_RUNTIME_INJECTION"] = "true" if args.runtime_injection else "false"
    return {"backend": "qbox-full", "boot_method": "full-system-ukiboot-efi",
            "schema_version": 1, "run_id": out.name, "monitor": monitor, "qmp_enabled": args.qmp,
            "autosd": str(manifest_path.absolute()), "mode": manifest["mode"],
            "input_selection": selection,
            "boot_profile": "diagnostic" if args.diagnostic_boot else "normal-rt",
            "observe_native_reboot": args.observe_native_reboot,
            "source_rootfs": str(source), "rootfs": str(out / "rootfs.wic"),
            "initrd": str(initrd), "uki_source": str(uki), "uki": str(out / "autosd.efi"),
            "uki_source_metadata": inspect_uki(uki), "source_disk": inspect_disk(source),
            "loader_files": loader_files, "bootargs": bootargs,
            "efi_source": str(required(deploy / "efi-capsule-update-disk-image-apollo-qvp.img", "EFI capsule disk")),
            "command": command, "out_dir": str(out), "timeout": args.timeout,
            "headless": args.headless, "session": session, "no_attach": args.no_attach,
            "build_dir": str(build), "ssh_port": args.ssh_port,
            "environment": {**monitor_env, "QBOX_APOLLO_NETDEV": f"type=user,hostfwd=tcp:127.0.0.1:{args.ssh_port}-:22",
                            "SSH_PORT": str(args.ssh_port), "PRIMARY_LOGIN_PROMPT": "login:",
                            "PRIMARY_SHELL_MARKER": "[root@", "QBOX_APOLLO_NUM_CPUS": "4",
                            "QBOX_APOLLO_RESET_TRACE": "1" if args.reset_trace else os.environ.get("QBOX_APOLLO_RESET_TRACE", "0")},
            "scope": "real RSE, SI CL0, SI CL1 and AP firmware boot; no AP-direct payload or mock domains"}


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


BOOT_STARTS = {
    "rse": r"Starting TF-M BL1_1",
    "si-cl0": r"(?:^|\n)\[[^\]\n]+\]  ___  ___ ___      __ _",
    "si-cl1": r"Out of Reset \(OoR\) completed on CPU: 0",
    "ap": r"(?:^|\n)U-Boot(?: |\r?\n|$)",
}


def boot_tail(text, pattern):
    starts = list(re.finditer(pattern, text))
    return (text[starts[-1].start():], len(starts)) if starts else (text, 0)


def domain_status(out):
    domains = []
    for domain, (_, filename) in LOGS.items():
        path = out / "full-system" / filename
        text = path.read_text(errors="replace") if path.exists() else ""
        pattern = BOOT_STARTS[domain]
        text, epoch = boot_tail(text, pattern)
        if domain == "si-cl0" and not epoch and "GIC-multiview configured successfully" in text:
            epoch = 1  # Legacy truncated logs have no initial ASCII banner.
        secure_epoch = None
        if domain == "ap":
            secure_path = out / "full-system/qbox-secure-console.log"
            secure = secure_path.read_text(errors="replace") if secure_path.exists() else ""
            secure, secure_epoch = boot_tail(secure, r"(?:^|\n)NOTICE:  BL2:(?: v[0-9]|\r?\n|$)")
            # BL2 precedes U-Boot. Never combine the new secure boot with
            # the previous Linux login (or vice versa).
            if secure_epoch > epoch:
                text = ""
            elif epoch > secure_epoch:
                secure = ""
            epoch = max(epoch, secure_epoch)
            # The outgoing kernel can request reset before any new firmware
            # prints. Immediately withdraw its old readiness in that interval.
            requests = list(re.finditer(r"(?:^|\n)(?:\[[^\]\r\n]+\]\s*)?reboot: Restarting system\r?\n", text))
            if requests:
                text = text[requests[-1].end():]
        hits = {marker: marker in text for marker in MARKERS[domain]}
        if domain == "ap":
            hits.update({marker: marker in secure for marker in
                         ("NOTICE:  BL2:", "NOTICE:  BL31:", "OP-TEE version:")})
        errors = {marker: True for marker in FAIL_MARKERS[domain] if marker in text}
        if domain == "ap":
            errors.update({marker: True for marker in ("PANIC", "ASSERT:",
                "[RSE-COMMS] Host to RSE MHU driver initialization failed") if marker in secure})
        failed = bool(errors)
        status = "FAIL" if failed else "PASS" if all(hits.values()) else "WAITING"
        domains.append({"id": domain, "status": status, "markers": hits, "errors": errors,
                        "boot_epoch": epoch, **({"secure_boot_epoch": secure_epoch} if domain == "ap" else {})})
    status = "FAIL" if any(d["status"] == "FAIL" for d in domains) else (
        "PASS" if all(d["status"] == "PASS" for d in domains) else "WAITING")
    return {"status": status, "domains": domains,
            "qualification": "firmware boot markers; not comprehensive hardware qualification"}


class EpochProvisioner:
    """One bounded worker at a time; obsolete boot results never become ready."""
    def __init__(self, plan, out):
        self.plan, self.out = plan, out
        self.epoch = None
        self.thread = None
        self.result = {"status": "WAITING"}
        self.completed = None
        self.started = False

    def update(self, epoch, login):
        if epoch != self.epoch:
            self.epoch, self.started = epoch, False
            self.result = {"status": "WAITING", "boot_epoch": epoch}
            write_json(self.out / "modules.json", self.result)
        if self.thread is not None and not self.thread.is_alive():
            old_epoch, result, directory = self.completed
            self.thread = None
            if old_epoch == epoch:
                self.result = dict(result, boot_epoch=epoch)
                if self.result.get("status") != "PASS":
                    self.result["status"] = "FAIL"
                write_json(self.out / "modules.json", self.result)
        if login and not self.started and self.thread is None and "ssh_port" in self.plan:
            self.started = True
            self.result = {"status": "RUNNING", "boot_epoch": epoch}
            directory = self.out / "provision" / f"boot-{epoch}"
            directory.mkdir(parents=True, exist_ok=True)
            logfile = self.out / "modules.log"
            if logfile.exists() or logfile.is_symlink():
                logfile.unlink()
            logfile.symlink_to(directory / "modules.log")
            def work():
                try:
                    from autosd_fullsystem_modules import provision
                    result = provision(self.plan["ssh_port"], Path(self.plan["build_dir"]), directory)
                except Exception as error:
                    result = {"status": "FAIL", "error": str(error)}
                self.completed = (epoch, result, directory)
            self.thread = threading.Thread(target=work, daemon=True)
            self.thread.start()
            write_json(self.out / "modules.json", self.result)
        return dict(self.result)


def stop_owned(proc):
    if proc.poll() is None:
        # Full runner forwards SIGTERM as SIGINT to its owned runtime;
        # that runtime's finally closes its separately-sessioned QBox child.
        proc.terminate()
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired as error:
            raise RuntimeError("owned full-system runtime did not stop within 30s") from error


class TmuxRuntime:
    """Validated canonical runtime handle, never a wildcard process search.

    Linux pidfds preserve ownership even if a PID is recycled after validation.
    The canonical tmux supervisor reaps this process; we only observe it.
    """
    def __init__(self, out):
        runtime = out / "full-system"
        deadline = time.monotonic() + 30
        pidfile = runtime / "qbox-run.pid"
        while not pidfile.exists() or not pidfile.read_text().strip():
            if (runtime / ".qbox-run.done").exists() or time.monotonic() >= deadline:
                raise RuntimeError("canonical tmux runtime did not create qbox-run.pid")
            time.sleep(.1)
        self.pid = int(pidfile.read_text().strip())
        self.fd = os.pidfd_open(self.pid)
        try:
            proc = Path(f"/proc/{self.pid}")
            if proc.stat().st_uid != os.getuid():
                raise RuntimeError("tmux runtime belongs to another user")
            expected = str(ROOT / "scripts/run/run_qbox_apollo_fvp_full.py").encode()
            identity_deadline = time.monotonic() + 5
            while True:
                env = dict(item.split(b"=", 1) for item in (proc / "environ").read_bytes().split(b"\0") if b"=" in item)
                argv = (proc / "cmdline").read_bytes().split(b"\0")
                if self.poll() is not None:
                    raise RuntimeError("canonical tmux runtime exited before supervision")
                if env.get(b"QBOX_SESSION_OUT_DIR") == str(runtime).encode() and expected in argv:
                    break
                # qbox-run.pid is written before stdbuf execs Python. Allow
                # only a bounded startup transition, never signal by PID.
                if time.monotonic() >= identity_deadline:
                    raise RuntimeError("qbox-run.pid does not identify this canonical full-system runtime")
                time.sleep(.05)
        except BaseException:
            self.close()
            raise

    def poll(self):
        return 1 if select.select([self.fd], [], [], 0)[0] else None

    def terminate(self):
        try:
            signal.pidfd_send_signal(self.fd, signal.SIGTERM)
        except ProcessLookupError:
            pass

    def wait(self, timeout=None):
        if not select.select([self.fd], [], [], timeout)[0]:
            raise subprocess.TimeoutExpired("canonical tmux runtime", timeout)
        return 1

    def close(self):
        os.close(self.fd)


def supervise(plan, owned_runtime=None):
    out = Path(plan["out_dir"])
    env = os.environ.copy()
    env.update(plan["environment"])
    start = time.monotonic()
    interrupted = False
    def request_stop(signum, frame):
        nonlocal interrupted
        interrupted = True
    previous = {sig: signal.signal(sig, request_stop) for sig in (signal.SIGTERM, signal.SIGINT)}
    status, code, poweroff = "FAIL", 1, False
    proc = owned_runtime
    provisioner = EpochProvisioner(plan, out)
    try:
        with (out / "qbox.log").open("w") as log:
            if proc is None:
                proc = subprocess.Popen(plan["command"], env=env, cwd=ROOT,
                                        stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            else:
                write_json(out / "supervisor.json", {"status": "RUNNING", "pid": os.getpid(),
                           "runtime_pid": proc.pid, "session": plan["session"]})
            while True:
                update_runtime(plan.get("monitor", {}), proc.pid, plan.get("run_id", out.name))
                domains = domain_status(out)
                uart = out / "linux-uart.log"
                text = uart.read_text(errors="replace") if uart.exists() else ""
                ap = next(d for d in domains["domains"] if d["id"] == "ap")
                provisioning = provisioner.update(ap["boot_epoch"], ap["markers"]["login:"])
                domains["provision"] = dict(provisioning)
                if provisioning["status"] == "FAIL":
                    domains["status"] = "FAIL"
                elif domains["status"] == "PASS" and provisioning["status"] != "PASS":
                    domains["status"] = "WAITING"
                write_json(out / "domains.json", domains)
                current_text, _ = boot_tail(text, BOOT_STARTS["ap"])
                if re.search(r"(?:^|\n)(?:\[[^\]\r\n]+\]\s*)?reboot: Power down\r?\n", current_text):
                    status, code, poweroff = "POWERED_OFF", 0, True
                    break
                if re.search(r"(?:^|\n)(?:\[[^\]\r\n]+\]\s*)?reboot: Restarting system\r?\n", text):
                    # A request is evidence of intent, not a successful reset.
                    # Keep the same owned QBox process under supervision.
                    restarts = list(re.finditer(r"reboot: Restarting system\r?\n", text))
                    write_json(out / "native-reboot-observation.json", {
                        "status": "REQUEST_OBSERVED", "requests": len(restarts),
                        "login_after_request": "login:" in text[restarts[-1].end():],
                        "qualification": "request log only; verify new boot ID and domain reset separately"})
                if interrupted:
                    status, code = "INTERRUPTED", 130
                    break
                if time.monotonic() - start >= plan["timeout"]:
                    status, code = "TIMEOUT", 124
                    break
                if proc.poll() is not None:
                    # A boot-marker PASS is not successful VM shutdown.
                    status = "UNEXPECTED_EXIT"
                    break
                time.sleep(0.5)
    finally:
        try:
            if proc is not None:
                stop_owned(proc)
        except RuntimeError:
            status, code = "CLEANUP_FAILED", 1
            raise
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
            write_json(out / "result.json", {"backend": "qbox-full", "status": status,
                       "returncode": code, "passed": code == 0, "poweroff_observed": poweroff,
                       "elapsed_s": time.monotonic() - start, "domains": domain_status(out)})
    return code


def supervise_tmux(plan_path):
    plan = json.loads(plan_path.read_text())
    out = Path(plan["out_dir"])
    try:
        runtime = TmuxRuntime(out)
        try:
            return supervise(plan, runtime)
        finally:
            runtime.close()
    except (OSError, ValueError, RuntimeError) as error:
        write_json(out / "supervisor.json", {"status": "FAIL", "error": str(error)})
        raise


def runtime_preflight(plan, proc_root=Path("/proc")):
    """Full-system SRAM shared memory is not multi-instance qualified."""
    for proc in proc_root.iterdir():
        if not proc.name.isdigit():
            continue
        try:
            if proc.stat().st_uid != os.getuid():
                continue
            argv = (proc / "cmdline").read_bytes().split(b"\0")
            full_runner = any(arg.endswith(b"/run_qbox_apollo_fvp_full.py") for arg in argv)
            full_platform = any(arg.endswith((b"/apollo-qvp.lua", b"/apollo-qvp-saturn-v.lua")) for arg in argv)
            if not (full_runner or full_platform):
                continue
            env = (proc / "environ").read_bytes().split(b"\0")
            if any(item.startswith(b"QBOX_SESSION_OUT_DIR=") for item in env):
                raise ValueError(f"Full-system QBox PID {proc.name} is already running; Power off it first (shared SRAM is not multi-instance qualified)")
        except FileNotFoundError:
            continue  # process exited during this read-only snapshot
    if plan.get("headless"):
        return  # dashboard needs the same exclusion, but never requires tmux
    tmux = os.environ.get("TMUX_BIN", "tmux")
    if subprocess.run([tmux, "has-session", "-t", "=" + plan["session"]],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        raise ValueError(f"tmux session already exists: {plan['session']}")


def cleanup_created_tmux(plan):
    """Use canonical F12 cleanup only after exact session ownership checks."""
    tmux = os.environ.get("TMUX_BIN", "tmux")
    runtime = str(Path(plan["out_dir"]) / "full-system")
    for key, expected in (("@qbox-managed", "1"), ("@qbox-owner-uid", str(os.getuid())),
                          ("@qbox-out-dir", runtime)):
        result = subprocess.run([tmux, "show-options", "-v", "-t", "=" + plan["session"], key],
                                capture_output=True, text=True)
        if result.returncode or result.stdout.strip() != expected:
            return  # never clean a foreign or pre-existing session
    env = os.environ.copy()
    env.update(OUT_DIR=runtime, TMUX_BIN=tmux)
    subprocess.run([str(ROOT / "scripts/run/run_qbox_apollo_fvp_full_tmux.sh"),
                    "--stop-session", plan["session"]], env=env, check=True, timeout=30)


def start_tmux(plan):
    out = Path(plan["out_dir"])
    env = os.environ.copy()
    env.update(plan["environment"])
    # The real canonical UI supplies UART FIFO input, layout, F12 lifecycle,
    # secure console and platform/shell panes. Do not duplicate those panes.
    observer = None
    try:
        subprocess.run(plan["command"], cwd=ROOT, env=env, check=True)
        with (out / "autosd-supervisor.log").open("w") as log:
            observer = subprocess.Popen([sys.executable, str(Path(__file__).resolve()),
                                         "--supervise-tmux", str(out / "launch.json")],
                                        cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log,
                                        stderr=subprocess.STDOUT, start_new_session=True)
        deadline = time.monotonic() + 35
        while not (out / "supervisor.json").exists():
            if observer.poll() is not None or time.monotonic() >= deadline:
                raise RuntimeError(f"AutoSD tmux supervisor failed; see {out / 'autosd-supervisor.log'}")
            time.sleep(.1)
        receipt = json.loads((out / "supervisor.json").read_text())
        if receipt["status"] != "RUNNING":
            raise RuntimeError(f"AutoSD tmux supervisor failed: {receipt}")
    except BaseException:
        cleanup_created_tmux(plan)
        if observer is not None and observer.poll() is None:
            observer.terminate()
            observer.wait(timeout=35)
        raise
    print(f"AutoSD supervisor: {observer.pid}; logs: {out}", flush=True)
    if not plan["no_attach"]:
        tmux = os.environ.get("TMUX_BIN", "tmux")
        action = "switch-client" if os.environ.get("TMUX") else "attach-session"
        print(f"Detach leaves the VM running; reattach: {tmux} attach-session -t {plan['session']}", flush=True)
        return subprocess.call([tmux, action, "-t", plan["session"]])
    return 0


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--supervise-tmux":
        return supervise_tmux(Path(sys.argv[2]))
    args = parser().parse_args()
    plan = make_plan(args)
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return 0
    print(f"AutoSD manifest: {plan['autosd']}\nAutoSD source disk: {plan['source_rootfs']}"
          f"\nSelection: {plan['input_selection']}\nOutput: {plan['out_dir']}", flush=True)
    if not args.headless:
        if not shutil.which(os.environ.get("TMUX_BIN", "tmux")):
            raise ValueError("tmux is required; use --headless for the dashboard")
        if not hasattr(os, "pidfd_open") or not hasattr(signal, "pidfd_send_signal"):
            raise ValueError("tmux supervision requires Linux pidfd support")
    runtime_preflight(plan)
    monitor_preflight(plan["monitor"])
    prepare_qmp(plan)
    out = Path(plan["out_dir"])
    out.mkdir(parents=True, exist_ok=True)
    for source, destination in ((plan["source_rootfs"], out / "rootfs.wic"),
                                (plan["efi_source"], out / "efi-capsule.img")):
        subprocess.run(["cp", "--reflink=auto", "--sparse=always", source, str(destination)], check=True)
    plan["prepared_uki"] = prepare_uki(Path(plan["uki_source"]), Path(plan["initrd"]),
                                      plan["bootargs"], Path(plan["uki"]))
    plan["prepared_disk"] = prepare_disk(out / "rootfs.wic", Path(plan["uki"]),
                                         **{key: Path(value) for key, value in plan["loader_files"].items()})
    plan["esp_check"] = check_private_esp(out / "rootfs.wic")
    for alias, target in LOGS.values():
        (out / alias).symlink_to(Path("full-system") / target)
    write_json(out / "launch.json", plan)
    return supervise(plan) if args.headless else start_tmux(plan)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"run_qbox_autosd: {error}", file=sys.stderr)
        sys.exit(1)
