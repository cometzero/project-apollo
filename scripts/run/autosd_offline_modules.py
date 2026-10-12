"""Install matching modules and PFDI before the first private full-system boot."""
from pathlib import Path
import shutil
import re
import ctypes
import shlex
import subprocess
import tarfile
import tempfile

from autosd_fullsystem_modules import module_inputs
from autosd_fullsystem_pfdi import pfdi_inputs, service_files


def prepare(disk, archive, build_dir, guestfish="guestfish"):
    modules = module_inputs(build_dir)
    pfdi = pfdi_inputs(build_dir)
    release = pfdi["pfdi_misc.ko"]["release"]
    if any(entry["release"] != release for entry in modules.values()):
        raise ValueError("PFDI and HIPC module releases disagree")
    with tempfile.TemporaryDirectory(prefix="autosd-payload-") as temporary:
        root = Path(temporary) / "root"
        root.mkdir()
        prefix = "lib/modules/" + release
        with tarfile.open(archive, "r:gz") as source:
            members = source.getmembers()
            if not any(member.name.startswith(prefix + "/") for member in members):
                raise ValueError("Archive does not match full-system kernel release")
            for member in members:
                name = member.name.rstrip("/")
                if name in ("lib", "lib/modules"):
                    continue
                if not (name == prefix or name.startswith(prefix + "/")) or ".." in Path(name).parts:
                    raise ValueError("Unexpected module archive path: " + name)
                if member.issym() or member.islnk():
                    raise ValueError("Module archive links are not supported")
                member.name = "usr/" + name
                source.extract(member, root, filter="data")
        entries = list(pfdi.values()) + [dict(entry, target=f"/usr/lib/modules/{release}/updates/{name}.ko", mode="0644")
                                          for name, entry in modules.items()]
        for entry in entries:
            target = root / entry["target"].lstrip("/")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(entry["path"], target)
            target.chmod(int(entry["mode"], 8))
        for name, contents in service_files().items():
            target = root / ("etc/systemd/system" if name.endswith(".service") else "usr/libexec") / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(contents)
            target.chmod(0o644 if name.endswith(".service") else 0o755)
        enabled = root / "etc/systemd/system/multi-user.target.wants"
        enabled.mkdir(parents=True)
        (enabled / "apollo-pfdi.service").symlink_to("../apollo-pfdi.service")
        module_load = root / "etc/modules-load.d/apollo-fullsystem.conf"
        module_load.parent.mkdir(parents=True)
        module_load.write_text("virtio_rpmsg_bus\narm_si_rproc\nrpmsg_net\n")
        (root / "lib").symlink_to("usr/lib")
        subprocess.run(["depmod", "-b", str(root), release], check=True, timeout=180)
        base = [guestfish, "--format=raw", "-a", str(disk)]
        filesystems = subprocess.check_output(base + ["--ro", "run", ":", "list-filesystems"], text=True, timeout=300)
        candidates = []
        for line in filesystems.splitlines():
            device, _, filesystem = line.partition(":")
            if filesystem.strip() == "ext4":
                contents = subprocess.check_output(base + ["--ro", "-m", device + ":/:ro", "is-file", "/etc/os-release", "followsymlinks:true"], text=True, timeout=300)
                if contents.strip() == "true":
                    candidates.append(device)
        if len(candidates) != 1:
            raise ValueError("Expected one regular AutoSD ext4 root filesystem")
        os_release = subprocess.check_output(base + ["--ro", "-m", candidates[0] + ":/:ro",
            "cat", "/etc/os-release"], text=True, timeout=300)
        if not any(line.strip() in ("ID=autosd", 'ID="autosd"') for line in os_release.splitlines()):
            raise ValueError("Offline payload requires AutoSD")
        config = subprocess.check_output(base + ["--ro", "-m", candidates[0] + ":/:ro",
            "cat", "/etc/selinux/config"], text=True, timeout=300)
        policies = re.findall(r"^\s*SELINUXTYPE\s*=\s*([A-Za-z0-9_-]+)\s*$", config, re.MULTILINE)
        if len(policies) != 1:
            raise ValueError("Expected one SELinux policy in guest config")
        contexts = "/etc/selinux/" + policies[0] + "/contexts/files/file_contexts"
        present = subprocess.check_output(base + ["--ro", "-m", candidates[0] + ":/:ro",
            "is-file", contexts, "followsymlinks:true"], text=True, timeout=300)
        if present.strip() != "true":
            raise ValueError("Missing guest SELinux file contexts")
        context_file = Path(temporary) / "file_contexts"
        subprocess.run(base + ["--ro", "-m", candidates[0] + ":/:ro", "download",
            contexts, str(context_file)], check=True, timeout=300)
        for suffix in (".local", ".subs", ".subs_dist"):
            exists = subprocess.check_output(base + ["--ro", "-m", candidates[0] + ":/:ro",
                "is-file", contexts + suffix, "followsymlinks:true"], text=True, timeout=300)
            if exists.strip() == "true":
                subprocess.run(base + ["--ro", "-m", candidates[0] + ":/:ro", "download",
                    contexts + suffix, str(context_file) + suffix], check=True, timeout=300)
        paths = [path for path in sorted(root.rglob("*")) if path != root / "lib"]
        labels = file_contexts(context_file, [("/" + str(path.relative_to(root)), path.lstat().st_mode)
                                              for path in paths])
        payload = Path(temporary) / "payload.tar"
        with tarfile.open(payload, "w") as target:
            for path in paths:
                # Omit parent directory metadata: keep existing guest modes.
                if path.is_dir():
                    continue
                member = target.gettarinfo(str(path), arcname=str(path.relative_to(root)))
                member.uid = member.gid = 0
                member.uname = member.gname = "root"
                if member.isfile():
                    with path.open("rb") as stream:
                        target.addfile(member, stream)
                else:
                    target.addfile(member)
        commands = [shlex.join(["mkdir-p", "/" + str(path.relative_to(root))])
                    for path in paths if path.is_dir()]
        commands.append(shlex.join(["tar-in", str(payload), "/"]))
        commands += [shlex.join(["lsetxattr", "security.selinux", context, str(len(context)), path])
                     for path, context in labels]
        subprocess.run(base + ["--rw", "-m", candidates[0]], input="\n".join(commands) + "\n",
                       text=True, check=True, timeout=1800)
    return {"status": "INSTALLED", "kernel_release": release,
            "qualification": "offline files and SELinux labels only; runtime PFDI remains unverified"}


