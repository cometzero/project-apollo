#!/usr/bin/env bash
set -euo pipefail

endpoint="${QBOX_HOST_GDBSERVER_ENDPOINT:-127.0.0.1:12339}"
args=("$@")

for ((index = 0; index < ${#args[@]}; index++)); do
    if [[ "${args[index]}" == "--args" ]]; then
        command=("${args[@]:index+1}")
        ((${#command[@]} > 0)) || {
            printf 'error: missing QBox command after --args\n' >&2
            exit 2
        }
        exec gdbserver --once "${endpoint}" "${command[@]}"
    fi
done

printf 'error: expected GDB --args separator\n' >&2
exit 2
