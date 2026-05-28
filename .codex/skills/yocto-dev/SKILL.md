---
name: yocto-dev
description: Use for Yocto Project, OpenEmbedded, BitBake, Poky, meta-* layers, recipes .bb/.bbappend/.inc, bbclass, image recipes, MACHINE/BSP, distro config, bblayers.conf, local.conf, TEMPLATECONF, PACKAGECONFIG, SRC_URI, SRCREV, LIC_FILES_CHKSUM, do_fetch/do_unpack/do_patch/do_configure/do_compile/do_install/do_package/do_rootfs/do_image/do_populate_sdk, devtool, recipetool, SDK/eSDK, ptest, QA errors, rootfs errors, package split errors, systemd service integration, kernel/device-tree/U-Boot changes, sstate, downloads, mirrors, and Yocto build debugging. Trigger when the user asks to implement, debug, review, refactor, upgrade, package, build, analyze, or document Yocto/OpenEmbedded metadata.
---

# Yocto Development Skill

## Purpose

Use this skill for Yocto Project, OpenEmbedded, and BitBake development.

This skill is intended for tasks involving:

- Yocto Project / OpenEmbedded / Poky
- BitBake builds and metadata
- `meta-*` layers
- Recipes: `.bb`, `.bbappend`, `.inc`
- Classes: `.bbclass`
- Configuration files:
  - `bblayers.conf`
  - `local.conf`
  - `layer.conf`
  - `distro.conf`
  - `machine.conf`
- Image recipes and packagegroups
- BSP, MACHINE, kernel, device tree, and U-Boot work
- `devtool`, `recipetool`, SDK, and eSDK
- QA errors, rootfs errors, package split errors
- `sstate-cache`, `downloads`, mirrors, and CI build debugging
- traditional Yocto build directories initialized with `oe-init-build-env`

---

## Core Behavior

When this skill is active:

1. Inspect the Yocto environment before editing.
2. Do not assume the Yocto release, build directory, `MACHINE`, `DISTRO`, image target, package manager, init system, or layer priority.
3. Prefer small, targeted BitBake commands before expensive image builds.
4. Do not run full image builds unless necessary or explicitly requested.
5. Do not run `bitbake -c cleanall` unless explicitly requested.
6. Do not delete `tmp/`, `downloads/`, or `sstate-cache/` unless explicitly requested.
7. Do not disable QA checks using `INSANE_SKIP` until the root cause is understood.
8. Avoid permanent product changes in `local.conf`; prefer layer/image/distro/machine metadata.
9. Preserve layer boundaries:
   - Product policy belongs in product or distro layers.
   - BSP policy belongs in BSP layers.
   - Application recipes belong in application/product layers.
10. Report files inspected, files changed, commands run, results, and remaining risks.

---

## Initial Inspection Checklist

Start with lightweight inspection.

```bash
pwd
git status --short
find . -maxdepth 4 -name 'bblayers.conf' -o -name 'local.conf' -o -name 'templateconf.cfg' -o -name 'oe-init-build-env'
find . -maxdepth 5 -type f -path '*/conf/layer.conf' | sort
find . -maxdepth 4 -type d -name 'meta-*' | sort
find . -maxdepth 3 -iname 'README*' -o -iname '*setup*' -o -iname '*build*.sh' -o -iname 'Dockerfile'
```

If a build environment appears to be initialized, run:

```bash
bitbake-layers show-layers
bitbake-layers show-appends
bitbake-layers show-recipes | head -100
```

If the environment is not initialized, inspect:

- `README*`
- setup scripts
- `TEMPLATECONF` samples and build setup scripts
- repo manifests
- Dockerfiles
- CI scripts
- project documentation

---

## Environment Detection

Identify these before making changes:

```text
Yocto release branch:
  kirkstone, langdale, mickledore, nanbield, scarthgap, styhead, walnascar, master, etc.

Build directory:
  build/
  build-*/
  custom output directory

Core layers:
  poky
  openembedded-core
  bitbake
  meta-openembedded

Custom layers:
  meta-company
  meta-product
  meta-bsp
  meta-apps
  meta-security
  meta-virtualization

Build variables:
  MACHINE
  DISTRO
  IMAGE_FSTYPES
  PACKAGE_CLASSES
  DISTRO_FEATURES
  IMAGE_FEATURES
  EXTRA_IMAGE_FEATURES
  INIT_MANAGER
  SDKMACHINE
```

Useful commands:

