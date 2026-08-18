# Yocto Focused Workflows

## Recipe Identity And Fetch

Verify `SUMMARY`, `DESCRIPTION`, `HOMEPAGE`, `LICENSE`,
`LIC_FILES_CHKSUM`, `SRC_URI`, `SRCREV`, `PV`, `S`, and `B`. Check final values
with `bitbake -e <recipe>` and provider selection with
`bitbake-layers show-recipes <recipe>`.

For local-source recipes, inspect the project externalsrc or local source patch
class before changing fetch/unpack behavior. Do not bypass BitBake signatures
or patch application to hide a source mismatch.

## Patch Failures

Inspect:

```bash
bitbake <recipe> -c unpack -f
bitbake <recipe> -c patch -f
```

Then read the task log and quilt state in the recipe work directory. Confirm
patch order, strip level, source revision, context drift, and
`Upstream-Status`. Refresh only the affected patch against the pinned source.

## Configure And Compile

Confirm the inherited build class, native/target dependencies, sysroot inputs,
`PACKAGECONFIG`, toolchain file, and generated task script. Prefer the existing
class (`cmake`, `meson`, `autotools`, `setuptools3`, `cargo`, or another project
choice) instead of custom shell tasks.

```bash
bitbake <recipe> -c configure -f
bitbake <recipe> -c compile -f
```

## Install And Packaging

Install into `${D}` using standard directory variables. Verify package splits,
`FILES:${PN}`, build dependencies in `DEPENDS`, runtime dependencies in
`RDEPENDS:${PN}`, and package-scoped QA exceptions only when justified.

```bash
bitbake <recipe> -c install -f
bitbake <recipe> -c package -f
bitbake <recipe> -c package_qa
oe-pkgdata-util list-pkgs
oe-pkgdata-util find-path <installed-path>
```

## systemd Services

Check that the service is installed into the correct systemd unit directory,
captured by the package, declared with `SYSTEMD_SERVICE:${PN}`, and paired with
the intended enable policy. Keep service runtime dependencies in the package
that owns the unit.

## Image And Rootfs

Before changing an image, inspect image inheritance, packagegroups,
`IMAGE_FEATURES`, `EXTRA_IMAGE_FEATURES`, required/conflicting features, and
the package manager solver log.

```bash
bitbake nexios-image -c rootfs -f
bitbake -e nexios-image
```

Do not solve a rootfs dependency conflict by silently removing an unrelated
feature or using a broad recommendation exclusion.

## Kernel And BSP

Kernel source is under `hsoc-stack/components/primary_compute/linux`; Apollo
kernel metadata belongs in `hsoc-stack/yocto/meta-hsoc-bsp`. Use the kernel
review skill for source, DTS, patches, or config fragments.

```bash
bitbake virtual/kernel -c compile
```

## Layer Changes

Inspect `conf/layer.conf`, `BBFILES`, collections/patterns, dependencies,
compatibility, dynamic layers, and priority. Validate active order with
`bitbake-layers show-layers` and appends with `show-appends`. Use
`yocto-check-layer` for a new or compatibility-sensitive layer when available.

## Evidence

Task completion proves only that task. Image completion does not prove QBox or
FVP boot. Record the exact command, task summary, relevant log path, deploy
artifact, and any skipped runtime validation.
