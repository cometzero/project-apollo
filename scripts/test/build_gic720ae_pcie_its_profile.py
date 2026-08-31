#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Final


SCRIPT_DIR: Final = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gic720ae_pcie_its_profile.build import (  # noqa: E402
    BuildContext,
    create_scratch_disk,
    deploy_manifest,
    oe_environment,
    run,
    write_json,
    write_override,
)
from gic720ae_pcie_its_profile.contract import (  # noqa: E402
    JsonObject,
    ProfileError,
    ProfileLayout,
    failure_receipt,
    hash_record as hash_record,
    load_json,
    validate_dtb_contract as validate_dtb_contract,
    validate_fvp_config as validate_fvp_config,
    validate_hash_record as validate_hash_record,
    validate_kernel_config as validate_kernel_config,
    validate_receipt,
    validate_scratch_disk as validate_scratch_disk,
    validate_uki_dtbs as validate_uki_dtbs,
)
from gic720ae_pcie_its_profile.dt_delivery import (  # noqa: E402
    linux_dtb_reference as linux_dtb_reference,
    validate_fip_hw_config as validate_fip_hw_config,
    validate_uki_sections as validate_uki_sections,
)
from gic720ae_pcie_its_profile.finalize import (  # noqa: E402
    FinalizeRequest,
    finalize_profile,
)
from gic720ae_pcie_its_profile.provenance import (  # noqa: E402
    authorize_path_containment_refresh as authorize_path_containment_refresh,
    validate_artifact_records as validate_artifact_records,
    validate_launchable_source_closure as validate_launchable_source_closure,
    validate_source_hash_claim as validate_source_hash_claim,
    validate_task_sigdata_records as validate_task_sigdata_records,
)
from gic720ae_pcie_its_profile import workflow as profile_workflow  # noqa: E402

safe_log_output = profile_workflow.safe_log_output
validate_output_capacity = profile_workflow.validate_output_capacity


