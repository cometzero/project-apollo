from __future__ import annotations

import ast
import json
import os
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from apollo_validation.profiles import (
    FvpTapNetwork,
    ProfileError,
    load_test_profile,
    merge_fvp_runtime_config,
)
from apollo_validation.root_cli import parse_root_args
from apollo_validation.selection import (
    prepare_selection,
    selected_test_environment,
    write_selection_evidence,
)


WORKSPACE = Path(__file__).resolve().parents[2]
SI_CL1_UART = "css.smb.si.cluster1_pl011_uart.uart_enable"
FVP_USER_NETWORKING = "ros.virtio_net.hostbridge.userNetworking"
FVP_INTERFACE_NAME = "ros.virtio_net.hostbridge.interfaceName"
SELECTED_FVP_CONFIG_ENV = "APOLLO_VALIDATION_FVP_CONFIG"
SELECTED_FVP_TAP_NETWORK_ENV = "APOLLO_VALIDATION_FVP_TAP_NETWORK"
BITBAKE_PASSTHROUGH_ENV = "BB_ENV_PASSTHROUGH_ADDITIONS"


def test_pfdi_profile_selects_bsp_oeqa_contract() -> None:
    # Given: the repository-owned PFDI test profile.
    # When: it is parsed for the FVP BSP backend.
    profile = load_test_profile(WORKSPACE, "pfdi", "fvp", "bsp")

    # Then: profile data resolves to executable OEQA selectors and target.
    assert profile.name == "pfdi"
    assert profile.selectors == ("test_00_bsp_boot", "test_64_bsp_pfdi")
    assert profile.oeqa_kind == "extended"
    assert profile.test_target == "HSOCBSPFVPTarget"
    assert profile.timeout_seconds == 1800


def test_cpuidle_profile_selects_the_bsp_native_contract() -> None:
    profile = load_test_profile(WORKSPACE, "cpuidle", "fvp", "bsp")

    assert profile.selectors == ("test_00_bsp_boot", "test_31_bsp_cpuidle")
    assert profile.oeqa_kind == "extended"
    assert profile.test_target == "HSOCBSPFVPTarget"
    assert profile.timeout_seconds == 3600


def test_cpufreq_profile_selects_the_bsp_native_contract() -> None:
    # Given: the repository-owned CPU frequency profile.
    # When: it is parsed for the FVP BSP backend.
    profile = load_test_profile(WORKSPACE, "cpufreq", "fvp", "bsp")

    # Then: the BSP boot gate precedes the ten CPU frequency assertions.
    assert profile.selectors == ("test_00_bsp_boot", "test_32_bsp_cpufreq")
    assert profile.oeqa_kind == "extended"
    assert profile.test_target == "HSOCBSPFVPTarget"
    assert profile.timeout_seconds == 3600


def test_platform_devices_profile_selects_product_runtime_contract() -> None:
    # Given: the product-only platform device validation profile.
    # When: it is resolved for the FVP product image.
    profile = load_test_profile(WORKSPACE, "platform-devices", "fvp", "product")

    # Then: systemd-boot, controller access, and all FVP device checks share
    # the same persistent Linux FVP session.
    assert profile.selectors == (
        "test_00_rse_boot",
        "test_00_fvp_boot",
        "test_00_uboot_boot",
        "test_00_systemd_boot",
        "test_00_linux_boot",
        "test_60_linux_connectivity",
        "test_61_linux_dsu",
        "test_62_linux_cpu_topology",
        "test_63_linux_fvp_devices",
    )
    assert profile.oeqa_kind == "extended"
    assert profile.test_target == "HSOCSingleSessionFVPTarget"
    assert profile.timeout_seconds == 3600
    assert profile.fvp_tap_network is not None
    assert profile.fvp_tap_network.interface_name == "apollo-fvp-tap0"
    assert profile.fvp_tap_network.host_ip == "192.0.2.1"
    assert profile.fvp_tap_network.target_ip == "192.0.2.10"


