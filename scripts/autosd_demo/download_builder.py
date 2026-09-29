#!/usr/bin/env python3
"""Download the official ARM64 AIB as a verified, self-contained OCI archive.

Only the Python standard library is required. A mutable tag is resolved once;
all subsequent requests use content digests. Nothing is stored in Docker's cache.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile
import tempfile
import time
import urllib.error
import urllib.request

REPOSITORY = "quay.io/centos-sig-automotive/automotive-image-builder"
API = "https://quay.io/v2/centos-sig-automotive/automotive-image-builder"
OCI = "application/vnd.oci.image."
ACCEPT = ", ".join((OCI + "index.v1+json", OCI + "manifest.v1+json",
                    "application/vnd.docker.distribution.manifest.list.v2+json",
                    "application/vnd.docker.distribution.manifest.v2+json"))


def sha(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def digest_path(digest):
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ValueError(f"Unsupported or malformed digest: {digest}")
    return "blobs/sha256/" + digest.split(":", 1)[1]


def parse_reference(reference):
    match = re.fullmatch(re.escape(REPOSITORY) +
                         r"(?::([A-Za-z0-9_][A-Za-z0-9_.-]{0,127})|@(sha256:[0-9a-f]{64}))", reference)
    if not match:
        raise ValueError("Expected the official AIB repository with an explicit tag or SHA256 digest")
    return match.group(1) or match.group(2)


def download(url, destination, expected=None, size=None):
    """Retry complete transfers; never accept a partial or unverified blob."""
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"Accept": ACCEPT})
            with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as out:
                hasher = hashlib.sha256()
                count = 0
                while block := response.read(1024 * 1024):
                    out.write(block)
                    hasher.update(block)
                    count += len(block)
                actual = "sha256:" + hasher.hexdigest()
                declared = response.headers.get("Docker-Content-Digest")
            if expected and actual != expected:
                raise ValueError(f"Digest mismatch: expected {expected}, received {actual}")
            if declared and actual != declared:
                raise ValueError("Registry content digest mismatch")
            if size is not None and count != size:
                raise ValueError(f"Size mismatch: expected {size}, received {count}")
            return actual
        except (OSError, ValueError, urllib.error.URLError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def encode(document):
    return json.dumps(document, separators=(",", ":"), sort_keys=True).encode()


def oci_manifest(raw):
    """Preserve OCI bytes; explicitly rehash a Docker-to-OCI conversion."""
    manifest = json.loads(raw)
    if manifest.get("mediaType") == OCI + "manifest.v1+json":
        return raw
    if manifest.get("mediaType") != "application/vnd.docker.distribution.manifest.v2+json":
        raise ValueError("Unsupported image manifest media type")
    manifest["mediaType"] = OCI + "manifest.v1+json"
    manifest["config"]["mediaType"] = OCI + "config.v1+json"
    types = {"application/vnd.docker.image.rootfs.diff.tar.gzip": OCI + "layer.v1.tar+gzip",
             "application/vnd.docker.image.rootfs.diff.tar": OCI + "layer.v1.tar"}
    for layer in manifest["layers"]:
        if layer["mediaType"] not in types:
            raise ValueError("Unsupported Docker layer type")
        layer["mediaType"] = types[layer["mediaType"]]
    return encode(manifest)


def build_archive(reference, output):
    selector = parse_reference(reference)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / "aib-builder.oci.tar"
    metadata = output / "metadata.json"
    if archive.exists() or metadata.exists():
        raise FileExistsError("Output archive or metadata already exists; use a fresh output directory")
    with tempfile.TemporaryDirectory(prefix=".aib-download-", dir=output) as temporary:
        root = Path(temporary)
        first = root / "source.json"
        source_digest = download(API + "/manifests/" + selector, first,
                                 selector if selector.startswith("sha256:") else None)
        raw = first.read_bytes()
        document = json.loads(raw)
        if "manifests" in document:
            candidates = [entry for entry in document["manifests"]
                          if entry.get("platform", {}).get("architecture") == "arm64"
                          and entry["platform"].get("os") == "linux"
                          and entry["platform"].get("variant", "v8") == "v8"]
            if len(candidates) != 1:
                raise ValueError("Expected exactly one linux/arm64/v8 image")
            descriptor = candidates[0]
            digest_path(descriptor["digest"])
            source_digest = download(API + "/manifests/" + descriptor["digest"], first,
                                     descriptor["digest"], descriptor["size"])
            raw = first.read_bytes()
        converted = oci_manifest(raw)
        manifest = json.loads(converted)
        manifest_digest = sha(converted)
        manifest_path = root / digest_path(manifest_digest)
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_bytes(converted)
        for descriptor in [manifest["config"], *manifest["layers"]]:
            blob = root / digest_path(descriptor["digest"])
            print(f"Downloading {descriptor['digest']} ({descriptor['size']} bytes)", flush=True)
            download(API + "/blobs/" + descriptor["digest"], blob,
                     descriptor["digest"], descriptor["size"])
        config = json.loads((root / digest_path(manifest["config"]["digest"])).read_bytes())
        if config.get("architecture") != "arm64" or config.get("os") != "linux":
            raise ValueError("Image config is not linux/arm64")
        index = {"schemaVersion": 2, "manifests": [{
            "mediaType": OCI + "manifest.v1+json", "digest": manifest_digest,
            "size": len(converted), "annotations": {
                "org.opencontainers.image.ref.name": REPOSITORY + ":apollo-replay"}}]}
        pending = root / "archive.tar"
        with tarfile.open(pending, "w") as tar:
            for name, data in [("oci-layout", encode({"imageLayoutVersion": "1.0.0"})),
                               ("index.json", encode(index))]:
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mode = 0o644
                tar.addfile(info, io.BytesIO(data))
            for blob in sorted((root / "blobs/sha256").iterdir()):
                tar.add(blob, arcname=str(blob.relative_to(root)), recursive=False)
        hasher = hashlib.sha256()
        with pending.open("rb") as stream:
            while block := stream.read(1024 * 1024):
                hasher.update(block)
        result = {"requested_reference": reference,
                  "source_reference": REPOSITORY + "@" + source_digest,
                  "builder_reference": REPOSITORY + "@" + manifest_digest,
                  "archive": str(archive.resolve()), "sha256": hasher.hexdigest(),
                  "architecture": "arm64", "os": "linux", "schema_version": 1}
        pending.rename(archive)
        metadata.write_text(json.dumps(result, indent=2) + "\n")
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", default=REPOSITORY + ":latest")
    parser.add_argument("--output", type=Path, default=Path("build/autosd/downloads/aib-builder"))
    args = parser.parse_args()
    try:
        result = build_archive(args.reference, args.output)
    except (OSError, ValueError, KeyError, tarfile.TarError) as error:
        parser.exit(1, f"AIB download failed: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
