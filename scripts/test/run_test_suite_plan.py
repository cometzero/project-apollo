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
VIRTUALIZATION_EXCLUSIONS: Final[list[JsonObject]] = [
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
SYSTEMD_BOOT_EXCLUSION: Final[JsonObject] = {
    "name": "test_01_systemd_boot",
    "reason": "replaced_by_auto_ad_nexios_uki_boot",
    "source_suite": "fvp-rd-aspen TEST_SUITES",
}
EXCLUDED_TEST_NAMES: Final = {
    "test_01_systemd_boot",
    "test_40_virtualization",
    "test_41_rt_patch_presence",
}
FUNCTIONAL_SINGLE_BOOT_SUITE: Final = [
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
BIST_EXTENDED_SUITE: Final = [
    "test_02_safety_boot.TestSafetyBoot.test_lbist",
    "test_02_safety_boot.TestSafetyBoot.test_mbist",
]
POWER_REBOOT_SUITE: Final = [
    "test_00_rse.RseTest.test_normal_boot",
    "test_00_rse.RseTest.test_measured_boot",
    "test_00_rse.RseTest.test_scmi_poweroff",
    "test_00_rse.RseTest.test_scmi_reboot",
    "fvp_boot",
]
HSOC_SKIP_REASON: Final = "excluded_by_hsoc_yocto_build_config"
HSOC_SKIP_SUITE_SOURCE: Final = "HSOC_RUN_TEST_SKIP_SUITES"
HSOC_SKIP_EXTRA_SOURCE: Final = "HSOC_RUN_TEST_SKIP_EXTRA_LANES"
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


def _json_strings(values: list[str]) -> list[JsonValue]:
    return [value for value in values]


def _json_objects(values: list[JsonObject]) -> list[JsonValue]:
    return [value for value in values]


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


def _hsoc_skip_suites(manifest: JsonObject) -> list[str]:
    return _str_list(manifest.get("hsoc_run_test_skip_suites"))


def _hsoc_skip_extra_lanes(manifest: JsonObject) -> list[str]:
    return _str_list(manifest.get("hsoc_run_test_skip_extra_lanes"))


def _hsoc_skip_reason(manifest: JsonObject) -> str:
    return _str_value(manifest.get("hsoc_run_test_skip_reason")) or HSOC_SKIP_REASON


def _filter_entries(entries: list[str], skip_entries: list[str]) -> list[str]:
    skipped = set(skip_entries)
    return [entry for entry in entries if entry not in skipped]


def _skip_base_names(skip_entries: list[str]) -> set[str]:
    return {entry.split(".")[0] for entry in skip_entries}


def _hsoc_exclusions(names: list[str], reason: str, source: str) -> list[JsonObject]:
    return [{"name": name, "reason": reason, "source_suite": source} for name in names]


def _current_suite(manifest: JsonObject) -> list[str]:
    skipped = set(EXCLUDED_TEST_NAMES) | set(_hsoc_skip_suites(manifest))
    skip_bases = _skip_base_names(list(skipped))
    return [
        test
        for test in FUNCTIONAL_SINGLE_BOOT_SUITE
        if test not in skipped and test.split(".")[0] not in skip_bases
    ]


def _power_reboot_suite(manifest: JsonObject) -> list[str]:
    skipped = set(EXCLUDED_TEST_NAMES) | set(_hsoc_skip_suites(manifest))
    skip_bases = _skip_base_names(list(skipped))
    return [
        test
        for test in POWER_REBOOT_SUITE
        if test not in skipped and test.split(".")[0] not in skip_bases
    ]


def resolve_plan(manifest: JsonObject) -> JsonObject:
    if manifest.get("status") == "blocked":
        return manifest
    skip_suites = _hsoc_skip_suites(manifest)
    skip_extra = _hsoc_skip_extra_lanes(manifest)
    reason = _hsoc_skip_reason(manifest)
    extended = _filter_entries(
        BIST_EXTENDED_SUITE + DEMO_SUITE_BASE + _cfg2_entries(manifest) + _pc16_entries(manifest),
        skip_suites,
    )
    exclusions = [
        SYSTEMD_BOOT_EXCLUSION,
        *VIRTUALIZATION_EXCLUSIONS,
        *_hsoc_exclusions(skip_suites, reason, HSOC_SKIP_SUITE_SOURCE),
        *_hsoc_exclusions(skip_extra, reason, HSOC_SKIP_EXTRA_SOURCE),
    ]
    return {
        "status": "ok",
        "machine": _str_value(manifest.get("machine")),
        "distro": _str_value(manifest.get("distro")),
        "included": {
            "validation_current": _json_strings(_current_suite(manifest)),
            "validation_power": _json_strings(_power_reboot_suite(manifest)),
            "validation_extended": _json_strings(extended),
            "extra": _json_strings(_filter_entries(EXTRA_LANES, skip_extra)),
        },
        "excluded": _json_objects(exclusions),
    }
