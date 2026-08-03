#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
QEMU_SOURCE="${ROOT_DIR}/hsoc-stack/tools/qemu"
BUILD_DIR="${ROOT_DIR}/build/qemu-gic720ae-qtest"
SUPPORTED_TESTS=(
    arm-gicv3-baseline
    arm-gicv3-ext-range-cpuif
    arm-gicv3-ext-range-gpio-delivery
    arm-gicv3-eppi
    arm-gicv3-espi
    arm-gicv3-ext-range-gpio-abi
    arm-gicv3-ext-range-vmstate
    arm-gicv4-1-vpendbaser
    arm-gicv4-1-its-vpe
    arm-gicv4-1-direct-lpi
)
declare -A EXPECTED_TAP_PLANS=(
    [arm-gicv3-baseline]=3
    [arm-gicv3-ext-range-cpuif]=22
    [arm-gicv3-ext-range-gpio-delivery]=7
    [arm-gicv3-eppi]=17
    [arm-gicv3-espi]=13
    [arm-gicv3-ext-range-gpio-abi]=5
    [arm-gicv3-ext-range-vmstate]=10
    [arm-gicv4-1-vpendbaser]=7
    [arm-gicv4-1-its-vpe]=5
    [arm-gicv4-1-direct-lpi]=6
)
CONFIGURE_ARGS=(
    --target-list=aarch64-softmmu
    --without-default-features
    --disable-download
    --disable-docs
    --disable-tools
    --disable-guest-agent
    --disable-werror
)

usage() {
    printf 'Usage: %s --list | --test TEST [--test TEST ...]\n' "${0##*/}"
}

list_tests() {
    printf '%s\n' "${SUPPORTED_TESTS[@]}"
}

die_usage() {
    printf 'error: %s\nCandidates:\n' "$1" >&2
    list_tests >&2
    exit 2
}

