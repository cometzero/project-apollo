from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import re
from typing import Literal, TypeAlias, assert_never

from .profile_results import (
    AssertionStatus,
    Backend,
    NormalizedProfile,
    ObservedAssertion,
    ProfileResultError,
    Verdict,
    evaluate_profile,
)
from .validation_matrix import load_validation_matrix
from .validation_types import CoverageKind, ValidationProfile


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
CommandStatus: TypeAlias = Literal["pass", "fail", "blocked", "skipped"]
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = WORKSPACE_ROOT / "qa-tests/validation/arm-zena-css-v2.2-non-xen.yaml"


_FVP_ALIASES: dict[str, tuple[str, ...]] = {
    "platform-devices:test_systemd_boot": ("systemd-boot-message",),
    "bsp-core:test_firmware_boot_chain": (
        "bsp-scp",
        "bsp-uboot-boot",
        "rse-normal-boot",
        "rse-measured-boot",
        "primary-fvp-boot",
        "pc-cpus-tfa",
        "secure-partition-optee",
    ),
    "bsp-core:test_linux_topology_and_devices": (
        "ap-dsu-cluster",
        "pc-cpus-linux",
    ),
    "bsp-core:test_safety_island_cl1": ("bsp-safety-island-cl1",),
    "si-cl1:test_safety_island_cl1": ("safety-island-cluster1",),
    "pfdi:test_01_prerequisites": ("pfdi-app",),
    "pfdi:test_02_service": ("pfdi-systemd-service",),
    "pfdi:test_03_cli": ("pfdi-cli",),
    "pfdi:test_04_online": ("pfdi-app-monitoring",),
    "pfdi:test_05_monitoring_started": (),
    "pfdi:test_90_force_error": (
        "pfdi-cli-force-error",
        "pfdi-app-monitoring-error",
    ),
    "pfdi:test_91_fault_propagation": ("pfdi-sbistc",),
    "pfdi-si-cl1:test_14_pfdi_multiple_runs_consistency_3x": (
        "si-pfdi-multiple-runs-consistency",
    ),
    "pfdi-si-cl1:test_15_pfdi_stress_5x": ("si-pfdi-stress",),
    "smcf:test_01_smcf_client_start": ("smcf-client-start",),
    "smcf:test_02_execute_smcf_test": ("smcf-execute-test",),
    "smcf:test_03_run_smcf_3x": ("smcf-run-3x",),
    "smcf:test_04_smcf_client_sensor_monitor": ("smcf-sensor-monitor",),
    "cpuidle:test_ensure_interface": ("cpuidle-ensure",),
    "cpuidle:test_cpuidle_c_states": ("cpuidle-c-states",),
    "cpuidle:test_default_status": ("cpuidle-default-status",),
    "cpuidle:test_disable_state": ("cpuidle-disable-state",),
    "cpuidle:test_residency_latency": ("cpuidle-residency-latency",),
    "cpuidle:test_governors": ("cpuidle-governors",),
    "cpuidle:test_governor_switching": ("cpuidle-governor-switching",),
    "cpuidle:test_invalid_governor": ("cpuidle-invalid-governor",),
    "cpufreq:test_cpufreq_policy": ("cpufreq-policy",),
    "cpufreq:test_update_invalid_governor": ("cpufreq-invalid-governor",),
    "cpufreq:test_update_scaling_min_frequencies": (
        "cpufreq-scaling-min-frequencies",
    ),
    "cpufreq:test_update_scaling_max_frequencies": (
        "cpufreq-scaling-max-frequencies",
    ),
    "cpufreq:test_update_min_max_scaling_frequencies_negative": (
        "cpufreq-min-max-negative",
    ),
    "hipc:test_01_mid_sanity_dt_and_shared_memory": (
        "hipc-dt-and-shared-memory",
    ),
    "hipc:test_02_enablement_linux_stack": ("hipc-linux-stack",),
    "hipc:test_03_memory_layout": ("hipc-memory-layout",),
    "hipc:test_04_icmp_bidirectional": ("hipc-icmp-bidirectional",),
    "hipc:test_05_udp_pc_to_cl1": ("hipc-udp-pc-to-cl1",),
    "hipc:test_06_tcp_pc_to_cl1": ("hipc-tcp-pc-to-cl1",),
    "hipc:test_07_udp_cl1_to_pc": ("hipc-udp-cl1-to-pc",),
    "hipc:test_08_tcp_cl1_to_pc": ("hipc-tcp-cl1-to-pc",),
    "hipc:test_09_boundary_payload_sizes": ("hipc-boundary-payload-sizes",),
    "hipc:test_10_boundary_multistream": ("hipc-boundary-multistream",),
}


