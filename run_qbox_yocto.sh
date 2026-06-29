#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${SCRIPT_DIR}"

die() {
    echo "run_qbox_yocto.sh: error: $*" >&2
    exit 1
}

usage() {
    cat <<'EOF'
Usage: ./run_qbox_yocto.sh [options] [-- extra-qbox-runner-options]

Run the apollo-fvp Yocto image on QBox using the Apollo full-system runner.
The tmux panes use the same primary-console-focused split pattern as
run_fvp.sh.

Options:
  --machine NAME              Yocto machine name (default: apollo-fvp)
  --build-dir DIR             Yocto build directory (default: ./build)
  --deploy-dir DIR            Yocto deploy image directory
  --work-dir DIR              Yocto machine work directory
  --image-basename NAME       Yocto image recipe basename (default: nexios-image)
  --local-build-dir DIR       Local-build directory used for QBox build/debug files
  --qbox-build-dir DIR        QBox platform build directory
  --conf FILE                 QBox Lua configuration
  --session NAME              tmux session name
  --out-dir DIR               Runtime output directory
  --si-mode MODE              Safety Island mode (default: live-cl0-cl1)
  --timeout SECONDS           Runner timeout, 0 keeps interactive run alive
  --jobs N                    Build jobs when the QBox runner builds dependencies
  --rootfs-bootargs-profile P Rootfs bootargs profile (default: none)
  --copy-disks                Copy writable rootfs/EFI disks into --out-dir first
  --no-copy-disks             Use Yocto deploy disk images in place (default)
  --legacy-file-backed-sram   Disable RSE SRAM fast-boot DMI accelerator
  --no-attach                 Start tmux session without attaching
  --dry-run                   Print the underlying QBox runner command
  --help                      Show this help

Artifact overrides:
  --rootfs FILE
  --efi-capsule-disk FILE
  --rse-rom FILE
  --rse-flash FILE
  --rse-otp FILE
  --ap-flash FILE
  --ap-bl2-elf FILE
  --rse-bl1-2-elf FILE
  --rse-bl2-elf FILE
  --provisioning-bundle FILE
  --ap-dtb FILE
  --rse-symbols FILE
  --si-cl0-image FILE
  --si-cl1-image FILE
  --si-cl1-symbols FILE

Useful environment variables:
  MACHINE, YOCTO_BUILD_DIR, DEPLOY_DIR, YOCTO_WORK_DIR, IMAGE_BASENAME,
  LOCAL_BUILD_DIR, QBOX_BUILD_DIR, QBOX_CONF, OUT_DIR, TMUX_SESSION,
  SI_MODE, TIMEOUT, JOBS, RUN_QBOX_COPY_DISKS, SSH_PORT
EOF
}

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

resolve_file() {
    local label="$1"
    shift

    local tried=()
    local candidate
    for candidate in "$@"; do
        [[ -n "${candidate}" ]] || continue
        tried+=("${candidate}")
        if [[ -f "${candidate}" ]]; then
            printf '%s\n' "${candidate}"
            return 0
        fi
    done

    {
        echo "missing required ${label}"
        for candidate in "${tried[@]}"; do
            echo "  tried: ${candidate}"
        done
    } >&2
    exit 1
}

resolve_file_with_glob() {
    local label="$1"
    local fixed="$2"
    local pattern="$3"

    if [[ -n "${fixed}" && -f "${fixed}" ]]; then
        printf '%s\n' "${fixed}"
        return 0
    fi

    local latest=""
    if [[ -n "${pattern}" ]]; then
        latest="$(latest_glob "${pattern}" || true)"
    fi
    if [[ -n "${latest}" ]]; then
        printf '%s\n' "${latest}"
        return 0
    fi

    {
        echo "missing required ${label}"
        [[ -n "${fixed}" ]] && echo "  tried: ${fixed}"
        [[ -n "${pattern}" ]] && echo "  tried glob: ${pattern}"
    } >&2
    exit 1
}

copy_sparse() {
    local src="$1"
    local dst="$2"
    mkdir -p "$(dirname "${dst}")"
    cp --reflink=auto --sparse=always "${src}" "${dst}"
}

default_ssh_port_range() {
    local start="${SSH_PORT_START:-8022}"
    local end="${SSH_PORT_END:-8122}"
    local port
    for ((port = start; port <= end; port++)); do
        if ! ss -ltn "( sport = :${port} )" | grep -q ":${port}"; then
            printf '%s\n' "${port}"
            return 0
        fi
    done
    die "no free SSH host port in range ${start}-${end}"
}

