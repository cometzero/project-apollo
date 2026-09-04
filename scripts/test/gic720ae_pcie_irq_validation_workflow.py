from __future__ import annotations

import os
from pathlib import Path
import signal
import subprocess
import sys
from typing import Final

try:
    import gic720ae_pcie_irq_validation_ap_map as ap_map
    import gic720ae_pcie_irq_validation_contract as contract
    import gic720ae_pcie_irq_validation_provenance as provenance
    import qbox_apollo_pcie_irq_task9_cleanup as task9_cleanup
    import qbox_apollo_pcie_irq_task9_process as task9_process
except ModuleNotFoundError:
    from scripts.test import gic720ae_pcie_irq_validation_ap_map as ap_map
    from scripts.test import gic720ae_pcie_irq_validation_contract as contract
    from scripts.test import gic720ae_pcie_irq_validation_provenance as provenance
    from scripts.test import qbox_apollo_pcie_irq_task9_cleanup as task9_cleanup
    from scripts.test import qbox_apollo_pcie_irq_task9_process as task9_process


TASK9_ADAPTER: Final = (
    contract.ROOT / "scripts/test/run_gic720ae_pcie_irq_validation_task9.py"
)
TASK10_ADAPTER: Final = (
    contract.ROOT / "scripts/test/run_gic720ae_pcie_irq_validation_task10.py"
)
AP_MAP_AUDIT_RELATIVE: Final = Path("scripts/test/audit_qbox_apollo_ap_memory_map.py")
PHASES: Final = (
    "parse_hash_inputs",
    "validate_fvp_gate",
    "provenance_preflight",
    "qbox_build",
    "ap_memory_map_audit",
    "task9_qualification",
    "task10_comparison",
    "cleanup_audit",
    "atomic_final_result",
)


def ap_map_audit_path(config: contract.RunConfig) -> Path:
    return ap_map.expected_path(config.run_root)


def ap_map_audit_command(config: contract.RunConfig) -> tuple[str, ...]:
    return (
        sys.executable,
        str(AP_MAP_AUDIT_RELATIVE),
        "--output",
        str(ap_map_audit_path(config)),
    )


def task9_command(
    config: contract.RunConfig, artifact: ap_map.ApMapArtifact | None = None
) -> tuple[str, ...]:
    sha256 = artifact.sha256 if artifact is not None else "${AP_MAP_SHA256}"
    size = str(artifact.size) if artifact is not None else "${AP_MAP_SIZE}"
    return (
        sys.executable,
        str(TASK9_ADAPTER.relative_to(contract.ROOT)),
        "--fvp-reference-gate",
        str(config.gate.resolve()),
        "--qbox-profile-manifest",
        str(config.profile.resolve()),
        "--run-root",
        str(config.run_root / "task9"),
        "--ap-map-audit",
        str(ap_map_audit_path(config)),
        "--ap-map-audit-sha256",
        sha256,
        "--ap-map-audit-size",
        size,
    )


def task10_command(config: contract.RunConfig) -> tuple[str, ...]:
    return (
        sys.executable,
        str(TASK10_ADAPTER.relative_to(contract.ROOT)),
        "--fvp-reference-gate",
        str(config.gate.resolve()),
        "--qbox-profile-manifest",
        str(config.profile.resolve()),
        "--qbox-run-root",
        str(config.run_root / "task9"),
        "--output",
        str(config.run_root / "boundary-comparison.json"),
    )


def display_plan(config: contract.RunConfig) -> tuple[str, ...]:
    commands = {
        "qbox_build": "./yocto_build.sh --bsp",
        "ap_memory_map_audit": " ".join(ap_map_audit_command(config)),
        "task9_qualification": " ".join(task9_command(config)),
        "task10_comparison": " ".join(task10_command(config)),
    }
    lines: list[str] = []
    for index, phase in enumerate(PHASES, start=1):
        lines.append(f"{index:02d} {phase}")
        command = commands.get(phase)
        if command is not None:
            lines.append(f"   {command}")
    lines.extend(
        (
            f"fvp_reference_gate={config.gate.resolve()}",
            f"qbox_profile_manifest={config.profile.resolve()}",
            f"run_root={config.run_root}",
            "fvp_started=false",
        )
    )
    return tuple(lines)


def terminate_child(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=10)