def _oeqa_method_dependencies(module: str) -> tuple[tuple[str, tuple[str, ...]], ...]:
    case = (
        WORKSPACE
        / "hsoc-stack/yocto/meta-hsoc-auto-solutions/lib/oeqa/runtime/cases"
        / f"{module}.py"
    )
    tree = ast.parse(case.read_text(encoding="utf-8"), filename=str(case))
    methods: list[tuple[str, tuple[str, ...]]] = []
    for class_node in tree.body:
        if not isinstance(class_node, ast.ClassDef):
            continue
        for method_node in class_node.body:
            if not isinstance(method_node, ast.FunctionDef):
                continue
            dependencies: list[str] = []
            for decorator in method_node.decorator_list:
                if not (
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Name)
                    and decorator.func.id == "OETestDepends"
                ):
                    continue
                for argument in decorator.args:
                    assert isinstance(argument, ast.List | ast.Tuple)
                    for dependency in argument.elts:
                        assert isinstance(dependency, ast.Constant)
                        assert isinstance(dependency.value, str)
                        dependencies.append(dependency.value)
            methods.append(
                (f"{module}.{class_node.name}.{method_node.name}", tuple(dependencies))
            )
    return tuple(methods)


def _assert_oeqa_dependency_closure(selectors: tuple[str, ...]) -> None:
    pending = list(selectors)
    visited: set[str] = set()
    graph: dict[str, tuple[str, ...]] = {}
    method_order: list[str] = []
    while pending:
        module = pending.pop(0)
        if module in visited:
            continue
        visited.add(module)
        for method, dependencies in _oeqa_method_dependencies(module):
            graph[method] = dependencies
            method_order.append(method)
            pending.extend(
                dependency.split(".", maxsplit=1)[0] for dependency in dependencies
            )

    selected = set(selectors)
    missing = {
        dependency.split(".", maxsplit=1)[0]
        for dependencies in graph.values()
        for dependency in dependencies
        if dependency.split(".", maxsplit=1)[0] not in selected
    }
    assert not missing

    selector_order = {selector: index for index, selector in enumerate(selectors)}
    method_positions = {method: index for index, method in enumerate(method_order)}
    for method, dependencies in graph.items():
        module = method.split(".", maxsplit=1)[0]
        for dependency in dependencies:
            dependency_module = dependency.split(".", maxsplit=1)[0]
            assert dependency in graph
            if dependency_module == module:
                assert method_positions[dependency] < method_positions[method]
            else:
                assert selector_order[dependency_module] < selector_order[module]


def test_platform_devices_profile_has_complete_oeqa_dependency_closure() -> None:
    profile = load_test_profile(WORKSPACE, "platform-devices", "fvp", "product")

    _assert_oeqa_dependency_closure(profile.selectors)


@pytest.mark.parametrize(
    "removed",
    [
        "test_00_rse_boot",
        "test_00_fvp_boot",
        "test_00_uboot_boot",
        "test_00_linux_boot",
        "test_60_linux_connectivity",
    ],
)
def test_platform_devices_profile_rejects_missing_oeqa_prerequisite(
    removed: str,
) -> None:
    profile = load_test_profile(WORKSPACE, "platform-devices", "fvp", "product")
    selectors = tuple(selector for selector in profile.selectors if selector != removed)

    with pytest.raises(AssertionError):
        _assert_oeqa_dependency_closure(selectors)


@pytest.mark.parametrize(
    ("backend", "image"),
    [("qbox", "product"), ("fvp", "bsp")],
)
def test_platform_devices_profile_rejects_unsupported_execution_boundary(
    backend: str,
    image: str,
) -> None:
    # Given: an execution boundary outside the product FVP contract.
    # When/Then: the typed profile loader rejects it before dispatch.
    with pytest.raises(ProfileError):
        load_test_profile(WORKSPACE, "platform-devices", backend, image)


@pytest.mark.parametrize(("backend", "image"), [("qbox", "bsp"), ("fvp", "product")])
def test_cpuidle_profile_rejects_unsupported_execution_boundary(
    backend: str,
    image: str,
) -> None:
    with pytest.raises(ProfileError):
        load_test_profile(WORKSPACE, "cpuidle", backend, image)


def test_bsp_core_profile_selects_the_complete_bsp_contract() -> None:
    # Given: the dedicated Apollo BSP core profile.
    # When: it is resolved for the FVP BSP backend.
    profile = load_test_profile(WORKSPACE, "bsp-core", "fvp", "bsp")

    # Then: BSP boot precedes all non-network BSP core assertions.
    assert profile.selectors == ("test_00_bsp_boot", "test_10_bsp_core")
    assert profile.test_target == "HSOCBSPFVPTarget"
    assert profile.timeout_seconds == 1800
    assert profile.fvp_config == ((SI_CL1_UART, "1"),)


