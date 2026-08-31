from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
from typing import Final

from .contract import (
    HashRecord,
    JsonObject,
    JsonValue,
    ProfileError,
    ProfileLayout,
    referenced_config_paths,
    sha256_file,
)
from .provenance import (
    BITBAKE_BUILD_INPUT_ROLES,
    RUNTIME_INPUT_ROLES,
    TOOL_POSTPROCESSOR_ROLES,
    authorize_path_containment_refresh,
    validate_artifact_records,
    validate_launchable_source_closure,
    validate_task_sigdata_records,
)


SAFE_ENVIRONMENT_VARIABLES = (
    "APOLLO_KERNEL_CONFIG_FRAGMENT",
    "DEPLOY_DIR",
    "DEPLOY_DIR_IMAGE",
    "MACHINE",
    "SSTATE_DIR",
    "TMPDIR",
)
MINIMUM_OUTPUT_FREE_BYTES: Final = 48 * 1024**3


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--machine", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=14400)
    parser.add_argument("--resume-postprocess", action="store_true")
    parser.add_argument(
        "--refresh-provenance-after-path-remediation",
        action="store_true",
    )
    return parser.parse_args(argv)


def validate_output_capacity(free_bytes: int) -> None:
    if free_bytes < MINIMUM_OUTPUT_FREE_BYTES:
        raise ProfileError("insufficient_output_capacity", str(free_bytes))


def preflight_output_capacity(output_root: Path) -> JsonObject:
    probe = output_root.absolute()
    while not probe.exists():
        probe = probe.parent
    free_bytes = shutil.disk_usage(probe).free
    validate_output_capacity(free_bytes)
    return {
        "required_free_bytes": MINIMUM_OUTPUT_FREE_BYTES,
        "observed_free_bytes": free_bytes,
        "probe_path": str(probe.resolve()),
    }


def safe_log_output(log_name: str, output: str) -> str:
    if not log_name.endswith("-environment.log"):
        return output
    prefixes = tuple(f'{name}="' for name in SAFE_ENVIRONMENT_VARIABLES)
    lines = [line for line in output.splitlines() if line.startswith(prefixes)]
    return "sanitized_environment=true\n" + "\n".join(lines) + "\n"


def environment_value(output: str, name: str) -> str:
    prefix = f'{name}="'
    values = [
        line[len(prefix):-1]
        for line in output.splitlines()
        if line.startswith(prefix) and line.endswith('"')
    ]
    if not values:
        raise ProfileError("bitbake_variable_missing", name)
    return values[-1]


