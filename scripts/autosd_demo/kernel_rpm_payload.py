#!/usr/bin/env python3
"""Container-side implementation for kernel_rpm_build.sh (not a kernel build)."""

import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile


RELEASE = "6.18.5-rt3-yocto-preempt-rt"
OUT = Path("/output")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(args, **kwargs):
    return subprocess.run(args, check=True, text=True, **kwargs)


def audit_payload(rpm, payload):
    """Verify RPM file digests against the unmodified staging payload."""
    file_hashes = run(["rpm", "-qp", "--qf", "[%{FILENAMES} %{FILEDIGESTS}\\n]", str(rpm)],
                      stdout=subprocess.PIPE).stdout
    (OUT / "rpm-file-digests.txt").write_text(file_hashes)
    for line in file_hashes.splitlines():
        fields = line.split()
        if len(fields) == 2 and fields[1] != "(none)":
            if digest(payload / fields[0].lstrip("/")) != fields[1]:
                raise ValueError(f"RPM payload digest mismatch: {fields[0]}")


def main():
    inputs = {"Image": Path("/inputs/deploy/Image"),
              "modules": Path("/inputs/deploy/modules-apollo-qvp.tgz"),
              "config": Path("/inputs/artifacts/.config"),
              "System.map": Path("/inputs/artifacts") / f"System.map-{RELEASE}"}
    hashes = {name: digest(path) for name, path in inputs.items()}
    image = inputs["Image"].read_bytes()
    releases = set(re.findall(rb"Linux version ([^ ]+) ", image))
    if releases != {RELEASE.encode()} or image[56:60] != b"ARM\x64":
        raise ValueError(f"Unexpected Image architecture/release: {releases}")
    marker = image.find(b"IKCFG_ST")
    end = image.find(b"IKCFG_ED", marker + 8)
    if marker < 0 or end < 0:
        raise ValueError("Image has no embedded config to authenticate build configuration")
    embedded_config = gzip.decompress(image[marker + 8:end])
    exported_config = inputs["config"].read_bytes()
    # Yocto's exported build-artifact config can drop this compiler probe.
    if embedded_config != exported_config and embedded_config.replace(b"CONFIG_CC_CAN_LINK=y\n", b"") != exported_config:
        raise ValueError("Build config does not match deployed Image IKCONFIG")
    payload = OUT / "payload"
    payload.mkdir()
    modules = payload / "usr/lib/modules" / RELEASE
    modules.mkdir(parents=True)
    prefix = PurePosixPath("lib/modules") / RELEASE
    with tarfile.open(inputs["modules"], "r:gz") as archive:
        members = archive.getmembers()
        epoch = int(max(member.mtime for member in members))
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or not (member.isfile() or member.isdir()):
                raise ValueError(f"Unsafe module archive member: {member.name}")
            if member.isdir() and path in (PurePosixPath("lib"), PurePosixPath("lib/modules")):
                continue
            if not path.is_relative_to(prefix):
                raise ValueError(f"Unexpected module release/path: {member.name}")
            destination = modules / path.relative_to(prefix)
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as source, destination.open("xb") as target:
                    shutil.copyfileobj(source, target)
                destination.chmod(0o644)
    module_files = sorted(modules.rglob("*.ko"))
    if not module_files:
        raise ValueError("Empty module archive")
    for path in module_files:
        vermagic = run(["modinfo", "-F", "vermagic", str(path)], stdout=subprocess.PIPE).stdout.strip()
        if not vermagic.startswith(RELEASE + " "):
            raise ValueError(f"Module release mismatch: {path}: {vermagic}")
        header = path.read_bytes()[:20]
        if header[:5] != b"\x7fELF\x02" or header[18:20] != b"\xb7\x00":
            raise ValueError(f"Non-AArch64 module: {path}")
    for name in ("modules.builtin", "modules.builtin.modinfo", "modules.order"):
        if not (modules / name).is_file():
            raise ValueError(f"Missing module metadata: {name}")
    for source, target in (("Image", "vmlinuz"), ("System.map", "System.map")):
        shutil.copyfile(inputs[source], modules / target)
    (modules / "config").write_bytes(embedded_config)
    # kmod expects /lib/modules; this symlink is staging-only, not RPM payload.
    (payload / "lib").symlink_to("usr/lib")
    depmod = run(["depmod", "-b", str(payload), "-e", "-F", str(modules / "System.map"), RELEASE],
                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (OUT / "depmod.log").write_text(depmod.stdout + depmod.stderr)
    if "unknown symbol" in depmod.stderr:
        raise ValueError("Module symbols do not match supplied System.map; see depmod.log")
    (payload / "lib").unlink()
    spec = OUT / "kernel-apollo.spec"
    spec.write_text(f"""%global debug_package %{{nil}}
%global __os_install_post %{{nil}}
%global _build_id_links none
%global use_source_date_epoch_as_buildtime 1
%global clamp_mtime_to_source_date_epoch 1
%global _buildhost apollo-repack
Name: kernel-apollo
Version: 6.18.5
Release: 1
Summary: Apollo Yocto kernel binary for AutoSD integration experiments
License: GPL-2.0-only
# --target aarch64 selects RPM architecture without BuildArch host compatibility
# recursion (this is binary repackaging, not execution of target build tools).
AutoReqProv: no
Provides: kernel-uname-r({RELEASE})
Provides: kernel-modules-uname-r({RELEASE})

%description
Unmodified deployed Apollo Image and matching modules. This unsigned package
does not generate initrds, install boot entries, or qualify AutoSD OTA behavior.

%prep
%build
%install
mkdir -p %{{buildroot}}/usr/lib/modules
cp -a /output/payload/usr/lib/modules/{RELEASE} %{{buildroot}}/usr/lib/modules/

%files
%defattr(0644,root,root,0755)
/usr/lib/modules/{RELEASE}
""")
    env = {**os.environ, "SOURCE_DATE_EPOCH": str(epoch)}
    build_command = ["rpmbuild", "-bb", "--target", "aarch64", "--define", "_topdir /output/rpmbuild", str(spec)]
    run(build_command, env=env)
    repo = OUT / "repo"
    repo.mkdir()
    rpm = next((OUT / "rpmbuild/RPMS/aarch64").glob("*.rpm"))
    first_digest = digest(rpm)
    run(build_command, env=env)
    if digest(rpm) != first_digest:
        raise ValueError("Repeated binary RPM build was not reproducible")
    shutil.copyfile(rpm, repo / rpm.name)
    for option, filename in (("--requires", "requires.txt"), ("--provides", "provides.txt"), ("--list", "files.txt")):
        result = run(["rpm", "-qp", option, str(rpm)], stdout=subprocess.PIPE)
        (OUT / filename).write_text(result.stdout)
    audit_payload(rpm, payload)
    run(["createrepo_c", "--revision", str(epoch), "--set-timestamp-to-revision", str(repo)])
    (OUT / "builder-packages.txt").write_text(run(
        ["rpm", "-qa", "--qf", "%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}\\n"],
        stdout=subprocess.PIPE).stdout)
    if {name: digest(path) for name, path in inputs.items()} != hashes:
        raise ValueError("Source changed during repackaging")
    (OUT / "result.json").write_text(json.dumps({
        "status": "PACKAGED_NOT_BOOT_TESTED", "kernel_release": RELEASE,
        "repeat_build_sha256_match": True,
        "rpm_nevra": "kernel-apollo-6.18.5-1.aarch64", "input_sha256": hashes,
        "rpm_sha256": digest(rpm), "module_count": len(module_files),
        "embedded_config_sha256": hashlib.sha256(embedded_config).hexdigest(),
        "source_date_epoch": epoch, "builder": os.environ["APOLLO_BUILDER"],
        "tool_versions": run(["rpm", "--version"], stdout=subprocess.PIPE).stdout.strip(),
        "limitations": ["unsigned local repository", "RPM EVR is not kernel uname_r",
                        "AIB kernel.uname_r override required", "no kernel-install scriptlets",
                        "not a signed vendor kernel or OTA qualification"]}, indent=2) + "\n")


if __name__ == "__main__":
    main()
