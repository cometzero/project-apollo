# Linux Kernel Source Review

Generated: 2026-05-15

## Purpose

Use this checklist when Linux kernel source, out-of-tree kernel modules, kernel
patches, kernel configuration fragments, or Linux device-tree bindings are
created or changed in this workspace.

The checklist is static-first but Sashiko-inspired: review starts from patch
intent, full code context, change category decomposition, reachability, and
false-positive removal before findings are reported. Escalate to BitBake task
validation, image validation, and FVP/runtime validation when the change risk
requires it.

## Primary Source Areas

| Area | Review target |
| --- | --- |
| `sw-ref-stack/components/primary_compute/linux_drivers/arm_si_rproc_mod/src` | Safety Island remoteproc module. |
| `sw-ref-stack/components/primary_compute/linux_drivers/rpmsg_net_mod/src` | RPMsg network module. |
| `sw-ref-stack/components/primary_compute/linux_drivers/pfdi_misc_mod/src` | PFDI misc driver and ioctl/SMC ABI. |
| `sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-kernel/linux` | Linux patches, kernel features, cfg/scc fragments. |
| `sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-kernel/hipc-mod` | HIPC kernel module recipes. |
| `sw-ref-stack/yocto/meta-arm-auto-solutions/recipes-kernel/pfdi-misc-mod` | PFDI kernel module recipe. |
| `arm-zena-css/yocto/meta-zena-css-bsp/recipes-kernel/linux` | RD-Aspen kernel recipes and BSP kernel metadata. |

## Static Review

Use this Sashiko-style sequence before reporting findings:

1. Read the full diff and changed functions. Do not reason from isolated diff
   fragments.
2. State the intended behavior and verify commit-message/comment claims against
   implementation.
3. Split the edit into change categories: control flow, return values, resource
   lifetime, locking, ABI, hardware access, config, and documentation.
4. Apply a reachability gate. Prove the changed path can execute for the active
   config/workload, or classify review as blocked.
5. Analyze implementation match, execution flow, resource management,
   synchronization, security/ABI, and hardware/driver semantics.
6. Eliminate false positives. Do not report an issue unless at least one
   concrete execution path proves it.

For C sources and headers:

- Check SPDX license tags and `MODULE_LICENSE`.
- Prefer existing kernel APIs and local module style before adding helpers.
- Validate lifetime and cleanup for every allocation, registration, work item,
  endpoint, netdev, misc device, and platform/RPMsg/remoteproc object.
- Check error paths for leaks, double-free, stale drvdata, and partially
  initialized device state.
- Check locking, IRQ/workqueue context, sleepability, per-CPU assumptions,
  timeouts, and hotplug behavior.
- Validate user pointers, ioctl sizes, ABI structs, endian assumptions, and
  compat impact.
- Keep logging rate-limited where repeated runtime failures are possible.
- Avoid private kernel internals unless the reason is documented and bounded.

For kernel patches:

- Patch subject and touched subsystem match upstream kernel style.
- Patch carries useful commit message context and `Upstream-Status:` when stored
  as Yocto patch metadata.
- Check whether exported symbols, Kconfig, Makefile, documentation, and binding
  files all move together.
- Verify patch series ordering and dependencies.

For kernel config fragments:

- Every enabled symbol has a feature reason tied to a driver, transport,
  filesystem, runtime, or test requirement.
- Do not infer final config from fragments alone. Use generated `.config` or
  BitBake evidence before claiming effective state.
- Keep `.scc` feature names aligned with referenced `.cfg` paths.

## Commands

Use the active kas environment:

```bash
kas shell .config.yaml -c 'bitbake virtual/kernel -c kernel_configcheck'
kas shell .config.yaml -c 'bitbake virtual/kernel -c compile'
kas shell .config.yaml -c 'bitbake <module-recipe> -c compile'
kas shell .config.yaml -c 'bitbake <module-recipe> -c package_qa'
```

Use kernel source tooling when a prepared kernel tree is available:

```bash
scripts/checkpatch.pl --strict <patch-or-source>
make C=1 <target>
make W=1 <target>
make coccicheck MODE=report
```

These tools are not always available from the workspace root. If the prepared
kernel source tree or tool is missing, report the check as blocked/skipped with
the exact missing path or command.

## Project-Specific Checks

For HIPC/RPMsg/remoteproc:

- Confirm AP-side Linux driver expectations match Safety Island Zephyr endpoint
  names, buffers, and MHU/shared-memory assumptions.
- Check RPMsg endpoint lifetime on open/close/remove and module unload.
- Check netdev stats, skb ownership, MTU bounds, and transmit failure behavior.

For PFDI:

- Treat userspace ioctl ABI, kernel misc driver, SMC IDs, timeout behavior, and
  TF-A backend as separate review layers.
- Validate CPU affinity and per-CPU miscdevice assumptions.
- Check that firmware return codes are mapped to Linux errno values
  intentionally.

For PREEMPT_RT:

- Recheck lock choice, sleepability, and interrupt/threaded context.
- Avoid assuming non-RT spinlock behavior when code can run on RT kernels.

## Codex Auto Review

Use `$linux-kernel-review` for dedicated Linux kernel source review.

The `.omx/hooks/linux-kernel-auto-review.mjs` hook is invoked through Codex
native hook events. It watches `PostToolUse` payloads for newly created or
changed kernel source, kernel module, kernel patch, and kernel config paths in
this workspace. It records pending review state under:

```text
.omx/state/hooks/plugins/linux-kernel-auto-review/data.json
```

On `turn-complete`, the hook sends one deduplicated `$linux-kernel-review`
prompt to the active Codex pane. If tmux side effects are unavailable, pending
state remains as evidence and the review can be invoked manually.

## References

- Sashiko, agentic Linux kernel code review system:
  https://github.com/sashiko-dev/sashiko
- Sashiko-linked Linux kernel review prompts:
  https://github.com/masoncl/review-prompts/tree/main/kernel
- Kernel review core protocol:
  https://raw.githubusercontent.com/masoncl/review-prompts/main/kernel/review-core.md
- Kernel technical patterns:
  https://raw.githubusercontent.com/masoncl/review-prompts/main/kernel/technical-patterns.md
- Kernel false-positive guide:
  https://raw.githubusercontent.com/masoncl/review-prompts/main/kernel/false-positive-guide.md
