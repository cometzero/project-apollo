#!/usr/bin/env bash
# Build the exact upstream examples used by the AutoSD demo, using Cargo's
# documented cross-build route. This is not the official Bazel RPM build.
set -euo pipefail
workspace=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
source_dir="$workspace/autosd/iceoryx2"
output="$workspace/build/autosd/demo-iceoryx-followup"
revision=bb0cb8a01bc5cc7b7462e258e04f3d56bf988496
test "$(git -C "$source_dir" rev-parse HEAD)" = "$revision"
test -z "$(git -C "$source_dir" status --porcelain --untracked-files=no)"
mkdir -p "$output/payload"
export CARGO_HOME="$workspace/autosd/.iceoryx-cargo"
export RUSTUP_HOME="$output/toolchains/rustup"
export CARGO_TARGET_DIR="$output/target"
export CARGO_TARGET_AARCH64_UNKNOWN_LINUX_GNU_LINKER=aarch64-linux-gnu-gcc
export CC_aarch64_unknown_linux_gnu=aarch64-linux-gnu-gcc
export AR_aarch64_unknown_linux_gnu=aarch64-linux-gnu-ar
export LIBCLANG_PATH=${LIBCLANG_PATH:-/usr/lib/llvm-18/lib}
export BINDGEN_EXTRA_CLANG_ARGS_aarch64_unknown_linux_gnu="--sysroot=$(aarch64-linux-gnu-gcc -print-sysroot)"
rustup toolchain install 1.83.0 --profile minimal --target aarch64-unknown-linux-gnu --no-self-update
rustup run 1.83.0 cargo build --manifest-path "$source_dir/Cargo.toml" \
  --locked --release --target aarch64-unknown-linux-gnu -j 4 \
  --example service_variant_customization_publisher \
  --example service_variant_customization_subscriber
for role in publisher subscriber; do
  install -m 0755 "$CARGO_TARGET_DIR/aarch64-unknown-linux-gnu/release/examples/service_variant_customization_$role" \
    "$output/payload/$role"
done
install -m 0644 "$workspace/autosd/sig-docs/demos/iceoryx2_ipc/iceoryx2.toml" "$output/payload/iceoryx2.toml"
mkdir -p "$output/payload/config"
install -m 0644 "$output/payload/iceoryx2.toml" "$output/payload/config/iceoryx2.toml"
git -C "$source_dir" rev-parse HEAD
rustup run 1.83.0 rustc -vV
file "$output/payload/publisher" "$output/payload/subscriber"
sha256sum "$output/payload/publisher" "$output/payload/subscriber" "$output/payload/iceoryx2.toml"
