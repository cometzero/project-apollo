# AGENTS.md

This workspace is an Arm Auto Solutions Yocto/BitBake tree and a QBox
co-simulation development workspace. The top-level directory is a Git
repository that pins nested source repositories with Git submodules. Source
ownership still lives mostly in those nested repositories, so check and commit
changes at the owning repository boundary.

## Project Mission

Implement the Arm Zena CSS RD-Aspen/Apollo reference behavior in QBox with
SystemC/TLM/QEMU so the active Apollo QVP is functionally comparable to Arm
FVP. The target is high-fidelity emulation, not driver-only shims: prefer real
SystemC/TLM or libqemu-backed hardware models over register-only stubs.

## Active Baseline

- Active Yocto build directory: `build/`
- Active Yocto template: `hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp/`
- Build entrypoint: `./yocto_build.sh`
- Current machine: `apollo-qvp`
- Product build: `./yocto_build.sh`
- BSP-only build: `./yocto_build.sh --bsp`
- Current BitBake TMPDIR: `build/tmp_baremetal`
- Current variant: `RD_ASPEN_VARIANT = "cfg2"`
- Current configured CPU count: `PC_CPUS_COUNT_DEFAULT = "4"`
- Arm FVP role: explicit reference, comparison, and source-level debug only;
  it is not the active Yocto machine.
- Apollo Safety Island Zephyr workspace:
  `hsoc-stack/components/system_mgmt/zephyrproject/` containing `zephyr/` and
  `zephyr_hsoc_src/`
- QBox core under active development:
  `hsoc-stack/tools/qbox/`
- QBox platform under active development:
  `hsoc-stack/tools/qbox-platform/platforms/apollo/`
- QBox-local QEMU/libqemu under active development:
  `hsoc-stack/tools/qemu/`
- QBox helper scripts:
  `./run_qbox_yocto.sh`,
  `./run_fvp.sh`,
  `./run_test.sh`,
  `scripts/update_codebase_indexes.sh`,
  `scripts/test/validate_qbox_apollo_fvp_full_map.py`,
  `scripts/run/run_qbox_apollo_fvp_full.py`,
  `scripts/test/audit_qbox_apollo_fvp_full_coverage.py`

## Source Boundaries

- `arm-zena-css/`: externally managed, read-only Arm Zena CSS BSP, RD-Aspen
  FVP docs, firmware, and Safety Island sources. Never create commits in this
  repository. Keep Apollo/QVP-specific changes in the project-owned
  `hsoc-stack/` repositories or top-level tooling instead.
- `sw-ref-stack/`: Arm Automotive Solutions images, demos, test automation,
  and CI fragments.
- `hsoc-stack/components/primary_compute/`: Apollo primary-compute local
  source submodules: Linux, U-Boot, TF-A, and OP-TEE.
- `hsoc-stack/components/system_mgmt/`: Apollo system-management and safety
  local source submodules: TF-M, SCP-firmware, and the Zephyr workspace
  containing `zephyr/` plus `zephyr_hsoc_src/`.
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
  Yocto build must not apply these patches automatically; QBox builds use the
  checked-out `hsoc-stack/tools/qbox/` source through
  `qbox-apollo-qvp-native` unless a task explicitly requests applying one of
  those patches.
- `hsoc-stack/tools/qemu/`: active local QEMU/libqemu source used by QBox.
- `hsoc-stack/tools/buildroot/`: retained Buildroot source; it is not part of
  the supported root build workflow.
- `scripts/`: categorized project orchestration helpers; root entrypoints
  `yocto_build.sh`, `run_qbox_yocto.sh`, `run_fvp.sh`, and `run_test.sh`
  call into these helpers.
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
   - `$update-codebase-indexes` for listing, refreshing, or verifying one or
     all canonical codebase-memory-mcp submodule indexes.
   When delegating, pass the exact registered role as `agent_type`; a
   `task_name` or role name in the message does not select its TOML model.
   The registrations and default model are in `.codex/config.toml`. If the
   active spawn surface has no `agent_type` field, keep the work in the
   `gpt-5.6-sol` project leader and do not claim that a specialist model ran.
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
8. Distinguish the build products:
   - `./yocto_build.sh` builds the full `nexios-image` product image.
   - `./yocto_build.sh --bsp` builds only `nexios-bsp-initramfs`.
9. QBox launchers replace only managed QBox tmux sessions and headless
   processes owned by the current Unix UID. Use `--multi-session` when existing
   QBox sessions must be preserved. Never broaden cleanup to other users or
   unrelated tmux sessions.
10. Treat `run_qbox_yocto.sh` as an interactive boot/login launcher: it
    intentionally disables the shared runner's
    post-login probe. Use the canonical Python runner for a full
    post-login qualification gate.

## Codebase Memory Indexing

Use `codebase-memory-mcp` as the first discovery surface when the owning
repository has a ready index. Prefer graph search, path tracing, exact snippets,
and indexed code search before broad filesystem scans. `list_projects` is the
authoritative inventory; do not copy node counts, branch names, or readiness
snapshots into project documentation because they are local, time-varying
state.

Check `index_status` and coverage for every path behind an exhaustive or
negative claim. Read the source directly when coverage is partial, skipped,
excluded, stale, or absent. A ready database proves that an index exists, not
that every construct was parsed.

Refresh the canonical project mapping with:

```bash
scripts/update_codebase_indexes.sh --list
scripts/update_codebase_indexes.sh --directory layers/meta-arm
scripts/update_codebase_indexes.sh --all
```

