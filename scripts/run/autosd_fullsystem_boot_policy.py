"""Conservative boot policy for the launcher's private AutoSD disk.

Uploaded and executed over the existing bounded SSH provisioning transport.
No connections are deleted, no address is invented, and no live mount is changed.
"""
import json
import os
from pathlib import Path
import re
import shlex
import stat
import subprocess
import tempfile


NM_PATH = "etc/NetworkManager/conf.d/90-apollo-rpmsg-no-auto-default.conf"
EFI_PATH = "etc/systemd/system/boot-efi.mount.d/90-apollo-private.conf"
TRACE_RULE = "98-trace-cmd.rules"
TRACE_MARKER = "apollo-trace-cmd-flightrecorder"
TRACE_UNIT_PATH = "etc/systemd/system/trace-cmd.service.d/90-apollo-runtime-marker.conf"
TRACE_VENDOR_RULE = ('SUBSYSTEM=="module", ACTION=="add", '
                     'PROGRAM="/usr/bin/systemctl is-active trace-cmd.service", '
                     'PROGRAM="/usr/bin/systemctl reload trace-cmd.service"')
TRACE_UNIT = """# Managed by Apollo private AutoSD full-system provisioning.
# RemainAfterExit keeps this directory for the active flightrecorder lifetime.
[Service]
RuntimeDirectory=apollo-trace-cmd-flightrecorder
RuntimeDirectoryMode=0755
"""
NM_CONFIG = """# Managed by Apollo private AutoSD full-system provisioning.
# ethsi1 is the RPMsg transport, not an unconfigured external DHCP network.
# Explicit user connection profiles remain eligible and unchanged.
[main]
no-auto-default+=interface-name:ethsi1
"""


def restrict_efi_mount(text):
    """Restrict only vfat /boot/efi; retain comments and stricter user masks."""
    output = []
    matches = 0
    for line in text.splitlines(keepends=True):
        if not line.strip() or line.lstrip().startswith("#"):
            output.append(line)
            continue
        fields = list(re.finditer(r"\S+", line))
        if len(fields) < 4 or fields[1].group() != "/boot/efi":
            output.append(line)
            continue
        matches += 1
        if matches > 1:
            raise ValueError("Multiple /boot/efi fstab entries; refusing ambiguous policy")
        if fields[2].group() != "vfat":
            raise ValueError("/boot/efi is not vfat; refusing to change mount policy")
        options = fields[3].group().split(",")
        found = False
        for index, option in enumerate(options):
            key, _, value = option.partition("=")
            if key not in {"umask", "fmask", "dmask"}:
                continue
            if not re.fullmatch(r"[0-7]{1,4}", value):
                raise ValueError("Invalid EFI mount permission mask")
            options[index] = key + "=" + format(int(value, 8) | 0o077, "04o")
            found |= key == "umask"
        if not found:
            options.append("umask=0077")
        field = fields[3]
        output.append(line[:field.start()] + ",".join(options) + line[field.end():])
    return "".join(output), matches


def _write(path, content):
    if path.is_symlink():
        raise ValueError("Refusing symlink policy target: " + str(path))
    if path.exists() and path.read_text() == content:
        return False
    metadata = path.stat() if path.exists() else None
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".apollo-policy-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(name, stat.S_IMODE(metadata.st_mode) if metadata else 0o644)
        if metadata and os.geteuid() == 0:
            os.chown(name, metadata.st_uid, metadata.st_gid)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return True


