"""Validate prepared manifests for the full-system AutoSD launcher."""

import json
from pathlib import Path


def autosd_manifest(path: Path | None) -> dict:
    if path is None:
        return {}
    path = path.absolute()
    if not path.is_file():
        raise ValueError(f"missing AutoSD manifest: {path}")
    manifest = json.loads(path.read_text())
    if not isinstance(manifest, dict) or manifest.get("mode") not in ("regular", "ostree"):
        raise ValueError("AutoSD manifest mode must be regular or ostree")
    for name in ("rootfs", "initrd"):
        value = manifest.get(name)
        if not isinstance(value, str) or not Path(value).is_absolute():
            raise ValueError(f"AutoSD manifest {name} must be an absolute path")
    if not isinstance(manifest.get("bootargs"), str) or not manifest["bootargs"].strip():
        raise ValueError("AutoSD manifest requires bootargs")
    return manifest
