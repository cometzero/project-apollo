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
- Current image target: `nexios-image`
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
  `./local_build.sh qbox`,
  `./run_qbox_local.sh`,
  `scripts/build/build_qbox.sh`,
  `scripts/update_codebase_indexes.sh`,
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
  build must not apply these patches automatically; QBox builds should use the
  checked-out `hsoc-stack/tools/qbox/` source unless a task explicitly requests
  applying one of those patches.
- `hsoc-stack/tools/qemu/`: active local QEMU/libqemu source used by QBox.
- `hsoc-stack/tools/buildroot/`: Buildroot source used by local initramfs and
  rootfs generation.
- `scripts/`: categorized project orchestration helpers; root entrypoints
  `yocto_build.sh`, `local_build.sh`, and `run_qbox_local.sh` call into these
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
   - `$update-codebase-indexes` for listing, refreshing, or verifying one or
     all canonical codebase-memory-mcp submodule indexes.
   - `$update-local-build-conf` for explicitly comparing active Yocto recipe
     values and refreshing the manually maintained `local_build.conf`.
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

## Codebase Memory Indexing

Use `codebase-memory-mcp` as the first code-discovery surface for repositories
that have a ready index. Prefer `search_graph`, `trace_path`,
`get_code_snippet`, `query_graph`, and `search_code` before broad filesystem
searches. Check the corresponding `index_status` and indexing coverage before
making exhaustive or negative claims. Read the source directly when coverage
is partial, skipped, excluded, stale, or otherwise uncertain.

### Managed Apollo Component Indexes

The following `hsoc-stack/components/` Git submodules were indexed separately
in `fast` mode. This is the verified snapshot from 2026-07-19:

| Project | Repository path | Nodes | Edges | Status |
| --- | --- | ---: | ---: | --- |
| `apollo-linux` | `hsoc-stack/components/primary_compute/linux` | 2,157,447 | 8,216,469 | ready |
| `apollo-u-boot` | `hsoc-stack/components/primary_compute/u-boot` | 376,014 | 934,469 | ready |
| `apollo-trusted-firmware-a` | `hsoc-stack/components/primary_compute/trusted-firmware-a` | 58,675 | 170,874 | ready |
| `apollo-optee-os` | `hsoc-stack/components/primary_compute/optee_os` | 33,375 | 132,160 | ready |
| `apollo-trusted-firmware-m` | `hsoc-stack/components/system_mgmt/trusted-firmware-m` | 8,385 | 22,901 | ready |
| `apollo-scp-firmware` | `hsoc-stack/components/system_mgmt/scp-firmware` | 98,068 | 257,834 | ready |
| `apollo-zephyr` | `hsoc-stack/components/system_mgmt/zephyrproject/zephyr` | 248,877 | 753,310 | ready |
| `apollo-zephyr-hsoc-src` | `hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src` | 214 | 222 | ready |

### Managed Other Top-Level Submodule Indexes

Every other top-level `.gitmodules` entry also has a ready index. This table
uses the canonical project name for future refreshes:

| Project | Repository path | Nodes | Edges | Status |
| --- | --- | ---: | ---: | --- |
| `build-arm-arm-auto-solutions-arm-zena-css` | `arm-zena-css` | 1,737 | 2,615 | ready |
| `apollo-meta-arm` | `layers/meta-arm` | 1,817 | 2,685 | ready |
| `apollo-meta-bluechi` | `layers/meta-bluechi` | 119 | 117 | ready |
| `apollo-meta-cassini` | `layers/meta-cassini` | 859 | 1,026 | ready |
| `apollo-meta-clang` | `layers/meta-clang` | 672 | 687 | ready |
| `apollo-meta-ewaol` | `layers/meta-ewaol` | 57 | 53 | ready |
| `apollo-meta-mender` | `layers/meta-mender` | 1,539 | 2,959 | ready |
| `apollo-meta-openembedded` | `layers/meta-openembedded` | 9,180 | 10,184 | ready |
| `apollo-meta-ptx` | `layers/meta-ptx` | 69 | 71 | ready |
| `apollo-meta-secure-core` | `layers/meta-secure-core` | 580 | 618 | ready |
| `apollo-meta-security` | `layers/meta-security` | 1,476 | 2,051 | ready |
| `apollo-meta-virtualization` | `layers/meta-virtualization` | 1,119 | 1,293 | ready |
| `apollo-meta-zephyr` | `layers/meta-zephyr` | 510 | 639 | ready |
| `apollo-poky` | `layers/poky` | 18,424 | 79,396 | ready |
| `apollo-sw-ref-stack` | `sw-ref-stack` | 2,020 | 7,481 | ready |
| `apollo-buildroot` | `hsoc-stack/tools/buildroot` | 13,522 | 32,950 | ready |
| `apollo-meta-hsoc-auto-solutions` | `hsoc-stack/yocto/meta-hsoc-auto-solutions` | 216 | 375 | ready |
| `apollo-meta-hsoc-bsp` | `hsoc-stack/yocto/meta-hsoc-bsp` | 305 | 370 | ready |
| `apollo-qbox` | `hsoc-stack/tools/qbox` | 9,033 | 28,146 | ready |
| `apollo-qbox-platform` | `hsoc-stack/tools/qbox-platform` | 5,057 | 14,543 | ready |
| `apollo-qemu` | `hsoc-stack/tools/qemu` | 138,058 | 670,087 | ready |
| `apollo-hsoc-tests` | `hsoc-stack/tests` | 251 | 931 | ready |

