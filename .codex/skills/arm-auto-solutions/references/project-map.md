# Arm Auto Solutions Compact Project Map

## Current Configuration

The active Yocto configuration is the traditional build directory under
`build/conf/`:

- `build/conf/local.conf`
- `build/conf/bblayers.conf`
- `build/conf/templateconf.cfg`
- `hsoc-apollo/yocto/meta-hsoc-apollo/conf/templates/apollo-fvp/`
- top-level `build.sh`

Current selected values:

- `MACHINE = "apollo-fvp"`
- `RD_ASPEN_VARIANT = "cfg2"`
- `PC_CPUS_COUNT_DEFAULT = "4"`
- `ARM_FVP_EULA_ACCEPT = "1"`
- baremetal enabled, virtualization disabled
- demos enabled, tests disabled

## Main Source Zones

`arm-zena-css/`:

- RD-Aspen machine and BSP metadata
- TF-A, TF-M, U-Boot, OP-TEE, SCP firmware integration
- Safety Island Zephyr module and Yocto layer
- Zena design/user documentation

`sw-ref-stack/`:

- shared Arm Automotive Solutions images
- EWAOL architecture selection
- PFDI/HIPC Linux integration recipes
- pytest-based test automation
- GitLab CI build/test fragments

`layers/`:

- pinned third-party and upstream Yocto layers
- avoid direct edits unless explicitly requested

`build/`:

- generated BitBake output
- current local evidence only

## Build Validation vs Runtime Validation

Build validation proves BitBake task success and artifacts.
Runtime validation proves FVP boot, console readiness, networking, and tests.
Do not infer runtime success from build success.

Current local build evidence is under:

- `build/tmp_baremetal/log/cooker/apollo-fvp/`
- `build/tmp_baremetal/deploy/images/apollo-fvp/`

Runtime validation needs:

- FVP binary, usually `FVP_Zena_CSS_Cfg2`
- Crypto plugin path
- deploy images
- console/terminal mappings
- SSH/user networking port availability
