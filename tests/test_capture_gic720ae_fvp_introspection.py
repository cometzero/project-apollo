from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / "scripts/test/capture_gic720ae_fvp_introspection.py"
AUDIT = ROOT / "scripts/test/audit_gic720ae_reference_contract.py"
CAPTURE_SCHEMA = ROOT / "tests/schemas/gic720ae-fvp-introspection.schema.json"
CONTRACT = ROOT / "doc/validation/gic-720ae/reference-contract.yaml"


def write_fake_fvp(path: Path) -> None:
    path.write_text(
        "#!/bin/sh\n"
        "case \"$1\" in\n"
        "  --version) printf '%s\\n' 'Fast Models 11.31.25' ;;\n"
        "  --list-instances) printf '%s\\n' 'css.gic_distributor: GIC720AE' 'css.smb.si.gic: GIC720AE' ;;\n"
        "  --list-params) cat <<'EOF'\n"
        "css.gic_distributor.SPI-blocks=30\n"
        "css.gic_distributor.PPI-count=16\n"
        "css.gic_distributor.extended-ppi-count=0\n"
        "css.gic_distributor.ITS-count=1\n"
        "css.gic_distributor.IIDR=117445691\n"
        "css.gic_distributor.enable-multiple-views-feature=1\n"
        "css.gic_distributor.enable_a4s=0\n"
        "css.gic_distributor.consolidators=\n"
        "css.gic_distributor.add-output-cpu-wake-request-signal-from-redistributor=0\n"
        "css.gic_distributor.has_nmi=0\n"
        "css.gic_distributor.GICR-invalidate-registers-implemented=0\n"
        "css.smb.si.gic.SPI-blocks=62\n"
        "css.smb.si.gic.extended-SPI-count=1024\n"
        "css.smb.si.gic.PPI-count=16\n"
        "css.smb.si.gic.extended-ppi-count=64\n"
        "css.smb.si.gic.CPU-affinities=0.0.0.0,0.1.0.0,0.1.1.0,0.1.2.0,0.1.3.0\n"
        "css.smb.si.gic.IIDR=117445691\n"
        "css.smb.si.gic.enable-multiple-views-feature=1\n"
        "css.smb.si.gic.enable_a4s=0\n"
        "css.smb.si.gic.consolidators=\n"
        "css.smb.si.gic.add-output-cpu-wake-request-signal-from-redistributor=0\n"
        "css.smb.si.gic.has_nmi=0\n"
        "css.smb.si.gic.GICR-invalidate-registers-implemented=0\n"
        "css.cmn.enable_a4s=0\n"
        "EOF\n"
        "esac\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def test_capture_and_audit_accept_fresh_cfg2_introspection_when_contract_matches(tmp_path: Path) -> None:
    # Given: a deterministic cfg2-shaped FVP executable and an empty output location.
    fvp = tmp_path / "FVP_Zena_CSS_Cfg2"
    output_dir = tmp_path / "introspection"
    output = tmp_path / "audit.json"
    write_fake_fvp(fvp)

    # When: the capture and reference-contract CLIs consume the fresh output.
    capture = subprocess.run(
        [sys.executable, str(CAPTURE), "--fvp-executable", str(fvp), "--output-dir", str(output_dir), "--schema", str(CAPTURE_SCHEMA)],
        cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    audit = subprocess.run(
        [sys.executable, str(AUDIT), "--introspection", str(output_dir / "fvp-gic-introspection.txt"), "--introspection-receipt", str(output_dir / "receipt.json"), "--contract", str(CONTRACT), "--output", str(output)],
        cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )

    # Then: the receipt contains exactly three fresh argv records and all rows classify.
    assert capture.returncode == 0, capture.stderr
    receipt = json.loads((output_dir / "receipt.json").read_text(encoding="utf-8"))
    assert [record["argv"][-1] for record in receipt["commands"]] == ["--version", "--list-instances", "--list-params"]
    assert audit.returncode == 0, audit.stderr
    assert {row["classification"] for row in json.loads(output.read_text(encoding="utf-8"))["rows"]} <= {"active", "inactive", "unverifiable"}


def test_capture_rejects_a_symlinked_executable_when_descriptor_trust_is_required(tmp_path: Path) -> None:
    # Given: a symlink in place of the explicit executable input.
    target = tmp_path / "target"
    link = tmp_path / "FVP_Zena_CSS_Cfg2"
    write_fake_fvp(target)
    link.symlink_to(target)

    # When: capture attempts to establish the no-follow descriptor chain.
    result = subprocess.run(
        [sys.executable, str(CAPTURE), "--fvp-executable", str(link), "--output-dir", str(tmp_path / "out"), "--schema", str(CAPTURE_SCHEMA)],
        cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )

    # Then: it fails closed rather than executing the symlink target.
    assert result.returncode != 0
    assert '"reason": "invalid_executable"' in result.stderr


def test_audit_rejects_mutated_or_missing_receipt_provenance_when_fresh_evidence_is_required(tmp_path: Path) -> None:
    fvp = tmp_path / "FVP_Zena_CSS_Cfg2"
    output_dir = tmp_path / "introspection"
    write_fake_fvp(fvp)
    capture = subprocess.run(
        [sys.executable, str(CAPTURE), "--fvp-executable", str(fvp), "--output-dir", str(output_dir), "--schema", str(CAPTURE_SCHEMA)],
        cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    assert capture.returncode == 0, capture.stderr
    pristine = json.loads((output_dir / "receipt.json").read_text(encoding="utf-8"))
    mutations = [
        lambda receipt: receipt["commands"][0].pop("env"),
        lambda receipt: receipt["commands"][0].__setitem__("started_at_utc", "not-a-timestamp"),
        lambda receipt: receipt["commands"][2].__setitem__("cwd", "/tmp"),
        lambda receipt: receipt["commands"][1].__setitem__("stdout_sha256", "deadbeef"),
        lambda receipt: receipt["executable"].__setitem__("sha256", "stale"),
        lambda receipt: receipt["commands"][1]["argv"].__setitem__(0, "/wrong/executable"),
        lambda receipt: receipt["commands"][1]["exec_argv"].__setitem__(0, "/proc/self/fd/999999"),
    ]
    for index, mutate in enumerate(mutations):
        receipt = json.loads(json.dumps(pristine))
        mutate(receipt)
        receipt_path = output_dir / f"mutated-{index}.json"
        output = tmp_path / f"audit-{index}.json"
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(AUDIT), "--introspection", str(output_dir / "fvp-gic-introspection.txt"), "--introspection-receipt", str(receipt_path), "--contract", str(CONTRACT), "--output", str(output)],
            cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        assert result.returncode == 2, result.stdout
        assert '"reason": "invalid_introspection_receipt"' in result.stderr
