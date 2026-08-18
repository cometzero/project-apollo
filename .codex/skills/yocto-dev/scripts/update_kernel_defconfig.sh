#!/usr/bin/env bash

set -euo pipefail

APOLLO_MACHINE="${MACHINE:-apollo-qvp}"
KERNEL_CONFIG_REQUESTS=("$@")

case "${APOLLO_MACHINE}" in
    apollo-fvp|apollo-qvp)
        ;;
    *)
        echo "error: MACHINE must be apollo-fvp or apollo-qvp" >&2
        exit 2
        ;;
esac

if ((${#KERNEL_CONFIG_REQUESTS[@]} == 0)); then
    echo "usage: update_kernel_defconfig.sh CONFIG_NAME=y|m|n [...]" >&2
    exit 2
fi

command -v bitbake >/dev/null || {
    echo "error: enter the Yocto environment with oe-init-build-env first" >&2
    exit 2
}
[[ -f conf/bblayers.conf ]] || {
    echo "error: run from the initialized Yocto build directory" >&2
    exit 2
}

normalized_requests=()
for request in "${KERNEL_CONFIG_REQUESTS[@]}"; do
    if [[ ! "${request}" =~ ^(CONFIG_[A-Z0-9_]+)=(y|m|n)$ ]]; then
        echo "error: invalid kernel config '${request}'" >&2
        exit 2
    fi
    symbol="${BASH_REMATCH[1]}"
    for existing in "${normalized_requests[@]}"; do
        if [[ "${existing%%=*}" == "${symbol}" ]]; then
            echo "error: duplicate kernel config '${symbol}'" >&2
            exit 2
        fi
    done
    normalized_requests+=("${request}")
done
KERNEL_CONFIG_REQUESTS=("${normalized_requests[@]}")

MACHINE="${APOLLO_MACHINE}" bitbake virtual/kernel -c defconfig -f

host_path="${PATH}"
env_assignments="$(
    MACHINE="${APOLLO_MACHINE}" bitbake -e virtual/kernel |
        sed -n -E '/^(export )?(S|B|ARCH|PATH|CFLAGS|TOOLCHAIN_OPTIONS|BUILD_CC|BUILD_CPP|BUILD_CFLAGS|BUILD_LDFLAGS|KERNEL_CC|KERNEL_LD|KERNEL_OBJCOPY|KERNEL_STRIP|APOLLO_KERNEL_DEFCONFIG_PATH)=/p'
)"

S='' B='' ARCH='' CFLAGS='' TOOLCHAIN_OPTIONS=''
BUILD_CC='' BUILD_CPP='' BUILD_CFLAGS='' BUILD_LDFLAGS=''
KERNEL_CC='' KERNEL_LD='' KERNEL_OBJCOPY='' KERNEL_STRIP=''
APOLLO_KERNEL_DEFCONFIG_PATH=''
eval "${env_assignments}"

kernel_s="${S}"
kernel_b="${B}"
kernel_arch="${ARCH}"
kernel_path="${PATH}"
PATH="${host_path}"
kernel_defconfig="${APOLLO_KERNEL_DEFCONFIG_PATH}"

[[ -x "${kernel_s}/scripts/config" ]] || {
    echo "error: missing ${kernel_s}/scripts/config" >&2
    exit 1
}
[[ -f "${kernel_b}/.config" ]] || {
    echo "error: missing ${kernel_b}/.config" >&2
    exit 1
}
[[ "${kernel_defconfig}" == "${kernel_s}/"* ]] || {
    echo "error: defconfig is outside the kernel source" >&2
    exit 1
}

kernel_defconfig_rel="${kernel_defconfig#"${kernel_s}/"}"
if [[ -n "$(git -C "${kernel_s}" status --short -- "${kernel_defconfig_rel}")" ]]; then
    echo "error: kernel defconfig already has changes: ${kernel_defconfig}" >&2
    exit 1
fi

install -m 0644 "${kernel_b}/.config" "${kernel_b}/.config.skill-base"

for request in "${KERNEL_CONFIG_REQUESTS[@]}"; do
    symbol="${request%%=*}"
    value="${request#*=}"
    if ! rg -q "^[[:space:]]*(menu)?config[[:space:]]+${symbol#CONFIG_}([[:space:]]|$)" \
        "${kernel_s}" --glob 'Kconfig*'; then
        echo "error: unknown kernel config symbol '${symbol}'" >&2
        exit 1
    fi
    case "${value}" in
        y) action="--enable" ;;
        m) action="--module" ;;
        n) action="--disable" ;;
    esac
    "${kernel_s}/scripts/config" --file "${kernel_b}/.config" \
        "${action}" "${symbol}"
