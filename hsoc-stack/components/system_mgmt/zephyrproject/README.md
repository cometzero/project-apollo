# Apollo QVP/FVP Zephyr Project

This directory is the local Zephyr workspace used for Apollo QVP and explicit
FVP Safety Island CL1 builds. It keeps the Apollo-owned Zephyr integration tree
and records how the common Arm Zena CSS Safety Island source is combined with
it:

- `zephyr/`: Zephyr RTOS core with the Apollo/RD-Aspen patch stack applied.
- `zephyr_hsoc_src/`: Apollo-owned Safety Island CL1 board, DTS, Kconfig,
  overlays, and HSOC-specific Zephyr integration sources.
- `apollo-modules.list`: module order used by the local build script. The
  `arm_zena_safety_island` token resolves to the common source under
  `arm-zena-css/components/safety_island/zephyr/src/`, and the
  `zephyr_hsoc_src` token resolves to this workspace's Apollo HSOC module.

Yocto builds use this directory through `EXTERNALSRC`, so local edits under
`zephyr/` and `zephyr_hsoc_src/` are direct build inputs. Common Safety Island
drivers, libraries, subsystems, and the sample app are taken from
`arm-zena-css/components/safety_island/zephyr/src/`. The dependency trees that
are no longer kept here, `modules/`, `bootloader/`, and `tools/`, are still
fetched by `meta-zephyr` and used from the Yocto `${UNPACKDIR}/git` unpack
tree.

Local builds follow the same model: `./local_build.sh zephyr` uses the Yocto
`zephyr-demos-cl1` unpack tree for the modules listed in
`apollo-modules.list`. Set `ZEPHYR_DEPS_SRC` only when using a custom
Yocto-unpacked dependency root.