All 30 top-level submodule roots were ready on 2026-07-19. The 17 indexes
created in the final expansion added 52,430 nodes and 143,516 edges in
approximately 6.02 seconds. Their DB files total 110,428,160 bytes, and the
largest observed maximum RSS was 799,028 KiB for `apollo-poky`.

Treat `list_projects` as the authoritative inventory and reuse the canonical
name above for the same root. Older overlapping QBox and QBox Platform aliases
exist in local cache state; do not create additional aliases unless a task
explicitly needs a narrower index.

Indexes are local machine state, not Git repository content. The default
storage is:

```text
~/.cache/codebase-memory-mcp/<project>.db
```

At the snapshot above, `apollo-linux.db` is approximately 3.8 GiB. Check free
space on the filesystem containing the cache before a full reindex because
SQLite temporary, WAL, and replacement files can require additional space.

### Refresh Existing Indexes

The CLI does not continuously synchronize source changes. Re-run the same
project name, repository path, and mode after changing or updating a submodule:

```bash
scripts/update_codebase_indexes.sh --list
scripts/update_codebase_indexes.sh --directory layers/meta-arm
scripts/update_codebase_indexes.sh --all
```

The helper preserves the canonical mapping above, updates indexes
sequentially, verifies every result, and writes logs plus `summary.tsv` below
`build/codebase-memory-index/<timestamp>/`. Use the direct CLI form only when
debugging or adding a mapping to the helper:

```bash
set -o pipefail

/usr/bin/time -v \
  codebase-memory-mcp cli index_repository \
    --repo-path /build/arm/arm-auto-solutions/hsoc-stack/components/primary_compute/linux \
    --name apollo-linux \
    --mode fast \
  2>&1 | tee /tmp/apollo-linux-index.log
```

With a healthy existing DB and stored file hashes, this routes to incremental
indexing. Unchanged files are reused, changed files are reparsed, deleted files
are purged, and a no-change run exits through the incremental no-op path.
Filesystem discovery and hash comparison still run, so a no-op is not
instantaneous on a large tree.

Confirm the result and route with:

```bash
codebase-memory-mcp cli index_status --project apollo-linux

rg 'pipeline.route|incremental.classify|incremental.noop|incremental.done' \
  ~/.cache/codebase-memory-mcp/logs/.worker-*.log
```

Incremental indexing is not guaranteed when the project name, root path, or
mode changes. A missing or corrupt DB, missing stored hashes, or a discovered
file count more than 50 percent above the stored hash count causes a full
reindex. Keep `fast` mode for the managed top-level submodule indexes unless wider
coverage is explicitly required.

### Add or Remove Index Scope

Use `.gitmodules` as the source of truth for new top-level repositories. Create
one separate `fast` index for each initialized submodule. Use a stable, unique
`apollo-*` project name and record it in the tables above:

```bash
CBM_SUBMODULE_PATH=layers/meta-example
CBM_PROJECT_NAME=apollo-meta-example

codebase-memory-mcp cli index_repository \
  --repo-path "/build/arm/arm-auto-solutions/${CBM_SUBMODULE_PATH}" \
  --name "${CBM_PROJECT_NAME}" \
  --mode fast
```

