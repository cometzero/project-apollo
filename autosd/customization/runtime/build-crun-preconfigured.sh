#!/usr/bin/env bash
# Resume using host-generated portable autotools inputs and installed build deps.
set -euo pipefail
test "$(uname -m)" = aarch64
cd /work
git config --global --add safe.directory /work
test "$(git rev-parse HEAD)" = f0d911de5587342cfeb16473bf32ecdfeaf25957
git apply --reverse --check /fix/crun-cgroup-mount-label.patch
test -x configure
./configure --prefix=/usr --enable-systemd --enable-seccomp
make -j2
./crun --version
install -m755 crun /out/crun
sha256sum /out/crun
ldd /out/crun
rpm -qa | sort > /out/builder-packages.txt
git diff -- src/libcrun/linux.c
