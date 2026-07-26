# Apollo QVP Workspace

This workspace builds the Apollo QVP software stack and runs it on QBox. Arm
FVP is kept as the reference platform for comparison, qualification, and
source-level debugging. The active Yocto baseline is `apollo-qvp`, RD-Aspen
`cfg2`, four Primary Compute CPUs, and `build/tmp_baremetal`.

## Source Structure

The top-level repository pins most implementation sources as Git submodules.
Make source changes and commits at the repository that owns the file.

| Path | Responsibility |
| --- | --- |
| `arm-zena-css/` | Arm Zena CSS BSP, RD-Aspen guides, FVP integration, firmware, and Safety Island reference sources. |
| `sw-ref-stack/` | Automotive images, demos, tests, CI fragments, HIPC/PFDI integration, and shared metadata. |
| `hsoc-stack/components/primary_compute/` | Linux, U-Boot, TF-A, and OP-TEE source submodules. |
| `hsoc-stack/components/system_mgmt/` | TF-M, SCP-firmware, and the Apollo Zephyr workspace. |
| `hsoc-stack/yocto/meta-hsoc-auto-solutions/` | Apollo distro, image, template, and QBox boot metadata. |
| `hsoc-stack/yocto/meta-hsoc-bsp/` | Apollo machine/BSP, firmware, kernel, signing, OP-TEE, WIC, and native-tool recipes. |
| `hsoc-stack/tools/qbox/` | Reusable QBox core, libqbox/libqemu integration, and SystemC/TLM/QEMU components. |
| `hsoc-stack/tools/qbox-platform/` | Apollo/RD-Aspen QBox overlay, Lua platforms, Zena/RSE models, and platform tests. |
| `hsoc-stack/tools/qemu/` | QBox-local QEMU/libqemu source. |
| `hsoc-stack/tools/buildroot/` | Buildroot source used by the local BSP initramfs flow. |
| `scripts/` | Categorized build, run, debug, setup, analysis, and test helpers. |
| `tests/` | Repository-local launcher and workflow tests. |
| `doc/` | Architecture notes, plans, runbooks, and verification reports. |

`build/conf/` is the active Yocto configuration. Other content under `build/`
is generated build or verification evidence and is not source.

## Clean Checkout

Initialize the root submodules and the nested dependencies required by Apollo:

```bash
git clone git@github.com:cometzero/project-apollo.git
cd project-apollo
scripts/setup/bootstrap_project.sh --jobs 8
```

Do not use a blanket `git submodule update --init --recursive` as the default.
Some optional Zephyr HAL gitlinks have no URL entries and can stop recursive
initialization before the Apollo dependencies are ready. To repair a partial
checkout:

```bash
scripts/setup/bootstrap_project.sh --jobs 8 --force
```

## Build Overview

The root entrypoints are the stable user interface:

| Command | Result |
| --- | --- |
| `./yocto_build.sh` | Build `nexios-bsp-initramfs` and then the full `nexios-image`. |
| `./yocto_build.sh --bsp` | Build only the minimal Yocto BSP initramfs image. |
| `./local_build.sh` | Build local firmware, Linux, Buildroot BSP initramfs, UKIs, boot disk, FVP config, debug manifest, and package. |
| `./local_build.sh qbox` | Build only the QBox/QEMU platform target set. |
| `./run_qbox_yocto.sh` | Boot the Yocto full product image on QBox. |
| `./run_qbox_yocto.sh --bsp` | Boot the Yocto BSP initramfs WIC on QBox. |
| `./run_qbox_local.sh` | Boot the local Buildroot BSP initramfs through U-Boot/EFI/UKI on QBox. |
| `./run_fvp.sh` | Run the Yocto `apollo-fvp` product image in an interactive FVP tmux session. |
| `./run_fvp.sh --machine apollo-qvp --bsp` | Run the QVP BSP initramfs artifacts on FVP. |
| `./run_test.sh` | Run the categorized FVP validation wrapper and preserve structured evidence. |

Run `COMMAND --help` for the complete option set. The sections below describe
the default contracts and the options that materially change behavior.

