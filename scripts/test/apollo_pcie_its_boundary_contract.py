from __future__ import annotations

from dataclasses import dataclass


BINDINGS = frozenset(("contract_collection_entry_size", "fvp_gate_schema_version", "fvp_reference_gate_sha256", "intx_ap_map_sha256", "intx_coverage_sha256", "intx_input_sha256", "intx_log_sha256", "intx_result_sha256", "intx_rootfs_sha256", "msix_ap_map_sha256", "msix_coverage_sha256", "msix_input_sha256", "msix_log_sha256", "msix_result_sha256", "msix_rootfs_sha256", "pair_result_sha256", "pcie_runtime_schema_version", "profile_schema_version", "qbox_profile_manifest_sha256", "qualification_schema_version", "qualification_sha256", "run_id", "spi_result_sha256", "spi_runtime_schema_version"))
type JsonValue = str | int | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
type Json = dict[str, JsonValue]


@dataclass(frozen=True, slots=True)
class BoundaryError(Exception):
    reason: str

    def __str__(self) -> str:
        return self.reason

@dataclass(frozen=True, slots=True)
class Row:
    key: str
    scope: str
    detail: str
    refs: tuple[str, ...]


ROWS = tuple(Row(*value) for value in (
    ("fvp_model_configuration", "FVP", "immutable configuration applied", ("fvp_reference_gate_sha256",)), ("fvp_ecam_first_read_serror", "FVP", "immutable ECAM limitation gate", ("fvp_reference_gate_sha256",)), ("fvp_cleanup", "FVP", "reference gate cleanup passed", ("fvp_reference_gate_sha256",)), ("fvp_reference_gate", "FVP", "reference gate PASS, qualification unsupported", ("fvp_reference_gate_sha256",)),
    ("qbox_msix_endpoint", "QBOX", "same PCI endpoint is bound", ("pair_result_sha256", "msix_result_sha256")), ("qbox_msix_workload", "QBOX", "endpoint workload passed", ("pair_result_sha256", "msix_log_sha256")), ("qbox_msix_its_lpi", "QBOX", "ordered physical ITS LPI chain passed", ("pair_result_sha256", "msix_result_sha256", "msix_rootfs_sha256")), ("qbox_msix_affinity", "QBOX", "CPU0 and CPU1 affinity passed", ("pair_result_sha256", "msix_log_sha256")), ("qbox_msix_offline_fallback", "QBOX", "offline fallback reached CPU0", ("pair_result_sha256", "msix_log_sha256")), ("qbox_msix_replay", "QBOX", "replay reached CPU1", ("pair_result_sha256", "msix_log_sha256")), ("qbox_msix_cleanup", "QBOX", "MSI-X cleanup passed", ("qualification_sha256", "msix_result_sha256")),
    ("qbox_intx_same_bdf", "QBOX", "INTx uses same PCI BDF", ("pair_result_sha256", "intx_result_sha256")), ("qbox_intx_empty_msi", "QBOX", "INTx chain has no MSI domain", ("pair_result_sha256", "intx_result_sha256")), ("qbox_intx_hwirq333", "QBOX", "INTx hwirq is 333", ("pair_result_sha256", "intx_result_sha256", "intx_rootfs_sha256")), ("qbox_intx_workload", "QBOX", "INTx workload passed", ("pair_result_sha256", "intx_log_sha256")), ("qbox_intx_cleanup", "QBOX", "INTx cleanup passed", ("qualification_sha256", "intx_result_sha256")),
    ("qbox_spi_hwirq293", "QBOX", "virtio-mmio hwirq is 293", ("spi_result_sha256", "msix_log_sha256")), ("qbox_spi_positive_delta", "QBOX", "isolated SPI delta is positive", ("spi_result_sha256", "msix_log_sha256")), ("qbox_spi_zero_pci_delta", "QBOX", "PCI vector delta is zero", ("spi_result_sha256", "msix_log_sha256")), ("qbox_spi_cleanup", "QBOX", "SPI cleanup passed", ("spi_result_sha256", "qualification_sha256")),
    ("qbox_msix_coverage", "QBOX", "MSI-X coverage passed", ("msix_coverage_sha256", "msix_result_sha256")), ("qbox_intx_coverage", "QBOX", "INTx coverage passed", ("intx_coverage_sha256", "intx_result_sha256")), ("qbox_msix_ap_map", "QBOX", "MSI-X AP-map audit passed", ("msix_ap_map_sha256", "msix_coverage_sha256")), ("qbox_intx_ap_map", "QBOX", "INTx AP-map audit passed", ("intx_ap_map_sha256", "intx_coverage_sha256")),
))
ROW_BY_KEY = {row.key: row for row in ROWS}


def row_schema(row: Row) -> Json:
    properties: Json = {"id": {"const": row.key}, "scope": {"const": row.scope}, "status": {"const": "UNSUPPORTED" if row.scope == "FVP" else "PASS"}, "detail": {"const": row.detail}, "bindings": {"type": "array", "minItems": len(row.refs), "maxItems": len(row.refs), "uniqueItems": True, "items": {"enum": list(sorted(row.refs))}}}
    result: Json = {"type": "object", "required": ["id", "scope", "status", "detail", "bindings"], "properties": properties, "additionalProperties": False}
    return result

def normalize_refs(value: JsonValue) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) for item in value):
        raise BoundaryError("row_bindings")
    refs: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise BoundaryError("row_bindings")
        refs.append(item)
    return tuple(sorted(refs))

def schema() -> Json:
    properties: Json = {"schema_version": {"const": 1}, "status": {"enum": ["PASS", "FAIL"]}, "reason": {"type": "string"}, "fvp_qualification": {"const": "UNSUPPORTED"}, "device_equivalence": {"const": "NOT_COMPARABLE"}, "bindings": {"type": "object"}, "rows": {"type": "object"}}
    rows: Json = {row.key: row_schema(row) for row in ROWS}
    pass_rules: Json = {"bindings": {"required": list(sorted(BINDINGS)), "propertyNames": {"enum": list(sorted(BINDINGS))}, "minProperties": len(BINDINGS), "maxProperties": len(BINDINGS)}, "rows": {"required": [row.key for row in ROWS], "properties": rows, "additionalProperties": False, "minProperties": len(ROWS), "maxProperties": len(ROWS)}}
    condition: Json = {"if": {"properties": {"status": {"const": "PASS"}}}, "then": {"properties": pass_rules}}
    result: Json = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": ["schema_version", "status", "reason", "fvp_qualification", "device_equivalence", "bindings", "rows"], "properties": properties, "additionalProperties": False, "allOf": [condition]}
    return result
