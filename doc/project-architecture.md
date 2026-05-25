# Project Architecture

Generated: 2026-05-15

## Summary

`/build/arm/arm-auto-solutions` is a kas workspace that combines Arm Zena CSS,
the Arm Automotive Solutions software reference stack, and pinned Yocto layers.
The top-level directory is not itself a Git repository; the source projects are
nested repositories such as `arm-zena-css/`, `sw-ref-stack/`, and `layers/*`.

The current generated configuration selects the Arm Zena CSS RD-Aspen FVP
machine in baremetal mode, CFG2, with demos and UEFI capsule support enabled.
The build output currently contains a successful `baremetal-image` deploy under
`build/tmp_baremetal/deploy/images/fvp-rd-aspen/`.

## Workspace Layout

| Path | Role | Notes |
| --- | --- | --- |
| `arm-zena-css/` | Arm Zena CSS platform repository | Adds RD-Aspen BSP, Safety Island, firmware, docs, and kas fragments. |
| `sw-ref-stack/` | Arm Automotive Solutions software reference stack | Adds EWAOL-based baremetal/virtualization use cases, images, tests, and CI fragments. |
| `layers/` | External Yocto layer checkouts | Contains pinned upstream/downstream layers such as `poky`, `meta-arm`, `meta-openembedded`, `meta-ewaol`, `meta-cassini`, and security/virtualization layers. |
| `build/` | Generated kas/BitBake output | Contains `tmp_baremetal`, deploy images, sstate cache, logs, sysroots, and task metadata. |
| `.config.yaml` | Current generated kas config | Captures the selected menu configuration and include stack. |
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

The current `.config.yaml` selects baremetal only:

- `ARCHITECTURE_BAREMETAL: true`
- `ARCHITECTURE_VIRTUALIZATION: false`
- `USE_CASE_DEMOS: true`
- `RUN_TESTS: false`

These values are visible in `.config.yaml:20`, `.config.yaml:22`,
`.config.yaml:28`, and `.config.yaml:29`.

## Current Configuration

The active generated kas configuration was produced by kas 4.8.1
(`.config.yaml:1`, `.config.yaml:2`) from source directory
`/build/arm/arm-auto-solutions/arm-zena-css` (`.config.yaml:4`). Its include
stack is:

- `yocto/kas/zena-css-bsp.yml`
- `yocto/kas/uefi-capsule.yml`
- `../sw-ref-stack/yocto/kas/baremetal.yml`
- `../sw-ref-stack/yocto/kas/demos.yml`
- `yocto/kas/repos.pinned.yml`

The include list is recorded in `.config.yaml:6` through `.config.yaml:12`.
The selected machine and variant are `MACHINE = "fvp-rd-aspen"` and
`RD_ASPEN_VARIANT = "cfg2"` (`.config.yaml:15`, `.config.yaml:16`). The current
Primary Compute CPU count default is four (`.config.yaml:17`), and Arm FVP EULA
acceptance is set in the generated local config (`.config.yaml:18`).

## Repository Boundary

The top-level workspace is a composition point. Treat these as separate source
ownership zones:

- `arm-zena-css/` owns platform-specific BSP, Safety Island, firmware, kas, and
  Zena documentation.
- `sw-ref-stack/` owns shared Arm Automotive Solutions images, image features,
  demos, test automation, and CI orchestration.
- `layers/` contains third-party or upstream layers, often patched by kas.
- `build/` is disposable/generated unless the user explicitly asks to inspect
  local build evidence.

For Codex work, prefer adding project-local analysis or automation under
`doc/`, `.codex/`, or `.omx/` unless the requested change explicitly targets a
source repository.
