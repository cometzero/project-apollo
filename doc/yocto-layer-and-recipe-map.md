# Yocto Layer And Recipe Map

Generated: 2026-05-15

## Summary

The workspace has three local solution layers that matter most for project
changes: `meta-zena-css-bsp`, `meta-zena-css-safety-island`, and
`meta-arm-auto-solutions`. They sit on top of upstream/pinned layers and are
joined by kas. Image selection is feature-gated: baremetal and virtualization
recipes conflict with each other and are selected by `EXTRA_IMAGE_FEATURES`.

## Local Layers

| Layer | Path | Primary role |
| --- | --- | --- |
| `meta-zena-css-bsp` | `arm-zena-css/yocto/meta-zena-css-bsp` | RD-Aspen machine, firmware, FVP, secure boot, UEFI capsule, TF-A/TF-M/U-Boot/OP-TEE/SCP integration. |
| `meta-zena-css-safety-island` | `arm-zena-css/yocto/meta-zena-css-safety-island` | Zephyr Safety Island CL1 build integration and patches. |
| `meta-arm-auto-solutions` | `sw-ref-stack/yocto/meta-arm-auto-solutions` | Automotive images, image features, demos, Xen integration, PFDI, HIPC, runtime tests. |

## Layer Dependencies

`meta-zena-css-bsp` depends on `core`, `meta-arm`, `meta-python`, `ptx`,
`openembedded-layer`, and `perl-layer`
(`arm-zena-css/yocto/meta-zena-css-bsp/conf/layer.conf:23`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/layer.conf:24`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/layer.conf:25`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/layer.conf:26`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/layer.conf:27`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/layer.conf:28`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/layer.conf:29`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/layer.conf:30`).

`meta-zena-css-safety-island` depends on `core`, `meta-zena-css-bsp`, and
`zephyrcore` (`arm-zena-css/yocto/meta-zena-css-safety-island/conf/layer.conf:17`,
`arm-zena-css/yocto/meta-zena-css-safety-island/conf/layer.conf:18`,
`arm-zena-css/yocto/meta-zena-css-safety-island/conf/layer.conf:19`,
`arm-zena-css/yocto/meta-zena-css-safety-island/conf/layer.conf:20`).

`meta-arm-auto-solutions` depends on `core`, `meta-arm`, both local Zena
layers, `meta-ewaol`, and `bluechi-layer`
(`sw-ref-stack/yocto/meta-arm-auto-solutions/conf/layer.conf:17`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/conf/layer.conf:18`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/conf/layer.conf:19`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/conf/layer.conf:20`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/conf/layer.conf:21`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/conf/layer.conf:22`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/conf/layer.conf:23`).

All three local layers declare `walnascar` compatibility
(`arm-zena-css/yocto/meta-zena-css-bsp/conf/layer.conf:32`,
`arm-zena-css/yocto/meta-zena-css-safety-island/conf/layer.conf:22`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/conf/layer.conf:25`).

## Machine Configuration

The active machine is `fvp-rd-aspen`. The machine config:

- Tunes for Cortex-A720 (`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:13`).
- Includes variant-specific FVP and RTL fragments
  (`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:14`,
  `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:15`).
- Defines maximum four Primary Compute clusters and four CPUs per cluster
  (`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:19`,
  `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:20`).
- Selects Linux 6.18, OP-TEE 4.7, TF-A 2.14, TF-M 2.2, SCP firmware 2.16, and
  U-Boot 2026.01 preferences
  (`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:51`
  through `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:62`).
- Enables machine features for EFI, FF-A, Trusted Services secure partitions,
  RAS bridge, and ACS BBSR
  (`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:71`,
  `arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:72`).

The current `.config.yaml` sets `RD_ASPEN_VARIANT = "cfg2"` and
`PC_CPUS_COUNT_DEFAULT = "4"` (`.config.yaml:15`, `.config.yaml:17`).

## Image Recipes

`baremetal-image.bb` is an EWAOL-based image with required image feature
`baremetal` and conflicts against `virtualization` and `domu`
(`sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-core/images/baremetal-image.bb:14`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-core/images/baremetal-image.bb:18`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-core/images/baremetal-image.bb:19`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-core/images/baremetal-image.bb:20`).
It sizes Primary Compute CPUs and memory from machine configuration
(`sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-core/images/baremetal-image.bb:22`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-core/images/baremetal-image.bb:25`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-core/images/baremetal-image.bb:27`).

`virtualization-image.bb` is also EWAOL-based, requires `virtualization`,
conflicts against `baremetal` and `domu`, and appends Xen EFI boot files
(`sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-core/images/virtualization-image.bb:15`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-core/images/virtualization-image.bb:19`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-core/images/virtualization-image.bb:20`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-core/images/virtualization-image.bb:21`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-core/images/virtualization-image.bb:23`).

## Firmware And Boot Chain

The machine config defines an image dependency on `firmware-fvp-rd-aspen:do_deploy`
(`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:34`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:36`).
UEFI capsule generation is controlled by `BUILD_UEFI_CAPSULE`, and when enabled
it adds the capsule disk image deploy dependency
(`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:38`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:40`,
`arm-zena-css/yocto/meta-zena-css-bsp/conf/machine/fvp-rd-aspen.conf:43`).

The Zena design documentation says TF-A BL2 loads subsequent boot stages and
configuration from the FIP image, including BL31, BL32/OP-TEE, BL33/U-Boot,
`HW_CONFIG`, and `TOS_FW_CONFIG`
(`arm-zena-css/documentation/design/components.rst:229`,
`arm-zena-css/documentation/design/components.rst:230`,
`arm-zena-css/documentation/design/components.rst:233`,
`arm-zena-css/documentation/design/components.rst:235`,
`arm-zena-css/documentation/design/components.rst:237`).

## Image Feature Hook Point

`meta-arm-auto-solutions` appends `arm_auto_solutions_image_features` into
`USER_CLASSES`, making image-feature selection a central behavior switch
(`sw-ref-stack/yocto/meta-arm-auto-solutions/conf/layer.conf:31`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/conf/layer.conf:33`).

When changing image composition, inspect:

- `sw-ref-stack/yocto/meta-arm-auto-solutions/classes/arm_auto_solutions_image_features.bbclass`
- image recipes under `sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-core/images/`
- kas fragments that append `EXTRA_IMAGE_FEATURES`

## Change Guidance

- Put platform-specific firmware, machine, FVP, secure boot, or capsule changes
  in `arm-zena-css/yocto/meta-zena-css-bsp`.
- Put Zephyr Safety Island build integration changes in
  `arm-zena-css/yocto/meta-zena-css-safety-island`.
- Put shared images, demos, Xen, runtime package, and test integration changes
  in `sw-ref-stack/yocto/meta-arm-auto-solutions`.
- Avoid editing `layers/*` directly unless the task explicitly asks for a local
  layer patch; kas already applies downstream patches from the solution repos.