## Yocto Build

The active template is:

```text
hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp/
```

The default build is intentionally a two-target build:

```bash
./yocto_build.sh
```

Equivalent BitBake target selection:

```text
MACHINE=apollo-qvp bitbake nexios-bsp-initramfs nexios-image
```

Build only the fast BSP validation image with:

```bash
./yocto_build.sh --bsp
```

This sets `APOLLO_BSP_BUILD_ONLY=1` for the invocation and selects only
`nexios-bsp-initramfs`. It prevents the standalone BSP build from inheriting
the full product image's dm-verity/initramfs dependency chain. It is a build
selection control, not a persistent distro feature.

The active QVP deploy directory is:

```text
build/tmp_baremetal/deploy/images/apollo-qvp/
```

The FVP machine uses its own deploy directory:

```text
build/tmp_baremetal/deploy/images/apollo-fvp/
```

Before changing metadata or making a build claim, inspect:

```text
build/conf/local.conf
build/conf/bblayers.conf
build/conf/templateconf.cfg
```

Initialize BitBake manually when a targeted task is more appropriate:

```bash
source layers/poky/oe-init-build-env build
bitbake <recipe> -c <task>
```

`yocto_build.sh` refreshes `build/conf/` from the selected template by default.
Use `--keep-conf` only when the existing configuration must be preserved. The
script writes `build/conf/apollo-bitbake-resources.conf` and derives BitBake
parallelism from host memory. Override it with `APOLLO_BUILD_THREADS`,
`APOLLO_PARALLEL_MAKE`, or `APOLLO_AUTO_RESOURCE_LIMITS=0`.

Explicit product dm-verity variants remain available:

```bash
./yocto_build.sh --dm-verity=on
./yocto_build.sh --dm-verity=off
```

These select machine-specific multiconfigs for `nexios-image`; they are
separate from the standalone BSP initramfs.

### `nexios-bsp-initramfs`

`nexios-bsp-initramfs` stops in a BusyBox shell and does not switch to the
dm-verity root filesystem. Its pass contract is:

```text
NEXIOS_BSP_INITRAMFS_READY machine=<machine>
nexios-bsp#
```

The Yocto recipe installs only the packages required for the current Apollo
FVP/QVP BSP checks:

| Package | Purpose |
| --- | --- |
| `base-files`, `base-passwd`, `busybox` | Minimal userspace, `/init`, shell, and basic commands. |
| `nexios-bsp-init` | BSP init, console/job-control setup, module loading, and self-test orchestration. |
| `kmod` | Kernel module loading and inspection. |
| `util-linux-mount`, `util-linux-lsblk` | Filesystem/configfs mounting and block-device inspection. |
| `iproute2-ip` | Network and RPMsg network inspection. |
| `perf` | Kernel timer/performance validation. |
| `arm-si-rproc-mod` | Safety Island remoteproc support. |
| `kernel-module-virtio-rpmsg-bus` | Virtio RPMsg transport. |
| `rpmsg-net-mod` | RPMsg network BSP path. |
| `pfdi-misc-mod` | Linux PFDI misc-device interface. |
| `pfdi-bsp-app` | PFDI library, sample app, local agent, and test configuration. |

The image deliberately omits package recommendations, demos, cloud services,
OpenSSH, overlayfs, the full root filesystem, and dm-verity. It publishes:

- `nexios-bsp-initramfs-<machine>.cpio.gz`
- A/B UKIs for the single ESP boot partition
- a two-partition WIC containing the ESP and boot-state metadata
- machine-specific `.qboxconf` and `.fvpconf` launch metadata

The UKI command line uses `rdinit=/init` so the BSP init script is selected
even if product root arguments are present elsewhere in the platform boot
configuration.

## Local Build

The local build uses the Yocto SDK as the cross-toolchain provider, but builds
the firmware and kernel from the checked-out sources:

```bash
./local_build.sh
```

The component set is:

```text
qbox tf-m scp-firmware zephyr optee u-boot tf-a linux
buildroot flash-images boot-disk fvpconf debug-manifest
```

