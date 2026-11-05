#!/usr/bin/env python3
"""Recreate disposable AutoSD inputs, then build/customize/verify the image."""
import json
import os
from pathlib import Path
import subprocess
import sys
import yaml

import build_minimal_qm as pipeline
from download_nightly import fetch
from download_builder import parse_reference, native_architecture

ROOT = pipeline.ROOT


def configuration(path):
    config = json.loads(path.read_text())
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported AutoSD configuration schema")
    if not isinstance(config.get("customize"), bool):
        raise ValueError("customize must be a boolean")
    if not isinstance(config.get("aib_manifest"), str):
        raise ValueError("aib_manifest must name a source manifest")
    return config


def parser():
    p = pipeline.parser()
    p.description = __doc__
    p.set_defaults(aib_manifest=None, customize=None)
    p.add_argument("--config", type=Path, default=ROOT / "autosd/config/automotive.json")
    p.add_argument("--rpm-build-dir", type=Path, help="Yocto kernel RPM packaging cache/output directory")
    p.add_argument("--kernel-artifacts", type=Path, help="matching Yocto kernel-build-artifacts directory")
    p.add_argument("--aib-cache-dir", type=Path, help="reuse OSBuild/package cache across new work directories")
    p.add_argument("--build-only", action="store_true", help="produce image without QBox validation")
    p.add_argument("--cache-dir", type=Path, help="disposable inputs; default BUILD_DIR/autosd")
    p.add_argument("--prepare-inputs-only", action="store_true", help="download/build inputs without starting a VM")
    p.add_argument("--minimal", action="store_true", help="select minimal_qm.aib.yml")
    p.add_argument("--nightly-build-id", help="pin an official nightly build instead of latest")
    p.add_argument("--builder-reference", help="official AIB tag/digest to download; recorded as immutable digest")
    return p


