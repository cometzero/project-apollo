# SPDX-License-Identifier: MIT
"""Owned, fresh-generation QBox sessions using the canonical board supervisor."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import uuid

from test_automation.utils.device import Device
from .networking import AP_SHELL, positive_timeout


class LocalQBox(Device):
    def __init__(self, platform_config, manager):
        self.config = platform_config
        self.manager = manager
        self.workspace_root = Path(platform_config["workspace_root"]).resolve()
        self.build_dir = Path(platform_config["build_dir"]).resolve()
        self.output_root = Path(platform_config["log_dir"]).resolve()
        self.image = platform_config.get("image", "bsp")
        if self.image not in ("bsp", "product"):
            raise ValueError("QBox image must be bsp or product")
        self.process = None
        self.owner = None
        self.run_dir = None
        self._generation = 0
        self._initialized = False
        self._watch_stop = threading.Event()
        self._watcher = None
        self._supervisor_log = None
        self.cleanup_result = None
        self._started = False

    def init(self):
        """Check prebuilt inputs only; never invoke BitBake or the launcher."""
        for relative in ("run_qbox_yocto.sh", "scripts/run/qbox_board_session.py",
                         "scripts/run/qbox_tc397.py"):
            if not (self.workspace_root / relative).is_file():
                raise FileNotFoundError(f"QBox launcher input missing: {relative}")
        self.deploy_dir = self.build_dir / "tmp_baremetal/deploy/images/apollo-qvp"
        basename = "nexios-bsp-initramfs" if self.image == "bsp" else "nexios-image"
        fixed = self.deploy_dir / f"{basename}-apollo-qvp.qboxconf"
        candidates = sorted(self.deploy_dir.glob(f"{basename}-apollo-qvp-*.qboxconf"))
        self.qboxconf = fixed if fixed.is_file() else candidates[-1] if candidates else fixed
        # BSP and product share the provider/firmware. Deployments may only
        # publish product metadata; pin BSP WIC separately below in that case.
        if self.image == "bsp" and not self.qboxconf.is_file():
            product = self.deploy_dir / "nexios-image-apollo-qvp.qboxconf"
            candidates = sorted(self.deploy_dir.glob("nexios-image-apollo-qvp-*.qboxconf"))
            self.qboxconf = product if product.is_file() else candidates[-1] if candidates else fixed
        if not self.qboxconf.is_file():
            raise FileNotFoundError(f"Prebuilt QBox configuration missing: {self.qboxconf}")
        data = json.loads(self.qboxconf.read_text())
        provider = data["provider"]
        executable = Path(provider["bindir"]) / data["exe"]
        platform = Path(provider["data_dir"]) / data["config"]
        if not executable.is_file() or not os.access(executable, os.X_OK):
            raise FileNotFoundError(f"Prebuilt QBox executable missing: {executable}")
        if not platform.is_file():
            raise FileNotFoundError(f"Prebuilt QBox platform missing: {platform}")
        for aliases in (("rse_rom",), ("rse_flash",), ("rse_otp",), ("ap_flash",),
                        ("ap_dtb", "dtb"),
                        ("si_cl0_image", "si0_ramfw"), ("si_cl1_image", "si_cl1")):
            name = next((data["images"].get(key) for key in aliases if data["images"].get(key)), None)
            if not name or not (self.qboxconf.parent / name).is_file():
                raise FileNotFoundError(f"Prebuilt QBox image missing: {aliases[0]} ({name})")
        if self.config.get("rootfs"):
            self.rootfs = Path(self.config["rootfs"]).expanduser().resolve()
        elif self.image == "bsp":
            fixed = self.deploy_dir / "nexios-bsp-initramfs-apollo-qvp.wic"
            candidates = sorted(self.deploy_dir.glob("nexios-bsp-initramfs-apollo-qvp-*.wic"))
            self.rootfs = fixed if fixed.is_file() else candidates[-1] if candidates else fixed
        else:
            name = data["images"].get("rootfs_wic", data["images"].get("wic", ""))
            self.rootfs = self.qboxconf.parent / name
        if not self.rootfs.is_file():
            raise FileNotFoundError(f"Prebuilt QBox {self.image} rootfs WIC missing: {self.rootfs}")
        # Reuse pidfd/descendant ownership, in addition to the board supervisor's
        # own cleanup. No process-name matching or workspace-wide termination.
        spec = importlib.util.spec_from_file_location(
            "_apollo_pytest_owned_processes", self.workspace_root / "scripts/run/qbox_tc397.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self._owner_type = module.OwnedProcesses
        self._initialized = True

    def _select_ssh_port(self):
        port = int(self.config.get("ssh_port", 0))
        if not 0 <= port <= 65535:
            raise ValueError("ssh_port must be 0 or a valid TCP port")
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", port))
            return listener.getsockname()[1]

    def start(self):
        if self.is_running():
            raise RuntimeError("QBox session is already running")
        if self.owner is not None:
            self.stop()
        if not self._initialized:
            self.init()
        positive_timeout(self.config.get("run_timeout", 14400))
        http_port = self.config.get("validation_http_port")
        if http_port is not None and (
                isinstance(http_port, bool) or not isinstance(http_port, int)
                or not 1 <= http_port <= 65535):
            raise ValueError("validation_http_port must be an integer in range 1..65535")
        self._generation += 1
        self.output_root.mkdir(parents=True, exist_ok=True)
        self.run_dir = self.output_root / f"run-{self._generation:04d}"
        self.run_dir.mkdir(mode=0o700, exist_ok=False)
        self.ssh_port = self._select_ssh_port()
        self.manager.bind(self.run_dir, self.ssh_port, self.is_running)
        command = [str(self.workspace_root / "run_qbox_yocto.sh"),
                   "--machine", "apollo-qvp", "--build-dir", str(self.build_dir),
                   "--deploy-dir", str(self.deploy_dir),
                   "--work-dir", str(self.build_dir / "tmp_baremetal/work/apollo_qvp-poky-linux"),
                   "--qboxconf", str(self.qboxconf), "--out-dir", str(self.run_dir),
                   "--rootfs", str(self.rootfs),
                   "--timeout", str(self.config.get("run_timeout", 14400)),
                   "--headless", "--multi-session", "--copy-disks",
                   "--no-persistent-rse-state", "--no-vmcu", "--foreground-runtime"]
        if self.image == "bsp":
            command.append("--bsp")
        if http_port is not None:
            # The canonical launcher adds the HTTP guestfwd to this session's
            # SSH netdev. Keep a single owner for guest-forwarding composition.
            command.extend(["--validation-http-port", str(http_port)])
        launch_spec = {"command": command, "cwd": str(self.workspace_root), "vmcu": False,
                       "env": {"SSH_PORT": str(self.ssh_port),
                               "IMAGE_BASENAME": "nexios-bsp-initramfs" if self.image == "bsp" else "nexios-image",
                               "QBOX_APOLLO_NETDEV": f"type=user,hostfwd=tcp:127.0.0.1:{self.ssh_port}-:22"}}
        spec_path = self.run_dir / "launch-spec.json"
        spec_path.write_text(json.dumps(launch_spec, indent=2) + "\n")
        self.run_id = "pytest-" + uuid.uuid4().hex
        supervisor = [sys.executable, str(self.workspace_root / "scripts/run/qbox_board_session.py"),
                      "--launch-spec", str(spec_path), "--out-dir", str(self.run_dir),
                      "--run-id", self.run_id]
        try:
            self._supervisor_log = (self.run_dir / "board-supervisor.log").open("wb")
            self.process = subprocess.Popen(
                supervisor, cwd=self.workspace_root, stdin=subprocess.DEVNULL,
                stdout=self._supervisor_log, stderr=subprocess.STDOUT, start_new_session=True)
            self.owner = self._owner_type(self.process)
            self._watch_stop.clear()

            def watch():
                while not self._watch_stop.wait(.2):
                    self.owner.discover()

            self._watcher = threading.Thread(target=watch, name="qbox-pytest-ownership", daemon=True)
            self._watcher.start()
            self.manager.connect()
            self._started = True
        except BaseException:
            self.stop()
            raise

    def stop(self):
        disconnect_error = None
        try:
            self.manager.disconnect()
        except Exception as error:
            disconnect_error = error
        self._watch_stop.set()
        if self._watcher is not None:
            self._watcher.join(timeout=2)
            self._watcher = None
        try:
            if self.owner is not None:
                try:
                    self.cleanup_result = self.owner.stop(35)
                    if self._started:
                        self._check_board_cleanup()
                    (self.run_dir / "target-cleanup.json").write_text(
                        json.dumps(self.cleanup_result, indent=2) + "\n")
                finally:
                    self.owner.close()
                    self.owner = None
                if self.cleanup_result["status"] != "PASS":
                    raise RuntimeError(f"QBox owned-process cleanup failed: {self.cleanup_result}")
            elif self.process is not None and self.process.poll() is None:
                # Popen succeeded but constructing OwnedProcesses failed.
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=5)
        finally:
            self._started = False
            if self._supervisor_log is not None:
                self._supervisor_log.close()
                self._supervisor_log = None
        if disconnect_error is not None:
            raise disconnect_error

    def _check_board_cleanup(self):
        """A clean outer process tree cannot override a failed board receipt."""
        try:
            board = json.loads((self.run_dir / "board-session.json").read_text())
            cleanup = board.get("cleanup")
            valid = (board.get("run_id") == self.run_id
                     and board.get("supervisor_pid") == self.process.pid
                     and board.get("status") == "STOPPED"
                     and board.get("returncode") == 0
                     and isinstance(cleanup, dict)
                     and cleanup.get("status") == "PASS"
                     and cleanup.get("residual_pids") == [])
            self.cleanup_result["board_session"] = {
                "status": board.get("status"), "returncode": board.get("returncode"),
                "cleanup": cleanup, "valid": valid,
            }
            if not valid:
                self.cleanup_result["status"] = "FAIL"
        except (OSError, ValueError, AttributeError) as error:
            self.cleanup_result.update(status="FAIL", board_session_error=str(error))

    def reset(self):
        self.stop()
        self.start()

    def wait_ready(self, timeout_s=None):
        timeout = positive_timeout(timeout_s if timeout_s is not None else self.config.get("boot_timeout", 600))
        prompt = (r"NEXIOS_BSP_INITRAMFS_READY|nexios-bsp#" if self.image == "bsp"
                  else r"(?m)apollo-qvp login:|" + AP_SHELL.removeprefix("(?m)"))
        if not self.is_running() or not self.manager.wait_for_prompt_in_log(self.manager.get_port("ap"), prompt, timeout, regex=True):
            status = self.process.poll() if self.process else None
            raise RuntimeError(f"QBox AP boot readiness failed (process rc={status}); logs: {self.run_dir}")

    def is_running(self):
        return self.process is not None and self.process.poll() is None

    def get_ports(self):
        return dict(self.manager.terminal_to_port)

    def log_path(self):
        return self.manager.log_path("ap")
