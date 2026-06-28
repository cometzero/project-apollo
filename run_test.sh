#!/usr/bin/env bash

set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="build"
TESTS_DIR="build/tests"
MACHINE="apollo-fvp" IMAGE="nexios-image" STAMP="" OUT_DIR=""
LIST_MODE=0 DRY_RUN=0 PREFLIGHT_ONLY=0 SKIP_RUNTIME=0
export INCLUDE_QBOX_RUNTIME=0
TIMEOUT_OEQA=10800 TIMEOUT_FVP=600
RUN_DIR="" SUMMARY_PATH="" COMMANDS_FILE=""
FINAL_EXIT_CODE=70 FINALIZED=0 INTERNAL_ERROR=0
INTERNAL_REASON="blocked_internal_runner_error"

usage() {
    python3 scripts/test/run_test_cli.py
}

usage_error() {
    printf 'error: %s\n' "$*" >&2
    usage >&2
    exit 64
}

while (($#)); do
    case "$1" in
        --build-dir=*) BUILD_DIR="${1#*=}"; shift ;;
        --build-dir) (($# >= 2)) || usage_error "--build-dir requires a path"; BUILD_DIR="$2"; shift 2 ;;
        --machine=*) MACHINE="${1#*=}"; shift ;;
        --machine) (($# >= 2)) || usage_error "--machine requires a name"; MACHINE="$2"; shift 2 ;;
        --image=*) IMAGE="${1#*=}"; shift ;;
        --image) (($# >= 2)) || usage_error "--image requires a name"; IMAGE="$2"; shift 2 ;;
        --out-dir=*) OUT_DIR="${1#*=}"; shift ;;
        --out-dir) (($# >= 2)) || usage_error "--out-dir requires a path"; OUT_DIR="$2"; shift 2 ;;
        --stamp=*) STAMP="${1#*=}"; shift ;;
        --stamp) (($# >= 2)) || usage_error "--stamp requires a value"; STAMP="$2"; shift 2 ;;
        --list) LIST_MODE=1; shift ;;
        --dry-run) DRY_RUN=1; shift ;;
        --preflight-only) PREFLIGHT_ONLY=1; shift ;;
        --skip-runtime) SKIP_RUNTIME=1; shift ;;
        --include-qbox-runtime) INCLUDE_QBOX_RUNTIME=1; shift ;;
        --timeout-oeqa=*) TIMEOUT_OEQA="${1#*=}"; shift ;;
        --timeout-oeqa) (($# >= 2)) || usage_error "--timeout-oeqa requires seconds"; TIMEOUT_OEQA="$2"; shift 2 ;;
        --timeout-fvp=*) TIMEOUT_FVP="${1#*=}"; shift ;;
        --timeout-fvp) (($# >= 2)) || usage_error "--timeout-fvp requires seconds"; TIMEOUT_FVP="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) usage_error "unknown option: $1" ;;
    esac
done

if [[ -z "${STAMP}" ]]; then
    if [[ -n "${OUT_DIR}" ]]; then
        STAMP="$(basename "${OUT_DIR}")"
    else
        STAMP="$(date +%Y%m%d-%H%M%S)"
    fi
fi
if [[ -z "${OUT_DIR}" ]]; then
    OUT_DIR="${TESTS_DIR}/${STAMP}"
fi

RUN_DIR="${OUT_DIR}"
SUMMARY_PATH="${RUN_DIR}/summary.json"
COMMANDS_FILE="${RUN_DIR}/commands.jsonl"

RUN_DIR_REJECTION="$(PYTHONPATH="${ROOT_DIR}/scripts/test" python3 -c 'from pathlib import Path; import sys; from run_test_conf import PublicRunRequest, public_run_rejection_message; message = public_run_rejection_message(PublicRunRequest(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))); print(message or ""); raise SystemExit(64 if message else 0)' "${ROOT_DIR}" "${BUILD_DIR}" "${RUN_DIR}")" || usage_error "${RUN_DIR_REJECTION:-invalid --out-dir}"

mark_internal() {
    INTERNAL_ERROR=1
    INTERNAL_REASON="$1"
    return 70
}

append_record() {
    local name="$1" status="$2" exit_code="$3" required="$4"
    local stdout_log="$5" stderr_log="$6" artifact_path="$7" blockers_path="$8"
    local reason="$9"
    shift 9
    local -a args=(python3 scripts/test/run_test_records.py append \
        --commands-file "${COMMANDS_FILE}" \
        --name "${name}" \
        --status "${status}" \
        --exit-code "${exit_code}" \
        --required "${required}" \
        --stdout-log "${stdout_log}" \
        --stderr-log "${stderr_log}" \
        --artifact-path "${artifact_path}" \
        --reason "${reason}")
    if [[ -n "${blockers_path}" ]]; then
        args+=(--blockers-path "${blockers_path}")
    fi
    args+=("$@")
    "${args[@]}" || mark_internal "blocked_command_record_write_failed"
}

write_internal_summary() {
    python3 scripts/test/run_test_result_io.py internal-summary \
        --summary "${SUMMARY_PATH}" \
        --run-dir "${RUN_DIR}" \
        --status BLOCKED \
        --exit-code "$1" \
        --reason "$2"
}

finalize() {
    local requested_exit="$1" status="BLOCKED" summarize_rc=70
    if ((FINALIZED)); then
        return
    fi
    FINALIZED=1
    trap - EXIT INT TERM
    mkdir -p "${RUN_DIR}/logs"
    if ! python3 scripts/test/run_test_result_io.py clear-summary --summary "${SUMMARY_PATH}"; then
        mark_internal "blocked_summary_clear_failed" || true
    fi
    if ((INTERNAL_ERROR)); then
        write_internal_summary 70 "${INTERNAL_REASON}" || true
        FINAL_EXIT_CODE=70
    elif [[ -f "${COMMANDS_FILE}" && -s "${COMMANDS_FILE}" ]]; then
        python3 scripts/test/run_test_manifest.py summarize \
            --run-dir "${RUN_DIR}" \
            --out "${SUMMARY_PATH}" \
            >"${RUN_DIR}/logs/summarize.stdout.log" \
            2>"${RUN_DIR}/logs/summarize.stderr.log"
        summarize_rc=$?
        if ((summarize_rc <= 2)) && [[ -s "${SUMMARY_PATH}" ]]; then
            status="$(python3 scripts/test/run_test_result_io.py status --summary "${SUMMARY_PATH}" 2>/dev/null || printf 'BLOCKED\n')"
            case "${status}" in
                PASS) FINAL_EXIT_CODE=0 ;;
                FAIL) FINAL_EXIT_CODE=1 ;;
                BLOCKED) FINAL_EXIT_CODE=2 ;;
                *) FINAL_EXIT_CODE=70 ;;
            esac
        else
            write_internal_summary 70 "blocked_summary_generation_failed" || true
            FINAL_EXIT_CODE=70
        fi
    else
        write_internal_summary 70 "blocked_no_command_records" || true
        FINAL_EXIT_CODE=70
    fi
    status="$(python3 scripts/test/run_test_result_io.py status --summary "${SUMMARY_PATH}" 2>/dev/null || printf 'BLOCKED\n')"
    if ((requested_exit == 64 || requested_exit == 70)); then
        FINAL_EXIT_CODE="${requested_exit}"
    fi
    ln -sfn "$(basename "${RUN_DIR}")" "${TESTS_DIR}/latest"
    printf 'RESULT: %s\n' "${status}"
    printf 'SUMMARY: %s\n' "${SUMMARY_PATH}"
}

