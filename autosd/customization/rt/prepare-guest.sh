#!/usr/bin/env bash
# Private regular guest only. Called before bundle installation, or to check it.
set -euo pipefail
mode=${1:?Usage: prepare-guest.sh install|check}
case "$mode" in install|check) ;; *) exit 2 ;; esac
test "$(id -u)" = 0
test "$(uname -m)" = aarch64
test ! -e /run/ostree-booted
test "$(getenforce)" = Enforcing
qm_root=$(podman inspect --format '{{.Rootfs}}' qm)
test "$qm_root" = /usr/lib/qm/rootfs
packages=(realtime-tests rtla trace-cmd stress-ng util-linux procps-ng)
if [[ $mode == install ]]; then
    timeout 900 dnf -y install "${packages[@]}"
    # minimal_qm has no DNF executable. Follow the existing BlueChi installroot
    # workflow. Restart afterwards: the bundle installer inspects QM before
    # stopping it, and Quadlet removes the container object when stopped.
    systemctl stop qm
    timeout 900 dnf --installroot "$qm_root" --releasever 10 \
        --setopt=reposdir=/etc/yum.repos.d --setopt=install_weak_deps=False \
        -y install stress-ng
    rpm -q "${packages[@]}"
    rpm --root "$qm_root" -q stress-ng
    systemctl start qm
    ready=false
    for ((attempt=0; attempt<60; attempt++)); do
        if timeout 5 podman exec qm systemctl list-units --no-pager >/dev/null 2>&1; then
            ready=true
            break
        fi
        sleep 1
    done
    "$ready"
    test "$(podman inspect --format '{{.Rootfs}}' qm)" = "$qm_root"
    echo AUTOSD_RT_PACKAGES_INSTALLED
    exit 0
fi
rpm -q "${packages[@]}"
rpm --root "$qm_root" -q stress-ng
test "$(cat /sys/kernel/realtime)" = 1
mountpoint -q /sys/kernel/tracing || mount -t tracefs tracefs /sys/kernel/tracing
for tracer in timerlat osnoise; do
    grep -qw "$tracer" /sys/kernel/tracing/available_tracers
done
for tool in cyclictest oslat rtla trace-cmd stress-ng chrt taskset; do
    command -v "$tool"
done
for file in rt-experiment.py rt-trace.py check-automotive.sh; do
    test -r "/usr/libexec/apollo/$file"
done
test -x /usr/libexec/apollo/latency-probe
test -x "$qm_root/usr/libexec/apollo/latency-probe"
sha256sum /usr/libexec/apollo/latency-probe "$qm_root/usr/libexec/apollo/latency-probe"
cmp /usr/libexec/apollo/latency-probe "$qm_root/usr/libexec/apollo/latency-probe"
/usr/libexec/apollo/latency-probe --help
podman exec qm /usr/libexec/apollo/latency-probe --help
podman exec qm stress-ng --version
echo AUTOSD_RT_READINESS_PASS
