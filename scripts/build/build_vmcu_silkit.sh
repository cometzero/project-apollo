#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
out=${VMCU_SILKIT_BUILD_DIR:-"$root/build/qbox-apollo-qvp/vmcu-silkit"}
package=SilKit-5.0.7-ubuntu-22.04-x86_64-gcc
sha=0f2ad1ed0a78bc1655eb6e2d451890973fdc2ab3b6b7cd73f7d5f24b86595990
url="https://github.com/vectorgrp/sil-kit/releases/download/v5.0.7/$package.zip"
bootstrap=false
if [[ ${1:-} == --bootstrap ]]; then bootstrap=true; shift; fi
if (($#)); then echo "Usage: $0 [--bootstrap]" >&2; exit 2; fi
if [[ $(uname -m) != x86_64 ]]; then
    echo "The pinned prebuilt SDK requires x86_64; use a native SIL Kit5.0.7 source build on other hosts." >&2
    exit 1
fi
mkdir -p "$out/sdk"
if [[ ! -f $out/sdk/$package.zip ]]; then
    $bootstrap || { echo "SDK archive missing; run $0 --bootstrap" >&2; exit 1; }
    curl --fail --location --retry 3 "$url" -o "$out/sdk/$package.zip.part"
    printf '%s  %s\n' "$sha" "$out/sdk/$package.zip.part" | sha256sum --check -
    mv "$out/sdk/$package.zip.part" "$out/sdk/$package.zip"
fi
printf '%s  %s\n' "$sha" "$out/sdk/$package.zip" | sha256sum --check -
if [[ ! -f $out/sdk/$package/SilKit/lib/cmake/SilKit/SilKitConfig.cmake ]]; then
    unzip -q "$out/sdk/$package.zip" -d "$out/sdk"
fi
sdk="$out/sdk/$package/SilKit"
cmake -S "$root/scripts/silkit" -B "$out/native" -G Ninja \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_PREFIX_PATH="$sdk" \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build "$out/native" --parallel "${VMCU_BUILD_JOBS:-4}"
ctest --test-dir "$out/native" --output-on-failure
python3 - "$out" "$root" "$package" "$url" "$sha" <<'PY'
import hashlib, json, pathlib, subprocess, sys
out, root = map(pathlib.Path, sys.argv[1:3])
package, url, sha = sys.argv[3:]
sdk = out / 'sdk' / package
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = {
    'version': '5.0.7', 'source_commit': 'fcb625632ad82edd85e322e1ec0de6f021bff497',
    'archive_url': url, 'archive_sha256': sha, 'license': str(sdk / 'LICENSE'),
    'license_sha256': digest(sdk / 'LICENSE'),
    'third_party_notices': str(sdk / 'SilKit-Source/ThirdParty/LICENSES.rst'),
    'third_party_notices_sha256': digest(sdk / 'SilKit-Source/ThirdParty/LICENSES.rst'),
    'sdk_library_sha256': digest(sdk / 'SilKit/lib/libSilKit.so'),
    'build_script_sha256': digest(root / 'scripts/build/build_vmcu_silkit.sh'),
    'registry': str(sdk / 'SilKit/bin/sil-kit-registry'),
    'binary': str(out / 'native/vmcu-silkit'),
    'binary_sha256': digest(out / 'native/vmcu-silkit'),
    'compiler': subprocess.check_output(['c++', '--version'], text=True).splitlines()[0],
    'runtime_dependencies': subprocess.check_output(['ldd', str(out / 'native/vmcu-silkit')], text=True).splitlines(),
    'source_sha256': {str(p.relative_to(root)): digest(p) for p in sorted((root / 'scripts/silkit').rglob('*')) if p.is_file()},
}
(out / 'build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(manifest['binary'])
PY
