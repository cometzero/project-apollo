#!/usr/bin/env bash
# Native AArch64 build, also usable through the host's existing binfmt handler.
# Run inside an unprivileged CentOS Stream 10 container with /src read-only,
# /fix read-only, and an empty writable /out artifact directory.
set -euo pipefail
test "$(uname -m)" = aarch64
test ! -e /out/crun
dnf -y --enablerepo=crb install autoconf automake gcc git-core libtool make \
    pkgconf-pkg-config python3 libcap-devel libseccomp-devel systemd-devel \
    libselinux-devel json-c-devel criu-devel patch
cp -a /src /tmp/crun
cd /tmp/crun
git config --global --add safe.directory /tmp/crun
test "$(git rev-parse HEAD)" = f0d911de5587342cfeb16473bf32ecdfeaf25957
patch -p1 < /fix/crun-cgroup-mount-label.patch
./autogen.sh
./configure --prefix=/usr --enable-systemd --enable-seccomp
make -j2
./crun --version
install -m755 crun /out/crun
sha256sum /out/crun
ldd /out/crun
git diff -- src/libcrun/linux.c
