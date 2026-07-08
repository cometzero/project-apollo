#!/usr/bin/env bash

machine_to_work_prefix() {
    local machine="$1"
    printf '%s\n' "${machine//-/_}"
}

latest_glob() {
    local pattern="$1"
    local matches=()
    local path
    while IFS= read -r path; do
        [[ -f "${path}" ]] || continue
        matches+=("${path}")
    done < <(compgen -G "${pattern}" || true)

    ((${#matches[@]} > 0)) || return 1
    printf '%s\n' "${matches[@]}" \
        | while IFS= read -r path; do
            printf '%s\t%s\n' "$(stat -c '%Y' "${path}")" "${path}"
        done \
        | sort -nr \
        | sed -n '1s/^[^	]*	//p'
}

resolve_qboxconf_default() {
    local fixed="${DEPLOY_DIR}/${IMAGE_BASENAME}-${MACHINE}.qboxconf"
    if [[ -f "${fixed}" ]]; then
        printf '%s\n' "${fixed}"
        return 0
    fi

    local latest=""
    latest="$(latest_glob "${DEPLOY_DIR}/${IMAGE_BASENAME}-${MACHINE}-*.qboxconf" || true)"
    if [[ -n "${latest}" ]]; then
        printf '%s\n' "${latest}"
        return 0
    fi

    local imgdeploy_pattern="${YOCTO_BUILD_DIR}/tmp_baremetal/work/${WORK_PREFIX}-poky-linux/${IMAGE_BASENAME}/*/deploy-${IMAGE_BASENAME}-image-complete"
    latest="$(latest_glob "${imgdeploy_pattern}/${IMAGE_BASENAME}-${MACHINE}.qboxconf" || true)"
    if [[ -n "${latest}" ]]; then
        printf '%s\n' "${latest}"
        return 0
    fi

    latest="$(latest_glob "${imgdeploy_pattern}/${IMAGE_BASENAME}-${MACHINE}-*.qboxconf" || true)"
    if [[ -n "${latest}" ]]; then
        printf '%s\n' "${latest}"
        return 0
    fi

    {
        echo "missing required QBox qboxconf"
        echo "  tried: ${fixed}"
        echo "  tried glob: ${DEPLOY_DIR}/${IMAGE_BASENAME}-${MACHINE}-*.qboxconf"
        echo "  tried glob: ${imgdeploy_pattern}/${IMAGE_BASENAME}-${MACHINE}.qboxconf"
        echo "  tried glob: ${imgdeploy_pattern}/${IMAGE_BASENAME}-${MACHINE}-*.qboxconf"
    } >&2
    exit 1
}

read_qboxconf_shell_assignments() {
    local qboxconf="$1"
    local current_ld_library_path="${LD_LIBRARY_PATH:-}"

    "${PYTHON:-python3}" - "${qboxconf}" "${current_ld_library_path}" "${YOCTO_BUILD_DIR}" <<'PY'
from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import shlex
import sys
from typing import TypeAlias


class QBoxConfError(Exception):
    pass


JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]
EXPECTED_PROVIDER = "qbox-apollo-qvp-native"


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def require_object(value: JsonObject, field: str) -> JsonObject:
    item = value.get(field)
    if not isinstance(item, dict):
        raise QBoxConfError(f"qboxconf field {field} must be an object")
    return item


def require_string(value: JsonObject, field: str) -> str:
    item = value.get(field)
    if not isinstance(item, str) or item == "":
        raise QBoxConfError(f"qboxconf field {field} must be a non-empty string")
    return item


def require_safe_relative(value: str, field: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\x00" in value:
        raise QBoxConfError(f"qboxconf field {field} must be a safe relative path")
    return value


def resolve_existing_dir(value: str, field: str) -> Path:
    try:
        resolved = Path(value).resolve(strict=True)
    except OSError as error:
        raise QBoxConfError(
            f"qboxconf trust error: {field} must resolve to an existing directory: {value}: {error}"
        ) from error
    if not resolved.is_dir():
        raise QBoxConfError(
            f"qboxconf trust error: {field} must resolve to an existing directory: {value}"
        )
    return resolved


def relative_to_trusted(path: Path, root: Path, field: str) -> tuple[str, ...]:
    try:
        return path.relative_to(root).parts
    except ValueError as error:
        raise QBoxConfError(
            f"qboxconf trust error: {field} resolves outside trusted Yocto path {root}: {path}"
        ) from error


def validate_provider_dir(
    value: str,
    field: str,
    components_root: Path,
    provider_usr: Path | None,
) -> tuple[Path, Path]:
    resolved = resolve_existing_dir(value, field)
    relative_parts = relative_to_trusted(resolved, components_root, field)
    if (
        len(relative_parts) < 4
        or relative_parts[1] != EXPECTED_PROVIDER
        or relative_parts[2] != "usr"
    ):
        raise QBoxConfError(
            f"qboxconf trust error: {field} must be under "
            f"{components_root}/<arch>/{EXPECTED_PROVIDER}/usr: {resolved}"
        )
    candidate_provider_usr = components_root.joinpath(
        relative_parts[0],
        EXPECTED_PROVIDER,
        "usr",
    )
    if provider_usr is not None and candidate_provider_usr != provider_usr:
        raise QBoxConfError(
            f"qboxconf trust error: {field} must use provider subtree {provider_usr}: {resolved}"
        )
    return resolved, candidate_provider_usr


def require_exact_path(path: Path, expected: Path, field: str) -> None:
    if path != expected:
        raise QBoxConfError(
            f"qboxconf trust error: {field} must resolve to {expected}: {path}"
        )


def require_under(path: Path, root: Path, field: str) -> None:
    relative_to_trusted(path, root, field)


def validate_trusted_paths(
    provider: JsonObject,
    sysroot: JsonObject,
    yocto_build_dir: Path,
) -> tuple[Path, Path, Path, Path, Path]:
    provider_name = require_string(provider, "name")
    if provider_name != EXPECTED_PROVIDER:
        raise QBoxConfError(
            f"qboxconf trust error: provider.name must be {EXPECTED_PROVIDER}: {provider_name}"
        )

    tmpdir = yocto_build_dir / "tmp_baremetal"
    expected_components_root = (tmpdir / "sysroots-components").resolve(strict=True)
    expected_work_root = (tmpdir / "work").resolve(strict=True)
    configured_components_root = resolve_existing_dir(
        require_string(sysroot, "components_dir"),
        "sysroot.components_dir",
    )
    require_exact_path(
        configured_components_root,
        expected_components_root,
        "sysroot.components_dir",
    )

    provider_usr: Path | None = None
    bindir, provider_usr = validate_provider_dir(
        require_string(provider, "bindir"),
        "provider.bindir",
        expected_components_root,
        provider_usr,
    )
    libdir, provider_usr = validate_provider_dir(
        require_string(provider, "libdir"),
        "provider.libdir",
        expected_components_root,
        provider_usr,
    )
    module_dir, provider_usr = validate_provider_dir(
        require_string(provider, "module_dir"),
        "provider.module_dir",
        expected_components_root,
        provider_usr,
    )
    data_dir, provider_usr = validate_provider_dir(
        require_string(provider, "data_dir"),
        "provider.data_dir",
        expected_components_root,
        provider_usr,
    )
    require_exact_path(bindir, provider_usr / "bin", "provider.bindir")
    require_exact_path(libdir, provider_usr / "lib", "provider.libdir")
    require_under(module_dir, provider_usr / "lib" / "qbox", "provider.module_dir")
    require_exact_path(data_dir, provider_usr / "share" / "qbox", "provider.data_dir")

    recipe_sysroot_native = resolve_existing_dir(
        require_string(sysroot, "recipe_sysroot_native"),
        "sysroot.recipe_sysroot_native",
    )
    require_under(
        recipe_sysroot_native,
        expected_work_root,
        "sysroot.recipe_sysroot_native",
    )
    return bindir, libdir, module_dir, data_dir, recipe_sysroot_native


def quote_assignment(name: str, value: str) -> str:
    return f"{name}={shlex.quote(value)}"


def image_path(images: JsonObject, qboxconf_dir: Path, *keys: str) -> str:
    for key in keys:
        item = images.get(key)
        if isinstance(item, str) and item:
            return str(qboxconf_dir / require_safe_relative(item, f"images.{key}"))
    return ""


raw_qboxconf = Path(sys.argv[1])
current_ld_library_path = sys.argv[2]
raw_yocto_build_dir = Path(sys.argv[3])
if not raw_qboxconf.is_file():
    fail(f"qboxconf not found: {raw_qboxconf}")
qboxconf = raw_qboxconf.resolve()
try:
    yocto_build_dir = raw_yocto_build_dir.resolve(strict=True)
except OSError as error:
    fail(f"Yocto build directory not found: {raw_yocto_build_dir}: {error}")

try:
    loaded = json.loads(qboxconf.read_text(encoding="utf-8"))
except json.JSONDecodeError as error:
    fail(f"invalid qboxconf JSON: {qboxconf}: line {error.lineno} column {error.colno}: {error.msg}")
except OSError as error:
    fail(f"unable to read qboxconf: {qboxconf}: {error}")

if not isinstance(loaded, dict):
    fail(f"invalid qboxconf schema: {qboxconf}: root must be an object")

try:
    provider = require_object(loaded, "provider")
    sysroot = require_object(loaded, "sysroot")
    bindir_path, libdir_path, module_dir_path, data_dir_path, recipe_sysroot_native_path = (
        validate_trusted_paths(provider, sysroot, yocto_build_dir)
    )
    bindir = str(bindir_path)
    libdir = str(libdir_path)
    module_dir = str(module_dir_path)
    data_dir = str(data_dir_path)
    recipe_sysroot_native = str(recipe_sysroot_native_path)
    exe = require_safe_relative(require_string(loaded, "exe"), "exe")
    config = require_safe_relative(require_string(loaded, "config"), "config")
except QBoxConfError as error:
    fail(f"invalid qboxconf schema: {qboxconf}: {error}")

debug_symbols_value = loaded.get("debug_symbols")
debug_symbols = debug_symbols_value if isinstance(debug_symbols_value, str) else ""
images_value = loaded.get("images")
images = images_value if isinstance(images_value, dict) else {}
qboxconf_dir = qboxconf.parent
ld_entries = [libdir, module_dir]
recipe_sysroot_native_libdir = recipe_sysroot_native_path / "usr" / "lib"
if recipe_sysroot_native_libdir.is_dir():
    ld_entries.append(str(recipe_sysroot_native_libdir))
if current_ld_library_path:
    ld_entries.append(current_ld_library_path)

assignments = {
    "QBOXCONF_PROVIDER_BINDIR": bindir,
    "QBOXCONF_PROVIDER_LIBDIR": libdir,
    "QBOXCONF_PROVIDER_MODULE_DIR": module_dir,
    "QBOXCONF_PROVIDER_DATA_DIR": data_dir,
    "QBOXCONF_RECIPE_SYSROOT_NATIVE": recipe_sysroot_native,
    "QBOXCONF_EXE": str(Path(bindir) / exe),
    "QBOXCONF_CONFIG": str(Path(data_dir) / config),
    "QBOXCONF_DEBUG_SYMBOLS": debug_symbols,
    "QBOXCONF_LD_LIBRARY_PATH": ":".join(ld_entries),
    "QBOXCONF_IMAGE_ROOTFS_WIC": image_path(images, qboxconf_dir, "rootfs_wic", "wic"),
    "QBOXCONF_IMAGE_EFI_CAPSULE_DISK": image_path(images, qboxconf_dir, "efi_capsule_disk"),
    "QBOXCONF_IMAGE_RSE_ROM": image_path(images, qboxconf_dir, "rse_rom"),
    "QBOXCONF_IMAGE_RSE_FLASH": image_path(images, qboxconf_dir, "rse_flash"),
    "QBOXCONF_IMAGE_RSE_OTP": image_path(images, qboxconf_dir, "rse_otp"),
    "QBOXCONF_IMAGE_AP_FLASH": image_path(images, qboxconf_dir, "ap_flash"),
    "QBOXCONF_IMAGE_AP_BL2_ELF": image_path(images, qboxconf_dir, "ap_bl2_elf"),
    "QBOXCONF_IMAGE_RSE_BL1_2_ELF": image_path(images, qboxconf_dir, "rse_bl1_2_elf"),
    "QBOXCONF_IMAGE_RSE_BL2_ELF": image_path(images, qboxconf_dir, "rse_bl2_elf"),
    "QBOXCONF_IMAGE_PROVISIONING_BUNDLE": image_path(images, qboxconf_dir, "provisioning_bundle"),
    "QBOXCONF_IMAGE_AP_DTB": image_path(images, qboxconf_dir, "ap_dtb", "dtb"),
    "QBOXCONF_IMAGE_SI_CL0": image_path(images, qboxconf_dir, "si_cl0_image", "si0_ramfw"),
    "QBOXCONF_IMAGE_SI_CL1": image_path(images, qboxconf_dir, "si_cl1_image", "si_cl1"),
    "QBOXCONF_IMAGE_SI_CL1_SYMBOLS": image_path(images, qboxconf_dir, "si_cl1_symbols"),
}
for name, value in assignments.items():
    print(quote_assignment(name, value))
PY
}
