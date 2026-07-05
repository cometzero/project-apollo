#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
# shellcheck source=scripts/build/local_build_common.sh
source "${ROOT_DIR}/scripts/build/local_build_common.sh"

PACKAGE_DIR="${PACKAGE_DIR:-${LOCAL_BUILD_DIR}/package/qbox}"
PACKAGE_LOCAL_BUILD_DIR="${PACKAGE_LOCAL_BUILD_DIR:-${PACKAGE_DIR}/local-build}"
QBOX_CONF="${QBOX_CONF:-${QBOX_PLATFORM_DIR}/platforms/apollo/apollo-qvp.lua}"
PACKAGE_RECORDS=()

usage()
{
    cat <<EOF
Usage: scripts/package.sh

Package existing local-build outputs into a QBox-runnable local-build tree.

Default output:
  ${PACKAGE_LOCAL_BUILD_DIR}

Run packaged images:
  ./run_qbox.sh --local-build-dir ${PACKAGE_LOCAL_BUILD_DIR} --qbox-build-dir ${QBOX_PLATFORM_BUILD_DIR}

Useful overrides:
  PACKAGE_DIR=/path/to/package ./local_build.sh --package
  LOCAL_BUILD_DIR=/path/to/local-build ./local_build.sh --package
EOF
}

copy_package_artifact()
{
    local name="$1"
    local rel="$2"
    local required="$3"
    local src="${LOCAL_BUILD_DIR}/${rel}"
    local dst="${PACKAGE_LOCAL_BUILD_DIR}/${rel}"

    if [[ ! -f "${src}" ]]; then
        if [[ "${required}" == "required" ]]; then
            die "missing package artifact ${name}: ${src}; run ./local_build.sh first"
        fi
        return 0
    fi

    mkdir -p "$(dirname "${dst}")"
    cp --reflink=auto --sparse=always -- "${src}" "${dst}"
    PACKAGE_RECORDS+=("${name}|${rel}|${required}")
}

