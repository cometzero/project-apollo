#!/usr/bin/env bash
# Package Yocto kernel binaries; only small application payloads compile in ARM64.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
deploy=$(realpath -- "${1:-$root/build/tmp_baremetal/deploy/images/apollo-qvp}")
artifacts=$(realpath -- "${2:-$root/build/tmp_baremetal/work-shared/apollo-qvp/kernel-build-artifacts}")
output=${3:-$root/build/autosd/rpm-yocto}
if (( $# > 4 )) || { (( $# == 4 )) && [[ "$4" != --prepare-only ]]; }; then
 echo 'Usage: kernel_rpm_build.sh DEPLOY ARTIFACTS OUTPUT [--prepare-only]' >&2; exit 2
fi
mkdir -p "$output"
output=$(realpath -- "$output")
podman build --platform linux/amd64 -t localhost/apollo-native-rpm -f "$root/autosd/build/Containerfile.native-rpm" "$root/autosd/build" > "$output/native-builder.log" 2>&1
podman build --platform linux/arm64 -t localhost/apollo-arm64-rpm -f "$root/autosd/build/Containerfile.aarch64-rpm" "$root/autosd/build" > "$output/arm64-builder.log" 2>&1
if [[ "${4:-}" == --prepare-only ]]; then exit 0; fi
python3 "$root/scripts/autosd_demo/kernel_rpm_inputs.py" "$root" "$deploy" "$artifacts" "$output"
if [[ -f "$output/result.json" ]]; then
 podman run --rm --userns=keep-id --user "$(id -u):$(id -g)" -v "$output/repo:/repo" localhost/apollo-native-rpm createrepo_c /repo
 echo "Validated Yocto RPM cache: $output"; exit 0
fi
podman run --rm --platform linux/arm64 --userns=keep-id --user "$(id -u):$(id -g)" \
 -e JOBS="${JOBS:-2}" -v "$root:/workspace:ro" -v "$output:/output" \
 localhost/apollo-arm64-rpm bash /workspace/scripts/autosd_demo/arm64_payload_build.sh 2>&1 | tee "$output/arm64-payload.log"
podman run --rm --platform linux/amd64 --userns=keep-id --user "$(id -u):$(id -g)" \
 -v "$root:/workspace:ro" -v "$deploy:/inputs/deploy:ro" -v "$artifacts:/inputs/artifacts:ro" -v "$output:/output" \
 localhost/apollo-native-rpm python3 /workspace/scripts/autosd_demo/kernel_rpm_payload.py 2>&1 | tee "$output/build.log"