def setup(args):
    config = configuration(args.config)
    if config.get("kernel_input", "yocto-deploy") != "yocto-deploy":
        raise ValueError("Supported kernel input is yocto-deploy; kernel compilation belongs to Yocto")
    args.build_dir = args.build_dir.absolute()
    args.deploy_dir = (args.deploy_dir or args.build_dir / "tmp_baremetal/deploy/images/apollo-qvp").absolute()
    args.kernel_artifacts = (args.kernel_artifacts or args.build_dir / "tmp_baremetal/work-shared/apollo-qvp/kernel-build-artifacts").absolute()
    cache = (args.cache_dir or args.build_dir / "autosd").absolute()
    if args.minimal and args.aib_manifest:
        raise ValueError("--minimal and --aib-manifest cannot be combined")
    minimal = ROOT / "autosd/sig-docs/demos/minimal_qm/minimal_qm.aib.yml"
    args.aib_manifest = minimal if args.minimal else args.aib_manifest or ROOT / config["aib_manifest"]
    if not args.aib_manifest.is_file():
        raise ValueError(f"AIB source manifest missing: {args.aib_manifest}")
    source = yaml.safe_load(args.aib_manifest.read_text())
    name = source.get("name") if isinstance(source, dict) else None
    if name not in ("apollo-automotive-scenario", "minimal_qm"):
        raise ValueError("Supported AIB profiles are apollo-automotive-scenario and minimal_qm")
    if args.customize is True and name == "minimal_qm":
        raise ValueError("--customize conflicts with the selected minimal_qm manifest")
    args.customize = name == "apollo-automotive-scenario"
    if args.crun_binary and not args.customize:
        raise ValueError("--crun-binary requires the Automotive profile")
    if args.crun_binary and not args.crun_binary.is_file() and not args.dry_run:
        raise ValueError(f"Explicit --crun-binary missing: {args.crun_binary}")
    args.nightly_build_id = args.nightly_build_id or config.get("nightly_build_id")
    if args.nightly_build_id:
        raise ValueError("Source builds do not consume nightly images; use the separate nightly import tools")
    if args.uki or args.modules:
        raise ValueError("AIB builds its UKI from Yocto kernel RPMs; select inputs with --deploy-dir/--kernel-artifacts, not --uki/--modules")
    if args.cc != "aarch64-linux-gnu-gcc":
        raise ValueError("Small application payloads use the AArch64 container GCC; --cc is a legacy option")
    args.builder_reference = args.builder_reference or config["builder_reference"]
    parse_reference(args.builder_reference)
    if not args.aib_manifest.is_file():
        raise ValueError(f"AIB source manifest missing: {args.aib_manifest}; initialize autosd submodules")
    if args.image and (args.builder_archive or args.builder_image):
        raise ValueError("--image cannot be combined with builder inputs")
    if args.builder_archive and not args.builder_image:
        raise ValueError("--builder-archive requires --builder-image")
    args.output = args.output or cache / ("automotive" if args.customize else "minimal-qm")
    args.work_dir = args.work_dir or cache / ("minimal-qm-build-" +
        pipeline.datetime.now(pipeline.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ"))
    return cache


def run(command, environment=None):
    print("[prepare-input] " + " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), cwd=ROOT, check=True,
                   env={**os.environ, **(environment or {})})


def checked_builder(cache, reference):
    architecture = native_architecture()
    directory = cache / ("builder-" + architecture)
    receipt_path = directory / "metadata.json"
    if not receipt_path.exists():
        run([sys.executable, ROOT / "scripts/autosd_demo/download_builder.py",
             "--reference", reference, "--output", directory])
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("architecture") != architecture:
        raise ValueError("Builder cache architecture differs from host; use a new --cache-dir")
    if receipt.get("requested_reference") != reference:
        raise ValueError("Builder reference changed; use a new --cache-dir")
    archive = Path(receipt["archive"])
    if not archive.is_file() or pipeline.sha256(archive) != receipt["sha256"]:
        raise ValueError("Builder archive missing/corrupt; use a new --cache-dir")
    return archive, receipt["builder_reference"]


def check_crun(directory):
    receipt = json.loads((directory / "provenance.json").read_text())
    runtime = ROOT / "autosd/customization/runtime"
    for name, repo in (("source_commit", ROOT / "autosd/crun"),
                       ("libocispec_commit", ROOT / "autosd/crun/libocispec")):
        head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
        if receipt[name] != head:
            raise ValueError("crun source changed; use a new --cache-dir")
    files = [(directory / "crun", receipt["crun_sha256"]),
             (runtime / "crun-cgroup-mount-label.patch", receipt["patch_sha256"]),
             (directory / receipt["base_image_archive"], receipt["base_image_archive_sha256"])]
    scripts = receipt["scripts_sha256"]
    for name in ("build-crun.sh", "build-crun-cross.sh", "crun-provenance.py", "resolve-centos-image.py"):
        files.append((runtime / name, scripts[name]))
    for path, digest in files:
        if not path.is_file() or pipeline.sha256(path) != digest:
            raise ValueError(f"crun inputs/output changed: {path}; use a new --cache-dir")


def prepare(args, cache):
    py = sys.executable
    # Download first: guestfish's appliance is tested against this read-only disk.
    nightly = None
    if not args.image and not args.manifest:
        nightly = fetch(cache / "downloads/nightly", args.nightly_build_id)
        smoke = Path(nightly["image"])
    elif args.image:
        smoke = args.image.absolute()
    else:
        smoke = Path(json.loads(args.manifest.read_text())["rootfs"])
    tools = cache / "host-tools"
    if args.guestfish == "guestfish":
        run([py, ROOT / "scripts/autosd_demo/prepare_host_tools.py",
             "--output", tools, "--smoke-image", smoke])
        host = json.loads((tools / "environment.json").read_text())
        if host["status"] != "PASS":
            raise ValueError("Host tool smoke failed")
        args.guestfish = host["guestfish"]
        os.environ.update(host["environment"])
    if not args.image and not args.builder_archive:
        args.builder_archive, args.builder_image = checked_builder(
            cache, args.builder_image or args.builder_reference)
    if args.customize and args.crun_binary and not args.crun_binary.is_file():
        raise ValueError(f"Explicit --crun-binary missing: {args.crun_binary}")
    if args.customize and args.crun_binary == cache / "crun/crun":
        check_crun(cache / "crun")
    receipt = {"config": str(args.config.absolute()),
               "config_sha256": pipeline.sha256(args.config),
               "manifest": str(args.manifest) if args.manifest else None,
               "builder_archive": str(args.builder_archive) if args.builder_archive else None,
               "builder_image": args.builder_image,
               "crun_binary": str(args.crun_binary) if args.customize and args.crun_binary else None,
               "guestfish": args.guestfish,
               "environment": {k: os.environ[k] for k in
                   ("SUPERMIN_KERNEL", "SUPERMIN_MODULES", "LIBGUESTFS_BACKEND") if k in os.environ}}
    cache.mkdir(parents=True, exist_ok=True)
    (cache / "inputs.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main(argv=None):
    args = parser().parse_args(argv)
    cache = setup(args)
    if args.dry_run:
        print(json.dumps({"config": str(args.config), "cache_dir": str(cache),
            "aib_manifest": str(args.aib_manifest), "nightly_build_id": args.nightly_build_id,
            "builder_reference": args.builder_reference, "customize": args.customize,
            "crun_binary": str(args.crun_binary) if args.customize and args.crun_binary else None,
            "builder_mode": "rootless-vm" if args.rootless else "rootful-user",
            "stages": ["package existing Yocto kernel/modules as RPMs", "AArch64 application/PFDI payloads", "native AIB inputs",
                       "resolve selected manifest with local RPMs", "native AIB complete image",
                       "QBox read-only readiness and shutdown validation unless --build-only"],
            "kernel_input": "yocto-deploy", "deploy_dir": str(args.deploy_dir),
            "kernel_artifacts": str(args.kernel_artifacts),
            "external_prerequisites": "matching Yocto kernel/modules/artifacts, Apollo firmware/providers, AArch64 binfmt, documented host packages"}, indent=2))
        return 0
    # Refuse known output collisions before lengthy downloads/builds.
    if not args.prepare_inputs_only:
        for path in (args.output, args.work_dir, args.qbox_out_dir):
            if path is not None and path.exists():
                raise ValueError(f"Output exists: {path}; choose new --output/--work-dir")
    if not args.image and not args.prepare_inputs_only:
        from builder_podman import preflight
        preflight(args.rootless)
    if args.image or args.manifest:
        raise ValueError("Existing image imports use prepare_autosd.py; source builds require an AIB manifest")
    from automotive_build import run as build_source_image
    return build_source_image(args, cache)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
