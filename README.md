# Apollo FVP Workspace

This repository builds the Apollo FVP/RD-Aspen software stack with traditional
Yocto, a local shell-based build, and QBox full-system emulation.

## Source Structure

The top-level directory is a Git repository that pins the project sources with
submodules. Most implementation ownership is still inside nested repositories;
commit and push changes at the repository that owns the file.

Main source areas:

| Path | Role |
| --- | --- |
| `arm-zena-css/` | Arm Zena CSS BSP, RD-Aspen FVP documentation, Safety Island integration, and upstream Arm platform metadata. |
| `sw-ref-stack/` | Arm Automotive Solutions reference stack with images, demos, CI fragments, test automation, HIPC/PFDI integration, and EWAOL metadata. |
| `hsoc-stack/components/primary_compute/` | Local primary-compute source submodules: Linux, U-Boot, TF-A, OP-TEE, and Buildroot. |
| `hsoc-stack/components/system_mgmt/` | Local system-management source submodules: TF-M, SCP-firmware, and the Apollo Zephyr workspace. |
| `hsoc-stack/yocto/meta-hsoc-auto-solutions/` | Apollo distro/template layer and dynamic-layer metadata. |
| `hsoc-stack/yocto/meta-hsoc-bsp/` | Apollo BSP layer for `apollo-fvp`, firmware recipes, kernel metadata, module signing, and OP-TEE integration. |
| `layers/` | External Yocto layer submodules such as Poky, meta-arm, meta-openembedded, meta-ewaol, meta-cassini, security, Zephyr, and virtualization layers. |
| `hsoc-stack/tools/qbox/` | Active upstream-friendly QBox core: `platforms-vp`, libqbox/libqemu integration, reusable SystemC/TLM components, reusable QEMU-backed components, tests, and examples. |
| `hsoc-stack/tools/qbox-platform/` | Active Apollo/RD-Aspen platform overlay: Apollo and RD-Aspen Lua entrypoints, Zena/RSE SystemC models, Apollo-specific QEMU wrappers, platform tests, and the `apollo_fvp_full_system` aggregate target. |
| `hsoc-stack/tools/qemu/` | Active local QEMU/libqemu source used by QBox. |
| `scripts/` | Categorized build, run, setup, debug, inspect, analyze, and test helpers. See `scripts/README.md`. |
| `tests/` | Repository-local tests for helper scripts and QBox runner behavior. |
| `doc/` | Project architecture notes, hardware analysis, plans, runbooks, and verification reports. |

Generated output lives under `build/`. Treat `build/conf/` as the active Yocto
configuration and treat the rest of `build/` as generated evidence, not source.
For a more detailed Korean ownership map, see
[doc/source-structure-ko.md](doc/source-structure-ko.md).

## Clean Checkout

Clone the repository and initialize submodules with the project bootstrap
script:

```bash
git clone git@github.com:cometzero/project-apollo.git
cd project-apollo
scripts/setup/bootstrap_project.sh --jobs 8
```

Do not use `git submodule update --init --recursive` as the default clean
checkout command. Some Zephyr HAL repositories contain optional nested gitlinks
without URL entries in their `.gitmodules` files, and a blanket recursive
update fails before the Apollo build starts. The bootstrap script initializes
all root submodules, including `hsoc-stack/tools/qbox`,
`hsoc-stack/tools/qbox-platform`, and `hsoc-stack/tools/qemu`, and only the
nested dependencies required by the Apollo Yocto, local build, and QBox flows.

If a checkout was already left in a partial state by a failed recursive
submodule update, restore the pinned submodule worktrees with:

```bash
scripts/setup/bootstrap_project.sh --jobs 8 --force
```

## Yocto Build

The Yocto entrypoint uses the Apollo template under
`hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-fvp/` and builds the
`nexios-image` target for `MACHINE = "apollo-fvp"`:

```bash
./yocto_build.sh
```

Apollo QVP is available as a separate Yocto machine and uses the shared
`build/` directory:

