from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/test/run_test_manifest.py"

SPEC = importlib.util.spec_from_file_location(
    "run_test_suite_plan",
    ROOT / "scripts/test/run_test_suite_plan.py",
)
assert SPEC is not None
assert SPEC.loader is not None
RUN_TEST_SUITE_PLAN = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RUN_TEST_SUITE_PLAN
SPEC.loader.exec_module(RUN_TEST_SUITE_PLAN)
resolve_plan = RUN_TEST_SUITE_PLAN.resolve_plan

CURRENT_SUITE = [
    "test_00_rse.RseTest.test_normal_boot",
    "test_00_secure_partition",
    "test_10_linuxboot",
    "test_10_linuxlogin",
    "ping",
    "ssh",
    "test_10_ping",
    "test_10_ssh",
    "test_00_fvp_boot",
    "test_00_linux_boot",
    "test_60_linux_connectivity",
    "test_00_apollo_uki_boot",
    "test_10_safety_island",
    "test_10_safetydiagnostics_ssu_fmu",
    "test_20_aspen_ap_dsu",
    "test_20_fvp_devices",
    "test_30_configurable_pc_cores.ConfiguredPCCPUSTest."
    "test_configured_pc_cpus_in_linux",
]
POWER_SUITE = {
    "test_00_rse.RseTest.test_measured_boot",
    "test_00_rse.RseTest.test_scmi_poweroff",
    "test_00_rse.RseTest.test_scmi_reboot",
    "fvp_boot",
}
EXTENDED_REQUIRED = {
    "test_02_safety_boot.TestSafetyBoot.test_lbist",
    "test_02_safety_boot.TestSafetyBoot.test_mbist",
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
    current = plan["included"]["validation_current"]
    assert current.index("test_10_linuxboot") < current.index("test_10_linuxlogin")
    assert POWER_SUITE.issubset(plan["included"]["validation_power"])
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


def test_functional_plan_excludes_tests_that_restart_or_stop_fvp() -> None:
    manifest = {
        "status": "ok",
        "machine": "apollo-qvp",
        "distro": "auto-ad-nexios",
        "rd_aspen_variant": "cfg2",
        "pc_cpus_count_default": 4,
        "test_suites": [
            "test_00_rse",
            "test_00_secure_partition",
            "test_10_linuxboot",
            "test_10_linuxlogin",
            "test_10_ping",
            "test_10_ssh",
            "test_90_ap_warm_reset",
            "test_99_linuxshutdown",
            "test_30_configurable_pc_cores",
            "fvp_boot",
        ],
    }

    plan = resolve_plan(manifest)

    functional = plan["included"]["validation_current"]
    assert "test_90_ap_warm_reset" not in functional
    assert "test_99_linuxshutdown" not in functional
    assert "fvp_boot" not in functional
    assert functional == CURRENT_SUITE


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
