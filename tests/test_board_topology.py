"""Launch-source and attachment contracts; existing AutoSD API stays unchanged."""
import json
from pathlib import Path
import shutil
from xml.etree import ElementTree as ET

import pytest

from scripts.autosd_dashboard import board_topology as board
from scripts.autosd_dashboard import topology

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not any(shutil.which(n) for n in ("lua5.4", "lua5.3", "lua", "luajit")),
                                reason="Lua interpreter required")


@pytest.fixture
def fixture(tmp_path):
    entry = tmp_path / topology.ENTRYPOINT
    entry.parent.mkdir(parents=True)
    entry.write_text('''
platform={moduletype="Container", router={moduletype="router"},
  device={moduletype="peripheral",enabled=true,
    mem={address=0,size=0,bind="&router.initiator_socket"}},
  high={moduletype="memory",mem={address="0x123456789abcdeff",
    size=4096,relative_addresses=false,bind="&router.initiator_socket"}},
  uart={moduletype="char_backend_socket",server=false,address=os.getenv("ENDPOINT") or "unset"}}
if os.getenv("QBOX_RDASPEN_ENABLE_AP_CPUS") == "true" then
  platform.ap_cpu_0={moduletype="cpu_arm"}
end
''')
    run = tmp_path / "run"
    launch = {"run_id": "test-run", "conf": str(entry), "environment": {}, "platform_params": [],
              "provider": {"executable": "/test/platforms-vp"}}
    return tmp_path, run, launch


def write_status(run, **values):
    run.mkdir(exist_ok=True)
    (run / "tc397-status.json").write_text(json.dumps({
        "qemu_command": ["qemu-system-tricore", "-M", "KIT_AURIX_TC397B_TRB"], **values}))


def test_preview_does_not_freeze_or_claim_effective_configuration(fixture):
    root, run, _ = fixture
    graph = board.get_board_topology(root, run)
    assert graph["evidence"] == "source-preview"
    assert graph["frozen"] is False
    assert not (run / "board-topology.json").exists()
    assert any(n["id"] == "platform.ap_cpu_0" for n in graph["nodes"])


def test_actual_env_not_host_or_preview_default_and_provider_path(fixture, monkeypatch):
    root, run, launch = fixture
    monkeypatch.setenv("ENDPOINT", "leaked-host-value")
    monkeypatch.setenv("QBOX_RDASPEN_ENABLE_AP_CPUS", "true")
    provider = root / "provider" / "selected.lua"
    provider.parent.mkdir()
    provider.write_text(Path(launch["conf"]).read_text())
    launch.update(conf=str(provider), environment={"ENDPOINT": "127.0.0.1:12345"})
    graph = board.get_board_topology(root, run, launch=launch)
    nodes = {n["id"]: n for n in graph["nodes"]}
    assert "platform.ap_cpu_0" not in nodes
    assert nodes["platform.uart"]["parameters"]["address"] == "127.0.0.1:12345"
    assert nodes["platform.uart"]["source"]["path"] == "provider/selected.lua"
    assert len(nodes["platform.uart"]["source"]["sha256"]) == 64


def test_snapshot_survives_source_changes_and_return_mutation(fixture):
    root, run, launch = fixture
    graph = board.get_board_topology(root, run, launch=launch)
    original = json.loads(json.dumps(graph))
    graph["nodes"].clear()
    Path(launch["conf"]).write_text("invalid Lua now")
    assert board.get_board_topology(root, run, launch=launch) == original
    assert len(original["snapshot"]["fingerprint"]) == 64


def test_snapshot_rejects_another_run(fixture):
    root, run, launch = fixture
    board.get_board_topology(root, run, launch=launch)
    launch["run_id"] = "different-run"
    with pytest.raises(board.TopologyError, match="another run"):
        board.get_board_topology(root, run, launch=launch)


def test_64_bit_zero_and_unknown_window_size(fixture):
    root, run, launch = fixture
    graph = board.get_board_topology(root, run, launch=launch)
    nodes = {n["id"]: n for n in graph["nodes"]}
    window = nodes["platform.high"]["windows"][0]
    assert window["address"] == "0x123456789abcdeff"
    assert window["end"] == "0x123456789abceefe"
    assert window["relative_addresses"] is False
    assert window["address_space"] == "&router.initiator_socket"
    zero = nodes["platform.device"]["windows"][0]
    assert zero["address"] == zero["size"] == "0x0"
    assert "end" not in zero
    assert nodes["platform.uart"]["windows"] == []


def test_declared_scalar_cci_override_and_unresolved_marker(fixture):
    root, run, launch = fixture
    launch["platform_params"] = ["platform.device.mem.address=0x1000", "platform.device.enabled=false",
                                 "platform.high.mem.size=2048", "platform.unknown=1"]
    graph = board.get_board_topology(root, run, launch=launch)
    nodes = {n["id"]: n for n in graph["nodes"]}
    assert nodes["platform.device"]["parameters"]["mem"]["address"] == "0x1000"
    assert nodes["platform.device"]["parameters"]["enabled"] is False
    assert nodes["platform.high"]["windows"][0]["size"] == "0x800"
    assert not graph["snapshot"]["run_exact"]
    assert len(graph["snapshot"]["resolved_overrides"]) == 3
    assert len(graph["snapshot"]["unresolved_overrides"]) == 1


