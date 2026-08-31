from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import time
from typing import Final

from fvp_apollo_pcie_its_output import OutputDirectory
from fvp_apollo_pcie_its_types import (
    DtContract,
    FvpResult,
    JsonObject,
    JsonValue,
    ProcessObservation,
    RunError,
)


PROFILE_NAME: Final = "profile.json"
FVP_EXECUTABLE: Final = "FVP_Zena_CSS_Cfg2"
EXPECTED_PARAMETERS: Final = {
    "css.gic_distributor.ITS-count": "1",
    "pcie_group_0.pcie4.hierarchy_file_name": "<default>",
    "pcie_group_0.pcie4.pcie_rc.ahci0.endpoint.ats_supported": "true",
}


@dataclass(frozen=True, slots=True)
class VerifiedProfile:
    root: Path
    profile_path: Path
    profile_sha256: str
    profile: JsonObject
    fvpconf: Path
    model_declared: Path
    dt_contract: DtContract


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_object(value: JsonValue, reason: str) -> JsonObject:
    if not isinstance(value, dict):
        raise RunError(reason)
    return value


def require_string(record: JsonObject, field: str, reason: str) -> str:
    value = record.get(field)
    if not isinstance(value, str):
        raise RunError(reason, field)
    return value


def load_json(path: Path) -> JsonObject:
    try:
        value: JsonValue = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RunError("profile_malformed", str(path)) from error
    return require_object(value, "profile_malformed")


def require_record(value: JsonValue, role: str) -> Path:
    record = require_object(value, "profile_record_missing")
    path = Path(require_string(record, "path", "profile_record_missing"))
    expected = require_string(record, "sha256", "profile_record_missing")
    if not path.is_file():
        raise RunError("profile_input_missing", role)
    if sha256_file(path) != expected:
        raise RunError("artifact_hash_stale", role)
    return path.resolve()


def verify_profile(
    profile_dir: Path, expected_profile_sha: str | None
) -> VerifiedProfile:
    root = profile_dir.resolve()
    profile_path = root / PROFILE_NAME
    if not profile_path.is_file():
        raise RunError("profile_missing", str(profile_path))
    profile_sha256 = sha256_file(profile_path)
    if expected_profile_sha is not None and profile_sha256 != expected_profile_sha:
        raise RunError("profile_hash_stale", profile_sha256)
    profile = load_json(profile_path)
    if profile.get("verdict") != "PASS" or profile.get("format_version") != 1:
        raise RunError("profile_not_launchable")
    artifacts = profile.get("artifacts")
    sources = profile.get("source_hashes")
    if not isinstance(artifacts, list) or not isinstance(sources, list):
        raise RunError("profile_records_missing")
    for record in artifacts:
        record_object = require_object(record, "profile_records_missing")
        role = record_object.get("role")
        require_record(record_object, role if isinstance(role, str) else "artifact")
    for record in sources:
        record_object = require_object(record, "profile_records_missing")
        role = record_object.get("role")
        require_record(record_object, role if isinstance(role, str) else "source")
    configuration = require_object(
        profile.get("configuration"), "model_configuration_missing"
    )
    if configuration.get("configuration_declared") is not True:
        raise RunError("model_configuration_missing")
    fvpconf = require_record(configuration.get("final_fvpconf"), "final_fvpconf")
    declared = require_record(
        configuration.get("baseline_contract"), "model_declared"
    )
    parameters = require_object(
        load_json(fvpconf).get("parameters"), "fvpconf_malformed"
    )
    for key, value in EXPECTED_PARAMETERS.items():
        if parameters.get(key) != value:
            raise RunError("model_configuration_missing", key)
    disk = require_string(
        parameters,
        "pcie_group_0.pcie4.pcie_rc.ahci0.ahci.image_path",
        "empty_disk",
    )
    disk_path = Path(disk)
    if not disk_path.is_file() or disk_path.stat().st_size == 0:
        raise RunError("empty_disk")
    declared_payload = load_json(declared)
    model = require_object(declared_payload.get("model"), "model_configuration_missing")
    declared_config = require_object(
        declared_payload.get("configuration"), "model_configuration_missing"
    )
    if model.get("model_present") is not True:
        raise RunError("model_configuration_missing", "model_present")
    if declared_config.get("configuration_declared") is not True:
        raise RunError("model_configuration_missing", "declared")
    delivery = require_object(profile.get("dt_delivery"), "dt_contract_missing")
    firmware = require_object(
        delivery.get("firmware_fip_hw_config"), "dt_contract_missing"
    )
    contract = require_object(firmware.get("host_contract"), "dt_contract_missing")
    values = {
        key: require_string(contract, key, "dt_contract_missing")
        for key in ("node", "ecam_base", "its_base", "smmu_base")
    }
    return VerifiedProfile(
        root=root,
        profile_path=profile_path,
        profile_sha256=profile_sha256,
        profile=profile,
        fvpconf=fvpconf,
        model_declared=declared,
        dt_contract=DtContract(**values),
    )


def atomic_write(output: OutputDirectory, payload: JsonObject | FvpResult) -> None:
    output.write_json(payload)


def failure_result(
    reason: str,
    profile_sha256: str,
    output: OutputDirectory,
    detail: JsonObject | None = None,
    configuration_applied_value: bool = False,
) -> FvpResult:
    payload: FvpResult = {
        "schema_version": 1,
        "status": "fail",
        "reason": reason,
        "profile_sha256": profile_sha256,
        "configuration_applied": configuration_applied_value,
        "qbox_started": False,
    }
    if detail is not None:
        payload["detail"] = detail
    atomic_write(output, payload)
    return payload


def process_snapshot(root_pid: int) -> list[ProcessObservation]:
    rows: dict[int, tuple[int, list[str]]] = {}
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            stat = (proc / "stat").read_text(encoding="utf-8").split()
            argv = [
                part.decode("utf-8", errors="replace")
                for part in (proc / "cmdline").read_bytes().split(b"\0")
                if part
            ]
            if len(stat) >= 4 and argv:
                rows[int(proc.name)] = (int(stat[3]), argv)
        except (OSError, ValueError):
            continue
    descendants = {root_pid}
    changed = True
    while changed:
        changed = False
        for pid, (parent, _) in rows.items():
            if parent in descendants and pid not in descendants:
                descendants.add(pid)
                changed = True
    selected: list[ProcessObservation] = []
    for pid in sorted(descendants):
        parent, argv = rows.get(pid, (0, []))
        if any(FVP_EXECUTABLE in value for value in argv):
            selected.append(
                {
                    "pid": pid,
                    "ppid": parent,
                    "argv": argv,
                    "observed_at_unix": time.time(),
                }
            )
    return selected


def configuration_applied(
    verified: VerifiedProfile,
    observed_processes: list[ProcessObservation],
    model_output: str,
) -> bool:
    parameters = require_object(
        load_json(verified.fvpconf).get("parameters"), "fvpconf_malformed"
    )
    expected_disk = require_string(
        parameters,
        "pcie_group_0.pcie4.pcie_rc.ahci0.ahci.image_path",
        "fvpconf_malformed",
    )
    required = [f"{key}={value}" for key, value in EXPECTED_PARAMETERS.items()]
    required.append(f"pcie_group_0.pcie4.pcie_rc.ahci0.ahci.image_path={expected_disk}")
    for process in observed_processes:
        joined = "\n".join(process["argv"])
        if all(value in joined for value in required) and "--parameter" in joined:
            return True
    return False
