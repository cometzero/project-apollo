# Apollo Kernel Defconfig Workflow

## Configuration Source Contract

Treat these externalsrc files as the only Apollo kernel configuration sources:

- `hsoc-stack/components/primary_compute/linux/arch/arm64/configs/apollo_qvp_defconfig`
- `hsoc-stack/components/primary_compute/linux/arch/arm64/configs/apollo_fvp_defconfig`

Keep the project recipe's `do_kernel_configme` equivalent to:

```bitbake
do_kernel_configme() {
    bbplain "Applying ${APOLLO_KERNEL_DEFCONFIG} to ${B}/.config"
    oe_runmake -C ${S} O=${B} ${APOLLO_KERNEL_DEFCONFIG}
}
```

Do not call `do_kernel_metadata config`, `scc`, or `merge_config.sh` from this
task. The inherited `do_kernel_metadata` task may still run, but
`do_kernel_configme` must not consume its configuration queue. Inherited
`KERNEL_FEATURES` entries may remain for metadata processing; do not add
Apollo-specific configuration `.scc` or `.cfg` files through `SRC_URI` or
`KERNEL_FEATURES`.

## Update Defconfigs

Enter the active Yocto environment, then use the skill's deterministic helper
inside the build directory:

```bash
workspace_dir="$PWD"
source layers/poky/oe-init-build-env build

MACHINE=apollo-qvp \
  "$workspace_dir/.codex/skills/yocto-dev/scripts/update_kernel_defconfig.sh" \
  CONFIG_FOO_PARENT=y CONFIG_FOO=y CONFIG_BAR=m CONFIG_BAZ=n
```

Run the helper again with `MACHINE=apollo-fvp` when the setting applies to both
machines. It obtains `S`, `B`, `ARCH`, compiler commands, and the source
defconfig path from the effective `virtual/kernel` environment. It applies
requests only to `${B}/.config`, runs `olddefconfig`, verifies resolved states,
saves the source defconfig, regenerates `.config`, and verifies it again.

The helper rejects unknown or duplicate symbols, dependency mismatches, and a
pre-existing source-defconfig diff. If a requested `y` or `m` resolves
differently, inspect the symbol's `depends on` or `choice` expression and add
only the required parent settings. Review `${B}/skill-kernel-diff.txt` and the
source repository diff after every update.

Never run Linux `scripts/config` directly against a source defconfig. Use an
explicit target with `-c` only for a normal BitBake task:

```bash
./yocto_build.sh virtual/kernel -c menuconfig
./yocto_build.sh virtual/bootloader -c cleansstate
```

## Retire Configuration Fragments

When removing a product-wide `.cfg` or `.scc` configuration fragment:

1. Move every required `CONFIG_*` state into both Apollo defconfigs.
2. Remove its `SRC_URI` or `KERNEL_FEATURES` connection.
3. Delete the fragment.
4. Verify the effective task body and both generated `.config` files.

The gzip initrd migration requires both defconfigs to contain:

```text
CONFIG_BLK_DEV_INITRD=y
CONFIG_RD_GZIP=y
```

Do not recreate `rd-gzip-initrd.cfg`.

## Validate Both Machines

Inspect the effective task and require no fragment merge commands:

```bash
source layers/poky/oe-init-build-env build
for machine in apollo-qvp apollo-fvp; do
  MACHINE="$machine" bitbake -e virtual/kernel |
    sed -n '/^do_kernel_configme()/,/^}/p'
  MACHINE="$machine" bitbake virtual/kernel -c kernel_configme -f
  MACHINE="$machine" bitbake virtual/kernel -c defconfig -f
  MACHINE="$machine" bitbake virtual/kernel -c configure -f
  MACHINE="$machine" bitbake virtual/kernel -c compile -f
done
```

Check `${B}/.config` for every migrated symbol and report forced-task taint
warnings separately from failures. Build a BSP image and boot it only when the
changed symbols require image or runtime qualification.