def test_si_cl1_profile_selects_only_its_bsp_method() -> None:
    # Given: the focused Safety Island CL1 profile.
    # When: it is resolved for the FVP BSP backend.
    profile = load_test_profile(WORKSPACE, "si-cl1", "fvp", "bsp")

    # Then: it cannot accidentally broaden to BSP core device coverage.
    assert profile.selectors == (
        "test_00_bsp_boot",
        "test_10_bsp_core.BSPCoreTest.test_safety_island_cl1",
    )
    assert profile.test_target == "HSOCBSPFVPTarget"
    assert profile.timeout_seconds == 1200
    assert profile.fvp_config == ((SI_CL1_UART, "1"),)


def test_profile_fvp_config_crosses_the_selected_environment_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: a selected BSP core profile and no inherited override.
    monkeypatch.delenv(SELECTED_FVP_CONFIG_ENV, raising=False)
    options = parse_root_args(
        ["--fvp", "--bsp", "--headless", "--test-profile", "bsp-core"]
    )
    selection, _resolved = prepare_selection(WORKSPACE, options)
    assert selection is not None

    # When: the selected run owns its explicit environment boundary.
    with selected_test_environment(selection):
        selected = os.environ.get(SELECTED_FVP_CONFIG_ENV)
        passthrough = os.environ.get(BITBAKE_PASSTHROUGH_ENV, "").split()

    # Then: the exact typed map is serialized and the outer environment restored.
    assert json.loads(selected or "null") == {SI_CL1_UART: "1"}
    assert SELECTED_FVP_CONFIG_ENV in passthrough
    assert SELECTED_FVP_CONFIG_ENV not in os.environ


def test_platform_devices_tap_network_crosses_the_selected_environment_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: the product FVP profile and no inherited network policy.
    monkeypatch.delenv(SELECTED_FVP_TAP_NETWORK_ENV, raising=False)
    options = parse_root_args(
        ["--fvp", "--headless", "--test-profile", "platform-devices"]
    )
    selection, _resolved = prepare_selection(WORKSPACE, options)
    assert selection is not None
    assert selection.fvp_config == (
        (FVP_USER_NETWORKING, "0"),
        (FVP_INTERFACE_NAME, "apollo-fvp-tap0"),
    )

    # When: the selected profile establishes its run-owned environment.
    with selected_test_environment(selection):
        selected = os.environ.get(SELECTED_FVP_TAP_NETWORK_ENV)
        selected_config = os.environ.get(SELECTED_FVP_CONFIG_ENV)
        passthrough = os.environ.get(BITBAKE_PASSTHROUGH_ENV, "").split()

    # Then: only the fixed non-loopback TAP contract reaches BitBake.
    assert json.loads(selected or "null") == {
        "host_ip": "192.0.2.1",
        "interface_name": "apollo-fvp-tap0",
        "prefix_length": 24,
        "target_ip": "192.0.2.10",
    }
    assert json.loads(selected_config or "null") == {
        FVP_INTERFACE_NAME: "apollo-fvp-tap0",
        FVP_USER_NETWORKING: "0",
    }
    assert SELECTED_FVP_CONFIG_ENV in passthrough
    assert SELECTED_FVP_TAP_NETWORK_ENV in passthrough
    assert SELECTED_FVP_TAP_NETWORK_ENV not in os.environ


def test_runtime_fvp_config_merges_uart_and_tap_parameters() -> None:
    # Given: independent typed UART and TAP policies selected for one FVP run.
    network = FvpTapNetwork("apollo-fvp-tap0", "192.0.2.1", "192.0.2.10", 24)

    # When: the runtime map is assembled at the selection boundary.
    merged = merge_fvp_runtime_config(((SI_CL1_UART, "1"),), network)

    # Then: each approved parameter appears once with its exact safe value.
    assert merged == (
        (SI_CL1_UART, "1"),
        (FVP_USER_NETWORKING, "0"),
        (FVP_INTERFACE_NAME, "apollo-fvp-tap0"),
    )


