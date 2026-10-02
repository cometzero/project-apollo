#!/usr/bin/env python3
"""Build official minimal_qm in a private guest, prepare it and verify QBox.

Requires an existing Apollo BSP/provider build and prepared nightly developer
manifest. No host package installation, foreign VM shutdown or image overwrite.
This verifies minimal QM, not the separate Automotive customization scenarios.
"""
import argparse
import hashlib
import json
import logging
import os
from pathlib import Path
import shlex
import shutil
import socket
import subprocess
import sys
import tarfile
import time
import re
import uuid
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def module_release(archive):
    with tarfile.open(archive, "r:gz") as source:
        releases = {member.name.split("/")[2] for member in source
                    if member.name.startswith("lib/modules/") and len(member.name.split("/")) > 3
                    and member.name.split("/")[2]}
    if len(releases) != 1:
        raise ValueError("Expected exactly one kernel release in modules archive")
    return releases.pop()


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, help="default: BUILD_DIR/autosd/regular.json")
    p.add_argument("--aib-manifest", type=Path, default=ROOT / "autosd/sig-docs/demos/minimal_qm/minimal_qm.aib.yml")
    p.add_argument("--image", type=Path, help="existing AIB qcow2; skip builder")
    p.add_argument("--builder-image", help="override builder container with an immutable image@sha256:digest")
    p.add_argument("--builder-archive", type=Path,
                   help="saved Podman OCI archive; requires --builder-image and disables registry fallback")
    p.add_argument("--customize", action="store_true", help="install Automotive services and RT tools; verify readiness after minimal QM")
    p.add_argument("--crun-binary", type=Path, help="required with --customize: previously built patched ARM64 crun")
    p.add_argument("--cc", default="aarch64-linux-gnu-gcc", help="customization static workload compiler")
    p.add_argument("--build-dir", type=Path, default=ROOT / "build")
    p.add_argument("--deploy-dir", type=Path)
    p.add_argument("--kernel", type=Path)
    p.add_argument("--uki", type=Path)
    p.add_argument("--modules", type=Path)
    p.add_argument("--qemu", type=Path)
    p.add_argument("--guestfish", default="guestfish")
    p.add_argument("--qemu-img", default="qemu-img")
    p.add_argument("--qbox-out-dir", type=Path, help="new full-system output directory; default is discoverable by run_qbox_autosd.sh")
    p.add_argument("--output", type=Path, help="default: BUILD_DIR/autosd/demo-minimal-qm-prepared")
    p.add_argument("--work-dir", type=Path, help="default: new timestamped directory under BUILD_DIR/autosd")
    p.add_argument("--builder-port", type=int, default=2226)
    p.add_argument("--qemu-port", type=int, default=2224)
    p.add_argument("--qbox-port", type=int, default=2244)
    p.add_argument("--boot-timeout", type=int, default=1800)
    p.add_argument("--build-timeout", type=int, default=7200)
    p.add_argument("--dry-run", action="store_true", help="print all stages without creating files or starting guests")
    return p


