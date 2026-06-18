# Yocto Layer And Recipe Map

Updated: 2026-06-18

## Summary

The active Apollo Yocto workspace has five local solution layers that matter
most for project changes: `meta-zena-css-bsp`, `meta-zena-css-safety-island`,
`meta-hsoc-auto-solutions`, `meta-hsoc-bsp`, and `meta-arm-auto-solutions`.
They sit on top of upstream/pinned layers and are joined by the traditional
`TEMPLATECONF` flow in `build/conf/`. Image selection is feature-gated:
baremetal and virtualization recipes conflict with each other and are selected
by `EXTRA_IMAGE_FEATURES`.

## Local Layers

| Layer | Path | Primary role |
| --- | --- | --- |
| `meta-zena-css-bsp` | `arm-zena-css/yocto/meta-zena-css-bsp` | RD-Aspen machine, firmware, FVP, secure boot, UEFI capsule, TF-A/TF-M/U-Boot/OP-TEE/SCP integration. |
| `meta-zena-css-safety-island` | `arm-zena-css/yocto/meta-zena-css-safety-island` | Zephyr Safety Island CL1 build integration and patches. |
| `meta-hsoc-auto-solutions` | `hsoc-stack/yocto/meta-hsoc-auto-solutions` | Apollo distro/template layer, traditional `apollo-fvp` `TEMPLATECONF`, and dynamic-layer patches moved out of external layers. |
| `meta-hsoc-bsp` | `hsoc-stack/yocto/meta-hsoc-bsp` | Apollo BSP layer, `apollo-fvp` machine, local externalsrc recipes, kernel metadata, module signing, firmware image recipes, and OP-TEE integration. |
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

The upstream Arm solution layers declare `walnascar` compatibility
(`arm-zena-css/yocto/meta-zena-css-bsp/conf/layer.conf:32`,
`arm-zena-css/yocto/meta-zena-css-safety-island/conf/layer.conf:22`,
`sw-ref-stack/yocto/meta-arm-auto-solutions/conf/layer.conf:25`).

## Machine Configuration

The active machine is `apollo-fvp`. Its machine metadata in
`hsoc-stack/yocto/meta-hsoc-bsp/conf/machine/apollo-fvp.conf` currently
inherits the RD-Aspen FVP machine while keeping Apollo-specific override points:

- Adds `MACHINEOVERRIDES =. "fvp-rd-aspen:"` and
  `NATIVE_MACHINE = "fvp-rd-aspen"` for compatibility with existing BSP
  recipes.
- Requires `conf/machine/fvp-rd-aspen.conf` as the current hardware baseline.
- Sets `KMACHINE = "apollo-fvp"` for kernel metadata.
- Sets `ARM_SYSTEMREADY_FIRMWARE = "firmware-apollo-fvp:do_deploy"`.

The inherited RD-Aspen machine config:

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

The active `build/conf/local.conf` sets `RD_ASPEN_VARIANT = "cfg2"` and
`PC_CPUS_COUNT_DEFAULT = "4"`.

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

The Apollo machine config overrides the firmware dependency to
`firmware-apollo-fvp:do_deploy`; the inherited RD-Aspen machine config still
documents the original `firmware-fvp-rd-aspen:do_deploy` dependency
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
  for the Apollo port in `hsoc-stack/yocto/meta-hsoc-bsp` unless the task is
  explicitly an upstream Arm Zena CSS change.
- Put Apollo distro/template and dynamic-layer changes in
  `hsoc-stack/yocto/meta-hsoc-auto-solutions`.
- Put upstream RD-Aspen BSP changes in `arm-zena-css/yocto/meta-zena-css-bsp`
  only when the intended owner is Arm Zena CSS rather than the Apollo port.
- Put Apollo Safety Island CL1 source changes in
  `hsoc-stack/components/system_mgmt/zephyrproject/safety_island/` and Apollo
  Zephyr build metadata in `hsoc-stack/yocto/meta-hsoc-bsp`; use
  `arm-zena-css/yocto/meta-zena-css-safety-island` only for upstream Zena CSS
  layer changes.
- Put shared images, demos, Xen, runtime package, and test integration changes
  in `sw-ref-stack/yocto/meta-arm-auto-solutions`.
- Avoid editing `layers/*` directly unless the task explicitly asks for a local
  layer patch; kas already applies downstream patches from the solution repos.
