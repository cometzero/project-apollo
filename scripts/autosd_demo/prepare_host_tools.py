#!/usr/bin/env python3
"""Recreate rootless guestfish tooling; never depend on an old build directory.

Host libguestfs/supermin/QEMU and installed kernel modules are prerequisites.
APT verifies downloaded package indexes/checksums; no package is installed here.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess


def run(command, **kwargs):
    return subprocess.run(command, check=True, text=True, capture_output=True, **kwargs)


def installed_version(package):
    result = run(["dpkg-query", "-W", "-f=${db:Status-Status} ${Version}", package])
    status, version = result.stdout.strip().split(maxsplit=1)
    if status != "installed":
        raise RuntimeError(f"Required host package is not installed: {package}")
    return version


def extract_package(package, output):
    # A separate directory prevents stale/unrelated .debs from being extracted.
    destination = output / "packages" / package.split("=", 1)[0]
    destination.mkdir(parents=True, exist_ok=True)
    run(["apt-get", "download", package], cwd=destination, timeout=600)
    packages = list(destination.glob("*.deb"))
    if len(packages) != 1:
        raise RuntimeError(f"Expected one downloaded package in {destination}")
    run(["dpkg-deb", "-x", str(packages[0]), str(output / "root")])
    with packages[0].open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"package": package, "file": str(packages[0]), "sha256": digest}


def kernel_candidates():
    return sorted((p for p in Path("/lib/modules").glob("*")
                   if p.is_dir() and (p / "modules.dep").exists()),
                  key=lambda p: tuple((0, int(x)) if x.isdigit() else (1, x)
                                      for x in re.split(r"(\d+)", p.name)),
                  reverse=True)


def prepare(output, smoke_image, requested_kernel=None):
    output = output.resolve()
    smoke_image = smoke_image.resolve(strict=True)
    # Fail before downloads with actionable prerequisites, not a partial private
    # dependency installation whose supermin appliance would use host metadata.
    for binary in ("apt-get", "dpkg-deb", "dpkg-query", "supermin"):
        if not shutil.which(binary):
            raise RuntimeError("Install host prerequisites: sudo apt-get install "
                               "libguestfs-tools supermin qemu-system-x86 linux-image-generic")
    for package in ("supermin", "qemu-system-x86"):
        installed_version(package)
    if not list(Path("/usr/lib").glob("**/guestfs/supermin.d")):
        raise RuntimeError("Install host libguestfs-tools (libguestfs appliance missing)")
    candidates = kernel_candidates()
    if requested_kernel:
        candidates = [p for p in candidates if p.name == requested_kernel]
    if not candidates:
        raise RuntimeError("Installed kernel modules missing; install linux-image-generic")
    kernel_modules = candidates[0]
    output.mkdir(parents=True, exist_ok=True)
    packages = []
    binary = shutil.which("guestfish")
    if not binary:
        packages.append(extract_package("guestfish", output))
        binary = str(output / "root/usr/bin/guestfish")
    run([binary, "--version"], timeout=30)
    kernel = Path("/boot") / ("vmlinuz-" + kernel_modules.name)
    if not os.access(kernel, os.R_OK):
        package = "linux-image-" + kernel_modules.name
        packages.append(extract_package(package + "=" + installed_version(package), output))
        kernel = output / "root/boot" / kernel.name
    if not kernel.is_file() or not os.access(kernel, os.R_OK):
        raise RuntimeError(f"No readable appliance kernel: {kernel}")
    environment = {"LIBGUESTFS_BACKEND": "direct", "SUPERMIN_KERNEL": str(kernel),
                   "SUPERMIN_MODULES": str(kernel_modules)}
    command = [binary, "--ro", "-a", str(smoke_image), "run", ":", "list-filesystems"]
    result = run(command, env={**os.environ, **environment}, timeout=300)
    (output / "guestfish-smoke.log").write_text(result.stdout + result.stderr)
    if not result.stdout.strip():
        raise RuntimeError("Guestfish appliance found no filesystems in smoke image")
    receipt = {"status": "PASS", "guestfish": binary, "environment": environment,
               "packages": packages, "smoke_image": str(smoke_image),
               "smoke_command": command}
    (output / "environment.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("build/autosd/host-tools"))
    parser.add_argument("--smoke-image", type=Path, required=True,
                        help="Existing raw/qcow2 image; opened read-only for appliance validation")
    parser.add_argument("--kernel-release", help="Installed host kernel module release to use")
    args = parser.parse_args(argv)
    try:
        receipt = prepare(args.output, args.smoke_image, args.kernel_release)
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        detail = getattr(error, "stderr", None) or str(error)
        parser.exit(1, f"Host tool preparation failed: {detail}\n")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
