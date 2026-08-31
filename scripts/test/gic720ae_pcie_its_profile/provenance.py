from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Final

from .contract import (
    AHCI_IMAGE_KEY,
    HashRecord,
    JsonObject,
    JsonValue,
    ProfileError,
    ProfileLayout,
    hash_record,
    sha256_file,
    string_parameters,
    validate_hash_record,
)


TOOL_POSTPROCESSOR_ROLES: Final = frozenset({
    "scripts/test/build_gic720ae_pcie_its_profile.py",
    "scripts/test/gic720ae_pcie_its_profile/__init__.py",
    "scripts/test/gic720ae_pcie_its_profile/contract.py",
    "scripts/test/gic720ae_pcie_its_profile/build.py",
    "scripts/test/gic720ae_pcie_its_profile/dt_delivery.py",
    "scripts/test/gic720ae_pcie_its_profile/finalize.py",
    "scripts/test/gic720ae_pcie_its_profile/provenance.py",
    "scripts/test/gic720ae_pcie_its_profile/workflow.py",
    "scripts/test/capture_apollo_fvp_pcie_model.py",
    "tests/schemas/apollo-fvp-pcie-model-contract.schema.json",
    "tests/schemas/gic720ae-pcie-its-profile.schema.json",
})
BITBAKE_BUILD_INPUT_ROLES: Final = frozenset({
    "hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/linux-yocto-apollo-common.inc",
    "hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/files/gic720ae-pcie-its.cfg",
    "hsoc-stack/components/primary_compute/linux/arch/arm64/configs/apollo_fvp_defconfig",
    "hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/arm/apollo-fvp.dts",
    "hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/arm/apollo-fvp.dtsi",
    "hsoc-stack/components/primary_compute/trusted-firmware-a/fdts/apollo_fvp_fvp.dts",
    "hsoc-stack/components/primary_compute/trusted-firmware-a/fdts/apollo_fvp.dtsi",
    "hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/config_cmn_cyprus.c",
    "hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/test/test_pcie_cmn_routes.c",
    "arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc",
})
RUNTIME_INPUT_ROLES: Final = frozenset({"layers/meta-arm/scripts/runfvp"})
PATH_CONTAINMENT_REMEDIATION_ROLES: Final = (
    "scripts/test/build_gic720ae_pcie_its_profile.py",
    "scripts/test/gic720ae_pcie_its_profile/contract.py",
    "scripts/test/gic720ae_pcie_its_profile/finalize.py",
    "scripts/test/gic720ae_pcie_its_profile/provenance.py",
    "scripts/test/gic720ae_pcie_its_profile/workflow.py",
    "tests/schemas/gic720ae-pcie-its-profile.schema.json",
)


def source_classification(role: str) -> str:
    if role in TOOL_POSTPROCESSOR_ROLES:
        return "tool_postprocessor"
    if role in BITBAKE_BUILD_INPUT_ROLES:
        return "bitbake_build_input"
    if role in RUNTIME_INPUT_ROLES:
        return "runtime_input"
    raise ProfileError("unknown_source_role", role)


def source_delta_records(records: list[HashRecord]) -> list[JsonObject]:
    deltas: list[JsonObject] = []
    for record in records:
        path = Path(record["path"])
        if not path.is_file():
            raise ProfileError("source_input_missing", record["role"])
        current = sha256_file(path)
        if current != record["sha256"]:
            deltas.append({
                "role": record["role"],
                "path": str(path.resolve()),
                "old_sha256": record["sha256"],
                "new_sha256": current,
                "classification": source_classification(record["role"]),
            })
    return deltas


def validate_launchable_source_closure(records: list[HashRecord]) -> None:
    if source_delta_records(records):
        raise ProfileError("stale_source_hashes")


def validate_source_hash_claim(
    records: list[HashRecord],
    claimed_valid: bool,
) -> None:
    try:
        validate_launchable_source_closure(records)
    except ProfileError as error:
        if claimed_valid and error.reason == "stale_source_hashes":
            raise ProfileError("false_source_hashes_valid_claim") from error
        raise


def authorize_path_containment_refresh(
    records: list[HashRecord],
) -> list[JsonObject]:
    deltas = source_delta_records(records)
    if any(item["classification"] != "tool_postprocessor" for item in deltas):
        raise ProfileError("immutable_build_input_changed")
    roles = tuple(item["role"] for item in deltas)
    if roles != PATH_CONTAINMENT_REMEDIATION_ROLES:
        raise ProfileError("unauthorized_source_delta")
    for item in deltas:
        item["reason"] = "path_containment_remediation"
    return deltas


def validate_task_sigdata_records(records: list[HashRecord]) -> None:
    try:
        for record in records:
            validate_hash_record(record)
    except ProfileError as error:
        raise ProfileError("stale_task_sigdata") from error


def validate_artifact_records(records: list[HashRecord]) -> None:
    try:
        for record in records:
            validate_hash_record(record)
    except ProfileError as error:
        raise ProfileError("stale_artifact") from error