```bash
bitbake -e | grep '^MACHINE='
bitbake -e | grep '^DISTRO='
bitbake -e | grep '^PACKAGE_CLASSES='
bitbake -e | grep '^DISTRO_FEATURES='
bitbake -e | grep '^INIT_MANAGER='
```

If a specific image or recipe is known:

```bash
bitbake -e <recipe-or-image> | grep '^MACHINE='
bitbake -e <recipe-or-image> | grep '^DISTRO='
bitbake -e <recipe-or-image> | grep '^IMAGE_INSTALL='
bitbake -e <recipe-or-image> | grep '^DISTRO_FEATURES='
```

---

## Layer Analysis Workflow

Use this when the task involves layer structure, bbappend behavior, or metadata conflicts.

```bash
bitbake-layers show-layers
bitbake-layers show-recipes <recipe>
bitbake-layers show-appends
bitbake-layers show-overlayed
```

Check layer configuration:

```bash
find . -path '*/conf/layer.conf' -print
grep -R "BBFILE_COLLECTIONS\|BBFILE_PATTERN\|BBFILE_PRIORITY\|LAYERSERIES_COMPAT" -n */conf/layer.conf */*/conf/layer.conf 2>/dev/null
```

Review:

- `BBFILE_COLLECTIONS`
- `BBFILE_PATTERN`
- `BBFILE_PRIORITY`
- `LAYERSERIES_COMPAT`
- layer dependencies
- layer ordering in `bblayers.conf`
- whether a `.bbappend` actually applies

---

## Recipe Creation Workflow

Prefer Yocto tooling when appropriate.

```bash
recipetool create <source-url-or-path>
devtool add <recipe-name> <source-url-or-path>
```

Manual skeleton:

```bitbake
SUMMARY = "Short package summary"
DESCRIPTION = "Longer package description"
HOMEPAGE = "https://example.com"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=<md5>"

SRC_URI = "git://example.com/project.git;protocol=https;branch=main"
SRCREV = "<commit-sha>"

S = "${WORKDIR}/git"

inherit cmake
```

Choose the correct class:

```text
cmake       CMake projects
autotools   Autoconf/Automake projects
meson       Meson projects
setuptools3 Python setuptools projects
python_poetry_core Python poetry-core projects
cargo       Rust/Cargo projects
go          Go projects
systemd     systemd service integration
pkgconfig   pkg-config integration
ptest       package test support
update-rc.d SysV init script integration
```

---

## Recipe Review Checklist

For any `.bb`, `.bbappend`, or `.inc` change, check:

```text
SUMMARY
DESCRIPTION
HOMEPAGE
LICENSE
LIC_FILES_CHKSUM
SRC_URI
SRCREV
PV
PR
S
B
inherit
DEPENDS
RDEPENDS:${PN}
RRECOMMENDS:${PN}
PACKAGECONFIG
EXTRA_OECMAKE
EXTRA_OECONF
EXTRA_OEMESON
do_configure
do_compile
do_install
FILES:${PN}
FILES:${PN}-dev
FILES:${PN}-dbg
SYSTEMD_SERVICE:${PN}
Upstream-Status in patches
```

For source fetch:

```bash
bitbake <recipe> -c fetch
bitbake <recipe> -c unpack
```

For patching:

```bash
bitbake <recipe> -c patch
```

For build/install/package:

```bash
bitbake <recipe> -c configure
bitbake <recipe> -c compile
bitbake <recipe> -c install
bitbake <recipe> -c package
```

---

## bbappend Workflow

Before creating a `.bbappend`:

```bash
bitbake-layers show-recipes <recipe>
bitbake-layers show-appends | grep <recipe> || true
```

Rules:

1. Match the recipe version carefully.
2. Use `%` wildcard only when compatible across versions.
3. Keep product policy in product layers.
4. Keep BSP policy in BSP layers.
5. Add comments for intentional overrides.
6. Verify the append is applied.

Common layout:

```text
meta-product/
  recipes-example/
    foo/
      foo_%.bbappend
      foo/
        0001-fix-build.patch
        foo.conf
```

Example:

```bitbake
FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

SRC_URI += "file://0001-fix-build.patch"
SRC_URI += "file://foo.conf"
```

Patch rule:

```text
Every patch should contain an Upstream-Status field.
Examples:
  Upstream-Status: Pending
  Upstream-Status: Submitted [link]
  Upstream-Status: Backport [link]
  Upstream-Status: Inappropriate [reason]
```

---

## Image Customization Workflow

