# AGENTS.md

This workspace is an Arm Auto Solutions Yocto/BitBake tree and a QBox
co-simulation development workspace. The top-level directory is a Git
repository that pins nested source repositories with Git submodules. Source
ownership still lives mostly in those nested repositories, so check and commit
changes at the owning repository boundary.

## Project Mission

Implement the Arm Zena CSS RD-Aspen/Apollo FVP behavior in QBox with
SystemC/TLM/QEMU so the QBox virtual platform is functionally equivalent to Arm
FVP for the active `apollo-fvp` configuration. The target is high-fidelity
emulation, not driver-only shims: prefer real SystemC/TLM or libqemu-backed
hardware models over register-only stubs.

## Active Baseline

- Active Yocto build directory: `build/`
- Active Yocto template: `hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-fvp/`
- Build entrypoint: `./yocto_build.sh`
- Current machine: `apollo-fvp`
- Current variant: `RD_ASPEN_VARIANT = "cfg2"`
- Current configured CPU count: `PC_CPUS_COUNT_DEFAULT = "4"`
- Apollo Safety Island Zephyr workspace:
  `hsoc-stack/components/system_mgmt/zephyrproject/`
- QBox core under active development:
  `hsoc-stack/tools/qbox/`
- QBox platform under active development:
  `hsoc-stack/tools/qbox-platform/platforms/apollo/`
- QBox-local QEMU/libqemu under active development:
  `hsoc-stack/tools/qemu/`
- QBox helper scripts:
  `./local-build.sh qbox`,
  `scripts/build/build_qbox.sh`,
  `scripts/package.sh`,
  `scripts/test/validate_qbox_apollo_fvp_full_map.py`,
  `scripts/run/run_qbox_apollo_fvp_full.py`,
  `scripts/run/run_qbox_fvp_rd_aspen_rse.py`,
  `scripts/test/audit_qbox_apollo_fvp_full_coverage.py`,
  `scripts/run/run_qbox_apollo_fvp_linux.py`

## Source Boundaries

- `arm-zena-css/`: Arm Zena CSS BSP, RD-Aspen FVP docs, firmware, and Safety
  Island sources.
- `sw-ref-stack/`: Arm Automotive Solutions images, demos, test automation,
  and CI fragments.
- `hsoc-stack/components/primary_compute/`: Apollo primary-compute local
  source submodules: Linux, U-Boot, TF-A, OP-TEE, and Buildroot.
- `hsoc-stack/components/system_mgmt/`: Apollo system-management and safety
  local source submodules: TF-M, SCP-firmware, and the Zephyr workspace
  containing `zephyr/` plus `safety_island/`.
- `hsoc-stack/yocto/meta-hsoc-auto-solutions/`: project-owned Apollo distro,
  template, and dynamic-layer metadata.
- `hsoc-stack/yocto/meta-hsoc-bsp/`: project-owned Apollo BSP metadata,
  machine configuration, firmware recipes, kernel metadata, module signing,
  and OP-TEE integration.
- `layers/`: pinned upstream/downstream Yocto layers. Treat as external unless
  explicitly asked to patch them.
- `hsoc-stack/tools/qbox/`: upstream-friendly QBox core, including
  `platforms-vp`, libqbox/libqemu integration, reusable SystemC/TLM
  components, reusable QEMU-backed components, tests, and examples.
- `hsoc-stack/tools/qbox-platform/`: Apollo/RD-Aspen platform overlay,
  including Apollo and RD-Aspen Lua entrypoints, Zena/RSE SystemC models,
  Apollo-specific QEMU wrappers, platform tests, and the
  `apollo_fvp_full_system` aggregate target. Patch files under
  `hsoc-stack/tools/qbox-platform/patch-qbox/` are archived candidate
  QBox-core patches for later manual review or application. The normal local
  build must not apply these patches automatically; QBox builds should use the
  checked-out `hsoc-stack/tools/qbox/` source unless a task explicitly requests
  applying one of those patches.
- `hsoc-stack/tools/qemu/`: active local QEMU/libqemu source used by QBox.
- `scripts/`: categorized project orchestration helpers; root entrypoints
  `yocto_build.sh`, `local-build.sh`, and `run_qbox.sh` call into these
  helpers.
- `tests/`: repository-local tests for Python tooling and QBox helper logic.
- `build/conf/`: active local Yocto build configuration.
- `build/` other than `build/conf/`: generated evidence only. Do not treat as
  source.
- `doc/`: project analysis, implementation plans, and verification reports.
- `.codex/`: project-local Codex skills and sub-agent definitions.

## Required Working Style

1. Inspect before editing. Read `build/conf/local.conf`,
   `build/conf/bblayers.conf`, and `build/conf/templateconf.cfg` before any
   Yocto build/runtime claim.