def resolve(args):
    for key in ("manifest", "aib_manifest", "image", "build_dir", "deploy_dir", "kernel", "uki", "modules", "qemu", "output", "work_dir", "qbox_out_dir", "crun_binary", "builder_archive"):
        value = getattr(args, key)
        if value is not None:
            setattr(args, key, value.absolute())
    args.manifest = args.manifest or args.build_dir / "autosd/regular.json"
    args.output = args.output or args.build_dir / "autosd/demo-minimal-qm-prepared"
    args.work_dir = args.work_dir or args.build_dir / "autosd" / ("minimal-qm-build-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ"))
    args.deploy_dir = args.deploy_dir or args.build_dir / "tmp_baremetal/deploy/images/apollo-qvp"
    args.kernel = args.kernel or args.deploy_dir / "Image"
    args.uki = args.uki or args.deploy_dir / "nexios-bsp-initramfs-a.efi"
    args.modules = args.modules or args.deploy_dir / "modules-apollo-qvp.tgz"
    args.qbox_out_dir = args.qbox_out_dir or args.build_dir / "qbox-apollo-qvp" / ("autosd-" + args.work_dir.name)
    local = args.build_dir / "autosd/host-tools/root/usr/bin/guestfish"
    if args.guestfish == "guestfish" and not shutil.which(args.guestfish) and local.is_file():
        args.guestfish = str(local)
    if min(args.boot_timeout, args.build_timeout) <= 0:
        raise ValueError("timeouts must be positive")
    if args.customize and args.crun_binary is None:
        raise ValueError("--customize requires explicit --crun-binary")
    if args.image and (args.builder_image or args.builder_archive):
        raise ValueError("--image cannot be combined with --builder-image or --builder-archive")
    if args.builder_archive and not args.builder_image:
        raise ValueError("--builder-archive requires an explicit --builder-image digest")
    if args.builder_image:
        import re
        if not re.fullmatch(r"quay\.io/centos-sig-automotive/automotive-image-builder@sha256:[0-9a-f]{64}", args.builder_image):
            raise ValueError("--builder-image must be an official AIB image pinned to a SHA256 digest")
    ports = [args.builder_port, args.qemu_port, args.qbox_port]
    if len(set(ports)) != len(ports) or any(not 1024 <= port <= 65535 for port in ports):
        raise ValueError("SSH ports must be distinct unprivileged TCP ports")
    return args


def plan(args):
    py = sys.executable
    work = args.work_dir
    image = args.image or work / "fetch/minimal_qm.aarch64.qcow2"
    prepared = args.output / "regular.json"
    commands = {}
    if not args.image:
        commands["builder"] = [py, str(ROOT / "scripts/autosd_demo/builder_launch.py"),
            "--manifest", str(args.manifest), "--kernel", str(args.kernel),
            "--work-dir", str(work / "builder"), "--ssh-port", str(args.builder_port),
            "--build-dir", str(args.build_dir), "--deploy-dir", str(args.deploy_dir)]
        if args.qemu:
            commands["builder"] += ["--qemu", str(args.qemu)]
    commands["prepare"] = [py, str(ROOT / "scripts/prepare_autosd.py"), "--image", str(image),
        "--mode", "regular", "--output", str(args.output), "--guestfish", args.guestfish,
        "--qemu-img", args.qemu_img]
    commands["qemu"] = [str(ROOT / "run_qemu_linux.sh"), "--autosd", str(prepared),
        "--uki", str(args.uki), "--build-dir", str(args.build_dir), "--deploy-dir", str(args.deploy_dir),
        "--headless", "--out-dir", str(work / "qemu"), "--netdev",
        f"user,id=net0,hostfwd=tcp:127.0.0.1:{args.qemu_port}-:22"]
    if args.qemu:
        commands["qemu"] += ["--qemu", str(args.qemu)]
    commands["modules"] = [py, str(ROOT / "scripts/run/autosd_fullsystem_modules.py"),
        "--prepare-only", "--port", str(args.qemu_port), "--build-dir", str(args.build_dir),
        "--out", str(work / "fullsystem-modules")]
    commands["qbox"] = [str(ROOT / "run_qbox_autosd.sh"), "--autosd", str(prepared),
        "--rootfs", str(work / "qemu/rootfs.wic"), "--uki", str(args.uki),
        "--build-dir", str(args.build_dir), "--deploy-dir", str(args.deploy_dir),
        "--headless", "--out-dir", str(args.qbox_out_dir), "--ssh-port", str(args.qbox_port),
        "--timeout", str(2 * args.boot_timeout + 2400)]
    if args.customize:
        commands["customization-bundle"] = [py, str(ROOT / "autosd/customization/prepare.py"),
            "--out", str(work / "customization-bundle"), "--crun-binary", str(args.crun_binary), "--cc", args.cc,
            "--rt-tools"]
    return {"commands": commands, "image": str(image), "prepared": str(prepared),
        "builder_image": args.builder_image or "required: bootstrap resolves official ARM64 image",
        "builder_archive": str(args.builder_archive) if args.builder_archive else None,
        "builder_archive_policy": "SHA256 verified transfer; load and require requested digest; no registry fallback" if args.builder_archive else None,
        "customize": args.customize,
        "rt_tools": args.customize,
        "stages": ["preflight", "builder boot + matching modules + AIB build + SHA-verified fetch" if not args.image else "validate supplied qcow2",
            "graceful builder shutdown", "prepare image", "QEMU UKI boot", "UART root login + SSH/iproute bootstrap",
            "matching modules + full-system assets",
            "minimal QM guest verification",
            *(["Automotive + RT bundle and root/QM packages", "QEMU RT readiness"] if args.customize else []),
            "graceful QEMU shutdown", "QBox full boot + all domains/modules",
            *(["QBox Automotive + RT readiness"] if args.customize else []),
            "minimal QM guest and UKIBoot verification", "graceful QBox shutdown"],
        "limitations": ("Automotive and RT tools installation/readiness only; scenario suites not executed." if args.customize
                        else "Minimal QM only; Automotive customization excluded.")
                        + " ASIL certification, OTA, IPC and timing qualification excluded."}