The helper updates indexes sequentially, verifies results, and writes
`summary.tsv`, command logs, and per-project `<project>-progress.log` files
below `build/codebase-memory-index/<timestamp>/`. The progress log follows the
new worker log created for that sequential request, so keep the documented
no-parallel-index rule in place. Never refresh the large Linux index in
parallel with Yocto, QBox, QEMU, or another memory-intensive index. Deleting
and recreating a project is destructive local-state cleanup and requires
explicit approval; normal source updates use the incremental refresh path.

## Explicit Apollo FVP Debugging

Build the selected Yocto machine before debugging. Firmware and kernel ELFs
come from the matching BitBake work directories, and the launcher generates a
run-local debug manifest from those artifacts.

`FVP_Zena_CSS_Cfg2` exposes an Iris debug server rather than a GDB remote
stub. Yocto QVP debug uses `lite-cornea` as the GDB-to-Iris bridge:

```bash
./run_fvp.sh --machine apollo-qvp --debug linux
```

When setting breakpoints manually, use component names and symbols from
`symbols.json`, for example `u-boot:board_init_f`, `linux:start_kernel`,
`tfa-bl31:bl31_main`, `scp-si0:arch_exception_reset`, or
`tfm-bl1_1:Reset_Handler`.

Boot issue escalation path:

1. Build the Yocto FVP image with `./yocto_build.sh --machine apollo-fvp`,
   then run normal
   log-backed boot validation with:
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
2. Inspect `build/fvp-boot/apollo-fvp/result.json`,
   `summary.txt`, `fvp_stdout.log`, and the per-UART logs for RSE,
   Safety Island CL0/CL1, TF-A, and U-Boot/Linux.
3. Identify the earliest failing domain or firmware handoff from those logs.
4. Reproduce with `./run_fvp.sh --machine apollo-qvp --debug <target>` or
   attach an Iris debugger to the reported Iris port.
5. Use the generated GDB command files to confirm symbol addresses, source
   paths, and expected breakpoint locations before changing code.

## QBox Build, Run, and Debug Contracts

Build the BSP or product, including the Yocto-native QBox provider, with:

```bash
./yocto_build.sh --bsp
./yocto_build.sh
```

Interactive boot/login launchers:

```bash
./run_qbox_yocto.sh
./run_qbox_yocto.sh --bsp
```

`--bsp` selects the deployed Yocto `nexios-bsp-initramfs` WIC/qboxconf and
expects
`NEXIOS_BSP_INITRAMFS_READY` and `nexios-bsp#` for BSP login.

Supported single-target GDB selections are `qbox`, `rse`, `si_cl0`, `si_cl1`,
`tf-a`, `u-boot`, and `linux`:

```bash
./run_qbox_yocto.sh --bsp --debug linux
```

Yocto QBox debug requires interactive tmux and rejects `--headless --debug`.

Normal QBox launchers stop only managed sessions/processes owned by the
current UID. `--multi-session` preserves existing QBox sessions. An explicit
duplicate session name remains an error, and dry-run never performs cleanup.

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
   - Use `bitbake nexios-bsp-initramfs -c rootfs` for BSP userspace changes.
   - Use `./yocto_build.sh --bsp` for a BSP-only image build.
   - Use `./yocto_build.sh` for the full product image build.
3. QBox build checks:
   - Use `./yocto_build.sh --bsp` for the BSP and its native QBox provider.
   - Use `./yocto_build.sh qbox-apollo-qvp-native -c compile` for a targeted
     provider compile.
   - Run provider unit tests through the recipe `do_check` task when QBox
     component behavior changes.
4. Runtime checks:
   - For Apollo full-system Yocto boot on QBox, use
     `./run_qbox_yocto.sh --headless --exit-after-pass` and inspect
     `build/qbox-apollo-qvp/yocto-*/`.
   - For an interactive Yocto BSP shell, use
     `./run_qbox_yocto.sh --bsp` and require
     `NEXIOS_BSP_INITRAMFS_READY` plus `nexios-bsp#`.
   - Use `--keep-running-after-pass` only for interactive demos that should not
     exit after the boot pass condition.
   - For focused source-level debug evidence, use
     `./run_qbox_yocto.sh --debug <target> --debug-mode probe`.
   - For Apollo FVP boot, build with
     `./yocto_build.sh --machine apollo-fvp`, then use
     `python3 scripts/run/runfvp_log_boot.py --machine apollo-fvp --fvpconf
     build/tmp_baremetal/deploy/images/apollo-fvp/nexios-image-apollo-fvp.fvpconf
     --out-dir build/fvp-boot/apollo-fvp --timeout 900 --require all
     --min-runtime 70 --no-login` and inspect
     `build/fvp-boot/apollo-fvp/result.json` plus per-UART logs before
     using GDB/Iris.
5. Coverage checks:
   - Run `python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py
     --result-json <runtime-result.json>
     --output build/qbox-apollo-qvp/full-coverage-audit.json` after active QVP
     full-system runtime checks.
6. FVP comparison:
   - Use non-interactive FVP log scripts and compare boot, memory-map, IRQ,
     device-tree, driver probe, and service evidence.
7. Root workflow checks:
   - Use `./run_test.sh --list` to inspect the categorized FVP suite.

## Documentation Requirements

When adding or replacing a hardware model, update project-local evidence:

- `doc/qbox-fvp-emulation-project.md` for roadmap/status changes.
- `hsoc-stack/tools/qbox-platform/platforms/apollo/README.md` for Apollo
  platform runtime instructions.
- `build/qbox-apollo-qvp/` for active QVP generated verification reports.
- `build/qbox-apollo-fvp/` for explicit FVP-comparison QBox reports when an
  explicit output directory selects that root.

Final reports must include files changed, commands run, static/build/runtime
validation, and explicit blockers or fidelity gaps.
