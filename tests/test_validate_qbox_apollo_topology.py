from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/validate_qbox_apollo_topology.py"
AP_MAP_SCRIPT = ROOT / "scripts/test/audit_qbox_apollo_ap_memory_map.py"
CONTRACT_DIR = (
    ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block"
)
CONTRACT_FILES = (
    "topology.lua",
    "address_map.lua",
    "transaction_routes.lua",
    "signal_routes.lua",
    "boot_control.lua",
    "software_contract.lua",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_validator(
    emit: Path,
    *,
    contract_dir: Path = CONTRACT_DIR,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--contract-dir",
            str(contract_dir),
            "--emit",
            str(emit),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def copy_contract(tmp_path: Path) -> Path:
    copied = tmp_path / "contract"
    copied.mkdir()
    for name in CONTRACT_FILES:
        shutil.copy2(CONTRACT_DIR / name, copied / name)
    return copied


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert text.count(old) == 1
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def error_ids(report: dict) -> set[str]:
    return {entry["id"] for entry in report["errors"]}


def test_contract_emits_all_route_evidence_and_artifact_hashes(tmp_path: Path) -> None:
    emit = tmp_path / "topology" / "topology.json"

    result = run_validator(emit)

    assert result.returncode == 0, result.stderr
    expected = {
        "topology.json",
        "address-routes.json",
        "transaction-routes.json",
        "irq-routes.json",
        "reset-routes.json",
        "boot-routes.json",
        "software-routes.json",
        "artifacts.json",
        "validation.json",
    }
    assert {path.name for path in emit.parent.iterdir()} == expected

    topology = load_json(emit)
    assert topology["schema_version"] == 1
    assert topology["machine"] == "apollo-qvp"
    assert {router["name"] for router in topology["routers"]} == {
        "system_router",
        "ap_router",
        "smd_router",
        "rse_router",
        "si_cl0_router",
        "si_cl1_router",
    }
    assert topology["validation"]["topology_frozen"] is True
    assert topology["validation"]["compatibility_debt"] == [
        "ap_system_bridge_1_to_1",
        "si_cl0_system_bridge_1_to_1",
        "si_cl1_system_bridge_1_to_1",
    ]

    artifacts = load_json(emit.parent / "artifacts.json")
    local_conf = next(
        entry for entry in artifacts["artifacts"] if entry["name"] == "local_conf"
    )
    assert local_conf["exists"] is True
    assert len(local_conf["sha256"]) == 64
    assert artifacts["configuration"]["machine"] == "apollo-qvp"
    assert artifacts["configuration"]["rd_aspen_variant"] == "cfg2"
    assert artifacts["configuration"]["pc_cpus_count_default"] == 4

    validation = load_json(emit.parent / "validation.json")
    assert validation["status"] == "pass"
    assert validation["errors"] == []


def test_ap_memory_map_audit_accepts_ap_router_bindings(tmp_path: Path) -> None:
    output = tmp_path / "ap-map-audit.json"

    result = subprocess.run(
        [
            sys.executable,
            str(AP_MAP_SCRIPT),
            "--check",
            "coverage",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
    assert load_json(output)["passed"] is True


def test_contract_output_is_stable_for_same_checkout(tmp_path: Path) -> None:
    first = tmp_path / "first" / "topology.json"
    second = tmp_path / "second" / "topology.json"

    first_result = run_validator(first)
    second_result = run_validator(second)

    assert first_result.returncode == 0, first_result.stderr
    assert second_result.returncode == 0, second_result.stderr
    stable_files = (
        "topology.json",
        "address-routes.json",
        "transaction-routes.json",
        "irq-routes.json",
        "reset-routes.json",
        "boot-routes.json",
        "software-routes.json",
    )
    for name in stable_files:
        assert (first.parent / name).read_bytes() == (second.parent / name).read_bytes()


def test_validator_rejects_undocumented_overlap(tmp_path: Path) -> None:
    contract = copy_contract(tmp_path)
    replace_once(
        contract / "address_map.lua",
        'name = "ap_primary_uart"; base = 0x1A400000;',
        'name = "ap_primary_uart"; base = 0x1A410000;',
    )
    emit = tmp_path / "out" / "topology.json"

    result = run_validator(emit, contract_dir=contract)

    assert result.returncode == 1
    report = load_json(emit.parent / "validation.json")
    assert "address:overlap:ap:ap_primary_uart:ap_secure_uart" in error_ids(report)


def test_validator_rejects_nonadjacent_nested_overlap(tmp_path: Path) -> None:
    contract = copy_contract(tmp_path)
    replace_once(
        contract / "address_map.lua",
        '{ name = "ap_rse_mhu_mbx"; base = 0x406B0000; size = 0x00030000; view = "ap"; target = "host_ap_rse_mhu_mbx"; owner = "rse"; access = "secure_rw"; bridge = "ap_to_smd_atu_apu"; alias_of = "ap_to_smd_atu"; priority = 0; reason = "AP secure MHU has a dedicated target inside the programmed ATU aperture"; scope = cfg2; source = guide };',
        '{ name = "ap_rse_mhu_mbx"; base = 0x406B0000; size = 0x00030000; view = "ap"; target = "host_ap_rse_mhu_mbx"; owner = "rse"; access = "secure_rw"; bridge = "ap_to_smd_atu_apu"; scope = cfg2; source = guide };',
    )
    emit = tmp_path / "out" / "topology.json"

    result = run_validator(emit, contract_dir=contract)

    assert result.returncode == 1
    report = load_json(emit.parent / "validation.json")
    assert "address:overlap:ap:ap_to_smd_atu:ap_rse_mhu_mbx" in error_ids(report)


def test_validator_rejects_address_width_overflow(tmp_path: Path) -> None:
    contract = copy_contract(tmp_path)
    replace_once(
        contract / "topology.lua",
        'name = "system"; domain = "system"; width = 52;',
        'name = "system"; domain = "system"; width = 32;',
    )
    emit = tmp_path / "out" / "topology.json"

    result = run_validator(emit, contract_dir=contract)

    assert result.returncode == 1
    report = load_json(emit.parent / "validation.json")
    assert any(item.startswith("address:width:system:") for item in error_ids(report))


def test_validator_rejects_dangling_transaction_initiator(tmp_path: Path) -> None:
    contract = copy_contract(tmp_path)
    replace_once(
        contract / "transaction_routes.lua",
        'initiator = "gpex_dma";',
        'initiator = "missing_gpex_dma";',
    )
    emit = tmp_path / "out" / "topology.json"

    result = run_validator(emit, contract_dir=contract)

    assert result.returncode == 1
    report = load_json(emit.parent / "validation.json")
    assert "transaction:initiator:pcie_dma_to_smmu:missing_gpex_dma" in error_ids(report)
