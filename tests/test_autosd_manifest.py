"""Validate the full-system AutoSD manifest contract."""

import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/run"))
from autosd_manifest import autosd_manifest


@pytest.mark.parametrize("changes", [{"mode": "invalid"}, {"rootfs": "relative.raw"},
                                     {"initrd": None}, {"bootargs": ""}])
def test_autosd_manifest_rejects_invalid_fields(tmp_path, changes):
    manifest = {"mode": "regular", "rootfs": "/disk.raw", "initrd": "/initrd",
                "bootargs": "console=ttyAMA0"}
    manifest.update(changes)
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        autosd_manifest(path)


def test_firmware_binding_rejects_incompatible_and_modified_artifact(tmp_path):
    import hashlib
    import importlib.util
    module_path = Path(__file__).resolve().parents[1] / 'scripts/run/autosd_manifest.py'
    spec = importlib.util.spec_from_file_location('platform_manifest', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    firmware = tmp_path / 'ap-flash-image.img'
    firmware.write_bytes(b'firmware')
    requirements = dict(machine='apollo-qvp', variant='cfg2', ap_cpus=4, pfdi=True)
    artifacts = {}
    for name in module.PLATFORM_ARTIFACTS:
        (tmp_path / name).write_bytes(b'firmware')
        artifacts[name] = hashlib.sha256(b'firmware').hexdigest()
    platform = dict(requirements, schema_version=1, artifacts=artifacts)
    (tmp_path / 'apollo-autosd-platform.json').write_text(json.dumps(platform))
    (tmp_path / 'apollo-autosd-platform-apollo-qvp.qboxconf').write_text('{}')
    assert module.verify_platform(tmp_path, requirements)['ap_cpus'] == 4
    with pytest.raises(ValueError, match='incompatibility'):
        module.verify_platform(tmp_path, dict(requirements, ap_cpus=8))
    firmware.write_bytes(b'changed')
    with pytest.raises(ValueError, match='hash mismatch'):
        module.verify_platform(tmp_path, requirements)


def test_firmware_binding_rejects_omitted_artifact_and_invalid_requirements(tmp_path):
    from autosd_manifest import verify_platform
    requirements = dict(machine='apollo-qvp', variant='cfg2', ap_cpus=4, pfdi=True)
    platform = dict(requirements, schema_version=1, artifacts={'ap-flash-image.img': 'a' * 64})
    (tmp_path / 'apollo-autosd-platform.json').write_text(json.dumps(platform))
    with pytest.raises(ValueError, match='missing required artifacts'):
        verify_platform(tmp_path, requirements)
    with pytest.raises(ValueError, match='must be an object'):
        verify_platform(tmp_path, ['machine'])


@pytest.mark.parametrize('release', [42, [], '6.18 bad', ''])
def test_prepared_manifest_requires_kernel_release_string(tmp_path, release):
    path = tmp_path / 'manifest.json'
    path.write_text(json.dumps(dict(schema_version=2, mode='regular', sha256='a' * 64,
        dtb_sha256='b' * 64, kernel_release=release, profile='automotive')))
    with pytest.raises(ValueError, match='kernel_release'):
        autosd_manifest(path)


@pytest.mark.parametrize('requirements', [None, [], 'cfg2'])
def test_prepared_manifest_requires_platform_object(tmp_path, requirements):
    path = tmp_path / 'manifest.json'
    path.write_text(json.dumps(dict(schema_version=2, mode='regular', sha256='a' * 64,
        dtb_sha256='b' * 64, kernel_release='6.18.5-rt3-yocto-preempt-rt+',
        profile='automotive', platform_requirements=requirements)))
    with pytest.raises(ValueError, match='platform_requirements'):
        autosd_manifest(path)
