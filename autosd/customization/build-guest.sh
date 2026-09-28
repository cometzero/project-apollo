#!/usr/bin/env bash
# Run inside the private native AArch64 AIB builder container, with the patched
# AIB at /src and Apollo kernel RPM repository at /apollo-kernel-repo.
set -euo pipefail
test "$(uname -m)" = aarch64
bundle=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
output=${1:?Usage: bash build-guest.sh NEW_IMAGE_PATH}
test ! -e "$output"
test ! -e "$bundle/automotive.oci.tar"
test -f /apollo-kernel-repo/repodata/repomd.xml
test -x /src/bin/aib
podman build --network=none --pull=never --arch arm64 \
    -t localhost/apollo-workload:1 "$bundle/payload"
/src/bin/aib build --distro autosd10-sig --arch aarch64 --target apollo-qvp \
    --no-vm --oci-archive --build-dir "$bundle/cache" --cache-max-size 10GB \
    --osbuild-manifest "$bundle/automotive.osbuild.json" \
    "$bundle/automotive.aib.yml" "$bundle/automotive.oci.tar" "$output"