handle_signal() {
    local signal_name="$1"
    append_record "interrupted" "blocked" "" "true" "" "" "" "" \
        "blocked_interrupted_${signal_name}" --argv "./run_test.sh" || true
    finalize 2
    exit "${FINAL_EXIT_CODE}"
}

trap 'status=$?; finalize "${status}"; exit "${FINAL_EXIT_CODE}"' EXIT
trap 'handle_signal INT' INT
trap 'handle_signal TERM' TERM

run_helper() {
    local name="$1" subcommand="$2" out_path="$3"
    local stdout_rel="logs/${name}.stdout.log" stderr_rel="logs/${name}.stderr.log"
    local status="pass" rc=0
    local helper_build_dir="${BUILD_DIR}"
    if ((DRY_RUN)) && [[ "${subcommand}" != "preflight" && ! -f "${BUILD_DIR}/conf/local.conf" ]]; then
        helper_build_dir="build"
    fi
    local -a argv=(python3 scripts/test/run_test_manifest.py "${subcommand}" --build-dir "${helper_build_dir}" --machine "${MACHINE}" --out "${out_path}")
    local -a record_argv=()
    "${argv[@]}" >"${RUN_DIR}/${stdout_rel}" 2>"${RUN_DIR}/${stderr_rel}"
    rc=$?
    for arg in "${argv[@]}"; do
        record_argv+=("--argv=${arg}")
    done
    if ((rc == 2)); then
        status="blocked"
    elif ((rc != 0)); then
        status="fail"
    fi
    if ((rc == 2)); then
        append_record "${name}" "${status}" "" "true" "${stdout_rel}" "${stderr_rel}" \
            "${out_path}" "${out_path}" "" "${record_argv[@]}" || return 70
    else
        append_record "${name}" "${status}" "${rc}" "true" "${stdout_rel}" "${stderr_rel}" \
            "${out_path}" "${out_path}" "" "${record_argv[@]}" || return 70
    fi
    return "${rc}"
}

