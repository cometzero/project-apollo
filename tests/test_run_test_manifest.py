from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/run_test_manifest.py"


def run_manifest(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_inspect_writes_active_apollo_manifest_when_config_is_current(tmp_path: Path) -> None:
    # Given: the checked-out Apollo FVP build configuration and deploy metadata.
    out = tmp_path / "manifest.json"

    # When: the manifest helper inspects the active build tree.
    result = run_manifest(
        "inspect",
        "--build-dir",
        "build",
        "--machine",
        "apollo-fvp",
        "--out",
        str(out),
    )

    # Then: it exits successfully and snapshots the active config values.
    assert result.returncode == 0, result.stderr
    manifest = load_json(out)
    assert manifest["machine"] == "apollo-fvp"
    assert manifest["distro"] == "auto-ad-nexios"
    assert manifest["rd_aspen_variant"] == "cfg2"
    assert manifest["pc_cpus_count_default"] == 4
    assert manifest["tmpdir"] in {"${TOPDIR}/tmp_baremetal", "tmp_baremetal"}
    assert {"baremetal", "demos"}.issubset(manifest["extra_image_features"])
    assert "testimage" in manifest["image_classes"]
    assert manifest["test_suites"] == [
        "ping",
        "ssh",
        "test_00_rse",
        "test_00_secure_partition",
        "test_01_auto_ad_nexios_uki_boot",
        "test_02_safety_boot",
        "test_10_linuxboot",
        "test_20_aspen_ap_dsu",
        "test_30_configurable_pc_cores",
        "fvp_boot",
        "fvp_devices",
    ]
    assert manifest["hsoc_run_test_skip_suites"] == [
        "test_00_aspen_boot",
        "test_10_pfdi",
        "test_10_ras_cpu",
        "test_10_sbistc_integration",
        "test_20_hipc_baremetal",
        "test_50_cryptographic_extension",
        "test_99_uefi_secure_boot",
        "test_100_fwu",
    ]
    assert manifest["test_fvp_devices"] == [
        "rtc",
        "watchdog",
        "networking",
        "virtiorng",
        "cpu_hotplug",
    ]
    assert manifest["test_target"] == "HSOCOEFVPTarget"
    assert manifest["test_target_ip"] == "127.0.0.1:2222"
    assert manifest["fvp_exe"] == "FVP_Zena_CSS_Cfg2"
    assert manifest["fvpconf"]["exe"] == "FVP_Zena_CSS_Cfg2"


def test_inspect_reports_blocked_missing_artifact_when_machine_is_unknown(
    tmp_path: Path,
) -> None:
    # Given: a machine name that has no deployed test artifacts.
    out = tmp_path / "missing.json"

    # When: the helper inspects that machine.
    result = run_manifest(
        "inspect",
        "--build-dir",
        "build",
        "--machine",
        "missing-machine",
        "--out",
        str(out),
    )

    # Then: it exits with the blocked code and writes a structured reason.
    assert result.returncode == 2
    report = load_json(out)
    assert report["status"] == "blocked"
    assert report["reason"] == "blocked_missing_artifact"
    assert report["machine"] == "missing-machine"
    assert "missing-machine" in report["message"]


def test_write_conf_uses_active_override_for_extended_suite(tmp_path: Path) -> None:
    # Given: the Apollo FVP distro defines TEST_SUITES with machine/distro overrides.
    run_dir = tmp_path / "run"

    # When: the helper writes an extended OEQA lane conf.
    result = run_manifest(
        "write-conf",
        "--build-dir",
        "build",
        "--machine",
        "apollo-fvp",
        "--run-dir",
        str(run_dir),
        "--kind",
        "extended",
    )

    # Then: the generated assignment also targets the active override tuple.
    assert result.returncode == 0, result.stderr
    conf_path = Path(result.stdout.strip())
    conf = conf_path.read_text(encoding="utf-8")
    tokens = conf.replace('"', " ").split()
    assert 'TEST_SUITES = "' in conf
    assert 'TEST_SUITES:apollo-fvp:auto-ad-nexios = "' in conf
    assert (
        'TEST_FVP_DEVICES = '
        '"rtc watchdog networking virtiorng cpu_hotplug"'
    ) in conf
    assert (
        'TEST_FVP_DEVICES:apollo-fvp:auto-ad-nexios = '
        '"rtc watchdog networking virtiorng cpu_hotplug"'
    ) in conf
    assert "test_100_fwu" not in conf
    assert "test_10_pfdi" not in tokens
    assert "test_10_ras_cpu" not in tokens
    assert "test_10_sbistc_integration" not in tokens
    assert "test_20_hipc_baremetal" not in tokens
    assert "test_50_cryptographic_extension" not in tokens
    assert "test_99_uefi_secure_boot" not in conf
