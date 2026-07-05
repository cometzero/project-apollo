# Apollo QVP Yocto/QBox Runbook

Updated: 2026-07-06

This runbook covers the Apollo QVP Yocto machine and the Yocto-built QBox host
bundle. It documents the deploy contract and current blockers. It does not
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
| Recommended build directory | `build-apollo-qvp` |
| Deploy image root | `build-apollo-qvp/tmp_baremetal/deploy/images/apollo-qvp` |
| QBox bundle directory | `qbox-apollo-qvp/` |
| QBox bundle env file | `qbox-apollo-qvp-env.sh` |
| QBox bundle manifest | `qbox-apollo-qvp-manifest.json` |
| libqemu native recipe | `qbox-libqemu-native` |
| Apollo QVP QBox bundle recipe | `qbox-apollo-qvp-native` |

## Setup

Initialize a separate Apollo QVP build directory:

```bash
export TEMPLATECONF=$PWD/hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp
source layers/poky/oe-init-build-env build-apollo-qvp
```

The QVP template sets `MACHINE = "apollo-qvp"` and keeps the baremetal
`TMPDIR` layout. It also keeps BitBake disk monitoring enabled with
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
build-apollo-qvp/tmp_baremetal/deploy/images/apollo-qvp/
```

Expected QVP deploy-visible image names include:

- `nexios-image-apollo-qvp.*`
- `apollo-qvp.dtb`
- `firmware-apollo-qvp`
- `uefi-capsule-apollo-qvp`
- `efi-capsule-update-disk-image-apollo-qvp.img`

## QBox Native Bundle

Build the QBox host-side native artifacts from an initialized
`build-apollo-qvp` BitBake shell:

```bash
MACHINE=apollo-qvp bitbake qbox-libqemu-native -c deploy
MACHINE=apollo-qvp bitbake qbox-apollo-qvp-native -c deploy
```

The canonical bundle path is:

```text
build-apollo-qvp/tmp_baremetal/deploy/images/apollo-qvp/qbox-apollo-qvp/
```

The bundle contract is:

| Path | Purpose |
| --- | --- |
| `platforms-vp` | Native QBox executable. |
| `lib/` | Apollo QBox modules, `libqbox.so`, `libqemu-system-aarch64.so`, and optional `liblua.so`. |
| `platforms/apollo/apollo-qvp.lua` | QVP Lua entrypoint. |
| `platforms/apollo/hw-block/` | Apollo hardware-block Lua configuration. |
| `fw/` | Optional QBox platform firmware helper files. |
| `share/` | Optional QBox/libqemu share data. |
| `qbox-apollo-qvp-env.sh` | Environment file that sets `QBOX_APOLLO_QVP_BUNDLE_DIR`, default `QBOX_CONF`, `PATH`, and `LD_LIBRARY_PATH`. |
| `qbox-apollo-qvp-manifest.json` | Machine-readable bundle manifest with source paths, aggregate target, required targets, and deployed artifacts. |
| `libqemu/manifest.txt` | `qbox-libqemu-native` deploy manifest for the standalone libqemu output. |

## Run

Run Apollo QVP through the Yocto deploy tree and QBox bundle:

```bash
./run_qbox_yocto.sh --machine apollo-qvp --build-dir build-apollo-qvp
```

For a file-backed dry run:

```bash
./run_qbox_yocto.sh --machine apollo-qvp --build-dir build-apollo-qvp --headless --dry-run
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
- `apollo-qvp.lua`: canonical QVP Lua entrypoint. A manifest-declared
  compatibility Lua path is acceptable only while the bundle records it.
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
| `runtime_blocked_missing_artifacts` | Required QVP image files, QBox bundle files, or runtime logs are missing. |
| `runtime_unverified` | Build or deploy evidence exists, but no QVP `result.json` and UART logs have been inspected. |
| `compatibility_alias_in_use` | A documented alias such as `apollo_fvp_full_system` or `fvp-rd-aspen` is still present as an implementation detail. |

Current blockers:

- `qbox-libqemu-native -c deploy` is blocked because configure did not finish
  before BitBake `STOPTASKS`; deploy was not run.
- `qbox-apollo-qvp-native` deploy/runtime artifacts are therefore missing.
- QVP runtime artifacts under `build/qbox-apollo-qvp/` are not available.

After freeing disk space, resume with:

```bash
source layers/poky/oe-init-build-env build-apollo-qvp
MACHINE=apollo-qvp bitbake qbox-libqemu-native -c deploy
MACHINE=apollo-qvp bitbake qbox-apollo-qvp-native -c deploy
./run_qbox_yocto.sh --machine apollo-qvp --build-dir build-apollo-qvp --headless --dry-run
```

Only run a bounded boot after the deploy artifacts and dry-run command are
valid.
