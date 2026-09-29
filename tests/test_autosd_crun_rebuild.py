"""The crun entry point must not require retained build artifacts."""
from pathlib import Path
import hashlib
import importlib.util
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "autosd/customization/runtime/build-crun.sh"


def run(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], text=True, capture_output=True)


def test_dry_run_is_independent_of_build_outputs(tmp_path):
    output = tmp_path / "fresh" / "runtime"
    result = run("--output", str(output), "--dry-run")
    assert result.returncode == 0, result.stderr
    assert f"output={output}" in result.stdout
    assert "autosd/crun" in result.stdout
    assert not output.parent.exists()


@pytest.mark.parametrize("image", ["latest", "quay.io/centos/centos:stream10", "evil@sha256:" + "a" * 64])
def test_unpinned_or_foreign_image_rejected(image):
    result = run("--base-image", image, "--dry-run")
    assert result.returncode == 2
    assert "digest-pinned" in result.stderr


def test_unknown_option_rejected():
    assert run("--oops").returncode == 2


def test_shell_syntax():
    for script in (SCRIPT, SCRIPT.with_name("build-crun-cross.sh")):
        result = subprocess.run(["bash", "-n", str(script)], capture_output=True)
        assert result.returncode == 0, result.stderr


def test_provenance_records_rebuild_inputs(tmp_path):
    helper = SCRIPT.with_name("crun-provenance.py")
    spec = importlib.util.spec_from_file_location("crun_provenance", helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    inputs = {
        "source-commit.txt": "a" * 40,
        "libocispec-commit.txt": "b" * 40,
        "patch.sha256": "c" * 64 + "  patch",
        "base-image.txt": "quay.io/centos/centos@sha256:" + "d" * 64,
        "crun": "runtime bytes",
        "base-image.docker.tar": "archive bytes",
    }
    for filename, contents in inputs.items():
        (tmp_path / filename).write_text(contents)
    data = module.record(tmp_path)
    assert data["source_commit"] == "a" * 40
    assert data["libocispec_commit"] == "b" * 40
    assert data["patch_sha256"] == "c" * 64
    assert data["crun_sha256"] == hashlib.sha256(b"runtime bytes").hexdigest()
    assert data["base_image_archive_sha256"] == hashlib.sha256(b"archive bytes").hexdigest()


def resolver():
    spec = importlib.util.spec_from_file_location("resolve_centos", SCRIPT.with_name("resolve-centos-image.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.arm64_reference


def test_arm64_registry_resolution():
    entries = [
        {"digest": "sha256:" + "a" * 64, "platform": {"architecture": "amd64", "os": "linux"}},
        {"digest": "sha256:" + "b" * 64, "platform": {"architecture": "arm64", "os": "linux", "variant": "v8"}},
    ]
    assert resolver()({"manifests": entries}) == "quay.io/centos/centos@sha256:" + "b" * 64


@pytest.mark.parametrize("manifest", [{}, {"manifests": [{"digest": "bad", "platform": {"architecture": "arm64", "os": "linux"}}]}])
def test_registry_resolution_rejects_missing_or_invalid_arm64(manifest):
    with pytest.raises(ValueError):
        resolver()(manifest)
