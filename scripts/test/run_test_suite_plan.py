from __future__ import annotations

from typing import Final


type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]

DEMO_SUITE_BASE: Final = [
    "test_00_rse",
    "test_00_secure_partition",
    "test_10_linuxboot",
    "test_10_linuxlogin",
    "test_10_ping",
    "test_10_ssh",
    "test_10_pfdi",
    "test_10_ras_cpu",
    "test_10_sbistc_integration",
    "test_10_safetydiagnostics_ssu_fmu",
    "test_20_fvp_devices",
    "test_40_rse_fw_encryption",
    "test_50_trusted_services",
    "test_50_cryptographic_extension",
    "test_60_cpuidle_cstates",
    "test_60_cpu_frequency",
    "test_90_ap_warm_reset",
    "test_99_linuxshutdown",
    "test_99_uefi_secure_boot",
    "test_100_fwu",
    "test_991_smcf",
]
CFG2_DEMO_SUITE: Final = [
    "test_10_pfdi_monitor_on_si",
    "test_10_safety_island",
    "test_20_hipc_baremetal",
    "test_992_safety_island_pfdi",
]
VIRTUALIZATION_EXCLUSIONS: Final = [
    {
        "name": "test_40_virtualization",
        "reason": "excluded_baremetal_no_xen",
        "source_suite": "TEST_SUITES:demos:virtualization",
    },
    {
        "name": "test_41_rt_patch_presence",
        "reason": "excluded_apollo_kernel_removes_xen",
        "source_suite": "TEST_SUITES:demos:virtualization",
    },
    {
        "name": "domu-lifecycle",
        "reason": "excluded_baremetal_no_xen_domu",
        "source_suite": "TEST_SUITES:demos:virtualization",
        "source_paths": [
            "sw-ref-stack/yocto/meta-arm-auto-solutions/classes/arm_auto_solutions_image_features.bbclass",
            "sw-ref-stack/yocto/meta-arm-auto-solutions/conf/multiconfig/domu.conf",
            "sw-ref-stack/yocto/kas/virtualization.yml",
        ],
        "note": "DomU lifecycle requires Xen virtualization, Dom0, and BBMULTICONFIG domu.",
    },
]
SYSTEMD_BOOT_EXCLUSION: Final = {
    "name": "test_01_systemd_boot",
    "reason": "replaced_by_auto_ad_nexios_uki_boot",
    "source_suite": "fvp-rd-aspen TEST_SUITES",
}
EXCLUDED_TEST_NAMES: Final = {
    "test_01_systemd_boot",
    "test_40_virtualization",
    "test_41_rt_patch_presence",
}
EXTRA_LANES: Final = [
    "extra-static-compileall",
    "extra-project-pytest",
    "extra-sw-ref-stack-unittests",
    "qbox-static-full-map",
    "qbox-static-core-boundary",
    "qbox-static-ap-memory-map",
    "qbox-static-boot-sequence",
    "qbox-ctest-list",
    "qbox-ctest-rse-components",
    "qbox-full-check-only",
    "qbox-full-live-cl0-cl1",
]


def _str_list(value: JsonValue) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _str_value(value: JsonValue) -> str:
    if isinstance(value, str):
        return value
    return ""


def _int_value(value: JsonValue) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return 0


def _cfg2_entries(manifest: JsonObject) -> list[str]:
    if _str_value(manifest.get("rd_aspen_variant")) == "cfg2":
        return CFG2_DEMO_SUITE.copy()
    return []


def _pc16_entries(manifest: JsonObject) -> list[str]:
    if _int_value(manifest.get("pc_cpus_count_default")) == 16:
        return ["test_70_mission_based_profiles"]
    return []


def _current_suite(manifest: JsonObject) -> list[str]:
    return [test for test in _str_list(manifest.get("test_suites")) if test not in EXCLUDED_TEST_NAMES]


def resolve_plan(manifest: JsonObject) -> JsonObject:
    if manifest.get("status") == "blocked":
        return manifest
    extended = DEMO_SUITE_BASE + _cfg2_entries(manifest) + _pc16_entries(manifest)
    return {
        "status": "ok",
        "machine": _str_value(manifest.get("machine")),
        "distro": _str_value(manifest.get("distro")),
        "included": {
            "validation_current": _current_suite(manifest),
            "validation_extended": extended,
            "extra": EXTRA_LANES.copy(),
        },
        "excluded": [SYSTEMD_BOOT_EXCLUSION, *VIRTUALIZATION_EXCLUSIONS],
    }
