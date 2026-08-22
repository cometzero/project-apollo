#!/usr/bin/env bash

set -euo pipefail

readonly BEGIN_MARKER="# BEGIN APOLLO MBPP 16-CPU"
readonly END_MARKER="# END APOLLO MBPP 16-CPU"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
readonly ROOT_DIR

die() {
    echo "error: $*" >&2
    exit 64
}

if [[ $# -ne 1 ]]; then
    die "build path must be exactly build/validation/apollo-fvp-16 or build/validation/apollo-qvp-16"
fi

case "$1" in
    build/validation/apollo-fvp-16)
        validation_machine="apollo-fvp"
        ;;
    build/validation/apollo-qvp-16)
        validation_machine="apollo-qvp"
        ;;
    *)
        die "build path must be exactly build/validation/apollo-fvp-16 or build/validation/apollo-qvp-16"
        ;;
esac

readonly validation_build_dir="${ROOT_DIR}/$1"
readonly template_dir="${ROOT_DIR}/hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/${validation_machine}"
readonly init_script="${ROOT_DIR}/layers/poky/oe-init-build-env"

for path in "${ROOT_DIR}/build" "${ROOT_DIR}/build/validation" "${validation_build_dir}"; do
    [[ ! -L "${path}" ]] || die "validation build path must not contain a symlink: ${path}"
done
[[ -f "${init_script}" ]] || die "missing Yocto environment initializer: ${init_script}"
[[ -d "${template_dir}" ]] || die "missing machine template: ${template_dir}"

mkdir -p -- "${validation_build_dir}"
[[ "$(realpath -m -- "${validation_build_dir}")" == "${validation_build_dir}" ]] ||
    die "validation build path resolved outside the canonical target"

export TEMPLATECONF="${template_dir}"
set +u
# shellcheck source=/dev/null
source "${init_script}" "${validation_build_dir}" >/dev/null
set -u
cd "${ROOT_DIR}"

readonly local_conf="${validation_build_dir}/conf/local.conf"
readonly bblayers_conf="${validation_build_dir}/conf/bblayers.conf"
[[ -f "${local_conf}" ]] || die "missing initialized local.conf: ${local_conf}"
[[ -f "${bblayers_conf}" ]] || die "missing initialized bblayers.conf: ${bblayers_conf}"

begin_count="$(grep -Fxc "${BEGIN_MARKER}" "${local_conf}" || true)"
end_count="$(grep -Fxc "${END_MARKER}" "${local_conf}" || true)"
[[ "${begin_count}" == "${end_count}" ]] ||
    die "unbalanced MBPP managed block in ${local_conf}"
((begin_count <= 1)) || die "duplicate MBPP managed block in ${local_conf}"

tmp_conf="$(mktemp "${local_conf}.XXXXXX")"
trap 'rm -f -- "${tmp_conf}"' EXIT
awk \
    -v begin="${BEGIN_MARKER}" \
    -v end="${END_MARKER}" \
    -v machine="${validation_machine}" \
    -v downloads="${ROOT_DIR}/build/downloads" \
    -v sstate="${ROOT_DIR}/build/sstate-cache" \
    '
    $0 == begin { managed = 1; next }
    $0 == end { managed = 0; next }
    !managed { print }
    END {
        print begin
        print "MACHINE = \"" machine "\""
        print "RD_ASPEN_VARIANT = \"cfg2\""
        print "PC_CPUS_COUNT_DEFAULT = \"16\""
        print "TMPDIR = \"${TOPDIR}/tmp_mbpp16\""
        print "DL_DIR = \"" downloads "\""
        print "SSTATE_DIR = \"" sstate "\""
        print end
    }
    ' "${local_conf}" >"${tmp_conf}"
chmod --reference="${local_conf}" "${tmp_conf}"
mv -- "${tmp_conf}" "${local_conf}"
trap - EXIT

echo "initialized ${validation_machine} MBPP validation build: $1"
