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
| `hsoc-stack/tools/buildroot/` | Retained Buildroot source; not part of the supported root build flow. |
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
| `./yocto_build.sh` | Build the full `nexios-image`. |
| `./yocto_build.sh --bsp` | Build only the minimal Yocto BSP initramfs image. |
| `./run_qbox_yocto.sh` | Boot the Yocto full product image on QBox. |
| `./run_qbox_yocto.sh --bsp` | Boot the Yocto BSP initramfs WIC on QBox. |
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

The default build selects only the product image:

```bash
./yocto_build.sh
```

Equivalent BitBake target selection:

```text
MACHINE=apollo-qvp bitbake nexios-image
```

Build only the fast BSP validation image with:

```bash
./yocto_build.sh --bsp
```

This selects only `nexios-bsp-initramfs`. The BSP recipe owns its non-verity
policy and clears the product initramfs and dm-verity dependencies without a
wrapper environment override.

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

The wrapper can run the same targeted tasks while preserving `build/conf`:

```bash
./yocto_build.sh virtual/kernel -c menuconfig
./yocto_build.sh virtual/bootloader -c cleansstate
```

For an Agent-run Apollo kernel defconfig update, enter the Yocto environment
and use the `$yocto-dev` skill helper:

```bash
workspace_dir="$PWD"
source layers/poky/oe-init-build-env build
MACHINE=apollo-qvp \
  "$workspace_dir/.codex/skills/yocto-dev/scripts/update_kernel_defconfig.sh" \
  CONFIG_IKCONFIG=y CONFIG_PROC_FS=y CONFIG_IKCONFIG_PROC=y
```

The helper resolves Kconfig dependencies in `${B}/.config`, verifies each
requested state, and updates the machine source defconfig. It accepts `y`,
`m`, and `n` and does not build an image.

Normal image builds through `yocto_build.sh` refresh `build/conf/` from the
selected template by default. Explicit target tasks preserve it automatically;
use `--keep-conf` to preserve it during a normal image build. The script writes
`build/conf/apollo-bitbake-resources.conf` and derives BitBake parallelism from
host memory. Override it with
`APOLLO_BUILD_THREADS`, `APOLLO_PARALLEL_MAKE`, or
`APOLLO_AUTO_RESOURCE_LIMITS=0`.

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

## Run QBox

### Interactive launchers

```bash
./run_qbox_yocto.sh
./run_qbox_yocto.sh --bsp
```

The Yocto launcher resolves the selected WIC,
firmware, QBox provider, native sysroot, and `.qboxconf` from the matching
machine deploy/work directories.

The convenience launcher uses the fixed full Safety Island topology, keeps
QBox alive after the login/pass marker, and disables the shared runner's
post-login probe. Its purpose is interactive boot/login work; use the
canonical Python runner when a full post-login qualification gate is required.

By default, a new QBox launch stops only managed QBox tmux sessions and
headless processes owned by the current Unix UID. It does not stop another
user's sessions or unrelated tmux sessions. Preserve existing QBox sessions
with:

```bash
./run_qbox_yocto.sh --multi-session
```

A duplicate explicit session name is still an error. `--dry-run` never performs
session cleanup.

### Headless and regression execution

Use the Yocto wrapper for structured QBox evidence:

```bash
./run_qbox_yocto.sh --headless --exit-after-pass
```

Expected evidence includes `result.json`, `summary.txt`, the QBox platform log,
and per-domain UART logs. A running process or tmux screen is not boot proof.

The Yocto wrapper can run without tmux:

```bash
./run_qbox_yocto.sh --headless --exit-after-pass
```

## Debug

### QBox GDB

The Yocto QBox launcher accepts one target:

```text
qbox rse si_cl0 si_cl1 tf-a u-boot linux
```

Examples:

```bash
./run_qbox_yocto.sh --bsp --debug linux
```

The interactive shell pane becomes the selected GDB session. Yocto QBox debug
requires interactive tmux and therefore rejects `--headless --debug`.
Firmware/AP targets use the component entrypoint from the generated
`symbols.json`; host QBox debugging uses `gdbserver`.

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

## Run FVP and Tests

Build and launch an explicit FVP machine:

```bash
./yocto_build.sh --machine apollo-fvp
./run_fvp.sh
```

`run_fvp.sh` is interactive and writes `runfvp.cmd`, model output, tmux
supervisor state, ports, and per-UART logs under
`build/fvp-tmux/<machine>-<timestamp>/`. It does not create `result.json`.

For a log-backed Yocto FVP qualification:

```bash
python3 scripts/run/runfvp_log_boot.py \
  --machine apollo-fvp \
  --fvpconf build/tmp_baremetal/deploy/images/apollo-fvp/nexios-image-apollo-fvp.fvpconf \
  --out-dir build/fvp-boot/apollo-fvp \
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
- Keep FVP qualification evidence under `build/fvp-boot/`.
- Treat build success, dry-run output, an open tmux pane, and logs from an
  older artifact generation as insufficient runtime evidence.
- For boot failures, inspect file-backed logs first, identify the earliest
  failing domain/handoff, and only then attach GDB or Iris.

Detailed runbooks live under `doc/`, including:

- [Apollo QVP Yocto/QBox runbook](doc/apollo-qvp-yocto-qbox-runbook.md)
- [FVP Iris debugging](doc/fvp-iris-debugging-guide-ko.md)
- [FVP log-backed boot](doc/fvp-log-boot.md)
- [Source ownership map](doc/source-structure-ko.md)
