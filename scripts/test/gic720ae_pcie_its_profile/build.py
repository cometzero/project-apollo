from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
from typing import Final

from .contract import (
    AHCI_IMAGE_KEY,
    HashRecord,
    JsonObject,
    JsonValue,
    ProfileError,
    ProfileLayout,
    hash_record,
    hash_record_json,
    load_json,
    sha256_file,
    string_parameters,
)
from .workflow import safe_log_output


MARKER_TEXT: Final = "APOLLO_GIC_ITS_AHCI_PROFILE_V1\n"


@dataclass(frozen=True, slots=True)
class BuildContext:
    workspace: Path
    layout: ProfileLayout
    environment: dict[str, str]
    timeout: int


def oe_environment(workspace: Path) -> dict[str, str]:
    result = subprocess.run(
        ["bash", "-c", "source layers/poky/oe-init-build-env build >/dev/null && env -0"],
        cwd=workspace,
        check=False,
        capture_output=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise ProfileError("bitbake_environment_failed")
    environment = {
        key.decode(): value.decode()
        for item in result.stdout.split(b"\0")
        if item
        for key, value in [item.split(b"=", 1)]
    }
    environment["MACHINE"] = "apollo-fvp"
    return environment


def run(context: BuildContext, argv: list[str], log_name: str) -> str:
    try:
        result = subprocess.run(
            argv,
            cwd=context.workspace,
            env=context.environment,
            check=False,
            capture_output=True,
            text=True,
            timeout=context.timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise ProfileError("build_command_timeout", log_name) from error
    log = context.layout.logs / log_name
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(
        safe_log_output(log_name, result.stdout + result.stderr),
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise ProfileError("build_command_failed", f"{log_name}:{result.returncode}")
    return result.stdout


def write_override(layout: ProfileLayout, workspace: Path) -> Path:
    include = layout.root / "conf/gic720ae-pcie-its.inc"
    default_sstate = (workspace / "build/sstate-cache").resolve()
    lines = (
        f'TMPDIR = "{layout.tmp}"',
        f'DEPLOY_DIR = "{layout.deploy}"',
        f'DEPLOY_DIR_IMAGE = "{layout.deploy_image}"',
        f'SSTATE_DIR = "{layout.sstate}"',
        'APOLLO_KERNEL_CONFIG_FRAGMENT = "gic720ae-pcie-its.cfg"',
        f'SSTATE_MIRRORS = "file://.* file://{default_sstate}/PATH;downloadfilename=PATH"',
        'BB_NUMBER_THREADS = "6"',
        'PARALLEL_MAKE = "-j6"',
    )
    include.parent.mkdir(parents=True, exist_ok=True)
    include.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return include


def deploy_manifest(root: Path) -> list[JsonObject]:
    if not root.exists():
        return []
    entries: list[JsonObject] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() and not path.is_symlink():
            continue
        record: JsonObject = {
            "path": path.relative_to(root).as_posix(),
            "kind": "symlink" if path.is_symlink() else "regular",
            "mode": stat.S_IMODE(path.resolve().stat().st_mode),
            "sha256": sha256_file(path.resolve()),
        }
        if path.is_symlink():
            record["link_text"] = os.readlink(path)
        entries.append(record)
    return entries


def write_json(
    path: Path,
    payload: JsonValue | list[JsonObject] | list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def create_scratch_disk(context: BuildContext) -> Path:
    disk = context.layout.artifacts / "storage/apollo-gic-its-ahci.raw"
    marker = context.layout.root / "scratch/marker/APOLLO_GIC_ITS_PROFILE"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(MARKER_TEXT, encoding="utf-8")
    disk.parent.mkdir(parents=True, exist_ok=True)
    with disk.open("wb") as stream:
        stream.truncate(64 * 1024 * 1024)
    command = [
        "mkfs.ext4", "-q", "-F", "-U", "00000000-0000-4000-8000-000000000720",
        "-L", "APOLLO_ITS", "-E", "lazy_itable_init=0,lazy_journal_init=0",
        "-d", str(marker.parent), str(disk),
    ]
    environment = dict(context.environment)
    environment["E2FSPROGS_FAKE_TIME"] = "946684800"
    disk_context = BuildContext(
        workspace=context.workspace,
        layout=context.layout,
        environment=environment,
        timeout=context.timeout,
    )
    run(disk_context, command, "mkfs-ahci.log")
    output = run(
        context,
        ["debugfs", "-R", "cat /APOLLO_GIC_ITS_PROFILE", str(disk)],
        "read-ahci-marker.log",
    )
    if output != MARKER_TEXT:
        raise ProfileError("scratch_disk_marker_mismatch")
    return disk


def one(paths: list[Path], role: str) -> Path:
    existing = [path for path in paths if path.is_file()]
    if len(existing) != 1:
        raise ProfileError("isolated_output_missing", role)
    return existing[0]


def copy_file(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source.resolve(strict=True), destination)
    return destination


def boot_artifacts(layout: ProfileLayout) -> dict[str, Path]:
    source = layout.deploy_image
    destination = layout.artifacts / "boot"
    mapping = {
        "kernel": (source / "Image", destination / "Image"),
        "dtb": (source / "apollo-fvp.dtb", destination / "apollo-fvp.dtb"),
        "initramfs": (
            source / "nexios-bsp-initramfs-apollo-fvp.cpio.gz",
            destination / "nexios-bsp-initramfs-apollo-fvp.cpio.gz",
        ),
        "wic": (
            source / "nexios-bsp-initramfs-apollo-fvp.wic",
            destination / "nexios-bsp-initramfs-apollo-fvp.wic",
        ),
    }
    return {role: copy_file(paths[0], paths[1]) for role, paths in mapping.items()}


def copy_config_inputs(
    source_config: Path,
    artifacts: dict[str, Path],
    scratch_disk: Path,
    layout: ProfileLayout,
) -> tuple[Path, JsonObject]:
    config = load_json(source_config)
    parameters = string_parameters(config)
    copied: dict[Path, Path] = {
        (layout.deploy_image / "nexios-bsp-initramfs-apollo-fvp.wic").resolve(): artifacts["wic"],
    }
    runtime = layout.artifacts / "runtime-inputs"
    for key, value in parameters.items():
        path = Path(value)
        if not path.is_absolute() or not path.is_file():
            continue
        source = path.resolve()
        destination = copied.get(source)
        if destination is None:
            destination = copy_file(source, runtime / source.name)
            copied[source] = destination
        parameters[key] = str(destination.resolve())
    parameters[AHCI_IMAGE_KEY] = str(scratch_disk.resolve())
    config["parameters"] = {key: value for key, value in parameters.items()}
    data = config.get("data", [])
    if not isinstance(data, list):
        raise ProfileError("fvp_config_invalid", "data")
    rewritten_data: list[JsonValue] = []
    for raw in data:
        if not isinstance(raw, str) or "=" not in raw:
            raise ProfileError("fvp_config_invalid", "data")
        key, value = raw.split("=", 1)
        path_text, separator, address = value.partition("@")
        source = Path(path_text).resolve(strict=True)
        destination = copied.get(source)
        if destination is None:
            destination = copy_file(source, runtime / source.name)
            copied[source] = destination
        rewritten_data.append(f"{key}={destination.resolve()}{separator}{address}")
    config["data"] = rewritten_data
    output = layout.artifacts / "apollo-fvp-pcie-its.fvpconf"
    write_json(output, config)
    return output, config


def extract_uki_dtbs(context: BuildContext, wic: Path) -> list[Path]:
    output: list[Path] = []
    verification = context.layout.artifacts / "verification"
    for slot in ("a", "b"):
        uki = verification / f"{slot}.efi"
        dtb = verification / f"{slot}.dtb"
        uki.parent.mkdir(parents=True, exist_ok=True)
        run(
            context,
            [
                "mcopy", "-o", "-i", f"{wic}@@1048576",
                f"::/EFI/Linux/{slot}-slot/auto-ad-nexios-{slot}.efi", str(uki),
            ],
            f"extract-uki-{slot}.log",
        )
        run(
            context,
            ["llvm-objcopy", "--dump-section", f".dtb={dtb}", str(uki)],
            f"extract-dtb-{slot}.log",
        )
        output.append(dtb)
    return output


def task_provenance(layout: ProfileLayout, recipe: str, task: str) -> JsonObject:
    candidates = list(layout.tmp.glob(f"stamps/*/{recipe}/*.{task}.sigdata.*"))
    if not candidates:
        raise ProfileError("task_provenance_missing", f"{recipe}:{task}")
    path = max(candidates, key=lambda candidate: candidate.stat().st_mtime_ns)
    return {
        "recipe": recipe,
        "task": task,
        "taskhash": path.name.rsplit(".", 1)[-1],
        "sigdata": hash_record_json(hash_record(f"{recipe}:{task}:sigdata", path)),
    }


def find_kernel_config(layout: ProfileLayout) -> Path:
    candidates = list(layout.tmp.glob("work/*/linux-yocto-rt/*/build/.config"))
    return one(candidates, "kernel_config")


def artifact_records(artifacts: dict[str, Path], extra: list[Path]) -> list[HashRecord]:
    records = [hash_record(role, path) for role, path in sorted(artifacts.items())]
    records.extend(hash_record(path.name, path) for path in extra)
    return records