2. Use project-local skills when relevant:
   - `$arm-auto-solutions` for workspace routing and evidence standards.
   - `$qbox-dev` for QBox/SystemC/QEMU virtual platform work.
   - `$systemc-dev` for SystemC/TLM component implementation or review.
   - `$yocto-dev` / `$yocto-review` for Yocto metadata work.
   - `$linux-kernel-review` for kernel, DTS, Kconfig, driver, HIPC, RPMsg,
     remoteproc, or PFDI Linux work.
3. Keep changes scoped to the owning repository or project-local docs. For
   example, kernel source changes belong in
   `hsoc-stack/components/primary_compute/linux`, QBox model changes belong in
   `hsoc-stack/tools/qbox`, QBox platform changes belong in
   `hsoc-stack/tools/qbox-platform`, and top-level workflow docs belong in
   this repository.
4. Preserve user changes. Do not reset nested repos or generated state unless
   explicitly requested.
5. Prefer log and artifact based validation over tmux-only screen output.
6. For complex boot failures, debug in this order: log-based triage first,
   then symbol/source-level debugging with GDB and FVP Iris only after logs
   identify the likely component or handoff.
7. For implementation and problem analysis involving Arm Zena CSS hardware or
   software structure, consult `doc/arm_zena_css_dev_guide/` early. Use it for
   memory maps, register maps, boot flows, firmware/domain responsibilities,
   and other hardware/software interface details before changing code.

## Apollo FVP Debugging

Use the local debug helpers when a component needs source symbols,
breakpoints, or precise handoff analysis. The local build enables debug
symbols by default:

- Linux: `local-build.sh` enables `CONFIG_DEBUG_INFO`,
  `CONFIG_GDB_SCRIPTS`, and `CONFIG_KALLSYMS_ALL` unless
  `KERNEL_DEBUG_INFO=0` is set.
- Buildroot userspace: `local-build.sh` builds with `BR2_ENABLE_DEBUG=y`,
  `BR2_OPTIMIZE_G=y`, and no target stripping.
- Firmware and boot components are built from their unstripped local build
  ELF files.
- Safety Island CL1 Zephyr is built locally from
  `hsoc-stack/components/system_mgmt/zephyrproject/` by
  `./local-build.sh zephyr` and as part of `./local-build.sh build`.

Generate or refresh the debug manifest after a local build:

```bash
scripts/setup/setup_local_debug_env.py \
  --local-build-dir build/local-apollo-fvp \
  --out-dir build/local-apollo-fvp/debug
```

The generated `build/local-apollo-fvp/debug/symbols.json` records the ELF,
architecture, FVP Iris target, and default breakpoint symbols for:

- TF-M BL1_1, BL1_2, BL2, and secure runtime on the RSE CPU.
- SCP-firmware on Safety Island cluster 0.
- Safety Island cluster 1 Zephyr demo.
- TF-A BL2 and BL31.
- OP-TEE core.
- U-Boot.
- Linux `vmlinux`.
- Buildroot BusyBox initramfs userspace.

Use GDB first for symbol/source inspection:

```bash
gdb-multiarch -x build/local-apollo-fvp/debug/gdb/u-boot.gdb
gdb-multiarch -x build/local-apollo-fvp/debug/gdb/linux.gdb
```

`FVP_Zena_CSS_Cfg2` exposes an Iris debug server rather than a GDB remote
stub. Use Iris or an Iris-capable debugger for live target control. For
command-line breakpoint smoke tests:

```bash
scripts/debug/run_local_fvp_debug.sh --no-attach --iris-port 7100 \
  --break tfm-bl1_1:Reset_Handler
```

When setting breakpoints manually, use component names and symbols from
`symbols.json`, for example `u-boot:board_init_f`, `linux:start_kernel`,
`tfa-bl31:bl31_main`, `scp-si0:arch_exception_reset`, or
`tfm-bl1_1:Reset_Handler`.

Boot issue escalation path:

1. Build local images with `./local-build.sh build`, then run normal
   log-backed boot validation with:
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
2. Inspect `build/local-apollo-fvp/fvp-boot/result.json`,
   `summary.txt`, `fvp_stdout.log`, and the per-UART logs for RSE,
   Safety Island CL0/CL1, TF-A, and U-Boot/Linux.
3. Identify the earliest failing domain or firmware handoff from those logs.
4. Refresh `build/local-apollo-fvp/debug/symbols.json`.
5. Reproduce with `scripts/debug/run_local_fvp_debug.sh --break <component:symbol>`
   or attach an Iris debugger to the reported Iris port.
6. Use GDB command files to confirm symbol addresses, source paths, and
   expected breakpoint locations before changing code.

## FVP-To-QBox Implementation Rules

For each hardware block or IP:

1. Inventory the FVP-visible behavior from local RD-Aspen sources first:
   `doc/arm_zena_css_dev_guide/`, `arm-zena-css/documentation/`, machine
   config, FVP include files, generated DTB/DTS, firmware logs, and existing
   FVP boot logs.
2. Check official Arm documentation and TRMs for programming model, reset
   values, interrupts, register layout, timing assumptions, and integration
   constraints. Record document version and URL in the implementation notes.
