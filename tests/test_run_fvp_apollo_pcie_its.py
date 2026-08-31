from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/run/run_fvp_apollo_pcie_its.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("fvp_pcie_its", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def profile(tmp_path: Path) -> Path:
    root = tmp_path / "profile"
    root.mkdir()
    fvpconf = root / "profile.fvpconf"
    fvpconf.write_text(
        json.dumps(
            {
                "parameters": {
                    "css.gic_distributor.ITS-count": "1",
                    "pcie_group_0.pcie4.hierarchy_file_name": "<default>",
                    "pcie_group_0.pcie4.pcie_rc.ahci0.endpoint.ats_supported": "true",
                    "pcie_group_0.pcie4.pcie_rc.ahci0.ahci.image_path": str(
                        root / "disk.raw"
                    ),
                }
            }
        ),
        encoding="utf-8",
    )
    (root / "disk.raw").write_bytes(b"disk")
    declared = root / "declared.json"
    declared.write_text(
        json.dumps(
            {
                "model": {"model_present": True},
                "configuration": {
                    "configuration_declared": True,
                    "declared": {
                        "its_count": 1,
                        "hierarchy": "<default>",
                        "ats_supported": True,
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    source = root / "source.py"
    source.write_text("source\n", encoding="utf-8")
    payload = {
        "format_version": 1,
        "verdict": "PASS",
        "configuration": {
            "configuration_declared": True,
            "final_fvpconf": {
                "path": str(fvpconf),
                "sha256": sha(fvpconf),
            },
            "baseline_contract": {"path": str(declared), "sha256": sha(declared)},
        },
        "artifacts": [
            {"path": str(fvpconf), "role": "fvpconf", "sha256": sha(fvpconf)},
            {"path": str(declared), "role": "declared", "sha256": sha(declared)},
        ],
        "source_hashes": [
            {"path": str(source), "role": "source", "sha256": sha(source)}
        ],
        "dt_delivery": {
            "firmware_fip_hw_config": {
                "host_contract": {
                    "node": "/soc/pcie@10040000000",
                    "ecam_base": "0x10040000000",
                    "its_base": "0x20840000",
                    "smmu_base": "0x1c0000000",
                }
            }
        },
    }
    (root / "profile.json").write_text(json.dumps(payload), encoding="utf-8")
    return root


def test_profile_rejects_stale_artifact_and_source(tmp_path: Path) -> None:
    runner = load_runner()
    root = profile(tmp_path)
    verified = runner.verify_profile(root, expected_profile_sha=None)
    assert verified.fvpconf.name == "profile.fvpconf"
    Path(verified.profile["artifacts"][0]["path"]).write_text(
        "changed", encoding="utf-8"
    )
    with pytest.raises(runner.RunError, match="artifact_hash_stale"):
        runner.verify_profile(root, expected_profile_sha=None)
    second = tmp_path / "second"
    second.mkdir()
    root = profile(second)
    source = Path(
        json.loads((root / "profile.json").read_text())["source_hashes"][0]["path"]
    )
    source.write_text("changed\n", encoding="utf-8")
    with pytest.raises(runner.RunError, match="artifact_hash_stale"):
        runner.verify_profile(root, expected_profile_sha=None)


@pytest.mark.parametrize(
    "reason",
    [
        "fvp_process_unobserved",
        "model_configuration_missing",
        "child_pass_semantic_fail",
        "unexpected_dt_source",
        "endpoint_missing",
        "smmu_fault",
        "runtime_contract_fail",
        "cleanup_missing",
        "empty_disk",
        "nomsi_control_inversion",
        "pcie_config_read_stall",
    ],
)
def test_failure_result_is_deterministic_and_qbox_free(
    tmp_path: Path, reason: str
) -> None:
    runner = load_runner()
    output = runner.parse_output_dir(tmp_path / "out", tmp_path)
    payload = runner.failure_result(reason, "a" * 64, output, detail={"test": reason})
    assert payload["status"] == "fail"
    assert payload["reason"] == reason
    assert payload["qbox_started"] is False
    assert json.loads((output.path / "result.json").read_text(encoding="utf-8"))["reason"] == reason
    output.close()


def test_fake_argv_or_child_success_cannot_apply_configuration(tmp_path: Path) -> None:
    runner = load_runner()
    root = profile(tmp_path)
    verified = runner.verify_profile(root, expected_profile_sha=None)
    applied = runner.configuration_applied(
        verified,
        observed_processes=[],
        model_output="configured all parameters",
    )
    assert applied is False
    applied = runner.configuration_applied(
        verified,
        observed_processes=[
            {"pid": 42, "argv": ["FVP_Zena_CSS_Cfg2", "--parameter", "bad=1"]}
        ],
        model_output="configured all parameters",
    )
    assert applied is False


def test_live_dt_contract_rejects_wrong_source_and_normalizes_expected(
    tmp_path: Path,
) -> None:
    runner = load_runner()
    expected = {
        "node": "/soc/pcie@10040000000",
        "ecam_base": "0x10040000000",
        "its_base": "0x20840000",
        "smmu_base": "0x1c0000000",
    }
    with pytest.raises(runner.RunError, match="unexpected_dt_source"):
        runner.verify_live_dt({"node": "/soc/pcie@0"}, expected)
    assert runner.verify_live_dt(dict(expected), expected)["node"] == expected["node"]


def test_runtime_validator_failure_is_not_promoted_by_child_pass(
    tmp_path: Path,
) -> None:
    runner = load_runner()
    runtime = tmp_path / "runtime.json"
    runtime.write_text(
        json.dumps({"status": "fail", "reason": "endpoint_identity"}), encoding="utf-8"
    )
    with pytest.raises(runner.RunError, match="runtime_contract_fail"):
        runner.require_runtime_pass(runtime)


def test_root_bus_no_progress_is_a_bounded_stall_not_a_success(tmp_path: Path) -> None:
    runner = load_runner()
    boot = tmp_path / "boot"
    boot.mkdir()
    log = boot / "terminal_ns_uart0_5004.log"
    log.write_text("PCI host bridge to bus 0004:00\n", encoding="utf-8")
    size, _, _ = runner.pcie_stall_state(boot, 0, time.monotonic())
    _, _, stalled = runner.pcie_stall_state(boot, size, time.monotonic() - 121)
    assert stalled is True
    log.write_text("PCI host bridge to bus 0004:00\n0004:00:1f.0\n", encoding="utf-8")
    _, _, stalled = runner.pcie_stall_state(
        boot, log.stat().st_size, time.monotonic() - 121
    )
    assert stalled is False
