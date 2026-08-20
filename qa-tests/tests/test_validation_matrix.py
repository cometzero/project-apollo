from __future__ import annotations

import json
from pathlib import Path
from collections.abc import Callable
from typing import TypeAlias

import pytest
from jsonschema import Draft202012Validator, ValidationError

from apollo_validation.validation_matrix import (
    MatrixError,
    JsonValue,
    ValidationMatrix,
    load_validation_matrix,
    parse_validation_matrix,
)


WORKSPACE = Path(__file__).resolve().parents[2]
MATRIX_PATH = WORKSPACE / "qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml"
PROFILE_RESULT_SCHEMA = WORKSPACE / "qa-tests/schema/profile-result.schema.json"
RUN_SET_SCHEMA = WORKSPACE / "qa-tests/schema/validation-run-set.schema.json"
JsonMap: TypeAlias = dict[str, JsonValue]
Mutation: TypeAlias = Callable[[JsonMap], None]
APPROVED_FVP_SELECTORS: dict[str, tuple[str, ...]] = {
    "bsp-core": ("test_00_bsp_boot", "test_10_bsp_core"),
    "platform-devices": ("test_00_fvp_boot", "test_00_linux_boot", "test_60_linux_connectivity", "test_61_linux_dsu", "test_62_linux_cpu_topology", "test_63_linux_fvp_devices"),
    "trusted-services": ("test_00_fvp_boot", "test_00_linux_boot", "test_60_linux_connectivity", "test_80_trusted_services"),
    "pfdi": ("test_00_bsp_boot", "test_64_bsp_pfdi"),
    "pfdi-si-cl1": ("test_00_bsp_boot", "test_30_si_cl1_pfdi", "test_31_bsp_si_pfdi_monitor"),
    "safety-diagnostics-tests": ("test_00_bsp_boot", "test_20_si_cl0_diagnostics"),
    "ras_cpu": (
        "test_00_fvp_boot.FVPBootTest.test_fvp_boot",
        "test_00_rse_boot.RseBootTest.test_normal_boot",
        "test_00_tfa_secure_partition_boot.TfaSecurePartitionBootTest.test_secure_partition_boot",
        "test_00_linux_boot.LinuxBootTest.test_linux_boot",
        "test_40_tfa_cpu_topology.TfaCpuTopologyTest.test_configured_pc_cpus_in_tfa",
        "test_41_tfa_ras",
    ),
    "si-cl1": ("test_00_bsp_boot", "test_10_bsp_core.BSPCoreTest.test_safety_island_cl1"),
    "crypto-extension": ("test_00_linux_boot", "test_65_linux_crypto"),
    "cpuidle": ("test_00_bsp_boot", "test_31_bsp_cpuidle"),
    "cpufreq": ("test_00_bsp_boot", "test_32_bsp_cpufreq"),
    "mbpp": ("test_00_fvp_boot", "test_00_linux_boot", "test_72_power_cpufreq", "test_73_power_mbpp"),
    "hipc": ("test_00_fvp_boot", "test_00_linux_boot", "test_00_si_cl1_boot", "test_31_si_cl1_hipc"),
    "smcf": ("test_00_bsp_boot", "test_21_bsp_smcf"),
}


def _mapping(value: JsonValue) -> JsonMap:
    assert isinstance(value, dict)
    return value


def _array(value: JsonValue) -> list[JsonValue]:
    assert isinstance(value, list)
    return value


def _matrix_data() -> JsonMap:
    loaded: JsonValue = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    return _mapping(loaded)


def _schema(path: Path) -> JsonMap:
    loaded: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    return _mapping(loaded)


def _area_actions(data: JsonMap) -> list[JsonValue]:
    areas = _array(data["areas"])
    return _array(_mapping(areas[0])["actions"])


def _first_profile(data: JsonMap) -> JsonMap:
    profiles = _array(data["profiles"])
    return _mapping(profiles[0])


def _drop_action(data: JsonMap) -> None:
    _area_actions(data).pop()


def _duplicate_assertion(data: JsonMap) -> None:
    actions = _area_actions(data)
    first = _mapping(actions[0])
    second = _mapping(actions[1])
    second["assertion_id"] = first["assertion_id"]


def _unknown_profile(data: JsonMap) -> None:
    areas = _array(data["areas"])
    _mapping(areas[0])["profile_id"] = "unknown-profile"


