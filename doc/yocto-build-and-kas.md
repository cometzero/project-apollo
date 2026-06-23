# Yocto Build And Kas Analysis

Generated: 2026-05-15

## Summary

The build is driven by kas YAML fragments from both `arm-zena-css/yocto/kas`
and `sw-ref-stack/yocto/kas`. The current generated `.config.yaml` composes the
Zena BSP, UEFI capsule support, baremetal architecture, demos, and pinned
release SHAs. The upstream baremetal kas fragment selects `baremetal-image`;
the active project entrypoint now builds the Apollo `nexios-image` target for
the `auto-ad-nexios` distro.

## Current Include Stack

The generated config records the active include stack:

1. `arm-zena-css/yocto/kas/zena-css-bsp.yml`
2. `arm-zena-css/yocto/kas/uefi-capsule.yml`
3. `sw-ref-stack/yocto/kas/baremetal.yml`
4. `sw-ref-stack/yocto/kas/demos.yml`
5. `arm-zena-css/yocto/kas/repos.pinned.yml`

Evidence: `.config.yaml:6` through `.config.yaml:12`.

This stack means the current workspace is not a generic build; it is a pinned
RD-Aspen baremetal build with demos and UEFI capsule generation enabled.

## Base Repositories

`sw-ref-stack/yocto/kas/base.yml` sets default repository branch `walnascar` and
defines core layers such as `poky` and `meta-openembedded`
(`sw-ref-stack/yocto/kas/base.yml:14`,
`sw-ref-stack/yocto/kas/base.yml:16`,
`sw-ref-stack/yocto/kas/base.yml:19`,
`sw-ref-stack/yocto/kas/base.yml:26`).

`arm-zena-css/yocto/kas/zena-base.yml` also defaults repositories to
`walnascar`, defines the core `poky` and `meta-openembedded` sources, and adds
disk space guardrails via `BB_DISKMON_DIRS`
(`arm-zena-css/yocto/kas/zena-base.yml:16`,
`arm-zena-css/yocto/kas/zena-base.yml:18`,
`arm-zena-css/yocto/kas/zena-base.yml:20`,
`arm-zena-css/yocto/kas/zena-base.yml:33`,
`arm-zena-css/yocto/kas/zena-base.yml:39`).

## Zena BSP Layer Composition

`zena-css-bsp.yml` includes `zena-base.yml`, enables the local Zena layers, adds
`meta-arm`, `meta-ptx`, `meta-clang`, and `meta-zephyr`, and carries many
platform patches against `meta-arm`
(`arm-zena-css/yocto/kas/zena-css-bsp.yml:8`,
`arm-zena-css/yocto/kas/zena-css-bsp.yml:10`,
`arm-zena-css/yocto/kas/zena-css-bsp.yml:15`,
`arm-zena-css/yocto/kas/zena-css-bsp.yml:17`,
`arm-zena-css/yocto/kas/zena-css-bsp.yml:20`,
`arm-zena-css/yocto/kas/zena-css-bsp.yml:189`,
`arm-zena-css/yocto/kas/zena-css-bsp.yml:193`,
`arm-zena-css/yocto/kas/zena-css-bsp.yml:197`).

The same fragment exposes important environment-controlled build knobs:

- `ARM_FVP_EULA_ACCEPT`
- `RD_ASPEN_VARIANT`
- `RD_ASPEN_RTL_VARIANT`
- `PFDI_SUPPORT`
- `PFDI_MONITOR_SUPPORT`
- `ASPEN_FVP_PATH`
- `CAPSULE_*`

Evidence: `arm-zena-css/yocto/kas/zena-css-bsp.yml:205` through
`arm-zena-css/yocto/kas/zena-css-bsp.yml:222`.

## Shared Automotive Stack Composition

`sw-ref-stack/yocto/kas/arm-auto-solutions.yml` includes EWAOL and the shared
base fragment, adds the local `meta-arm-auto-solutions` layer, and integrates
`meta-arm` toolchain layers
(`sw-ref-stack/yocto/kas/arm-auto-solutions.yml:8`,
`sw-ref-stack/yocto/kas/arm-auto-solutions.yml:10`,
`sw-ref-stack/yocto/kas/arm-auto-solutions.yml:11`,
`sw-ref-stack/yocto/kas/arm-auto-solutions.yml:13`,
`sw-ref-stack/yocto/kas/arm-auto-solutions.yml:42`,
`sw-ref-stack/yocto/kas/arm-auto-solutions.yml:44`,
`sw-ref-stack/yocto/kas/arm-auto-solutions.yml:47`,
`sw-ref-stack/yocto/kas/arm-auto-solutions.yml:50`).

It also adjusts Cassini/EWAOL feature composition by removing security, OTA,
and Parsec features while appending `cassini-dev` and `zephyr`
(`sw-ref-stack/yocto/kas/arm-auto-solutions.yml:69`,
`sw-ref-stack/yocto/kas/arm-auto-solutions.yml:71`,
`sw-ref-stack/yocto/kas/arm-auto-solutions.yml:72`,
`sw-ref-stack/yocto/kas/arm-auto-solutions.yml:73`).

