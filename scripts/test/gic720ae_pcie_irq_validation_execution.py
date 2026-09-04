from __future__ import annotations

from pathlib import Path

try:
    import gic720ae_pcie_irq_validation_contract as contract
    import gic720ae_pcie_irq_validation_provenance as provenance
    import gic720ae_pcie_irq_validation_result as result_contract
    import gic720ae_pcie_irq_validation_workflow as workflow
    import qbox_apollo_pcie_irq_task9_cleanup as task9_cleanup
    import qbox_apollo_pcie_irq_task9_process as task9_process
except ModuleNotFoundError:
    from scripts.test import gic720ae_pcie_irq_validation_contract as contract
    from scripts.test import gic720ae_pcie_irq_validation_provenance as provenance
    from scripts.test import gic720ae_pcie_irq_validation_result as result_contract
    from scripts.test import gic720ae_pcie_irq_validation_workflow as workflow
    from scripts.test import qbox_apollo_pcie_irq_task9_cleanup as task9_cleanup
    from scripts.test import qbox_apollo_pcie_irq_task9_process as task9_process


def cleanup_after_failure(task9_root: Path) -> contract.JsonObject:
    receipts: dict[str, contract.JsonValue] = {}
    for mode in ("msix", "intx"):
        out_dir = task9_root / mode
        if not out_dir.is_dir():
            continue
        task9_cleanup.terminate_task_owned(out_dir)
        receipt = out_dir / "task9-process-cleanup.json"
        if receipt.is_file():
            receipts[mode] = workflow.file_binding(receipt)
    residual: list[contract.JsonValue] = list(
        task9_process.residual_processes(task9_root)
    )
    return {
        "status": "PASS" if not residual else "FAIL",
        "residual_pids": residual,
        "receipts": receipts,
    }