```bash
export TEMPLATECONF=$PWD/hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp
source layers/poky/oe-init-build-env build
```

From the repository root, build the Apollo QVP image with:

```bash
./yocto_build.sh --machine apollo-qvp
```

The recommended Apollo QVP deploy root is:

```text
build/tmp_baremetal/deploy/images/apollo-qvp/
```

QVP deploy-visible names use `apollo-qvp`, including
`nexios-image-apollo-qvp.*`, `apollo-qvp.dtb`,
`firmware-apollo-qvp`, `uefi-capsule-apollo-qvp`, and
`efi-capsule-update-disk-image-apollo-qvp.img`.

For the Yocto-built QBox host bundle, build the native recipes from an
initialized `build/` shell:

```bash
MACHINE=apollo-qvp bitbake qbox-libqemu-native -c deploy
MACHINE=apollo-qvp bitbake qbox-apollo-qvp-native -c deploy
```

Those recipes deploy the QBox runtime under:

```text
build/tmp_baremetal/deploy/images/apollo-qvp/qbox-apollo-qvp/
```

See [doc/apollo-qvp-yocto-qbox-runbook.md](doc/apollo-qvp-yocto-qbox-runbook.md)
for the full Apollo QVP Yocto/QBox flow, compatibility aliases, and current
blockers.

To build explicit dm-verity variants, use the Apollo Yocto multiconfig
wrappers:

```bash
./yocto_build.sh --dm-verity=on
./yocto_build.sh --dm-verity=off
```

The `on` variant uses `mc:apollo-fvp-dm-verity:nexios-image` and deploys
under `build/tmp_baremetal-apollo-fvp-dm-verity/`. The `off` variant uses
`mc:apollo-fvp-no-dm-verity:nexios-image`, deploys under
`build/tmp_baremetal-apollo-fvp-no-dm-verity/`, builds a plain ext4 root slot,
and omits the UKI initramfs.

After a Yocto build, run the generated Apollo FVP image in tmux with:

```bash
./run_fvp.sh
```

The wrapper uses
`build/tmp_baremetal/deploy/images/apollo-fvp/nexios-image-apollo-fvp.fvpconf`
by default, starts an interactive tmux session, and mirrors subsystem UARTs to
`build/fvp-tmux/apollo-fvp-<timestamp>/`.

To run the same Yocto deploy image on QBox instead of FVP:

```bash
./run_qbox_yocto.sh
```

For Apollo QVP images and the Yocto-built QBox bundle, use:

```bash
./run_qbox_yocto.sh --machine apollo-qvp
```

The wrapper resolves the Apollo Yocto WIC image, RSE/AP firmware images,
TF-A/TF-M ELFs, DTB, and Safety Island images from
`build/tmp_baremetal/deploy/images/apollo-fvp/` plus the matching Yocto
workdir, then launches the Apollo full-system QBox runner. QBox itself must
already be built, for example with `./local_build.sh qbox`.

For QVP, the expected deploy root is
`build/tmp_baremetal/deploy/images/apollo-qvp/` and the expected
Yocto-built QBox bundle directory is `qbox-apollo-qvp/`. Treat QVP runtime as
blocked until the image artifacts, `qbox-apollo-qvp/qbox-apollo-qvp-env.sh`,
`qbox-apollo-qvp/qbox-apollo-qvp-manifest.json`, and file-backed QBox logs are
present.

`yocto_build.sh` writes `build/conf/apollo-bitbake-resources.conf` by default and
caps `BB_NUMBER_THREADS` / `PARALLEL_MAKE` from host memory. This keeps clean
LLVM/Rust native builds from overcommitting smaller machines while defaulting
to at most 6 parallel jobs. On a 16-core host with about 13 GiB RAM this
selects `-j6`.

Useful resource overrides for larger hosts:

```bash
APOLLO_BUILD_THREADS=8 APOLLO_PARALLEL_MAKE="-j8" ./yocto_build.sh
```

