#!/usr/bin/env python3
"""Build a self-contained Apollo AutoSD customization input bundle."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import jsonschema
import yaml

LAYER = Path(__file__).resolve().parent
ROOT = LAYER.parents[1]


def prepare(output, compiler, rt_tools=False, crun_binary=None, watchdog_tools=False):
    output.mkdir(parents=True, exist_ok=False)
    payload = output / "payload"
    payload.mkdir()
    binary = payload / "workload"
    subprocess.run([compiler, "-static", "-O2", "-Wall", "-Wextra", "-Werror",
                    str(LAYER / "apps/workload.c"), "-o", str(binary)], check=True)
    # This bundle targets the existing Apollo AArch64 BSP only.
    header = binary.read_bytes()[:20]
    if header[:4] != b"\x7fELF" or int.from_bytes(header[18:20], "little") != 183:
        raise ValueError("Compiler must produce an AArch64 ELF")
    (payload / "Containerfile").write_text(
        "FROM scratch\nCOPY workload /workload\nCMD [\"/workload\", \"run\", \"/run/heartbeat\"]\n")
    base = yaml.safe_load((ROOT / "scripts/autosd_demo/apollo_kernel_image.aib.yml").read_text())
    base["name"] = "apollo-automotive-scenario"
    # Authentication is supplied explicitly by the product integrator.
    base.pop("auth", None)
    base.pop("image", None)  # Do not inherit the demo's always-success health check.
    root = base["content"]
    root["rpms"] = ["podman", "python3", "bluechi-controller", "bluechi-agent",
                    "bluechi-selinux", "bluechi-ctl"]
    root["systemd"] = {"enabled_services": ["bluechi-controller.service", "bluechi-agent.service",
                                               "apollo-safety-monitor.service"]}
    image = {"source": "localhost/apollo-workload", "tag": "1",
             "name": "localhost/apollo-workload:1", "containers-transport": "containers-storage"}
    root["container_images"] = [image.copy()]
    base["qm"] = {"cpu_weight": 50, "memory_limit": {"high": "768M", "max": "1G"},
                  "content": {"rpms": ["podman", "bluechi-agent"],
                              "container_images": [image.copy()],
                              "systemd": {"enabled_services": ["bluechi-agent.service",
                                                               "apollo-qm-app.service"]}}}
    qm = base["qm"]["content"]
    if crun_binary is not None:
        patched_runtime = Path(crun_binary).read_bytes()
        if patched_runtime[:4] != b"\x7fELF" or int.from_bytes(patched_runtime[18:20], "little") != 183:
            raise ValueError("Patched crun must be an AArch64 ELF")
        shutil.copy2(crun_binary, payload / "crun")
        for content in (root, qm):
            content.setdefault("add_files", []).append(
                {"path": "/usr/bin/crun", "source_path": "./payload/crun"})
            content.setdefault("chmod_files", []).append({"path": "/usr/bin/crun", "mode": "0755"})

    def add(content, source, destination):
        # Embed text so manifests can be moved between host and native builder.
        content.setdefault("add_files", []).append({"path": destination, "text": source.read_text()})

    for name in ("apollo-safety-monitor.service", "apollo-asil-b.slice"):
        add(root, LAYER / "root" / name, "/etc/systemd/system/" + name)
    add(root, LAYER / "root/safety-monitor.py", "/usr/libexec/apollo/safety-monitor.py")
    add(root, LAYER / "root/apollo-adas.container", "/etc/containers/systemd/apollo-adas.container")
    add(root, LAYER / "root/20-automotive-qm.conf", "/etc/containers/systemd/qm.container.d/20-automotive.conf")
    add(root, LAYER / "root/apollo-container-network.conf", "/etc/modules-load.d/apollo-container-network.conf")
    add(qm, LAYER / "qm/apollo-qm-app.service", "/etc/systemd/system/apollo-qm-app.service")
    add(qm, LAYER / "qm/apollo-qm-container.container", "/etc/containers/systemd/apollo-qm-container.container")
    conf = ROOT / "autosd/sig-docs/demos/bluechi_root_qm/conf"
    add(root, conf / "10-bluechi-controller.conf", "/etc/bluechi/controller.conf.d/10-automotive.conf")
    add(root, conf / "10-bluechi-agent-root.conf", "/etc/bluechi/agent.conf.d/10-automotive.conf")
    add(qm, conf / "10-bluechi-agent-qm.conf", "/etc/bluechi/agent.conf.d/10-automotive.conf")
    qm["add_files"].append({"path": "/usr/libexec/apollo/workload", "source_path": "./payload/workload"})
    qm.setdefault("chmod_files", []).append({"path": "/usr/libexec/apollo/workload", "mode": "0755"})
    watchdog_source = ROOT / "scripts/autosd_demo/watchdog_guest.py"
    if watchdog_tools:
        # Install diagnostics only in root; never enable a watchdog owner or
        # allow a QM workload to control the AP hardware watchdog.
        add(root, watchdog_source, "/usr/libexec/apollo/watchdog-guest.py")
        shutil.copy2(watchdog_source, output / "watchdog-guest.py")
    if rt_tools:
        # AutoSD RPM name is realtime-tests, not the Yocto recipe name rt-tests.
        root["rpms"] += ["realtime-tests", "rtla", "trace-cmd", "util-linux",
                         "procps-ng", "stress-ng"]
        qm["rpms"] += ["stress-ng"]
        probe = payload / "latency-probe"
        subprocess.run([compiler, "-static", "-O2", "-Wall", "-Wextra", "-Werror",
                        str(LAYER / "apps/latency-probe.c"), "-o", str(probe)], check=True)
        header = probe.read_bytes()[:20]
        if header[:4] != b"\x7fELF" or int.from_bytes(header[18:20], "little") != 183:
            raise ValueError("Latency probe must be an AArch64 ELF")
        for content in (root, qm):
            content["add_files"].append({"path": "/usr/libexec/apollo/latency-probe",
                                         "source_path": "./payload/latency-probe"})
            content.setdefault("chmod_files", []).append(
                {"path": "/usr/libexec/apollo/latency-probe", "mode": "0755"})
        add(root, LAYER / "rt/experiment.py", "/usr/libexec/apollo/rt-experiment.py")
        add(root, LAYER / "rt/trace-guest.py", "/usr/libexec/apollo/rt-trace.py")
        add(root, LAYER / "check-guest.sh", "/usr/libexec/apollo/check-automotive.sh")
        # Diagnostics are explicitly invoked, never an automatically enabled RT service.
        shutil.copy2(LAYER / "rt/experiment.py", output / "rt-experiment.py")
        shutil.copy2(LAYER / "rt/trace-guest.py", output / "rt-trace.py")
    for content in (root, qm):
        directories = sorted({str(Path(f["path"]).parent) for f in content["add_files"]})
        content["make_dirs"] = [{"path": d, "mode": 0o755, "parents": True, "exist_ok": True}
                                for d in directories]
    schema = yaml.safe_load((ROOT / "autosd/automotive-image-builder/files/manifest_schema.yml").read_text())
    jsonschema.Draft7Validator(schema).validate(base)
    (output / "automotive.aib.yml").write_text(yaml.safe_dump(base, sort_keys=False))
    (output / "runtime-files.json").write_text(json.dumps(base, indent=2) + "\n")
    shutil.copy2(LAYER / "build-guest.sh", output / "build-guest.sh")
    shutil.copy2(LAYER / "install-private-guest.py", output / "install-private-guest.py")
    sources = [p for p in LAYER.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    if watchdog_tools:
        sources.append(watchdog_source)
    provenance = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    provenance["workload_sha256"] = hashlib.sha256(binary.read_bytes()).hexdigest()
    if crun_binary is not None:
        provenance["crun_sha256"] = hashlib.sha256(patched_runtime).hexdigest()
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    return base


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--cc", default="aarch64-linux-gnu-gcc")
    parser.add_argument("--rt-tools", action="store_true",
                        help="Add opt-in RT measurement utilities; leave QM RT restrictions intact")
    parser.add_argument("--crun-binary", type=Path,
                        help="Pinned patched AArch64 crun overlay for root and QM (see runtime/README.md)")
    parser.add_argument("--watchdog-tools", action="store_true",
                        help="Install opt-in root watchdog diagnostics; never enable RuntimeWatchdog")
    args = parser.parse_args()
    prepare(args.out.resolve(), args.cc, args.rt_tools, args.crun_binary, args.watchdog_tools)
