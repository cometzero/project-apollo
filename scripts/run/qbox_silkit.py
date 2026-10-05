"""Owned SIL Kit processes for the TC397 supervisor (no SDK import required)."""

import json
import os
from pathlib import Path
import re
import stat
import subprocess
import time
import uuid


def add_arguments(parser):
    root = Path(__file__).resolve().parents[2]
    build = root / "build/qbox-apollo-qvp/vmcu-silkit"
    parser.add_argument("--sil-kit", action="store_true")
    parser.add_argument("--sil-kit-registry", default="")
    parser.add_argument("--sil-kit-allow-actuation", action="store_true")
    parser.add_argument("--sil-kit-echo-fixture", action="store_true")
    parser.add_argument("--sil-kit-binary", type=Path, default=Path(os.environ.get(
        "QBOX_SILKIT_BINARY", str(build / "native/vmcu-silkit"))))
    parser.add_argument("--sil-kit-registry-binary", type=Path, default=Path(os.environ.get(
        "QBOX_SILKIT_REGISTRY_BINARY", str(build / "sdk/SilKit-5.0.7-ubuntu-22.04-x86_64-gcc/SilKit/bin/sil-kit-registry"))))


def validate(args, parser):
    if not args.sil_kit:
        if args.sil_kit_registry or args.sil_kit_allow_actuation or args.sil_kit_echo_fixture:
            parser.error("SIL Kit options require --sil-kit")
        return
    paths = [args.sil_kit_binary]
    if not args.sil_kit_registry:
        paths.append(args.sil_kit_registry_binary)
    for path in paths:
        if not path.is_file() or not os.access(path, os.X_OK):
            parser.error(f"SIL Kit executable unavailable: {path}; run scripts/build/build_vmcu_silkit.sh --bootstrap")
    if args.sil_kit_registry and not args.sil_kit_registry.startswith("silkit://"):
        parser.error("--sil-kit-registry must be a silkit:// URI")


class SilKit:
    """Start participants while MCU is paused; parent owns process termination."""

    def __init__(self, args, output, owners, owner_type, stopped):
        self.args, self.output = args, output
        self.owners, self.owner_type, self.stopped = owners, owner_type, stopped
        self.files, self.processes = [], []
        self.metadata = {"status": "STARTING", "processes": [],
                         "allow_actuation": args.sil_kit_allow_actuation,
                         "echo_fixture": args.sil_kit_echo_fixture,
                         "external_registry": bool(args.sil_kit_registry)}

    def spawn(self, role, command, stdin=None):
        log = self.output / ("silkit-" + role + ".log")
        handle = log.open("wb")
        self.files.append(handle)
        process = subprocess.Popen(command, stdin=stdin or subprocess.DEVNULL,
                                   stdout=handle, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        self.owners.append(self.owner_type(process))
        self.processes.append(process)
        self.metadata["processes"].append({"role": role, "pid": process.pid,
                                           "command": command, "log": str(log)})

    def check(self):
        if self.stopped():
            raise InterruptedError("SIL Kit startup interrupted")
        for process, entry in zip(self.processes, self.metadata["processes"]):
            if process.poll() is not None:
                raise RuntimeError(f"SIL Kit {entry['role']} exited unexpectedly ({process.returncode}); see {entry['log']}")

    def start(self, endpoint):
        deadline = time.monotonic() + self.args.startup_timeout
        uri = self.args.sil_kit_registry
        if not uri:
            generated = self.output / "silkit-registry.yaml"
            generated.unlink(missing_ok=True)
            self.spawn("registry", [str(self.args.sil_kit_registry_binary.resolve()),
                       "-u", "silkit://127.0.0.1:0", "-g", str(generated), "-l", "warn"])
            while not uri:
                self.check()
                if time.monotonic() >= deadline:
                    raise TimeoutError("SIL Kit registry readiness timed out")
                if generated.exists():
                    match = re.search(r"RegistryUri:\s*['\"]?(silkit://[^\s'\"]+)", generated.read_text())
                    if match:
                        uri = match[1]
                time.sleep(.02)
        suffix = "-" + uuid.uuid4().hex[:12]
        names = {"bridge": "TC397CanBridge" + suffix, "restbus": "VehicleRestbus" + suffix}
        fifo = self.output / "vehicle-can.in"
        if not fifo.exists():
            os.mkfifo(fifo, 0o600)
        if not stat.S_ISFIFO(fifo.stat().st_mode):
            raise ValueError(f"Vehicle CAN input must be a FIFO: {fifo}")
        # Hold both ends so absent writers cannot produce EOF in the participant.
        fifo_file = os.fdopen(os.open(fifo, os.O_RDWR | os.O_NONBLOCK), "rb", buffering=0)
        self.files.append(fifo_file)
        self.metadata.update(registry_uri=uri, participant_names=names,
                             can_endpoint=endpoint, input_fifo=str(fifo), network="VehicleCAN")
        readers = []
        for role, filename in (("bridge", "tc397-can.jsonl"), ("restbus", "vehicle-can.jsonl")):
            path = self.output / filename
            path.write_text("")
            reader = path.open()
            self.files.append(reader)
            readers.append(reader)
            self.metadata[role + "_events"] = str(path)
            command = [str(self.args.sil_kit_binary.resolve()), "--role", role,
                       "--registry-uri", uri, "--name", names[role], "--require-peer",
                       names["restbus" if role == "bridge" else "bridge"], "--events", str(path)]
            if role == "bridge":
                command += ["--qemu-endpoint", endpoint]
            else:
                command += ["--stdin"]
                if self.args.sil_kit_allow_actuation:
                    command += ["--allow-actuation"]
                if self.args.sil_kit_echo_fixture:
                    command += ["--echo-fixture"]
            self.spawn(role, command, fifo_file if role == "restbus" else None)
        events = [set(), set()]
        controller_seen = False
        pending = ["", ""]
        while not (controller_seen and all({"participant_ready", "peer_running"} <= seen for seen in events)):
            self.check()
            if time.monotonic() >= deadline:
                raise TimeoutError("SIL Kit participant readiness timed out")
            for index, reader in enumerate(readers):
                pending[index] += reader.read(65536)
                lines = pending[index].split("\n")
                pending[index] = lines.pop()
                if len(pending[index]) > 65536:
                    raise RuntimeError("SIL Kit event exceeded size limit")
                for line in lines:
                    event = json.loads(line).get("event")
                    if index == 0 and event in ("controller_started", "controller_stopped"):
                        controller_seen = True
                    if event in ("participant_ready", "peer_running"):
                        events[index].add(event)
                    elif event == "peer_unavailable":
                        events[index].discard("peer_running")
            time.sleep(.02)
        self.metadata.update(status="READY", can_transport_ready=True)

    def close(self):
        for process, entry in zip(self.processes, self.metadata["processes"]):
            entry["returncode"] = process.poll()
        for handle in self.files:
            handle.close()
