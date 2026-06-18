#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

die()
{
    printf 'error: %s\n' "$*" >&2
    exit 1
}

usage()
{
    cat <<'EOF'
Usage: ./local-build.sh [command]

Default command: build

Commands:
  all       Build/install SDK if needed and build local images.
  sdk       Build and install the Yocto SDK under build/local-sdk.
  qbox      Build the QBox targets required by Apollo full-system boot.
  build     Build local TF-M/SCP/Zephyr/OP-TEE/U-Boot/TF-A/Linux/Buildroot images.
  zephyr    Build only the local Safety Island CL1 Zephyr image.
  package   Package built local images for QBox execution.
  clean     Remove build/local-apollo-fvp.

Useful overrides:
  SDK_DIR=/path/to/sdk LOCAL_BUILD_DIR=/path/to/output QBOX_PLATFORM_BUILD_DIR=/path/to/qbox-platform-build JOBS=16 ./local-build.sh all
  QBOX_BUILD_DIR=/path/to/qbox-platform-build ./local-build.sh qbox
  QBOX_CORE_DIR=/path/to/qbox QBOX_PLATFORM_DIR=/path/to/qbox-platform ./local-build.sh qbox
  ZEPHYR_SDK_INSTALL_DIR=/path/to/zephyr-sdk ./local-build.sh zephyr
  SAFETY_ISLAND_CL1_BIN=/path/to/zephyr-demos-cl1.bin ./local-build.sh build
  LINUX_DEFCONFIG=apollo_fvp_defconfig ./local-build.sh build
  LINUX_CONFIG=/path/to/.config ./local-build.sh build
  KERNEL_MODULES_AUTOLOAD="bridge virtio_rpmsg_bus rpmsg_net arm_si_rproc pfdi_misc" ./local-build.sh build
  KERNEL_DEBUG_INFO=0 ./local-build.sh build
  RSE_OTP_RESET=1 ./local-build.sh build
  RSE_OTP_HOST_PROVISION=0 RSE_OTP_RESET=1 ./local-build.sh build
EOF
}

run_build_script()
{
    local script="$1"
    shift
    exec "${ROOT_DIR}/scripts/build/${script}" "$@"
}

main()
{
    local cmd="${1:-build}"
    if (($# > 0)); then
        shift
    fi

    case "${cmd}" in
        all)
            run_build_script build_all.sh "$@"
            ;;
        sdk)
            run_build_script build_sdk.sh "$@"
            ;;
        qbox)
            run_build_script build_qbox.sh "$@"
            ;;
        build)
            run_build_script build_images.sh "$@"
            ;;
        zephyr)
            run_build_script build_zephyr.sh "$@"
            ;;
        package)
            exec "${ROOT_DIR}/scripts/package.sh" "$@"
            ;;
        clean)
            run_build_script build_clean.sh "$@"
            ;;
        -h|--help|help)
            usage
            ;;
        *)
            usage >&2
            die "unknown command: ${cmd}"
            ;;
    esac
}

main "$@"