def test_runtime_fvp_config_rejects_duplicate_parameter() -> None:
    # Given: an explicit profile map conflicts with a derived TAP parameter.
    network = FvpTapNetwork("apollo-fvp-tap0", "192.0.2.1", "192.0.2.10", 24)

    # When/Then: the merge rejects the duplicate before environment export.
    with pytest.raises(ProfileError, match="duplicate FVP config key"):
        merge_fvp_runtime_config(((FVP_USER_NETWORKING, "1"),), network)


def test_pfdi_selection_clears_inherited_fvp_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: a PFDI profile process inheriting a stale SI CL1 override.
    monkeypatch.setenv(
        SELECTED_FVP_CONFIG_ENV,
        json.dumps({SI_CL1_UART: "1"}),
    )
    options = parse_root_args(
        ["--fvp", "--bsp", "--headless", "--test-profile", "pfdi"]
    )
    selection, _resolved = prepare_selection(WORKSPACE, options)
    assert selection is not None

    # When: the PFDI selection owns the run environment.
    with selected_test_environment(selection):
        selected = os.environ.get(SELECTED_FVP_CONFIG_ENV)

    # Then: PFDI emits no FVP override and the inherited value is restored later.
    assert selected is None
    assert json.loads(os.environ[SELECTED_FVP_CONFIG_ENV]) == {SI_CL1_UART: "1"}


@pytest.mark.parametrize(
    ("profile_name", "fvp_config", "reason"),
    [
        ("bsp-core", {"unknown.parameter": "1"}, "unknown FVP config key"),
        ("bsp-core", {SI_CL1_UART: ["1"]}, "must be a string"),
        ("bsp-core", {SI_CL1_UART: '1\"\\nINJECT = "1'}, "unsafe FVP config value"),
        ("pfdi", {SI_CL1_UART: "1"}, "does not permit FVP config"),
    ],
)
def test_profile_rejects_invalid_fvp_config(
    tmp_path: Path,
    profile_name: str,
    fvp_config: object,
    reason: str,
) -> None:
    # Given: a repository-shaped profile carrying invalid FVP parameter data.
    profile_dir = tmp_path / "qa-tests/profiles"
    profile_dir.mkdir(parents=True)
    payload = {
        "version": 1,
        "name": profile_name,
        "description": "invalid fixture",
        "compatibility": {"backends": ["fvp"], "images": ["bsp"]},
        "oeqa": {"kind": "extended", "selectors": ["test_x"], "timeout_seconds": 1},
        "targets": {"fvp": "Target"},
        "fvp_config": fvp_config,
    }
    (profile_dir / f"{profile_name}.yaml").write_text(
        json.dumps(payload), encoding="utf-8"
    )

    # When/Then: the typed profile boundary rejects it before selection.
    with pytest.raises(ProfileError, match=reason):
        load_test_profile(tmp_path, profile_name, "fvp", "bsp")


@pytest.mark.parametrize(
    "tap_network",
    [
        None,
        {"interface_name": "lo", "host_ip": "192.0.2.1", "target_ip": "192.0.2.10", "prefix_length": 24},
        {"interface_name": "apollo-fvp-tap0", "host_ip": "127.0.0.1", "target_ip": "192.0.2.10", "prefix_length": 24},
        {"interface_name": "apollo-fvp-tap0", "host_ip": "192.0.2.1", "target_ip": "127.0.0.1", "prefix_length": 24},
        {"interface_name": "apollo-fvp-tap0", "host_ip": "192.0.2.1", "target_ip": "192.0.2.10", "prefix_length": "24"},
    ],
)
def test_profile_rejects_malformed_fvp_tap_network(
    tmp_path: Path,
    tap_network: object,
) -> None:
    # Given: a profile whose TAP declaration cannot safely reach the host.
    profile_dir = tmp_path / "qa-tests/profiles"
    profile_dir.mkdir(parents=True)
    payload = {
        "version": 1,
        "name": "platform-devices",
        "compatibility": {"backends": ["fvp"], "images": ["product"]},
        "oeqa": {"kind": "extended", "selectors": ["test_x"], "timeout_seconds": 1},
        "targets": {"fvp": "Target"},
        "fvp_tap_network": tap_network,
    }
    (profile_dir / "platform-devices.yaml").write_text(
        json.dumps(payload), encoding="utf-8"
    )

    # When/Then: parsing rejects it before a runner can use host networking.
    with pytest.raises(ProfileError, match="FVP TAP network"):
        load_test_profile(tmp_path, "platform-devices", "fvp", "product")


