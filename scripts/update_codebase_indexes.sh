#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CACHE_DIR="${XDG_CACHE_HOME:-${HOME}/.cache}/codebase-memory-mcp"
RUN_ID="$(date +%Y%m%d-%H%M%S)"
OUTPUT_DIR="${ROOT_DIR}/build/codebase-memory-index/${RUN_ID}"

INDEX_ENTRIES=(
    "arm-auto-solutions-top|."
    "apollo-meta-hsoc-auto-solutions|hsoc-stack/yocto/meta-hsoc-auto-solutions"
    "apollo-meta-hsoc-bsp|hsoc-stack/yocto/meta-hsoc-bsp"
    "apollo-hsoc-tests|hsoc-stack/tests"
    "apollo-meta-bluechi|layers/meta-bluechi"
    "apollo-meta-ewaol|layers/meta-ewaol"
    "apollo-meta-ptx|layers/meta-ptx"
    "apollo-meta-zephyr|layers/meta-zephyr"
    "apollo-meta-clang|layers/meta-clang"
    "apollo-meta-cassini|layers/meta-cassini"
    "apollo-meta-secure-core|layers/meta-secure-core"
    "apollo-meta-mender|layers/meta-mender"
    "apollo-meta-security|layers/meta-security"
    "apollo-meta-virtualization|layers/meta-virtualization"
    "apollo-meta-arm|layers/meta-arm"
    "apollo-sw-ref-stack|sw-ref-stack"
    "build-arm-arm-auto-solutions-arm-zena-css|arm-zena-css"
    "apollo-optee-os|hsoc-stack/components/primary_compute/optee_os"
    "apollo-trusted-firmware-m|hsoc-stack/components/system_mgmt/trusted-firmware-m"
    "apollo-trusted-firmware-a|hsoc-stack/components/primary_compute/trusted-firmware-a"
    "apollo-scp-firmware|hsoc-stack/components/system_mgmt/scp-firmware"
    "apollo-qbox-platform|hsoc-stack/tools/qbox-platform"
    "apollo-qbox|hsoc-stack/tools/qbox"
    "apollo-meta-openembedded|layers/meta-openembedded"
    "apollo-poky|layers/poky"
    "apollo-buildroot|hsoc-stack/tools/buildroot"
    "apollo-qemu|hsoc-stack/tools/qemu"
    "apollo-u-boot|hsoc-stack/components/primary_compute/u-boot"
    "apollo-zephyr-hsoc-src|hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src"
    "apollo-zephyr|hsoc-stack/components/system_mgmt/zephyrproject/zephyr"
    "apollo-linux|hsoc-stack/components/primary_compute/linux"
)

SELECTED_ENTRIES=()
RUN_ALL=0
LIST_ONLY=0

usage()
{
    cat <<EOF
Usage: scripts/update_codebase_indexes.sh [options]

Options:
  --directory DIR   Update one registered repository index; may be repeated
  --all             Update all registered repository indexes sequentially
  --list            List registered project names and directories
  -h, --help        Show this help

DIR may be absolute or relative to:
  ${ROOT_DIR}

Examples:
  scripts/update_codebase_indexes.sh --directory .
  scripts/update_codebase_indexes.sh --directory layers/meta-arm
  scripts/update_codebase_indexes.sh --directory layers/meta-arm --directory hsoc-stack/tools/buildroot
  scripts/update_codebase_indexes.sh --all

Each update uses the canonical project name and fast mode. Logs and a TSV
summary are written below build/codebase-memory-index/<timestamp>/.
EOF
}

die()
{
    printf 'error: %s\n' "$*" >&2
    exit 1
}

