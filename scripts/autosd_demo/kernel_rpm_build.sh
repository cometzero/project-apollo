#!/usr/bin/env bash
# Package the deployed Apollo kernel; no host package installation or guest writes.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
DEPLOY=${1:-"$ROOT/build/tmp_baremetal/deploy/images/apollo-qvp"}
ARTIFACTS=${2:-"$ROOT/build/tmp_baremetal/work-shared/apollo-qvp/kernel-build-artifacts"}
OUTPUT=${3:-"$ROOT/build/autosd/demo-kernel-rpm"}
BUILDER=quay.io/centos-sig-automotive/automotive-image-builder@sha256:39287bf2bf49f006e7460d31fe705c74b357fe12e6d1c3524b59b90bf05be712
DEPLOY=$(realpath -- "$DEPLOY")
ARTIFACTS=$(realpath -- "$ARTIFACTS")
mkdir -p -- "$(dirname -- "$OUTPUT")"
mkdir -- "$OUTPUT" # Never reuse or overwrite an earlier build.
OUTPUT=$(realpath -- "$OUTPUT")
docker run --rm --platform linux/amd64 --entrypoint /bin/bash \
    -e TASK_UID="$(id -u)" -e TASK_GID="$(id -g)" -e APOLLO_BUILDER="$BUILDER" \
    --mount "type=bind,src=$DEPLOY,dst=/inputs/deploy,readonly" \
    --mount "type=bind,src=$ARTIFACTS,dst=/inputs/artifacts,readonly" \
    --mount "type=bind,src=$ROOT/scripts/autosd_demo/kernel_rpm_payload.py,dst=/kernel_rpm_payload.py,readonly" \
    --mount "type=bind,src=$OUTPUT,dst=/output" "$BUILDER" -ec '
      dnf -y --setopt=timeout=30 --setopt=retries=1 install \
        rpm-build-4.19.1.1-25.el10.x86_64 createrepo_c-1.1.2-4.el10.x86_64
      exec setpriv --reuid="$TASK_UID" --regid="$TASK_GID" --clear-groups \
        python3 /kernel_rpm_payload.py
    ' 2>&1 | tee "$OUTPUT/build.log"