def _xen_selector(data: JsonMap) -> None:
    _array(_first_profile(data)["fvp_selectors"]).append("test_40_virtualization")


def _empty_expected_set(data: JsonMap) -> None:
    _first_profile(data)["qbox_assertions"] = []


def _invalid_coverage_kind(data: JsonMap) -> None:
    _first_profile(data)["coverage_kind"] = "performance"


def test_canonical_matrix_maps_the_documented_non_xen_contract() -> None:
    # Given: the repository-owned Arm Zena CSS v2.2 matrix.
    # When: the typed loader parses its real JSON-compatible YAML content.
    matrix = load_validation_matrix(MATRIX_PATH)

    # Then: every documented non-Xen area/action is mapped exactly once.
    assert isinstance(matrix, ValidationMatrix)
    assert matrix.area_count == 15
    assert matrix.profile_count == 14
    assert matrix.action_count == 100
    assert matrix.semantic_qbox_area_count == 2
    assert matrix.xen_selector_count == 0
    assert matrix.excluded_xen_selector_count == 1


def test_canonical_matrix_links_actions_to_profile_assertions() -> None:
    # Given: the loaded canonical non-Xen matrix.
    matrix = load_validation_matrix(MATRIX_PATH)

    # When: action mappings are traversed through their profile contract.
    mappings = tuple(matrix.action_mappings())

    # Then: stable action and assertion IDs are unique and executable.
    assert len({mapping.action_id for mapping in mappings}) == 100
    assert len({mapping.assertion_id for mapping in mappings}) == 100
    assert all(mapping.assertion_id in mapping.qbox_assertions for mapping in mappings)


def test_canonical_matrix_matches_approved_profile_selector_contract() -> None:
    # Given: the plan-approved public profile and FVP selector contract.
    matrix = load_validation_matrix(MATRIX_PATH)

    # When: the canonical matrix is compared to that independent contract.
    actual = {
        profile.profile_id: profile.fvp_selectors for profile in matrix.profiles
    }

    # Then: public profile names and prerequisite selectors cannot silently drift.
    assert actual == APPROVED_FVP_SELECTORS


def test_systemd_boot_action_is_owned_by_platform_devices() -> None:
    # Given: the canonical profile matrix after BSP-only qualification.
    matrix = load_validation_matrix(MATRIX_PATH)
    profiles = {profile.profile_id: profile for profile in matrix.profiles}

    # When: systemd-boot's assertion owner is checked independently.
    bsp_assertions = profiles["bsp-core"].qbox_assertions
    platform_assertions = profiles["platform-devices"].qbox_assertions

    # Then: BSP does not claim a runtime EFI variable unavailable after bootefi.
    assert "systemd-boot-message" not in bsp_assertions
    assert "systemd-boot-message" in platform_assertions


def test_platform_devices_owns_controller_and_boot_actions() -> None:
    # Given: the canonical action mapping for BSP and product profiles.
    matrix = load_validation_matrix(MATRIX_PATH)
    actions_by_profile = {
        area.profile_id: {action.action_id for action in area.actions}
        for area in matrix.areas
    }

    # When: controller-network and systemd-boot action ownership is inspected.
    bsp_actions = actions_by_profile["bsp-core"]
    platform_actions = actions_by_profile["platform-devices"]

    # Then: the BSP profile stays native while product owns transport and boot.
    assert {"primary-ping", "primary-ssh", "systemd-boot-message"}.isdisjoint(
        bsp_actions
    )
    assert {"primary-ping", "primary-ssh", "systemd-boot-message"} <= platform_actions
    assert matrix.action_count == 100


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        (
            _drop_action,
            "expected 100 actions",
        ),
        (
            _duplicate_assertion,
            "duplicate assertion id",
        ),
        (
            _unknown_profile,
            "unknown profile",
        ),
        (
            _xen_selector,
            "Xen selector",
        ),
        (
            _empty_expected_set,
            "empty expected assertion set",
        ),
        (
            _invalid_coverage_kind,
            "invalid coverage kind",
        ),
    ],
)
def test_matrix_rejects_document_contract_drift(
    mutation: Mutation,
    reason: str,
) -> None:
    # Given: a parsed canonical matrix with one adversarial mutation.
    data = _matrix_data()
    mutation(data)

    # When/Then: parsing rejects the broken document contract stably.
    with pytest.raises(MatrixError, match=reason):
        parse_validation_matrix(data, MATRIX_PATH)