Outputs are rooted at `build/local-${MACHINE}`. The reviewed defaults live in
`scripts/build/local_build.conf`; environment values override that file. Use
`$update-local-build-conf` when Yocto machine metadata changes require a
reviewed refresh of those inputs.

The local BSP root filesystem is a Buildroot-generated CPIO, not the Yocto
`nexios-bsp-initramfs` artifact. It reuses `nexios-bsp-init` and the same BSP
self-test contract, and includes BusyBox, kmod, iproute2, util-linux, perf,
iperf, the PFDI applications/library/configuration, and the locally built
`arm_si_rproc`, `rpmsg_net`, and `pfdi_misc` kernel modules.

Local packaging creates:

```text
build/local-apollo-qvp/deploy/initramfs.cpio.gz
build/local-apollo-qvp/deploy/auto-ad-nexios-a.efi
build/local-apollo-qvp/deploy/auto-ad-nexios-b.efi
build/local-apollo-qvp/deploy/boot-fat.img
build/local-apollo-qvp/deploy/apollo-qvp-local-disk.img
build/local-apollo-qvp/debug/symbols.json
```

Useful focused commands:

```bash
./local_build.sh qbox
./local_build.sh qbox --qbox-unit-tests
./local_build.sh linux clean-build --no-package
./local_build.sh debug-manifest --no-package
./local_build.sh --package
```

The QBox overlay build uses `hsoc-stack/tools/qbox-platform` with the
checkout-local QBox core and QEMU sources. Its default aggregate target is
`apollo_fvp_full_system`.

## Run QBox

### Interactive launchers

```bash
./run_qbox_local.sh
./run_qbox_yocto.sh
./run_qbox_yocto.sh --bsp
```

The local launcher boots the Buildroot BSP CPIO through the locally generated
U-Boot EFI disk and A/B UKIs. The Yocto launcher resolves the selected WIC,
firmware, QBox provider, native sysroot, and `.qboxconf` from the matching
machine deploy/work directories.

Both convenience launchers use `--si-mode live-cl0-cl1`, keep QBox alive after
the login/pass marker, and disable the shared runner's post-login probe. Their
purpose is interactive boot/login work; use the canonical Python runner when a
full post-login qualification gate is required.

By default, a new QBox launch stops only managed QBox tmux sessions and
headless processes owned by the current Unix UID. It does not stop another
user's sessions or unrelated tmux sessions. Preserve existing QBox sessions
with:

```bash
./run_qbox_local.sh --multi-session
./run_qbox_yocto.sh --multi-session
```

A duplicate explicit session name is still an error. `--dry-run` never performs
session cleanup.

### Headless and regression execution

Use the canonical runner for structured QBox evidence:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 \
  --timeout 600