def preflight(args):
    for path in (args.work_dir, args.output, args.qbox_out_dir):
        if path.exists():
            raise ValueError(f"Refusing to overwrite existing directory: {path}")
    if not args.image and not args.builder_image:
        raise ValueError("Use build_autosd_minimal_qm.sh to prepare inputs, or supply --builder-image")
    required = [args.kernel, args.uki, args.modules,
                args.aib_manifest]
    required += [args.deploy_dir / name for name in (
        "ukibootaa64.efi", "slot_a.addon.efi", "slot_b.addon.efi",
        "u-boot-apollo-qemu.bin", "efi-capsule-update-disk-image-apollo-qvp.img",
        "nexios-bsp-initramfs-apollo-qvp.qboxconf")]
    required.append(args.image if args.image else args.manifest)
    if args.builder_archive:
        required.append(args.builder_archive)
    if args.customize:
        required.append(args.crun_binary)
        if not shutil.which(args.cc):
            raise ValueError(f"Missing customization compiler: {args.cc}")
        import yaml  # noqa: F401
        import jsonschema  # noqa: F401
    if args.qemu:
        required.append(args.qemu)
    else:
        required.append(args.build_dir / "tmp_baremetal/deploy/qemu-apollo-native/qemu-apollo-native.json")
    for path in required:
        if not path.is_file():
            raise ValueError(f"Missing prerequisite: {path}; build the Apollo BSP/provider first")
    for binary in (args.guestfish, args.qemu_img, "cp", "modinfo", "fsck.fat", "mcopy", "mdir"):
        if not shutil.which(binary):
            raise ValueError(f"Missing host tool: {binary}; no packages will be installed automatically")
    import paramiko  # noqa: F401; fail before creating images
    sys.path.insert(0, str(ROOT / "scripts/run"))
    from autosd_fullsystem_modules import module_inputs
    from autosd_fullsystem_pfdi import pfdi_inputs
    modules = module_inputs(args.build_dir)
    if any(entry["release"] != module_release(args.modules) for entry in modules.values()):
        raise ValueError("Module archive and full-system module releases disagree")
    pfdi_inputs(args.build_dir)
    ancestor = args.work_dir.parent
    while not ancestor.exists():
        ancestor = ancestor.parent
    if shutil.disk_usage(ancestor).free < 32 * 1024**3:
        raise ValueError("At least 32 GiB free disk space is required")
    ports = (args.qemu_port, args.qbox_port) if args.image else (args.builder_port, args.qemu_port, args.qbox_port)
    for port in ports:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", port))
    # Full-system processes share host resources even when SSH ports differ.
    for cmdline in Path("/proc").glob("[0-9]*/cmdline"):
        try:
            data = cmdline.read_bytes()
        except (OSError, PermissionError):
            continue
        if any(name in data for name in (b"apollo-qvp.lua", b"apollo-qvp-saturn-v.lua")) and (b"qbox" in data or b"gs-vp" in data):
            raise ValueError(f"Existing QBox full-system process {cmdline.parent.name}; shut it down explicitly first")