Index one large component at a time. Record the project name, exact root,
mode, node and edge counts, DB size, elapsed time, maximum RSS, and exit status
before starting another large index. Do not index the aggregate
`hsoc-stack/components/` directory when the submodules are already indexed
individually; that duplicates graph data and increases memory and storage use.

The top-level `.cbmignore` currently contains:

```gitignore
build/
```

This excludes the generated top-level build tree only when the indexed root is
`/build/arm/arm-auto-solutions`. `codebase-memory-mcp` loads `.cbmignore` from
the exact `--repo-path` root; the top-level file does not automatically apply
to separately indexed submodules. Add a submodule-local `.cbmignore` when that
submodule needs extra exclusions. Preserve source directories unless there is
a measured indexing or relevance reason to exclude them.

Changing ignore rules can leave previously indexed, now-excluded files
preserved by an incremental run. When the old nodes must be removed, request
explicit approval, delete the named project, and recreate it with the same
canonical name and intended mode:

```bash
CBM_SUBMODULE_PATH=layers/meta-example
CBM_PROJECT_NAME=apollo-meta-example

codebase-memory-mcp cli delete_project --project "${CBM_PROJECT_NAME}"
codebase-memory-mcp cli index_repository \
  --repo-path "/build/arm/arm-auto-solutions/${CBM_SUBMODULE_PATH}" \
  --name "${CBM_PROJECT_NAME}" \
  --mode fast
```

`delete_project` is destructive local-state cleanup. Never run it merely to
refresh source changes; normal refreshes must use incremental indexing.

### Resource and Coverage Cautions

- The first `apollo-linux` fast index took 12 minutes 10 seconds, reached
  approximately 12.5 GiB maximum RSS, and produced a 3.8 GiB DB. Ensure enough
  RAM, swap, cache filesystem space, and idle CPU before a Linux full reindex.
- Run only one memory-intensive index at a time. Do not run Linux indexing in
  parallel with Yocto, QBox, QEMU, or another large index/build.
- Keep `set -o pipefail` when piping through `tee`; otherwise `tee` can mask an
  indexing failure.
- A `ready` status and matching node counts prove that a DB exists, not that
  every source construct was parsed. Inspect coverage and use direct source
  search for excluded, skipped, or partially parsed paths.
- `apollo-poky` fast mode excludes `scripts/`, `bitbake/bin`, and documentation.
  Read those paths directly or create an explicitly wider index when the task
  depends on BitBake command entrypoints or Poky helper scripts.
- `layers/meta-mender/tests/acceptance/image-tests` and QEMU ROM/test nested
  submodules were not initialized in this snapshot. Their parent indexes are
  ready, but those absent nested sources are not covered.
- Report OOM, signal termination, nonzero exit status, node/edge mismatches, or
  a non-`ready` status as an indexing failure. Do not treat a partial DB as
  current.

## Explicit Apollo FVP Debugging

Use the local debug helpers when a component needs source symbols,
breakpoints, or precise handoff analysis. The local build enables debug
symbols by default:

- Linux: `local_build.sh` enables `CONFIG_DEBUG_INFO`,
  `CONFIG_GDB_SCRIPTS`, and `CONFIG_KALLSYMS_ALL` unless
  `KERNEL_DEBUG_INFO=0` is set.
- Buildroot userspace: `local_build.sh` builds with `BR2_ENABLE_DEBUG=y`,
  `BR2_OPTIMIZE_G=y`, and no target stripping.
- Firmware and boot components are built from their unstripped local build
  ELF files.
- Safety Island CL1 Zephyr is built locally from
  `hsoc-stack/components/system_mgmt/zephyrproject/` by
  `./local_build.sh zephyr` and as part of `./local_build.sh build`.

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

1. Build local images with `./local_build.sh build`, then run normal
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
   - Use `./yocto_build.sh` for the configured `nexios-image` build.
3. QBox build checks:
   - Prefer `./local_build.sh qbox` for the Apollo overlay build contract.
   - Targeted overlay builds use
     `cmake --build build/local-${MACHINE}/work/qbox-platform --target
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
   - For Apollo FVP local boot, build with `./local_build.sh build`, then use
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
