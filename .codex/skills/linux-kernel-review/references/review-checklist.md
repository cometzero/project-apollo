# Linux Kernel Review Checklist

## C Source And Headers

- Start from the complete diff and full function/type context, not snippets.
- Record change categories before judging correctness.
- Prove changed paths are reachable under the active config/workload.
- SPDX license and `MODULE_LICENSE` are consistent.
- Object lifetime is balanced across probe/open/start, error paths, remove,
  stop/release, and module unload.
- `devm_*` and manual cleanup are not mixed incorrectly.
- Locking, sleepability, interrupt context, workqueue context, and PREEMPT_RT
  behavior are valid.
- User pointers, ioctl ABI structs, sizes, endian assumptions, and compat impact
  are checked.
- Return values and Linux errno mappings are intentional.
- Logs use the right device context and are rate-limited when noisy.
- False-positive gate: do not report defensive checks unless invalid data can
  reach the site and the current code can fail.

## Kernel Modules

- `Kbuild`/`Makefile` builds only intended objects.
- Recipe inherits `module` and packages the expected module name.
- Runtime dependencies and autoload behavior match the intended device path.
- `modprobe`, remove, and reload behavior are considered.

## Patches And Config

- Patch subject, commit message, and touched subsystem are coherent.
- Commit message claims and comments are verified against implementation.
- Yocto-stored patches include useful context and `Upstream-Status:`.
- Kconfig, Makefile, documentation, bindings, and code are updated together.
- `.cfg` and `.scc` fragments are paired and validated with
  `kernel_configcheck`.

## Project-Specific

- HIPC/RPMsg/remoteproc: endpoint names, MTU, skb ownership, netdev stats, and
  AP/Safety Island shared-memory assumptions.
- PFDI: ioctl ABI, SMC ID mapping, firmware return-code mapping, per-CPU device
  assumptions, timeout behavior, and TF-A backend compatibility.
- RD-Aspen: boot args, PREEMPT_RT, MHUv3, remoteproc, RPMsg, RAS, and deploy
  artifact boundaries.
