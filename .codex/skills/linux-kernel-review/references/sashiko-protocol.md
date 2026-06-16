# Sashiko-Inspired Kernel Review Protocol

This local protocol adapts the public Sashiko approach for Codex reviews from
the current project top directory. It does not require the Sashiko binary or
any external LLM provider.

## Principles

- Treat kernel review as deep regression analysis, not a fast style scan.
- Assume comments, commit messages, and API claims may be wrong until proven by
  code.
- Never report a bug that is only theoretical. Prove at least one concrete
  execution path.
- Never dismiss a suspected bug from comments alone. Read the implementation and
  relevant config branches.
- Prefer full function/type/caller/callee context over diff fragments.

## Required Stages

1. Intent: summarize what the patch or local edit is trying to accomplish.
2. Full context: read the full changed functions, touched data structures, and
   one caller/callee level around the changed path when practical.
3. Change categories: split the diff into control flow, return value, resource
   management, locking, ABI, hardware, config, and documentation categories.
4. Reachability: prove the path can execute under the active config and
   workload, or classify review as blocked.
5. Implementation match: verify code behavior matches the stated intent.
6. Execution flow: trace error paths, returns, loops, and fallthrough.
7. Resource lifetime: check allocation, initialization, ownership transfer,
   cleanup, delayed callbacks, and module unload.
8. Synchronization: check lock ownership, RCU rules, per-CPU assumptions,
   interrupt/workqueue context, and PREEMPT_RT implications.
9. Security and ABI: check user input, ioctl structs, copy_to/from_user,
   integer bounds, information leaks, and compatibility.
10. Hardware and driver semantics: check MMIO/register ordering, DMA/shared
    memory, barriers, endpoint names, state machines, and firmware contracts.
11. False-positive removal: eliminate findings that cannot be proven by code,
    config, and call path evidence.
12. Report: produce only actionable, proven findings with file/line evidence and
    a short fix direction.

## Project Mapping

- RPMsg/netdev changes: emphasize endpoint lifetime, MTU, skb ownership,
  transmit failure behavior, and Safety Island endpoint compatibility.
- Remoteproc changes: emphasize resource tables, firmware handoff, MHU/shared
  memory, probe/remove order, and Zephyr peer expectations.
- PFDI changes: emphasize ioctl ABI, per-CPU device assumptions, SMC IDs,
  firmware return-code mapping, timeout behavior, and TF-A compatibility.
- Kernel cfg/scc changes: emphasize final config proof using
  `kernel_configcheck` or generated `.config` evidence.

## Reporting Rules

- Findings first; no long summary before issues.
- Severity is based on crash, hang, data corruption, security exposure,
  user-visible breakage, or build/runtime failure.
- Include false positives eliminated when they materially shaped the result.
- If no issues are found, say so and identify any missing evidence.

## Source Inspiration

- Sashiko README review stages:
  https://github.com/sashiko-dev/sashiko
- Kernel review prompts:
  https://github.com/masoncl/review-prompts/tree/main/kernel
