import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location("native_build", Path(__file__).resolve().parents[1] / "scripts/autosd_demo/native_build.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_only_build_root_replaced_and_rpm_policy_preserved():
    target = {"pipelines": [{"name": "build", "stages": [{"type": "org.osbuild.rpm"}]},
        {"name": "rootfs", "build": "name:build", "stages": [
            {"type": "org.osbuild.rpm", "options": {"gpgkeys": ["key"]}},
            {"type": "org.osbuild.copy", "options": {"paths": []}}]}],
        "sources": {"org.osbuild.curl": {"items": {"target": "target-rpm"}}}}
    native = {"pipelines": [{"name": "build", "stages": [{"type": "org.osbuild.rpm", "options": {"gpgkeys": ["native-key"]}}]}],
        "sources": {"org.osbuild.curl": {"items": {"native": "native-rpm"}}}}
    result = MODULE.cross_manifest(target, native)
    assert result["pipelines"][0] == native["pipelines"][0]
    assert result["pipelines"][1]["stages"][0]["options"] == {"gpgkeys": ["key"], "ignorearch": True}
    assert "ignorearch" not in target["pipelines"][1]["stages"][0]["options"]
    assert set(result["sources"]["org.osbuild.curl"]["items"]) == {"target", "native"}
    native["sources"]["org.osbuild.curl"]["items"]["target"] = "conflicting-url"
    with pytest.raises(ValueError, match="Conflicting source"):
        MODULE.cross_manifest(target, native)


def test_missing_build_pipeline_rejected():
    with pytest.raises(ValueError, match="one named build"):
        MODULE.cross_manifest({"pipelines": []}, {"pipelines": []})


def test_noarch_url_alias_keeps_content_checksum():
    digest = "sha256:" + "a" * 64
    def manifest(url):
        return {"pipelines": [{"name": "build", "stages": []}],
                "sources": {"org.osbuild.curl": {"items": {digest: url}}}}
    target = manifest("https://example/aarch64/same.noarch.rpm")
    native = manifest("https://example/x86_64/same.noarch.rpm")
    assert MODULE.cross_manifest(target, native)["sources"] == target["sources"]
