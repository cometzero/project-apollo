from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Final, Literal, assert_never

import jsonschema

ROOT: Final = Path(__file__).resolve().parents[2]
CONTRACT_MODULE: Final = Path(__file__).resolve()
CANONICAL_FVP_GATE: Final = (
    ROOT
    / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current"
    / "fvp-reference-gate-current.json"
)
CANONICAL_FVP_GATE_SHA256: Final = (
    "5ceb377244eb0e4fddd6e4346a701fa1a75185d0dc689d2e396c917cb3549a82"
)
FVP_GATE_SCHEMA: Final = (
    ROOT / "tests/schemas/apollo-fvp-pcie-limit-producer.schema.json"
)
FVP_MANIFEST: Final = (
    ROOT / "tests/fixtures/gic720ae/pcie-its/fvp-limit/manifest.json"
)
FVP_LIMIT_RECEIPT: Final = (
    ROOT
    / ".omo/evidence/apollo-gic-its/final/F2/cycle2/integration-current"
    / "reference-limit-current.json"
)
PROFILE_SCHEMA: Final = ROOT / "tests/schemas/apollo-qbox-pcie-irq-profile.schema.json"
INPUT_SCHEMA: Final = ROOT / "tests/schemas/apollo-qbox-pcie-irq-input.schema.json"
AP_COMPUTE: Final = (
    ROOT / "hsoc-stack/tools/qbox-platform/platforms/apollo/hw-block/ap_compute.lua"
)
OVERLAY: Final = (
    ROOT
    / "hsoc-stack/tools/qbox-platform/platforms/apollo/test-profile"
    / "apollo-qvp-pcie-irq-overlay.dtso"
)
GUEST_PROBE: Final = ROOT / "scripts/test/apollo_pcie_its_guest.sh"
SHARED_VALIDATOR: Final = ROOT / "scripts/test/validate_apollo_pcie_its_runtime.py"
GUEST_WRAPPER: Final = (
    ROOT
    / "hsoc-stack/tools/qbox-platform/platforms/apollo/test-profile"
    / "apollo-qvp-pcie-irq-test.sh"
)

type JsonValue = (
    str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
)
type JsonObject = dict[str, JsonValue]
Mode = Literal["msix", "intx"]
Artifact = JsonObject


class ProfileError(RuntimeError):
    reason: str

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


def canonical_bytes(payload: JsonObject) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def has_symlink(path: Path) -> bool:
    current = path.absolute()
    while current != current.parent:
        if current.is_symlink():
            return True
        current = current.parent
    return False


