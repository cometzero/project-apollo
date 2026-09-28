"""Loopback monitor launch contract and Linux listener ownership evidence."""
import json
import os
from pathlib import Path
import socket
import time
import tempfile

_last_updates = {}


def prepare_qmp(plan):
    """Create a private short path; Unix sun_path cannot fit long run paths."""
    if not plan.get("qmp_enabled"):
        plan["environment"]["QBOX_APOLLO_QMP_DIR"] = ""
        return
    directory = Path(tempfile.mkdtemp(prefix=f"qbox-qmp-{os.getuid()}-"))
    plan["environment"]["QBOX_APOLLO_QMP_DIR"] = str(directory)
    for domain in plan["monitor"]["domains"]:
        domain["qmp_socket"] = str(directory / (domain["domain_id"] + ".sock"))
        domain["qmp_biflow"] = "platform." + domain["domain_id"].replace("-", "_") + "_qmp.qmp_socket.qmp_socket_router"
        if domain["domain_id"] == "rse":
            domain["qmp_biflow"] = "platform.rse_cpu_pass.rse_qmp.qmp_socket.qmp_socket_router"


def monitor_plan(enabled, port, out, full=False, cpus=4):
    enabled = bool(enabled or port is not None)
    port = 18080 if port is None else port
    if not 1 <= port <= 65535:
        raise ValueError("monitor port must be in range 1..65535")
    domains = [("ap", "ap_qemu_inst", [f"ap_cpu_{i}" for i in range(cpus)])]
    if full:
        domains[:0] = [("rse", "rse_cpu_pass.qemu_inst", ["rse_cpu_pass.cpu_0.cpu"]),
                       ("si-cl0", "si_cl0_qemu_inst", ["si_cl0_cpu_0"]),
                       ("si-cl1", "si_cl1_qemu_inst", [f"si_cl1_cpu_{i}" for i in range(4)])]
    return {"enabled": enabled, "host": "127.0.0.1", "port": port,
            "url": f"http://127.0.0.1:{port}", "runtime_manifest": str(out / "monitor-runtime.json"),
            "domains": [{"domain_id": d, "qemu_instance_path": "platform." + q,
                         "cpu_object_paths": ["platform." + c for c in cs]} for d, q, cs in domains]}


def monitor_environment(monitor):
    return {"QBOX_APOLLO_MONITOR": "true" if monitor["enabled"] else "false",
            "QBOX_APOLLO_MONITOR_PORT": str(monitor["port"]),
            "QBOX_APOLLO_MONITOR_BIND_ADDRESS": "127.0.0.1",
            "QBOX_APOLLO_RUNTIME_INJECTION": "false"}


def preflight(monitor):
    if monitor.get("enabled"):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", monitor["port"]))


def process_identity(pid):
    text = Path(f"/proc/{pid}/stat").read_text()
    fields = text[text.rfind(")") + 2:].split()
    return int(fields[1]), int(fields[19])


def listener_owner(port, parent):
    """Resolve actual loopback LISTEN inode to an owned descendant process."""
    inodes = set()
    for line in Path("/proc/net/tcp").read_text().splitlines()[1:]:
        fields = line.split()
        if fields[1] == f"0100007F:{port:04X}" and fields[3] == "0A":
            inodes.add(fields[9])
    if not inodes:
        return None
    processes = {}
    for path in Path("/proc").iterdir():
        if path.name.isdigit():
            try:
                if path.stat().st_uid == os.getuid():
                    processes[int(path.name)] = process_identity(int(path.name))
            except (OSError, ValueError):
                pass
    descendants = {parent}
    while True:
        expanded = descendants | {p for p, (pp, _) in processes.items() if pp in descendants}
        if expanded == descendants:
            break
        descendants = expanded
    for pid in descendants:
        try:
            if any(fd.readlink().as_posix() in {f"socket:[{i}]" for i in inodes}
                   for fd in Path(f"/proc/{pid}/fd").iterdir()):
                return {"pid": pid, "start_ticks": processes[pid][1]}
        except (OSError, KeyError):
            continue
    raise RuntimeError("monitor port listener is not owned by this QBox launch")


def update_runtime(monitor, parent, run_id):
    if not monitor.get("enabled"):
        return
    key = monitor["runtime_manifest"]
    now = time.monotonic()
    if now - _last_updates.get(key, -10) < 2:
        return
    _last_updates[key] = now
    owner = listener_owner(monitor["port"], parent)
    value = {"schema_version": 1, "run_id": run_id, "status": "READY" if owner else "STARTING",
             "host": "127.0.0.1", "port": monitor["port"], **(owner or {})}
    path = Path(monitor["runtime_manifest"])
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value) + "\n")
    temporary.replace(path)
