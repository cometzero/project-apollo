#!/usr/bin/env bash
# Recheck an already provisioned private disk on QEMU or QBox after boot.
set -euo pipefail
evidence=$(mktemp -d /var/tmp/apollo-followup-recheck.XXXXXX)
printf 'EVIDENCE=%s\n' "$evidence"
test "$(getenforce)" = Enforcing
for ((i=0; i<60; i++)); do
    if bluechictl status host | grep -q online && bluechictl status qm.host | grep -q online; then break; fi
    sleep 2
done
bluechictl status host | tee "$evidence/bluechi-root.log" | grep online
bluechictl status qm.host | tee "$evidence/bluechi-qm.log" | grep online
bluechictl start qm.host test.service
podman exec qm systemctl is-active --quiet test.service
bluechictl stop qm.host test.service
test "$(podman exec qm systemctl is-active test.service)" = inactive
echo BLUECHI_RECHECK_PASS
bash /var/tmp/apollo-followup/ipc-check.sh /var/tmp/apollo-followup
bash /var/tmp/apollo-followup/cpu-weight.sh
bash /root/selinux-demo-v1.0.1/selinux_guest_check.sh "$evidence/policy"
systemctl stop server server-other client
podman exec qm systemctl stop server client client-other
systemctl reset-failed server server-other client || true
podman exec qm systemctl reset-failed server client client-other || true
bash /var/tmp/apollo-followup/iceoryx-setup.sh /var/tmp/apollo-followup --qm-shared-label
bash /var/tmp/apollo-followup/iceoryx-probe.sh /opt/apollo-iceoryx "$evidence/iceoryx"
test "$(getenforce)" = Enforcing
echo "QM_FOLLOWUP_RECHECK_PASS evidence=$evidence"
