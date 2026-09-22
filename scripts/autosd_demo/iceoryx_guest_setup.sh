#!/usr/bin/env bash
# Install unchanged cross-built examples into a private guest and its QM rootfs.
set -euo pipefail
payload=${1:?Usage: iceoryx_guest_setup.sh PAYLOAD_DIR}
label_mode=${2:-}
test -z "$label_mode" || test "$label_mode" = --qm-shared-label
target=/opt/apollo-iceoryx
test "$(getenforce)" = Enforcing
qm_root=$(podman inspect --format '{{.Rootfs}}' qm)
test "$qm_root" = /usr/lib/qm/rootfs
dropin=/etc/containers/systemd/qm.container.d/30-apollo-iceoryx.conf
if test -e "$dropin"; then
    test "$(cat "$dropin")" = $'[Container]\nVolume=/tmp/iceoryx2:/tmp/iceoryx2'
fi
systemctl stop qm
install -d "$target/config" "$qm_root$target/config"
for binary in publisher subscriber; do
    install -m755 "$payload/$binary" "$target/$binary"
    install -m755 "$payload/$binary" "$qm_root$target/$binary"
done
install -m644 "$payload/iceoryx2.toml" "$target/config/iceoryx2.toml"
install -m644 "$payload/iceoryx2.toml" "$qm_root$target/config/iceoryx2.toml"
install -d /tmp/iceoryx2/{services,nodes}
install -d /etc/tmpfiles.d
printf 'd /run/ipc 0755 root root -\nd /tmp/iceoryx2 0755 root root -\nd /tmp/iceoryx2/services 0755 root root -\nd /tmp/iceoryx2/nodes 0755 root root -\n' > /etc/tmpfiles.d/apollo-qm-shared-paths.conf
printf '[Container]\nVolume=/tmp/iceoryx2:/tmp/iceoryx2\n' > "$dropin"
restorecon -RF "$target" "$qm_root$target" /tmp/iceoryx2 "$dropin"
if test "$label_mode" = --qm-shared-label; then
    # Opt-in functional sharing with the existing QM domain; not app isolation.
    # /tmp is volatile: rerun setup after boot, before starting these examples.
    chcon -R -t qm_file_t /tmp/iceoryx2
fi
systemctl daemon-reload
systemctl start qm
for ((i=0; i<60; i++)); do
    if timeout 5 podman exec qm systemctl list-units --no-pager >/dev/null 2>&1; then break; fi
    sleep 1
done
podman exec qm test -d /tmp/iceoryx2/services
podman exec qm test -x "$target/subscriber"
echo ICEORYX_GUEST_PAYLOAD_READY
