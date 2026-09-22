#!/usr/bin/env bash
# Build the reviewed local 1.0.1 derivative without touching the original artifacts.
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
out="$repo/build/autosd/demo-selinux-followup"
python3 "$repo/scripts/autosd_demo/selinux_policy_adjust.py"
image=quay.io/centos-sig-automotive/automotive-image-builder@sha256:39287bf2bf49f006e7460d31fe705c74b357fe12e6d1c3524b59b90bf05be712
docker run --rm --name apollo-selinux-adjusted-build --platform linux/amd64 \
    -v "$out:/work" --workdir /work "$image" bash -euxc '
        dnf -y install selinux-policy-devel rpm-build make qm git
        make -C /work/policy-v1.0.1 rpm
        sha256sum /work/policy-v1.0.1/rpmbuild/RPMS/noarch/*.rpm
    '
