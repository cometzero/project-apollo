from __future__ import annotations

from pathlib import Path

import apollo_pcie_its_boundary_contract as contract
import apollo_pcie_its_boundary_io as boundary_io
import jsonschema

ROOT = Path(__file__).resolve().parents[2]
PROFILE_SCHEMA = ROOT / "tests/schemas/apollo-qbox-pcie-irq-profile.schema.json"
RUNTIME_SCHEMA = ROOT / "tests/schemas/apollo-pcie-its-runtime.schema.json"
SPI_SCHEMA = ROOT / "tests/schemas/apollo-qbox-pcie-irq-spi.schema.json"
FVP_SHA256 = "5ceb377244eb0e4fddd6e4346a701fa1a75185d0dc689d2e396c917cb3549a82"
PROFILE_SHA256 = "d0fd532fc4e07edbe02d62ae06cb6afb84663b69cdf0f139729bc3a3f65cf03b"
type JsonValue = str | int | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
type Json = dict[str, JsonValue]


class BoundaryError(ValueError):
    pass


def need(value: JsonValue | None, expected: JsonValue, reason: str) -> None:
    if value != expected:
        raise BoundaryError(reason)


def object_at(value: JsonValue | None, reason: str) -> Json:
    if not isinstance(value, dict):
        raise BoundaryError(reason)
    return value


def array_at(value: JsonValue | None, reason: str) -> list[JsonValue]:
    if not isinstance(value, list):
        raise BoundaryError(reason)
    return value


def schema(value: Json, path: Path, reason: str) -> None:
    try:
        jsonschema.Draft202012Validator(boundary_io.load_json(path, reason)).validate(value)
    except (OSError, jsonschema.ValidationError) as error:
        raise BoundaryError(reason) from error


def symlink_free(path: Path) -> bool:
    return not any(parent.is_symlink() for parent in (path, *path.parents))


def run_root(path: Path) -> Path:
    root = path.absolute()
    if not root.is_dir() or not symlink_free(root):
        raise BoundaryError("qbox_run_root")
    return root


def contained_file(root: Path, relative: str, reason: str) -> Path:
    path = (root / relative).absolute()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise BoundaryError(reason) from error
    if not path.is_file() or not symlink_free(path):
        raise BoundaryError(reason)
    return path


def absolute_file(value: JsonValue | None, reason: str) -> Path:
    path = Path(str(value))
    if not path.is_absolute() or not path.is_file() or not symlink_free(path):
        raise BoundaryError(reason)
    return path


def artifact(entry: Json, reason: str) -> tuple[Path, str]:
    path = absolute_file(entry.get("path"), reason)
    expected = entry.get("sha256")
    if not isinstance(expected, str) or boundary_io.digest(path) != expected:
        raise BoundaryError(reason)
    return path, expected


def phase(payload: Json, name: str, cpu: int, reason: str) -> None:
    item = object_at(object_at(payload.get("phases"), reason).get(name), reason)
    values = item.get("delta")
    if not isinstance(values, list) or len(values) < 2 or not all(isinstance(value, int) for value in values):
        raise BoundaryError(reason)
    target_delta = values[cpu]
    if item.get("effective_cpu") != cpu or not isinstance(target_delta, int) or target_delta <= 0 or any(not isinstance(value, int) or value != 0 for index, value in enumerate(values) if index != cpu):
        raise BoundaryError(reason)


def check_mode(payload: Json, mode: str, log_hash: str, input_hash: str) -> None:
    schema(payload, RUNTIME_SCHEMA, f"{mode}_runtime_schema")
    need(payload.get("schema_version"), 1, "runtime_schema_version")
    need(payload.get("status"), "pass", f"{mode}_status")
    need(payload.get("platform"), "qbox", f"{mode}_platform")
    need(payload.get("mode"), mode, f"{mode}_mode")
    need(payload.get("source_log_sha256"), log_hash, f"{mode}_source_log")
    need(payload.get("input_sha256"), input_hash, f"{mode}_input_hash")
    need(payload.get("input_sha256_valid"), True, f"{mode}_input_hash")
    endpoint = object_at(payload.get("endpoint"), f"{mode}_endpoint")
    for key, expected in {"bdf": "0000:00:01.0", "driver": "virtio-pci", "target": "eth1"}.items():
        need(endpoint.get(key), expected, f"{mode}_endpoint")
    cleanup = object_at(payload.get("cleanup"), f"{mode}_cleanup")
    if cleanup.get("rc") != "0" or cleanup.get("affinity_restored") != "1" or cleanup.get("cpu1_restored") != "1":
        raise BoundaryError(f"{mode}_cleanup")
    for name, cpu in (("cpu0", 0), ("cpu1", 1), ("offline", 0), ("replay", 1)):
        phase(payload, name, cpu, f"{mode}_{name}")


