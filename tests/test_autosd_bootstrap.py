"""Cold-start configuration, cache identity and opt-out contracts."""
import importlib.util
import json
from pathlib import Path
import sys

import pytest


@pytest.fixture
def module(monkeypatch):
    folder = Path(__file__).resolve().parents[1] / "scripts/autosd_demo"
    monkeypatch.syspath_prepend(str(folder))
    spec = importlib.util.spec_from_file_location("autosd_bootstrap", folder / "bootstrap.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_clean_dry_run_no_generated_inputs(module, tmp_path, capsys):
    assert module.main(["--dry-run", "--cache-dir", str(tmp_path / "empty")]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["customize"] is True
    assert result["kernel_input"] == "yocto-deploy"
    assert result["deploy_dir"].endswith("tmp_baremetal/deploy/images/apollo-qvp")
    assert "source RPM compilation" not in " ".join(result["stages"])
    assert result["builder_reference"].endswith("@sha256:37ce37564e1c76b6db707aa53800a77e112dfdc6167a2da77f93d4ce679f548f")
    assert not list(tmp_path.iterdir())


def test_minimal_opt_out(module, tmp_path):
    args = module.parser().parse_args(["--minimal", "--cache-dir", str(tmp_path)])
    module.setup(args)
    assert args.customize is False
    assert args.crun_binary is None


def test_default_paths_are_not_historical(module, tmp_path):
    args = module.parser().parse_args(["--cache-dir", str(tmp_path)])
    module.setup(args)
    assert args.crun_binary is None
    assert args.output == tmp_path / "automotive"
    assert "202609" not in str(args.aib_manifest)


@pytest.mark.parametrize("override", [False, True])
def test_prepare_uses_vendor_runtime_unless_explicit(module, tmp_path, monkeypatch, override):
    runtime = tmp_path / "crun/crun"
    runtime.parent.mkdir()
    runtime.write_bytes(b"old custom runtime")
    extra = ["--crun-binary", str(tmp_path / "missing-runtime")] if override else []
    args = module.parser().parse_args([
        "--cache-dir", str(tmp_path), "--image", str(tmp_path / "source.qcow2"),
        "--guestfish", "/tools/guestfish", *extra])
    if override:
        with pytest.raises(ValueError, match="Explicit --crun-binary missing"):
            module.setup(args)
        return
    module.setup(args)
    monkeypatch.setattr(module, "run", lambda *_: pytest.fail("unexpected build/download"))
    monkeypatch.setattr(module, "check_crun", lambda *_: pytest.fail("implicit custom runtime cache"))
    assert module.prepare(args, tmp_path)["crun_binary"] is None
    assert runtime.read_bytes() == b"old custom runtime"


@pytest.mark.parametrize("extra", [["--image", "x", "--builder-image", "y"],
                                  ["--builder-archive", "x"]])
def test_conflicting_inputs(module, extra):
    with pytest.raises(ValueError):
        module.setup(module.parser().parse_args(extra))


def test_builder_cache_hash_checked(module, tmp_path, monkeypatch):
    cache = tmp_path / ("builder-" + module.native_architecture())
    cache.mkdir()
    archive = cache / "aib-builder.oci.tar"
    archive.write_bytes(b"archive")
    reference = "official:latest"
    metadata = {"requested_reference": reference, "archive": str(archive), "architecture": module.native_architecture(),
                "sha256": module.pipeline.sha256(archive), "builder_reference": "pinned"}
    (cache / "metadata.json").write_text(json.dumps(metadata))
    monkeypatch.setattr(module, "run", lambda *_: pytest.fail("unexpected network"))
    assert module.checked_builder(tmp_path, reference) == (archive, "pinned")
    archive.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="corrupt"):
        module.checked_builder(tmp_path, reference)


def test_existing_output_rejected_before_downloads(module, tmp_path, monkeypatch):
    monkeypatch.setattr(module, "prepare", lambda *_: pytest.fail("download started"))
    with pytest.raises(ValueError, match="Output exists"):
        module.main(["--output", str(tmp_path)])


def test_nightly_cache_not_silently_retargeted(module, tmp_path):
    import download_nightly
    (tmp_path / "download.json").write_text(json.dumps({"requested_build_id": "123.abcd"}))
    with pytest.raises(ValueError, match="selection changed"):
        download_nightly.fetch(tmp_path, "456.abcd")


def test_nightly_cache_hash_checked(module, tmp_path):
    import download_nightly
    archive, image = tmp_path / "image.xz", tmp_path / "image.qcow2"
    archive.write_bytes(b"archive")
    image.write_bytes(b"disk")
    receipt = {"requested_build_id": None, "compressed": str(archive), "image": str(image),
               "compressed_sha256": module.pipeline.sha256(archive),
               "image_sha256": module.pipeline.sha256(image)}
    (tmp_path / "download.json").write_text(json.dumps(receipt))
    assert download_nightly.fetch(tmp_path) == receipt
    image.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="corrupt"):
        download_nightly.fetch(tmp_path)


