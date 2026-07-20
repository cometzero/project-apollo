from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/analyze/compare_apollo_fvp_qbox_same_state.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "compare_apollo_fvp_qbox_same_state", SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def make_results(tmp_path: Path, *, shared_hash: bool = True) -> tuple[Path, Path]:
    module = load_module()
    artifact = tmp_path / "rse-flash-image.img"
    artifact.write_bytes(b"same-state")
    fvp_hash = module.sha256_file(artifact)
    qbox_artifact = artifact
    if not shared_hash:
        qbox_artifact = tmp_path / "qbox-rse-flash-image.img"
        qbox_artifact.write_bytes(b"different-state")

    fvp_primary = tmp_path / "fvp-primary.log"
    qbox_primary = tmp_path / "qbox-primary.log"
    common_log = "\n".join(
        [
            "arm-smmu-v3 1c0000000.iommu",
            "ITS [mem 0x300400000-0x30041ffff]",
            "CPU0: Out of Reset (OoR) test OK",
            "CPU1: Out of Reset (OoR) test OK",
            "CPU2: Out of Reset (OoR) test OK",
            "CPU3: Out of Reset (OoR) test OK",
            "failed_units_count:0",
        ]
    )
    fvp_primary.write_text(common_log, encoding="utf-8")
    qbox_primary.write_text(common_log, encoding="utf-8")

    progress = {
        name: {"elapsed_s": index + 1}
        for index, name in enumerate(module.CANONICAL_MARKERS)
    }
    fvp_result = tmp_path / "fvp-result.json"
    write_json(
        fvp_result,
        {
            "passed": True,
            "initial_state": {
                "rse_flash": {
                    "path": str(artifact),
                    "sha256": fvp_hash,
                }
            },
            "domains": {
                name: {"passed": True}
                for name in module.FVP_DOMAIN_MARKERS
            },
            "progress_marker_first_hits": progress,
            "status": {
                "consoles": {
                    "terminal_ns_uart0": {"path": str(fvp_primary)}
                }
            },
        },
    )
    qbox_result = tmp_path / "qbox-result.json"
    write_json(
        qbox_result,
        {
            "passed": True,
            "input_artifacts": {
                "rse_flash": {
                    "exists": True,
                    "path": str(qbox_artifact),
                }
            },
            "rse_flash_state": {
                "action": "ephemeral",
                "source_sha256": module.sha256_file(qbox_artifact),
            },
            "marker_groups": {
                group: {"ready": True}
                for group in module.QBOX_DOMAIN_MARKERS
            },
            "progress_marker_first_hits": progress,
            "console_logs": {"primary_console": str(qbox_primary)},
            "post_login_probe": {
                "requested": True,
                "passed": True,
                "driver_patterns": {
                    "smmu_v3": True,
                    "pfdi_4cpu": True,
                },
            },
        },
    )
    return fvp_result, qbox_result


def test_same_state_comparison_passes_matching_runs(tmp_path: Path) -> None:
    module = load_module()
    fvp_result, qbox_result = make_results(tmp_path)
    map_validation = tmp_path / "map-validation.json"
    write_json(map_validation, {"passed": True})

    result = module.compare(fvp_result, qbox_result, map_validation)

    assert result["passed"] is True
    assert result["artifact_state"]["rse_flash"]["matched"] is True
    assert all(domain["passed"] for domain in result["domains"].values())
    assert result["drivers"]["pfdi_4cpu"]["passed"] is True


def test_same_state_comparison_fails_hash_mismatch(tmp_path: Path) -> None:
    module = load_module()
    fvp_result, qbox_result = make_results(tmp_path, shared_hash=False)
    map_validation = tmp_path / "map-validation.json"
    write_json(map_validation, {"passed": True})

    result = module.compare(fvp_result, qbox_result, map_validation)

    assert result["passed"] is False
    assert result["artifact_state"]["rse_flash"]["matched"] is False
