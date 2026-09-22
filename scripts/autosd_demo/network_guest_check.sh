#!/usr/bin/env bash
# Actual root Podman traffic checks; not QM or timing qualification.
set -euo pipefail
image=${1:-docker.io/library/alpine:3.22}
name="apollo-net-check-$$"
table="apollo_fib_check_$$"
cleanup() {
    podman logs "$name" 2>/dev/null || true
    podman rm -f "$name" >/dev/null 2>&1 || true
    nft delete table inet "$table" >/dev/null 2>&1 || true
}
trap cleanup EXIT
trap 'echo RESULT root_container_network FAIL' ERR
uname -r
getenforce
nft add table inet "$table"
nft add chain inet "$table" output
nft add rule inet "$table" output fib daddr type local counter
echo RESULT nft_fib_rule PASS
podman image exists "$image"
podman run -d --pull=never --name "$name" -p 18080:8080 "$image" \
    sh -ec 'while true; do printf "HTTP/1.0 200 OK\r\nContent-Length: 15\r\n\r\nAPOLLO_HTTP_OK\n" | nc -l -p 8080; done'
response=$(curl --fail --retry 8 --retry-connrefused --retry-delay 1 \
    --max-time 10 http://127.0.0.1:18080/)
[[ "$response" == APOLLO_HTTP_OK ]]
echo RESULT published_http PASS
timeout --kill-after=5 60 podman exec "$name" nslookup example.com
echo RESULT container_dns PASS
timeout --kill-after=5 60 podman exec "$name" wget -T 30 -O /dev/null http://example.com/
echo RESULT container_egress_http PASS
podman network inspect podman
nft list ruleset
echo 'RESULT root_container_network PASS; QM_network_unverified'
