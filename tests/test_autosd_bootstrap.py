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
    assert result["builder_reference"].endswith(":latest")
    assert not list(tmp_path.iterdir())


def test_minimal_opt_out(module, tmp_path):
    args = module.parser().parse_args(["--minimal", "--cache-dir", str(tmp_path)])
    module.setup(args)
    assert args.customize is False
    assert args.crun_binary is None


def test_default_paths_are_not_historical(module, tmp_path):
    args = module.parser().parse_args(["--cache-dir", str(tmp_path)])
    module.setup(args)
    assert args.crun_binary == tmp_path / "crun/crun"
    assert args.output == tmp_path / "demo-minimal-qm-prepared"
    assert "202609" not in str(args.aib_manifest)


@pytest.mark.parametrize("extra", [["--image", "x", "--builder-image", "y"],
                                  ["--builder-archive", "x"]])
def test_conflicting_inputs(module, extra):
    with pytest.raises(ValueError):
        module.setup(module.parser().parse_args(extra))


def test_builder_cache_hash_checked(module, tmp_path, monkeypatch):
    cache = tmp_path / "builder"
    cache.mkdir()
    archive = cache / "aib-builder.oci.tar"
    archive.write_bytes(b"archive")
    reference = "official:latest"
    metadata = {"requested_reference": reference, "archive": str(archive),
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