To use BitBake's own defaults instead:

```bash
APOLLO_AUTO_RESOURCE_LIMITS=0 ./yocto_build.sh
```

The active build directory is `build/`. Before changing Yocto metadata, inspect
`build/conf/local.conf`, `build/conf/bblayers.conf`, and
`build/conf/templateconf.cfg`.

## Local Build

The local build builds the QBox Apollo full-system targets first, then uses the
Yocto SDK as the cross-toolchain provider for TF-M, SCP-firmware, Safety Island
CL1 Zephyr, OP-TEE, U-Boot, TF-A, Linux, and Buildroot images from local
sources:

```bash
./local_build.sh build
```

When the SDK is missing, `local_build.sh` creates it with
`bitbake nexios-image -c populate_sdk` and applies the same automatic
BitBake resource limits as `yocto_build.sh`. Use `APOLLO_BUILD_THREADS`,
`APOLLO_PARALLEL_MAKE`, or `APOLLO_AUTO_RESOURCE_LIMITS=0` for the same
overrides.

To build only the SDK first when it is not installed:

```bash
scripts/build/build_sdk.sh
./local_build.sh build
```

To prebuild only the QBox targets used by the Apollo full-system runner:

```bash
./local_build.sh qbox
```

### Yocto-Derived Local Build Defaults

`local_build.sh` consumes a cached Yocto variable JSON at
`build/local-apollo-fvp/yocto-local-build-vars.json`, generated by
`scripts/build/collect_yocto_local_build_vars.py`, so local component builds
track the active Apollo BitBake configuration without requiring a full image
build for every invocation. Environment overrides still take precedence over
cached values. Set `APOLLO_LOCAL_BUILD_USE_YOCTO_VARS=0` to disable cache
usage, or set `APOLLO_LOCAL_BUILD_YOCTO_VARS=/path/to/json` to select a
specific cache file.

The cache mirrors values local-build directly consumes, including
`MACHINE`, `RD_ASPEN_VARIANT`, `PC_CPUS_COUNT`, the Linux bootargs tail,
U-Boot defconfig, Linux defconfig and DTB, OP-TEE platform/workdir lookup, and
related firmware inputs. Full `nexios-image` product-image behavior remains
Yocto-only by design: rootfs composition, WIC layout, dm-verity, UKI A/B
generation, package QA, licensing, and sstate behavior are intentionally out
of local-build scope.

To refresh the cached local-build inputs from the active Yocto configuration:

```bash
python3 scripts/build/collect_yocto_local_build_vars.py \
  --output build/local-apollo-fvp/yocto-local-build-vars.json
```

To audit the in-scope parity contract:

```bash
python3 scripts/test/audit_local_build_yocto_parity.py \
  --vars build/local-apollo-fvp/yocto-local-build-vars.json \
  --output build/local-apollo-fvp/yocto-local-build-parity-audit.json
```

The user-facing `local_build.sh` and `scripts/build/build_*.sh` stage
entrypoints are intentionally thin. Component implementation lives in
sourceable modules under `scripts/build/modules/`, while
`scripts/build/local_build_common.sh` owns shared defaults, logging, cached
command helpers, SDK environment setup, and the module loader.

To check that Apollo/RD-Aspen overlay files have not drifted back into the QBox
core tree:

```bash
python3 scripts/test/audit_qbox_core_boundary.py
```

This configures the Apollo overlay in
`build/local-apollo-fvp/work/qbox-platform` by default. The overlay build uses
`hsoc-stack/tools/qbox-platform` as the CMake source tree,
`hsoc-stack/tools/qbox` as `QBOX_CORE_DIR`, and `hsoc-stack/tools/qemu` as the
checkout-local libqemu source. The
legacy `QBOX_BUILD_DIR` environment variable is still accepted as an alias for
`QBOX_PLATFORM_BUILD_DIR`.

To package existing local-build outputs into a QBox-runnable image set:

