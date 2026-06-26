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
        *) require_command sgdisk ;;
    esac

    if [[ -f "${BOOT_DIR}/Image" && -f "${BOOT_DIR}/apollo-fvp.dtb" ]]; then
        require_command sgdisk
        require_command mdir
        require_command mmd
        require_command mcopy
    fi
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


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(16 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


artifacts: list[dict[str, object]] = []


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
    ensure_existing_source(src, root, "Yocto deploy source")
    safe_write_path(dst)
    safe_mkdir(dst.parent)
    same_file = dst.exists() and os.path.samefile(src, dst)
    source_hash = digest(src)
    if not same_file:
        copy_preserving_sparse(src, dst)
        if dst.stat().st_size != src.stat().st_size:
            fail(f"copied artifact size mismatch: {src} -> {dst}")
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


def copy_local(src: Path, dst: Path, provenance: str, label: str | None = None) -> None:
    ensure_local_source(src, local_build, label or provenance)
    safe_write_path(dst)
    safe_mkdir(dst.parent)
    if not dst.exists() or src.resolve(strict=True) != dst.resolve(strict=True):
        shutil.copy2(src, dst)
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


if deploy.is_symlink():
    fail(f"refusing to use deploy root symlink: {deploy}")

fvpconf_src = latest_or_stable(
    f"nexios-image-{machine}.fvpconf", f"nexios-image-{machine}-*.fvpconf"
)
wic_src = latest_or_stable(
    f"nexios-image-{machine}.wic", f"nexios-image-{machine}-*.wic"
)

cfg = json.loads(fvpconf_src.read_text(encoding="utf-8"))
copy_artifact(wic_src, images / f"nexios-image-{machine}.wic", "yocto-copied")

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
local_image = deploy / "boot" / "Image"
local_dtb = deploy / "boot" / "apollo-fvp.dtb"
if local_image.exists() and local_dtb.exists():
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
    wic = images / f"nexios-image-{machine}.wic"
    try:
        subprocess.run(["sgdisk", "-p", str(wic)], check=True, stdout=subprocess.PIPE, text=True)
        for name, offset in ((uki_a, "1048576"), (uki_b, "135266304")):
            ensure_mtools_dir(f"{wic}@@{offset}", "::/EFI")
            subprocess.run(["mcopy", "-o", "-i", f"{wic}@@{offset}", str(images / name), "::/EFI/BOOT/BOOTAA64.EFI"], check=True)
    except subprocess.CalledProcessError:
        wic.unlink(missing_ok=True)
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
for path in (local_fvpconf, manifest_path, pending_fvpconf, pending_manifest):
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
pending_fvpconf.replace(local_fvpconf)
pending_manifest.replace(manifest_path)
print(f"local FVP package: {local_fvpconf}")
PY
}
