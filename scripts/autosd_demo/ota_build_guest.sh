#!/usr/bin/env bash
# Execute exclusively in the private native AArch64 builder on SSH port 2226.
set -euo pipefail
variant=${1:?base, good, bad, builder, or convert}
case "$variant" in base|good|bad|builder|convert) ;; *) exit 2;; esac
test "$(uname -m)" = aarch64
test "$(findmnt -n -o LABEL /srv/aib)" = apollo-aib-scrat
test "$(df --output=avail -B1 /srv/aib | tail -1)" -gt 4294967296
mkdir -p /srv/aib/ota/{work,nested/aib-tmp}
image=quay.io/centos-sig-automotive/automotive-image-builder@sha256:179a58db45306498791d2011b7cbd4d5e20ace29d7e9d51e95bb987c98027c36
common=(--distro autosd10-sig --arch aarch64 --build-dir /shared-cache
        --cache-max-size 10GB --no-progress)
case "$variant" in
    builder)
        command=(build-builder "${common[@]}" --if-needed
                 --osbuild-manifest /work/builder.osbuild.json);;
    convert)
        test ! -e /srv/aib/ota/work/base.qcow2
        command=(to-disk-image --no-vm --oci-archive /work/base.oci.tar /work/base.qcow2);;
    *)
        test ! -e "/srv/aib/ota/work/$variant.oci.tar"
        command=(build "${common[@]}" --no-vm --target apollo-qvp --define reproducible_image=true
                 --osbuild-manifest "/work/$variant.osbuild.json" --oci-archive
                 "/manifest/$variant.aib.yml" "/work/$variant.oci.tar")
        # Build the helper separately before calling convert. OCI output remains
        # useful even if disk conversion needs additional platform integration.
        ;;
esac
timeout 14400 podman --root /srv/aib/outer --runroot /run/apollo-aib run --rm \
    --name "apollo-ota-build-$variant" --privileged --network host --security-opt label=disable \
    -e AIB_TMPDIR_BASE=/var/lib/containers/storage/aib-tmp \
    -v /srv/aib/ota/work:/work -v /srv/aib/ota/nested:/var/lib/containers/storage \
    -v /srv/aib/work/cache:/shared-cache \
    -v /srv/aib/ota/automotive-image-builder:/src:ro \
    -v /srv/aib/ota/manifests:/manifest:ro -v /srv/aib/ota/repo:/apollo-kernel-repo:ro \
    --workdir /work "$image" /src/bin/aib "${command[@]}"
if test -f "/srv/aib/ota/work/$variant.oci.tar"; then
    sha256sum "/srv/aib/ota/work/$variant.oci.tar"
fi
df -h /srv/aib
