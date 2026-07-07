# Apollo QVP Yocto/QBox Runbook

Updated: 2026-07-06

This runbook covers the Apollo QVP Yocto machine and the Yocto-built QBox host
provider. It documents the deploy contract and current blockers. It does not
claim QVP runtime success; that requires QBox runtime logs and `result.json`
evidence from the QVP path.

## Scope

Apollo QVP is a first-class Yocto `MACHINE` with QVP deploy-visible names. The
initial QBox platform still uses transition compatibility names where existing
QBox and RD-Aspen/FVP infrastructure has not been renamed.

Canonical names:

| Item | Name |
| --- | --- |
| Yocto machine | `apollo-qvp` |
| Recommended build directory | `build/` |
| Deploy image root | `build/tmp_baremetal/deploy/images/apollo-qvp` |
| QBox run config | `nexios-image-apollo-qvp.qboxconf` |
| QBox image class | `qboxboot` |
| libqemu native recipe | `qbox-libqemu-native` |
| Apollo QVP QBox provider recipe | `qbox-apollo-qvp-native` |

## Setup

Initialize the shared Apollo build directory:

```bash
export TEMPLATECONF=$PWD/hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp
source layers/poky/oe-init-build-env build
```

The QVP template sets `MACHINE ??= "apollo-qvp"` and keeps the baremetal
`TMPDIR` layout. The shared `build/conf/local.conf` can also be overridden
with `MACHINE=apollo-qvp bitbake ...` or `./yocto_build.sh --machine
apollo-qvp`. The template keeps BitBake disk monitoring enabled with
`STOPTASKS` thresholds for `${TMPDIR}`, `${DL_DIR}`, `${SSTATE_DIR}`, and
`/tmp`.

Return to the repository root before using the wrapper commands:

```bash
cd "$OLDPWD"
```

## Build

Build the Apollo QVP image from the repository root:

```bash
./yocto_build.sh --machine apollo-qvp
```

Optional dm-verity variants use QVP multiconfig names:

```bash
./yocto_build.sh --machine apollo-qvp --dm-verity=on
./yocto_build.sh --machine apollo-qvp --dm-verity=off
```

The expected deploy image root is:

```text
build/tmp_baremetal/deploy/images/apollo-qvp/
```

Expected QVP deploy-visible image names include:

- `nexios-image-apollo-qvp.*`
- `apollo-qvp.dtb`
- `firmware-apollo-qvp`
- `uefi-capsule-apollo-qvp`
- `efi-capsule-update-disk-image-apollo-qvp.img`

## QBox Native Sysroot/qboxconf

Build the QBox host-side native provider and generate the image `.qboxconf`
from an initialized `build/` BitBake shell:

```bash
MACHINE=apollo-qvp bitbake qbox-libqemu-native -c populate_sysroot
MACHINE=apollo-qvp bitbake qbox-apollo-qvp-native -c populate_sysroot
MACHINE=apollo-qvp bitbake nexios-image -c do_write_qboxboot_conf
```

The canonical QBox run config is:

```text
build/tmp_baremetal/deploy/images/apollo-qvp/nexios-image-apollo-qvp.qboxconf
```

The deploy contract is the generated `.qboxconf` plus the native sysroot
provider. The deploy tree carries the run configuration; host executables,
libraries, modules, and data stay in native sysroot components.

| Field or path | Purpose |
| --- | --- |
| `provider.name` | Native provider recipe, currently `qbox-apollo-qvp-native`. |
| `provider.bindir` | Native sysroot component directory containing `platforms-vp`. |
| `provider.libdir` | Native sysroot component directory containing `libqbox.so` and libqemu libraries. |
| `provider.module_dir` | Native sysroot component directory containing QBox module `.so` files. |
| `provider.data_dir` | Native sysroot component directory containing QBox Lua platform data. |
| `sysroot.components_dir` | Yocto native sysroot components root. |
| `sysroot.recipe_sysroot_native` | Provider recipe native sysroot used by the runner. |
| `exe` | Relative executable path, currently `platforms-vp`. |
| `config` | Relative Lua entrypoint, currently `platforms/apollo/apollo-qvp.lua`. |
| `images` | Deploy image artifact names consumed by the runner. |

## Run

Run Apollo QVP through the Yocto deploy tree, generated `.qboxconf`, and
native sysroot provider:

```bash
./run_qbox_yocto.sh
```

For a file-backed dry run:

```bash
./run_qbox_yocto.sh --headless --dry-run
```

The QVP runtime output root should use:

```text
build/qbox-apollo-qvp/
```

Runtime success requires generated QBox evidence, not only a successful build.
Do not report QVP runtime success until `result.json`, `summary.txt`, and the
per-UART logs exist under the QVP runtime output directory.

## Compatibility Aliases

These names are allowed only as transition details:

- `apollo_fvp_full_system`: current QBox aggregate CMake target used by
  `qbox-apollo-qvp-native` through `QBOX_APOLLO_BUILD_TARGET`.
- `apollo-qvp.lua`: canonical QVP Lua entrypoint. A `.qboxconf`-declared
  compatibility Lua path is acceptable only while the config records it.
- `fvp-rd-aspen`: inherited machine override, native machine name, firmware
  recipe include, and existing RD-Aspen QBox environment prefix. QVP runtime
  scripts do not automatically fall back to FVP-named deploy artifacts; use an
  explicit command-line override when a compatibility artifact is intentional.
- `apollo-fvp`: historical source/configuration reference only. QVP deploy
  names must remain `apollo-qvp` or `qbox-apollo-qvp`.

Compatibility aliases must not replace QVP deploy-visible names.

## Blocker Classification

Use these statuses in reports:

| Status | Meaning |
| --- | --- |
| `blocked_disk_space_stoptasks` | BitBake stopped scheduling tasks because the disk monitor action was `STOPTASKS`. Current `df -h /build` evidence shows `/build` at 100% with 713M available, below the configured 1G threshold, and QBox native deploy did not complete. |
| `runtime_blocked_missing_artifacts` | Required QVP image files, `.qboxconf`, native sysroot provider files, or runtime logs are missing. |
| `runtime_unverified` | Build or deploy evidence exists, but no QVP `result.json` and UART logs have been inspected. |
| `compatibility_alias_in_use` | A documented alias such as `apollo_fvp_full_system` or `fvp-rd-aspen` is still present as an implementation detail. |

Current verification notes:

- Build and deploy evidence belongs under the shared `build/` directory.
- Native QBox provider artifacts belong in Yocto sysroot components; deploy
  contains the `.qboxconf` run configuration and image artifacts.
- QVP runtime success still requires generated `result.json`, `summary.txt`,
  and per-UART logs under `build/qbox-apollo-qvp/`.

To refresh the QBox provider and run config directly:

```bash
source layers/poky/oe-init-build-env build
MACHINE=apollo-qvp bitbake qbox-libqemu-native -c populate_sysroot
MACHINE=apollo-qvp bitbake qbox-apollo-qvp-native -c populate_sysroot
MACHINE=apollo-qvp bitbake nexios-image -c do_write_qboxboot_conf
./run_qbox_yocto.sh --headless --dry-run
```

Only run a bounded boot after the image artifacts, `.qboxconf`, native provider
artifacts, and dry-run command are valid.
