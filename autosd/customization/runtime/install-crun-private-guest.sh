#!/usr/bin/env bash
# Install only in a disposable regular qualification guest; reboot separately.
set -euo pipefail
binary=${1:?usage: install-crun-private-guest.sh BINARY SHA256}
expected=${2:?expected SHA256 required}
test "$(uname -m)" = aarch64
test "$(getenforce)" = Enforcing
test ! -e /run/ostree-booted
test "$(sha256sum "$binary" | cut -d ' ' -f1)" = "$expected"
"$binary" --version | grep -F +SELINUX
! ldd "$binary" | grep -F 'not found'
for target in /usr/bin/crun /usr/lib/qm/rootfs/usr/bin/crun; do
    test -f "$target"
    if test ! -e "$target.apollo-vendor-backup"; then
        cp -a "$target" "$target.apollo-vendor-backup"
    fi
    # Existing runtimes may still be executing: replace the inode atomically.
    install -m755 "$binary" "$target.apollo-new"
    chcon --reference="$target" "$target.apollo-new"
    mv -f "$target.apollo-new" "$target"
    restorecon "$target"
    sha256sum "$target"
    ls -lZ "$target"
done
crun --version
podman exec qm crun --version
podman exec qm ldd /usr/bin/crun
test "$(getenforce)" = Enforcing