def contained(path: Path, parent: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def require_file(path: Path, reason: str, *, parent: Path = ROOT) -> Path:
    absolute = path.absolute()
    if (
        not absolute.is_file()
        or absolute != absolute.resolve()
        or has_symlink(absolute)
        or not contained(absolute, parent)
    ):
        raise ProfileError(reason)
    return absolute


def load_object(path: Path, reason: str) -> JsonObject:
    try:
        value: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProfileError(reason) from error
    if not isinstance(value, dict):
        raise ProfileError(reason)
    return value


def object_field(value: JsonValue, reason: str) -> JsonObject:
    if not isinstance(value, dict):
        raise ProfileError(reason)
    return value


def string_field(value: JsonValue, reason: str) -> str:
    if not isinstance(value, str):
        raise ProfileError(reason)
    return value


def artifact(path: Path, exposed_path: Path | None = None) -> Artifact:
    return {
        "path": str((exposed_path or path).absolute()),
        "size": path.stat().st_size,
        "sha256": sha256(path),
    }


def verified_artifact_path(entry_value: JsonValue, parent: Path, reason: str) -> Path:
    entry = object_field(entry_value, reason)
    path = require_file(Path(string_field(entry.get("path"), reason)), reason)
    if not contained(path, parent):
        raise ProfileError(reason)
    if entry.get("size") != path.stat().st_size or entry.get("sha256") != sha256(path):
        raise ProfileError(reason)
    return path


def contract() -> JsonObject:
    return {
        "bdf": "0000:00:01.0",
        "requester_id": 0x0008,
        "device_id": 0x0008,
        "stream_id": 0x0040,
        "event_id_base": 0,
        "its_translator": "0x20850040",
        "legacy_gpex_spi_input": 301,
        "legacy_gic_intid": 333,
        "virtio_mmio_hwirq": 293,
        "collection_entry_size": 2,
    }


def verify_reference_gate(path: Path) -> JsonObject:
    gate = require_file(path, "fvp_reference_gate_path")
    if gate != CANONICAL_FVP_GATE or sha256(gate) != CANONICAL_FVP_GATE_SHA256:
        raise ProfileError("fvp_reference_gate_path")
    payload = load_object(gate, "fvp_reference_gate_json")
    schema = load_object(FVP_GATE_SCHEMA, "fvp_reference_gate_schema")
    try:
        jsonschema.Draft202012Validator(schema).validate(payload)
    except jsonschema.ValidationError as error:
        raise ProfileError("fvp_reference_gate_schema") from error
    if (
        payload.get("reference_gate") != "PASS"
        or payload.get("fvp_qualification") != "UNSUPPORTED"
        or payload.get("qbox_allowed") is not True
        or payload.get("reason") != "immutable_ecam_limit"
        or payload.get("configuration_applied") is not True
        or payload.get("qbox_started") is not False
    ):
        raise ProfileError("fvp_reference_gate_fields")
    hashes = object_field(payload.get("hashes"), "fvp_reference_gate_hashes")
    manifest = load_object(FVP_MANIFEST, "fvp_manifest")
    inputs = object_field(manifest.get("inputs"), "fvp_manifest")
    runtime = object_field(inputs.get("runtime_result"), "fvp_manifest")
    runtime_path = FVP_MANIFEST.parent / string_field(
        runtime.get("path"), "fvp_manifest"
    )
    expected = {
        "manifest_sha256": sha256(require_file(FVP_MANIFEST, "fvp_manifest")),
        "limit_receipt_sha256": hashlib.sha256(
            json.dumps(
                load_object(
                    require_file(FVP_LIMIT_RECEIPT, "fvp_limit_receipt"),
                    "fvp_limit_receipt",
                ),
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest(),
        "raw_result_sha256": sha256(require_file(runtime_path, "fvp_runtime")),
    }
    if hashes != expected:
        raise ProfileError("fvp_reference_gate_hashes")
    return payload


def validate_platform_contract(ap_compute: Path, overlay: Path) -> None:
    lua = require_file(
        ap_compute, "platform_source", parent=ap_compute.absolute().parent
    ).read_text(encoding="utf-8")
    dts = require_file(
        overlay, "overlay_source", parent=overlay.absolute().parent
    ).read_text(encoding="utf-8")
    if lua.count("gic_its_cte_size = 2;") != 1 or "gic_its_cte_size = 8;" in lua:
        raise ProfileError("collection_entry_size")
    if lua.count('addr = "01.0";') != 1:
        raise ProfileError("endpoint_bdf")
    required = (
        "msi-map = <0x8 &pcie_irq_its 0x8 0x1>;",
        "iommu-map = <0x8 &pcie_irq_smmu 0x40 0x1>;",
        "0x0 0x0 0x0 0x12d 0x4",
    )
    if any(token not in dts for token in required):
        raise ProfileError("overlay_contract")


def mode_input_payload(
    mode: Mode,
    inputs: dict[str, Artifact],
    gate_sha256: str,
    command_line_sha256: str,
    command: list[str],
) -> JsonObject:
    match mode:
        case "msix":
            required: list[JsonValue] = []
            forbidden: list[JsonValue] = ["pci=nomsi"]
        case "intx":
            required = ["pci=nomsi"]
            forbidden = []
        case _ as unreachable:
            assert_never(unreachable)
    input_payload: JsonObject = {}
    for name, item in inputs.items():
        input_payload[name] = item
    boot: JsonObject = {
        "command_line_sha256": command_line_sha256,
        "required_arguments": required,
        "forbidden_arguments": forbidden,
    }
    command_values: list[JsonValue] = [value for value in command]
    command_payload: JsonObject = {
        "argv": command_values,
        "profile_mode": mode,
    }
    return {
        "schema_version": 1,
        "profile": "apollo-qvp-pcie-irq",
        "platform": "qbox",
        "mode": mode,
        "fvp_reference_gate_sha256": gate_sha256,
        "contract": contract(),
        "inputs": input_payload,
        "boot": boot,
        "command": command_payload,
    }
