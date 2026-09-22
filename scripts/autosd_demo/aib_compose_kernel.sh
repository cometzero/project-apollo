#!/usr/bin/env bash
# Compose an ARM64 bootc manifest; does not build or qualify a bootable image.
set -euo pipefail
workspace=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
repo=$(realpath -- "${1:?Usage: aib_compose_kernel.sh RPM_REPO NEW_OUTPUT_DIR}")
output=${2:?Usage: aib_compose_kernel.sh RPM_REPO NEW_OUTPUT_DIR}
test -f "$repo/repodata/repomd.xml"
mkdir -- "$output"
output=$(realpath -- "$output")
mkdir "$output/nested"
builder=quay.io/centos-sig-automotive/automotive-image-builder@sha256:39287bf2bf49f006e7460d31fe705c74b357fe12e6d1c3524b59b90bf05be712
# Native host container is sufficient for RPM resolution, not ARM64 installation.
# Privilege is needed by AIB's nested Podman setup, even for --dry-run.
docker run --rm --privileged --platform linux/amd64 \
  --mount "type=bind,src=$workspace/autosd/automotive-image-builder,dst=/src,readonly" \
  --mount "type=bind,src=$workspace/scripts/autosd_demo/apollo_kernel_image.aib.yml,dst=/manifest.aib.yml,readonly" \
  --mount "type=bind,src=$repo,dst=/apollo-kernel-repo,readonly" \
  --mount "type=bind,src=$output,dst=/work" \
  --mount "type=bind,src=$output/nested,dst=/var/lib/containers/storage" \
  --workdir /work "$builder" /src/bin/aib build \
  --distro autosd10-sig --arch aarch64 --target apollo-qvp --dry-run \
  --osbuild-manifest /work/apollo-kernel.osbuild.json \
  /manifest.aib.yml localhost/apollo-kernel-base:latest 2>&1 | tee "$output/compose.log"
