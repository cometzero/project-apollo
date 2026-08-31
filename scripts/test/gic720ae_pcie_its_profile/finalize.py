from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .build import (
    BuildContext,
    artifact_records,
    boot_artifacts,
    copy_config_inputs,
    deploy_manifest,
    find_kernel_config,
    task_provenance,
    write_json,
)
from .contract import (
    JsonObject,
    JsonValue,
    ProfileError,
    ProfileLayout,
    hash_record,
    hash_record_json,
    load_json,
    sha256_file,
    validate_dtb_contract,
    validate_fvp_config,
    validate_hash_record,
    validate_kernel_config,
    validate_scratch_disk,
)
from .dt_delivery import inspect_dt_delivery
from .provenance import (
    BITBAKE_BUILD_INPUT_ROLES,
    RUNTIME_INPUT_ROLES,
    TOOL_POSTPROCESSOR_ROLES,
    active_sigdata_manifest,
    fvp_config_delta,
    repository_heads,
    source_hashes,
)
from .workflow import (
    referenced_file_records,
    validate_declared_contract,
    validate_prior_receipt,
)


@dataclass(frozen=True, slots=True)
class FinalizeRequest:
    workspace: Path
    layout: ProfileLayout
    capacity: JsonObject
    timeout: int
    bitbake_rerun: bool
    prior_receipt: JsonObject | None
    refresh_reason: str | None


def validate_image_build(log: Path) -> None:
    if not log.is_file():
        raise ProfileError("image_build_receipt_missing")
    content = log.read_text(encoding="utf-8")
    if "Tasks Summary:" not in content or "all succeeded" not in content:
        raise ProfileError("image_build_receipt_failed")
    if "ERROR:" in content:
        raise ProfileError("image_build_receipt_failed")


def validate_provenance_item(item: JsonObject) -> None:
    sigdata = item.get("sigdata")
    if not isinstance(sigdata, dict):
        raise ProfileError("task_provenance_missing")
    role = sigdata.get("role")
    path = sigdata.get("path")
    digest = sigdata.get("sha256")
    if not isinstance(role, str) or not isinstance(path, str) or not isinstance(digest, str):
        raise ProfileError("task_provenance_invalid")
    validate_hash_record({"role": role, "path": path, "sha256": digest})