def test_64_bit_cci_integer_preserved(fixture):
    root, run, launch = fixture
    launch["platform_params"] = ["platform.device.mem.address=0x123456789abcdeff"]
    graph = board.get_board_topology(root, run, launch=launch)
    node = next(n for n in graph["nodes"] if n["id"] == "platform.device")
    assert node["windows"][0]["address"] == "0x123456789abcdeff"


def test_unsafe_floating_address_cannot_claim_exact_64_bits():
    with pytest.raises(board.TopologyError, match="precision unavailable"):
        board._safe_numbers({"address": float(0x123456789abcdeff)})


def test_manifest_from_disk_and_only_matching_uart_attachment(fixture):
    root, run, launch = fixture
    endpoint = "127.0.0.1:12345"
    launch["environment"] = {"ENDPOINT": endpoint}
    write_status(run, uart_endpoint=endpoint, safety_endpoint="127.0.0.1:54321", gpio_endpoint=None)
    (run / "board-launch.json").write_text(json.dumps(launch))
    graph = board.get_board_topology(root, run)
    links = {a["id"]: a for a in graph["attachments"]}
    assert links["uart_endpoint"]["connection"] == "CONFIGURED_ENDPOINT_MATCH"
    assert links["safety_endpoint"]["connection"] == "UNCONFIRMED"
    edges = [e for e in graph["edges"] if e["provenance"] == "launcher-attached"]
    assert len(edges) == 1 and edges[0]["target"] == "platform.uart"
    assert all("RUNNING" not in json.dumps(e) for e in edges)
    assert ET.fromstring(topology.topology_drawio(graph)).tag == "mxGraphModel"


def test_can_data_route_excludes_registry(fixture):
    root, run, launch = fixture
    endpoint = "127.0.0.1:24680"
    write_status(run, qemu_command=["qemu", "-global", "tc397-can.chardev=tc397can"],
                 sil_kit={"can_endpoint": endpoint, "network": "VehicleCAN", "registry_uri": "silkit://127.0.0.1:1",
                          "participant_names": {"bridge": "bridge", "restbus": "restbus"},
                          "processes": [{"role": "bridge", "command": ["bridge", "--qemu-endpoint", endpoint]},
                                        {"role": "registry", "command": ["registry"]},
                                        {"role": "restbus", "command": ["restbus"]}]})
    graph = board.get_board_topology(root, run, launch=launch)
    edges = [e for e in graph["edges"] if e["kind"] == "can"]
    assert len(edges) == 2
    assert not any("registry" in e["source"] or "registry" in e["target"] for e in edges)


def test_rejected_include_escape_not_replaced_with_static_preview(fixture):
    root, run, launch = fixture
    Path(launch["conf"]).write_text('dofile("../outside.lua")')
    with pytest.raises(board.TopologyError, match="module_outside_root"):
        board.get_board_topology(root, run, launch=launch)
    assert not (run / "board-topology.json").exists()


def test_current_real_source_and_actual_attachments(tmp_path):
    launch = {"run_id": "real-source-test", "conf": str(ROOT / topology.ENTRYPOINT),
              "environment": {"QBOX_RDASPEN_ENABLE_AP_CPUS": "true",
                              "QBOX_APOLLO_VMCU_UART_ENDPOINT": "127.0.0.1:12001",
                              "QBOX_APOLLO_VMCU_SAFETY_ENDPOINT": "127.0.0.1:12002",
                              "QBOX_APOLLO_VMCU_GPIO_ENDPOINT": "127.0.0.1:12003"}, "platform_params": []}
    write_status(tmp_path, uart_endpoint="127.0.0.1:12001", safety_endpoint="127.0.0.1:12002",
                 gpio_endpoint="127.0.0.1:12003")
    graph = board.get_board_topology(ROOT, tmp_path, launch=launch)
    assert len(graph["nodes"]) > 300
    assert graph["warnings"] == []
    assert all(a["connection"] == "CONFIGURED_ENDPOINT_MATCH" for a in graph["attachments"])
    nodes = {n["id"]: n for n in graph["nodes"]}
    assert "platform.vmcu_uart_socket" in nodes
    assert "platform.vmcu_safety_sink" not in nodes
    assert nodes["platform.ap_dw_uart_2"]["parameters"]["backend_socket"]["bind"] == "&vmcu_uart_socket.biflow_socket"
    assert nodes["platform.si_cl0_vmcu_uart"]["windows"][0]["address"] == "0x2a820000"
    assert all(n["source"].get("sha256") for n in graph["nodes"])