## Baremetal Build Path

`sw-ref-stack/yocto/kas/baremetal.yml` includes the shared automotive stack,
secure signing, and UEFI capsule support. It sets `TMPDIR` to
`${TOPDIR}/tmp_baremetal`, appends the `baremetal` image feature, enables PFDI
support, and selects `baremetal-image`
(`sw-ref-stack/yocto/kas/baremetal.yml:8`,
`sw-ref-stack/yocto/kas/baremetal.yml:10`,
`sw-ref-stack/yocto/kas/baremetal.yml:11`,
`sw-ref-stack/yocto/kas/baremetal.yml:12`,
`sw-ref-stack/yocto/kas/baremetal.yml:13`,
`sw-ref-stack/yocto/kas/baremetal.yml:15`,
`sw-ref-stack/yocto/kas/baremetal.yml:17`,
`sw-ref-stack/yocto/kas/baremetal.yml:18`,
`sw-ref-stack/yocto/kas/baremetal.yml:22`,
`sw-ref-stack/yocto/kas/baremetal.yml:23`,
`sw-ref-stack/yocto/kas/baremetal.yml:26`).

The historical generated build output confirms that the upstream baremetal
target completed: the cooker log reports all 6590 attempted tasks succeeded
(`build/tmp_baremetal/log/cooker/fvp-rd-aspen/20260510034323.log` tail).

## Virtualization Build Path

`sw-ref-stack/yocto/kas/virtualization.yml` includes the same shared automotive
stack but adds `meta-virtualization`, appends `xen ptest` features, uses
`tmp_virtualization`, configures a DomU multiconfig, and targets
`virtualization-image`
(`sw-ref-stack/yocto/kas/virtualization.yml:8`,
`sw-ref-stack/yocto/kas/virtualization.yml:10`,
`sw-ref-stack/yocto/kas/virtualization.yml:18`,
`sw-ref-stack/yocto/kas/virtualization.yml:32`,
`sw-ref-stack/yocto/kas/virtualization.yml:34`,
`sw-ref-stack/yocto/kas/virtualization.yml:38`,
`sw-ref-stack/yocto/kas/virtualization.yml:39`,
`sw-ref-stack/yocto/kas/virtualization.yml:41`,
`sw-ref-stack/yocto/kas/virtualization.yml:43`).

Do not assume virtualization artifacts exist in the current checkout unless
`build/tmp_virtualization` is present or a fresh build is run.

## Demos And UEFI Capsule

`sw-ref-stack/yocto/kas/demos.yml` appends the `demos` image feature
(`sw-ref-stack/yocto/kas/demos.yml:11`,
`sw-ref-stack/yocto/kas/demos.yml:12`). The generated config has
`USE_CASE_DEMOS: true` (`.config.yaml:29`).

`arm-zena-css/yocto/kas/uefi-capsule.yml` sets `BUILD_UEFI_CAPSULE = "1"`
(`arm-zena-css/yocto/kas/uefi-capsule.yml:11`,
`arm-zena-css/yocto/kas/uefi-capsule.yml:12`,
`arm-zena-css/yocto/kas/uefi-capsule.yml:13`). The current deploy directory
contains capsule-related files such as `efi-capsule-update-image.img.uefi.capsule`
and signed capsule binaries.

## Pinned Release State

`arm-zena-css/yocto/kas/repos.pinned.yml` identifies itself as the pinned SHA
file for the v2.1 release, generated by `kas dump --update --force-checkout
--lock` (`arm-zena-css/yocto/kas/repos.pinned.yml:7`,
`arm-zena-css/yocto/kas/repos.pinned.yml:8`). It pins external layers including
`poky`, `meta-arm`, `meta-openembedded`, `meta-zephyr`, `meta-cassini`,
`meta-security`, `meta-virtualization`, `meta-ewaol`, and `meta-bluechi`
(`arm-zena-css/yocto/kas/repos.pinned.yml:14` through
`arm-zena-css/yocto/kas/repos.pinned.yml:39`).

For reproducible work, prefer `kas build .config.yaml` or an explicitly
documented include stack that uses `repos.pinned.yml`.

## Practical Build Entry Points

Current configured build:

```bash
kas build .config.yaml
```

Current configured shell:

```bash
kas shell .config.yaml
```

Direct baremetal include stack equivalent:

```bash
kas build arm-zena-css/yocto/kas/zena-css-bsp.yml:arm-zena-css/yocto/kas/uefi-capsule.yml:sw-ref-stack/yocto/kas/baremetal.yml:sw-ref-stack/yocto/kas/demos.yml:arm-zena-css/yocto/kas/repos.pinned.yml
```

These commands assume kas, network/source access, disk space, and FVP license
acceptance requirements are already satisfied.
