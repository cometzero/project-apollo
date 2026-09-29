#!/usr/bin/env python3
"""Resolve the official Stream 10 tag against the registry, not Docker cache."""
import json
import re
import subprocess


def arm64_reference(manifest):
    candidates = {
        entry.get("digest", "")
        for entry in manifest.get("manifests", [])
        if entry.get("platform", {}).get("architecture") == "arm64"
        and entry.get("platform", {}).get("os") == "linux"
        and entry.get("platform", {}).get("variant", "v8") == "v8"
    }
    if len(candidates) != 1:
        raise ValueError("Require exactly one Linux ARM64 Stream 10 manifest")
    digest = candidates.pop()
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ValueError("Invalid registry manifest digest")
    return "quay.io/centos/centos@" + digest


if __name__ == "__main__":
    result = subprocess.run(
        ["docker", "manifest", "inspect", "quay.io/centos/centos:stream10"],
        check=True, capture_output=True, text=True, timeout=180,
    )
    print(arm64_reference(json.loads(result.stdout)))
