---
name: linux-kernel-review
description: Review or modify Apollo Linux drivers, DTS, Kconfig and kernel/BSP interfaces.
---

# Apollo Linux

Kernel source belongs in hsoc-stack/components/primary_compute/linux;
kernel recipe/signing integration belongs in hsoc-stack/yocto/meta-hsoc-bsp.
Confirm the affected configuration and call path, not a hardcoded machine snapshot.

Inspect changed code with its callers, locking/context, lifetimes/error cleanup,
MMIO ordering, IRQ/DMA semantics and relevant DTS/Kconfig contracts.
Report only findings with a concrete reachable failure and file/line evidence.
Use [review checklist](references/review-checklist.md) for deeper review, or
[sashiko protocol](references/sashiko-protocol.md) for that specialized workflow.

Choose supported source checks and focused subsystem/kernel builds.
Driver behavior changes need guest probe/traffic evidence when integrated.
Do not treat compilation or a graph index as proof of runtime correctness.
