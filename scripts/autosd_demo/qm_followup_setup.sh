#!/usr/bin/env bash
# Run in the private minimal_qm guest; input files are uploaded to this directory.
set -euo pipefail
payload=${1:?Usage: qm_followup_setup.sh PAYLOAD_DIR}
test "$(getenforce)" = Enforcing
qm_root=$(podman inspect --format '{{.Rootfs}}' qm)
test "$qm_root" = /usr/lib/qm/rootfs
# minimal_qm deliberately excludes DNF/RPM executables. Install into its
# stopped rootfs using the host package manager and existing image RPM database.
systemctl stop qm
timeout 900 dnf --installroot "$qm_root" --releasever 10 \
    --setopt=reposdir=/etc/yum.repos.d --setopt=install_weak_deps=False \
    -y install bluechi-agent podman
install -d /etc/bluechi/{controller,agent}.conf.d /etc/containers/systemd/qm.container.d
install -m 644 "$payload/10-bluechi-controller.conf" /etc/bluechi/controller.conf.d/
install -m 644 "$payload/10-bluechi-agent-root.conf" /etc/bluechi/agent.conf.d/
install -m 644 "$payload/10-qm.conf" /etc/containers/systemd/qm.container.d/10-bluechi-demo.conf
install -d /etc/qm/bluechi/agent.conf.d /etc/qm/systemd/system
install -m 644 "$payload/10-bluechi-agent-qm.conf" /etc/qm/bluechi/agent.conf.d/
install -m 644 "$payload/test.service" /etc/qm/systemd/system/
restorecon -RF /etc/bluechi /etc/qm /etc/containers/systemd "$qm_root"
systemctl enable --now bluechi-controller bluechi-agent
test -S /run/bluechi/bluechi.sock
systemctl daemon-reload
systemctl restart qm
for ((i=0; i<60; i++)); do
    if timeout 5 podman exec qm systemctl list-units --no-pager >/dev/null 2>&1; then
        break
    fi
    sleep 1
done
podman exec qm systemctl daemon-reload
podman exec qm systemctl enable --now bluechi-agent
for ((i=0; i<60; i++)); do
    if bluechictl status host | grep -q online && bluechictl status qm.host | grep -q online; then
        break
    fi
    sleep 2
done
bluechictl status host
bluechictl status qm.host
bluechictl status host | grep -q online
bluechictl status qm.host | grep -q online
bluechictl start qm.host test.service
podman exec qm systemctl is-active --quiet test.service
bluechictl status qm.host test.service
bluechictl stop qm.host test.service
test "$(podman exec qm systemctl is-active test.service)" = inactive
ps -eZ | grep bluechi
test "$(getenforce)" = Enforcing
echo BLUECHI_ROOT_QM_PASS
