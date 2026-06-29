from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/run_test_manifest.py"
sys.path.insert(0, str(ROOT / "scripts/test"))

from run_test_suite_plan import resolve_plan

CURRENT_SUITE = [
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
EXTENDED_REQUIRED = {
    "test_70_mission_based_profiles",
    "test_991_smcf",
    "test_992_safety_island_pfdi",
}
EXTENDED_SKIPPED = {
    "test_10_pfdi",
    "test_10_ras_cpu",
    "test_10_sbistc_integration",
    "test_20_hipc_baremetal",
    "test_50_cryptographic_extension",
}


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


def test_plan_suite_resolution_when_active_config_is_current(tmp_path: Path) -> None:
    # Given: the checked-out Apollo FVP build configuration and deploy metadata.
    out = tmp_path / "plan.json"

    # When: the plan command resolves validation suites.
    result = run_manifest(
        "plan",
        "--build-dir",
        "build",
        "--machine",
        "apollo-fvp",
        "--out",
        str(out),
    )

    # Then: current, extended, and extra suites are deterministically grouped.
    assert result.returncode == 0, result.stderr
    plan = load_json(out)
    assert plan["included"]["validation_current"] == CURRENT_SUITE
    assert EXTENDED_REQUIRED.issubset(plan["included"]["validation_extended"])
    assert EXTENDED_SKIPPED.isdisjoint(plan["included"]["validation_extended"])
    assert "test_99_uefi_secure_boot" not in plan["included"]["validation_extended"]
    assert "test_100_fwu" not in plan["included"]["validation_extended"]
    assert "test_50_cryptographic_extension" not in plan["included"]["validation_extended"]
    excluded = {item["name"]: item["reason"] for item in plan["excluded"]}
    for name in EXTENDED_SKIPPED:
        assert excluded[name] == "excluded_by_hsoc_yocto_build_config"
    assert {
        "extra-static-compileall",
        "extra-project-pytest",
        "qbox-static-full-map",
        "qbox-full-check-only",
        "qbox-full-live-cl0-cl1",
    }.issubset(plan["included"]["extra"])


def test_plan_xen_exclusion_when_virtualization_is_incompatible(tmp_path: Path) -> None:
    # Given: the active .config.yaml disables virtualization for baremetal Apollo.
    out = tmp_path / "plan.json"

    # When: the plan command resolves suites that include Xen candidates.
    result = run_manifest(
        "plan",
        "--build-dir",
        "build",
        "--machine",
        "apollo-fvp",
        "--out",
        str(out),
    )

    # Then: Xen and replaced RD-Aspen tests are excluded with explicit reasons.
    assert result.returncode == 0, result.stderr
    plan = load_json(out)
    included = (
        plan["included"]["validation_current"]
        + plan["included"]["validation_extended"]
        + plan["included"]["extra"]
    )
    excluded = {item["name"]: item["reason"] for item in plan["excluded"]}
    assert "test_40_virtualization" not in included
    assert excluded["test_40_virtualization"] == "excluded_baremetal_no_xen"
    assert excluded["test_41_rt_patch_presence"] == "excluded_apollo_kernel_removes_xen"
    assert excluded["test_01_systemd_boot"] == "replaced_by_auto_ad_nexios_uki_boot"
    assert excluded["domu-lifecycle"] == "excluded_baremetal_no_xen_domu"


def test_plan_xen_exclusion_when_virtualization_test_is_requested() -> None:
    # Given: a fixture with virtualization disabled and test_40 requested.
    manifest = {
        "status": "ok",
        "machine": "apollo-fvp",
        "distro": "auto-ad-nexios",
        "rd_aspen_variant": "cfg2",
        "pc_cpus_count_default": 16,
        "test_suites": ["test_40_virtualization"],
        "config_yaml": {"menu_configuration": {"ARCHITECTURE_VIRTUALIZATION": False}},
    }

    # When: the resolver builds an executable plan.
    plan = resolve_plan(manifest)

    # Then: the requested Xen test is excluded, not included.
    assert "test_40_virtualization" not in plan["included"]["validation_current"]
    excluded = {item["name"]: item["reason"] for item in plan["excluded"]}
    assert excluded["test_40_virtualization"] == "excluded_baremetal_no_xen"
    assert excluded["domu-lifecycle"] == "excluded_baremetal_no_xen_domu"


def test_plan_excludes_hsoc_yocto_skip_entries_when_declared() -> None:
    # Given: hsoc-stack Yocto metadata marks tests unsupported by this build.
    manifest = {
        "status": "ok",
        "machine": "apollo-fvp",
        "distro": "auto-ad-nexios",
        "rd_aspen_variant": "cfg2",
        "pc_cpus_count_default": 16,
        "test_suites": ["ping", "test_00_aspen_boot"],
        "hsoc_run_test_skip_suites": [
            "test_00_aspen_boot",
            "test_70_mission_based_profiles",
        ],
        "hsoc_run_test_skip_extra_lanes": ["extra-sw-ref-stack-unittests"],
        "hsoc_run_test_skip_reason": "excluded_by_hsoc_yocto_build_config",
    }

    # When: the resolver builds an executable plan.
    plan = resolve_plan(manifest)

    # Then: configured skips are removed from every executable lane.
    included = (
        plan["included"]["validation_current"]
        + plan["included"]["validation_extended"]
        + plan["included"]["extra"]
    )
    excluded = {item["name"]: item["reason"] for item in plan["excluded"]}
    assert "test_00_aspen_boot" not in included
    assert "test_70_mission_based_profiles" not in included
    assert "extra-sw-ref-stack-unittests" not in included
    assert excluded["test_00_aspen_boot"] == "excluded_by_hsoc_yocto_build_config"
    assert (
        excluded["extra-sw-ref-stack-unittests"]
        == "excluded_by_hsoc_yocto_build_config"
    )
