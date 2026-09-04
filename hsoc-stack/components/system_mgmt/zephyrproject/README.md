# Apollo QVP/FVP Zephyr Project

This directory is the local Zephyr workspace used for Apollo QVP and explicit
FVP Safety Island CL1 builds. It keeps the Apollo-owned Zephyr integration tree
and records how the common Arm Zena CSS Safety Island source is combined with
it:

- `zephyr/`: Zephyr RTOS core with the Apollo/RD-Aspen patch stack applied.
- `zephyr_hsoc_src/`: Apollo-owned Safety Island CL1 board, DTS, Kconfig,
  overlays, and HSOC-specific Zephyr integration sources.
- `zephyr_hsoc_src/config/apollo-cl1-modules.list`: module order used by the
  Yocto recipe. The `arm_zena_safety_island` token resolves to the common
  source under `arm-zena-css/components/safety_island/zephyr/src/`, and the
  `zephyr_hsoc_src` token resolves to this workspace's Apollo HSOC module.

Yocto builds use this directory through `EXTERNALSRC`, so local edits under
`zephyr/` and `zephyr_hsoc_src/` are direct build inputs. Common Safety Island
drivers, libraries, subsystems, and the sample app are taken from
`arm-zena-css/components/safety_island/zephyr/src/`. The dependency trees that
are no longer kept here, `modules/`, `bootloader/`, and `tools/`, are still
fetched by `meta-zephyr` and used from the Yocto `${UNPACKDIR}/git` unpack
tree.

Build the supported BSP with `./yocto_build.sh --bsp`. The
`zephyr-demos-cl1` recipe uses the module list above with dependencies from
the Yocto unpack tree.
