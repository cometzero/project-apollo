"""Deploy matching Yocto HIPC/PFDI payload to the owned private AutoSD guest."""
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import time
import uuid

import paramiko

MODULES = {"arm_si_rproc": "arm-si-rproc-mod", "rpmsg_net": "rpmsg-net-mod"}


def module_inputs(build_dir):
    """Fail closed on ambiguous builds or mixed kernel releases."""
    work = Path(build_dir) / "tmp_baremetal/work/apollo_qvp-poky-linux"
    modules = {}
    for name, recipe in MODULES.items():
        paths = list((work / recipe).glob(f"*/image/usr/lib/modules/*/updates/{name}.ko"))
        if len(paths) != 1:
            raise ValueError(f"Expected one built {name}.ko under {work / recipe}; found {len(paths)}")
        path = paths[0].resolve()
        vermagic = subprocess.check_output(["modinfo", "-F", "vermagic", str(path)], text=True).strip()
        release = vermagic.split()[0]
        if not re.fullmatch(r"[A-Za-z0-9_.+-]+", release):
            raise ValueError("Invalid module kernel release")
        if path.parent.parent.name != release:
            raise ValueError("Module path and vermagic release disagree")
        modules[name] = {"path": str(path), "release": release, "vermagic": vermagic,
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    if len({m["vermagic"] for m in modules.values()}) != 1:
        raise ValueError("Full-system modules were built for different kernels")
    return modules


def endpoint_ready_command():
    """Check enumeration only; do not imply link traffic qualification."""
    return r'''ready=0; attempts=0
while [ "$attempts" -lt 30 ]; do
    if [ -r /sys/class/net/ethsi1/ifindex ]; then
        for endpoint in /sys/bus/rpmsg/devices/*; do
            [ -r "$endpoint/name" ] || continue
            [ "$(cat "$endpoint/name")" = ethsi1 ] || continue
            [ "$(basename "$(readlink "$endpoint/driver")")" = rpmsg_netdev ] || continue
            printf 'HIPC_ENDPOINT_READY boot_id=%s ifindex=%s endpoint=%s driver=rpmsg_netdev\n' "$(cat /proc/sys/kernel/random/boot_id)" "$(cat /sys/class/net/ethsi1/ifindex)" "$endpoint"
            ready=1; break
        done
    fi
    [ "$ready" = 0 ] || break
    attempts=$((attempts + 1)); sleep 1
done
[ "$ready" = 1 ] || { echo HIPC_NETDEV_NOT_READY >&2; exit 1; }'''


def install_command(modules, remote, prepare_only=False):
    release = modules["arm_si_rproc"]["release"]
    destination = "/usr/lib/modules/" + release + "/updates"
    q = shlex.quote
    commands = ["set -eu", 'test "$(id -u)" = 0', '. /etc/os-release; test "$ID" = autosd',
                'test "$(uname -r)" = ' + q(release), "install -d " + q(destination)]
    for name, entry in modules.items():
        source = remote + "/" + name + ".ko"
        commands += ["printf '%s\\n' " + q(entry["sha256"] + "  " + source) + " | sha256sum -c -",
                     "install -m 0644 " + q(source) + " " + q(destination + "/" + name + ".ko")]
    commands += ["restorecon -R " + q(destination), "depmod -a " + q(release),
                 "printf '%s\\n' virtio_rpmsg_bus arm_si_rproc rpmsg_net > /etc/modules-load.d/apollo-fullsystem.conf",
                 "restorecon /etc/modules-load.d/apollo-fullsystem.conf",
                 "modprobe virtio_rpmsg_bus", "modprobe arm_si_rproc", "modprobe rpmsg_net",
                 "test -d /sys/module/arm_si_rproc", "test -d /sys/module/rpmsg_net",
                 "modinfo -F vermagic arm_si_rproc", "modinfo -F vermagic rpmsg_net"]
    if not prepare_only:
        commands.append(endpoint_ready_command())
    commands.append("printf '%s\\n' AUTOSD_FULLSYSTEM_MODULES_PASS")
    return "timeout -k 5s 120s sh -c " + q("; ".join(commands))


def provision(port, build_dir, out, prepare_only=False):
    """Bounded SSH provisioning; firmware readiness remains a separate check."""
    out = Path(out)
    result = {"status": "FAIL", "prepare_only": prepare_only,
              "qualification": "payload installation; endpoint not qualified" if prepare_only else
              "module load, RPMsg ethsi1 enumeration and PFDI startup; not sustained monitoring or RPMsg traffic qualification"}
    client = None
    try:
        if not 1024 <= port <= 65535:
            raise ValueError("Invalid private guest SSH port")
        modules = module_inputs(build_dir)
        result["modules"] = modules
        from autosd_fullsystem_pfdi import pfdi_inputs, service_files, install_commands
        from autosd_fullsystem_boot_policy import service_files as boot_files, install_commands as boot_commands
        pfdi = pfdi_inputs(build_dir)
        result["pfdi_assets"] = pfdi
        deadline = time.monotonic() + 180
        last_error = "SSH unavailable"
        while time.monotonic() < deadline:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect("127.0.0.1", port=port, username="root", password="password",
                               look_for_keys=False, allow_agent=False, timeout=3, banner_timeout=5, auth_timeout=5)
                break
            except (OSError, paramiko.SSHException) as error:
                last_error = str(error)
                client.close()
                client = None
                time.sleep(2)
        if client is None:
            raise RuntimeError(last_error)
        remote = "/var/tmp/apollo-fullsystem-" + uuid.uuid4().hex
        with client.open_sftp() as sftp:
            sftp.get_channel().settimeout(15)
            sftp.mkdir(remote, mode=0o700)
            for name, entry in modules.items():
                sftp.put(entry["path"], remote + "/" + name + ".ko")
            for name, entry in pfdi.items():
                sftp.put(entry["path"], remote + "/" + name)
            for name, content in {**service_files(), **boot_files()}.items():
                with sftp.open(remote + "/" + name, "w") as stream:
                    stream.write(content)
        channel = client.get_transport().open_session(timeout=5)
        channel.settimeout(5)
        channel.set_combine_stderr(True)
        command = install_command(modules, remote, prepare_only=prepare_only)
        pfdi_commands = install_commands(pfdi, remote, prepare_only=prepare_only)
        command += " && timeout -k 5s 120s sh -c " + shlex.quote("set -eu; " + "; ".join(pfdi_commands))
        command += " && timeout -k 5s 60s sh -c " + shlex.quote("set -eu; " + "; ".join(boot_commands(remote)))
        channel.exec_command(command)
        deadline = time.monotonic() + 150
        with (out / "modules.log").open("wb") as log:
            while True:
                if time.monotonic() >= deadline:
                    channel.close()
                    raise TimeoutError("Module deployment command exceeded 150 host seconds")
                if channel.recv_ready():
                    log.write(channel.recv(16384))
                    log.flush()
                elif channel.exit_status_ready():
                    result["returncode"] = channel.recv_exit_status()
                    break
                else:
                    time.sleep(.1)
        if result["returncode"] != 0:
            raise RuntimeError("Module installation/loading failed; inspect modules.log")
        result["status"] = "PASS"
    except (OSError, ValueError, RuntimeError, paramiko.SSHException, subprocess.SubprocessError) as error:
        result["error"] = str(error)
    finally:
        if client is not None:
            client.close()
        temporary = out / "modules.json.tmp"
        temporary.write_text(json.dumps(result, indent=2) + "\n")
        temporary.replace(out / "modules.json")
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=2244)
    parser.add_argument("--build-dir", type=Path, default=Path("build"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--prepare-only", action="store_true",
                        help="Install/enable full-system payload in a booted private guest; do not start PFDI")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    report = provision(args.port, args.build_dir, args.out, args.prepare_only)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)
