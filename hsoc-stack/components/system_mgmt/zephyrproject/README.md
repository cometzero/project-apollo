# Apollo FVP Zephyr Project

This directory is the local Zephyr workspace used for Apollo FVP Safety Island
CL1 builds. It keeps only the Apollo-owned source trees:

- `zephyr/`: Zephyr RTOS core with the Apollo/RD-Aspen patch stack applied.
- `safety_island/`: Apollo-owned Safety Island Zephyr board, drivers, overlays,
  and sample app.
- `apollo-modules.list`: module order used by the local build script.

Yocto builds use this directory through `EXTERNALSRC`, so local edits under
`zephyr/` and `safety_island/` are direct build inputs. The dependency trees
that are no longer kept here, `modules/`, `bootloader/`, and `tools/`, are
still fetched by `meta-zephyr` and used from the Yocto
`${UNPACKDIR}/git` unpack tree.

Local builds follow the same model: `./local-build.sh zephyr` uses the Yocto
`zephyr-demos-cl1` unpack tree for the modules listed in
`apollo-modules.list`. Set `ZEPHYR_DEPS_SRC` only when using a custom
Yocto-unpacked dependency root.