class Pipeline:
    def __init__(self, args):
        self.args = args
        self.plan = plan(args)
        self.results = []
        self.processes = []
        self.logs = []
        self.environment = dict(os.environ)
        self.environment.setdefault("LIBGUESTFS_BACKEND", "direct")
        boot = args.build_dir / "autosd/host-tools/root/boot"
        kernels = [p for p in boot.glob("vmlinuz-*") if (Path("/lib/modules") / p.name.removeprefix("vmlinuz-")).is_dir()]
        if len(kernels) == 1:
            self.environment.setdefault("SUPERMIN_KERNEL", str(kernels[0]))
            self.environment.setdefault("SUPERMIN_MODULES", str(Path("/lib/modules") / kernels[0].name.removeprefix("vmlinuz-")))

    def command(self, name, command, timeout):
        print(f"[{name}] {shlex.join(map(str, command))}", flush=True)
        with (self.args.work_dir / f"{name}.log").open("w") as log:
            result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                    timeout=timeout, env=self.environment)
        self.results.append({"stage": name, "returncode": result.returncode})
        if result.returncode:
            raise RuntimeError(f"{name} failed; see {self.args.work_dir / (name + '.log')}")

    def start(self, name):
        command = self.plan["commands"][name]
        log = (self.args.work_dir / f"{name}-launcher.log").open("w")
        self.logs.append(log)
        process = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL, start_new_session=True, env=self.environment)
        self.processes.append((name, process))
        (self.args.work_dir / f"{name}-launcher.pid").write_text(str(process.pid) + "\n")
        return process

    def guest(self, name, port, command, *, uploads=(), downloads=(), timeout=600):
        cmd = [sys.executable, str(ROOT / "scripts/autosd_demo/guest_exec.py"),
            "--port", str(port), "--command", command, "--out", str(self.args.work_dir / name),
            "--timeout", str(timeout), "--connect-timeout", "60"]
        for local, remote in uploads:
            cmd += ["--upload", f"{local}:{remote}"]
        for remote, local in downloads:
            cmd += ["--download", f"{remote}:{local}"]
        self.command(name, cmd, timeout + 30)

    def wait_ssh(self, process, port):
        import paramiko
        # Expected connection retries should not flood stderr with transport
        # thread tracebacks. Actual failure still has the bounded stage error.
        logging.getLogger("autosd.pipeline.ssh").setLevel(logging.CRITICAL)
        deadline = time.monotonic() + self.args.boot_timeout
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"VM launcher exited before SSH: {process.returncode}")
            client = paramiko.SSHClient()
            client.set_log_channel("autosd.pipeline.ssh")
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect("127.0.0.1", port=port, username="root", password="password",
                               look_for_keys=False, allow_agent=False, timeout=10,
                               auth_timeout=10, banner_timeout=10)
                return
            except (OSError, paramiko.SSHException):
                time.sleep(3)
            finally:
                client.close()
        raise TimeoutError(f"SSH not ready on {port}")

    def bootstrap_qemu_ssh(self, process):
        """Bootstrap official minimal_qm through the launcher's owned UART.

        That image intentionally has no SSH server. Wait for auto-login, then
        require a standalone output marker, never the echoed command text.
        """
        uart = self.args.work_dir / "qemu/linux-uart.log"
        uart_in = self.args.work_dir / "qemu/linux-uart.in"
        stage = "qemu-ssh-bootstrap"
        token = uuid.uuid4().hex
        prefix = "APOLLO_SSH_BOOTSTRAP_" + token
        success, failure = prefix + "_PASS", prefix + "_FAIL"
        command = (
            "if timeout 900 bash -ec 'dnf -y install openssh-server iproute tar gzip kmod; "
            "mkdir -p /etc/ssh/sshd_config.d; "
            'printf "PermitRootLogin yes\\nPasswordAuthentication yes\\n" '
            "> /etc/ssh/sshd_config.d/00-apollo-demo.conf; "
            "chmod 600 /etc/ssh/sshd_config.d/00-apollo-demo.conf; "
            "restorecon /etc/ssh/sshd_config.d/00-apollo-demo.conf; "
            "systemctl enable sshd; systemctl restart sshd; systemctl is-active --quiet sshd'; "
            f"then printf '\\n{prefix}_%s\\n' PASS; "
            f"else printf '\\n{prefix}_%s\\n' FAIL; fi\n"
        )
        deadline = time.monotonic() + self.args.boot_timeout
        sent, offset, observed = False, 0, ""
        result = {"stage": stage, "status": "FAIL", "command": command.strip()}
        print(f"[{stage}] Waiting for root console; install openssh-server and iproute", flush=True)
        try:
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError("QEMU exited during SSH bootstrap")
                if uart.is_file():
                    with uart.open("rb") as stream:
                        if sent:
                            stream.seek(offset)
                        else:
                            stream.seek(max(0, uart.stat().st_size - 65536))
                        observed = stream.read().decode(errors="replace")
                    clean = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", observed).replace("\r", "")
                    if not sent and re.search(r"(?:\[root@[^\n]*\]#|root@[^\n]*#)\s*$", clean):
                        # Do not create a missing input endpoint: only the
                        # owned launcher may establish the console channel.
                        if not uart_in.is_file():
                            raise RuntimeError("QEMU UART input endpoint is missing")
                        offset = uart.stat().st_size
                        with uart_in.open("ab") as destination:
                            destination.write(command.encode())
                        sent = True
                        deadline = time.monotonic() + 1020
                    elif sent:
                        lines = {line.strip() for line in clean.splitlines()}
                        if success in lines:
                            result["status"] = "PASS"
                            self.results.append({"stage": stage, "returncode": 0})
                            return
                        if failure in lines:
                            raise RuntimeError("Guest SSH package installation/service startup failed")
                time.sleep(2)
            raise TimeoutError("QEMU root console/SSH bootstrap exceeded deadline")
        except (OSError, RuntimeError) as error:
            result["error"] = str(error)
            raise
        finally:
            (self.args.work_dir / f"{stage}.json").write_text(json.dumps(result, indent=2) + "\n")
            (self.args.work_dir / f"{stage}.log").write_text(observed)

    def install_modules(self, name, port):
        self.guest(name, port, "bash /root/install_guest_modules.sh /root/apollo-modules.tgz --load",
            uploads=[(ROOT / "scripts/autosd_demo/install_guest_modules.sh", "/root/install_guest_modules.sh"),
                     (self.args.modules, "/root/apollo-modules.tgz")], timeout=900)

    def shutdown(self, name, process, port):
        self.guest(name + "-poweroff", port,
                   "systemd-run --on-active=3s /usr/bin/systemctl poweroff", timeout=90)
        code = process.wait(timeout=300)
        if code:
            raise RuntimeError(f"{name} shutdown returned {code}")
        if name in ("builder", "qemu"):
            uart = self.args.work_dir / name / ("uart.log" if name == "builder" else "linux-uart.log")
            if "reboot: Power down" not in uart.read_text(errors="replace"):
                raise RuntimeError(f"{name} missing guest poweroff marker; disk not qualified for reuse")

    def verify_guest(self, name, port):
        self.guest(name, port,
            "set -eu; test -d /sys/firmware/efi; test \"$(uname -r)\" = "
            + shlex.quote(module_release(self.args.modules))
            + "; bash /root/qm_guest_check.sh; ukibootctl dump; "
              "booted=$(ukibootctl get-booted); active=$(ukibootctl get-active); "
              "case \"$booted\" in 0|1) ;; *) exit 1;; esac; test \"$booted\" = \"$active\"; "
              "journalctl -b -p warning --no-pager; "
              "if journalctl -b --no-pager | grep -Fi 'bootctl partition is invalid'; then exit 1; fi",
            uploads=[(ROOT / "scripts/autosd_demo/qm_guest_check.sh", "/root/qm_guest_check.sh")], timeout=900)

    def provenance(self):
        files = [self.args.kernel, self.args.uki, self.args.modules,
                 self.args.aib_manifest,
                 ROOT / "scripts/autosd_demo/builder_guest.sh"]
        repositories = [ROOT, ROOT / "autosd/sig-docs", ROOT / "autosd/automotive-image-builder",
                        ROOT / "hsoc-stack/tools/qbox", ROOT / "hsoc-stack/tools/qbox-platform"]
        if self.args.customize:
            files.append(self.args.crun_binary)
        if self.args.builder_archive:
            files.append(self.args.builder_archive)
        return {"files": {str(path): sha256(path) for path in files},
                "source_heads": {str(repo): subprocess.check_output(
                    ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
                    for repo in repositories if repo.is_dir()},
                "guestfish_environment": {key: value for key, value in self.environment.items()
                    if key in ("LIBGUESTFS_BACKEND", "SUPERMIN_KERNEL", "SUPERMIN_MODULES")}}

    def build_guest_image(self):
        args = self.args
        command = "bash /root/builder_guest.sh"
        uploads = [(ROOT / "scripts/autosd_demo/builder_guest.sh", "/root/builder_guest.sh"),
                   (args.aib_manifest, "/root/minimal_qm.aib.yml")]
        if args.builder_image:
            command += " " + shlex.quote(args.builder_image)
        if args.builder_archive:
            remote = "/root/aib-builder.oci.tar"
            uploads.append((args.builder_archive, remote))
            digest = sha256(args.builder_archive)
            # The helper mounts its scratch store, loads this archive there,
            # and requires image-exists for the exact digest before running.
            # An archive miss must not become an implicit registry pull.
            command = ("printf '%s\\n' " + shlex.quote(digest + "  " + remote)
                       + " | sha256sum -c - && " + command + " " + shlex.quote(remote))
        self.guest("aib", args.builder_port, command, uploads=uploads, timeout=args.build_timeout)

    def customize(self):
        args = self.args
        self.command("customization-bundle", self.plan["commands"]["customization-bundle"], 600)
        archive = args.work_dir / "customization-bundle.tar.gz"
        with tarfile.open(archive, "w:gz") as target:
            for path in sorted((args.work_dir / "customization-bundle").iterdir()):
                target.add(path, arcname=path.name)
        self.guest("customization-packages", args.qemu_port,
            "timeout 900 dnf -y install bluechi-controller bluechi-agent bluechi-selinux bluechi-ctl python3 podman; "
            "test $? = 0 && mkdir -p /root/bluechi-payload", timeout=1000)
        source = ROOT / "autosd/sig-docs/demos/bluechi_root_qm"
        uploads = [(path, "/root/bluechi-payload/" + path.name) for path in sorted((source / "conf").iterdir()) if path.is_file()]
        uploads += [(source / "systemd/test.service", "/root/bluechi-payload/test.service"),
                    (ROOT / "scripts/autosd_demo/qm_followup_setup.sh", "/root/qm_followup_setup.sh")]
        self.guest("customization-bluechi", args.qemu_port,
            "bash /root/qm_followup_setup.sh /root/bluechi-payload", uploads=uploads, timeout=1500)
        self.guest("customization-rt-packages", args.qemu_port,
            "bash /root/prepare-rt-guest.sh install",
            uploads=[(ROOT / "autosd/customization/rt/prepare-guest.sh", "/root/prepare-rt-guest.sh")],
            timeout=2000)
        self.guest("customization-install", args.qemu_port,
            "set -eu; mkdir /root/automotive-demo-bundle; "
            "tar -C /root/automotive-demo-bundle -xzf /root/automotive-demo-bundle.tar.gz; "
            "python3 /root/automotive-demo-bundle/install-private-guest.py",
            uploads=[(archive, "/root/automotive-demo-bundle.tar.gz")], timeout=900)
        self.verify_customization("qemu-customization", args.qemu_port)
        self.verify_rt("qemu-rt-readiness", args.qemu_port)

    def verify_rt(self, name, port):
        self.guest(name, port, "bash /root/prepare-rt-guest.sh check",
            uploads=[(ROOT / "autosd/customization/rt/prepare-guest.sh", "/root/prepare-rt-guest.sh")],
            timeout=300)

    def verify_customization(self, name, port):
        self.guest(name, port, "bash /root/wait-ready-guest.sh && bash /root/check-guest.sh",
            uploads=[(ROOT / "autosd/customization" / file, "/root/" + file)
                     for file in ("wait-ready-guest.sh", "check-guest.sh")], timeout=600)

    def run(self):
        args = self.args
        preflight(args)
        args.work_dir.mkdir(parents=True, exist_ok=False)
        (args.work_dir / "plan.json").write_text(json.dumps(self.plan, indent=2) + "\n")
        status, error = "FAIL", None
        try:
            (args.work_dir / "provenance.json").write_text(json.dumps(self.provenance(), indent=2) + "\n")
            if not args.image:
                builder = self.start("builder")
                self.wait_ssh(builder, args.builder_port)
                self.install_modules("builder-modules", args.builder_port)
                self.build_guest_image()
                self.guest("fetch", args.builder_port,
                    "sha256sum /srv/aib/work/minimal_qm.aarch64.qcow2 > /root/minimal_qm.sha256",
                    downloads=[("/srv/aib/work/minimal_qm.aarch64.qcow2", "minimal_qm.aarch64.qcow2"),
                               ("/srv/aib/work/minimal_qm.osbuild.json", "minimal_qm.osbuild.json"),
                               ("/root/minimal_qm.sha256", "minimal_qm.sha256")], timeout=1800)
                self.shutdown("builder", builder, args.builder_port)
            image = Path(self.plan["image"])
            digest = sha256(image)
            if not args.image and digest != (args.work_dir / "fetch/minimal_qm.sha256").read_text().split()[0]:
                raise RuntimeError("Builder/download SHA256 mismatch")
            (args.work_dir / "image-sha256.txt").write_text(digest + "  " + str(image) + "\n")
            self.command("image-check", [args.qemu_img, "check", "-f", "qcow2", str(image)], 300)
            self.command("prepare", self.plan["commands"]["prepare"], 1800)
            qemu = self.start("qemu")
            self.bootstrap_qemu_ssh(qemu)
            self.wait_ssh(qemu, args.qemu_port)
            self.install_modules("qemu-modules", args.qemu_port)
            self.command("modules", self.plan["commands"]["modules"], 1200)
            self.verify_guest("qemu-guest-check", args.qemu_port)
            if args.customize:
                self.customize()
            self.shutdown("qemu", qemu, args.qemu_port)
            qbox = self.start("qbox")
            self.wait_ssh(qbox, args.qbox_port)
            deadline = time.monotonic() + args.boot_timeout
            while time.monotonic() < deadline:
                modules = args.qbox_out_dir / "modules.json"
                if modules.exists():
                    state = json.loads(modules.read_text()).get("status")
                    if state == "PASS":
                        break
                    if state == "FAIL":
                        raise RuntimeError("QBox matching module provisioning failed")
                if qbox.poll() is not None:
                    raise RuntimeError("QBox exited during module provisioning")
                time.sleep(3)
            else:
                raise TimeoutError("QBox matching modules did not become ready")
            self.verify_guest("qbox-guest-check", args.qbox_port)
            if args.customize:
                self.verify_customization("qbox-customization", args.qbox_port)
                self.verify_rt("qbox-rt-readiness", args.qbox_port)
            domains = json.loads((args.qbox_out_dir / "domains.json").read_text())
            if domains.get("status") != "PASS":
                raise RuntimeError("QBox domain boot evidence is not PASS")
            self.shutdown("qbox", qbox, args.qbox_port)
            result = json.loads((args.qbox_out_dir / "result.json").read_text())
            if not (result.get("status") == "POWERED_OFF" and result.get("passed") is True
                    and result.get("poweroff_observed") and result.get("domains", {}).get("status") == "PASS"):
                raise RuntimeError("QBox all-domain/shutdown evidence failed")
            status = "PASS"
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
            error = str(exc)
            raise
        finally:
            live = [{"name": name, "pid": proc.pid} for name, proc in self.processes if proc.poll() is None]
            report = {"status": status, "error": error, "stages": self.results,
                      "live_owned_launchers": live, "limitations": self.plan["limitations"],
                      "prepared_manifest": self.plan["prepared"],
                      "verified_disk": str(args.qbox_out_dir / "rootfs.wic"),
                      "qbox_out_dir": str(args.qbox_out_dir)}
            (args.work_dir / "result.json").write_text(json.dumps(report, indent=2) + "\n")
            for log in self.logs:
                log.close()
            if live:
                print(f"VMs preserved for diagnosis; shut down explicitly: {live}", file=sys.stderr)


def main(argv=None):
    args = resolve(parser().parse_args(argv))
    if args.dry_run:
        print(json.dumps(plan(args), indent=2))
        return 0
    Pipeline(args).run()
    print(f"PASS: {args.work_dir / 'result.json'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
