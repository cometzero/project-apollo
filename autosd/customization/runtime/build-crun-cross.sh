#!/usr/bin/env bash
# Extract an installed EL10 AArch64 builder sysroot; compile on the host.
# Usage: bash build-crun-cross.sh RUNNING_BUILDER SOURCE_CLONE NEW_WORK_DIR
set -euo pipefail
builder=${1:?running dependency-builder container required}
source=$(realpath "${2:?crun clone required}")
work=$(realpath -m "${3:?new work directory required}")
fix=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
test ! -e "$work"
test "$(git -C "$source" rev-parse HEAD)" = f0d911de5587342cfeb16473bf32ecdfeaf25957
test "$(docker exec "$builder" uname -m)" = aarch64
mkdir -p "$work/sysroot/usr/include" "$work/sysroot/usr/lib64" "$work/sysroot/lib"
docker exec "$builder" tar -C /usr/include -cf - . |
    tar --no-same-permissions --no-same-owner -C "$work/sysroot/usr/include" -xf -
docker exec "$builder" tar -C /usr/lib64 -cf - . |
    tar --no-same-permissions --no-same-owner -C "$work/sysroot/usr/lib64" -xf -
docker cp -L "$builder:/lib/ld-linux-aarch64.so.1" "$work/sysroot/lib/ld-linux-aarch64.so.1"
ln -s usr/lib64 "$work/sysroot/lib64"
docker exec "$builder" rpm -qa | sort > "$work/builder-packages.txt"
cp -a "$source" "$work/source"
cd "$work/source"
patch -p1 < "$fix/crun-cgroup-mount-label.patch"
./autogen.sh > "$work/autogen.log" 2>&1
export PKG_CONFIG_SYSROOT_DIR="$work/sysroot"
export PKG_CONFIG_LIBDIR="$work/sysroot/usr/lib64/pkgconfig"
export CC="aarch64-linux-gnu-gcc --sysroot=$work/sysroot -B$work/sysroot/usr/lib64/"
aarch64-linux-gnu-gcc --version > "$work/compiler.txt"
./configure --host=aarch64-linux-gnu --prefix=/usr --enable-systemd --enable-seccomp \
    > "$work/configure.log" 2>&1
make -j"${CRUN_BUILD_JOBS:-8}" > "$work/build.log" 2>&1
install -m755 crun "$work/crun"
sha256sum "$work/crun"
# --version and ldd must also pass in the target before installation.