def finalize_profile(request: FinalizeRequest) -> JsonObject:
    workspace = request.workspace
    layout = request.layout
    include = layout.root / "conf/gic720ae-pcie-its.inc"
    default_include = layout.root / "conf/default-kernel-contract.inc"
    refresh, prior_artifacts, prior_tasks = validate_prior_receipt(
        request.prior_receipt,
        layout,
        request.refresh_reason,
    )
    validate_image_build(layout.logs / "image-build.log")
    before_path = layout.root / "default-deploy-before.json"
    if not before_path.is_file():
        raise ProfileError("default_deploy_manifest_missing")
    active_sigdata_before = active_sigdata_manifest(workspace)
    sources = source_hashes(workspace)
    heads = repository_heads(workspace)
    context = BuildContext(
        workspace=workspace,
        layout=layout,
        environment={},
        timeout=request.timeout,
    )
    scratch_disk = layout.artifacts / "storage/apollo-gic-its-ahci.raw"
    validate_scratch_disk(scratch_disk)
    baseline_fvpconf = layout.deploy_image / "nexios-bsp-initramfs-apollo-fvp.fvpconf"
    baseline_config = load_json(baseline_fvpconf)
    declared_receipt_path = layout.artifacts / "configuration/model-declared.json"
    validate_declared_contract(load_json(declared_receipt_path))
    artifacts = boot_artifacts(layout)
    final_fvpconf, final_config = copy_config_inputs(
        baseline_fvpconf, artifacts, scratch_disk, layout
    )
    allowed_delta = fvp_config_delta(baseline_config, final_config, layout)
    fvp_contract = validate_fvp_config(final_config, layout.root)
    host_contract = validate_dtb_contract(artifacts["dtb"])
    dt_delivery, dt_files = inspect_dt_delivery(context, artifacts)
    kernel_config = find_kernel_config(layout)
    validate_kernel_config(kernel_config)
    provenance = [
        task_provenance(layout, "linux-yocto-rt", "do_compile"),
        task_provenance(layout, "nexios-bsp-initramfs", "do_image_complete"),
    ]
    for item in provenance:
        validate_provenance_item(item)
    after_path = layout.root / "default-deploy-after.json"
    write_json(
        after_path,
        deploy_manifest(workspace / "build/tmp_baremetal/deploy/images/apollo-fvp"),
    )
    if sha256_file(before_path) != sha256_file(after_path):
        raise ProfileError("default_deploy_contaminated")
    active_sigdata_after = active_sigdata_manifest(workspace)
    if active_sigdata_before != active_sigdata_after:
        raise ProfileError("active_default_taskhash_changed")
    for record in sources:
        validate_hash_record(record)
    final_argv = [
        str((workspace / "layers/meta-arm/scripts/runfvp").resolve()),
        "-t", "none", str(final_fvpconf.resolve()),
    ]
    final_argv_path = layout.artifacts / "final-argv.json"
    write_json(final_argv_path, final_argv)
    extra = [
        scratch_disk,
        final_fvpconf,
        declared_receipt_path,
        include,
        default_include,
        before_path,
        after_path,
        final_argv_path,
        kernel_config,
        *dt_files,
        *referenced_file_records(final_config),
    ]
    records = artifact_records(artifacts, extra)
    for record in records:
        if not Path(record["path"]).resolve().is_relative_to(layout.root):
            raise ProfileError("profile_path_escape", record["path"])
        validate_hash_record(record)
    if prior_artifacts and records != prior_artifacts:
        raise ProfileError("immutable_artifact_changed")
    if prior_tasks and provenance != prior_tasks:
        raise ProfileError("immutable_task_provenance_changed")
    source_json: list[JsonValue] = [hash_record_json(record) for record in sources]
    artifact_json: list[JsonValue] = [hash_record_json(record) for record in records]
    provenance_json: list[JsonValue] = [item for item in provenance]
    delta_json: list[JsonValue] = [value for value in allowed_delta]
    argv_json: list[JsonValue] = [value for value in final_argv]
    heads_json: JsonObject = {path: value for path, value in heads.items()}
    tool_roles: list[JsonValue] = [role for role in sorted(TOOL_POSTPROCESSOR_ROLES)]
    build_roles: list[JsonValue] = [role for role in sorted(BITBAKE_BUILD_INPUT_ROLES)]
    runtime_roles: list[JsonValue] = [role for role in sorted(RUNTIME_INPUT_ROLES)]
    source_classes: JsonObject = {
        "tool_postprocessor": tool_roles,
        "bitbake_build_input": build_roles,
        "runtime_input": runtime_roles,
    }
    configuration: JsonObject = {
        "configuration_declared": True,
        "baseline_contract": hash_record_json(
            hash_record("task1-declared-contract", declared_receipt_path)
        ),
        "baseline_fvpconf": hash_record_json(
            hash_record("baseline-fvpconf", baseline_fvpconf)
        ),
        "final_fvpconf": hash_record_json(hash_record("final-fvpconf", final_fvpconf)),
        "allowed_delta": delta_json,
        "kernel_fragment": hash_record_json(hash_record(
            "kernel-fragment",
            workspace / "hsoc-stack/yocto/meta-hsoc-bsp/recipes-kernel/linux/files/gic720ae-pcie-its.cfg",
        )),
        "kernel_config": hash_record_json(hash_record("isolated-kernel-config", kernel_config)),
        "bitbake_override": hash_record_json(hash_record("bitbake-override", include)),
        "default_fragment_value": "",
    }
    default_deploy: JsonObject = {
        "root": str((workspace / "build/tmp_baremetal/deploy/images/apollo-fvp").resolve()),
        "before_sha256": sha256_file(before_path),
        "after_sha256": sha256_file(after_path),
        "unchanged": True,
        "active_sigdata_unchanged": True,
    }
    build_inputs: JsonObject = {
        "image_build_completed": True,
        "profile_override": hash_record_json(hash_record("bitbake-override", include)),
        "task_sigdata_valid": True,
        "source_hashes_valid": True,
        "bitbake_rerun": request.bitbake_rerun,
    }
    receipt: JsonObject = {
        "format_version": 1,
        "verdict": "PASS",
        "reason": "isolated_pcie_its_profile_built",
        "machine": "apollo-fvp",
        "output_root": str(layout.root),
        "source_hashes": source_json,
        "repository_heads": heads_json,
        "source_classification": source_classes,
        "artifacts": artifact_json,
        "configuration": configuration,
        "task_provenance": provenance_json,
        "host_contract": host_contract,
        "dt_delivery": dt_delivery,
        "fvp_contract": fvp_contract,
        "default_deploy": default_deploy,
        "capacity": request.capacity,
        "build_input_verification": build_inputs,
        "final_argv": argv_json,
    }
    if refresh is not None:
        receipt["provenance_refresh"] = refresh
    return receipt