def execute(config: contract.RunConfig, closure: contract.JsonObject) -> int:
    completed = {
        "parse_hash_inputs",
        "validate_fvp_gate",
        "provenance_preflight",
    }
    failed: str | None = None
    qbox_started = False
    children: dict[str, contract.JsonValue] = {}
    ap_map_payload: contract.JsonObject = {"status": "NOT_RUN"}
    task9_payload: contract.JsonObject = {"status": "NOT_RUN", "artifacts": {}}
    task10_payload: contract.JsonObject = {"status": "NOT_RUN"}
    run_root = config.run_root
    run_root.mkdir(parents=True, exist_ok=False)
    closure_path = config.provenance_output or run_root / "provenance.json"
    provenance.atomic_write(closure_path, closure)
    try:
        build = workflow.run_child(
            ("./yocto_build.sh", "--bsp"),
            run_root / "qbox-build.log",
            config.timeout,
            run_root / "qbox-build-process.json",
        )
        children["qbox_build"] = result_contract.child_binding(build)
        workflow.require_child(build, "qbox_build")
        if provenance.binary_identity(config.qbox_binary).get("status") != "PRESENT":
            raise contract.ValidationError("qbox_binary_missing")
        completed.add("qbox_build")
        provenance.assert_unchanged(config, closure)

        ap_map_payload = {"status": "FAIL"}
        audit_path = workflow.prepare_ap_map_audit(config)
        audit = workflow.run_child(
            workflow.ap_map_audit_command(config),
            run_root / "ap-map-audit.log",
            config.timeout,
            run_root / "ap-map-audit-process.json",
        )
        children["ap_memory_map_audit"] = result_contract.child_binding(audit)
        workflow.require_child(audit, "ap_memory_map_audit")
        audit_artifact = workflow.validate_ap_map_audit(config, audit_path)
        ap_map_payload = {"status": "PASS", "artifact": audit_artifact.binding()}
        completed.add("ap_memory_map_audit")
        closure = provenance.bind_ap_map_audit(closure, config, audit_artifact)
        provenance.atomic_write(closure_path, closure)
        provenance.assert_unchanged(config, closure)

        task9 = workflow.run_child(
            workflow.task9_command(config, audit_artifact),
            run_root / "task9-host.log",
            config.timeout,
            run_root / "task9-process.json",
        )
        children["task9"] = result_contract.child_binding(task9)
        workflow.require_child(task9, "task9_qualification")
        qbox_started = True
        provenance.assert_unchanged(config, closure)
        task9_payload = {
            "status": "PASS",
            "artifacts": workflow.task9_artifacts(run_root / "task9", audit_artifact),
        }
        completed.add("task9_qualification")

        task10 = workflow.run_child(
            workflow.task10_command(config),
            run_root / "task10-host.log",
            config.timeout,
            run_root / "task10-process.json",
        )
        children["task10"] = result_contract.child_binding(task10)
        workflow.require_child(task10, "task10_comparison")
        provenance.assert_unchanged(config, closure)
        task10_payload = {
            "status": "PASS",
            "comparison": workflow.comparison_binding(
                run_root / "boundary-comparison.json"
            ),
        }
        completed.add("task10_comparison")

        cleanup = workflow.cleanup_audit(run_root / "task9")
        completed.add("cleanup_audit")
        provenance.assert_unchanged(config, closure)
        completed.add("atomic_final_result")
        payload = result_contract.build(
            result_contract.ResultInputs(
                config,
                closure_path,
                completed,
                None,
                "ok",
                qbox_started,
                children,
                ap_map_payload,
                task9_payload,
                task10_payload,
                cleanup,
            )
        )
    except (contract.ValidationError, OSError) as error:
        reason = str(error)
        try:
            provenance.assert_unchanged(config, closure)
        except contract.ValidationError as provenance_error:
            if str(provenance_error) == "provenance_changed":
                reason = str(provenance_error)
        qbox_started = qbox_started or any(
            (run_root / "task9" / mode / "task9-process-registry.json").is_file()
            for mode in ("msix", "intx")
        )
        for phase in workflow.PHASES:
            if phase not in completed:
                failed = phase
                break
        cleanup = cleanup_after_failure(run_root / "task9")
        payload = result_contract.build(
            result_contract.ResultInputs(
                config,
                closure_path,
                completed,
                failed,
                reason,
                qbox_started,
                children,
                ap_map_payload,
                task9_payload,
                task10_payload,
                cleanup,
            )
        )
    contract.validate_schema(payload, contract.RESULT_SCHEMA, "result_schema")
    provenance.atomic_write(run_root / "result.json", payload)
    print(f"overall={payload['overall']}")
    print(run_root / "result.json")
    return 0 if payload["overall"] == "PASS" else 1


def build_only(config: contract.RunConfig, closure: contract.JsonObject) -> int:
    if config.provenance_output is None:
        raise contract.ValidationError("build_only_provenance_output")
    log = config.provenance_output.with_suffix(".build.log")
    registry = config.provenance_output.with_suffix(".build-process.json")
    result = workflow.run_child(
        ("./yocto_build.sh", "--bsp"), log, config.timeout, registry
    )
    workflow.require_child(result, "qbox_build")
    if provenance.binary_identity(config.qbox_binary).get("status") != "PRESENT":
        raise contract.ValidationError("qbox_binary_missing")
    audit_path = workflow.prepare_ap_map_audit(config)
    audit = workflow.run_child(
        workflow.ap_map_audit_command(config),
        config.provenance_output.with_suffix(".audit.log"),
        config.timeout,
        config.provenance_output.with_suffix(".audit-process.json"),
    )
    workflow.require_child(audit, "ap_memory_map_audit")
    audit_artifact = workflow.validate_ap_map_audit(config, audit_path)
    current = provenance.build(config)
    current = provenance.bind_ap_map_audit(current, config, audit_artifact)
    if config.frozen_provenance is not None:
        provenance.compare_frozen(
            current, config.frozen_provenance, config.run_root
        )
    provenance.atomic_write(config.provenance_output, current)
    print("status=BUILD_ONLY")
    print("full_qualification=false")
    return 0