For product behavior, prefer image recipes or packagegroups over `local.conf`.

Find image metadata:

```bash
bitbake-layers show-recipes '*image*'
grep -R "IMAGE_INSTALL\|CORE_IMAGE_EXTRA_INSTALL\|IMAGE_FEATURES\|EXTRA_IMAGE_FEATURES" -n meta-* */meta-* 2>/dev/null
```

Simple addition:

```bitbake
IMAGE_INSTALL:append = " my-package"
```

Feature addition:

```bitbake
IMAGE_FEATURES += "ssh-server-openssh"
```

Product image example:

```bitbake
require recipes-core/images/core-image-base.bb

SUMMARY = "Product image"

IMAGE_INSTALL:append = " packagegroup-product my-application"
```

Packagegroup example:

```bitbake
SUMMARY = "Product package group"
LICENSE = "MIT"

inherit packagegroup

RDEPENDS:${PN} = "\
    my-application \
    my-service \
    openssh \
"
```

---

## systemd Service Integration

Use this pattern when adding a service.

```bitbake
SUMMARY = "My service"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI += "file://my-service.service"

inherit systemd

SYSTEMD_SERVICE:${PN} = "my-service.service"
SYSTEMD_AUTO_ENABLE:${PN} = "enable"

do_install:append() {
    install -d ${D}${systemd_system_unitdir}
    install -m 0644 ${WORKDIR}/my-service.service ${D}${systemd_system_unitdir}/
}

FILES:${PN} += "${systemd_system_unitdir}/my-service.service"
```

Check whether systemd is enabled:

```bash
bitbake -e <image-or-recipe> | grep '^DISTRO_FEATURES='
bitbake -e <image-or-recipe> | grep '^INIT_MANAGER='
```

Do not add systemd-only metadata blindly if the distro uses SysV init or busybox init.

---

## Debugging BitBake Task Failures

First identify the failing task:

```text
do_fetch
do_unpack
do_patch
do_configure
do_compile
do_install
do_package
do_rootfs
do_image
do_populate_sdk
```

Find logs:

```bash
find build/tmp/work -path '*temp/log.do_*' | tail -50
find build/tmp/work -path '*temp/log.do_compile*' | grep <recipe> || true
find build/tmp/work -path '*temp/log.do_install*' | grep <recipe> || true
find build/tmp/work -path '*temp/log.do_rootfs*' | grep <image> || true
```

Inspect generated task scripts:

```bash
find build/tmp/work -path '*temp/run.do_compile*' | grep <recipe> || true
find build/tmp/work -path '*temp/run.do_install*' | grep <recipe> || true
```

Inspect final variable values:

```bash
bitbake -e <recipe> | grep '^S='
bitbake -e <recipe> | grep '^B='
bitbake -e <recipe> | grep '^WORKDIR='
bitbake -e <recipe> | grep '^DEPENDS='
bitbake -e <recipe> | grep '^RDEPENDS'
bitbake -e <recipe> | grep '^FILES'
```

Useful task commands:

```bash
bitbake <recipe> -c listtasks
bitbake <recipe> -c devshell
bitbake <recipe> -c cleansstate
bitbake <recipe> -c compile -f
bitbake <recipe> -c install -f
bitbake <recipe> -c package -f
```

Avoid `cleanall` unless explicitly requested.

---

## QA Failure Workflow

Do not immediately add `INSANE_SKIP`.

First determine:

1. Exact QA tag.
2. Failing package.
3. Failing file path.
4. Whether the issue is:
   - installed but not shipped
   - bad RPATH
   - already-stripped binary
   - missing runtime dependency
   - build path leakage
   - host contamination
   - license checksum mismatch
   - invalid symlink
   - wrong file ownership
   - static library in wrong package
   - development file in runtime package
   - architecture mismatch

Common QA tags and typical response:

```text
installed-vs-shipped
  Add files to FILES:${PN} or remove unintended installed files.

rpaths
  Fix build system install RPATH. Avoid disabling unless justified.

already-stripped
  Fix upstream build flags so binaries are not stripped before packaging.

dev-so
  Move development .so symlink to ${PN}-dev or adjust package split.

file-rdeps
  Add missing RDEPENDS:${PN} only after confirming runtime need.

ldflags
  Ensure target LDFLAGS are respected.

buildpaths
  Remove build directory paths from output files.

arch
  Verify cross-compile target and installed binary architecture.

license-checksum
  Update LIC_FILES_CHKSUM only after confirming license text change.
```

