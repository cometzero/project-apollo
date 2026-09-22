#!/usr/bin/env bash
# Apply the official custom-policy demo payload to a disposable regular AutoSD VM.
# Run only after other QM tests finish: this intentionally restarts QM.
set -euo pipefail
payload=${1:-/root/selinux-demo}
resume=${2:-}
test -z "$resume" || test "$resume" = --resume-installed
test "$(id -u)" = 0
test "$(getenforce)" = Enforcing
test -f "$payload/custom-policy-selinux.rpm"
(cd "$payload" && sha256sum -c SHA256SUMS)
payload_nevra=$(rpm -qp --qf '%{NEVRA}' "$payload/custom-policy-selinux.rpm")
installed_nevra=$(rpm -q --qf '%{NEVRA}' custom-policy-selinux 2>/dev/null || true)
already_installed=false
if test "$installed_nevra" = "$payload_nevra"; then
    rpm -V custom-policy-selinux
    already_installed=true
fi
if test "$resume" = --resume-installed; then
    # QM uses --rm, so its inspect object is absent after the interrupted install.
    # Resume only the verified package/paths from this fixture, never another rootfs.
    test "$already_installed" = true
    qm_root=/usr/lib/qm/rootfs
    qm_etc=/etc/qm
else
    qm_root=$(podman inspect --format '{{.Rootfs}}' qm)
    qm_etc=$(podman inspect --format '{{range .Mounts}}{{if eq .Destination "/etc"}}{{.Source}}{{end}}{{end}}' qm)
fi
test "$qm_root" = /usr/lib/qm/rootfs
test "$qm_etc" = /etc/qm
test -d "$qm_root/usr/bin"
test -d "$qm_etc/systemd/system"

# Refuse to overwrite different files from another demo or user workload.
same_or_absent() {
    if test -L "$2" || { test -e "$2" && test "$(sha256sum < "$1")" != "$(sha256sum < "$2")"; }; then
        echo "Refusing to overwrite unrelated file: $2" >&2
        exit 1
    fi
}
for name in server server-other client; do
    role=${name%-other}
    same_or_absent "$payload/$role" "/usr/bin/$name"
    same_or_absent "$payload/systemd/$name.service" "/etc/systemd/system/$name.service"
done
for name in client client-other server; do
    role=${name%-other}
    same_or_absent "$payload/$role" "$qm_root/usr/bin/$name"
    same_or_absent "$payload/systemd/$name.service" "$qm_etc/systemd/system/$name.service"
done
same_or_absent "$payload/10-shm-demo.conf" /etc/containers/systemd/qm.container.d/10-shm-demo.conf
same_or_absent "$payload/10-tmpfiles.conf" /usr/lib/tmpfiles.d/10-tmpfiles.conf

systemctl stop qm
for name in server server-other client; do
    role=${name%-other}
    install -m755 "$payload/$role" "/usr/bin/$name"
    install -m644 "$payload/systemd/$name.service" "/etc/systemd/system/$name.service"
done
for name in client client-other server; do
    role=${name%-other}
    install -m755 "$payload/$role" "$qm_root/usr/bin/$name"
    install -m644 "$payload/systemd/$name.service" "$qm_etc/systemd/system/$name.service"
done
install -Dm644 "$payload/10-shm-demo.conf" /etc/containers/systemd/qm.container.d/10-shm-demo.conf
install -Dm644 "$payload/10-tmpfiles.conf" /usr/lib/tmpfiles.d/10-tmpfiles.conf
if test "$already_installed" != true; then
    rpm -Uvh "$payload/custom-policy-selinux.rpm"
fi
# The official D!/d! entries are boot-only; restrict --boot to this demo's file.
systemd-tmpfiles --create --boot /usr/lib/tmpfiles.d/10-tmpfiles.conf
# selcraft 0.3.1 generates a broad /dev/shm context; never recursively relabel all shm.
restorecon -v /usr/bin/server /usr/bin/server-other /usr/bin/client \
    "$qm_root/usr/bin/client" "$qm_root/usr/bin/client-other" "$qm_root/usr/bin/server"
restorecon -Rv /run/nshm_demo /dev/shm/qm
restorecon -v /etc/systemd/system/{server,server-other,client}.service \
    "$qm_etc/systemd/system/client.service" "$qm_etc/systemd/system/client-other.service" \
    "$qm_etc/systemd/system/server.service"
systemctl daemon-reload
systemctl start qm
for ((i=0; i<60; i++)); do
    # A degraded QM can still run the specific test services; do not wait unboundedly.
    if timeout 5 podman exec qm systemctl list-units >/dev/null 2>&1; then break; fi
    sleep 1
done
podman exec qm systemctl daemon-reload
systemctl is-active qm
getenforce
ls -lZ /usr/bin/{server,server-other,client} "$qm_root/usr/bin/"{client,client-other,server}
ls -ldZ /run/nshm_demo /dev/shm/qm
echo SELINUX_DEMO_PAYLOAD_INSTALLED
