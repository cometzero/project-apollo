# Apollo FVP Zephyr Project

This directory is the local Zephyr workspace used for Apollo FVP Safety Island
CL1 builds. It mirrors the Zephyr 4.1.0 source layout expected by
`zephyr-demos-cl1`:

- `zephyr/`: Zephyr RTOS core with the Apollo/RD-Aspen patch stack applied.
- `modules/`, `bootloader/`, and `tools/`: Zephyr module dependencies pinned to
  the same commits as the Yocto recipe.
- `tools/bsim/`: BabbleSim manifest and component sources. This tree is
  vendored as files because the upstream layout nests component repositories
  below the manifest directory.
- `safety_island/`: Apollo-owned Safety Island Zephyr board, drivers, overlays,
  and sample app.
- `apollo-modules.list`: module order used by the local build script.

Yocto builds use this tree through `EXTERNALSRC`. Local builds use the same tree
through `./local-build.sh zephyr` or as part of `./local-build.sh build`.
