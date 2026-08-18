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

Use the project wrapper for dependency-aware `y`, `m`, and `n` requests:

```bash
./yocto_build.sh --machine apollo-qvp \
  --enable-config CONFIG_FOO_PARENT=y \
  --enable-config CONFIG_FOO=y
./yocto_build.sh --machine apollo-fvp \
  --enable-config CONFIG_FOO_PARENT=y \
  --enable-config CONFIG_FOO=y
```

Linux `scripts/config` records requests but does not resolve dependencies.
Let the wrapper run `olddefconfig`, compare requested and resolved states,
save a candidate defconfig, regenerate `.config`, and verify it again. If a
requested `y` or `m` resolves differently, inspect the symbol's `depends on`
or `choice` expression and add only the required parent settings.

Never run `scripts/config` directly against a source defconfig. Use an explicit
target with `-c` only for a normal BitBake task:

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
