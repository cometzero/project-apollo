---
name: linux-kernel-review
description: Linux kernel review and implementation workflow for this Apollo project. Use for kernel source, modules, drivers, patches, DTS/bindings, Kconfig/Kbuild, config fragments, PREEMPT_RT, MMIO/IRQ/DMA, HIPC, RPMsg, remoteproc, PFDI, or kernel boot failures.
---

# Linux Kernel Review

Use this skill for kernel work owned by:

- `hsoc-stack/components/primary_compute/linux`: active Apollo kernel source.
- `hsoc-stack/yocto/meta-hsoc-bsp`: kernel recipes, config, device tree,
  signing, modules, and BSP integration.
- `sw-ref-stack/yocto/meta-arm-auto-solutions`: shared automotive kernel
  integration when the task reaches that layer.

Read `build/conf/local.conf`, `build/conf/bblayers.conf`, and
`build/conf/templateconf.cfg` first. Route architecture/firmware questions to
`arm-expert` and runtime root-cause work to `debug-expert`.

Use `agent_type = "linux-kernel-expert"` (`gpt-5.6-sol`, high) for the review
and any accepted implementation. Escalate cross-domain boot root-cause work
with `agent_type = "debug-expert"` (`gpt-5.6-sol`, xhigh). If the spawn surface
does not expose `agent_type`, keep the work in the project leader and do not
claim specialist selection.

## Review Method

1. Read the complete diff and state intended behavior.
2. Gather the changed function, type, callers, configuration, DTS, and firmware
   interface context.
3. Prove the changed path is reachable on active `apollo-qvp` cfg2.
4. Review control flow, return values, resource lifetime, locking, ABI,
   hardware access, and error cleanup separately.
5. Eliminate findings that lack a concrete execution path.
6. Check coupling across Kconfig, Kbuild/Makefile, DTS bindings, config
   fragments, Yocto recipes, and patches.

Use `references/sashiko-protocol.md` and `references/review-checklist.md` for
the detailed review checklist. Preserve user changes and repository ownership.

## Kernel-Specific Checks

- lifetime and every error/unwind path
- lock ordering, sleepability, IRQ context, and PREEMPT_RT behavior
- MMIO ordering, register width, endianness, IRQ and DMA semantics
- user pointer handling, ioctl ABI, sysfs/debugfs lifetime and permissions
- module reference/unload behavior
- devicetree schema, compatible strings, address/size cells, IRQs, clocks,
  resets, and reserved memory
- patch ordering, commit message claims, and `Upstream-Status`

## Validation

Start with source checks appropriate to the touched tree. Use targeted BitBake
tasks for integrated metadata:

```bash
source layers/poky/oe-init-build-env build
bitbake virtual/kernel -c kernel_configcheck
bitbake virtual/kernel -c compile
bitbake <module-recipe> -c compile
bitbake <module-recipe> -c package_qa
```

Use `scripts/checkpatch.pl`, sparse, or Coccinelle only when the prepared kernel
tree supports them. Runtime claims require QBox or explicit FVP console, probe,
and driver evidence.

Report findings first by severity with file/line and reachable execution path,
then list reviewed paths, commands, results, skipped checks, and residual risk.
