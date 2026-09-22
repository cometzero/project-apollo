#!/usr/bin/env bash
# Package unchanged official demo sources/services with the generated policy RPM.
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
out="$repo/build/autosd/demo-selinux-followup"
source="$repo/autosd/sig-docs/demos/custom_selinux_policy"
payload="$out/payload"
mkdir -p "$payload/systemd"
for name in server client common.h; do
    file=$name
    test "$name" = common.h || file=$name.c
    cmp "$source/src/$file" "$repo/autosd/sig-docs/demos/shared_memory_qm_root/src/$file"
done
for role in server client; do
    cp "$repo/build/autosd/demo-ipc-payload/shm-$role" "$payload/$role"
done
cp "$source/systemd/"*.service "$payload/systemd/"
cp "$source/systemd/10-tmpfiles.conf" "$payload/"
cp "$source/qm/10-shm-demo.conf" "$payload/"
cp "$source/selinux/conf.selcraft.yaml" "$payload/"
cp "$out/policy/rpmbuild/RPMS/noarch/custom-policy-selinux-1.0.0-1.el10.noarch.rpm" "$payload/custom-policy-selinux.rpm"
cp "$repo/scripts/autosd_demo/selinux_guest_install.sh" "$repo/scripts/autosd_demo/selinux_guest_check.sh" "$payload/"
cp "$repo/build/autosd/demo-ipc-payload/build-provenance.txt" "$payload/ipc-build-provenance.txt"
(
    cd "$payload"
    sha256sum server client custom-policy-selinux.rpm systemd/*.service \
        10-tmpfiles.conf 10-shm-demo.conf conf.selcraft.yaml selinux_guest_*.sh \
        ipc-build-provenance.txt > SHA256SUMS
)
tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner \
    -C "$payload" -czf "$out/selinux-demo.tar.gz" .
sha256sum "$out/selinux-demo.tar.gz"
