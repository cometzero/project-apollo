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
| `tools/qbox/` | QBox SystemC/TLM/QEMU virtual platform implementation, including `platforms/apollo/`, SystemC components, and QEMU-backed components. |
| `tools/qemu/` | Local QEMU/libqemu source used by QBox. |
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
all root submodules and only the nested dependencies required by the Apollo
Yocto, local build, and QBox flows.

If a checkout was already left in a partial state by a failed recursive
submodule update, restore the pinned submodule worktrees with:

```bash
scripts/setup/bootstrap_project.sh --jobs 8 --force
```

## Yocto Build

The Yocto entrypoint uses the Apollo template under
`hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-fvp/` and builds the
`baremetal-image` target for `MACHINE = "apollo-fvp"`:

```bash
./build.sh
```

`build.sh` writes `build/conf/apollo-bitbake-resources.conf` by default and
caps `BB_NUMBER_THREADS` / `PARALLEL_MAKE` from host memory. This keeps clean
LLVM/Rust native builds from overcommitting smaller machines. On a 16-core
host with about 13 GiB RAM this selects `-j3`.

Useful resource overrides for larger hosts:

```bash
APOLLO_BUILD_THREADS=8 APOLLO_PARALLEL_MAKE="-j8" ./build.sh
```

To use BitBake's own defaults instead:

```bash
APOLLO_AUTO_RESOURCE_LIMITS=0 ./build.sh
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
./local-build.sh build
```

When the SDK is missing, `local-build.sh` creates it with
`bitbake baremetal-image -c populate_sdk` and applies the same automatic
BitBake resource limits as `build.sh`. Use `APOLLO_BUILD_THREADS`,
`APOLLO_PARALLEL_MAKE`, or `APOLLO_AUTO_RESOURCE_LIMITS=0` for the same
overrides.

To build the SDK first when it is not installed:

```bash
./local-build.sh sdk
./local-build.sh build
```

To prebuild only the QBox targets used by the Apollo full-system runner:

```bash
./local-build.sh qbox
```

To package existing local-build outputs into a QBox-runnable image set:

```bash
./local-build.sh package
./run_qbox.sh --local-build-dir build/local-apollo-fvp/package/qbox/local-build
```

Repeated `local-build.sh build` runs check the QBox CMake cache and required
Apollo QBox targets through the QBox runner's `--build-only` path. The runner
builds QBox's `apollo_fvp_full_system` aggregate target by default, so Makefile
generators evaluate the shared QBox/libqemu dependency graph once instead of
once per dynamic module. libqemu uses CMake external-project stamps by default,
so unchanged QEMU sources do not repeat the QEMU build/install step on every
local build. Set `QBOX_LIBQEMU_BUILD_ALWAYS=ON` only when you explicitly need
to force the QEMU external project build step.

Main output directory:

```text
build/local-apollo-fvp/
```

## QBox Boot

After the local build, boot the local images with the default QBox performance
options:

```bash
./run_qbox.sh
```

For non-interactive validation with file-backed logs:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --skip-build \
  --post-login-probe \
  --qbox-performance-preset \
  --cc3xx-qemu-native-backend \
  --remotepass-dmi-cache \
  --si-mode live-cl0-cl1 \
  --timeout 900
```

Runtime evidence is written under `build/qbox-apollo-fvp/`. Inspect
`result.json`, `summary.txt`, and the per-subsystem UART logs for RSE, Safety
Island CL0/CL1, TF-A/U-Boot/Linux, and the QBox platform.

If `tools/qbox/build/` has not been configured yet, the runner configures QBox
with the checkout-local `tools/qemu` submodule as libqemu and
`LIBQEMU_TARGETS=aarch64` before building the required Apollo platform targets.
This avoids an ABI mismatch with upstream `qualcomm/qemu.git`. Set
`QBOX_CMAKE_PRESET=<preset>`, `QBOX_LIBQEMU_TARGETS=<targets>`,
`QBOX_LIBQEMU_GIT=<url>`, `QBOX_FETCHCONTENT_SOURCE_DIR_LIBQEMU=<path>`,
`QBOX_GIT_BRANCH=<ref>`, or `QBOX_APOLLO_BUILD_TARGET=<target>` to override
those clean-configure defaults. Set `QBOX_APOLLO_BUILD_TARGET=` to use the
legacy explicit target list, or `QBOX_LIBQEMU_BUILD_ALWAYS=ON` to restore
libqemu's always-build behavior for QEMU development.

`local-build.sh build` creates a provisioned RSE OTP image from the TF-M local
build outputs so a clean checkout can boot directly in QBox without first
running FVP lifecycle provisioning. The image is written to
`build/local-apollo-fvp/deploy/firmware/rse-otp-image.img`. If TF-M
provisioning artifacts change, the image is regenerated automatically; use
`RSE_OTP_RESET=1 ./local-build.sh build` to force regeneration.

For explicit lifecycle experiments, disable the host-side OTP generation and
let the QBox runner handle a blank OTP fallback:

```bash
RSE_OTP_HOST_PROVISION=0 RSE_OTP_RESET=1 ./local-build.sh build
```

The fallback is enabled by default in the runner for older local-build outputs,
but normal clean-checkout validation should not need it. Disable the fallback
only when a pre-provisioned OTP is required:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py --no-auto-provision-rse-otp
```