def source_hashes(workspace: Path) -> list[HashRecord]:
    paths = (
        "scripts/test/build_gic720ae_pcie_its_profile.py",
        "scripts/test/gic720ae_pcie_its_profile/__init__.py",
        "scripts/test/gic720ae_pcie_its_profile/contract.py",
        "scripts/test/gic720ae_pcie_its_profile/build.py",
        "scripts/test/gic720ae_pcie_its_profile/dt_delivery.py",
        "scripts/test/gic720ae_pcie_its_profile/finalize.py",
        "scripts/test/gic720ae_pcie_its_profile/provenance.py",
        "scripts/test/gic720ae_pcie_its_profile/workflow.py",
        "scripts/test/capture_apollo_fvp_pcie_model.py",
        "tests/schemas/apollo-fvp-pcie-model-contract.schema.json",
        "tests/schemas/gic720ae-pcie-its-profile.schema.json",
        "hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/linux-yocto-apollo-common.inc",
        "hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/files/gic720ae-pcie-its.cfg",
        "hsoc-stack/components/primary_compute/linux/arch/arm64/configs/apollo_fvp_defconfig",
        "hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/arm/apollo-fvp.dts",
        "hsoc-stack/components/primary_compute/linux/arch/arm64/boot/dts/arm/apollo-fvp.dtsi",
        "hsoc-stack/components/primary_compute/trusted-firmware-a/fdts/apollo_fvp_fvp.dts",
        "hsoc-stack/components/primary_compute/trusted-firmware-a/fdts/apollo_fvp.dtsi",
        "hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/config_cmn_cyprus.c",
        "hsoc-stack/components/system_mgmt/scp-firmware/product/automotive-rd/apollo-fvp/si0_ramfw/test/test_pcie_cmn_routes.c",
        "arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/include/fvp/fvp.inc",
        "layers/meta-arm/scripts/runfvp",
    )
    return [hash_record(path, workspace / path) for path in paths]


def repository_heads(workspace: Path) -> dict[str, str]:
    repositories = (
        workspace,
        workspace / "hsoc-stack/yocto/meta-hsoc-bsp",
        workspace / "hsoc-stack/components/primary_compute/linux",
        workspace / "hsoc-stack/components/primary_compute/trusted-firmware-a",
        workspace / "hsoc-stack/components/system_mgmt/scp-firmware",
    )
    heads: dict[str, str] = {}
    for repository in repositories:
        result = subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
        value = result.stdout.strip()
        if result.returncode != 0 or len(value) != 40:
            raise ProfileError("source_repository_missing", str(repository))
        heads[str(repository.resolve())] = value
    return heads


def active_sigdata_manifest(workspace: Path) -> list[HashRecord]:
    stamps = workspace / "build/tmp_baremetal/stamps"
    paths = sorted(stamps.glob("*/linux-yocto-rt/*.do_kernel_configme.sigdata.*"))
    return [hash_record("active-default-kernel-configme", path) for path in paths]


def changed_parameter_allowed(
    key: str,
    before: str,
    after: str,
    layout: ProfileLayout,
) -> bool:
    if key == AHCI_IMAGE_KEY:
        return before == "" and Path(after).is_file() and Path(after).resolve().is_relative_to(layout.root)
    before_path = Path(before)
    after_path = Path(after)
    return (
        before_path.is_absolute()
        and before_path.resolve(strict=False).is_relative_to(layout.deploy_image)
        and after_path.is_file()
        and after_path.resolve().is_relative_to(layout.artifacts)
    )


def fvp_config_delta(
    baseline: JsonObject,
    final: JsonObject,
    layout: ProfileLayout,
) -> list[str]:
    baseline_parameters = string_parameters(baseline)
    final_parameters = string_parameters(final)
    if baseline_parameters.keys() != final_parameters.keys():
        raise ProfileError("fvp_config_delta_forbidden", "parameter keys")
    allowed: list[str] = []
    for key, before in baseline_parameters.items():
        after = final_parameters[key]
        if before == after:
            continue
        if not changed_parameter_allowed(key, before, after, layout):
            raise ProfileError("fvp_config_delta_forbidden", key)
        allowed.append(f"parameters:{key}")
    baseline_data = baseline.get("data", [])
    final_data = final.get("data", [])
    if not isinstance(baseline_data, list) or not isinstance(final_data, list):
        raise ProfileError("fvp_config_delta_forbidden", "data shape")
    if len(baseline_data) != len(final_data):
        raise ProfileError("fvp_config_delta_forbidden", "data length")
    for index, before_value in enumerate(baseline_data):
        after_value = final_data[index]
        if before_value == after_value:
            continue
        if not isinstance(before_value, str) or not isinstance(after_value, str):
            raise ProfileError("fvp_config_delta_forbidden", "data type")
        before = Path(before_value.split("=", 1)[-1].split("@", 1)[0])
        after = Path(after_value.split("=", 1)[-1].split("@", 1)[0])
        if not before.resolve(strict=False).is_relative_to(layout.deploy_image):
            raise ProfileError("fvp_config_delta_forbidden", f"data:{index}")
        if not after.is_file() or not after.resolve().is_relative_to(layout.artifacts):
            raise ProfileError("fvp_config_delta_forbidden", f"data:{index}")
        allowed.append(f"data:{index}")
    ignored = {"parameters", "data"}
    baseline_rest: dict[str, JsonValue] = {
        key: value for key, value in baseline.items() if key not in ignored
    }
    final_rest: dict[str, JsonValue] = {
        key: value for key, value in final.items() if key not in ignored
    }
    if baseline_rest != final_rest:
        raise ProfileError("fvp_config_delta_forbidden", "top-level")
    if f"parameters:{AHCI_IMAGE_KEY}" not in allowed:
        raise ProfileError("fvp_config_delta_forbidden", "AHCI image unchanged")
    return allowed