require_command()
{
    command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

list_entries()
{
    local entry
    local project
    local path

    printf '%-48s %s\n' "PROJECT" "DIRECTORY"
    for entry in "${INDEX_ENTRIES[@]}"; do
        IFS='|' read -r project path <<<"${entry}"
        printf '%-48s %s\n' "${project}" "${path}"
    done
}

entry_for_directory()
{
    local input="$1"
    local absolute
    local relative
    local entry
    local project
    local path

    if [[ "${input}" == /* ]]; then
        absolute="$(realpath -m -- "${input}")"
    else
        absolute="$(realpath -m -- "${ROOT_DIR}/${input#./}")"
    fi
    [[ -d "${absolute}" ]] || die "directory does not exist: ${input}"
    if [[ "${absolute}" == "${ROOT_DIR}" ]]; then
        relative="."
    elif [[ "${absolute}" == "${ROOT_DIR}/"* ]]; then
        relative="${absolute#"${ROOT_DIR}/"}"
    else
        die "directory is outside the workspace: ${input}"
    fi

    for entry in "${INDEX_ENTRIES[@]}"; do
        IFS='|' read -r project path <<<"${entry}"
        if [[ "${relative}" == "${path}" ]]; then
            printf '%s\n' "${entry}"
            return 0
        fi
    done
    die "directory is not registered for indexing: ${relative}"
}

add_selected_entry()
{
    local candidate="$1"
    local entry

    for entry in "${SELECTED_ENTRIES[@]}"; do
        [[ "${entry}" == "${candidate}" ]] && return 0
    done
    SELECTED_ENTRIES+=("${candidate}")
}

root_ignore_has_pattern()
{
    local expected="$1"
    local line

    while IFS= read -r line || [[ -n "${line}" ]]; do
        [[ "${line}" == "${expected}" ]] && return 0
    done <"${ROOT_DIR}/.cbmignore"
    return 1
}

validate_root_index_exclusions()
{
    local entry
    local path
    local pattern

    [[ -f "${ROOT_DIR}/.cbmignore" ]] ||
        die "root index requires ${ROOT_DIR}/.cbmignore"
    root_ignore_has_pattern "/build/" ||
        die "root index exclusion is missing from .cbmignore: /build/"

    for entry in "${INDEX_ENTRIES[@]}"; do
        IFS='|' read -r _ path <<<"${entry}"
        [[ "${path}" == "." ]] && continue
        pattern="/${path%/}/"
        root_ignore_has_pattern "${pattern}" ||
            die "root index exclusion is missing from .cbmignore: ${pattern}"
    done
}

write_summary_row()
{
    local project="$1"
    local path="$2"
    local command_rc="$3"
    local run_log="$4"
    local status_log="$5"
    local time_log="$6"
    local db_path="${CACHE_DIR}/${project}.db"

    python3 - \
        "${project}" "${path}" "${command_rc}" \
        "${run_log}" "${status_log}" "${time_log}" "${db_path}" <<'PY'
import json
from pathlib import Path
import sys

project, path, command_rc, run_name, status_name, time_name, db_name = sys.argv[1:]


def read_json_line(filename: str) -> dict[str, object]:
    for line in reversed(Path(filename).read_text(encoding="utf-8").splitlines()):
        if line.startswith("{"):
            return json.loads(line)
    raise RuntimeError(f"no JSON result in {filename}")


run = read_json_line(run_name)
status = read_json_line(status_name)
elapsed = ""
max_rss_kb = ""
for line in Path(time_name).read_text(encoding="utf-8").splitlines():
    if "Elapsed (wall clock) time" in line:
        elapsed = line.rsplit(": ", 1)[-1]
    elif "Maximum resident set size (kbytes)" in line:
        max_rss_kb = line.rsplit(": ", 1)[-1]

db_path = Path(db_name)
db_bytes = db_path.stat().st_size if db_path.is_file() else 0
expected_counts_match = (
    "expected_nodes" not in run
    or "expected_edges" not in run
    or (
        run.get("nodes") == run.get("expected_nodes")
        and run.get("edges") == run.get("expected_edges")
    )
)
valid = (
    command_rc == "0"
    and run.get("status") == "indexed"
    and expected_counts_match
    and status.get("status") == "ready"
    and status.get("root_path") == path
)

print(
    "\t".join(
        str(value)
        for value in (
            project,
            path,
            status.get("status", "unknown"),
            status.get("nodes", 0),
            status.get("edges", 0),
            db_bytes,
            elapsed,
            max_rss_kb,
            command_rc,
        )
    )
)
raise SystemExit(0 if valid else 1)
PY
}

index_entry()
{
    local entry="$1"
    local project
    local relative_path
    local repo_path
    local run_log
    local status_log
    local time_log
    local command_rc
    local tee_rc
    local status_rc
    local status_tee_rc
    local -a pipeline_status
    local summary_row

    IFS='|' read -r project relative_path <<<"${entry}"
    if [[ "${relative_path}" == "." ]]; then
        repo_path="${ROOT_DIR}"
        validate_root_index_exclusions
    else
        repo_path="${ROOT_DIR}/${relative_path}"
    fi
    [[ -d "${repo_path}" ]] || die "repository directory is missing: ${relative_path}"
    git -C "${repo_path}" rev-parse --is-inside-work-tree >/dev/null 2>&1 ||
        die "not an initialized Git worktree: ${relative_path}"

    run_log="${OUTPUT_DIR}/${project}-index.log"
    status_log="${OUTPUT_DIR}/${project}-status.log"
    time_log="${OUTPUT_DIR}/${project}-time.log"

    printf '\n==> %s (%s)\n' "${project}" "${relative_path}"
    set +e
    /usr/bin/time -v -o "${time_log}" \
        codebase-memory-mcp cli index_repository \
            --repo-path "${repo_path}" \
            --name "${project}" \
            --mode fast \
        2>&1 | tee "${run_log}"
    pipeline_status=("${PIPESTATUS[@]}")
    command_rc="${pipeline_status[0]}"
    tee_rc="${pipeline_status[1]}"
    set -e
    [[ "${command_rc}" -eq 0 ]] || die "indexing failed for ${project}; see ${run_log}"
    [[ "${tee_rc}" -eq 0 ]] || die "could not write index log: ${run_log}"

    set +e
    codebase-memory-mcp cli index_status --project "${project}" \
        2>&1 | tee "${status_log}"
    pipeline_status=("${PIPESTATUS[@]}")
    status_rc="${pipeline_status[0]}"
    status_tee_rc="${pipeline_status[1]}"
    set -e
    [[ "${status_rc}" -eq 0 ]] || die "status check failed for ${project}"
    [[ "${status_tee_rc}" -eq 0 ]] || die "could not write status log: ${status_log}"

    summary_row="$(
        write_summary_row \
            "${project}" "${repo_path}" "${command_rc}" \
            "${run_log}" "${status_log}" "${time_log}"
    )" || die "index verification failed for ${project}"
    printf '%s\n' "${summary_row}" | tee -a "${SUMMARY_FILE}"
}

while (($#)); do
    case "$1" in
        --directory)
            (($# >= 2)) || die "--directory requires a value"
            add_selected_entry "$(entry_for_directory "$2")"
            shift 2
            ;;
        --all)
            RUN_ALL=1
            shift
            ;;
        --list)
            LIST_ONLY=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            die "unknown option: $1"
            ;;
    esac
done

if ((LIST_ONLY)); then
    ((RUN_ALL == 0 && ${#SELECTED_ENTRIES[@]} == 0)) ||
        die "--list cannot be combined with update options"
    list_entries
    exit 0
fi

if ((RUN_ALL)); then
    ((${#SELECTED_ENTRIES[@]} == 0)) ||
        die "--all cannot be combined with --directory"
    SELECTED_ENTRIES=("${INDEX_ENTRIES[@]}")
fi

((${#SELECTED_ENTRIES[@]} > 0)) || die "select --directory DIR or --all"

require_command codebase-memory-mcp
require_command git
require_command python3
require_command realpath
[[ -x /usr/bin/time ]] || die "required command not found: /usr/bin/time"

mkdir -p "${OUTPUT_DIR}"
SUMMARY_FILE="${OUTPUT_DIR}/summary.tsv"
printf 'project\troot_path\tstatus\tnodes\tedges\tdb_bytes\telapsed\tmax_rss_kb\texit_status\n' \
    >"${SUMMARY_FILE}"

printf 'Workspace: %s\n' "${ROOT_DIR}"
printf 'Output:    %s\n' "${OUTPUT_DIR}"
printf 'Indexes:   %d\n' "${#SELECTED_ENTRIES[@]}"

for entry in "${SELECTED_ENTRIES[@]}"; do
    index_entry "${entry}"
done

printf '\nAll requested indexes are ready.\n'
printf 'Summary: %s\n' "${SUMMARY_FILE}"