def file_contexts(policy, paths):
    """Resolve guest labels without requiring SELinux support in the appliance."""
    library = ctypes.CDLL("libselinux.so.1", use_errno=True)
    class Option(ctypes.Structure):
        _fields_ = [("type", ctypes.c_int), ("value", ctypes.c_char_p)]
    library.selabel_open.argtypes = [ctypes.c_uint, ctypes.POINTER(Option), ctypes.c_uint]
    library.selabel_open.restype = ctypes.c_void_p
    library.selabel_lookup_raw.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_char_p), ctypes.c_char_p, ctypes.c_int]
    library.selabel_close.argtypes = [ctypes.c_void_p]
    library.freecon.argtypes = [ctypes.c_char_p]
    # SELABEL_CTX_FILE=0, SELABEL_OPT_PATH=3 from selinux/label.h.
    options = Option(3, str(policy).encode())
    handle = library.selabel_open(0, ctypes.byref(options), 1)
    if not handle:
        raise OSError(ctypes.get_errno(), "Cannot open guest SELinux file contexts")
    try:
        result = []
        for path, mode in paths:
            context = ctypes.c_char_p()
            if library.selabel_lookup_raw(handle, ctypes.byref(context), path.encode(), mode):
                raise OSError(ctypes.get_errno(), "No guest SELinux context for " + path)
            try:
                result.append((path, context.value.decode()))
            finally:
                library.freecon(context)
        return result
    finally:
        library.selabel_close(handle)