def write_default_contract_override(layout: ProfileLayout) -> Path:
    path = layout.root / "conf/default-kernel-contract.inc"
    root = layout.root / "default-kernel-contract"
    lines = (
        f'TMPDIR = "{root / "tmp"}"',
        f'DEPLOY_DIR = "{root / "deploy"}"',
        f'DEPLOY_DIR_IMAGE = "{root / "deploy/images/apollo-fvp"}"',
        f'SSTATE_DIR = "{layout.sstate}"',
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def validate_declared_contract(receipt: JsonObject) -> None:
    configuration = receipt.get("configuration")
    if not isinstance(configuration, dict):
        raise ProfileError("model_declared_contract_missing")
    if configuration.get("configuration_declared") is not True:
        raise ProfileError("model_declared_contract_missing")
    if "configuration_applied" in configuration:
        raise ProfileError("model_contract_boundary_violation")


def referenced_file_records(config: JsonObject) -> list[Path]:
    files = [path for path in referenced_config_paths(config) if path.is_file()]
    bindir = config.get("fvp-bindir")
    executable = config.get("exe")
    if isinstance(bindir, str) and isinstance(executable, str):
        files.append(Path(bindir) / executable)
    return list(dict.fromkeys(path.resolve(strict=True) for path in files))


def parse_hash_record(value: JsonValue | None, field: str) -> HashRecord:
    if not isinstance(value, dict):
        raise ProfileError("prior_receipt_invalid", field)
    role = value.get("role")
    path = value.get("path")
    digest = value.get("sha256")
    if not isinstance(role, str) or not isinstance(path, str) or not isinstance(digest, str):
        raise ProfileError("prior_receipt_invalid", field)
    return {"role": role, "path": path, "sha256": digest}


def parse_hash_records(value: JsonValue | None, field: str) -> list[HashRecord]:
    if not isinstance(value, list):
        raise ProfileError("prior_receipt_invalid", field)
    return [parse_hash_record(item, field) for item in value]


def prior_task_provenance(value: JsonValue | None) -> tuple[list[JsonObject], list[HashRecord]]:
    if not isinstance(value, list):
        raise ProfileError("prior_receipt_invalid", "task_provenance")
    items: list[JsonObject] = []
    records: list[HashRecord] = []
    for item in value:
        if not isinstance(item, dict):
            raise ProfileError("prior_receipt_invalid", "task_provenance")
        taskhash = item.get("taskhash")
        record = parse_hash_record(item.get("sigdata"), "task_provenance")
        if not isinstance(taskhash, str) or not Path(record["path"]).name.endswith(taskhash):
            raise ProfileError("stale_task_sigdata")
        records.append(record)
        items.append(item)
    validate_task_sigdata_records(records)
    return items, records


def validate_prior_configuration(value: JsonValue | None) -> None:
    if not isinstance(value, dict):
        raise ProfileError("prior_receipt_invalid", "configuration")
    fields = (
        "baseline_contract",
        "baseline_fvpconf",
        "final_fvpconf",
        "kernel_fragment",
        "kernel_config",
        "bitbake_override",
    )
    validate_artifact_records([
        parse_hash_record(value.get(field), field) for field in fields
    ])


def validate_prior_receipt(
    prior: JsonObject | None,
    layout: ProfileLayout,
    refresh_reason: str | None,
) -> tuple[JsonObject | None, list[HashRecord], list[JsonObject]]:
    if prior is None or prior.get("verdict") != "PASS":
        return None, [], []
    if prior.get("output_root") != str(layout.root):
        raise ProfileError("prior_receipt_invalid", "output_root")
    sources = parse_hash_records(prior.get("source_hashes"), "source_hashes")
    artifacts = parse_hash_records(prior.get("artifacts"), "artifacts")
    validate_artifact_records(artifacts)
    validate_prior_configuration(prior.get("configuration"))
    task_items, _ = prior_task_provenance(prior.get("task_provenance"))
    image_log = layout.logs / "image-build.log"
    if not image_log.is_file() or "all succeeded" not in image_log.read_text(encoding="utf-8"):
        raise ProfileError("image_build_receipt_failed")
    prior_sha256 = sha256_file(layout.root / "profile.json")
    if refresh_reason is None:
        validate_launchable_source_closure(sources)
        return None, artifacts, task_items
    if refresh_reason != "path_containment_remediation":
        raise ProfileError("unauthorized_refresh_reason", refresh_reason)
    deltas = authorize_path_containment_refresh(sources)
    delta_json: list[JsonValue] = [item for item in deltas]
    refresh: JsonObject = {
        "reason": refresh_reason,
        "prior_receipt_sha256": prior_sha256,
        "source_deltas": delta_json,
        "tool_sources_checked": len(TOOL_POSTPROCESSOR_ROLES),
        "bitbake_build_inputs_checked": len(BITBAKE_BUILD_INPUT_ROLES),
        "runtime_inputs_checked": len(RUNTIME_INPUT_ROLES),
        "artifacts_checked": len(artifacts),
        "task_sigdata_checked": len(task_items),
    }
    return refresh, artifacts, task_items


def receipt_paths(layout: ProfileLayout, workspace: Path) -> tuple[Path, Path]:
    checked = ProfileLayout.create(layout.root, workspace)
    if checked.root != layout.root:
        raise ProfileError("output_root_changed", str(layout.root))
    layout.root.mkdir(parents=True, exist_ok=True)
    checked = ProfileLayout.create(layout.root, workspace)
    if checked.root != layout.root:
        raise ProfileError("output_root_changed", str(layout.root))
    output = layout.root / "profile.json"
    temporary = layout.root / f".profile.json.{os.getpid()}.tmp"
    for path in (output, temporary):
        if path.is_symlink():
            raise ProfileError("receipt_path_symlink_forbidden", str(path))
        if path.resolve(strict=False).parent != layout.root:
            raise ProfileError("receipt_path_escape", str(path))
    return output, temporary


def remove_receipt_temporary(directory_fd: int, name: str) -> None:
    try:
        os.unlink(name, dir_fd=directory_fd)
    except FileNotFoundError:
        return


def write_receipt_atomic(
    layout: ProfileLayout,
    workspace: Path,
    receipt: JsonObject,
) -> Path:
    output, temporary = receipt_paths(layout, workspace)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    directory_fd: int | None = None
    try:
        directory_fd = os.open(
            layout.root,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
        )
        descriptor = os.open(temporary.name, flags, 0o664, dir_fd=directory_fd)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        checked_output, checked_temporary = receipt_paths(layout, workspace)
        if checked_output != output or checked_temporary != temporary:
            raise ProfileError("output_root_changed", str(layout.root))
        if temporary.resolve(strict=True).parent != layout.root:
            raise ProfileError("receipt_path_escape", str(temporary))
        os.replace(
            temporary.name,
            output.name,
            src_dir_fd=directory_fd,
            dst_dir_fd=directory_fd,
        )
    except OSError as error:
        raise ProfileError("receipt_write_failed", str(output)) from error
    finally:
        if directory_fd is not None:
            remove_receipt_temporary(directory_fd, temporary.name)
            os.close(directory_fd)
    return output