TEST_NAMES=()
while (($#)); do
    case "$1" in
        --list)
            ((${#TEST_NAMES[@]} == 0 && $# == 1)) || {
                usage >&2
                exit 2
            }
            list_tests
            exit 0
            ;;
        --test)
            (($# >= 2)) || die_usage "missing test name after --test"
            TEST_NAMES+=("$2")
            shift 2
            ;;
        *)
            usage >&2
            exit 2
            ;;
    esac
done

((${#TEST_NAMES[@]} > 0)) || {
    usage >&2
    exit 2
}

declare -A SELECTED_TESTS=()
for test_name in "${TEST_NAMES[@]}"; do
    TEST_SUPPORTED=0
    for candidate in "${SUPPORTED_TESTS[@]}"; do
        if [[ "${test_name}" == "${candidate}" ]]; then
            TEST_SUPPORTED=1
            break
        fi
    done
    ((TEST_SUPPORTED == 1)) || die_usage "unsupported test: ${test_name}"
    [[ -z "${SELECTED_TESTS[${test_name}]+x}" ]] ||
        die_usage "duplicate test: ${test_name}"
    SELECTED_TESTS["${test_name}"]=1
done

QEMU_SOURCE="$(realpath -e "${QEMU_SOURCE}")"
QEMU_TOP="$(realpath -e "$(git -C "${QEMU_SOURCE}" rev-parse --show-toplevel)")"
[[ "${QEMU_SOURCE}" == "${QEMU_TOP}" ]] ||
    die_usage "local QEMU source identity mismatch: ${QEMU_SOURCE}"
MESON_WHEEL="${QEMU_SOURCE}/python/wheels/meson-1.10.0-py3-none-any.whl"
MESON_WRAP_LOCK="${QEMU_SOURCE}/subprojects/.wraplock"
MESON_WRAP_LOCK_PREEXISTED=0
PYTHON_BINARY="$(command -v python3)"
[[ -f "${MESON_WHEEL}" ]] ||
    die_usage "local QEMU Meson wheel is missing: ${MESON_WHEEL}"
[[ -e "${MESON_WRAP_LOCK}" ]] && MESON_WRAP_LOCK_PREEXISTED=1

mkdir -p "${BUILD_DIR}"
exec 9>"${BUILD_DIR}/.lock"
flock --wait 600 9 || {
    printf 'error: timed out waiting for build lock: %s\n' "${BUILD_DIR}/.lock" >&2
    exit 1
}

EVIDENCE_DIR="${BUILD_DIR}/evidence/$(IFS=__ ; printf '%s' "${TEST_NAMES[*]}")"
mkdir -p "${EVIDENCE_DIR}"
SOURCE_MARKER="${BUILD_DIR}/.qemu-source-path"
if [[ -f "${SOURCE_MARKER}" ]]; then
    [[ "$(<"${SOURCE_MARKER}")" == "${QEMU_SOURCE}" ]] || {
        printf 'error: build cache belongs to a different QEMU source\n' >&2
        exit 1
    }
elif find "${BUILD_DIR}" -mindepth 1 -maxdepth 1 \
        ! -name .lock ! -name evidence -print -quit | grep -q .; then
    printf 'error: refusing untrusted pre-existing QEMU build cache\n' >&2
    exit 1
else
    printf '%s\n' "${QEMU_SOURCE}" >"${SOURCE_MARKER}"
fi

TOOLING_BIN="${BUILD_DIR}/tooling/bin"
MESON_WRAPPER="${TOOLING_BIN}/meson"
mkdir -p "${TOOLING_BIN}"
{
    printf '#!/usr/bin/env bash\n'
    printf 'exec env PYTHONPATH=%q %q -m mesonbuild.mesonmain "$@"\n' \
        "${MESON_WHEEL}" "${PYTHON_BINARY}"
} >"${MESON_WRAPPER}"
chmod 0755 "${MESON_WRAPPER}"

QEMU_SHA="$(git -C "${QEMU_SOURCE}" rev-parse HEAD)"
QTEST_LIBRARY_SOURCE="${QEMU_SOURCE}/tests/qtest/libqtest.c"
QEMU_BINARY="${BUILD_DIR}/qemu-system-aarch64"
QTEST_LIBRARY="${BUILD_DIR}/tests/qtest/libqos/libqos.a.p"
COMMAND_RESULTS="${EVIDENCE_DIR}/command-results.tsv"
FINAL_STATUS="fail"
ACTIVE_STEP_PID=""

on_exit() {
    local exit_code=$?

    if ((MESON_WRAP_LOCK_PREEXISTED == 0)) &&
            ! rm -f -- "${MESON_WRAP_LOCK}"; then
        printf 'error: failed to remove Meson source-tree lock: %s\n' \
            "${MESON_WRAP_LOCK}" >&2
        FINAL_STATUS="fail"
        if ((exit_code == 0)); then
            exit_code=1
        fi
    fi
    {
        printf 'status=%s\n' "${FINAL_STATUS}"
        printf 'exit_code=%d\n' "${exit_code}"
        printf 'test_names=%s\n' "${TEST_NAMES[*]}"
        printf 'qemu_sha=%s\n' "${QEMU_SHA}"
        printf 'qemu_binary=%s\n' "${QEMU_BINARY}"
    } >"${EVIDENCE_DIR}/result.txt"
    trap - EXIT
    exit "${exit_code}"
}

trap on_exit EXIT

on_signal() {
    local exit_code="$1"

    trap - INT TERM
    if [[ -n "${ACTIVE_STEP_PID}" ]] &&
            kill -0 "${ACTIVE_STEP_PID}" 2>/dev/null; then
        kill -TERM "${ACTIVE_STEP_PID}" 2>/dev/null || true
        wait "${ACTIVE_STEP_PID}" 2>/dev/null || true
    fi
    exit "${exit_code}"
}

trap 'on_signal 130' INT
trap 'on_signal 143' TERM

: >"${COMMAND_RESULTS}"
git -C "${QEMU_SOURCE}" status --short >"${EVIDENCE_DIR}/qemu-status.txt"
{
    printf 'test_names=%s\n' "${TEST_NAMES[*]}"
    printf 'qemu_sha=%s\n' "${QEMU_SHA}"
    printf 'qemu_source=%s\n' "${QEMU_SOURCE}"
    printf 'build_dir=%s\n' "${BUILD_DIR}"
    printf 'qtest_library_source=%s\n' "${QTEST_LIBRARY_SOURCE}"
    printf 'qtest_library_build=%s\n' "${QTEST_LIBRARY}"
    printf 'qemu_binary=%s\n' "${QEMU_BINARY}"
    printf 'python_binary=%s\n' "${PYTHON_BINARY}"
    printf 'meson_wrapper=%s\n' "${MESON_WRAPPER}"
    printf 'meson_wheel=%s\n' "${MESON_WHEEL}"
    printf 'meson_wheel_sha256=%s\n' \
        "$(sha256sum "${MESON_WHEEL}" | awk '{print $1}')"
    printf 'meson_version=%s\n' "$("${MESON_WRAPPER}" --version)"
    printf 'configure_cwd=%s\n' "${BUILD_DIR}"
    printf 'configure_program=%s\n' "${QEMU_SOURCE}/configure"
    for index in "${!CONFIGURE_ARGS[@]}"; do
        printf 'configure_arg[%d]=%s\n' "${index}" "${CONFIGURE_ARGS[index]}"
    done
    if [[ -s "${EVIDENCE_DIR}/qemu-status.txt" ]]; then
        printf 'qemu_worktree=dirty\n'
    else
        printf 'qemu_worktree=clean\n'
    fi
    for test_name in "${TEST_NAMES[@]}"; do
        printf 'qtest_source[%s]=%s\n' "${test_name}" \
            "${QEMU_SOURCE}/tests/qtest/${test_name}-test.c"
        printf 'qtest_binary[%s]=%s\n' "${test_name}" \
            "${BUILD_DIR}/tests/qtest/${test_name}-test"
    done
} >"${EVIDENCE_DIR}/provenance.txt"

run_step() {
    local step_name="$1"
    local timeout_seconds="$2"
    local log_path="${EVIDENCE_DIR}/${step_name}.log"
    local exit_code
    shift 2

    {
        printf 'cwd=%q\n' "${PWD}"
        printf 'command='
        printf '%q ' timeout --signal=TERM --kill-after=30 "${timeout_seconds}" "$@"
        printf '\n'
    } >"${log_path}"

    timeout --signal=TERM --kill-after=30 "${timeout_seconds}" "$@" \
        >>"${log_path}" 2>&1 &
    ACTIVE_STEP_PID=$!
    if wait "${ACTIVE_STEP_PID}"; then
        exit_code=0
    else
        exit_code=$?
    fi
    ACTIVE_STEP_PID=""
    printf '%s\t%d\t%s\n' "${step_name}" "${exit_code}" "${log_path}" \
        >>"${COMMAND_RESULTS}"
    cat "${log_path}"
    return "${exit_code}"
}

pushd "${BUILD_DIR}" >/dev/null
run_step configure 600 env "PATH=${TOOLING_BIN}:${PATH}" \
    "${QEMU_SOURCE}/configure" "${CONFIGURE_ARGS[@]}"
popd >/dev/null

build_targets=(qemu-system-aarch64)
for test_name in "${TEST_NAMES[@]}"; do
    build_targets+=("tests/qtest/${test_name}-test")
done
run_step build 1800 ninja -C "${BUILD_DIR}" -j 8 "${build_targets[@]}"

[[ -x "${QEMU_BINARY}" ]] || {
    printf 'error: targeted QEMU executable was not produced: %s\n' \
        "${QEMU_BINARY}" >&2
    exit 1
}
[[ -d "${QTEST_LIBRARY}" ]] || {
    printf 'error: local qtest support objects were not produced: %s\n' \
        "${QTEST_LIBRARY}" >&2
    exit 1
}

for test_name in "${TEST_NAMES[@]}"; do
    QTEST_BINARY="${BUILD_DIR}/tests/qtest/${test_name}-test"
    [[ -x "${QTEST_BINARY}" ]] || {
        printf 'error: targeted qtest executable was not produced: %s\n' \
            "${QTEST_BINARY}" >&2
        exit 1
    }
    pushd "${BUILD_DIR}" >/dev/null
    run_step "test-${test_name}" 180 env "QTEST_QEMU_BINARY=${QEMU_BINARY}" \
        "${QTEST_BINARY}" --tap -k
    popd >/dev/null
    test_log="${EVIDENCE_DIR}/test-${test_name}.log"
    expected_plan="${EXPECTED_TAP_PLANS[${test_name}]}"
    actual_plan="$(sed -n 's/^1\.\.//p' "${test_log}")"
    [[ "${actual_plan}" == "${expected_plan}" ]] || {
        printf 'error: qtest TAP plan mismatch for %s: expected %s, got %q\n' \
            "${test_name}" "${expected_plan}" "${actual_plan}" >&2
        exit 1
    }
    ok_count="$(grep -Ec '^ok [1-9][0-9]* ' "${test_log}" || true)"
    [[ "${ok_count}" == "${expected_plan}" ]] || {
        printf 'error: qtest TAP pass count mismatch for %s: expected %s, got %s\n' \
            "${test_name}" "${expected_plan}" "${ok_count}" >&2
        exit 1
    }
    if grep -Eq '^(not ok|Bail out!)' "${test_log}"; then
        printf 'error: qtest TAP failure marker found for %s\n' \
            "${test_name}" >&2
        exit 1
    fi
    awk -v expected="${expected_plan}" '
        $1 == "ok" {
            seen++
            if ($2 != seen) {
                exit 1
            }
        }
        END {
            if (seen != expected) {
                exit 1
            }
        }
    ' "${test_log}" || {
        printf 'error: qtest TAP numbering mismatch for %s\n' "${test_name}" >&2
        exit 1
    }
done

{
    stat -c 'qemu_binary=%n mode=%A size=%s mtime=%y' "${QEMU_BINARY}"
    stat -c 'qtest_library=%n mode=%A size=%s mtime=%y' "${QTEST_LIBRARY}"
    "${QEMU_BINARY}" --version | head -1
    for test_name in "${TEST_NAMES[@]}"; do
        stat -c 'qtest_binary=%n mode=%A size=%s mtime=%y' \
            "${BUILD_DIR}/tests/qtest/${test_name}-test"
    done
} >"${EVIDENCE_DIR}/build-identity.txt"

FINAL_STATUS="pass"
printf 'PASS tests=%s qemu_sha=%s evidence=%s\n' \
    "${TEST_NAMES[*]}" "${QEMU_SHA}" "${EVIDENCE_DIR}"