def test_pfdi_profile_selects_qbox_probe_contract() -> None:
    # Given: the repository-owned PFDI profile and QBox BSP backend.
    # When: the profile is resolved for QBox.
    profile = load_test_profile(WORKSPACE, "pfdi", "qbox", "bsp")

    # Then: the same selectors route through the QBox PFDI probe target.
    assert profile.selectors == ("test_00_bsp_boot", "test_64_bsp_pfdi")
    assert profile.test_target == "QBoxPFDIRunner"
    assert profile.timeout_seconds == 1800


def test_profile_selection_applies_timeout_and_writes_snapshot(
    tmp_path: Path,
) -> None:
    # Given: the public profile command without an explicit timeout override.
    options = parse_root_args(
        ["--fvp", "--bsp", "--headless", "--test-profile", "pfdi"]
    )

    # When: the profile is resolved and its evidence is written.
    selection, resolved = prepare_selection(WORKSPACE, options)
    assert selection is not None
    write_selection_evidence(tmp_path, selection)

    # Then: OEQA selection, target, timeout, and profile snapshot agree.
    assert selection.ordered_tests == ("test_00_bsp_boot", "test_64_bsp_pfdi")
    assert selection.test_target == "HSOCBSPFVPTarget"
    assert resolved.category == "functional"
    assert resolved.timeout_oeqa == 1800
    assert (tmp_path / "resolved-profile.yaml").is_file()


def test_bsp_core_snapshot_captures_fvp_config(tmp_path: Path) -> None:
    # Given: the public BSP core profile selection.
    options = parse_root_args(
        ["--fvp", "--bsp", "--headless", "--test-profile", "bsp-core"]
    )
    selection, _resolved = prepare_selection(WORKSPACE, options)
    assert selection is not None

    # When: the resolved profile snapshot is recorded.
    write_selection_evidence(tmp_path, selection)
    snapshot = json.loads(
        (tmp_path / "resolved-profile.yaml").read_text(encoding="utf-8")
    )

    # Then: provenance consumers see the exact run-owned FVP parameter map.
    assert snapshot["fvp_config"] == {SI_CL1_UART: "1"}


def test_si_cl1_profile_selects_full_safety_island_suite() -> None:
    # Given: the Arm validation profile for Safety Island CL1 PFDI.
    # When: it is resolved for the FVP BSP backend.
    profile = load_test_profile(WORKSPACE, "pfdi-si-cl1", "fvp", "bsp")

    # Then: the BSP boot and complete SI CL1 OEQA module are selected.
    assert profile.selectors == (
        "test_00_bsp_boot",
        "test_30_si_cl1_pfdi",
        "test_31_bsp_si_pfdi_monitor",
    )
    assert profile.test_target == "HSOCBSPFVPTarget"
    assert profile.timeout_seconds == 3600
    assert profile.fvp_config == ((SI_CL1_UART, "1"),)


def test_si_cl1_profile_selects_qbox_probe_contract() -> None:
    # Given: the Safety Island CL1 PFDI profile and QBox BSP backend.
    # When: the profile is resolved for QBox.
    profile = load_test_profile(WORKSPACE, "pfdi-si-cl1", "qbox", "bsp")

    # Then: the complete selectors route through the SI CL1 QBox probe.
    assert profile.selectors == (
        "test_00_bsp_boot",
        "test_30_si_cl1_pfdi",
        "test_31_bsp_si_pfdi_monitor",
    )
    assert profile.test_target == "QBoxSICl1PFDIRunner"
    assert profile.timeout_seconds == 3600


def test_smcf_profile_selects_fvp_bsp_contract() -> None:
    # Given: the BSP-native SMCF integration profile.
    # When: it is resolved for its only supported backend and image.
    profile = load_test_profile(WORKSPACE, "smcf", "fvp", "bsp")

    # Then: it selects only BSP boot and the complete SMCF OEQA module.
    assert profile.selectors == ("test_00_bsp_boot", "test_21_bsp_smcf")
    assert profile.test_target == "HSOCBSPFVPTarget"
    assert profile.timeout_seconds == 2400


