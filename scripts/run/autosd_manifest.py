"""Validate prepared manifests for the full-system AutoSD launcher."""

import json
from pathlib import Path

PLATFORM_ARTIFACTS = frozenset((
    "ap-flash-image.img", "rse-flash-image.img", "rse-otp-image.img",
    "rse-rom-image.img", "si0_ramfw.bin", "zephyr-demos-cl1.bin",
    "efi-capsule-update-disk-image-apollo-qvp.img",
    "bl2-apollo_qvp.elf", "combined_provisioning_message.bin",
))


def autosd_manifest(path: Path | None) -> dict:
    if path is None:
        return {}
    path = path.absolute()
    if not path.is_file():
        raise ValueError(f"missing AutoSD manifest: {path}")
    manifest = json.loads(path.read_text())
    if not isinstance(manifest, dict) or manifest.get("mode") not in ("regular", "ostree"):
        raise ValueError("AutoSD manifest mode must be regular or ostree")
    if manifest.get("schema_version") not in (None, 1, 2):
        raise ValueError("Unsupported AutoSD manifest schema")
    prepared = manifest.get("schema_version") == 2
    if prepared:
        import re
        for name in ("sha256", "dtb_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", str(manifest.get(name, ""))):
                raise ValueError(f"Prepared manifest requires {name}")
        release = manifest.get("kernel_release")
        if not isinstance(release, str) or not re.fullmatch(r"[A-Za-z0-9_.+~-]+", release) or manifest.get("profile") not in ("automotive", "minimal-qm"):
            raise ValueError("Prepared manifest requires kernel_release and profile")
        if not isinstance(manifest.get("platform_requirements"), dict):
            raise ValueError("Prepared manifest platform_requirements must be an object")
    for name in (("rootfs", "dtb") if prepared else ("rootfs", "initrd")):
        value = manifest.get(name)
        if not isinstance(value, str) or not Path(value).is_absolute():
            raise ValueError(f"AutoSD manifest {name} must be an absolute path")
    if not isinstance(manifest.get("bootargs"), str) or not manifest["bootargs"].strip():
        raise ValueError("AutoSD manifest requires bootargs")
    return manifest


def verify_platform(deploy: Path, requirements: dict) -> dict:
    """Bind current firmware bytes to their generated compatibility record."""
    import hashlib
    import re

    if not isinstance(requirements, dict):
        raise ValueError('Image platform requirements must be an object')
    path = deploy / 'apollo-autosd-platform.json'
    platform = json.loads(path.read_text())
    if not isinstance(platform, dict) or platform.get('schema_version') != 1:
        raise ValueError('Unsupported Apollo platform manifest schema')
    for field in ('machine', 'variant', 'ap_cpus', 'pfdi'):
        if field not in requirements or platform.get(field) != requirements[field]:
            raise ValueError(f'Image/platform incompatibility: {field}')
    if not isinstance(platform.get('artifacts'), dict) or not platform['artifacts']:
        raise ValueError('Platform manifest requires artifact hashes')
    missing = PLATFORM_ARTIFACTS - platform['artifacts'].keys()
    if missing:
        raise ValueError('Platform manifest missing required artifacts: ' + ', '.join(sorted(missing)))
    for name, digest in platform['artifacts'].items():
        if Path(name).name != name or not re.fullmatch(r'[0-9a-f]{64}', str(digest)):
            raise ValueError('Invalid platform artifact entry')
        with (deploy / name).open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != digest:
                raise ValueError(f'Platform artifact hash mismatch: {name}')
    platform['manifest_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    config = deploy / 'apollo-autosd-platform-apollo-qvp.qboxconf'
    platform['qboxconf_sha256'] = hashlib.sha256(config.read_bytes()).hexdigest()
    return platform
