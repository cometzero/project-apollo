#!/usr/bin/env bash
# New versioned payload; never overwrite the official-policy evidence bundle.
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
out="$repo/build/autosd/demo-selinux-followup"
payload="$out/payload-v1.0.1"
test ! -e "$payload"
test ! -e "$out/selinux-demo-v1.0.1.tar.gz"
cp -a "$out/payload" "$payload"
cp "$out/policy-v1.0.1/rpmbuild/RPMS/noarch/custom-policy-selinux-1.0.1-1.el10.noarch.rpm" "$payload/custom-policy-selinux.rpm"
cp "$repo/scripts/autosd_demo/selinux_guest_install.sh" "$repo/scripts/autosd_demo/selinux_guest_check.sh" "$payload/"
(
    cd "$payload"
    sha256sum server client custom-policy-selinux.rpm systemd/*.service \
        10-tmpfiles.conf 10-shm-demo.conf conf.selcraft.yaml selinux_guest_*.sh \
        ipc-build-provenance.txt > SHA256SUMS
)
tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner \
    -C "$payload" -czf "$out/selinux-demo-v1.0.1.tar.gz" .
sha256sum "$out/selinux-demo-v1.0.1.tar.gz"