def test_crun_cache_binds_recipe_source_and_binary(module, tmp_path, monkeypatch):
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module.subprocess, "check_output", lambda *_a, **_kw: "head\n")
    runtime = tmp_path / "autosd/customization/runtime"
    runtime.mkdir(parents=True)
    output = tmp_path / "cache"
    output.mkdir()
    for path in (output / "crun", output / "base-image.docker.tar",
                 runtime / "crun-cgroup-mount-label.patch"):
        path.write_bytes(b"data")
    scripts = {}
    for name in ("build-crun.sh", "build-crun-cross.sh", "crun-provenance.py", "resolve-centos-image.py"):
        (runtime / name).write_text("recipe")
        scripts[name] = module.pipeline.sha256(runtime / name)
    receipt = {"source_commit": "head", "libocispec_commit": "head",
               "patch_sha256": module.pipeline.sha256(runtime / "crun-cgroup-mount-label.patch"),
               "crun_sha256": module.pipeline.sha256(output / "crun"),
               "base_image_archive": "base-image.docker.tar",
               "base_image_archive_sha256": module.pipeline.sha256(output / "base-image.docker.tar"),
               "scripts_sha256": scripts}
    (output / "provenance.json").write_text(json.dumps(receipt))
    module.check_crun(output)
    (output / "crun").write_text("tampered")
    with pytest.raises(ValueError, match="changed"):
        module.check_crun(output)


def test_explicit_minimal_manifest(module, tmp_path):
    args = module.parser().parse_args(["--aib-manifest", str(module.ROOT / "autosd/sig-docs/demos/minimal_qm/minimal_qm.aib.yml"), "--cache-dir", str(tmp_path)])
    module.setup(args)
    assert not args.customize
    assert args.output == tmp_path / "minimal-qm"


def test_manifest_selection_conflict(module):
    args = module.parser().parse_args(["--minimal", "--aib-manifest", "anything.yml"])
    with pytest.raises(ValueError, match="cannot be combined"):
        module.setup(args)


def test_unknown_profile_is_rejected(module, tmp_path):
    manifest = tmp_path / 'custom.yml'
    manifest.write_text('name: unknown\ncontent:\n  rpms: []\n')
    with pytest.raises(ValueError, match='Supported AIB profiles'):
        module.setup(module.parser().parse_args(['--aib-manifest', str(manifest)]))


def test_customize_cannot_override_minimal_profile(module):
    with pytest.raises(ValueError, match='conflicts'):
        module.setup(module.parser().parse_args(['--minimal', '--customize']))


def test_explicit_yocto_kernel_inputs(module, tmp_path):
    args = module.parser().parse_args([
        "--deploy-dir", str(tmp_path / "deploy"),
        "--kernel-artifacts", str(tmp_path / "artifacts"), "--dry-run"])
    module.setup(args)
    assert args.deploy_dir == tmp_path / "deploy"
    assert args.kernel_artifacts == tmp_path / "artifacts"
