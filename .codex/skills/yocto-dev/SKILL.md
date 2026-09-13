---
name: yocto-dev
description: Change Apollo Yocto metadata or diagnose its BitBake, packaging and image failures.
---

# Apollo Yocto

Confirm effective machine, template and layers from build/conf for the requested
build. Product/distro policy belongs in meta-hsoc-auto-solutions; BSP, firmware,
kernel and signing metadata in meta-hsoc-bsp. Keep external layers unchanged
unless explicitly in scope, and permanent product policy out of local.conf.

Inspect final provider/override values and the first failing log.do_*/run.do_*.
Use a targeted task before image builds. Preserve QA, licensing, package
ownership and patch Upstream-Status; do not clean downloads/sstate/TMPDIR as
routine troubleshooting. Serialize shared builds.

Apollo kernel configuration sources are apollo_qvp_defconfig and
apollo_fvp_defconfig; do not add Apollo configuration .scc/.cfg fragments.
For those changes read [kernel defconfig](references/kernel-defconfig.md).
For task-specific packaging/fetch/systemd guidance read only the relevant
section of [workflows](references/workflows.md).

Root yocto_build.sh builds the product; --bsp selects nexios-bsp-initramfs.
For artifact-format/deploy changes verify the produced UKI/WIC/configuration,
not merely rootfs success. Runtime claims require matching runtime artifacts.
