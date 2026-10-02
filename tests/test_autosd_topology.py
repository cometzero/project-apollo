"""Topology contracts use both actual evaluated platform Lua and small fixtures."""
import json
import importlib.util
import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("autosd_topology", ROOT / "scripts/autosd_dashboard/topology.py")
topology = importlib.util.module_from_spec(spec)
spec.loader.exec_module(topology)
HAS_LUA = any(shutil.which(name) for name in ("lua5.4", "lua5.3", "lua", "luajit"))
requires_lua = pytest.mark.skipif(not HAS_LUA, reason="Lua interpreter not installed")


@pytest.fixture
def fixture_root(tmp_path):
    entry = tmp_path / topology.ENTRYPOINT
    entry.parent.mkdir(parents=True)
    entry.write_text('''
platform = {
    moduletype = "Container",
    router = {moduletype = "router"},
    qemu = {moduletype = "QemuInstance"},
    cpu = {moduletype = "cpu_arm", args={"&qemu"}, mem={bind="&router.target_socket"}},
    device = {moduletype = "test_device", mem={address=4096,size=256,bind="&router.initiator_socket"}},
    nested = {moduletype="Container", qemu={moduletype="QemuInstance"},
              cpu={moduletype="ApolloRseCPU",args={"&qemu"}}}
}
''')
    return tmp_path


@requires_lua
def test_full_system_evaluates_bindings_and_cpu_ownership():
    graph = topology.get_topology(ROOT)
    nodes = {node["id"]: node for node in graph["nodes"]}
    assert len(nodes) > 300
    assert {"fabric", "rse", "ap_compute", "si_cl0", "si_cl1", "ros", "system_mgmt"} <= {
        group["id"] for group in graph["groups"]}
    assert graph["warnings"] == []
    assert graph["environment"] == {"QBOX_RDASPEN_ENABLE_AP_CPUS": "true"}
    assert nodes["platform.rse_cpu_pass.cpu_0"]["kind"] == "cpu"
    assert nodes["platform.rse_cpu_pass.cpu_0"]["qemu_instance"] == "platform.rse_cpu_pass.qemu_inst"
    assert nodes["platform.ap_cpu_0"]["qemu_instance"] == "platform.ap_qemu_inst"
    assert all(nodes[f"platform.si_cl1_cpu_{index}"]["group"] == "si_cl1" for index in range(4))
    assert nodes["platform.si_cl0_cpu_0"]["group"] == "si_cl0"
    assert nodes["platform.ap_router"]["group"] == "ap_compute"
    assert nodes["platform.ap_qemu_inst"]["group"] == "ap_compute"
    assert nodes["platform.ap_virtioblk_0"]["group"] == "vp"
    assert any(edge["source"] == "platform.ap_cpu_0" and edge["target"] == "platform.ap_router"
               and edge["kind"] == "tlm" for edge in graph["edges"])
    assert any(edge["source"] == "platform.system_router" and edge["target"] == "platform.system_to_smd_nci"
               for edge in graph["edges"])
    for edge in graph["edges"]:
        assert edge["source"] in nodes and edge["target"] in nodes
        assert edge["binding"]["reference"].startswith("&")
    assert len({edge["id"] for edge in graph["edges"]}) == len(graph["edges"])
    assert all((ROOT / source["path"]).is_file() for source in graph["sources"])
    assert all((ROOT / node["source"]["path"]).is_file() for node in graph["nodes"])
    json.dumps(graph)


@requires_lua
def test_direction_and_nested_instance_scope(fixture_root):
    graph = topology.get_topology(fixture_root)
    nodes = {node["id"]: node for node in graph["nodes"]}
    assert nodes["platform.nested.cpu"]["qemu_instance"] == "platform.nested.qemu"
    edge = next(e for e in graph["edges"] if e["target"] == "platform.device")
    assert edge["source"] == "platform.router"
    assert edge["source_port"] == "initiator_socket"
    assert edge["target_port"] == "mem"
    assert edge["address"] == 4096
    assert edge["binding"]["owner"] == "platform.device"


