import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile

import pytest

PATH = Path(__file__).resolve().parents[1] / "scripts/autosd_demo/download_builder.py"
SPEC = importlib.util.spec_from_file_location("download_builder", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


@pytest.mark.parametrize("reference", ["other/repo:latest", MODULE.REPOSITORY,
    MODULE.REPOSITORY + "@sha256:abc", MODULE.REPOSITORY + ":../../escape"])
def test_rejects_nonofficial_reference(reference):
    with pytest.raises(ValueError):
        MODULE.parse_reference(reference)


def test_official_references():
    assert MODULE.parse_reference(MODULE.REPOSITORY + ":latest") == "latest"
    assert MODULE.parse_reference(MODULE.REPOSITORY + "@sha256:" + "a" * 64) == "sha256:" + "a" * 64


def test_conversion_changes_digest_and_preserves_layers():
    raw = MODULE.encode({"schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
        "config": {"mediaType": "application/vnd.docker.container.image.v1+json"},
        "layers": [{"mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
                    "digest": "sha256:" + "a" * 64}]})
    converted = MODULE.oci_manifest(raw)
    assert MODULE.sha(raw) != MODULE.sha(converted)
    assert json.loads(converted)["layers"][0]["digest"] == "sha256:" + "a" * 64
    assert MODULE.oci_manifest(converted) == converted


def test_archive_is_self_contained(monkeypatch, tmp_path):
    config = MODULE.encode({"architecture": "arm64", "os": "linux"})
    layer = b"example compressed layer"
    descriptor = lambda data, kind: {"mediaType": MODULE.OCI + kind,
        "digest": MODULE.sha(data), "size": len(data)}
    raw = MODULE.encode({"schemaVersion": 2, "mediaType": MODULE.OCI + "manifest.v1+json",
        "config": descriptor(config, "config.v1+json"),
        "layers": [descriptor(layer, "layer.v1.tar+gzip")]})
    index = MODULE.encode({"schemaVersion": 2, "manifests": [{
        **descriptor(raw, "manifest.v1+json"), "platform": {"architecture": "arm64", "os": "linux"}}]})
    sources = {"latest": index, MODULE.sha(raw): raw,
               MODULE.sha(config): config, MODULE.sha(layer): layer}

    def fake_download(url, destination, expected=None, size=None):
        data = sources[url.rsplit("/", 1)[1]]
        if expected:
            assert MODULE.sha(data) == expected
        if size is not None:
            assert len(data) == size
        destination.write_bytes(data)
        return MODULE.sha(data)

    monkeypatch.setattr(MODULE, "download", fake_download)
    result = MODULE.build_archive(MODULE.REPOSITORY + ":latest", tmp_path)
    assert result["builder_reference"] == MODULE.REPOSITORY + "@" + MODULE.sha(raw)
    archive = Path(result["archive"])
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == result["sha256"]
    assert json.loads((tmp_path / "metadata.json").read_text()) == result
    with tarfile.open(archive) as tar:
        descriptor = json.load(tar.extractfile("index.json"))["manifests"][0]
        assert descriptor["annotations"]["org.opencontainers.image.ref.name"].endswith(":apollo-replay")
        for data in (raw, config, layer):
            assert tar.extractfile(MODULE.digest_path(MODULE.sha(data))).read() == data
    with pytest.raises(FileExistsError):
        MODULE.build_archive(MODULE.REPOSITORY + ":latest", tmp_path)


def test_reject_digest_path_traversal():
    with pytest.raises(ValueError):
        MODULE.digest_path("sha256:../../bad")