Only use `INSANE_SKIP:${PN}` with a clear comment after confirming the issue is intentional and safe.

---

## Package Split Workflow

Inspect installed files:

```bash
find build/tmp/work -path '*image' -type d | grep <recipe> || true
```

Use package data:

```bash
oe-pkgdata-util list-pkgs | grep <recipe-or-package> || true
oe-pkgdata-util list-pkg-files <package>
oe-pkgdata-util find-path /usr/bin/<binary>
```

Common package split variables:

```bitbake
FILES:${PN} += "/usr/bin/my-app"
FILES:${PN} += "${systemd_system_unitdir}/my-service.service"
FILES:${PN}-dev += "${includedir}/my-lib"
FILES:${PN}-dbg += "${libdir}/.debug"
RDEPENDS:${PN} += "runtime-package"
```

Do not put build dependencies in `RDEPENDS`.
Do not put runtime dependencies in `DEPENDS` unless needed at build time.

---

## devtool Workflow

Use `devtool` for active source development.

Modify existing recipe:

```bash
devtool modify <recipe>
devtool build <recipe>
devtool finish <recipe> <target-layer>
```

Add new recipe:

```bash
devtool add <recipe-name> <source-path-or-url>
devtool build <recipe-name>
devtool finish <recipe-name> <target-layer>
```

Upgrade recipe:

```bash
devtool upgrade <recipe>
devtool build <recipe>
devtool finish <recipe> <target-layer>
```

Reset workspace when done:

```bash
devtool reset <recipe>
```

Before finishing:

```bash
git status --short
devtool status
```

---

## recipetool Workflow

Use `recipetool` to bootstrap recipes.

```bash
recipetool create <source-url>
recipetool create -o <output-recipe-path> <source-url>
```

After generation:

1. Review `LICENSE`.
2. Review `LIC_FILES_CHKSUM`.
3. Review inherited class.
4. Review `DEPENDS`.
5. Review `do_install`.
6. Build targeted recipe.
7. Fix QA issues.

---

## Kernel / BSP Workflow

Before changing BSP or kernel metadata:

```bash
bitbake-layers show-recipes virtual/kernel
bitbake -e virtual/kernel | grep '^PREFERRED_PROVIDER_virtual/kernel='
bitbake -e virtual/kernel | grep '^MACHINE='
bitbake -e virtual/kernel | grep '^KERNEL_DEVICETREE='
```

Common BSP files:

```text
conf/machine/<machine>.conf
recipes-kernel/linux/linux-*.bbappend
recipes-kernel/linux/linux-*/defconfig
recipes-kernel/linux/linux-*/*.cfg
recipes-kernel/linux/linux-*/*.patch
recipes-bsp/u-boot/u-boot-*.bbappend
wic/*.wks
```

Prefer config fragments:

```bitbake
FILESEXTRAPATHS:prepend := "${THISDIR}/${PN}:"

SRC_URI += "file://my-feature.cfg"
```

Device tree additions:

```bitbake
SRC_URI += "file://my-board-overlay.dts"
KERNEL_DEVICETREE:append = " vendor/my-board.dtb"
```

Validate against project conventions before adding.

---

## U-Boot Workflow

Inspect provider:

```bash
bitbake-layers show-recipes virtual/bootloader
bitbake -e virtual/bootloader | grep '^PREFERRED_PROVIDER_virtual/bootloader='
```

Common files:

```text
recipes-bsp/u-boot/u-boot_%.bbappend
recipes-bsp/u-boot/files/defconfig
recipes-bsp/u-boot/files/*.patch
```

Check:

- `UBOOT_MACHINE`
- `UBOOT_CONFIG`
- defconfig
- boot script
- environment
- WIC image layout
- SPL/TPL requirements

---

## Rootfs Failure Workflow

For rootfs failures, inspect:

```bash
find build/tmp/work -path '*temp/log.do_rootfs*' | tail -20
bitbake -e <image> | grep '^IMAGE_INSTALL='
bitbake -e <image> | grep '^PACKAGE_CLASSES='
```

Package conflict investigation:

```bash
oe-pkgdata-util find-path <path>
oe-pkgdata-util list-pkgs | grep <name>
```

Check:

- duplicate file ownership
- package conflicts
- missing runtime dependency
- unavailable package
- package renamed by `PACKAGES`
- excluded package by `PACKAGE_EXCLUDE`
- incompatible `DISTRO_FEATURES`
- image recipe typo