reject_removed_env() {
    local removed=(
        QBOX_ENABLE_TESTDEV
        QBOX_GIC_USE_QEMU
        QBOX_RSE_TIMER_MODEL
        QBOX_SOC_UART_MODEL
        QBOX_CC3XX_FAST_RANDOM
    )
    local name
    for name in "${removed[@]}"; do
        if [[ -n "${!name-}" ]]; then
            die "${name} is no longer supported; use the default production-capable QBox models"
        fi
    done
}

default_ap_cpu_count() {
    local local_conf="${YOCTO_BUILD_DIR}/conf/local.conf"
    [[ -f "${local_conf}" ]] || return 1

    sed -nE \
        's/^[[:space:]]*PC_CPUS?_COUNT_DEFAULT[[:space:]]*[?+:.]*=[[:space:]]*"([^"]+)".*/\1/p' \
        "${local_conf}" | tail -n 1
}

validate_ap_cpu_count() {
    local value="$1"

    [[ "${value}" =~ ^[0-9]+$ ]] ||
        die "QBOX_APOLLO_NUM_CPUS must be numeric: ${value}"
    ((value >= 1 && value <= 16)) ||
        die "QBOX_APOLLO_NUM_CPUS must be in range 1..16: ${value}"
}

RUN_STAMP="$(date +%Y%m%d-%H%M%S)"
MACHINE="${MACHINE:-apollo-fvp}"
YOCTO_BUILD_DIR="${YOCTO_BUILD_DIR:-${ROOT_DIR}/build}"
DEPLOY_DIR="${DEPLOY_DIR:-}"
YOCTO_WORK_DIR="${YOCTO_WORK_DIR:-}"
IMAGE_BASENAME="${IMAGE_BASENAME:-nexios-image}"

LOCAL_BUILD_DIR="${LOCAL_BUILD_DIR:-${ROOT_DIR}/build/local-apollo-fvp}"
QBOX_BUILD_DIR="${QBOX_BUILD_DIR:-${QBOX_PLATFORM_BUILD_DIR:-${LOCAL_BUILD_DIR}/work/qbox-platform}}"
QBOX_CONF="${QBOX_CONF:-${ROOT_DIR}/tools/qbox-platform/platforms/apollo/apollo-qvp.lua}"
TMUX_SESSION="${TMUX_SESSION:-apollo-qbox-yocto-${RUN_STAMP}}"
OUT_DIR="${OUT_DIR:-${ROOT_DIR}/build/qbox-apollo-fvp/yocto-${MACHINE}-${RUN_STAMP}}"
SI_MODE="${SI_MODE:-live-cl0-cl1}"
TIMEOUT="${TIMEOUT:-0}"
JOBS="${JOBS:-$(nproc)}"
ROOTFS_BOOTARGS_PROFILE="${ROOTFS_BOOTARGS_PROFILE:-none}"
RUN_QBOX_COPY_DISKS="${RUN_QBOX_COPY_DISKS:-0}"
LEGACY_FILE_BACKED_SRAM="${LEGACY_FILE_BACKED_SRAM:-0}"
NO_ATTACH="${NO_ATTACH:-0}"
DRY_RUN="${DRY_RUN:-0}"
RSE_OTP_IMAGE_SIZE="${RSE_OTP_IMAGE_SIZE:-65536}"

ROOTFS_OVERRIDE="${ROOTFS:-}"
EFI_CAPSULE_DISK_OVERRIDE="${EFI_CAPSULE_DISK:-}"
RSE_ROM_OVERRIDE="${RSE_ROM:-}"
RSE_FLASH_OVERRIDE="${RSE_FLASH:-}"
RSE_OTP_OVERRIDE="${RSE_OTP:-}"
AP_FLASH_OVERRIDE="${AP_FLASH:-}"
AP_BL2_ELF_OVERRIDE="${AP_BL2_ELF:-}"
RSE_BL1_2_ELF_OVERRIDE="${RSE_BL1_2_ELF:-}"
RSE_BL2_ELF_OVERRIDE="${RSE_BL2_ELF:-}"
PROVISIONING_BUNDLE_OVERRIDE="${PROVISIONING_BUNDLE:-}"
AP_DTB_OVERRIDE="${AP_DTB:-}"
RSE_SYMBOLS_OVERRIDE="${RSE_SYMBOLS:-}"
SI_CL0_IMAGE_OVERRIDE="${SI_CL0_IMAGE:-}"
SI_CL1_IMAGE_OVERRIDE="${SI_CL1_IMAGE:-}"
SI_CL1_SYMBOLS_OVERRIDE="${SI_CL1_SYMBOLS:-}"