3. Search for existing open-source SystemC/TLM models before writing a new
   model. Prefer permissive, upstream-friendly code and respect licenses.
4. Prefer real SystemC/TLM behavior or libqemu-backed models over stubs.
   Register-only stubs are temporary compatibility debt and must be documented
   with missing behavior and a replacement plan.
5. Preserve QBox conventions: C++14, SystemC/TLM-2.0, CCI parameters, Lua
   platform configuration, CMake target style, TLM socket direction, QEMU
   `QemuInstance` usage, and log-based test evidence.
6. Keep FVP/QBox memory maps, IRQ lines, device tree expectations, boot
   artifacts, and Linux driver evidence aligned.

## Apollo Timer Topology

Apollo QBox timer work must preserve the Arm Zena CSS split between CPU
internal timers and platform REFCLK timer frames:

- CPU internal Arm generic timers remain per-core PPI devices owned by the
  QEMU `ARMCPU` path. Do not replace the per-core PPI wiring with a platform
  MMIO timer.
- AP REFCLK is a 125MHz Arm memory-mapped generic timer exposed through the
  reusable Arm MMIO QEMU/QBox path. Apollo AP REFCLK must not use
  `qemu_hexagon_qtimer`, `qct-qtimer`, or a `qct-qtimer` compatibility alias.
- AP REFCLK frame 0 is the non-secure `AP_SYS_CNT_BASE_NS` view and uses
  SPI 49.
- AP REFCLK frame 1 is the secure `AP_SYS_CNT_BASE_S` view and uses SPI 48.
- SI0, CSS, and RSE counter windows use the `host_gtimer` control/read/sync
  frame model where firmware expects REFCLK counter behavior. Do not model
  these windows as broad inert memory unless the missing behavior is recorded
  as explicit fidelity debt.

## Validation Ladder

Use the narrowest meaningful command first, then broaden only when needed.

1. Static checks:
   - `python3 -m py_compile scripts/*/*.py` for changed Python helpers.
   - `git -C hsoc-stack/tools/qbox diff --check` for QBox core changes.
   - `python3 scripts/test/validate_qbox_apollo_fvp_full_map.py`
   - `python3 scripts/test/audit_qbox_core_boundary.py`
2. Yocto build checks:
   - Initialize with `source layers/poky/oe-init-build-env build`.
   - Use `bitbake-layers show-layers` when layer order changes.
   - Use targeted tasks first, such as
     `bitbake <recipe> -c configure` or `bitbake <recipe> -c compile`.
   - Use `./yocto_build.sh` for the configured `baremetal-image` build.
3. QBox build checks:
   - Prefer `./local-build.sh qbox` for the Apollo overlay build contract.
   - Targeted overlay builds use
     `cmake --build build/local-apollo-fvp/work/qbox-platform --target
     <target> --parallel <n>`.
   - Build `platforms-vp` from the qbox-platform build directory when Lua
     platform wiring changes.
4. Runtime checks:
   - For Apollo full-system local-build boot on QBox, use
     `python3 scripts/run/run_qbox_apollo_fvp_full.py --si-mode
     live-cl0-cl1 --timeout 600` and inspect
     `build/qbox-apollo-fvp/full-<timestamp>/`.
   - Use `--keep-running-after-pass` only for interactive demos that should not
     exit after the boot pass condition.
   - For Apollo local-build Primary Compute direct boot on QBox, use
     `python3 scripts/run/run_qbox_apollo_fvp_linux.py --timeout 600` and
     inspect `build/qbox-apollo-fvp/<timestamp>/`.
   - Use `scripts/run/run_qbox_fvp_rd_aspen_rse.py` only as the lower-level
     RSE/RD-Aspen compatibility runner when focused RSE evidence is needed.
   - For Apollo FVP local boot, build with `./local-build.sh build`, then use
     `python3 scripts/run/runfvp_log_boot.py --machine apollo-fvp --fvpconf
     build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf --out-dir
     build/local-apollo-fvp/fvp-boot --timeout 900 --require all
     --min-runtime 70 --no-login` and inspect
     `build/local-apollo-fvp/fvp-boot/result.json` plus per-UART logs before
     using GDB/Iris.
5. Coverage checks:
   - Run `python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py
     --result-json <runtime-result.json>
     --output build/qbox-apollo-fvp/full-coverage-audit.json` after Apollo
     full-system runtime checks.
6. FVP comparison:
   - Use non-interactive FVP log scripts and compare boot, memory-map, IRQ,
     device-tree, driver probe, and service evidence.

## Documentation Requirements

When adding or replacing a hardware model, update project-local evidence:

- `doc/qbox-fvp-emulation-project.md` for roadmap/status changes.
- `hsoc-stack/tools/qbox-platform/platforms/apollo/README.md` for Apollo
  platform runtime instructions.
- `build/qbox-apollo-fvp/` only for generated verification reports.

Final reports must include files changed, commands run, static/build/runtime
validation, and explicit blockers or fidelity gaps.
