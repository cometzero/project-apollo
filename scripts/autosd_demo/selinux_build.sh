#!/usr/bin/env bash
# Generate upstream demo policy in a native x86_64 container; no host installs.
set -euo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
out="$repo/build/autosd/demo-selinux-followup"
mkdir -p "$out"
image=quay.io/centos-sig-automotive/automotive-image-builder@sha256:39287bf2bf49f006e7460d31fe705c74b357fe12e6d1c3524b59b90bf05be712
docker run --rm --name apollo-selcraft-policy-build --platform linux/amd64 \
    -v "$out:/work" \
    -v "$repo/autosd/sig-docs/demos/custom_selinux_policy:/source:ro" \
    --workdir /work "$image" bash -euxc '
        dnf -y install python3-pip selinux-policy-devel rpm-build make createrepo_c qm git
        python3 -m pip install selcraft==0.3.1
        python3 -m pip freeze > /work/python-requirements.txt
        selcraft generate --config=/source/selinux/conf.selcraft.yaml --output-dir=/work/policy
        ls -la /work/policy
        make -C /work/policy rpm
        createrepo_c /work/policy/rpmbuild/RPMS/noarch
        rpm -qp --requires /work/policy/rpmbuild/RPMS/noarch/*.rpm > /work/rpm-requires.txt
        sha256sum /work/policy/rpmbuild/RPMS/noarch/*.rpm > /work/rpm-sha256.txt
    '
