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


def test_normal_rt_policy_is_applied_before_uki_generation():
    original = {'pipelines': [{'name': 'rootfs', 'stages': [{'type': 'org.osbuild.kernel-cmdline',
        'options': {'kernel_opts': 'root=UUID=test slub_debug=FPZ console=ttyAMA0 rcupdate.rcu_expedited=1 rcupdate.rcu_normal_after_boot=0'}}]}]}
    normalized = MODULE.normal_rt_manifest(original)
    assert normalized['pipelines'][0]['stages'][0]['options']['kernel_opts'] == 'root=UUID=test console=ttyAMA0'
    assert 'slub_debug' in original['pipelines'][0]['stages'][0]['options']['kernel_opts']
    with pytest.raises(ValueError, match='exactly one'):
        MODULE.normal_rt_manifest({'pipelines': []})


def test_native_tool_policy_retains_qm_without_target_kernel():
    policy = MODULE.native_tools_policy()
    assert 'qm' in policy
    assert 'kernel' not in policy
    assert 'target' not in policy
    assert policy['content']['rpms'] == []
    assert policy['qm']['content']['rpms'] == []


def test_native_apollo_build_replaces_host_dependent_uki_stage():
    target = {'pipelines': [{'name': 'image-tree', 'stages': [
        {'type': 'org.osbuild.kernel-cmdline', 'options': {'kernel_opts': 'root=UUID=test'}},
        {'type': 'org.osbuild-auto.aboot.update', 'options': {'kernel': '6.18.5-apollo'}},
    ]}]}
    result = MODULE.normal_rt_manifest(target, "a" * 64)
    assert result['pipelines'][0]['stages'][1] == {
        'type': 'org.osbuild.apollo.uki', 'options': {'kernel': '6.18.5-apollo', 'implementation_sha256': 'a' * 64}}
    changed = MODULE.normal_rt_manifest(target, 'b' * 64)
    assert changed != result
    with pytest.raises(ValueError, match='implementation hash is required'):
        MODULE.normal_rt_manifest(target)