```

Expected evidence includes `result.json`, `summary.txt`, the QBox platform log,
and per-domain UART logs. A running process or tmux screen is not boot proof.

The Yocto wrapper can run without tmux:

```bash
./run_qbox_yocto.sh --headless --exit-after-pass
```

Run the timing/error regression wrapper with:

```bash
./run_qbox_boot_regression.sh --record-baseline
./run_qbox_boot_regression.sh
./run_qbox_boot_regression.sh --threshold 0.10
./run_qbox_boot_regression.sh -- --copy-disks
```

The first command creates the required JSON baseline; later invocations compare
stage timing and newly observed error patterns against it. The wrapper launches
QBox headlessly and always terminates its own QBox process group.
`--multi-session` preserves unrelated sessions, but processes that hold the
selected writable image files can still be stopped to prevent image
corruption. To inspect a first-run command without booting, combine
`--record-baseline --dry-run`.

## Debug

### QBox GDB

Both local and Yocto QBox launchers accept one target:

```text
qbox rse si_cl0 si_cl1 tf-a u-boot linux
```

Examples:

```bash
./run_qbox_local.sh --debug qbox
./run_qbox_local.sh --debug linux
./run_qbox_yocto.sh --bsp --debug linux
```

The interactive shell pane becomes the selected GDB session. Yocto QBox debug
requires interactive tmux and therefore rejects `--headless --debug`.
Firmware/AP targets use the component entrypoint from the generated
`symbols.json`; host QBox debugging uses `gdbserver`.

For all QBox domains at once:

```bash
./run_qbox_local_debug.sh
./run_qbox_local_debug.sh --vscode --no-attach
```

Fixed endpoints on `127.0.0.1` are:

| Domain | Port |
| --- | ---: |
| QBox host | 12339 |
| RSE | 12340 |
| Safety Island CL0 | 12341 |
| Safety Island CL1 | 12342 |
| Primary Compute | 12343 |

Normal multi-domain attachment waits for PFDI readiness. Use
`--firmware-early-attach` or `--ap-early-attach` only when the earlier handoff
itself must be inspected.

### FVP Iris

FVP exposes Iris rather than a native GDB remote stub. The Yocto native
`lite-cornea` package bridges GDB to Iris:

```bash
./run_fvp.sh --machine apollo-qvp --debug linux
./run_fvp.sh --machine apollo-qvp --debug rse --iris-port 7110
```

Supported targets are `rse`, `si_cl0`, `si_cl1`, `tf-a`, `u-boot`, and
`linux`. This debug mode is currently restricted to
`--machine apollo-qvp`.

For locally built `apollo-fvp` firmware, use the direct Iris helper:

```bash
scripts/debug/run_local_fvp_debug.sh \
  --no-attach \
  --iris-port 7100 \
  --break tfm-bl1_1:Reset_Handler
```

Generate or refresh its manifest with:

```bash
scripts/setup/setup_local_debug_env.py \
  --local-build-dir build/local-apollo-fvp \
  --out-dir build/local-apollo-fvp/debug
```

The manifest covers firmware, TF-A/OP-TEE/U-Boot/Linux, QBox host/core/plugins,
libqemu, and aggregate `domain-*` GDB scripts. Buildroot BusyBox is
intentionally excluded.

## Run FVP and Tests

Build and launch an explicit FVP machine:

```bash
./yocto_build.sh --machine apollo-fvp
./run_fvp.sh
```

`run_fvp.sh` is interactive and writes `runfvp.cmd`, model output, tmux
supervisor state, ports, and per-UART logs under
`build/fvp-tmux/<machine>-<timestamp>/`. It does not create `result.json`.

For a log-backed local FVP qualification:

```bash
python3 scripts/run/runfvp_log_boot.py \
  --machine apollo-fvp \
  --fvpconf build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf \
  --out-dir build/local-apollo-fvp/fvp-boot \
  --timeout 900 \
  --require all \
  --min-runtime 70 \
  --no-login
```

Inspect `result.json`, `summary.txt`, `fvp_stdout.log`, and the subsystem UART
logs before claiming a boot pass.

The higher-level validation wrapper selects categorized FVP suites:

```bash
./run_test.sh --list
./run_test.sh --category basic
./run_test.sh --test <name>
```

It writes a structured result under `build/tests/<timestamp>/` and exits with
`0` for PASS, `1` for FAIL, or `2` for BLOCKED.

## Evidence and Troubleshooting

- Keep QVP runtime evidence under `build/qbox-apollo-qvp/`.
- Keep explicit FVP-comparison QBox evidence under
  `build/qbox-apollo-fvp/` by passing an explicit `--out-dir`.
- Keep local FVP qualification evidence under
  `build/local-apollo-fvp/fvp-boot/`.
- Treat build success, dry-run output, an open tmux pane, and logs from an
  older artifact generation as insufficient runtime evidence.
- For boot failures, inspect file-backed logs first, identify the earliest
  failing domain/handoff, and only then attach GDB or Iris.

Detailed runbooks live under `doc/`, including:

- [Apollo QVP Yocto/QBox runbook](doc/apollo-qvp-yocto-qbox-runbook.md)
- [Local QBox GDB debugging](doc/local-build-gdb-debug.md)
- [FVP Iris debugging](doc/fvp-iris-debugging-guide-ko.md)
- [FVP log-backed boot](doc/fvp-log-boot.md)
- [Source ownership map](doc/source-structure-ko.md)
