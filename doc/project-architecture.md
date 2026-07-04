# Project Architecture

Updated: 2026-07-04

## Summary

`/build/arm/arm-auto-solutions` is the top-level Git repository for the Apollo
FVP workspace. It combines Arm Zena CSS, the Arm Automotive Solutions software
reference stack, local Apollo/HSoC source components, pinned Yocto layers, and
QBox/QEMU co-simulation sources through Git submodules.

The active local configuration selects `MACHINE = "apollo-fvp"` in baremetal
mode, `RD_ASPEN_VARIANT = "cfg2"`, four Primary Compute CPUs, demos, Zephyr,
module signing, and UEFI capsule support. The current traditional Yocto
template is
`hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-fvp/`.

## Workspace Layout

| Path | Role | Notes |
| --- | --- | --- |
| `arm-zena-css/` | Arm Zena CSS platform repository | Adds RD-Aspen BSP, Safety Island integration, firmware, documentation, and historical kas fragments. |
| `sw-ref-stack/` | Arm Automotive Solutions software reference stack | Adds EWAOL-based baremetal/virtualization use cases, images, tests, CI fragments, and HIPC/PFDI integration. |
| `hsoc-stack/components/primary_compute/` | Apollo primary-compute sources | Local source submodules for Linux, U-Boot, TF-A, OP-TEE, and Buildroot. |
| `hsoc-stack/components/system_mgmt/` | Apollo system-management sources | Local source submodules for TF-M, SCP-firmware, and Zephyr Safety Island CL1. |
| `hsoc-stack/yocto/` | Apollo project Yocto metadata | Contains `meta-hsoc-auto-solutions` and `meta-hsoc-bsp` for the active Apollo template, distro, BSP, firmware, kernel, and OP-TEE integration. |
| `layers/` | External Yocto layer checkouts | Contains pinned upstream/downstream layers such as `poky`, `meta-arm`, `meta-openembedded`, `meta-ewaol`, `meta-cassini`, and security/virtualization layers. |
| `hsoc-stack/tools/qbox/` | Active QBox core source | SystemC/TLM/QEMU co-simulation core, reusable QEMU-backed components, reusable SystemC components, and QBox tests. |
| `hsoc-stack/tools/qbox-platform/` | Active Apollo/RD-Aspen QBox platform overlay | Apollo and RD-Aspen Lua platforms, Zena/RSE SystemC models, Apollo-specific QEMU wrappers, platform tests, and `apollo_fvp_full_system`. |
| `hsoc-stack/tools/qemu/` | Active QEMU/libqemu source | Local QEMU/libqemu source consumed by the Apollo QBox local build. |
| `tools/qbox/`, `tools/qbox-platform/`, `tools/qemu/` | Legacy QBox/QEMU checkouts | Retained for comparison and migration history; normal Apollo QBox local builds use `hsoc-stack/tools/`. |
| `scripts/` | Project orchestration helpers | Categorized build, run, setup, debug, inspect, analyze, and test scripts. |
| `tests/` | Repository-local tests | Tests for helper scripts and QBox runner behavior. |
| `build/conf/` | Active Yocto configuration | Generated from the Apollo `TEMPLATECONF` flow and edited as local build configuration. |
| `build/` | Generated BitBake/local/QBox output | Contains local build outputs, deploy images, sstate cache, logs, sysroots, task metadata, and runtime evidence. |
| `.config.yaml` | Historical kas config snapshot | Captures the older menu/kas include stack and should not be treated as the active build entrypoint. |
| `doc/` | Codex-generated analysis | This directory. |
| `.codex/` | Codex project automation | Project expert agent and skill. |
| `.omx/` | OMX runtime state | Ultragoal state and project hook plugin. |

## Product And Platform Model

Arm Zena CSS targets automotive reference systems. The Zena CSS README states
that the project demonstrates automotive use cases with RSE/TF-M, Safety Island,
and Primary Compute firmware using TF-A, U-Boot, OP-TEE, and Trusted Services
aligned with Arm SystemReady Devicetree
(`arm-zena-css/README.md:8`, `arm-zena-css/README.md:10`,
`arm-zena-css/README.md:13`, `arm-zena-css/README.md:16`,
`arm-zena-css/README.md:18`).