@pytest.mark.parametrize(
    ("backend", "image"),
    [("qbox", "bsp"), ("fvp", "product")],
)
def test_smcf_profile_rejects_unsupported_execution_boundary(
    backend: str,
    image: str,
) -> None:
    # Given: a backend or image outside the FVP BSP-only SMCF contract.
    # When/Then: profile loading rejects the unsupported execution boundary.
    with pytest.raises(ProfileError):
        load_test_profile(WORKSPACE, "smcf", backend, image)


@pytest.mark.parametrize("profile_name", ["smcf", "pfdi-si-cl1", "platform-devices"])
def test_bsp_profile_matches_the_strict_schema(profile_name: str) -> None:
    # Given: each Todo 7 profile and the repository-owned strict profile schema.
    schema_path = WORKSPACE / "qa-tests/schema/test-profile.schema.json"
    profile_path = WORKSPACE / "qa-tests/profiles" / f"{profile_name}.yaml"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    profile = json.loads(profile_path.read_text(encoding="utf-8"))

    # When/Then: the schema accepts the exact public profile representation.
    Draft202012Validator(schema).validate(profile)


def test_unknown_profile_reports_typed_error() -> None:
    # Given: a profile name with no repository definition.
    # When/Then: the loader reports its typed boundary error cleanly.
    with pytest.raises(ProfileError, match="unknown test profile: missing"):
        load_test_profile(WORKSPACE, "missing", "fvp", "bsp")


def test_safety_diagnostics_profile_selects_ssu_fmu_suite() -> None:
    # Given: the Arm Safety Island diagnostics validation profile.
    # When: it is resolved for the FVP BSP backend.
    profile = load_test_profile(
        WORKSPACE,
        "safety-diagnostics-tests",
        "fvp",
        "bsp",
    )

    # Then: the BSP boot and SSU/FMU OEQA module are selected.
    assert profile.selectors == (
        "test_00_bsp_boot",
        "test_20_si_cl0_diagnostics",
    )
    assert profile.test_target == "HSOCBSPFVPTarget"
    assert profile.timeout_seconds == 1800


def test_safety_diagnostics_profile_selects_qbox_probe() -> None:
    # Given: the Safety Island diagnostics profile and QBox BSP backend.
    # When: the profile is resolved for QBox.
    profile = load_test_profile(
        WORKSPACE,
        "safety-diagnostics-tests",
        "qbox",
        "bsp",
    )

    # Then: the complete SSU/FMU selectors route through the QBox probe.
    assert profile.selectors == (
        "test_00_bsp_boot",
        "test_20_si_cl0_diagnostics",
    )
    assert profile.test_target == "QBoxSafetyDiagnosticsRunner"
    assert profile.timeout_seconds == 1800


def test_ras_cpu_profile_selects_complete_product_suite() -> None:
    # Given: the Primary Compute CPU RAS validation profile.
    # When: it is resolved for the FVP product-image backend.
    profile = load_test_profile(WORKSPACE, "ras_cpu", "fvp", "product")

    # Then: every boot dependency and the complete RAS module are selected.
    assert profile.selectors == (
        "test_00_fvp_boot.FVPBootTest.test_fvp_boot",
        "test_00_rse_boot.RseBootTest.test_normal_boot",
        "test_00_tfa_secure_partition_boot."
        "TfaSecurePartitionBootTest.test_secure_partition_boot",
        "test_00_linux_boot.LinuxBootTest.test_linux_boot",
        "test_40_tfa_cpu_topology."
        "TfaCpuTopologyTest.test_configured_pc_cpus_in_tfa",
        "test_41_tfa_ras",
    )
    assert profile.test_target == "HSOCSingleSessionFVPTarget"
    assert profile.timeout_seconds == 3600


def test_ras_cpu_profile_selects_qbox_probe_contract() -> None:
    # Given: the complete Primary Compute RAS profile and QBox product backend.
    # When: the profile is resolved for QBox.
    profile = load_test_profile(WORKSPACE, "ras_cpu", "qbox", "product")

    # Then: all FVP selectors route through the QBox cross-console probe.
    assert profile.selectors[-1] == "test_41_tfa_ras"
    assert profile.test_target == "QBoxRASCpuRunner"
    assert profile.timeout_seconds == 3600
