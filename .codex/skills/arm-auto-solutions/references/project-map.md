# Apollo Project Map

## Active Configuration

The traditional Yocto build directory is initialized under `build/`:

- `build/conf/local.conf`
- `build/conf/bblayers.conf`
- `build/conf/templateconf.cfg`
- `hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp/`
- top-level `yocto_build.sh`

Current selected values are `MACHINE = "apollo-qvp"`, cfg2, four Primary
Compute CPUs, `TMPDIR = "${TOPDIR}/tmp_baremetal"`, and default image target
`nexios-image`. `./yocto_build.sh --bsp` selects only the BSP image. Poky is
pinned to the Yocto 5.2.4 baseline.

## Source Zones

| Zone | Ownership |
| --- | --- |
| `arm-zena-css/` | Reference architecture, firmware, FVP behavior, design docs |
| `sw-ref-stack/` | Shared automotive images, demos, tests, CI |
| `hsoc-stack/components/primary_compute/` | Linux, U-Boot, TF-A, OP-TEE |
| `hsoc-stack/components/system_mgmt/` | TF-M, SCP-firmware, Zephyr workspace |
| `hsoc-stack/yocto/meta-hsoc-auto-solutions/` | Product/template/image policy |
| `hsoc-stack/yocto/meta-hsoc-bsp/` | BSP, firmware, kernel, signing policy |
| `hsoc-stack/tools/qbox/` | Reusable QBox core |
| `hsoc-stack/tools/qbox-platform/` | Apollo QBox platform overlay |
| `hsoc-stack/tools/qemu/` | QBox-local QEMU/libqemu |
| `hsoc-stack/tools/buildroot/` | Local initramfs/rootfs source |
| `layers/` | Pinned external Yocto layers |

## Generated Evidence

- Yocto task and deploy state: `build/tmp_baremetal/`
- QVP deploy images: `build/tmp_baremetal/deploy/images/apollo-qvp/`
- local component build: `build/local-${MACHINE}/`
- QBox full-system runtime: `build/qbox-apollo-qvp/full-<timestamp>/`
- explicit FVP-comparison QBox runtime: `build/qbox-apollo-fvp/`
- explicit FVP runtime: `build/local-apollo-fvp/fvp-boot/`

Generated evidence can be stale relative to source. Record the command and
timestamp that produced it before using it as proof.

## Validation Boundaries

- Static validation proves metadata, maps, syntax, or source structure.
- Targeted build validation proves one configured task or target.
- Image build validation proves the requested image completed.
- QBox runtime validation proves the selected virtual platform booted.
- FVP runtime validation is separate comparison evidence.
- Coverage audit proves only the assertions encoded by the audit script.
