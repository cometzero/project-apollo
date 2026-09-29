#!/usr/bin/env bash
# Recreate the EL10 AArch64 runtime without retained build/autosd inputs.
set -euo pipefail
runtime=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
root=$(cd "$runtime/../../.." && pwd)
output="$root/build/autosd/crun-cgroup-fix"
base_image=quay.io/centos/centos:stream10
explicit_image=false
dry_run=false
while (($#)); do
    case "$1" in
        --output) output=$(realpath -m "${2:?output required}"); shift 2 ;;
        --base-image) base_image=${2:?image required}; explicit_image=true; shift 2 ;;
        --dry-run) dry_run=true; shift ;;
        -h|--help)
            echo 'Usage: build-crun.sh [--output NEW_DIRECTORY] [--base-image quay.io/centos/centos@sha256:DIGEST] [--dry-run]'
            exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 2 ;;
    esac
done
if $explicit_image; then
[[ "$base_image" =~ ^quay\.io/centos/centos@sha256:[0-9a-f]{64}$ ]] || {
    echo 'Require a digest-pinned official CentOS image' >&2; exit 2;
}
fi
if $dry_run; then
    printf 'source=%s\nbase_image=%s\noutput=%s\n' "$root/autosd/crun" "$base_image" "$output"
    exit 0
fi
for tool in docker git tar patch autoreconf pkg-config make python3 aarch64-linux-gnu-gcc; do
    command -v "$tool" >/dev/null || { echo "Missing tool: $tool" >&2; exit 1; }
done
test ! -e "$output" || { echo "Output already exists: $output" >&2; exit 1; }
if ! $explicit_image; then
    base_image=$(python3 "$runtime/resolve-centos-image.py")
fi
# Always contact the registry. A stale local cache must not hide an unavailable
# digest. Explicit digest failures are fatal; never silently use a different image.
docker pull --platform linux/arm64 "$base_image"
if [[ ! -f "$root/autosd/crun/configure.ac" ]]; then
    git -C "$root" submodule update --init --recursive -- autosd/crun
fi
test "$(git -C "$root/autosd/crun" rev-parse HEAD)" = f0d911de5587342cfeb16473bf32ecdfeaf25957
if [[ ! -f "$root/autosd/crun/libocispec/configure.ac" ]]; then
    git -C "$root/autosd/crun" submodule update --init --recursive
fi
if [[ ! -d "$root/autosd/crun/libocispec/image-spec/schema" || ! -d "$root/autosd/crun/libocispec/runtime-spec/schema" ]]; then
    git -C "$root/autosd/crun/libocispec" submodule update --init --recursive
fi
if git -C "$root/autosd/crun" submodule status --recursive | grep -q '^[+-U]'; then
    echo 'crun submodules must match their pinned commits' >&2
    exit 1
fi
test "$(git -C "$root/autosd/crun/libocispec" rev-parse HEAD)" = \
    "$(git -C "$root/autosd/crun" ls-tree HEAD libocispec | awk '{print $3}')"
# No privileged mode, host mounts or Docker socket exposure in the builder.
# Existing host AArch64 binfmt support is required on x86_64 hosts.
builder=
cleanup() {
    if [[ -n "$builder" ]]; then docker rm -f "$builder" >/dev/null; fi
}
trap cleanup EXIT
builder=$(docker run -d --platform linux/arm64 "$base_image" sleep infinity)
test "$(docker exec "$builder" uname -m)" = aarch64
docker exec "$builder" dnf -y --enablerepo=crb install \
    libcap-devel libseccomp-devel systemd-devel libselinux-devel json-c-devel \
    criu-devel glibc-devel glibc-static
bash "$runtime/build-crun-cross.sh" "$builder" "$root/autosd/crun" "$output"
printf '%s\n' "$base_image" > "$output/base-image.txt"
docker image inspect "$base_image" > "$output/base-image.json"
docker image save -o "$output/base-image.docker.tar" "$base_image"
python3 "$runtime/crun-provenance.py" "$output"
printf 'Runtime generated: %s/crun\nValidate --version and ldd in the target guest before installation.\n' "$output"
