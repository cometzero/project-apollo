#!/usr/bin/env bash

# Variables assigned here are consumed by functions sourced from sibling
# modules in the same shell.
# shellcheck disable=SC2034,SC2154

if [[ -z "${APOLLO_LOCAL_BUILD_COMMON_SOURCED:-}" ]]; then
    printf 'error: source scripts/build/local_build_common.sh before %s\n' \
        "${BASH_SOURCE[0]}" >&2
    exit 1
fi

component_dag_stage()
{
    case "$1" in
        qbox|tf-m|scp-firmware|zephyr|optee|u-boot|linux)
            printf '0\n'
            ;;
        tf-a|buildroot)
            printf '1\n'
            ;;
        flash-images|boot-disk)
            printf '2\n'
            ;;
        fvpconf)
            printf '3\n'
            ;;
        debug-manifest)
            printf '4\n'
            ;;
        *)
            return 1
            ;;
    esac
}

scheduler_stage_components()
{
    local -n output="$1"
    local stage="$2"
    shift 2
    local component

    output=()
    for component in "$@"; do
        [[ "$(component_dag_stage "${component}")" == "${stage}" ]] ||
            continue
        output+=("${component}")
    done
}

scheduler_lane_count()
{
    local component_count="$1"
    local configured="${APOLLO_LOCAL_BUILD_COMPONENT_LANES:-2}"

    [[ "${configured}" =~ ^[1-9][0-9]*$ ]] ||
        die "APOLLO_LOCAL_BUILD_COMPONENT_LANES must be a positive integer"

    if ((configured > JOBS)); then
        configured="${JOBS}"
    fi
    if ((configured > component_count)); then
        configured="${component_count}"
    fi
    printf '%s\n' "${configured}"
}

scheduler_lane_jobs()
{
    local slot="$1"
    local lanes="$2"
    local base=$((JOBS / lanes))
    local remainder=$((JOBS % lanes))

    if ((slot < remainder)); then
        printf '%s\n' "$((base + 1))"
    else
        printf '%s\n' "${base}"
    fi
}

run_parallel_component_stage()
{
    local action="$1"
    shift
    local -a components=("$@")
    ((${#components[@]} > 0)) || return 0

    local lanes
    lanes="$(scheduler_lane_count "${#components[@]}")"
    if ((lanes == 1)); then
        local component
        for component in "${components[@]}"; do
            run_step "${component}-${action}" \
                run_component "${component}" "${action}"
        done
        return 0
    fi

    if declare -F local_build_timing_init >/dev/null; then
        local_build_timing_init
        LOCAL_BUILD_TIMING_INITIALIZED=1
    fi

    local -a lane_jobs=()
    local -a lane_pids=()
    local slot
    for ((slot = 0; slot < lanes; slot++)); do
        lane_jobs[slot]="$(scheduler_lane_jobs "${slot}" "${lanes}")"
        lane_pids[slot]=""
    done

    local next=0
    local failed=0
    local first_status=0
    local component
    local pid
    local status

    while ((next < ${#components[@]})); do
        for ((slot = 0; slot < lanes; slot++)); do
            lane_pids[slot]=""
        done
        for ((slot = 0; slot < lanes && next < ${#components[@]}; slot++)); do
            component="${components[${next}]}"
            (
                local JOBS="${lane_jobs[${slot}]}"
                run_step "${component}-${action}" \
                    run_component "${component}" "${action}"
            ) &
            pid=$!
            lane_pids[slot]="${pid}"
            next=$((next + 1))
        done

        for ((slot = 0; slot < lanes; slot++)); do
            pid="${lane_pids[${slot}]}"
            [[ -n "${pid}" ]] || continue
            if wait "${pid}"; then
                status=0
            else
                status=$?
            fi
            if ((status != 0 && failed == 0)); then
                failed=1
                first_status="${status}"
            fi
        done
        ((failed == 0)) || break
    done

    return "${first_status}"
}

run_component_dag()
{
    local action="$1"
    shift
    local -a selected=("$@")
    local -a stage_components=()
    local stage

    for stage in 0 1 2 3 4; do
        scheduler_stage_components stage_components "${stage}" "${selected[@]}"
        run_parallel_component_stage "${action}" "${stage_components[@]}" ||
            return $?
    done
}

run_selected_components()
{
    local action="$1"
    shift
    local component

    case "${action}" in
        build|clean-build)
            run_component_dag "${action}" "$@"
            ;;
        *)
            for component in "$@"; do
                run_step "${component}-${action}" \
                    run_component "${component}" "${action}"
            done
            ;;
    esac
}