def coverage_binding(root: Path, mode: str, result: Path) -> tuple[str, str]:
    coverage_path = contained_file(root, f"{mode}-coverage-audit.json", f"{mode}_coverage")
    coverage = boundary_io.load_json(coverage_path, f"{mode}_coverage")
    if coverage.get("passed") is not True or coverage.get("runtime_result") != str(result):
        raise BoundaryError(f"{mode}_coverage")
    memory = object_at(coverage.get("ap_9_1_1_memory_map"), f"{mode}_ap_map")
    ap_map = absolute_file(memory.get("audit_path"), f"{mode}_ap_map")
    if memory.get("passed") is not True or memory.get("audit_passed") is not True or boundary_io.load_json(ap_map, f"{mode}_ap_map").get("passed") is not True:
        raise BoundaryError(f"{mode}_ap_map")
    return boundary_io.digest(coverage_path), boundary_io.digest(ap_map)


def qbox_rows(profile: Json, supplied_root: Path) -> tuple[list[JsonValue], Json]:
    root = run_root(supplied_root)
    schema(profile, PROFILE_SCHEMA, "profile_schema")
    need(profile.get("schema_version"), 2, "profile_schema_version")
    need(profile.get("profile"), "apollo-qvp-pcie-irq", "profile")
    profile_contract = object_at(profile.get("contract"), "profile_contract")
    need(profile_contract.get("legacy_gic_intid"), 333, "profile_contract")
    need(profile_contract.get("virtio_mmio_hwirq"), 293, "profile_contract")
    qualification_path = contained_file(root, "qualification.json", "qualification")
    qualification = boundary_io.load_json(qualification_path, "qualification")
    run_id = qualification.get("run_id")
    if not isinstance(run_id, str) or root.name != run_id:
        raise BoundaryError("run_id")
    need(qualification.get("schema_version"), 1, "qualification_schema_version")
    need(qualification.get("status"), "pass", "qualification_status")
    pins = object_at(qualification.get("pins"), "qualification_pins")
    need(pins.get("fvp_reference_gate_sha256"), FVP_SHA256, "qualification_fvp_pin")
    need(pins.get("profile_manifest_sha256"), PROFILE_SHA256, "qualification_profile_pin")
    cleanup = object_at(qualification.get("process_cleanup"), "qualification_cleanup")
    need(cleanup.get("status"), "PASS", "qualification_cleanup")
    need(cleanup.get("residual_pids"), [], "qualification_cleanup")
    modes = object_at(qualification.get("modes"), "qualification_modes")
    runtime_path = contained_file(root, "pcie-runtime-validation.json", "pcie_runtime")
    runtime = boundary_io.load_json(runtime_path, "pcie_runtime")
    need(runtime.get("schema_version"), 2, "pcie_schema_version")
    need(runtime.get("status"), "pass", "pcie_status")
    runtime_profile = object_at(runtime.get("profile_manifest"), "runtime_profile")
    need(runtime_profile.get("sha256"), PROFILE_SHA256, "runtime_profile")
    validated: dict[str, Json] = {}
    input_hashes: dict[str, str] = {}
    result_hashes: dict[str, str] = {}
    rootfs_hashes: dict[str, str] = {}
    coverage_hashes: dict[str, str] = {}
    ap_map_hashes: dict[str, str] = {}
    profile_modes = object_at(profile.get("modes"), "profile_modes")
    for mode in ("msix", "intx"):
        mode_run = object_at(modes.get(mode), "qualification_modes")
        result_path = contained_file(root, f"{mode}/result.json", f"{mode}_result")
        log_path = contained_file(root, f"{mode}/qbox-primary-console.log", f"{mode}_log")
        if boundary_io.digest(result_path) != mode_run.get("result_sha256") or boundary_io.digest(log_path) != mode_run.get("primary_log_sha256"):
            raise BoundaryError(f"{mode}_runner_binding")
        payload = object_at(runtime.get(mode), f"{mode}_runtime")
        artifacts = object_at(object_at(profile_modes.get(mode), "profile_mode").get("artifacts"), "profile_artifacts")
        _, input_hash = artifact(object_at(artifacts.get("input_manifest"), "profile_input"), "profile_input")
        disk, disk_hash = artifact(object_at(artifacts.get("disk"), "profile_rootfs"), f"{mode}_rootfs")
        if mode_run.get("rootfs_sha256") != disk_hash:
            raise BoundaryError(f"{mode}_rootfs")
        result = boundary_io.load_json(result_path, f"{mode}_result")
        rootfs = object_at(result.get("input_artifacts"), f"{mode}_result").get("rootfs")
        if object_at(rootfs, f"{mode}_result").get("path") != str(disk):
            raise BoundaryError(f"{mode}_result")
        check_mode(payload, mode, boundary_io.digest(log_path), input_hash)
        validated[mode] = payload
        input_hashes[mode] = input_hash
        result_hashes[mode] = boundary_io.digest(result_path)
        rootfs_hashes[mode] = disk_hash
        coverage_hashes[mode], ap_map_hashes[mode] = coverage_binding(root, mode, result_path)
    chain = array_at(validated["msix"].get("chain"), "msix_lpi")
    if len(chain) < 3 or object_at(chain[0], "msix_lpi").get("chip") != "PCI-MSIX" or object_at(chain[1], "msix_lpi").get("chip") != "ITS-MSI" or object_at(chain[2], "msix_lpi").get("chip") != "GICv3" or int(str(object_at(chain[1], "msix_lpi").get("hwirq", "0")), 0) < 8192:
        raise BoundaryError("msix_lpi")
    intx_chain = array_at(validated["intx"].get("chain"), "intx_hwirq")
    if len(intx_chain) != 1 or object_at(intx_chain[0], "intx_hwirq").get("chip") != "GICv3" or "MSI" in str(object_at(intx_chain[0], "intx_hwirq").get("domain", "")) or int(str(object_at(intx_chain[0], "intx_hwirq").get("hwirq", "0")), 0) != 333:
        raise BoundaryError("intx_hwirq")
    spi_path = contained_file(root, "spi-runtime-validation.json", "spi_runtime")
    spi = boundary_io.load_json(spi_path, "spi_runtime")
    schema(spi, SPI_SCHEMA, "spi_schema")
    need(spi.get("schema_version"), 1, "spi_schema_version")
    need(spi.get("status"), "pass", "spi_status")
    need(spi.get("source_log_sha256"), boundary_io.digest(contained_file(root, "msix/qbox-primary-console.log", "msix_log")), "spi_source_log")
    need(spi.get("input_sha256"), input_hashes["msix"], "spi_input_hash")
    spi_chain = array_at(spi.get("chain"), "spi_chain")
    spi_delta = array_at(spi.get("spi_delta"), "spi_isolation")
    pci_delta = array_at(spi.get("pci_vector_delta"), "spi_isolation")
    if not spi_chain or not spi_delta or not isinstance(spi_delta[0], int) or int(str(object_at(spi_chain[0], "spi_chain").get("hwirq", "0")), 0) != 293 or spi_delta[0] <= 0 or any(pci_delta):
        raise BoundaryError("spi_isolation")
    rows: list[JsonValue] = []
    for item in contract.ROWS:
        if item.scope != "QBOX":
            continue
        refs: list[JsonValue] = [ref for ref in sorted(item.refs)]
        row: Json = {
            "id": item.key,
            "scope": item.scope,
            "status": "PASS",
            "detail": item.detail,
            "bindings": refs,
        }
        rows.append(row)
    return rows, {
        "run_id": run_id, "qualification_schema_version": 1, "profile_schema_version": 2,
        "pcie_runtime_schema_version": 2, "spi_runtime_schema_version": 1,
        "contract_collection_entry_size": 2, "qualification_sha256": boundary_io.digest(qualification_path),
        "pair_result_sha256": boundary_io.digest(runtime_path), "spi_result_sha256": boundary_io.digest(spi_path),
        "msix_input_sha256": input_hashes["msix"], "intx_input_sha256": input_hashes["intx"],
        "msix_result_sha256": result_hashes["msix"], "intx_result_sha256": result_hashes["intx"],
        "msix_rootfs_sha256": rootfs_hashes["msix"], "intx_rootfs_sha256": rootfs_hashes["intx"],
        "msix_log_sha256": boundary_io.digest(contained_file(root, "msix/qbox-primary-console.log", "msix_log")),
        "intx_log_sha256": boundary_io.digest(contained_file(root, "intx/qbox-primary-console.log", "intx_log")),
        "msix_coverage_sha256": coverage_hashes["msix"], "intx_coverage_sha256": coverage_hashes["intx"],
        "msix_ap_map_sha256": ap_map_hashes["msix"], "intx_ap_map_sha256": ap_map_hashes["intx"],
    }
