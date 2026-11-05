#!/usr/bin/env python3
"""Run inside native AIB: native build root, ARM64 target pipelines."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tempfile


def cross_manifest(target, native):
    result = copy.deepcopy(target)
    builds = [p for p in native["pipelines"] if p["name"] == "build"]
    if len(builds) != 1 or sum(p["name"] == "build" for p in result["pipelines"]) != 1:
        raise ValueError("Expected one named build pipeline in each AIB manifest")
    for index, pipeline in enumerate(result["pipelines"]):
        if pipeline["name"] == "build":
            result["pipelines"][index] = copy.deepcopy(builds[0])
        else:
            for stage in pipeline.get("stages", []):
                if stage["type"] == "org.osbuild.rpm":
                    stage.setdefault("options", {})["ignorearch"] = True
    for kind, source in native.get("sources", {}).items():
        dest = result.setdefault("sources", {}).setdefault(kind, copy.deepcopy(source))
        if {k: v for k, v in dest.items() if k != "items"} != {k: v for k, v in source.items() if k != "items"}:
            raise ValueError(f"Incompatible source options: {kind}")
        for digest, item in source.get("items", {}).items():
            if digest in dest["items"] and dest["items"][digest] != item:
                # Noarch RPMs have identical content at different arch repository URLs.
                if kind == "org.osbuild.curl" and re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
                    continue
                raise ValueError(f"Conflicting source: {digest}")
            dest["items"][digest] = copy.deepcopy(item)
    return result



def normal_rt_manifest(manifest, uki_stage_sha256=None):
    """Apply the existing Apollo normal-RT policy before AIB creates the UKI."""
    result = copy.deepcopy(manifest)
    diagnostics = {"slub_debug=FPZ", "rcupdate.rcu_expedited=1", "rcupdate.rcu_normal_after_boot=0"}
    count = 0
    for pipeline in result["pipelines"]:
        for stage in pipeline.get("stages", []):
            if stage["type"] == "org.osbuild-auto.aboot.update":
                if not uki_stage_sha256:
                    raise ValueError("Apollo UKI stage implementation hash is required")
                stage["type"] = "org.osbuild.apollo.uki"
                stage["options"]["implementation_sha256"] = uki_stage_sha256
            if stage["type"] == "org.osbuild.kernel-cmdline":
                options = stage["options"]
                options["kernel_opts"] = " ".join(word for word in options["kernel_opts"].split() if word not in diagnostics)
                count += 1
    if count != 1:
        raise ValueError("Apollo image requires exactly one kernel cmdline stage")
    return result


def native_tools_policy():
    # QM stages copy the vendor SELinux policy from the build root.
    # Keep its package dependency while excluding target kernel/application policy.
    return {"name": "native-tools", "content": {"rpms": []},
            "qm": {"content": {"rpms": []}}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--rootless", action="store_true")
    args = parser.parse_args()
    if args.rootless:
        # The native build pipeline labels its tree before any VM is available.
        with tempfile.NamedTemporaryFile(dir="/work", prefix=".selinux-probe-") as probe:
            try:
                os.setxattr(probe.name, "security.selinux", b"system_u:object_r:container_file_t:s0")
            except OSError as error:
                raise RuntimeError("Rootless native AIB requires security.selinux xattrs on its build store; "
                                   "this host denies them. Use rootful mode or a complete builder VM; "
                                   "target SELinux labeling will not be skipped.") from error
    def run(command):
        print("[native-build] " + " ".join(map(str, command)), flush=True)
        subprocess.run(command, check=True)
    apollo = Path("/apollo-kernel-repo/repodata/repomd.xml").exists()
    native_manifest = Path("/work/native-tools.aib.yml")
    native_manifest.write_text(json.dumps(native_tools_policy()) + "\n")
    if apollo and (args.manifest.parent / "payload/Containerfile").exists():
        run(["podman", "build", "--network=none", "--pull=never", "--timestamp", "0", "--arch", "arm64",
             "-t", "localhost/apollo-workload:1", str(args.manifest.parent / "payload")])
    aib = "/src/bin/aib-dev" if apollo else "aib-dev"
    for label, arch in (("target", "aarch64"), ("native", platform.machine())):
        source = native_manifest if apollo and label == "native" else args.manifest
        target_name = "apollo-qvp" if apollo and label == "target" else "qemu"
        run([aib, "build", "--dry-run", "--no-sudo", "--distro", "autosd10-sig",
             "--target", target_name, "--arch", arch, "--build-dir", "/work/cache",
             "--osbuild-manifest", f"/work/{label}.osbuild.json", str(source), "/work/unused.qcow2"])
    target = json.loads(Path("/work/target.osbuild.json").read_text())
    native = json.loads(Path("/work/native.osbuild.json").read_text())
    merged = Path("/work/minimal_qm.osbuild.json")
    combined = cross_manifest(target, native)
    if apollo:
        combined = normal_rt_manifest(combined, hashlib.sha256(Path("/osbuild_apollo_uki.py").read_bytes()).hexdigest())
    merged.write_text(json.dumps(combined, indent=2) + "\n")
    command = ["osbuild", "--store", "/work/cache/osbuild-store", "--output-directory", "/work/export",
               "--cache-max-size", "10GB", "--export", "image"]
    if apollo:
        libdir = Path("/work/apollo-osbuild-lib")
        shutil.copytree("/usr/lib/osbuild", libdir, dirs_exist_ok=True)
        shutil.copy2("/osbuild_apollo_uki.py", libdir / "stages/org.osbuild.apollo.uki")
        command += ["--libdir", str(libdir)]
    for checkpoint in ("build", "qm_rootfs_base", "rootfs", "image-tree", "org.osbuild.rpm"):
        command += ["--checkpoint", checkpoint]
    if args.rootless:
        command += ["--in-vm", "image"]
    run(command + [str(merged)])
    run(["qemu-img", "convert", "-f", "raw", "-O", "qcow2", "/work/export/image/disk.img",
         "/work/minimal_qm.aarch64.qcow2"])


if __name__ == "__main__":
    main()
