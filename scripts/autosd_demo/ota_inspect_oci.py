#!/usr/bin/env python3
"""Read a built OSTree OCI archive without extracting or executing its files."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile


def selected(name):
    return (name.endswith(("/vmlinuz", "/initramfs.img", "/kernel/cmdline", "/BOOTAA64.EFI"))
            or "/bootc/install/" in name
            or name == "usr/lib/bootc-image-builder/disk.yaml"
            or "sysboot-check@" in name and ".service.d/" in name)


def inspect(path):
    with path.open("rb") as source:
        result = {"archive_sha256": hashlib.file_digest(source, "sha256").hexdigest()}
    with tarfile.open(path) as archive:
        index = json.load(archive.extractfile("index.json"))
        if len(index["manifests"]) != 1:
            raise ValueError("Expected one built image")

        def blob(descriptor):
            algorithm, digest = descriptor["digest"].split(":", 1)
            if algorithm != "sha256":
                raise ValueError("Expected sha256 OCI descriptor")
            name = "blobs/sha256/" + digest
            with archive.extractfile(name) as stream:
                if hashlib.file_digest(stream, "sha256").hexdigest() != digest:
                    raise ValueError("OCI blob checksum mismatch")
            return name

        manifest = json.load(archive.extractfile(blob(index["manifests"][0])))
        config = json.load(archive.extractfile(blob(manifest["config"])))
        result.update(image_digest=index["manifests"][0]["digest"],
                      architecture=config["architecture"], labels=config["config"].get("Labels", {}))
        layers = [blob(item) for item in manifest["layers"]]
        aliases, files = {}, {}
        # OSTree chunked OCI stores regular payloads under repo/objects and
        # exposes filesystem paths as hardlinks, sometimes in another layer.
        for layer in layers:
            with tarfile.open(fileobj=archive.extractfile(layer), mode="r|*") as stream:
                for member in stream:
                    if selected(member.name) and (member.isfile() or member.islnk()):
                        aliases[member.name] = member.linkname if member.islnk() else member.name
        targets = set(aliases.values())
        for layer in layers:
            with tarfile.open(fileobj=archive.extractfile(layer), mode="r|*") as stream:
                for member in stream:
                    if member.name in targets and member.isfile():
                        content = stream.extractfile(member).read()
                        record = {"size": len(content), "sha256": hashlib.sha256(content).hexdigest()}
                        if len(content) < 16384:
                            record["text"] = content.decode(errors="replace")
                        files[member.name] = record
        result["files"] = {name: files[target] for name, target in aliases.items()}
        if result["architecture"] != "arm64":
            raise ValueError("OTA image is not ARM64")
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = inspect(args.archive)
    with args.output.open("x") as output:
        json.dump(result, output, indent=2)
        output.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
