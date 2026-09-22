#!/usr/bin/env bash
# Cross-build unchanged upstream demo programs; never edits sig-docs.
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
out=${1:-"$repo/build/autosd/demo-ipc-payload"}
cc=${CC:-aarch64-linux-gnu-gcc}
src="$repo/autosd/sig-docs/demos"
mkdir -p "$out"
for role in server client; do
    "$cc" -D_GNU_SOURCE -O2 -static -Wall -Wextra \
        "$src/ipc_between_qm_root_2/src/echo-uds-$role.c" -o "$out/uds-$role"
    "$cc" -D_GNU_SOURCE -O2 -static -Wall -Wextra \
        "$src/shared_memory_qm_root/src/$role.c" -o "$out/shm-$role"
done
cp "$repo/scripts/autosd_demo/ipc_guest_baseline.sh" "$out/"
{
    git -C "$repo/autosd/sig-docs" rev-parse HEAD
    "$cc" --version
    sha256sum "$src/ipc_between_qm_root_2/src/"*.[ch] \
        "$src/shared_memory_qm_root/src/"*.[ch] "$out/"*-server "$out/"*-client
} > "$out/build-provenance.txt"
printf 'PAYLOAD=%s\n' "$out"