def test_profile_result_schema_accepts_a_complete_normalized_fixture() -> None:
    # Given: the strict profile-result schema and a complete normalized result.
    schema = _schema(PROFILE_RESULT_SCHEMA)
    fixture = {
        "version": 1,
        "profile_id": "platform-devices",
        "backend": "qbox",
        "verdict": "PASS",
        "expected": ["platform-device-networking"],
        "assertions": [
            {
                "id": "platform-device-networking",
                "status": "PASS",
                "coverage_kind": "semantic",
            }
        ],
    }

    # When: Draft 2020-12 validates the result.
    validator = Draft202012Validator(schema)
    validator.validate(fixture)

    # Then: the normalized result is accepted without permissive fields.
    assert validator.is_valid(fixture)


def test_profile_result_schema_rejects_unknown_fields() -> None:
    # Given: a normalized result with an undeclared field.
    schema = _schema(PROFILE_RESULT_SCHEMA)
    fixture = {
        "version": 1,
        "profile_id": "platform-devices",
        "backend": "qbox",
        "verdict": "PASS",
        "expected": ["platform-device-networking"],
        "assertions": [
            {
                "id": "platform-device-networking",
                "status": "PASS",
                "coverage_kind": "semantic",
            }
        ],
        "unexpected": "must fail",
    }

    # When/Then: strict schema validation rejects the extra surface.
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(fixture)


def test_validation_run_set_schema_accepts_complete_results() -> None:
    # Given: the strict run-set schema and a non-empty profile result set.
    schema = _schema(RUN_SET_SCHEMA)
    fixture = {
        "version": 1,
        "matrix_sha256": "a" * 64,
        "results": [
            {
                "version": 1,
                "profile_id": "bsp-core",
                "backend": "fvp",
                "verdict": "PASS",
                "expected": ["bsp-scp"],
                "assertions": [
                    {
                        "id": "bsp-scp",
                        "status": "PASS",
                        "coverage_kind": "identical",
                    }
                ],
            }
        ],
    }

    # When: Draft 2020-12 validates the run set.
    validator = Draft202012Validator(schema)
    validator.validate(fixture)

    # Then: the non-empty result set is accepted.
    assert validator.is_valid(fixture)


def test_normalized_schemas_accept_every_canonical_public_profile_id() -> None:
    # Given: every public profile parsed from the canonical non-Xen matrix.
    matrix = load_validation_matrix(MATRIX_PATH)
    profile_validator = Draft202012Validator(_schema(PROFILE_RESULT_SCHEMA))
    run_set_validator = Draft202012Validator(_schema(RUN_SET_SCHEMA))

    # When: each profile is represented by one schema-complete PASS result.
    for profile in matrix.profiles:
        assertion_id = profile.qbox_assertions[0]
        result = {
            "version": 1,
            "profile_id": profile.profile_id,
            "backend": "fvp",
            "verdict": "PASS",
            "expected": [assertion_id],
            "assertions": [
                {
                    "id": assertion_id,
                    "status": "PASS",
                    "coverage_kind": profile.coverage_kind,
                }
            ],
        }
        run_set = {"version": 1, "matrix_sha256": "a" * 64, "results": [result]}

        # Then: both result surfaces accept the same canonical public ID.
        profile_validator.validate(result)
        run_set_validator.validate(run_set)


def test_normalized_schemas_reject_invalid_public_profile_id() -> None:
    # Given: a complete result with a profile ID outside the public grammar.
    result = {
        "version": 1,
        "profile_id": "ras.cpu",
        "backend": "fvp",
        "verdict": "PASS",
        "expected": ["ras-inject-list"],
        "assertions": [
            {
                "id": "ras-inject-list",
                "status": "PASS",
                "coverage_kind": "identical",
            }
        ],
    }
    run_set = {"version": 1, "matrix_sha256": "a" * 64, "results": [result]}

    # When/Then: both strict schemas reject the invalid public ID.
    with pytest.raises(ValidationError):
        Draft202012Validator(_schema(PROFILE_RESULT_SCHEMA)).validate(result)
    with pytest.raises(ValidationError):
        Draft202012Validator(_schema(RUN_SET_SCHEMA)).validate(run_set)