The software reference stack README describes Arm Automotive Solutions as a set
of open source components for automotive use cases, with the Primary Compute
subsystem based on EWAOL and supporting baremetal and virtualization
architectures (`sw-ref-stack/README.md:8`, `sw-ref-stack/README.md:10`,
`sw-ref-stack/README.md:14`, `sw-ref-stack/README.md:15`).

The Zena CSS overview gives the architectural split:

- Primary Compute: Cortex-A720AE application processors
  (`arm-zena-css/documentation/overview.rst:20`,
  `arm-zena-css/documentation/overview.rst:137`).
- Safety Island: Cortex-R82AE real-time/safety domain
  (`arm-zena-css/documentation/overview.rst:22`,
  `arm-zena-css/documentation/overview.rst:138`).
- RSE: Cortex-M55 Runtime Security Engine for secure boot and services
  (`arm-zena-css/documentation/overview.rst:25`,
  `arm-zena-css/documentation/overview.rst:139`).

## Architecture Variants

The platform supports baremetal and virtualization modes. Baremetal boots a
single real-time Linux OS on Primary Compute, while virtualization boots Xen and
runs Dom0 plus two DomU guests
(`arm-zena-css/documentation/overview.rst:145`,
`arm-zena-css/documentation/overview.rst:151`,
`arm-zena-css/documentation/overview.rst:154`,
`arm-zena-css/documentation/overview.rst:165`,
`arm-zena-css/documentation/overview.rst:168`).

The historical `.config.yaml` snapshot selects baremetal only:

- `ARCHITECTURE_BAREMETAL: true`
- `ARCHITECTURE_VIRTUALIZATION: false`
- `USE_CASE_DEMOS: true`
- `RUN_TESTS: false`

These values are visible in `.config.yaml:20`, `.config.yaml:22`,
`.config.yaml:28`, and `.config.yaml:29`.

## Current Configuration

The active build uses the traditional Yocto `TEMPLATECONF` path rather than the
old kas-generated entrypoint:

- `build/conf/templateconf.cfg` points to
  `hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-fvp`.
- `build/conf/local.conf` sets `MACHINE = "apollo-fvp"`.
- `build/conf/local.conf` sets `RD_ASPEN_VARIANT = "cfg2"`.
- `build/conf/local.conf` sets `PC_CPUS_COUNT_DEFAULT = "16"`.
- `build/conf/local.conf` enables demos, Zephyr, module signing, capsule
  support, and `DISTRO ??= "ewaol"`.

The Apollo machine metadata in
`hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-fvp.conf` currently inherits
the RD-Aspen FVP machine while keeping `KMACHINE = "apollo-fvp"` and
`ARM_SYSTEMREADY_FIRMWARE = "firmware-apollo-fvp:do_deploy"` for Apollo-specific
growth.

## Repository Boundary

The top-level repository is a composition point. Treat these as separate source
ownership zones and commit at the owning boundary:

- `arm-zena-css/` owns platform-specific BSP, Safety Island, firmware, kas, and
  Zena documentation.
- `sw-ref-stack/` owns shared Arm Automotive Solutions images, image features,
  demos, test automation, and CI orchestration.
- `hsoc-stack/components/primary_compute/*` owns local AP-domain component
  sources.
- `hsoc-stack/components/system_mgmt/*` owns local RSE, SCP, and Safety Island
  CL1 component sources.
- `hsoc-stack/yocto/meta-hsoc-auto-solutions` owns the Apollo distro/template
  layer and dynamic-layer patches.
- `hsoc-stack/yocto/meta-hsoc-bsp` owns the Apollo BSP layer, machine, firmware
  recipes, kernel metadata, and secure-world integration.
- `hsoc-stack/tools/qbox/` owns reusable QBox core changes.
- `hsoc-stack/tools/qbox-platform/` owns Apollo/RD-Aspen platform models,
  Lua wiring, and Apollo-specific QEMU wrappers.
- `hsoc-stack/tools/qemu/` owns the local libqemu/QEMU source consumed by the
  Apollo QBox local build.
- `layers/` contains third-party or upstream layers, often patched by kas.
- `build/conf/` is active local configuration; other `build/` paths are
  disposable/generated unless the user explicitly asks to inspect local build
  evidence.

For Codex work, prefer adding project-local analysis or automation under
`doc/`, `.codex/`, or `.omx/` unless the requested change explicitly targets a
source repository.
