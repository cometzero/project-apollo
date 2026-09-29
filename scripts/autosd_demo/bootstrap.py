#!/usr/bin/env python3
"""Recreate disposable AutoSD inputs, then build/customize/verify the image."""
import json
import os
from pathlib import Path
import subprocess
import sys

import build_minimal_qm as pipeline
from download_nightly import fetch
from download_builder import parse_reference

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
    p.add_argument("--config", type=Path, default=ROOT / "autosd/config/minimal-qm.json")
    p.add_argument("--cache-dir", type=Path, help="disposable inputs; default BUILD_DIR/autosd")
    p.add_argument("--prepare-inputs-only", action="store_true", help="download/build inputs without starting a VM")
    p.add_argument("--minimal", action="store_false", dest="customize", help="omit Automotive customization")
    p.add_argument("--nightly-build-id", help="pin an official nightly build instead of latest")
    p.add_argument("--builder-reference", help="official AIB tag/digest to download; recorded as immutable digest")
    return p


def setup(args):
    config = configuration(args.config)
    args.build_dir = args.build_dir.absolute()
    cache = (args.cache_dir or args.build_dir / "autosd").absolute()
    args.aib_manifest = args.aib_manifest or ROOT / config["aib_manifest"]
    if args.customize is None:
        args.customize = config["customize"]
    args.nightly_build_id = args.nightly_build_id or config.get("nightly_build_id")
    args.builder_reference = args.builder_reference or config["builder_reference"]
    parse_reference(args.builder_reference)
    if not args.aib_manifest.is_file():
        raise ValueError(f"AIB source manifest missing: {args.aib_manifest}; initialize autosd submodules")
    if args.image and (args.builder_archive or args.builder_image):
        raise ValueError("--image cannot be combined with builder inputs")
    if args.builder_archive and not args.builder_image:
        raise ValueError("--builder-archive requires --builder-image")
    if args.customize and not args.crun_binary:
        args.crun_binary = cache / "crun/crun"
    args.output = args.output or cache / "demo-minimal-qm-prepared"
    args.work_dir = args.work_dir or cache / ("minimal-qm-build-" +
        pipeline.datetime.now(pipeline.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ"))
    return cache


def run(command, environment=None):
    print("[prepare-input] " + " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), cwd=ROOT, check=True,
                   env={**os.environ, **(environment or {})})


def checked_builder(cache, reference):
    directory = cache / "builder"
    receipt_path = directory / "metadata.json"
    if not receipt_path.exists():
        run([sys.executable, ROOT / "scripts/autosd_demo/download_builder.py",
             "--reference", reference, "--output", directory])
    receipt = json.loads(receipt_path.read_text())
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
    if nightly:
        # Source identity, including the selected nightly URL, remains in download.json.
        prepared = cache / "builder-base"
        args.manifest = prepared / "regular.json"
        if args.manifest.exists():
            data = json.loads(args.manifest.read_text())
            if data.get("source_sha256") != nightly["image_sha256"]:
                raise ValueError("Builder base does not match the downloaded nightly")
            for key in ("rootfs", "initrd"):
                path = Path(data[key])
                if not path.is_file() or pipeline.sha256(path) != data[key + "_sha256"]:
                    raise ValueError("Builder base missing/corrupt; use a new --cache-dir")
        else:
            run([py, ROOT / "scripts/prepare_autosd.py", "--mode", "regular",
                 "--image", smoke, "--output", prepared, "--guestfish", args.guestfish,
                 "--qemu-img", args.qemu_img])
    if not args.image and not args.builder_archive:
        args.builder_archive, args.builder_image = checked_builder(
            cache, args.builder_image or args.builder_reference)
    if args.customize and not args.crun_binary.is_file():
        if args.crun_binary != cache / "crun/crun":
            raise ValueError(f"Explicit --crun-binary missing: {args.crun_binary}")
        run(["bash", ROOT / "autosd/customization/runtime/build-crun.sh",
             "--output", cache / "crun"])
    if args.customize and args.crun_binary == cache / "crun/crun":
        check_crun(cache / "crun")
    receipt = {"config": str(args.config.absolute()),
               "config_sha256": pipeline.sha256(args.config),
               "manifest": str(args.manifest) if args.manifest else None,
               "builder_archive": str(args.builder_archive) if args.builder_archive else None,
               "builder_image": args.builder_image,
               "crun_binary": str(args.crun_binary) if args.customize else None,
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
            "stages": ["download nightly + checksum", "host-tools readonly smoke",
                       "prepare private builder base", "download ARM64 AIB + digest",
                       "build patched crun if customization enabled",
                       "AIB build, QEMU and QBox validation unless --prepare-inputs-only"],
            "external_prerequisites": "Apollo BSP/providers, documented host packages; no previous build/autosd inputs"}, indent=2))
        return 0
    # Refuse known output collisions before lengthy downloads/builds.
    if not args.prepare_inputs_only:
        for path in (args.output, args.work_dir, args.qbox_out_dir):
            if path is not None and path.exists():
                raise ValueError(f"Output exists: {path}; choose new --output/--work-dir")
    receipt = prepare(args, cache)
    if args.prepare_inputs_only:
        print(json.dumps(receipt, indent=2))
        return 0
    args = pipeline.resolve(args)
    pipeline.Pipeline(args).run()
    print(f"PASS: {args.work_dir / 'result.json'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
