#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Isolated TriCore Zephyr build; never changes the SI Zephyr checkout.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
overlay="$root/hsoc-stack/components/system_mgmt/zephyrproject/zephyr_vmcu_src"
workspace=${VMCU_ZEPHYR_WORKSPACE:-"$root/build/qbox-apollo-qvp/zephyr-vmcu"}
app="$overlay"
build_dir=""
bootstrap=false
jobs=${VMCU_BUILD_JOBS:-8}
while (($#)); do
    case "$1" in
        --bootstrap) bootstrap=true; shift ;;
        --app) app=$2; shift 2 ;;
        --build-dir) build_dir=$2; shift 2 ;;
        --jobs) jobs=$2; shift 2 ;;
        --help|-h)
            echo "Usage: $0 [--bootstrap] [--app PATH] [--build-dir PATH] [--jobs N]"
            echo "--bootstrap downloads the pinned Zephyr checkout and installs Python build dependencies."
            exit 0 ;;
        *) echo "Unknown argument: $1" >&2; exit 2 ;;
    esac
done
mkdir -p "$workspace"
workspace=$(realpath "$workspace")
app=$(realpath "$app")
build_dir=${build_dir:-"$workspace/app"}
source_dir="$workspace/zephyr"
revision=$(sed -n 's/^      revision: \([0-9a-f]\{40\}\)$/\1/p' "$overlay/west.yml")
[[ $revision =~ ^[0-9a-f]{40}$ ]] || { echo "Invalid pinned Zephyr revision" >&2; exit 1; }
toolchain=${TRICORE_TOOLCHAIN_PATH:-"$workspace/toolchain"}
archive_name=aurixgcc_03-2026_Linux_x86-x64.zip
archive_sha=4d2a82c0bd2a65657e9f5212c75c6d9e5fab325d24baf632ff19b5214a332858
archive_url="https://github.com/linumiz/aurix-gcc-toolchain/releases/download/v11.3.0/$archive_name"
if [[ ! -x $toolchain/bin/tricore-elf-gcc ]] && $bootstrap && [[ -z ${TRICORE_TOOLCHAIN_PATH:-} ]]; then
    [[ -f $workspace/$archive_name ]] || curl --fail --location --retry 3 "$archive_url" -o "$workspace/$archive_name"
    printf '%s  %s\n' "$archive_sha" "$workspace/$archive_name" | sha256sum --check -
    mkdir -p "$toolchain"
    unzip -q "$workspace/$archive_name" -d "$toolchain"
    # This upstream zip does not preserve executable mode bits.
    find "$toolchain/bin" "$toolchain/libexec" "$toolchain/tricore-elf/bin" \
        -type f -exec chmod u+x {} +
fi
cross_compile="$toolchain/bin/tricore-elf-"
if [[ ! -x ${cross_compile}gcc ]]; then
    echo "TriCore GCC missing: ${cross_compile}gcc (run --bootstrap or set TRICORE_TOOLCHAIN_PATH)" >&2
    exit 1
fi
if [[ ! -d $source_dir/.git ]]; then
    if ! $bootstrap; then
        echo "Pinned Zephyr checkout missing; run $0 --bootstrap" >&2
        exit 1
    fi
    git init "$source_dir"
    git -C "$source_dir" remote add origin https://github.com/zephyrproject-rtos/zephyr.git
    git -C "$source_dir" fetch --depth 1 origin "$revision"
    git -C "$source_dir" checkout --detach FETCH_HEAD
fi
if [[ $(git -C "$source_dir" rev-parse HEAD) != "$revision" ]] ||
   [[ -n $(git -C "$source_dir" status --porcelain --untracked-files=no) ]]; then
    echo "Expected clean Zephyr revision $revision at $source_dir; refusing to replace local work." >&2
    exit 1
fi
if $bootstrap; then
    python3 -m venv "$workspace/venv"
    "$workspace/venv/bin/python" -m pip install -r "$source_dir/scripts/requirements-base.txt"
fi
python=${VMCU_PYTHON:-"$workspace/venv/bin/python"}
[[ -x $python ]] || python=python3
"$python" -c 'import elftools, yaml, pykwalify, jsonschema, packaging, west' || {
    echo "Python build dependencies missing; run $0 --bootstrap" >&2
    exit 1
}
export ZEPHYR_BASE="$source_dir"
export ZEPHYR_TOOLCHAIN_VARIANT=cross-compile
export CROSS_COMPILE="$cross_compile"
# Explicit module list prevents an enclosing SI west workspace from leaking in.
cmake -S "$app" -B "$build_dir" -G Ninja \
    -DBOARD=qemu_tc3x \
    -DPython3_EXECUTABLE="$(command -v "$python")" \
    -DZEPHYR_MODULES="$overlay" \
    -DDTC_OVERLAY_FILE="$overlay/boards/qemu_tc3x.overlay" \
    -DSYSROOT_DIR="$toolchain/tricore-elf"
cmake --build "$build_dir" --parallel "$jobs"
"$python" - "$source_dir" "$revision" "$cross_compile" "$build_dir" "$app" "$overlay" "$archive_url" "$archive_sha" <<'PY'
import hashlib
import json
import pathlib
import subprocess
import sys

source, revision, cross, build, app, overlay, archive_url, archive_sha = sys.argv[1:]
elf = pathlib.Path(build) / "zephyr/zephyr.elf"
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
metadata = {
    "zephyr_revision": revision,
    "zephyr_source": source,
    "application": app,
    "board": "qemu_tc3x",
    "toolchain": subprocess.check_output([cross + "gcc", "--version"], text=True).splitlines()[0],
    "default_toolchain_archive": {"url": archive_url, "sha256": archive_sha},
    "compiler_sha256": digest(pathlib.Path(cross + "gcc")),
    "linker_sha256": digest(pathlib.Path(cross + "ld")),
    "python_version": sys.version,
    "python_packages": subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True).splitlines(),
    "elf": str(elf.resolve()),
    "elf_sha256": digest(elf),
    "sources": {str(p.relative_to(overlay)): digest(p)
                for p in sorted(pathlib.Path(overlay).rglob("*"))
                if p.is_file() and ".git" not in p.relative_to(overlay).parts},
}
(pathlib.Path(build) / "vmcu-build.json").write_text(json.dumps(metadata, indent=2) + "\n")
print(f"Zephyr vMCU ELF: {elf}")
PY