prepare_run_dir() {
    mkdir -p "${RUN_DIR}/logs" "${TESTS_DIR}"
    if ! python3 scripts/test/run_test_records.py init --commands-file "${COMMANDS_FILE}"; then
        mark_internal "blocked_command_record_init_failed"
        return 70
    fi
    ln -sfn "$(basename "${RUN_DIR}")" "${TESTS_DIR}/latest"
}

acquire_lock() {
    local lock_path="${TESTS_DIR}/.run_test.lock"
    if ! command -v flock >/dev/null 2>&1; then
        append_record "lock" "blocked" "" "true" "" "" "" "" \
            "blocked_lock_unavailable" --argv=flock "--argv=${lock_path}" || return 70
        return 2
    fi
    exec 9>"${lock_path}"
    if ! flock -n 9; then
        append_record "lock" "blocked" "" "true" "" "" "" "" \
            "blocked_lock_held" --argv=flock --argv=-n "--argv=${lock_path}" || return 70
        return 2
    fi
    append_record "lock" "pass" 0 "true" "" "" "" "" "" \
        --argv=flock --argv=-n "--argv=${lock_path}" || return 70
}

main() {
    cd "${ROOT_DIR}" || return 70
    prepare_run_dir || return $?
    run_helper "manifest" "inspect" "${RUN_DIR}/manifest.json" || return $?
    run_helper "plan" "plan" "${RUN_DIR}/plan.json" || return $?
    python3 scripts/test/run_test_plan_output.py write-excluded \
        --plan "${RUN_DIR}/plan.json" \
        --out "${RUN_DIR}/excluded.json" || return 70

    if ((LIST_MODE)); then
        python3 scripts/test/run_test_plan_output.py print-list --plan "${RUN_DIR}/plan.json" || return 70
        append_record "list" "pass" 0 "false" "" "" "" "" "" \
            --argv=./run_test.sh --argv=--list --argv=--image "--argv=${IMAGE}" || return 70
        return 0
    fi
    if ((DRY_RUN)); then
        local -a extra_args=(python3 scripts/test/run_test_extra_lanes.py --run-dir "${RUN_DIR}" --stamp "${STAMP}" --commands-file "${COMMANDS_FILE}" --timeout-fvp "${TIMEOUT_FVP}" --dry-run)
        ((SKIP_RUNTIME)) && extra_args+=(--skip-runtime)
        "${extra_args[@]}" || return $?
        python3 scripts/test/run_test_oeqa_lanes.py --run-dir "${RUN_DIR}" --commands-file "${COMMANDS_FILE}" --build-dir "${BUILD_DIR}" --image "${IMAGE}" --timeout-oeqa "${TIMEOUT_OEQA}" --dry-run || return $?
        return 0
    fi
    if ((PREFLIGHT_ONLY)); then
        acquire_lock || return $?
        run_helper "preflight" "preflight" "${RUN_DIR}/preflight.json"
        return $?
    fi
    local -a extra_args=(python3 scripts/test/run_test_extra_lanes.py --run-dir "${RUN_DIR}" --stamp "${STAMP}" --commands-file "${COMMANDS_FILE}" --timeout-fvp "${TIMEOUT_FVP}")
    ((SKIP_RUNTIME)) && extra_args+=(--skip-runtime)
    "${extra_args[@]}"
    extra_rc=$?
    ((extra_rc == 70)) && return 70
    if ((SKIP_RUNTIME)); then
        append_record "runtime-placeholder" "skipped" "" "false" "" "" "" "" "" \
            --argv=./run_test.sh --argv=--skip-runtime --argv=--image "--argv=${IMAGE}" || return 70
        return "${extra_rc}"
    fi
    acquire_lock || return $?
    run_helper "preflight" "preflight" "${RUN_DIR}/preflight.json"
    preflight_rc=$?
    ((preflight_rc == 70)) && return 70
    ((preflight_rc != 0)) && return "${extra_rc:-${preflight_rc}}"
    python3 scripts/test/run_test_oeqa_lanes.py --run-dir "${RUN_DIR}" --commands-file "${COMMANDS_FILE}" --build-dir "${BUILD_DIR}" --image "${IMAGE}" --timeout-oeqa "${TIMEOUT_OEQA}"
    oeqa_rc=$?
    ((oeqa_rc == 70)) && return 70
    return "$((extra_rc != 0 ? extra_rc : oeqa_rc))"
}

main