@requires_lua
def test_cache_invalidates_source_and_return_isolation(fixture_root):
    graph = topology.get_topology(fixture_root)
    graph["nodes"].clear()
    assert topology.get_topology(fixture_root)["nodes"]
    entry = fixture_root / topology.ENTRYPOINT
    entry.write_text(entry.read_text() + '\nplatform.extra={moduletype="extra"}\n')
    newer = topology.get_topology(fixture_root)
    assert newer["sources"] != graph["sources"]
    assert any(n["id"] == "platform.extra" for n in newer["nodes"])


@requires_lua
def test_unresolved_binding_is_reported_not_invented(fixture_root):
    entry = fixture_root / topology.ENTRYPOINT
    entry.write_text(entry.read_text() + '\nplatform.cpu.mem.bind="&missing.target_socket"\n')
    graph = topology.get_topology(fixture_root)
    assert any("missing.target_socket" in warning for warning in graph["warnings"])
    assert not any(node["id"] == "platform.missing" for node in graph["nodes"])


def test_missing_lua_is_explicit_error():
    with patch.object(topology.shutil, "which", return_value=None):
        with pytest.raises(topology.TopologyError, match="interpreter missing"):
            topology._evaluate({"apollo-qvp.lua": "platform={}"})


def test_missing_entry_is_explicit_error(tmp_path):
    with pytest.raises(topology.TopologyError, match="source graph unavailable"):
        topology.get_topology(tmp_path)


def test_evaluation_timeout_is_explicit_error():
    with patch.object(topology.shutil, "which", return_value="/usr/bin/lua"), patch.object(
            topology.subprocess, "run", side_effect=subprocess.TimeoutExpired("lua", 12)):
        with pytest.raises(topology.TopologyError, match="TimeoutExpired"):
            topology._evaluate({"apollo-qvp.lua": "while true do end"})


@requires_lua
def test_included_source_cache_invalidation(fixture_root):
    entry = fixture_root / topology.ENTRYPOINT
    child = entry.parent / "child.lua"
    child.write_text('return {moduletype="first"}')
    entry.write_text('platform={child=dofile("./child.lua")}')
    first = topology.get_topology(fixture_root)
    child.write_text('return {moduletype="second"}')
    second = topology.get_topology(fixture_root)
    assert first["nodes"][0]["moduletype"] == "first"
    assert second["nodes"][0]["moduletype"] == "second"
    assert first["sources"] != second["sources"]


@requires_lua
@pytest.mark.parametrize("source", [
    'os.execute("touch /tmp/forbidden")',
    'io.open("/etc/passwd")',
    'require("os")',
    'dofile("/etc/passwd")',
])
def test_lua_has_no_file_process_or_module_access(source):
    with pytest.raises(topology.TopologyError, match="Lua evaluation failed"):
        topology._evaluate({"apollo-qvp.lua": source})


@requires_lua
def test_no_inherited_environment(monkeypatch, fixture_root):
    monkeypatch.setenv("QBOX_RDASPEN_ENABLE_AP_CPUS", "false")
    monkeypatch.setenv("QBOX_APOLLO_QMP_DIR", "/tmp/private")
    result = topology._evaluate({"apollo-qvp.lua": '''
assert(os.getenv("QBOX_RDASPEN_ENABLE_AP_CPUS") == "true")
assert(os.getenv("QBOX_APOLLO_QMP_DIR") == nil)
platform={moduletype="Container"}
'''})
    assert result["platform"]["moduletype"] == "Container"


@requires_lua
def test_drawio_native_xml_preserves_nodes_edges(fixture_root):
    graph = topology.get_topology(fixture_root)
    xml = topology.topology_drawio(graph)
    root = ET.fromstring(xml)
    assert root.tag == "mxGraphModel"
    objects = root.findall(".//object")
    assert len(objects) == len(graph["nodes"])
    assert all("parameters" in obj.attrib for obj in objects)
    edge_cells = root.findall('.//mxCell[@edge="1"]')
    assert len(edge_cells) == len(graph["edges"])
    assert all(edge.find("mxGeometry").get("relative") == "1" for edge in edge_cells)
    ids = [element.get("id") for element in root.iter() if element.get("id")]
    assert len(ids) == len(set(ids))
    assert "<!--" not in xml


def test_source_graph_rejects_escape(fixture_root):
    entry = fixture_root / topology.ENTRYPOINT
    entry.write_text('dofile("../outside.lua")')
    with pytest.raises(topology.TopologyError, match="module_outside_root"):
        topology.get_topology(fixture_root)
