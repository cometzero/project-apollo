#!/usr/bin/env python3
"""Prepare AutoSD nightly or locally built disks and original initrds for Apollo.

Local example: --image build/demo.qcow2 --mode regular --output build/autosd/demo
Local raw/qcow2 images must be offline and self-contained. Their SHA256 is
recorded as provenance, not authenticated against a nightly checksum. Existing
per-mode output files are never overwritten by local-image preparation.

Requires qemu-img and guestfish with a working libguestfs appliance. Neither
sudo nor host mounts are used. SUPERMIN_KERNEL and LIBGUESTFS_BACKEND are
inherited, allowing an unprivileged, readable host kernel and direct backend.
"""

from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
import lzma
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import subprocess
import tempfile
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen


INDEX = "https://autosd.sig.centos.org/AutoSD-10/nightly/sample-images/"
DOWNLOAD = "https://download.autosd.sig.centos.org/AutoSD-10/nightly/sample-images/"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "build/autosd"
IMAGE = re.compile(
    r"auto-osbuild-qemu-autosd10-developer-(regular|ostree)-aarch64-"
    r"([0-9]+\.[0-9a-f]+)\.qcow2\.xz$"
)


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.hrefs.extend(value for key, value in attrs if key == "href" and value)


def select_images(html: str, modes: list[str], build_id: str | None) -> dict[str, str]:
    """Select one common build for both modes, never independently mix builds."""
    if build_id is not None:
        if not re.fullmatch(r"[0-9]+\.[0-9a-f]+", build_id):
            raise ValueError(f"Invalid build ID: {build_id!r}")
        return {mode: DOWNLOAD + "auto-osbuild-qemu-autosd10-developer-"
                + f"{mode}-aarch64-{build_id}.qcow2.xz" for mode in modes}
    links = Links()
    links.feed(html)
    builds: dict[str, dict[str, str]] = {}
    for href in links.hrefs:
        url = urljoin(INDEX, href)
        match = IMAGE.fullmatch(PurePosixPath(urlparse(url).path).name)
        if (match and urlparse(url).scheme == "https"
                and urlparse(url).netloc in ("autosd.sig.centos.org",
                                            "download.autosd.sig.centos.org")):
            mode, identifier = match.groups()
            builds.setdefault(identifier, {})[mode] = url
    candidates = [key for key, images in builds.items()
                  if all(mode in images for mode in modes)
                  and (build_id is None or key == build_id)]
    if not candidates:
        raise ValueError(f"No matching nightly build for {modes}, build ID {build_id!r}")
    chosen = max(candidates, key=lambda value: (int(value.split('.')[0]), value))
    return {mode: builds[chosen][mode] for mode in modes}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_checksum(path: Path, checksum_text: str) -> str:
    expected = None
    for line in checksum_text.splitlines():
        match = re.fullmatch(r"([0-9a-fA-F]{64})\s+\*?(.+)", line.strip())
        if match and match[2] in (path.name, "./" + path.name):
            expected = match[1].lower()
            break
    if expected is None:
        raise ValueError(f"No SHA256 entry for {path.name}")
    actual = sha256(path)
    if actual != expected:
        raise ValueError(f"SHA256 mismatch for {path}: expected {expected}, got {actual}")
    return actual


