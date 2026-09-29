#!/usr/bin/env python3
"""Record reproducibility inputs for a completed crun cross build."""
import hashlib
import json
from pathlib import Path
import sys


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(output):
    return {
        "schema_version": 1,
        "source_commit": (output / "source-commit.txt").read_text().strip(),
        "libocispec_commit": (output / "libocispec-commit.txt").read_text().strip(),
        "patch_sha256": (output / "patch.sha256").read_text().split()[0],
        "crun_sha256": sha256(output / "crun"),
        "base_image": (output / "base-image.txt").read_text().strip(),
        "base_image_archive": "base-image.docker.tar",
        "base_image_archive_sha256": sha256(output / "base-image.docker.tar"),
        "scripts_sha256": {
            name: sha256(Path(__file__).parent / name)
            for name in ("build-crun.sh", "build-crun-cross.sh", "crun-provenance.py", "resolve-centos-image.py")
        },
    }


if __name__ == "__main__":
    directory = Path(sys.argv[1])
    (directory / "provenance.json").write_text(json.dumps(record(directory), indent=2) + "\n")
