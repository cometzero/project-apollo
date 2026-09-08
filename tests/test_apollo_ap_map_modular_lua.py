from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "scripts/test/audit_qbox_apollo_ap_memory_map.py"
MODULAR = ROOT / "scripts/test/apollo_ap_map_lua.py"


def load_module(path: Path, name: str):
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_numeric_table_parser_preserves_legacy_scalars_and_modular_fields() -> None:
    audit = load_module(AUDIT, "apollo_map_audit_tables")
    constants, _tables = audit.parse_constants(
        "LEGACY_BASE = 0x1000\n"
        "local AP_ADDRESS = {\n"
        "    uart = 0x1A400000;\n"
        "}\n"
        "local AP_SIZE = {\n"
        "    uart = 0x10000;\n"
        "}\n"
    )
    assert constants["LEGACY_BASE"] == 0x1000
    assert constants["AP_ADDRESS.uart"] == 0x1A400000
    assert constants["AP_SIZE.uart"] == 0x10000


def test_current_modular_map_resolves_real_ap_components() -> None:
    audit = load_module(AUDIT, "apollo_map_audit_current")
    sockets = audit.current_coverage(ROOT)
    identities = {
        (socket.object_name, socket.socket_name, socket.address, socket.size)
        for socket in sockets
    }
    assert ("host_ap_shared_sram", "target_socket", 0x0, 0x100000) in identities
    assert ("ap_primary_uart", "target_socket", 0x1A400000, 0x10000) in identities
    assert ("pinctrl_peri0", "target_socket", 0x301E0000, 0x10000) in identities
    assert ("pinctrl_peri1", "target_socket", 0x301F0000, 0x10000) in identities
    assert ("host_ap_dram1", "target_socket", 0x80000000, 0x7F000000) in identities
    assert any(identity[0] == "ap_smmu_0" and identity[2] == 0x1C0000000 for identity in identities)
    assert any(identity[0] == "ap_cl0_ni710ae_fmu" for identity in identities)


def test_module_graph_loads_dofile_tree_and_rejects_missing_cycle_and_malformed(
    tmp_path: Path,
) -> None:
    modular = load_module(MODULAR, "apollo_map_modules")
    root = tmp_path / "entry.lua"
    child = tmp_path / "child.lua"
    child.write_text("return {}\n", encoding="utf-8")
    root.write_text('local child = dofile("child.lua")\n', encoding="utf-8")
    assert set(modular.load_module_graph(root)) == {"entry.lua", "child.lua"}

    root.write_text('dofile("missing.lua")\n', encoding="utf-8")
    with pytest.raises(modular.LuaModuleError, match="missing_module"):
        modular.load_module_graph(root)

    child.write_text('dofile("entry.lua")\n', encoding="utf-8")
    root.write_text('dofile("child.lua")\n', encoding="utf-8")
    with pytest.raises(modular.LuaModuleError, match="module_cycle"):
        modular.load_module_graph(root)

    root.write_text('dofile("child.lua"\n', encoding="utf-8")
    with pytest.raises(modular.LuaModuleError, match="malformed_dofile"):
        modular.load_module_graph(root)