```bash
./local_build.sh --package
./run_qbox_local.sh --local-build-dir build/local-apollo-fvp/package/qbox/local-build
```

Repeated `local_build.sh build` runs check the qbox-platform CMake cache and
required Apollo QBox targets through the QBox runner's `--build-only` path. The
runner builds qbox-platform's `apollo_fvp_full_system` aggregate target by
default, so Makefile generators evaluate the shared QBox/libqemu dependency
graph once instead of once per dynamic module. libqemu uses CMake
external-project stamps by default, so unchanged QEMU sources do not repeat the
QEMU build/install step on every local build. Set
`QBOX_LIBQEMU_BUILD_ALWAYS=ON` only when you explicitly need to force the QEMU
external project build step.

Main output directory:

```text
build/local-apollo-fvp/
```

## QBox Boot

After the local build, boot the local images with the default QBox performance
options:

```bash
./run_qbox_local.sh
```

For Apollo images produced by the Yocto build, use:

```bash
./run_qbox_yocto.sh
```

For Apollo QVP images and the Yocto-built QBox bundle, use:

```bash
./run_qbox_yocto.sh --machine apollo-qvp
```

For non-interactive validation with file-backed logs:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --skip-build \
  --qbox-performance-preset \
  --cc3xx-qemu-native-backend \
  --si-mode live-cl0-cl1 \
  --timeout 900
```

Runtime evidence is written under `build/qbox-apollo-fvp/`. Inspect
`result.json`, `summary.txt`, and the per-subsystem UART logs for RSE, Safety
Island CL0/CL1, TF-A/U-Boot/Linux, and the QBox platform.

Apollo QVP runtime evidence should be written under `build/qbox-apollo-qvp/`
after the QVP deploy image and `qbox-apollo-qvp/` bundle exist. Do not treat a
QVP build or dry-run as runtime success without `result.json`, `summary.txt`,
and per-UART logs from that output root.

If `build/local-apollo-fvp/work/qbox-platform/` has not been configured yet,
the runner configures `hsoc-stack/tools/qbox-platform` with checkout-local
`hsoc-stack/tools/qbox` as `QBOX_CORE_DIR` and checkout-local
`hsoc-stack/tools/qemu` as libqemu before building the required Apollo
platform targets. This avoids an ABI mismatch with upstream `qualcomm/qemu.git`
while keeping Apollo/RD-Aspen code out of the QBox core source tree. Set
`QBOX_CORE_DIR=<path>`, `QBOX_PLATFORM_DIR=<path>`,
`QBOX_PLATFORM_BUILD_DIR=<path>`,
`QBOX_LIBQEMU_TARGETS=<targets>`, `QBOX_LIBQEMU_GIT=<url>`,
`QBOX_FETCHCONTENT_SOURCE_DIR_LIBQEMU=<path>`, or
`QBOX_APOLLO_BUILD_TARGET=<target>` to override those clean-configure defaults.
Set `QBOX_APOLLO_BUILD_TARGET=` to use the legacy explicit target list, or
`QBOX_LIBQEMU_BUILD_ALWAYS=ON` to restore libqemu's always-build behavior for
QEMU development.

`local_build.sh build` creates a provisioned RSE OTP image from the TF-M local
build outputs so a clean checkout can boot directly in QBox without first
running FVP lifecycle provisioning. The image is written to
`build/local-apollo-fvp/deploy/firmware/rse-otp-image.img`. If TF-M
provisioning artifacts change, the image is regenerated automatically; use
`RSE_OTP_RESET=1 ./local_build.sh build` to force regeneration.

For explicit lifecycle experiments, disable the host-side OTP generation and
let the QBox runner handle a blank OTP fallback:

```bash
RSE_OTP_HOST_PROVISION=0 RSE_OTP_RESET=1 ./local_build.sh build
```

The fallback is enabled by default in the runner for older local-build outputs,
but normal clean-checkout validation should not need it. Disable the fallback
only when a pre-provisioned OTP is required:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py --no-auto-provision-rse-otp
```