write_package_readme()
{
    write_file_if_changed "${PACKAGE_DIR}/README.md" <<EOF
# Apollo FVP QBox Image Package

This package mirrors the subset of \`build/local-apollo-fvp\` that the Apollo
QBox full-system runner consumes.

Run it from the workspace top directory:

\`\`\`bash
./run_qbox.sh --local-build-dir ${PACKAGE_LOCAL_BUILD_DIR} --qbox-build-dir ${QBOX_PLATFORM_BUILD_DIR}
\`\`\`

The artifact manifest is \`manifest.json\`.
EOF
}

write_package_manifest()
{
    python3 - \
        "${PACKAGE_DIR}" \
        "${PACKAGE_LOCAL_BUILD_DIR}" \
        "${LOCAL_BUILD_DIR}" \
        "${QBOX_CORE_DIR}" \
        "${QBOX_PLATFORM_DIR}" \
        "${QBOX_QEMU_DIR}" \
        "${QBOX_PLATFORM_BUILD_DIR}" \
        "${QBOX_CONF}" \
        "${PACKAGE_RECORDS[@]}" <<'PY'
import hashlib
import json
import pathlib
import subprocess
import sys

package_dir = pathlib.Path(sys.argv[1]).resolve()
package_local_build_dir = pathlib.Path(sys.argv[2]).resolve()
source_local_build_dir = pathlib.Path(sys.argv[3]).resolve()
qbox_core_dir = pathlib.Path(sys.argv[4]).resolve()
qbox_platform_dir = pathlib.Path(sys.argv[5]).resolve()
qbox_qemu_dir = pathlib.Path(sys.argv[6]).resolve()
qbox_platform_build_dir = pathlib.Path(sys.argv[7]).resolve()
qbox_conf = pathlib.Path(sys.argv[8]).resolve()


def file_record(path: pathlib.Path) -> dict[str, object]:
    record: dict[str, object] = {
        "path": str(path),
        "exists": path.exists(),
        "size": None,
        "sha256": None,
    }
    if path.is_file():
        with path.open("rb") as handle:
            record["sha256"] = hashlib.file_digest(handle, "sha256").hexdigest()
        record["size"] = path.stat().st_size
    return record


def git_record(path: pathlib.Path) -> dict[str, object]:
    record: dict[str, object] = {"path": str(path), "head": None, "status": None}
    if not (path / ".git").exists():
        return record
    head = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if head.returncode == 0:
        record["head"] = head.stdout.strip()
    status = subprocess.run(
        ["git", "-C", str(path), "status", "--porcelain=v1", "--untracked-files=no"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if status.returncode == 0:
        record["status"] = status.stdout.splitlines()
    return record

artifacts = {}
for record in sys.argv[9:]:
    name, rel, requirement = record.split("|", 2)
    path = package_local_build_dir / rel
    artifact = file_record(path)
    artifact.update(
        {
            "relative_path": rel,
            "source_path": str(source_local_build_dir / rel),
            "requirement": requirement,
        }
    )
    artifacts[name] = {
        key: artifact[key]
        for key in ["path", "relative_path", "source_path", "size", "sha256", "requirement"]
    }

manifest = {
    "package_dir": str(package_dir),
    "local_build_dir": str(package_local_build_dir),
    "source_local_build_dir": str(source_local_build_dir),
    "run_command": [
        "./run_qbox.sh",
        "--local-build-dir",
        str(package_local_build_dir),
        "--qbox-build-dir",
        str(qbox_platform_build_dir),
    ],
    "artifacts": artifacts,
    "qbox": {
        "core": git_record(qbox_core_dir),
        "platform": git_record(qbox_platform_dir),
        "qemu": git_record(qbox_qemu_dir),
        "platform_build_dir": str(qbox_platform_build_dir),
        "platform_executable": file_record(qbox_platform_build_dir / "platforms-vp"),
        "platform_conf": file_record(qbox_conf),
    },
}

(package_dir / "manifest.json").write_text(
    json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY
}

package_qbox_images()
{
    [[ "${PACKAGE_LOCAL_BUILD_DIR}" != "/" ]] || die "refusing to package into /"
    require_file "${QBOX_PLATFORM_BUILD_DIR}/platforms-vp"
    require_file "${QBOX_CONF}"
    rm -rf "${PACKAGE_LOCAL_BUILD_DIR}"
    mkdir -p "${PACKAGE_LOCAL_BUILD_DIR}"

    copy_package_artifact rse_rom deploy/firmware/rse-rom-image.img required
    copy_package_artifact rse_flash deploy/firmware/rse-flash-image.img required
    copy_package_artifact rse_otp deploy/firmware/rse-otp-image.img required
    copy_package_artifact ap_flash deploy/firmware/ap-flash-image.img required
    copy_package_artifact fip deploy/firmware/fip.bin required
    copy_package_artifact init_fwu_metadata deploy/firmware/init_fwu_metadata.bin required
    copy_package_artifact provisioning_bundle deploy/firmware/combined_provisioning_message.bin required
    copy_package_artifact si_cl0_image deploy/firmware/si0_ramfw.bin required
    copy_package_artifact si_cl1_image deploy/firmware/zephyr-demos-cl1.bin required
    copy_package_artifact si_cl1_symbols deploy/firmware/zephyr-demos-cl1.elf required
    copy_package_artifact rootfs deploy/boot/apollo-fvp-local-disk.img required
    copy_package_artifact efi_capsule_disk deploy/boot/boot-fat.img required
    copy_package_artifact ap_dtb deploy/boot/apollo-fvp.dtb required
    copy_package_artifact signed_ap_bl2 work/signing/deploy/signed_bl2.bin required
    copy_package_artifact ap_bl2_elf work/trusted-firmware-a/apollo_fvp/debug/bl2/bl2.elf required
    copy_package_artifact rse_bl1_2_elf work/trusted-firmware-m/bin/bl1_2.elf required
    copy_package_artifact rse_bl2_elf work/trusted-firmware-m/bin/bl2.elf required
    copy_package_artifact rse_symbols debug/symbols.json required

    copy_package_artifact kernel_image deploy/boot/Image optional
    copy_package_artifact initramfs deploy/boot/initramfs.cpio.gz optional
    copy_package_artifact boot_script deploy/boot/boot.scr optional
    copy_package_artifact boot_command deploy/boot/boot.cmd optional
    copy_package_artifact fvp_config "deploy/${MACHINE}-local.fvpconf" optional
    copy_package_artifact tfm_bl1_1 deploy/firmware/bl1_1.bin optional
    copy_package_artifact tfa_bl2 deploy/firmware/bl2.bin optional
    copy_package_artifact tfm_bl2_signed deploy/firmware/bl2_signed.bin optional
    copy_package_artifact tfm_runtime_signed deploy/firmware/tfm_s_signed.bin optional
    copy_package_artifact rom_dma_ics deploy/firmware/rom_dma_ics.bin optional
    copy_package_artifact encryption_key deploy/firmware/enc_key_s.b64 optional

    write_package_manifest
    write_package_readme
    log "Packaged QBox local-build images: ${PACKAGE_LOCAL_BUILD_DIR}"
}

main()
{
    case "${1:-}" in
        -h|--help|help)
            usage
            return 0
            ;;
    esac

    (($# == 0)) || die "scripts/package.sh does not accept arguments"
    package_qbox_images
}

main "$@"
