from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/compare_qbox_fvp_gic_logs.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "compare_qbox_fvp_gic_logs",
        SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


FVP_GIC_LOG = "\n".join(
    [
        "GICv3: 960 SPIs implemented",
        "GICv3: GICv3 features: 16 PPIs, DirectLPI",
        "GICv3: GICv4 features: DirectLPI RVPEID Valid+Dirty ",
        "ITS@0x0000000020840000: Using GICv4.1 mode 00000000 00000001",
        "ITS@0x0000000020840000: allocated 32768 Interrupt Collections @200001f0000 (flat, esz 2, psz 64K, shr 1)",
        "ITS: Using DirectLPI for VPE invalidation",
    ]
)

QBOX_GIC_LOG = "\n".join(
    [
        "GICv3: 960 SPIs implemented",
        "GICv3: GICv3 features: 16 PPIs",
        "GICv3: GICv4 features: ",
        "ITS@0x0000000020840000: allocated 8192 Interrupt Collections @200001f0000 (flat, esz 8, psz 64K, shr 1)",
    ]
)


def test_parse_gic_evidence_when_fvp_exposes_direct_lpi_features() -> None:
    module = load_module()

    evidence = module.parse_gic_evidence(FVP_GIC_LOG)

    assert evidence["spis"] == 960
    assert evidence["direct_lpi_gicv3"] is True
    assert evidence["direct_lpi_rvpeid_gicv4"] is True
    assert evidence["gicv4_1_mode"] is True
    assert evidence["interrupt_collections"] == 32768
    assert evidence["direct_lpi_vpe_invalidation"] is True


def test_cli_fails_when_qbox_lacks_fvp_gic_parity(tmp_path: Path) -> None:
    fvp_log = tmp_path / "fvp.log"
    qbox_log = tmp_path / "qbox.log"
    output = tmp_path / "report.json"
    fvp_log.write_text(FVP_GIC_LOG, encoding="utf-8")
    qbox_log.write_text(QBOX_GIC_LOG, encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--fvp-log",
            str(fvp_log),
            "--qbox-log",
            str(qbox_log),
            "--expect-fvp-parity",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert completed.returncode == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["status"] == "fail"
    assert set(report["missing_from_qbox"]) == {
        "direct_lpi_gicv3",
        "direct_lpi_rvpeid_gicv4",
        "gicv4_1_mode",
        "interrupt_collections_32768",
        "direct_lpi_vpe_invalidation",
    }


def test_cli_passes_for_fvp_self_compare(tmp_path: Path) -> None:
    fvp_log = tmp_path / "fvp.log"
    output = tmp_path / "report.json"
    fvp_log.write_text(FVP_GIC_LOG, encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--fvp-log",
            str(fvp_log),
            "--qbox-log",
            str(fvp_log),
            "--expect-fvp-parity",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert completed.returncode == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["status"] == "pass"
    assert report["missing_from_qbox"] == []
