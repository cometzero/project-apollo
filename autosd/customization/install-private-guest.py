#!/usr/bin/python3
"""Install the layer only in a disposable, regular AutoSD VM for qualification.

Production OS images must be built with AIB. This installer requires the
previously validated minimal_qm demo with BlueChi and nested Podman installed.
"""
import json
from pathlib import Path
import shutil
import subprocess


def run(*args):
    return subprocess.run(args, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()


def main():
    bundle = Path(__file__).resolve().parent
    assert run("uname", "-m") == "aarch64"
    assert run("getenforce") == "Enforcing"
    assert int(run("getconf", "_NPROCESSORS_ONLN")) >= 4
    assert not Path("/run/ostree-booted").exists(), "Use a regular private image"
    for package in ("podman", "python3", "bluechi-controller", "bluechi-agent", "bluechi-selinux"):
        run("rpm", "-q", package)
    qm_root = Path(run("podman", "inspect", "--format", "{{.Rootfs}}", "qm"))
    assert str(qm_root) == "/usr/lib/qm/rootfs"
    run("systemctl", "stop", "qm")
    manifest = json.loads((bundle / "runtime-files.json").read_text())
    for content, is_qm in ((manifest["content"], False), (manifest["qm"]["content"], True)):
        for item in content["add_files"]:
            destination = Path(item["path"])
            if is_qm:
                destination = (Path("/etc/qm") / destination.relative_to("/etc")
                               if destination.is_relative_to("/etc")
                               else qm_root / destination.relative_to("/"))
            destination.parent.mkdir(parents=True, exist_ok=True)
            if "text" in item:
                destination.write_text(item["text"])
            else:
                source = bundle / item["source_path"]
                if item["path"] == "/usr/bin/crun":
                    backup = destination.with_name("crun.apollo-vendor-backup")
                    if not backup.exists():
                        shutil.copy2(destination, backup)
                    temporary = destination.with_name("crun.apollo-new")
                    shutil.copy2(source, temporary)
                    temporary.chmod(0o755)
                    temporary.replace(destination)
                    run("restorecon", str(destination))
                else:
                    shutil.copy2(source, destination)
    # The runtime installer mirrors the AIB QM resource policy.
    Path("/etc/containers/systemd/qm.container.d/30-automotive-limits.conf").write_text(
        "[Service]\nCPUWeight=50\nMemoryHigh=768M\nMemoryMax=1G\n")
    run("restorecon", "-RF", "/etc/bluechi", "/etc/qm", "/etc/containers/systemd",
        "/etc/systemd/system", "/etc/modules-load.d", "/usr/libexec/apollo", str(qm_root / "usr/libexec/apollo"))
    # Mirror the next boot's modules-load.d policy before starting QM now.
    run("modprobe", "br_netfilter")
    run("podman", "build", "--network=none", "--pull=never", "-t", "localhost/apollo-workload:1",
        str(bundle / "payload"))
    run("podman", "save", "--format=oci-archive", "-o", str(bundle / "workload.oci"),
        "localhost/apollo-workload:1")
    run("systemctl", "daemon-reload")
    run("systemctl", "restart", "bluechi-controller", "bluechi-agent")
    run("systemctl", "start", "qm")
    run("podman", "cp", str(bundle / "workload.oci"), "qm:/run/workload.oci")
    run("podman", "exec", "qm", "podman", "load", "-i", "/run/workload.oci")
    run("podman", "exec", "qm", "systemctl", "daemon-reload")
    run("podman", "exec", "qm", "systemctl", "enable", "--now", "bluechi-agent", "apollo-qm-app")
    run("podman", "exec", "qm", "systemctl", "start", "apollo-qm-container")
    run("systemctl", "start", "apollo-adas")
    run("systemctl", "enable", "--now", "apollo-safety-monitor")
    print("LAYER_INSTALLED", flush=True)


if __name__ == "__main__":
    main()
