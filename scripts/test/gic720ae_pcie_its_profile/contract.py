from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Final, TypedDict

import jsonschema


type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]

PCIE_NODE: Final = "/soc/pcie@10040000000"
AHCI_IMAGE_KEY: Final = "pcie_group_0.pcie4.pcie_rc.ahci0.ahci.image_path"
EXPECTED_CELLS: Final = {
    "reg": (0x100, 0x40000000, 0, 0x10000000),
    "ranges": (
        0x02000000, 0, 0x60000000, 0, 0x60000000, 0, 0x20000000,
        0x43000000, 0x101, 0x60000000, 0x101, 0x60000000, 0, 0x20000000,
    ),
    "bus-range": (0, 0xFF),
    "linux,pci-domain": (4,),
}


class HashRecord(TypedDict):
    role: str
    path: str
    sha256: str


@dataclass(frozen=True, slots=True)
class ProfileError(Exception):
    reason: str
    detail: str = ""

    def __str__(self) -> str:
        return f"{self.reason}: {self.detail}"


@dataclass(frozen=True, slots=True)
class ProfileLayout:
    root: Path
    tmp: Path
    deploy: Path
    deploy_image: Path
    sstate: Path
    logs: Path
    artifacts: Path

    @classmethod
    def create(cls, output_root: Path, workspace: Path) -> ProfileLayout:
        root = Path(os.path.abspath(output_root))
        resolved_root = root.resolve(strict=False)
        active_tmp = (workspace / "build/tmp_baremetal").resolve()
        active_deploy = (active_tmp / "deploy").resolve()
        if resolved_root != root:
            raise ProfileError("output_root_symlink_forbidden", str(root))
        for candidate in (root, resolved_root):
            if candidate == active_tmp or candidate == active_deploy:
                raise ProfileError("active_default_path_forbidden", str(root))
            if candidate.is_relative_to(active_tmp) or active_tmp.is_relative_to(candidate):
                raise ProfileError("active_default_path_forbidden", str(root))
        if root.exists() and not root.is_dir():
            raise ProfileError("invalid_output_root", str(root))
        deploy = root / "deploy/bitbake"
        return cls(
            root=root,
            tmp=root / "tmp",
            deploy=deploy,
            deploy_image=deploy / "images/apollo-fvp",
            sstate=root / "sstate-cache",
            logs=root / "logs",
            artifacts=root / "artifacts",
        )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_record(role: str, path: Path) -> HashRecord:
    resolved = path.resolve(strict=True)
    if not resolved.is_file():
        raise ProfileError("hash_input_missing", str(path))
    return {"role": role, "path": str(resolved), "sha256": sha256_file(resolved)}


def hash_record_json(record: HashRecord) -> JsonObject:
    return {
        "role": record["role"],
        "path": record["path"],
        "sha256": record["sha256"],
    }


def validate_hash_record(record: HashRecord) -> None:
    path = Path(record["path"])
    if not path.is_file() or sha256_file(path) != record["sha256"]:
        raise ProfileError("stale_hash", record["role"])


def validate_scratch_disk(path: Path) -> None:
    if not path.is_file():
        raise ProfileError("scratch_disk_missing", str(path))
    if path.stat().st_size == 0:
        raise ProfileError("scratch_disk_empty", str(path))


def validate_kernel_config(path: Path) -> None:
    try:
        values = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as error:
        raise ProfileError("kernel_config_missing", str(path)) from error
    if "CONFIG_GENERIC_IRQ_DEBUGFS=y" not in values:
        raise ProfileError("irq_debugfs_missing", str(path))


