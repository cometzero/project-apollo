---
name: linux-kernel-review
description: Linux kernel review workflow for /build/arm/arm-auto-solutions. Use whenever a prompt mentions reviewing or changing Linux kernel source, kernel modules, drivers, patches, DTS/DTB/devicetree bindings, Kconfig, Kbuild, kernel Makefiles, defconfig/config fragments, PREEMPT_RT, platform drivers, IRQ/DMA/MMIO, sysfs/debugfs, dmesg kernel failures, HIPC, RPMsg, remoteproc, PFDI kernel code, 커널/드라이버/디바이스트리 리뷰, or when the linux-kernel-auto-review hook reports pending kernel review.
---

# Linux Kernel Review

Use this skill for focused Linux kernel source and kernel metadata review in
`/build/arm/arm-auto-solutions`.

## Intake

1. Read `.config.yaml` and confirm the active kas variant.
2. If the request came from the auto-review hook, inspect
   `.omx/state/hooks/plugins/linux-kernel-auto-review/data.json`.
3. Read `doc/linux-kernel-source-review.md` for the full project checklist.
4. Route unclear kernel behavior or cross-layer boot issues to
   `linux-kernel-expert` first, then `debug-expert` if runtime evidence is
   needed.

## Sashiko-Style Review Workflow

Use a Sashiko-inspired deep regression analysis, not a quick style pass:

1. Identify the diff or pending hook paths and read every changed hunk.
2. State the intended behavior of the change before judging correctness.
3. Gather full function/type context for changed code. Do not reason only from
   diff fragments.
4. Split the change into fine-grained categories such as control flow, return
   values, resource management, locking, ABI, hardware access, and config.
5. Apply a reachability gate: prove the changed code path can execute for the
   configured workload or report the blocked path.
6. Review each category through implementation matching, execution flow,
   resource lifetime, locking/synchronization, security, and hardware/driver
   constraints.
7. Eliminate false positives before reporting. If you cannot prove an issue with
   a concrete execution path, do not report it as a bug.

Read `references/sashiko-protocol.md` for the compact local protocol and
`references/review-checklist.md` for project-specific checks.

Start with source and diff context:

```bash
git -C sw-ref-stack status --short
git -C arm-zena-css status --short
git -C sw-ref-stack diff -- <paths>
git -C arm-zena-css diff -- <paths>
rg -n "TODO|FIXME|XXX|BUG_ON|panic\\(|msleep\\(|udelay\\(" <paths>
```

For module or kernel build validation:

```bash
kas shell .config.yaml -c 'bitbake <module-recipe> -c compile'
kas shell .config.yaml -c 'bitbake <module-recipe> -c package_qa'
kas shell .config.yaml -c 'bitbake virtual/kernel -c kernel_configcheck'
kas shell .config.yaml -c 'bitbake virtual/kernel -c compile'
```

Use kernel tree tools only when the prepared source tree is available:

```bash
scripts/checkpatch.pl --strict <patch-or-source>
make C=1 <target>
make W=1 <target>
make coccicheck MODE=report
```

## Output

Lead with proven findings only, ordered by severity, with file and line
references. For every finding include the concrete path that reaches the bug and
the reason it is not a false positive. Then report:

- reviewed paths,
- change categories,
- reachability result,
- exact commands run,
- static, kernel-tooling, BitBake task, image, and runtime evidence separately,
- skipped checks and blockers,
- whether pending hook state remains.

For LKML/upstream-style patch review, optionally create `review-inline.txt` in
the current working directory using polite inline-comment style. Do not create
that file for ordinary local project reviews unless the user asks for it.