def trace_policy_files(root):
    """Recognize the vendor contract; never replace a user's rule or unit."""
    root = Path(root)
    vendor = root / "usr/lib/udev/rules.d" / TRACE_RULE
    unit = root / "usr/lib/systemd/system/trace-cmd.service"
    if not vendor.is_file() or not unit.is_file():
        return {}, "SKIP-vendor-rule-or-service-missing"
    source = vendor.read_text()
    lines = [line for line in source.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if lines != [TRACE_VENDOR_RULE]:
        return {}, "SKIP-unrecognized-vendor-rule"
    service = unit.read_text()
    if ("Type=oneshot" not in service.splitlines()
            or "RemainAfterExit=yes" not in service.splitlines()):
        return {}, "SKIP-unrecognized-service-lifecycle"
    override = root / "etc/systemd/system/trace-cmd.service"
    if override.exists() or override.is_symlink():
        return {}, "SKIP-user-service-override"
    for dropin in (root / "etc/systemd/system/trace-cmd.service.d").glob("*.conf"):
        if dropin != root / TRACE_UNIT_PATH:
            return {}, "SKIP-user-service-dropin"
    rule_path = "etc/udev/rules.d/" + TRACE_RULE
    guarded = source.replace(TRACE_VENDOR_RULE,
                             'TEST=="/run/' + TRACE_MARKER + '", ' + TRACE_VENDOR_RULE)
    files = {rule_path: guarded, TRACE_UNIT_PATH: TRACE_UNIT}
    for relative, content in files.items():
        path = root / relative
        if path.is_symlink() or (path.exists() and path.read_text() != content):
            return {}, "SKIP-user-trace-policy-conflict"
    return files, "guarded-next-boot; active-flightrecorder-reload-preserved"


def apply_policy(root, efi_mount=None):
    root = Path(root)
    fstab = root / "etc/fstab"
    text = fstab.read_text() if fstab.exists() else ""
    updated, count = restrict_efi_mount(text)
    dropin = None
    if not count and efi_mount is not None:
        if efi_mount.get("Where") != "/boot/efi" or efi_mount.get("Type") != "vfat":
            raise ValueError("EFI mount identity is not /boot/efi vfat")
        options = efi_mount.get("Options", "defaults")
        if not options or re.search(r"\s|%", options):
            raise ValueError("Invalid EFI mount options")
        restricted, _ = restrict_efi_mount("ESP /boot/efi vfat " + options + " 0 0\n")
        dropin = "# Managed by Apollo private AutoSD full-system provisioning.\n[Mount]\nOptions=" + restricted.split()[3] + "\n"
        destination = root / EFI_PATH
        if destination.exists() and not destination.read_text().startswith("# Managed by Apollo private AutoSD"):
            raise ValueError("Existing EFI policy is user-owned; preserve it")
    nm = root / NM_PATH
    # Do not overwrite a user-owned file that happens to use our reserved name.
    if nm.exists() and nm.read_text() != NM_CONFIG:
        raise ValueError("Existing Apollo NetworkManager policy differs; preserve it")
    if fstab.is_symlink() or nm.is_symlink():
        raise ValueError("Refusing symlink policy target")
    changed = []
    if count and _write(fstab, updated):
        changed.append("/etc/fstab")
    if dropin is not None and _write(root / EFI_PATH, dropin):
        changed.append("/" + EFI_PATH)
    if _write(nm, NM_CONFIG):
        changed.append("/" + NM_PATH)
    trace_files, trace_status = trace_policy_files(root)
    for relative, content in trace_files.items():
        if _write(root / relative, content):
            changed.append("/" + relative)
    return {"status": "PASS", "changed": changed,
            "efi_mount": "restricted-next-boot" if count or dropin is not None else "SKIP-no-mount-description",
            "network": "no-new-auto-default-ethsi1-profiles-next-boot",
            "trace_coldplug": trace_status,
            "existing_profiles": "preserved; existing DHCP profiles may still activate"}


def service_files():
    return {"apollo-boot-policy.py": Path(__file__).read_text()}


def install_commands(remote):
    q = shlex.quote
    return ["python3 " + q(remote + "/apollo-boot-policy.py") + " --apply",
            "if test -f /etc/fstab; then restorecon /etc/fstab; fi",
            "restorecon /" + NM_PATH,
            "if test -d /etc/systemd/system/boot-efi.mount.d; then restorecon -R /etc/systemd/system/boot-efi.mount.d; fi",
            "if test -f /etc/udev/rules.d/98-trace-cmd.rules; then restorecon /etc/udev/rules.d/98-trace-cmd.rules; fi",
            "if test -d /etc/systemd/system/trace-cmd.service.d; then restorecon -R /etc/systemd/system/trace-cmd.service.d; fi",
            "printf '%s\\n' AUTOSD_BOOT_POLICY_INSTALLED_REBOOT_REQUIRED"]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", required=True)
    parser.parse_args()
    if os.geteuid() != 0:
        raise SystemExit("Private guest policy requires root")
    os_release = Path("/etc/os-release").read_text()
    if not re.search(r'^ID=["\']?autosd["\']?$', os_release, re.MULTILINE):
        raise SystemExit("Private guest policy requires AutoSD")
    properties = subprocess.check_output(
        ["systemctl", "show", "boot-efi.mount", "--property=Where,Type,Options"],
        text=True, timeout=30)
    mount = dict(line.split("=", 1) for line in properties.splitlines() if "=" in line)
    print(json.dumps(apply_policy("/", mount), sort_keys=True))