---

## SDK / eSDK Workflow

Build SDK:

```bash
bitbake <image> -c populate_sdk
```

Build extensible SDK:

```bash
bitbake <image> -c populate_sdk_ext
```

Check variables:

```bash
bitbake -e <image> | grep '^SDKMACHINE='
bitbake -e <image> | grep '^TOOLCHAIN_HOST_TASK='
bitbake -e <image> | grep '^TOOLCHAIN_TARGET_TASK='
```

Add SDK content intentionally:

```bitbake
TOOLCHAIN_TARGET_TASK:append = " my-package-dev"
TOOLCHAIN_HOST_TASK:append = " nativesdk-my-tool"
```

---

## Fetch / Mirror / SRCREV Workflow

For fetch failures:

```bash
bitbake <recipe> -c fetch
bitbake -e <recipe> | grep '^SRC_URI='
bitbake -e <recipe> | grep '^SRCREV='
bitbake -e <recipe> | grep '^DL_DIR='
bitbake -e <recipe> | grep '^PREMIRRORS='
bitbake -e <recipe> | grep '^MIRRORS='
```

Check:

- protocol: `git`, `https`, `ssh`, `file`
- branch
- commit exists
- network access
- credentials
- mirror configuration
- `BB_NO_NETWORK`
- `BB_FETCH_PREMIRRORONLY`
- submodules
- Git LFS usage

Avoid floating branches for reproducible builds. Prefer pinned `SRCREV`.

---

## License Workflow

For license errors:

```bash
bitbake <recipe> -c configure
bitbake -e <recipe> | grep '^LICENSE='
bitbake -e <recipe> | grep '^LIC_FILES_CHKSUM='
```

Rules:

1. Do not blindly update checksum.
2. Inspect the license file diff.
3. Confirm whether license terms changed.
4. Update `LIC_FILES_CHKSUM` only after review.
5. Ensure `LICENSE` accurately describes the package.

---

## CMake Recipe Pattern

```bitbake
SUMMARY = "CMake application"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=<md5>"

SRC_URI = "git://example.com/app.git;protocol=https;branch=main"
SRCREV = "<commit>"

S = "${WORKDIR}/git"

inherit cmake pkgconfig

DEPENDS += "zlib"

EXTRA_OECMAKE += "\
    -DENABLE_TESTS=OFF \
"

do_install:append() {
    :
}
```

---

## Meson Recipe Pattern

```bitbake
SUMMARY = "Meson application"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=<md5>"

SRC_URI = "git://example.com/app.git;protocol=https;branch=main"
SRCREV = "<commit>"

S = "${WORKDIR}/git"

inherit meson pkgconfig

DEPENDS += "glib-2.0"
```

---

## Autotools Recipe Pattern

```bitbake
SUMMARY = "Autotools application"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://COPYING;md5=<md5>"

SRC_URI = "git://example.com/app.git;protocol=https;branch=main"
SRCREV = "<commit>"

S = "${WORKDIR}/git"

inherit autotools pkgconfig
```

---

## Python Recipe Pattern

```bitbake
SUMMARY = "Python application"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE;md5=<md5>"

SRC_URI = "git://example.com/pyapp.git;protocol=https;branch=main"
SRCREV = "<commit>"

S = "${WORKDIR}/git"

inherit setuptools3

RDEPENDS:${PN} += "python3-core"
```

---

## Rust / Cargo Recipe Notes

For Rust projects, inspect project conventions first. Common classes and helpers vary by Yocto release.

Check:

```bash
bitbake-layers show-recipes | grep cargo
grep -R "inherit cargo" -n meta-* */meta-* 2>/dev/null | head
```

Review:

- `Cargo.lock`
- vendoring strategy
- crate fetcher support
- license handling
- network restrictions

---

## Go Recipe Notes

For Go projects, inspect existing recipes first.

```bash
grep -R "inherit go" -n meta-* */meta-* 2>/dev/null | head
```

Check:

- module mode
- vendoring
- `GO_IMPORT`
- generated binaries
- install path
- static linking implications

---

## ptest Workflow

If package tests are required:

```bitbake
inherit ptest

SRC_URI += "file://run-ptest"

do_install_ptest() {
    install -d ${D}${PTEST_PATH}
    install -m 0755 ${WORKDIR}/run-ptest ${D}${PTEST_PATH}/
}
```

Run tests according to project test infrastructure.

---

## Traditional Yocto Build Workflow

If the project uses a traditional Yocto build directory:

```bash
find . -path '*/conf/templates/*/local.conf.sample' -o \
    -path '*/conf/templates/*/bblayers.conf.sample'
export TEMPLATECONF=<layer>/conf/templates/<template>
source layers/poky/oe-init-build-env build
bitbake <target>
```

Inspect:

- `build/conf/bblayers.conf`
- `build/conf/local.conf`
- `build/conf/templateconf.cfg`
- layer order and dependencies
- machine
- distro
- target
- environment passthrough

Prefer durable layer metadata and TEMPLATECONF samples for reusable
configuration. Edit `build/conf` only when the task explicitly concerns the
active local build directory.

---

## CI Debugging Workflow

Inspect CI files:

```bash
find . -maxdepth 4 -name '.gitlab-ci.yml' -o -path '*/.github/workflows/*' -o -name 'Jenkinsfile' -o -name 'Dockerfile'
```

Check:

- container image
- required host packages
- cache paths
- `DL_DIR`
- `SSTATE_DIR`
- build config (`bblayers.conf`, `local.conf`, `templateconf.cfg`)
- machine/image matrix
- artifact collection
- log collection
- license/SBOM steps

Prefer reproducing the smallest failing target locally.

---

## Safe Command Policy

Prefer targeted commands:

```bash
bitbake <recipe> -c fetch
bitbake <recipe> -c unpack
bitbake <recipe> -c patch
bitbake <recipe> -c configure
bitbake <recipe> -c compile
bitbake <recipe> -c install
bitbake <recipe> -c package
bitbake <image> -c rootfs
```

Use with caution:

```bash
bitbake <recipe> -c cleansstate
bitbake <recipe> -c clean
```

Avoid unless explicitly requested:

```bash
bitbake <recipe> -c cleanall
rm -rf build/tmp
rm -rf downloads
rm -rf sstate-cache
bitbake <full-image>
```

---

## Common Grep Commands

Find recipes:

```bash
find . -name '*.bb' | sort
find . -name '*.bbappend' | sort
```

Find recipe content:

```bash
grep -R "SUMMARY\|LICENSE\|SRC_URI\|SRCREV\|do_install\|SYSTEMD_SERVICE\|IMAGE_INSTALL" -n meta-* */meta-* 2>/dev/null
```

Find package image additions:

```bash
grep -R "IMAGE_INSTALL\|CORE_IMAGE_EXTRA_INSTALL\|PACKAGEGROUP\|RDEPENDS" -n meta-* */meta-* 2>/dev/null
```

Find machine config:

```bash
find . -path '*/conf/machine/*.conf' | sort
```

Find distro config:

```bash
find . -path '*/conf/distro/*.conf' | sort
```

---

## Decision Guide

Use this guide to choose where a change belongs.

```text
Need to add an app to an image?
  -> image recipe or packagegroup

Need to configure product policy?
  -> distro config or product layer

Need to configure hardware?
  -> machine config or BSP layer

Need to patch upstream source?
  -> recipe patch or bbappend in appropriate layer

Need to add build dependency?
  -> DEPENDS

Need runtime dependency?
  -> RDEPENDS:${PN}

Need optional build feature?
  -> PACKAGECONFIG

Need installed file packaged?
  -> FILES:${PN}

Need systemd service?
  -> inherit systemd + SYSTEMD_SERVICE:${PN}

Need temporary local experiment?
  -> local.conf, but do not treat as final product solution
```

---

## Final Response Format

When responding after using this skill, use this format:

```text
Summary
Detected environment
Files inspected
Files changed
Commands run
Build/test result
Root cause, if debugging
Remaining risks
Next recommended command
```

If no files were changed, explicitly say:

```text
Files changed: none
```

If no commands were run, explicitly say:

```text
Commands run: none
```

If the environment was not initialized, explicitly say what was missing and what setup command or file should be checked next.

---

## Minimal Natural-Language Trigger Examples

This skill should activate for requests like:

```text
Yocto recipe 하나 만들어줘.
BitBake build failure 원인 찾아줘.
do_install QA error 수정해줘.
rootfs 생성 중 package conflict 분석해줘.
meta-custom layer에 bbappend 추가해줘.
systemd service를 이미지에 포함시켜줘.
devtool로 recipe upgrade 해줘.
MACHINE config 추가해줘.
device tree fragment 연결해줘.
SDK에 dev package 포함해줘.
TEMPLATECONF 기반 Yocto build 설정 분석해줘.
```
