#!/usr/bin/env python3
"""Build ARM64 AutoSD using native AIB/OSBuild and target-only qemu-user."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import uuid

from build_minimal_qm import sha256
from download_builder import native_architecture


def podman(rootless=False):
    return ([] if rootless or os.geteuid() == 0 else ["sudo", "-n"]) + ["podman"]


def preflight(rootless=False):
    result = subprocess.run(podman(rootless) + ["info", "--format", "{{.Host.Security.Rootless}}"],
                            capture_output=True, text=True, timeout=30)
    if result.returncode or result.stdout.strip() != ("true" if rootless else "false"):
        raise RuntimeError(("Rootless Podman required. " if rootless else "Rootful Podman required (sudo -n podman). ")
                           + result.stderr.strip())


def build(args):
    if not re.fullmatch(r"quay\.io/centos-sig-automotive/automotive-image-builder@sha256:[0-9a-f]{64}", args.image):
        raise ValueError("Builder must be an official immutable AIB digest")
    work = args.work_dir.absolute()
    manifest = args.manifest.absolute()
    if work.exists() or not manifest.is_file():
        raise ValueError("Build directory must be new and manifest must exist")
    rootless = args.rootless
    architecture = native_architecture()
    container_platform = "linux/" + architecture
    preflight(rootless)
    pm = podman(rootless)
    def run(command):
        subprocess.run(command, check=True, timeout=args.timeout)
    if args.archive:
        run(pm + ["load", "--input", str(args.archive.absolute())])
        run(pm + ["image", "exists", args.image])
    else:
        run(pm + ["pull", "--platform", container_platform, args.image])
    arch = subprocess.check_output(pm + ["image", "inspect", "--format", "{{.Architecture}}", args.image], text=True).strip()
    if arch != architecture:
        raise ValueError(f"Expected native {architecture} builder, got {arch}; select a native AIB digest")
    work.mkdir(parents=True)
    (work / "cache").mkdir()
    (work / "containers").mkdir()
    name = "apollo-aib-" + uuid.uuid4().hex
    # Rootless --privileged stays within the invoking user's namespace.
    command = pm + ["run", "--rm", "--name", name, "--pull=never",
        "--platform", container_platform, "--privileged", "--security-opt", "label=disable",
        "-v", f"{work}:/work", "-v", f"{work / 'containers'}:/var/lib/containers/storage",
        "-v", f"{manifest.parent}:/manifest:ro", "--workdir", "/work",
        "-v", f"{Path(__file__).with_name('native_build.py').resolve()}:/native_build.py:ro",
        "--entrypoint", "/bin/bash", args.image, "-ec",
        'uname -m; aib-dev --version; '
        'unshare --mount --pid --fork /bin/true; '
        'if ! bwrap --unshare-pid --ro-bind / / /bin/true; then '
        'echo "AIB blocked: native bwrap namespace probe failed" >&2; exit 1; fi; '
        'mkdir -p /tmp/apollo-mount; mount -t tmpfs tmpfs /tmp/apollo-mount; '
        'umount /tmp/apollo-mount; podman info >/dev/null; '
        'exec python3 /native_build.py '
        + ('--rootless ' if rootless else '')
        + '"$1"', "aib-build", "/manifest/" + manifest.name]
    if getattr(args, "cache_dir", None):
        cache = args.cache_dir.absolute()
        cache.mkdir(parents=True, exist_ok=True)
        command[command.index("--entrypoint"):command.index("--entrypoint")] = ["-v", f"{cache}:/work/cache"]
    if getattr(args, "rpm_repo", None):
        repo = args.rpm_repo.resolve()
        if not (repo / "repodata/repomd.xml").is_file():
            raise ValueError("RPM repository metadata missing")
        aib_source = Path(__file__).resolve().parents[2] / "autosd/automotive-image-builder"
        command[command.index("--entrypoint"):command.index("--entrypoint")] = [
            "-v", f"{repo}:/apollo-kernel-repo:ro", "-v", f"{aib_source}:/src:ro",
            "-v", f"{Path(__file__).with_name('osbuild_apollo_uki.py').resolve()}:/osbuild_apollo_uki.py:ro"]
    if not rootless:
        # loop-control can allocate devices after Podman populated its private /dev.
        command[command.index("--entrypoint"):command.index("--entrypoint")] = ["-v", "/dev:/dev"]
    try:
        run(command)
    finally:
        # Only this invocation's container may survive a timeout/interruption.
        subprocess.run(pm + ["rm", "--force", "--ignore", name], timeout=60, check=True)
    for filename in ("minimal_qm.aarch64.qcow2", "minimal_qm.osbuild.json"):
        path = work / filename
        if not path.is_file():
            raise RuntimeError(f"AIB did not produce {path}")
        if not rootless and os.geteuid() != 0:
            run(["sudo", "-n", "chown", f"{os.getuid()}:{os.getgid()}", str(path)])
    image = work / "minimal_qm.aarch64.qcow2"
    (work / "minimal_qm.sha256").write_text(sha256(image) + "  " + image.name + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--rpm-repo", type=Path)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=7200)
    parser.add_argument("--rootless", action="store_true", help="experimental rootless/VM build; no sudo; requires SELinux xattrs")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