def run_child(
    command: tuple[str, ...], log: Path, timeout: int, registry: Path
) -> contract.ChildResult:
    registry_payload: contract.JsonObject = {
        "schema_version": 1,
        "status": "REGISTERED_BEFORE_SPAWN",
        "command": list(command),
        "uid": os.getuid(),
        "pid": None,
        "pgid": None,
    }
    provenance.atomic_write(registry, registry_payload)
    process: subprocess.Popen[bytes] | None = None
    with log.open("wb") as stream:
        try:
            process = subprocess.Popen(
                command,
                cwd=contract.ROOT,
                stdout=stream,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            registry_payload["status"] = "SPAWNED"
            registry_payload["pid"] = process.pid
            registry_payload["pgid"] = process.pid
            provenance.atomic_write(registry, registry_payload)
            returncode = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired as error:
            if process is not None:
                terminate_child(process)
                registry_payload["status"] = "TERMINATED"
                registry_payload["reason"] = "timeout"
                registry_payload["returncode"] = process.returncode
                provenance.atomic_write(registry, registry_payload)
            raise contract.ValidationError(f"child_timeout:{command[0]}") from error
        except contract.ValidationError:
            if process is not None:
                terminate_child(process)
                registry_payload["status"] = "TERMINATED"
                registry_payload["reason"] = "interrupted"
                registry_payload["returncode"] = process.returncode
                provenance.atomic_write(registry, registry_payload)
            raise
        finally:
            if process is not None:
                terminate_child(process)
    registry_payload["status"] = "EXITED"
    registry_payload["returncode"] = returncode
    provenance.atomic_write(registry, registry_payload)
    return contract.ChildResult(command, returncode, log)


def require_child(result: contract.ChildResult, reason: str) -> None:
    if result.returncode != 0:
        raise contract.ValidationError(f"{reason}:{result.returncode}")


def prepare_ap_map_audit(config: contract.RunConfig) -> Path:
    path = ap_map_audit_path(config)
    root = config.run_root.absolute()
    if (
        path.parent != root
        or not path.is_relative_to(root)
        or root.is_symlink()
        or any(parent.is_symlink() for parent in root.parents)
    ):
        raise contract.ValidationError("ap_memory_map_audit_path")
    for parent in path.parents:
        if parent == root:
            break
        if parent.is_symlink():
            raise contract.ValidationError("ap_memory_map_audit_parent_symlink")
    path.unlink(missing_ok=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def validate_ap_map_audit(
    config: contract.RunConfig, path: Path
) -> ap_map.ApMapArtifact:
    if path.absolute() != ap_map.expected_path(config.run_root):
        raise contract.ValidationError("ap_memory_map_audit_path")
    return ap_map.load(path, config.run_root, "ap_memory_map_audit")


def file_binding(path: Path) -> contract.JsonObject:
    return {
        "path": str(path.resolve()),
        "sha256": contract.digest(path),
        "size": path.stat().st_size,
    }


def task9_artifacts(
    root: Path, artifact: ap_map.ApMapArtifact | None = None
) -> dict[str, contract.JsonValue]:
    bound = artifact or ap_map.task11_artifact(
        root.parent, ap_map.expected_path(root.parent)
    )
    paths = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix in (".json", ".log", ".txt")
    )
    artifacts: dict[str, contract.JsonValue] = {
        str(path.relative_to(root)).replace("/", "_"): file_binding(path)
        for path in paths
    }
    for mode in ("msix", "intx"):
        ap_map.validate_coverage(root / f"{mode}-coverage-audit.json", bound)
        artifacts[f"{mode}_ap_map_audit"] = bound.binding()
    return artifacts


def cleanup_audit(root: Path) -> contract.JsonObject:
    residual = task9_process.residual_processes(root)
    mode_receipts: dict[str, contract.JsonValue] = {}
    for mode in ("msix", "intx"):
        out_dir = root / mode
        task9_cleanup.terminate_task_owned(out_dir)
        receipt = contract.load_object(
            out_dir / "task9-process-cleanup.json", f"{mode}_cleanup_receipt"
        )
        if receipt.get("status") != "PASS":
            raise contract.ValidationError(f"{mode}_cleanup")
        mode_receipts[mode] = file_binding(out_dir / "task9-process-cleanup.json")
    if residual:
        raise contract.ValidationError("cleanup_residual_processes")
    return {"status": "PASS", "residual_pids": [], "receipts": mode_receipts}


def comparison_binding(path: Path) -> contract.JsonObject:
    payload = contract.load_object(path, "task10_comparison_json")
    contract.validate_schema(
        payload,
        contract.ROOT / "tests/schemas/apollo-pcie-its-boundary-comparison.schema.json",
        "task10_comparison_schema",
    )
    if payload.get("status") != "PASS":
        raise contract.ValidationError("task10_comparison")
    return file_binding(path)
