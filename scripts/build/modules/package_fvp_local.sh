#!/usr/bin/env bash

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

package_local_flash_images()
{
    local mode="${APOLLO_LOCAL_BUILD_PACKAGE_FLASH_TEST_MODE:-}"
    local log="${APOLLO_LOCAL_BUILD_PACKAGE_FLASH_TEST_LOG:-}"
    if [[ -n "${log}" ]]; then
        mkdir -p "$(dirname "${log}")"
        printf 'package_flash_images\n' >>"${log}"
    fi
    case "${mode}" in
        record-only)
            return 0
            ;;
        fixture)
            mkdir -p "${FW_DIR}"
            local name
            for name in rse-rom-image.img rse-flash-image.img rse-otp-image.img \
                ap-flash-image.img combined_provisioning_message.bin; do
                [[ -e "${FW_DIR}/${name}" ]] ||
                    printf 'fixture-package_flash_images:%s\n' "${name}" >"${FW_DIR}/${name}"
            done
            return 0
            ;;
    esac
    package_flash_images
}

validate_local_build_write_dir()
{
    local label="$1"
    local path="$2"
    local root="${LOCAL_BUILD_DIR%/}"
    local target="${path%/}"
    local root_real
    local target_real
    local rel
    local current
    local part

    [[ "${target}" == "${root}" || "${target}" == "${root}/"* ]] ||
        die "refusing to use ${label} outside local build root: ${path}"
    root_real="$(realpath -m -- "${root}")"
    target_real="$(realpath -m -- "${target}")"
    case "${target_real}" in
        "${root_real}"|"${root_real}"/*) ;;
        *) die "refusing to use ${label} outside local build root: ${path}" ;;
    esac

    current="${root}"
    [[ ! -L "${current}" ]] ||
        die "refusing to use local build root symlink: ${current}"
    if [[ -e "${current}" && ! -d "${current}" ]]; then
        die "refusing to use non-directory local build root: ${current}"
    fi

    rel="${target#${root}/}"
    [[ "${target}" != "${root}" ]] || return 0
    IFS=/ read -r -a parts <<<"${rel}"
    for part in "${parts[@]}"; do
        current="${current}/${part}"
        [[ ! -L "${current}" ]] ||
            die "refusing to use ${label} symlink: ${current}"
        if [[ -e "${current}" && ! -d "${current}" ]]; then
            die "refusing to use non-directory ${label} path: ${current}"
        fi
    done
}

validate_local_fvp_deploy_root()
{
    validate_local_build_write_dir "deploy root" "${DEPLOY_DIR}"
    validate_local_build_write_dir "firmware dir" "${FW_DIR}"
    validate_local_build_write_dir "boot dir" "${BOOT_DIR}"
    validate_local_build_write_dir "signing dir" "${SIGN_DIR}"
}

preflight_local_fvp_package_tools()
{
    require_command python3

    case "${APOLLO_LOCAL_BUILD_PACKAGE_FLASH_TEST_MODE:-}" in
        fixture|record-only) ;;
        *)
            add_yocto_native_paths
            require_command sgdisk
            ;;
    esac

    if [[ -f "${BOOT_DIR}/Image" && -f "${BOOT_DIR}/apollo-fvp.dtb" ]]; then
        require_command sgdisk
        require_command mdir
        require_command mmd
        require_command mcopy
    fi

    case "${APOLLO_LOCAL_BUILD_PACKAGE_FLASH_TEST_MODE:-}" in
        fixture|record-only) ;;
        *) require_command fiptool ;;
    esac
}

package_local_fvp_outputs()
{
    validate_local_fvp_deploy_root
    preflight_local_fvp_package_tools
    package_local_flash_images
    export YOCTO_TMP
    python3 - "$YOCTO_DEPLOY_DIR" "$LOCAL_BUILD_DIR" "$MACHINE" \
        "$APOLLO_LOCAL_BUILD_YOCTO_VARS" <<'PY'
from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


yocto_deploy = Path(sys.argv[1])
local_build = Path(sys.argv[2])
machine = sys.argv[3]
vars_path = Path(sys.argv[4])
deploy = local_build / "deploy"
images = deploy / "images"
firmware = deploy / "firmware"
digest_cache_path = deploy / ".apollo-package-digests.json"

try:
    loaded_digest_cache = json.loads(digest_cache_path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError):
    loaded_digest_cache = {}
if not isinstance(loaded_digest_cache, dict):
    loaded_digest_cache = {}
digest_cache: dict[str, str] = {
    str(key): str(value)
    for key, value in loaded_digest_cache.items()
    if isinstance(key, str) and isinstance(value, str)
}
copied_artifact_keys: set[tuple[str, str, str]] = set()


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def ensure_not_symlink(path: Path, label: str) -> None:
    if path.is_symlink():
        fail(f"refusing to write {label}: {path}")


def ensure_existing_source(path: Path, root: Path, label: str) -> Path:
    if not path.exists():
        fail(f"missing {label}: {path}. Run ./yocto_build.sh first")
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        fail(f"{label}: {path}: {exc}")
    root_resolved = root.resolve(strict=True)
    if not (resolved == root_resolved or root_resolved in resolved.parents):
        fail(f"{label} outside YOCTO_DEPLOY_DIR: {path}")
    return resolved


def ensure_local_source(path: Path, root: Path, label: str) -> Path:
    if path.is_symlink():
        fail(f"{label} source is a symlink: {path}")
    if not path.exists():
        fail(f"missing {label}: {path}. Run ./local_build.sh --package")
    resolved = path.resolve(strict=True)
    root_resolved = root.resolve(strict=True)
    if not (resolved == root_resolved or root_resolved in resolved.parents):
        fail(f"{label} outside LOCAL_BUILD_DIR: {path}")
    return resolved


def assert_safe_parent(path: Path) -> None:
    current = path
    while current != deploy:
        if current.exists() and current.is_symlink():
            fail(f"refusing to write through symlinked parent: {current}")
        current = current.parent
    if deploy.is_symlink():
        fail(f"refusing to write deploy root: {deploy}")


def safe_write_path(path: Path) -> None:
    assert_safe_parent(path.parent)
    if path.is_symlink():
        fail(f"refusing to write symlink destination: {path}")


def safe_mkdir(path: Path) -> None:
    assert_safe_parent(path)
    path.mkdir(parents=True, exist_ok=True)


def digest_cache_key(path: Path) -> tuple[Path, str]:
    resolved = path.resolve(strict=True)
    stat = resolved.stat()
    return resolved, f"{resolved}\0{stat.st_size}\0{stat.st_mtime_ns}"


def digest(path: Path) -> str:
    resolved, key = digest_cache_key(path)
    cached = digest_cache.get(key)
    if cached is not None:
        return cached
    h = hashlib.sha256()
    with resolved.open("rb") as stream:
        for chunk in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            h.update(chunk)
    value = h.hexdigest()
    digest_cache[key] = value
    return value


artifacts: list[dict[str, object]] = []


def forget_artifact_path(dst: Path) -> None:
    dst_str = str(dst)
    artifacts[:] = [
        artifact
        for artifact in artifacts
        if artifact.get("local_path") != dst_str
    ]
    copied_artifact_keys.difference_update(
        [key for key in copied_artifact_keys if key[1] == dst_str]
    )


def append_artifact(src: Path, dst: Path, provenance: str, source_hash: str) -> None:
    artifacts.append(
        {
            "source_path": str(src),
            "local_path": str(dst),
            "component_provenance": provenance,
            "size": dst.stat().st_size,
            "sha256": source_hash,
            "source_sha256_before": source_hash,
            "source_sha256_after": source_hash,
            "source_preserved": True,
        }
    )


def copy_preserving_sparse(src: Path, dst: Path) -> None:
    try:
        subprocess.run(
            [
                "cp",
                "--reflink=auto",
                "--sparse=always",
                "--preserve=mode,timestamps",
                "--",
                str(src),
                str(dst),
            ],
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        shutil.copy2(src, dst)


def ensure_mtools_dir(image: str, dirname: str) -> None:
    existing = subprocess.run(
        ["mdir", "-i", image, dirname],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    if existing.returncode == 0:
        return
    subprocess.run(["mmd", "-i", image, dirname], check=True)


def copy_artifact(src: Path, dst: Path, provenance: str, root: Path = yocto_deploy) -> None:
    resolved_src = ensure_existing_source(src, root, "Yocto deploy source")
    safe_write_path(dst)
    safe_mkdir(dst.parent)
    artifact_key = (str(resolved_src), str(dst), provenance)
    if artifact_key in copied_artifact_keys:
        return
    same_file = dst.exists() and os.path.samefile(src, dst)
    source_hash = digest(resolved_src)
    if not same_file:
        copy_preserving_sparse(resolved_src, dst)
        if dst.stat().st_size != src.stat().st_size:
            fail(f"copied artifact size mismatch: {src} -> {dst}")
    append_artifact(src, dst, provenance, source_hash)
    copied_artifact_keys.add(artifact_key)


def record_copied_artifact(
    src: Path,
    dst: Path,
    provenance: str,
    root: Path = yocto_deploy,
) -> None:
    resolved_src = ensure_existing_source(src, root, "Yocto deploy source")
    safe_write_path(dst)
    artifact_key = (str(resolved_src), str(dst), provenance)
    if artifact_key in copied_artifact_keys:
        return
    if not dst.exists():
        fail(f"missing local artifact: {dst}")
    source_hash = digest(resolved_src)
    append_artifact(src, dst, provenance, source_hash)
    copied_artifact_keys.add(artifact_key)


def copy_local(src: Path, dst: Path, provenance: str, label: str | None = None) -> None:
    ensure_local_source(src, local_build, label or provenance)
    safe_write_path(dst)
    safe_mkdir(dst.parent)
    if not dst.exists() or src.resolve(strict=True) != dst.resolve(strict=True):
        shutil.copy2(src, dst)
    forget_artifact_path(dst)
    artifacts.append(
        {
            "source_path": str(src),
            "local_path": str(dst),
            "component_provenance": provenance,
            "size": dst.stat().st_size,
            "sha256": digest(dst),
            "source_preserved": True,
        }
    )


def safe_name(name: str, variable: str) -> str:
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or len(path.parts) != 1:
        fail(f"{variable}: unsafe file name: {name}")
    return name


def safe_kernel_release(release: str) -> str:
    if not release:
        fail("kernel.release: empty release")
    path = Path(release)
    if (
        path.is_absolute()
        or len(path.parts) != 1
        or ".." in path.parts
        or "/" in release
        or "\\" in release
        or not all(char.isalnum() or char in "._+-" for char in release)
    ):
        fail(f"unsafe kernel.release: {release}")
    return release


def latest_or_stable(stable: str, pattern: str) -> Path:
    path = yocto_deploy / stable
    if path.exists():
        ensure_existing_source(path, yocto_deploy, "Yocto deploy source")
        return path
    candidates = sorted(yocto_deploy.glob(pattern), key=lambda item: item.stat().st_mtime)
    if not candidates:
        fail(f"missing {stable}. Run ./yocto_build.sh first")
    path = candidates[-1]
    ensure_existing_source(path, yocto_deploy, "Yocto deploy source")
    return path


def local_image_path(src: Path, *, firmware_side: bool = False) -> Path:
    base = images / ("yocto-firmware" if firmware_side else "") / src.name
    return base


def skip_image_path_placeholder(value: str) -> bool:
    return value in ("", "<default>")


def same_existing_file(left: Path, right: Path) -> bool:
    try:
        return left.resolve(strict=True) == right.resolve(strict=True)
    except OSError:
        return False


def wic_patch_marker(wic: Path) -> Path:
    return wic.with_name(f".{wic.name}.local-uki-patch.json")


def file_fingerprint(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    stat = resolved.stat()
    return {
        "path": str(resolved),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def wic_patch_payload(
    wic_src: Path,
    slots: tuple[tuple[str, str], ...],
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "source": file_fingerprint(wic_src),
        "slots": [
            {
                "name": name,
                "offset": offset,
                "sha256": digest(images / name),
            }
            for name, offset in slots
        ],
    }


def wic_patch_current(wic: Path, payload: dict[str, object]) -> bool:
    marker = wic_patch_marker(wic)
    if not wic.exists() or not marker.is_file():
        return False
    try:
        current = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return current == payload


def write_wic_patch_marker(wic: Path, payload: dict[str, object]) -> None:
    marker = wic_patch_marker(wic)
    pending = marker.with_suffix(marker.suffix + ".tmp")
    safe_write_path(marker)
    safe_write_path(pending)
    pending.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    pending.replace(marker)


if deploy.is_symlink():
    fail(f"refusing to use deploy root symlink: {deploy}")

fvpconf_src = latest_or_stable(
    f"nexios-image-{machine}.fvpconf", f"nexios-image-{machine}-*.fvpconf"
)
wic_src = latest_or_stable(
    f"nexios-image-{machine}.wic", f"nexios-image-{machine}-*.wic"
)

cfg = json.loads(fvpconf_src.read_text(encoding="utf-8"))
wic = images / f"nexios-image-{machine}.wic"
local_image = deploy / "boot" / "Image"
local_dtb = deploy / "boot" / "apollo-fvp.dtb"
local_linux_inputs_present = local_image.exists() and local_dtb.exists()
if not local_linux_inputs_present:
    copy_artifact(wic_src, wic, "yocto-copied")

side_names = [
    f"nexios-image-{machine}.manifest",
    f"nexios-image-{machine}.testdata.json",
    f"nexios-image-{machine}.ext4.verity",
    f"nexios-image-{machine}.ext4.verity.env",
    f"nexios-initramfs-image-{machine}.cpio.gz",
    "auto-ad-nexios-a.efi",
    "auto-ad-nexios-b.efi",
    "linuxaa64.efi.stub",
    "efi-capsule-update-disk-image-fvp-rd-aspen.img",
    "efi-capsule-update-image.img.json",
    "efi-capsule-update-image.img.uefi.capsule",
    "nexios-image.env",
]
for src in sorted(yocto_deploy.glob(f"u-boot-{machine}-*.bin")):
    copy_artifact(src, images / src.name, "yocto-copied")
for src in sorted(yocto_deploy.glob(f"u-boot-initial-env-{machine}-*")):
    copy_artifact(src, images / src.name, "yocto-copied")
for name in side_names:
    src = yocto_deploy / name
    if src.exists():
        copy_artifact(src, images / src.name, "yocto-copied")

local_map: dict[str, str] = {}
for key, value in list(cfg.get("parameters", {}).items()):
    if not isinstance(value, str):
        continue
    if key.endswith(".image_path"):
        if skip_image_path_placeholder(value):
            continue
        src = Path(value)
        if local_linux_inputs_present and same_existing_file(src, wic_src):
            local_map[str(src)] = str(wic)
            continue
        copy_artifact(src, local_image_path(src), "yocto-copied")
        local_map[str(src)] = str(local_image_path(src))

for name in (
    "rse-rom-image.img",
    "rse-flash-image.img",
    "rse-otp-image.img",
    "ap-flash-image.img",
    "combined_provisioning_message.bin",
):
    src = firmware / name
    copy_local(src, firmware / name, "local-firmware-overlay", "local firmware overlay")

firmware_names = {
    "rse-rom-image.img",
    "rse-flash-image.img",
    "rse-otp-image.img",
    "ap-flash-image.img",
    "combined_provisioning_message.bin",
}

for key, value in list(cfg.get("parameters", {}).items()):
    if not isinstance(value, str):
        continue
    src = Path(value)
    if src.name in firmware_names:
        cfg["parameters"][key] = str(firmware / src.name)
    elif key.endswith(".image_path"):
        if skip_image_path_placeholder(value):
            continue
        cfg["parameters"][key] = local_map[str(src)]

rewritten_data = []
for entry in cfg.get("data", []):
    if not isinstance(entry, str) or "=" not in entry or "@" not in entry:
        rewritten_data.append(entry)
        continue
    prefix, rest = entry.split("=", 1)
    path_text, suffix = rest.rsplit("@", 1)
    src = Path(path_text)
    if src.name in firmware_names:
        dst = firmware / src.name
    else:
        dst = local_image_path(src, firmware_side=True)
        if not (local_linux_inputs_present and same_existing_file(src, wic_src)):
            copy_artifact(src, dst, "yocto-copied")
    rewritten_data.append(f"{prefix}={dst}@{suffix}")
cfg["data"] = rewritten_data


def recipe_vars(recipe: str) -> dict[str, str]:
    try:
        raw = json.loads(vars_path.read_text(encoding="utf-8"))
    except OSError:
        return {}
    return raw.get("recipes", {}).get(recipe, {}).get("variables", {})


REQUIRED_UKI_VARS = (
    "INITRD_ARCHIVE",
    "EFI_ARCH",
    "AUTO_AD_NEXIOS_UKI_A",
    "AUTO_AD_NEXIOS_UKI_B",
    "AUTO_AD_NEXIOS_UKI_CMDLINE_A",
    "AUTO_AD_NEXIOS_UKI_CMDLINE_B",
    "UEFI_SECURE_BOOT",
)


def refresh_vars_if_needed(variables: dict[str, str]) -> dict[str, str]:
    missing = [name for name in REQUIRED_UKI_VARS if not variables.get(name)]
    if not missing:
        return variables
    collector = Path.cwd() / "scripts" / "build" / "collect_yocto_local_build_vars.py"
    if collector.is_file():
        subprocess.run(["python3", str(collector), "--output", str(vars_path)], check=True)
    variables = recipe_vars("nexios-image")
    missing = [name for name in REQUIRED_UKI_VARS if not variables.get(name)]
    if missing:
        fail(f"refresh did not provide required UKI variable(s): {', '.join(missing)}")
    return variables


def native_python_env(native_root: Path) -> dict[str, str]:
    env = os.environ.copy()
    sites = sorted(native_root.glob("usr/lib/python*/site-packages"))
    if sites:
        env["PYTHONPATH"] = f"{sites[-1]}:{env.get('PYTHONPATH', '')}".rstrip(":")
    return env


def native_root_for_tool(tool: Path) -> Path | None:
    if (
        len(tool.parents) >= 3
        and tool.parent.name == "bin"
        and tool.parent.parent.name == "usr"
    ):
        root = tool.parents[2]
        if list(root.glob("usr/lib/python*/site-packages")):
            return root
    return None


def find_native_ukify() -> tuple[str, dict[str, str]] | None:
    yocto_tmp = os.environ.get("YOCTO_TMP")
    if not yocto_tmp:
        return None
    candidates = sorted(
        Path(yocto_tmp).glob("work/*/nexios-image/*/recipe-sysroot-native/usr/bin/ukify")
    )
    if not candidates:
        return None
    tool = candidates[-1]
    return str(tool), native_python_env(tool.parents[2])


def resolve_ukify(raw_cmd: str) -> tuple[str, dict[str, str]]:
    argv = shlex.split(raw_cmd or "ukify")
    if not argv:
        argv = ["ukify"]
    tool = argv[0]
    extra = argv[1:]
    if extra and extra != ["build"]:
        fail(f"unsupported UKIFY_CMD arguments: {raw_cmd}")
    if tool != "ukify":
        path = Path(tool)
        if not path.is_file():
            fail(f"UKIFY_CMD not found: {tool}")
        native_root = native_root_for_tool(path)
        if native_root is not None:
            return str(path), native_python_env(native_root)
        return str(path), os.environ.copy()
    native = find_native_ukify()
    if native is not None:
        return native
    found = shutil.which("ukify")
    if found:
        return found, os.environ.copy()
    fail("UKIFY_CMD not found: ukify")


linux_source = "yocto-copied"
if local_linux_inputs_present:
    variables = refresh_vars_if_needed(recipe_vars("nexios-image"))
    uki_a = safe_name(variables.get("AUTO_AD_NEXIOS_UKI_A", "auto-ad-nexios-a.efi"), "AUTO_AD_NEXIOS_UKI_A")
    uki_b = safe_name(variables.get("AUTO_AD_NEXIOS_UKI_B", "auto-ad-nexios-b.efi"), "AUTO_AD_NEXIOS_UKI_B")
    initrd_name = safe_name(variables["INITRD_ARCHIVE"], "INITRD_ARCHIVE")
    ukify, ukify_env = resolve_ukify(variables.get("UKIFY_CMD", "ukify"))
    if variables.get("UEFI_SECURE_BOOT") == "1":
        for key_name in ("UKI_SB_KEY", "UKI_SB_CERT"):
            key_path = Path(variables.get(key_name, ""))
            if not key_path.is_file():
                fail(f"{key_name} not found: {key_path}")
    stub = images / "linuxaa64.efi.stub"
    initrd = images / initrd_name
    copy_artifact(yocto_deploy / "linuxaa64.efi.stub", stub, "yocto-copied")
    if os.environ.get("APOLLO_LOCAL_BUILD_UKI_INITRD") == "local" and (deploy / "boot" / "initramfs.cpio.gz").exists():
        initrd = deploy / "boot" / "initramfs.cpio.gz"
        ensure_local_source(initrd, local_build, "local-initramfs")
        cmdline_a = os.environ.get("LOCAL_BUILD_BOOTARGS", variables["AUTO_AD_NEXIOS_UKI_CMDLINE_A"])
        cmdline_b = os.environ.get("LOCAL_BUILD_BOOTARGS", variables["AUTO_AD_NEXIOS_UKI_CMDLINE_B"])
        initrd_provenance = "local-initramfs"
    else:
        copy_artifact(yocto_deploy / initrd_name, initrd, "yocto-copied")
        cmdline_a = variables["AUTO_AD_NEXIOS_UKI_CMDLINE_A"]
        cmdline_b = variables["AUTO_AD_NEXIOS_UKI_CMDLINE_B"]
        initrd_provenance = "yocto-copied"
    for name, cmd_var in (
        (uki_a, cmdline_a),
        (uki_b, cmdline_b),
    ):
        out = images / name
        safe_write_path(out)
        cmdline = cmd_var
        subprocess.run(
            [
                ukify,
                "build",
                f"--linux={local_image}",
                "--devicetree",
                str(local_dtb),
                f"--initrd={initrd}",
                "--stub",
                str(stub),
                f"--cmdline={cmdline}",
                f"--output={out}",
            ],
            check=True,
            env=ukify_env,
        )
        forget_artifact_path(out)
        artifacts.append(
            {
                "source_path": str(local_image),
                "local_path": str(out),
                "component_provenance": "local-uki",
                "size": out.stat().st_size,
                "sha256": digest(out),
                "source_preserved": True,
            }
        )
    wic_slots = ((uki_a, "1048576"), (uki_b, "135266304"))
    wic_payload = wic_patch_payload(wic_src, wic_slots)
    try:
        if wic_patch_current(wic, wic_payload):
            record_copied_artifact(wic_src, wic, "yocto-copied")
        else:
            copy_artifact(wic_src, wic, "yocto-copied")
            subprocess.run(["sgdisk", "-p", str(wic)], check=True, stdout=subprocess.PIPE, text=True)
            for name, offset in wic_slots:
                ensure_mtools_dir(f"{wic}@@{offset}", "::/EFI")
                subprocess.run(["mcopy", "-o", "-i", f"{wic}@@{offset}", str(images / name), "::/EFI/BOOT/BOOTAA64.EFI"], check=True)
            write_wic_patch_marker(wic, wic_payload)
    except subprocess.CalledProcessError:
        wic.unlink(missing_ok=True)
        wic_patch_marker(wic).unlink(missing_ok=True)
        (deploy / "apollo-fvp-local.fvpconf").unlink(missing_ok=True)
        raise
    modules_order = local_build / "work" / "linux" / "modules.order"
    release_file = local_build / "work" / "linux" / "include" / "config" / "kernel.release"
    local_linux_modules = None
    if modules_order.exists() and release_file.exists():
        release = safe_kernel_release(release_file.read_text(encoding="utf-8").strip())
        modules_dir = deploy / "modules" / release
        for line in modules_order.read_text(encoding="utf-8").splitlines():
            if line.startswith("/") or ".." in Path(line).parts:
                fail(f"unsafe modules.order entry: {line}")
            src = local_build / "work" / "linux" / line
            if src.exists():
                copy_local(src, modules_dir / line, "local-linux-module-staged")
        local_linux_modules = {
            "kernel_release": release,
            "staged_dir": str(modules_dir),
            "injected_into_rootfs": False,
            "limitation": "local modules are staged but not injected into rootfs",
        }
    local_linux = {
        "initrd": str(initrd),
        "initrd_provenance": initrd_provenance,
        "cmdline_a": cmdline_a,
        "cmdline_b": cmdline_b,
    }
    linux_source = "local-uki"
else:
    local_linux_modules = None
    local_linux = None

local_uboot = deploy / "u-boot" / "u-boot.bin"
if local_uboot.exists():
    copy_local(local_uboot, images / f"u-boot-{machine}-local.bin", "local-u-boot-overlay")

local_fvpconf = deploy / "apollo-fvp-local.fvpconf"
manifest_path = deploy / "local-package-manifest.json"
pending_fvpconf = deploy / "apollo-fvp-local.fvpconf.tmp"
pending_manifest = deploy / "local-package-manifest.json.tmp"
pending_digest_cache = deploy / ".apollo-package-digests.json.tmp"
for path in (
    local_fvpconf,
    manifest_path,
    digest_cache_path,
    pending_fvpconf,
    pending_manifest,
    pending_digest_cache,
):
    safe_write_path(path)

safe_mkdir(deploy)
pending_fvpconf.write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n", encoding="utf-8")
manifest = {
    "schema_version": 1,
    "machine": machine,
    "linux_source": linux_source,
    "source_preservation": {"all_sources_preserved": True},
    "artifacts": artifacts,
}
if local_linux is not None:
    manifest["local_linux"] = local_linux
if local_linux_modules is not None:
    manifest["local_linux_modules"] = local_linux_modules
pending_manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
pending_digest_cache.write_text(
    json.dumps(digest_cache, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
pending_fvpconf.replace(local_fvpconf)
pending_manifest.replace(manifest_path)
pending_digest_cache.replace(digest_cache_path)
print(f"local FVP package: {local_fvpconf}")
PY
}