done

kernel_make() {
    env PATH="${kernel_path}" \
        make -C "${kernel_s}" O="${kernel_b}" \
            "ARCH=${kernel_arch}" \
            "CFLAGS=${CFLAGS} ${TOOLCHAIN_OPTIONS}" \
            "HOSTCC=${BUILD_CC} ${BUILD_CFLAGS} ${BUILD_LDFLAGS}" \
            "HOSTCPP=${BUILD_CPP}" \
            "CC=${KERNEL_CC}" \
            "LD=${KERNEL_LD}" \
            "OBJCOPY=${KERNEL_OBJCOPY}" \
            "STRIP=${KERNEL_STRIP}" \
            "$@"
}

verify_requests() {
    local actual expected request symbol

    for request in "${KERNEL_CONFIG_REQUESTS[@]}"; do
        symbol="${request%%=*}"
        expected="${request#*=}"
        actual="$(
            "${kernel_s}/scripts/config" --file "${kernel_b}/.config" \
                --state "${symbol}"
        )"
        case "${expected}:${actual}" in
            y:y|m:m|n:n|n:undef)
                ;;
            *)
                printf 'error: %s requested=%s resolved=%s\n' \
                    "${symbol}" "${expected}" "${actual}" >&2
                return 1
                ;;
        esac
    done
}

verify_project_invariants() {
    local actual symbol

    for symbol in CONFIG_BLK_DEV_INITRD CONFIG_RD_GZIP; do
        actual="$(
            "${kernel_s}/scripts/config" --file "${kernel_b}/.config" \
                --state "${symbol}"
        )"
        if [[ "${actual}" != "y" ]]; then
            printf 'error: project invariant %s resolved=%s\n' \
                "${symbol}" "${actual}" >&2
            return 1
        fi
    done
}

kernel_make olddefconfig
verify_requests
verify_project_invariants
"${kernel_s}/scripts/diffconfig" "${kernel_b}/.config.skill-base" \
    "${kernel_b}/.config" >"${kernel_b}/skill-kernel-diff.txt"

kernel_make savedefconfig
candidate="${kernel_b}/defconfig"
[[ -f "${candidate}" ]] || {
    echo "error: savedefconfig did not create ${candidate}" >&2
    exit 1
}
if ! rg -q '^CONFIG_RD_GZIP=y$' "${candidate}"; then
    sed -i '/^CONFIG_BLK_DEV_INITRD=y$/a CONFIG_RD_GZIP=y' "${candidate}"
fi

backup="$(mktemp "${kernel_b}/apollo-defconfig.backup.XXXXXX")"
install -m 0644 "${kernel_defconfig}" "${backup}"
install -m 0644 "${candidate}" "${kernel_defconfig}"
rm -f -- "${candidate}"

if ! MACHINE="${APOLLO_MACHINE}" bitbake virtual/kernel -c defconfig -f ||
    ! verify_requests || ! verify_project_invariants; then
    install -m 0644 "${backup}" "${kernel_defconfig}"
    rm -f -- "${backup}"
    echo "error: regenerated config failed; restored the original" >&2
    exit 1
fi
rm -f -- "${backup}"

echo "updated ${kernel_defconfig}"
git -C "${kernel_s}" diff -- "${kernel_defconfig_rel}"