TMUX_RUNNER_ARGS=()
EXTRA_CHILD_ARGS=()

while (($#)); do
    case "$1" in
        --help|-h)
            usage
            exit 0
            ;;
        --machine)
            [[ $# -ge 2 ]] || die "--machine requires a value"
            MACHINE="$2"
            shift 2
            ;;
        --build-dir)
            [[ $# -ge 2 ]] || die "--build-dir requires a value"
            YOCTO_BUILD_DIR="$2"
            shift 2
            ;;
        --deploy-dir)
            [[ $# -ge 2 ]] || die "--deploy-dir requires a value"
            DEPLOY_DIR="$2"
            shift 2
            ;;
        --work-dir)
            [[ $# -ge 2 ]] || die "--work-dir requires a value"
            YOCTO_WORK_DIR="$2"
            shift 2
            ;;
        --image-basename)
            [[ $# -ge 2 ]] || die "--image-basename requires a value"
            IMAGE_BASENAME="$2"
            shift 2
            ;;
        --local-build-dir)
            [[ $# -ge 2 ]] || die "--local-build-dir requires a value"
            LOCAL_BUILD_DIR="$2"
            shift 2
            ;;
        --qbox-build-dir)
            [[ $# -ge 2 ]] || die "--qbox-build-dir requires a value"
            QBOX_BUILD_DIR="$2"
            shift 2
            ;;
        --conf)
            [[ $# -ge 2 ]] || die "--conf requires a value"
            QBOX_CONF="$2"
            shift 2
            ;;
        --session)
            [[ $# -ge 2 ]] || die "--session requires a value"
            TMUX_SESSION="$2"
            shift 2
            ;;
        --out-dir)
            [[ $# -ge 2 ]] || die "--out-dir requires a value"
            OUT_DIR="$2"
            shift 2
            ;;
        --si-mode)
            [[ $# -ge 2 ]] || die "--si-mode requires a value"
            SI_MODE="$2"
            shift 2
            ;;
        --timeout)
            [[ $# -ge 2 ]] || die "--timeout requires a value"
            TIMEOUT="$2"
            shift 2
            ;;
        --jobs)
            [[ $# -ge 2 ]] || die "--jobs requires a value"
            JOBS="$2"
            shift 2
            ;;
        --rootfs-bootargs-profile)
            [[ $# -ge 2 ]] || die "--rootfs-bootargs-profile requires a value"
            ROOTFS_BOOTARGS_PROFILE="$2"
            shift 2
            ;;
        --copy-disks)
            RUN_QBOX_COPY_DISKS=1
            shift
            ;;
        --no-copy-disks)
            RUN_QBOX_COPY_DISKS=0
            shift
            ;;
        --legacy-file-backed-sram)
            LEGACY_FILE_BACKED_SRAM=1
            shift
            ;;
        --no-attach)
            NO_ATTACH=1
            shift
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --rootfs)
            [[ $# -ge 2 ]] || die "--rootfs requires a value"
            ROOTFS_OVERRIDE="$2"
            shift 2
            ;;
        --efi-capsule-disk)
            [[ $# -ge 2 ]] || die "--efi-capsule-disk requires a value"
            EFI_CAPSULE_DISK_OVERRIDE="$2"
            shift 2
            ;;
        --rse-rom)
            [[ $# -ge 2 ]] || die "--rse-rom requires a value"
            RSE_ROM_OVERRIDE="$2"
            shift 2
            ;;
        --rse-flash)
            [[ $# -ge 2 ]] || die "--rse-flash requires a value"
            RSE_FLASH_OVERRIDE="$2"
            shift 2
            ;;
        --rse-otp)
            [[ $# -ge 2 ]] || die "--rse-otp requires a value"
            RSE_OTP_OVERRIDE="$2"
            shift 2
            ;;
        --ap-flash)
            [[ $# -ge 2 ]] || die "--ap-flash requires a value"
            AP_FLASH_OVERRIDE="$2"
            shift 2
            ;;
        --ap-bl2-elf)
            [[ $# -ge 2 ]] || die "--ap-bl2-elf requires a value"
            AP_BL2_ELF_OVERRIDE="$2"
            shift 2
            ;;
        --rse-bl1-2-elf)
            [[ $# -ge 2 ]] || die "--rse-bl1-2-elf requires a value"
            RSE_BL1_2_ELF_OVERRIDE="$2"
            shift 2
            ;;
        --rse-bl2-elf)
            [[ $# -ge 2 ]] || die "--rse-bl2-elf requires a value"
            RSE_BL2_ELF_OVERRIDE="$2"
            shift 2
            ;;
        --provisioning-bundle)
            [[ $# -ge 2 ]] || die "--provisioning-bundle requires a value"
            PROVISIONING_BUNDLE_OVERRIDE="$2"
            shift 2
            ;;
        --ap-dtb)
            [[ $# -ge 2 ]] || die "--ap-dtb requires a value"
            AP_DTB_OVERRIDE="$2"
            shift 2
            ;;
        --rse-symbols)
            [[ $# -ge 2 ]] || die "--rse-symbols requires a value"
            RSE_SYMBOLS_OVERRIDE="$2"
            shift 2
            ;;
        --si-cl0-image)
            [[ $# -ge 2 ]] || die "--si-cl0-image requires a value"
            SI_CL0_IMAGE_OVERRIDE="$2"
            shift 2
            ;;
        --si-cl1-image)
            [[ $# -ge 2 ]] || die "--si-cl1-image requires a value"
            SI_CL1_IMAGE_OVERRIDE="$2"
            shift 2
            ;;
        --si-cl1-symbols)
            [[ $# -ge 2 ]] || die "--si-cl1-symbols requires a value"
            SI_CL1_SYMBOLS_OVERRIDE="$2"
            shift 2
            ;;
        --enable-test-device|--use-qemu-gic|--rse-qemu-timer|--soc-uart-qemu|--cc3xx-fast-random|--mock-cc3xx)
            die "$1 is no longer supported; use the default production-capable QBox models"
            ;;
        --)
            shift
            EXTRA_CHILD_ARGS+=("$@")
            break
            ;;
        *)
            TMUX_RUNNER_ARGS+=("$1")
            shift
            ;;
    esac
done

reject_removed_env

WORK_PREFIX="$(machine_to_work_prefix "${MACHINE}")"
DEPLOY_DIR="${DEPLOY_DIR:-${YOCTO_BUILD_DIR}/tmp_baremetal/deploy/images/${MACHINE}}"
YOCTO_WORK_DIR="${YOCTO_WORK_DIR:-${YOCTO_BUILD_DIR}/tmp_baremetal/work/${WORK_PREFIX}-poky-linux}"

[[ -d "${DEPLOY_DIR}" ]] || die "Yocto deploy directory not found: ${DEPLOY_DIR}"
[[ -d "${YOCTO_WORK_DIR}" ]] || die "Yocto work directory not found: ${YOCTO_WORK_DIR}"
[[ -d "${LOCAL_BUILD_DIR}" ]] || die "local build directory not found: ${LOCAL_BUILD_DIR}. Build QBox first with ./local-build.sh qbox or set --local-build-dir."
[[ -f "${QBOX_CONF}" ]] || die "QBox config not found: ${QBOX_CONF}"
[[ -d "${QBOX_BUILD_DIR}" ]] || die "QBox build directory not found: ${QBOX_BUILD_DIR}. Build QBox first with ./local-build.sh qbox or set --qbox-build-dir."

QBOX_APOLLO_NUM_CPUS="${QBOX_APOLLO_NUM_CPUS:-$(default_ap_cpu_count || true)}"
QBOX_APOLLO_NUM_CPUS="${QBOX_APOLLO_NUM_CPUS:-4}"
validate_ap_cpu_count "${QBOX_APOLLO_NUM_CPUS}"
export QBOX_APOLLO_NUM_CPUS

ROOTFS="$(resolve_file_with_glob \
    "Yocto rootfs WIC image" \
    "${ROOTFS_OVERRIDE:-${DEPLOY_DIR}/${IMAGE_BASENAME}-${MACHINE}.wic}" \
    "${DEPLOY_DIR}/${IMAGE_BASENAME}-${MACHINE}-*.wic")"
EFI_CAPSULE_DISK="$(resolve_file \
    "EFI capsule update disk" \
    "${EFI_CAPSULE_DISK_OVERRIDE:-${DEPLOY_DIR}/efi-capsule-update-disk-image-${MACHINE}.img}" \
    "${DEPLOY_DIR}/efi-capsule-update-disk-image-fvp-rd-aspen.img")"
RSE_ROM="$(resolve_file \
    "RSE ROM image" \
    "${RSE_ROM_OVERRIDE:-${DEPLOY_DIR}/rse-rom-image.img}")"
RSE_FLASH="$(resolve_file \
    "RSE flash image" \
    "${RSE_FLASH_OVERRIDE:-${DEPLOY_DIR}/rse-flash-image.img}")"
RSE_OTP="$(resolve_file \
    "RSE OTP image" \
    "${RSE_OTP_OVERRIDE:-${DEPLOY_DIR}/rse-otp-image.img}")"
AP_FLASH="$(resolve_file \
    "AP flash image" \
    "${AP_FLASH_OVERRIDE:-${DEPLOY_DIR}/ap-flash-image.img}")"
AP_BL2_ELF="$(resolve_file_with_glob \
    "AP TF-A BL2 ELF" \
    "${AP_BL2_ELF_OVERRIDE:-${DEPLOY_DIR}/bl2.elf}" \
    "${YOCTO_WORK_DIR}/trusted-firmware-a/*/build/${WORK_PREFIX}/debug/bl2/bl2.elf")"
RSE_BL1_2_ELF="$(resolve_file_with_glob \
    "RSE TF-M BL1_2 ELF" \
    "${RSE_BL1_2_ELF_OVERRIDE}" \
    "${YOCTO_WORK_DIR}/trusted-firmware-m/*/build/bin/bl1_2.elf")"
RSE_BL2_ELF="$(resolve_file_with_glob \
    "RSE TF-M BL2 ELF" \
    "${RSE_BL2_ELF_OVERRIDE}" \
    "${YOCTO_WORK_DIR}/trusted-firmware-m/*/build/bin/bl2.elf")"
PROVISIONING_BUNDLE="$(resolve_file \
    "combined provisioning bundle" \
    "${PROVISIONING_BUNDLE_OVERRIDE:-${DEPLOY_DIR}/combined_provisioning_message.bin}")"
AP_DTB="$(resolve_file \
    "AP device tree" \
    "${AP_DTB_OVERRIDE:-${DEPLOY_DIR}/${MACHINE}.dtb}")"
RSE_SYMBOLS="$(resolve_file \
    "QBox RSE debug symbol manifest" \
    "${RSE_SYMBOLS_OVERRIDE:-${LOCAL_BUILD_DIR}/debug/symbols.json}")"
SI_CL0_IMAGE="$(resolve_file \
    "Safety Island CL0 SCP image" \
    "${SI_CL0_IMAGE_OVERRIDE:-${DEPLOY_DIR}/si0_ramfw.bin}")"
SI_CL1_IMAGE="$(resolve_file \
    "Safety Island CL1 Zephyr image" \
    "${SI_CL1_IMAGE_OVERRIDE:-${DEPLOY_DIR}/zephyr-demos-cl1.bin}")"
SI_CL1_SYMBOLS="$(resolve_file \
    "Safety Island CL1 Zephyr symbols" \
    "${SI_CL1_SYMBOLS_OVERRIDE:-${DEPLOY_DIR}/zephyr-demos-cl1.elf}")"

RUN_ROOTFS="${ROOTFS}"
RUN_EFI_CAPSULE_DISK="${EFI_CAPSULE_DISK}"
RUN_RSE_OTP="${RSE_OTP}"
if [[ "${RUN_QBOX_COPY_DISKS}" == "1" ]]; then
    RUN_ROOTFS="${OUT_DIR}/input-images/$(basename "${ROOTFS}")"
    RUN_EFI_CAPSULE_DISK="${OUT_DIR}/input-images/$(basename "${EFI_CAPSULE_DISK}")"
    if [[ "${DRY_RUN}" == "0" ]]; then
        copy_sparse "${ROOTFS}" "${RUN_ROOTFS}"
        copy_sparse "${EFI_CAPSULE_DISK}" "${RUN_EFI_CAPSULE_DISK}"
    fi
fi
if [[ -z "${RSE_OTP_OVERRIDE}" && ! -s "${RSE_OTP}" ]]; then
    RUN_RSE_OTP="${OUT_DIR}/input-images/$(basename "${RSE_OTP}")"
    if [[ "${DRY_RUN}" == "0" ]]; then
        python3 "${ROOT_DIR}/scripts/setup/provision_rse_otp_image.py" \
            --root "${ROOT_DIR}" \
            --tfm-build-dir "$(cd "$(dirname "${RSE_BL2_ELF}")/.." && pwd)" \
            --output "${RUN_RSE_OTP}" \
            --size "${RSE_OTP_IMAGE_SIZE}"
    fi
fi

SSH_PORT_VALUE="${SSH_PORT:-$(default_ssh_port_range)}"
NETDEV="type=user,hostfwd=tcp::${SSH_PORT_VALUE}-:22"

RSE_FAST_BOOT_MODE="--rse-fast-boot-sram-dmi"
if [[ "${LEGACY_FILE_BACKED_SRAM}" != "0" ]]; then
    RSE_FAST_BOOT_MODE="--rse-fast-boot-aliases"
fi

QBOX_ACCEL_ARGS=(
    --rse-hotpath-accel
    --rse-lms-accel
    "${RSE_FAST_BOOT_MODE}"
    --rse-bl2-libc-hotpath
    --rse-bl2-delay-accel
    --rse-bl2-load-accel
    --rse-bl2-boot-enc-accel
    --rse-bl2-img-hash-accel
    --rse-bl2-verify-sig-accel
)

RUNNER_CMD=(
    "${ROOT_DIR}/scripts/run/run_qbox_apollo_fvp_full_tmux.sh"
    --session "${TMUX_SESSION}"
    --out-dir "${OUT_DIR}"
    --local-build-dir "${LOCAL_BUILD_DIR}"
    --qbox-build-dir "${QBOX_BUILD_DIR}"
    --conf "${QBOX_CONF}"
    --si-mode "${SI_MODE}"
    --timeout "${TIMEOUT}"
    --jobs "${JOBS}"
    --skip-build
    --post-login-probe
    --keep-running-after-pass
    --rootfs-bootargs-profile "${ROOTFS_BOOTARGS_PROFILE}"
    --qbox-performance-preset
    --cc3xx-qemu-native-backend
    --netdev "${NETDEV}"
    --tmux-layout fvp-like
)

if [[ "${NO_ATTACH}" == "1" ]]; then
    RUNNER_CMD+=(--no-attach)
fi
if [[ "${DRY_RUN}" == "1" ]]; then
    RUNNER_CMD+=(--dry-run)
fi
RUNNER_CMD+=("${TMUX_RUNNER_ARGS[@]}")
RUNNER_CMD+=(
    --
    --rse-rom "${RSE_ROM}"
    --rse-flash "${RSE_FLASH}"
    --rse-otp "${RUN_RSE_OTP}"
    --ap-flash "${AP_FLASH}"
    --ap-bl2-elf "${AP_BL2_ELF}"
    --rse-bl1-2-elf "${RSE_BL1_2_ELF}"
    --rse-bl2-elf "${RSE_BL2_ELF}"
    --rootfs "${RUN_ROOTFS}"
    --efi-capsule-disk "${RUN_EFI_CAPSULE_DISK}"
    --provisioning-bundle "${PROVISIONING_BUNDLE}"
    --ap-dtb "${AP_DTB}"
    --rse-symbols "${RSE_SYMBOLS}"
    --si-cl0-image "${SI_CL0_IMAGE}"
    --si-cl1-image "${SI_CL1_IMAGE}"
    --si-cl1-symbols "${SI_CL1_SYMBOLS}"
)
RUNNER_CMD+=("${QBOX_ACCEL_ARGS[@]}")
RUNNER_CMD+=("${EXTRA_CHILD_ARGS[@]}")

cat <<EOF
Apollo QBox Yocto launch
  machine:       ${MACHINE}
  deploy dir:    ${DEPLOY_DIR}
  work dir:      ${YOCTO_WORK_DIR}
  output dir:    ${OUT_DIR}
  session:       ${TMUX_SESSION}
  qbox conf:     ${QBOX_CONF}
  ap cpus:       ${QBOX_APOLLO_NUM_CPUS}
  rootfs:        ${RUN_ROOTFS}
  efi disk:      ${RUN_EFI_CAPSULE_DISK}
  rse otp:       ${RUN_RSE_OTP}
  ssh port:      ${SSH_PORT_VALUE}
EOF

exec "${RUNNER_CMD[@]}"
