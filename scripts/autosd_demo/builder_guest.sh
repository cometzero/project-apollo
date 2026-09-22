#!/usr/bin/env bash
# Run only in builder_launch.py's private full-system AArch64 guest.
set -euo pipefail
test "$(uname -m)" = aarch64
# The copied developer image has QM RPMs but not its built rootfs.
# Do not spend builder CPU on the known unavailable system service.
if test ! -d /var/qm/usr && systemctl cat qm >/dev/null 2>&1; then
    systemctl stop qm
fi
command -v mkfs.ext4 >/dev/null || timeout 300 dnf -y install e2fsprogs
mapfile -t candidates < <(lsblk -bdn -o NAME,SIZE,TYPE | awk '$2 == 25769803776 && $3 == "disk" { print "/dev/" $1 }')
test "${#candidates[@]}" = 1
scratch=${candidates[0]}
test "$(lsblk -nr "$scratch" | wc -l)" = 1
mkdir -p /srv/aib
if ! blkid "$scratch"; then
    mkfs.ext4 -L apollo-aib-scrat "$scratch"
fi
test "$(blkid -s LABEL -o value "$scratch")" = apollo-aib-scrat
mountpoint -q /srv/aib || mount "$scratch" /srv/aib
mkdir -p /srv/aib/{outer,nested,work,manifest}
cp /root/minimal_qm.aib.yml /srv/aib/manifest/
uname -a
getenforce
unshare --mount --pid --fork /bin/true
df -h / /srv/aib
image=quay.io/centos-sig-automotive/automotive-image-builder@sha256:179a58db45306498791d2011b7cbd4d5e20ace29d7e9d51e95bb987c98027c36
timeout 900 podman --root /srv/aib/outer --runroot /run/apollo-aib pull "$image"
# The privileged container has guest-only authority. No host paths or socket are exposed.
timeout 5400 podman --root /srv/aib/outer --runroot /run/apollo-aib run --rm --name apollo-aib-minimal-qm \
    --privileged --network host --security-opt label=disable \
    -v /srv/aib/work:/work -v /srv/aib/nested:/var/lib/containers/storage \
    -v /srv/aib/manifest:/manifest:ro --workdir /work "$image" aib-dev build \
    --distro autosd10-sig --target qemu --arch aarch64 \
    --build-dir /work/cache --cache-max-size 10GB \
    --osbuild-manifest /work/minimal_qm.osbuild.json --no-progress --no-vm \
    /manifest/minimal_qm.aib.yml /work/minimal_qm.aarch64.qcow2
sha256sum /srv/aib/work/minimal_qm.aarch64.qcow2