def build(args: argparse.Namespace) -> JsonObject:
    workspace = Path(__file__).resolve().parents[2]
    if args.machine != "apollo-fvp":
        raise ProfileError("unsupported_machine", args.machine)
    if args.timeout <= 0:
        raise ProfileError("invalid_timeout", str(args.timeout))
    layout = ProfileLayout.create(args.output_root, workspace)
    capacity = profile_workflow.preflight_output_capacity(layout.root)
    if args.refresh_provenance_after_path_remediation:
        if args.resume_postprocess:
            raise ProfileError("incompatible_profile_modes")
        if not layout.root.is_dir():
            raise ProfileError("resume_profile_missing", str(layout.root))
        prior = load_json(layout.root / "profile.json")
        return finalize_profile(FinalizeRequest(
            workspace=workspace,
            layout=layout,
            capacity=capacity,
            timeout=args.timeout,
            bitbake_rerun=False,
            prior_receipt=prior,
            refresh_reason="path_containment_remediation",
        ))
    if args.resume_postprocess:
        if not layout.root.is_dir():
            raise ProfileError("resume_profile_missing", str(layout.root))
        prior = load_json(layout.root / "profile.json")
        return finalize_profile(FinalizeRequest(
            workspace=workspace,
            layout=layout,
            capacity=capacity,
            timeout=args.timeout,
            bitbake_rerun=False,
            prior_receipt=prior,
            refresh_reason=None,
        ))
    if layout.root.exists() and any(layout.root.iterdir()):
        raise ProfileError("output_root_not_empty", str(layout.root))
    for path in (layout.tmp, layout.deploy_image, layout.sstate, layout.logs, layout.artifacts):
        path.mkdir(parents=True, exist_ok=True)
    default_root = workspace / "build/tmp_baremetal/deploy/images/apollo-fvp"
    before_manifest = deploy_manifest(default_root)
    before_path = layout.root / "default-deploy-before.json"
    write_json(before_path, before_manifest)
    create_scratch_disk(
        BuildContext(workspace, layout, oe_environment(workspace), args.timeout)
    )
    include = write_override(layout, workspace)
    default_include = profile_workflow.write_default_contract_override(layout)
    context = BuildContext(workspace, layout, oe_environment(workspace), args.timeout)
    default_environment = run(
        context,
        ["bitbake", "-R", str(default_include), "-e", "virtual/kernel"],
        "default-kernel-environment.log",
    )
    default_fragment = profile_workflow.environment_value(
        default_environment, "APOLLO_KERNEL_CONFIG_FRAGMENT"
    )
    if default_fragment != "":
        raise ProfileError("default_kernel_fragment_enabled", default_fragment)
    profile_environment = run(
        context,
        ["bitbake", "-R", str(include), "-e", "virtual/kernel"],
        "profile-kernel-environment.log",
    )
    if profile_workflow.environment_value(
        profile_environment, "APOLLO_KERNEL_CONFIG_FRAGMENT"
    ) != "gic720ae-pcie-its.cfg":
        raise ProfileError("profile_kernel_fragment_missing")
    run(
        context,
        ["bitbake", "-R", str(include), "nexios-bsp-initramfs"],
        "image-build.log",
    )
    baseline_fvpconf = layout.deploy_image / "nexios-bsp-initramfs-apollo-fvp.fvpconf"
    baseline_config = load_json(baseline_fvpconf)
    bindir = baseline_config.get("fvp-bindir")
    executable = baseline_config.get("exe")
    if not isinstance(bindir, str) or not isinstance(executable, str):
        raise ProfileError("fvp_executable_missing")
    declared_receipt_path = layout.artifacts / "configuration/model-declared.json"
    run(
        context,
        [
            "python3", "scripts/test/capture_apollo_fvp_pcie_model.py",
            "--fvp", str(Path(bindir) / executable),
            "--fvpconf", str(baseline_fvpconf),
            "--schema", "tests/schemas/apollo-fvp-pcie-model-contract.schema.json",
            "--output", str(declared_receipt_path),
        ],
        "capture-model-declared.log",
    )
    profile_workflow.validate_declared_contract(load_json(declared_receipt_path))
    return finalize_profile(FinalizeRequest(
        workspace=workspace,
        layout=layout,
        capacity=capacity,
        timeout=args.timeout,
        bitbake_rerun=True,
        prior_receipt=None,
        refresh_reason=None,
    ))


def main(argv: list[str] | None = None) -> int:
    args = profile_workflow.parse_args(sys.argv[1:] if argv is None else argv)
    workspace = Path(__file__).resolve().parents[2]
    schema_path = workspace / "tests/schemas/gic720ae-pcie-its-profile.schema.json"
    schema = load_json(schema_path)
    try:
        trusted_layout = ProfileLayout.create(args.output_root, workspace)
    except ProfileError as error:
        print(
            json.dumps({"reason": error.reason, "detail": error.detail}, sort_keys=True),
            file=sys.stderr,
        )
        return 1
    try:
        receipt = build(args)
        validate_receipt(receipt, schema)
        output = profile_workflow.write_receipt_atomic(
            trusted_layout, workspace, receipt
        )
    except ProfileError as error:
        if args.refresh_provenance_after_path_remediation:
            print(
                json.dumps({"reason": error.reason, "detail": error.detail}, sort_keys=True),
                file=sys.stderr,
            )
            return 1
        receipt = failure_receipt(error.reason, args.output_root)
        validate_receipt(receipt, schema)
        try:
            profile_workflow.write_receipt_atomic(
                trusted_layout, workspace, receipt
            )
        except ProfileError as receipt_error:
            print(
                json.dumps(
                    {
                        "reason": error.reason,
                        "detail": error.detail,
                        "receipt_reason": receipt_error.reason,
                    },
                    sort_keys=True,
                ),
                file=sys.stderr,
            )
            return 1
        print(json.dumps({"reason": error.reason, "detail": error.detail}, sort_keys=True), file=sys.stderr)
        return 1
    print(json.dumps({"status": "pass", "profile": str(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