def fdt_cells(dtb: Path, node: str, prop: str) -> tuple[int, ...]:
    result = subprocess.run(
        ["fdtget", "-t", "x", str(dtb), node, prop],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        reason = "pcie_host_missing" if node == PCIE_NODE else "pcie_host_mismatch"
        raise ProfileError(reason, f"{node}:{prop}")
    return tuple(int(value, 16) for value in result.stdout.split())


def fdt_string(dtb: Path, node: str, prop: str) -> str:
    result = subprocess.run(
        ["fdtget", "-t", "s", str(dtb), node, prop],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ProfileError("pcie_host_missing", f"{node}:{prop}")
    return result.stdout.strip()


def validate_dtb_contract(dtb: Path) -> JsonObject:
    if fdt_string(dtb, PCIE_NODE, "compatible") != "pci-host-ecam-generic":
        raise ProfileError("pcie_host_mismatch", "compatible")
    actual = {prop: fdt_cells(dtb, PCIE_NODE, prop) for prop in EXPECTED_CELLS}
    if actual != EXPECTED_CELLS:
        raise ProfileError("pcie_host_mismatch", "address contract")
    properties = subprocess.run(
        ["fdtget", "-p", str(dtb), PCIE_NODE],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split()
    if not {"dma-coherent", "ats-supported"}.issubset(properties):
        raise ProfileError("pcie_host_mismatch", "capabilities")
    msi_map = fdt_cells(dtb, PCIE_NODE, "msi-map")
    iommu_map = fdt_cells(dtb, PCIE_NODE, "iommu-map")
    its = fdt_cells(dtb, "/soc/interrupt-controller@20800000/msi-controller@20840000", "phandle")
    smmu = fdt_cells(dtb, "/soc/iommu@1c0000000", "phandle")
    if msi_map != (0, *its, 0, 0x10000) or iommu_map != (0, *smmu, 0, 0x10000):
        raise ProfileError("pcie_host_mismatch", "RID maps")
    return {
        "node": PCIE_NODE,
        "ecam_base": "0x10040000000",
        "its_base": "0x20840000",
        "smmu_base": "0x1c0000000",
    }


def validate_uki_dtbs(expected: Path, extracted: list[Path]) -> None:
    expected_hash = sha256_file(expected)
    if len(extracted) != 2:
        raise ProfileError("uki_dtb_missing", str(len(extracted)))
    for path in extracted:
        if sha256_file(path) != expected_hash:
            raise ProfileError("uki_dtb_mismatch", path.name)
        validate_dtb_contract(path)


def string_parameters(config: JsonObject) -> dict[str, str]:
    raw = config.get("parameters")
    if not isinstance(raw, dict):
        raise ProfileError("fvp_parameters_missing")
    parameters: dict[str, str] = {}
    for key, value in raw.items():
        if not isinstance(value, str):
            raise ProfileError("fvp_parameters_invalid", key)
        parameters[key] = value
    return parameters


def referenced_config_paths(config: JsonObject) -> list[Path]:
    paths: list[Path] = []
    bindir = config.get("fvp-bindir")
    if isinstance(bindir, str) and Path(bindir).is_absolute():
        paths.append(Path(bindir))
    for value in string_parameters(config).values():
        if Path(value).is_absolute():
            paths.append(Path(value))
    for field in ("args", "data"):
        values = config.get(field, [])
        if not isinstance(values, list):
            raise ProfileError("fvp_config_invalid", field)
        for value in values:
            if not isinstance(value, str):
                raise ProfileError("fvp_config_invalid", field)
            candidate = value.split("=", 1)[-1].split("@", 1)[0]
            if Path(candidate).is_absolute():
                paths.append(Path(candidate))
    return paths


def validate_fvp_config(config: JsonObject, profile_root: Path) -> JsonObject:
    parameters = string_parameters(config)
    checks = (
        ("pcie_group_0.pcie4.hierarchy_file_name", "<default>", "fvp_default_hierarchy_missing"),
        ("pcie_group_0.pcie4.pcie_rc.ahci0.endpoint.ats_supported", "true", "fvp_ats_disabled"),
        ("css.gic_distributor.ITS-count", "1", "fvp_its_count_mismatch"),
    )
    for key, expected, reason in checks:
        if parameters.get(key) != expected:
            raise ProfileError(reason, key)
    image = parameters.get(AHCI_IMAGE_KEY)
    if not image:
        raise ProfileError("fvp_image_path_empty", AHCI_IMAGE_KEY)
    image_path = Path(image)
    if not image_path.is_file():
        raise ProfileError("fvp_image_path_missing", image)
    root = profile_root.resolve()
    for path in referenced_config_paths(config):
        resolved = path.resolve(strict=False)
        if not resolved.is_relative_to(root):
            raise ProfileError("profile_path_escape", str(path))
        if not path.exists():
            raise ProfileError("fvp_referenced_path_missing", str(path))
    validate_scratch_disk(image_path)
    return {
        "hierarchy": "<default>",
        "ats_supported": True,
        "its_count": 1,
        "ahci_image_path": str(image_path.resolve()),
    }


def failure_receipt(reason: str, output_root: Path) -> JsonObject:
    return {
        "format_version": 1,
        "verdict": "FAIL",
        "reason": reason,
        "machine": "apollo-fvp",
        "output_root": str(output_root.absolute()),
    }


def validate_receipt(receipt: JsonObject, schema: JsonObject) -> None:
    jsonschema.Draft202012Validator(schema).validate(receipt)


def load_json(path: Path) -> JsonObject:
    try:
        value: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ProfileError("json_input_missing", str(path)) from error
    except json.JSONDecodeError as error:
        raise ProfileError("json_input_invalid", str(path)) from error
    if not isinstance(value, dict):
        raise ProfileError("json_input_invalid", str(path))
    return value