def download(url: str, destination: Path) -> None:
    if destination.exists():
        return
    print(f"Downloading {url}", flush=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as directory:
        temporary = Path(directory) / destination.name
        with urlopen(url, timeout=120) as source, temporary.open("wb") as target:
            shutil.copyfileobj(source, target, length=8 * 1024 * 1024)
        temporary.replace(destination)


def parse_bls(text: str) -> tuple[str, str]:
    fields: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            fields.setdefault(parts[0], []).append(parts[1].strip())
    if len(fields.get("initrd", [])) != 1 or len(fields.get("options", [])) != 1:
        raise ValueError("BLS entry must contain exactly one initrd and options line")
    initrd = fields["initrd"][0]
    if not initrd.startswith("/") or ".." in PurePosixPath(initrd).parts:
        raise ValueError(f"Invalid BLS initrd path: {initrd!r}")
    options = shlex.split(fields["options"][0])
    if not any(option.startswith("root=") for option in options):
        raise ValueError("BLS entry has no root= option")
    options = [option for option in options
               if option not in ("quiet", "rhgb", "splash")
               and not option.startswith(("console=", "rd.modules-load=", "loglevel=",
                                          "systemd.show_status=", "rd.systemd.show_status="))]
    options += ["console=ttyAMA0", "earlycon=pl011,0x1a400000", "loglevel=7",
                "systemd.show_status=yes", "rd.systemd.show_status=yes"]
    # Keep quoted kernel arguments intact; these images normally use bare tokens.
    return initrd, " ".join('"' + item.replace('"', '\\"') + '"'
                            if any(char.isspace() for char in item) else item
                            for item in options)


def guestfish(binary: str, disk: Path, *command: str, device: str | None = None,
              image_format: str = "qcow2") -> str:
    if image_format not in ("raw", "qcow2"):
        raise ValueError(f"Unsupported image format: {image_format}")
    args = [binary, "--ro", f"--format={image_format}", "-a", str(disk)]
    if device:
        args += ["-m", f"{device}:/:ro"]
    else:
        args += ["run", ":"]
    result = subprocess.run(args + list(command), check=True, text=True,
                            stdout=subprocess.PIPE)
    return result.stdout.strip()


def extract_boot(binary: str, disk: Path, directory: Path,
                 image_format: str = "qcow2") -> tuple[str, str, str]:
    def fish(*command: str, device: str | None = None) -> str:
        return guestfish(binary, disk, *command, device=device, image_format=image_format)

    filesystems = fish("list-filesystems")
    for line in filesystems.splitlines():
        device, separator, filesystem = line.partition(":")
        if not separator or filesystem.strip() != "ext4":
            continue
        entries = fish("glob-expand", "/boot/loader/entries/*.conf", device=device).splitlines()
        entries = [entry for entry in entries if entry.endswith(".conf") and "*" not in entry]
        if not entries:
            continue
        # Version-aware ordering also handles multiple kernel entries.
        entries.sort(key=lambda entry: [int(part) if part.isdigit() else part
                                       for part in re.split(r"(\d+)", entry)])
        entry = entries[-1]
        bls = fish("cat", entry, device=device)
        initrd, bootargs = parse_bls(bls)
        candidates = [initrd] if initrd.startswith("/boot/") else ["/boot" + initrd, initrd]
        for candidate in candidates:
            if fish("is-file", candidate, device=device) == "true":
                fish("download", candidate, str(directory / "initrd.img"), device=device)
                (directory / "entry.conf").write_text(bls + "\n")
                return bootargs, entry, candidate
        raise ValueError(f"BLS initrd not found: {initrd}")
    raise ValueError("No ext4 filesystem with /boot/loader/entries/*.conf found")


def prepare_local(mode: str, image: Path, output: Path, fish: str, qemu_img: str) -> Path:
    """Inspect a staged copy, preserving an offline local build and prior output."""
    if mode not in ("regular", "ostree"):
        raise ValueError("Local images require an explicit regular or ostree mode")
    image = image.resolve(strict=True)
    if not image.is_file():
        raise ValueError("Local image must be a regular file")
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    destinations = {"disk.raw": output / f"{mode}.raw",
                    "initrd.img": output / f"{mode}-initrd.img",
                    "entry.conf": output / f"{mode}-entry.conf",
                    "manifest.json": output / f"{mode}.json"}
    if any(path.exists() or path.is_symlink() for path in destinations.values()):
        raise ValueError("Local image outputs already exist; select a fresh --output directory")
    info = json.loads(subprocess.run([qemu_img, "info", "--output=json", str(image)],
                      check=True, text=True, stdout=subprocess.PIPE).stdout)
    image_format = info.get("format")
    format_data = info.get("format-specific", {}).get("data", {})
    if (image_format not in ("raw", "qcow2") or info.get("backing-filename")
            or info.get("full-backing-filename") or format_data.get("data-file")):
        raise ValueError("Local image must be a self-contained raw or qcow2 image without a backing file")
    digest = sha256(image)
    with tempfile.TemporaryDirectory(prefix=f".{mode}-local-", dir=output) as temporary:
        stage = Path(temporary)
        subprocess.run([qemu_img, "convert", "-f", image_format, "-O", "raw",
                        "-S", "4k", str(image), str(stage / "disk.raw")], check=True)
        bootargs, entry, initrd_source = extract_boot(fish, stage / "disk.raw", stage, image_format="raw")
        if sha256(image) != digest:
            raise ValueError("Local source image changed during preparation; use an offline image")
        manifest = {
            "mode": mode, "rootfs": str(destinations["disk.raw"]),
            "initrd": str(destinations["initrd.img"]), "bootargs": bootargs,
            "source_kind": "local", "source_path": str(image), "source_format": image_format,
            "source_sha256": digest, "checksum_verification": "local provenance only",
            "bls": str(destinations["entry.conf"]), "bls_source": entry, "initrd_source": initrd_source,
            "rootfs_sha256": sha256(stage / "disk.raw"), "initrd_sha256": sha256(stage / "initrd.img"),
        }
        (stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        # Same-filesystem hard links publish with exclusive creation. Removing
        # the staging directory leaves ordinary single-link output files.
        # Publish the manifest last so incomplete output is never advertised.
        for name, destination in destinations.items():
            os.link(stage / name, destination)
    print(f"Prepared {destinations['manifest.json']}", flush=True)
    return destinations["manifest.json"]


def prepare(mode: str, url: str, output: Path, fish: str, qemu_img: str) -> Path:
    compressed = output / PurePosixPath(urlparse(url).path).name
    checksum = output / (compressed.name + ".sha256")
    download(url + ".sha256", checksum)
    download(url, compressed)
    digest = verify_checksum(compressed, checksum.read_text())
    qcow = compressed.with_suffix("")
    manifest_path = output / f"{mode}.json"
    # A completed manifest binds cached outputs to the verified download.
    if manifest_path.exists():
        cached = json.loads(manifest_path.read_text())
        if (cached.get("source_sha256") == digest
                and Path(cached.get("bls", "")).is_file()
                and all(Path(cached.get(key, "")).is_file()
                        and sha256(Path(cached[key])) == cached.get(key + "_sha256")
                        for key in ("rootfs", "initrd"))):
            # Refresh launcher policy even when the disk/initrd are unchanged.
            _, bootargs = parse_bls(Path(cached["bls"]).read_text())
            if cached.get("bootargs") != bootargs:
                cached["bootargs"] = bootargs
                manifest_path.write_text(json.dumps(cached, indent=2) + "\n")
            print(f"Verified cached {manifest_path}", flush=True)
            return manifest_path
    with tempfile.TemporaryDirectory(prefix=f".{mode}-", dir=output) as temporary:
        stage = Path(temporary)
        # Recreate derived files if no hash-bound manifest proves their identity.
        print(f"Decompressing {compressed.name}", flush=True)
        unpacked = stage / "disk.qcow2"
        with lzma.open(compressed, "rb") as source, unpacked.open("wb") as target:
            shutil.copyfileobj(source, target, length=8 * 1024 * 1024)
        subprocess.run([qemu_img, "convert", "-f", "qcow2", "-O", "raw",
                        "-S", "4k", str(unpacked), str(stage / "disk.raw")], check=True)
        bootargs, entry, initrd_source = extract_boot(fish, unpacked, stage)
        rootfs = output / f"{mode}.raw"
        initrd = output / f"{mode}-initrd.img"
        bls = output / f"{mode}-entry.conf"
        manifest = {
            "mode": mode, "rootfs": str(rootfs), "initrd": str(initrd),
            "bootargs": bootargs, "source_url": url, "source_sha256": digest,
            "checksum_url": url + ".sha256", "index_url": INDEX,
            "compressed": str(compressed), "qcow2": str(qcow),
            "bls": str(bls), "bls_source": entry, "initrd_source": initrd_source,
            "rootfs_sha256": sha256(stage / "disk.raw"),
            "initrd_sha256": sha256(stage / "initrd.img"),
        }
        unpacked.replace(qcow)
        (stage / "disk.raw").replace(rootfs)
        (stage / "initrd.img").replace(initrd)
        (stage / "entry.conf").replace(bls)
        staged_manifest = stage / "manifest.json"
        staged_manifest.write_text(json.dumps(manifest, indent=2) + "\n")
        staged_manifest.replace(manifest_path)
    print(f"Prepared {manifest_path}", flush=True)
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("regular", "ostree", "all"), default="all")
    parser.add_argument("--build-id", help="Pinned build, e.g. 2869696176.466d2e78")
    parser.add_argument("--image", type=Path, help="offline local raw/qcow2 image; requires --mode regular or ostree")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--guestfish", default="guestfish")
    parser.add_argument("--qemu-img", default="qemu-img")
    args = parser.parse_args()
    if args.image and (args.mode == "all" or args.build_id):
        parser.error("--image requires --mode regular or ostree and cannot be combined with --build-id")
    for binary in (args.guestfish, args.qemu_img):
        if not shutil.which(binary):
            parser.error(f"Required executable not found: {binary}")
    if args.image:
        prepare_local(args.mode, args.image, args.output, args.guestfish, args.qemu_img)
        return
    modes = ["regular", "ostree"] if args.mode == "all" else [args.mode]
    if args.build_id:
        images = select_images("", modes, args.build_id)
    else:
        with urlopen(INDEX, timeout=120) as source:
            images = select_images(source.read().decode("utf-8"), modes, None)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    for mode, url in images.items():
        prepare(mode, url, output, args.guestfish, args.qemu_img)


if __name__ == "__main__":
    main()