def _mapping(value: JsonValue, field: str) -> dict[str, JsonValue]:
    if not isinstance(value, dict):
        raise ProfileResultError(f"profile result field {field} must be an object")
    return value


def _items(value: JsonValue, field: str) -> list[JsonValue]:
    if not isinstance(value, list):
        raise ProfileResultError(f"profile result field {field} must be an array")
    return value


def _string(value: JsonValue, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ProfileResultError(f"profile result field {field} must be a string")
    return value


def _assertion_status(value: JsonValue) -> AssertionStatus:
    raw = _string(value, "assertions.status").upper()
    aliases: dict[str, AssertionStatus] = {
        "PASS": "PASS",
        "PASSED": "PASS",
        "OK": "PASS",
        "FAIL": "FAIL",
        "FAILED": "FAIL",
        "ERROR": "FAIL",
        "BLOCKED": "BLOCKED",
        "SKIPPED": "SKIPPED",
        "SKIP": "SKIPPED",
    }
    parsed = aliases.get(raw)
    if parsed is None:
        raise ProfileResultError(f"unsupported assertion status: {raw}")
    return parsed


def _coverage(value: JsonValue) -> CoverageKind:
    raw = _string(value, "assertions.coverage_kind")
    kinds: dict[str, CoverageKind] = {
        "identical": "identical",
        "semantic": "semantic",
    }
    coverage = kinds.get(raw)
    if coverage is None:
        raise ProfileResultError(f"unsupported coverage kind: {raw}")
    return coverage


def _read_json(path: Path) -> JsonValue:
    try:
        loaded: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as error:
        raise ProfileResultError(f"invalid profile result artifact: {path}") from error
    return loaded


def _command_record(line: str) -> dict[str, JsonValue]:
    try:
        loaded: JsonValue = json.loads(line)
    except json.JSONDecodeError as error:
        raise ProfileResultError("invalid profile command record") from error
    return _mapping(loaded, "command")


def _command_status(value: JsonValue) -> CommandStatus:
    raw = _string(value, "command.status").lower()
    statuses: dict[str, CommandStatus] = {
        "pass": "pass",
        "fail": "fail",
        "blocked": "blocked",
        "skipped": "skipped",
    }
    status = statuses.get(raw)
    if status is None:
        raise ProfileResultError(f"invalid profile command status: {raw}")
    return status


def _artifact_paths(run_dir: Path, kind: str) -> tuple[Path, ...]:
    commands = run_dir / "commands.jsonl"
    if not commands.is_file():
        return ()
    paths: list[Path] = []
    for line in commands.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = _command_record(line)
        for raw_artifact in _items(record.get("artifacts", []), "artifacts"):
            artifact = _mapping(raw_artifact, "artifact")
            if artifact.get("kind") != kind:
                continue
            raw_path = _string(artifact.get("path"), "artifact.path")
            path = Path(raw_path)
            paths.append(path if path.is_absolute() else run_dir / path)
    return tuple(paths)


def _required_command_gate(run_dir: Path) -> tuple[Verdict, str] | None:
    commands = run_dir / "commands.jsonl"
    if not commands.is_file():
        return "BLOCKED", "blocked_profile_commands_missing"
    statuses: list[CommandStatus] = []
    for line in commands.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = _command_record(line)
        if record.get("required", True) is not False:
            statuses.append(_command_status(record.get("status")))
    if any(status == "fail" for status in statuses):
        return "FAIL", "failed_required_profile_command"
    if any(status in {"blocked", "skipped"} for status in statuses):
        return "BLOCKED", "blocked_required_profile_command"
    return None


def _fvp_ids(profile: ValidationProfile, test_name: str) -> tuple[str, ...]:
    method = test_name.rsplit(".", maxsplit=1)[-1]
    alias = _FVP_ALIASES.get(f"{profile.profile_id}:{method}")
    if alias is not None:
        return alias
    candidate = re.sub(r"^test_(?:\d+_)?", "", method).replace("_", "-")
    candidates = (candidate, re.sub(r"^(?:ts-|pfdi-)", "", candidate))
    matched = tuple(
        assertion_id
        for assertion_id in profile.qbox_assertions
        if any(
            assertion_id == item or assertion_id.endswith(f"-{item}")
            for item in candidates
        )
    )
    return matched if len(matched) == 1 else ()


def _fvp_assertions(
    profile: ValidationProfile,
    paths: tuple[Path, ...],
) -> tuple[ObservedAssertion, ...]:
    assertions: list[ObservedAssertion] = []
    for path in paths:
        root = _mapping(_read_json(path), "root")
        for raw_result_set in root.values():
            result_set = _mapping(raw_result_set, "result_set")
            results = _mapping(result_set.get("result"), "result")
            for name, raw_result in results.items():
                result = _mapping(raw_result, f"result.{name}")
                status = _assertion_status(result.get("status"))
                assertions.extend(
                    ObservedAssertion(assertion_id, status, profile.coverage_kind)
                    for assertion_id in _fvp_ids(profile, name)
                )
    return tuple(assertions)


def _qbox_assertions(paths: tuple[Path, ...]) -> tuple[ObservedAssertion, ...]:
    assertions: list[ObservedAssertion] = []
    for path in paths:
        root = _mapping(_read_json(path), "root")
        for index, raw_assertion in enumerate(
            _items(root.get("assertions"), "assertions")
        ):
            assertion = _mapping(raw_assertion, f"assertions[{index}]")
            assertions.append(
                ObservedAssertion(
                    _string(assertion.get("id"), "assertions.id"),
                    _assertion_status(assertion.get("status")),
                    _coverage(assertion.get("coverage_kind")),
                )
            )
    return tuple(assertions)


def normalize_profile_run(
    run_dir: Path,
    profile_id: str,
    backend: Backend,
) -> NormalizedProfile:
    matrix = load_validation_matrix(MATRIX_PATH)
    profile = next(
        (item for item in matrix.profiles if item.profile_id == profile_id),
        None,
    )
    if profile is None:
        raise ProfileResultError(f"unknown validation profile: {profile_id}")
    try:
        match backend:
            case "fvp":
                observed = _fvp_assertions(profile, _artifact_paths(run_dir, "oeqa_result"))
            case "qbox":
                observed = _qbox_assertions(_artifact_paths(run_dir, "qbox_result"))
            case unexpected:
                assert_never(unexpected)
        command_gate = _required_command_gate(run_dir)
    except ProfileResultError:
        invalid = evaluate_profile(profile, backend, ())
        return replace(
            invalid,
            reasons=(
                "blocked_malformed_profile_evidence",
                "blocked_invalid_profile_result",
                *invalid.reasons,
            ),
        )
    normalized = evaluate_profile(profile, backend, observed)
    if command_gate is None:
        return normalized
    verdict, reason = command_gate
    return replace(
        normalized,
        result=replace(normalized.result, verdict=verdict),
        reasons=(*normalized.reasons, reason),
    )
