# Arm Auto Solutions Analysis

Updated: 2026-07-22

This directory contains Codex-facing analysis notes for the current
`/build/arm/arm-auto-solutions` workspace. The workspace is now a top-level Git
repository that pins nested source repositories with submodules. The notes keep
source repositories, generated build artifacts, and Codex automation surfaces
separate.

## Documents

- [Current Source Structure KR](source-structure-ko.md) - Korean source
  ownership map for the top repository, `hsoc-stack`, primary compute,
  system management, QBox/QEMU, Yocto layers, scripts, tests, generated build
  outputs, and documentation update rules.
- [Project Architecture](project-architecture.md) - workspace layout,
  subsystems, and current configuration.
- [Arm Zena CSS Hardware Blocks](arm-zena-css-hardware-blocks.md) - RD-Aspen
  hardware block map, Safety Island/RSE/Primary Compute relationships, and
  FVP-visible device evidence.
- [Apollo FVP Hardware Analysis KR](apollo-fvp-hardware-analysis-ko.md) -
  Korean source-backed hardware analysis for Apollo FVP/RD-Aspen CFG2 covering
  RSE, Safety Island CL0/CL1, interconnect, interrupt, processor, I/O, system
  management, and peripheral blocks.
- [Arm Zena CSS FVP Timer And Counter Analysis KR](arm-zena-css-fvp-timer-counter-analysis-ko.md) -
  Korean source- and Iris-backed analysis of the Zena CSS REFCLK, shared System
  Counter, per-domain timer frames, the RSE Local System Counter, and the
  hardware-versus-FVP topology difference.
- [FVP Iris Debugging Guide KR](fvp-iris-debugging-guide-ko.md) - Korean guide
  for building local FVP debug artifacts, launching the existing halted Iris
  server helper, setting symbolic breakpoints, checking logs, and resolving
  common manifest, port, symbol, and timeout failures.
- [Apollo QBox Hardware KR](apollo-qbox-hardware-ko.md) - Korean mapping from
  Apollo FVP hardware blocks to current QBox/QEMU emulation paths, including
  Lua instances, SystemC modules, QEMU modules, and fidelity status.
- [Apollo FVP-QVP Hardware Comparison KR](apollo-fvp-qvp-hardware-comparison-ko.md) -
  Korean subsystem-by-subsystem comparison of the Arm Zena CSS FVP memory map
  and Apollo QVP Lua, SystemC, and QEMU implementation modules, including
  explicit partial-model, placeholder, and missing-IP gaps.
- [QBox-FVP Timer And Counter Comparison KR](qbox-fvp-timer-counter-comparison-ko.md) -
  Korean comparison of the FVP shared-counter behavior and the implemented
  QBox shared-provider topology, including exact frequencies, remaining
  fidelity debt, and the passing structured differential evidence.
- [Apollo QVP Timer And Counter Implementation Plan KR](apollo-qvp-timer-counter-implementation-plan-ko.md) -
  Korean implementation and completion record for the shared CSS counter provider,
  per-QEMU-instance bridges, AP/SI CPU and MMIO timer integration, independent
  RSE local counter/timers, repository ownership, phased gates, and 44/44
  FVP/QBox differential validation.
- [Apollo QVP Machine Architecture KR](apollo-qvp-machine-architecture-ko.md) -
  Korean architecture comparison of current Apollo QVP and Arm Zena CSS/FVP,
  covering address views, buses, memory, hardware blocks, routing gaps, and
  the target domain-separated virtual-platform structure.
- [Apollo QVP Machine Improvement Plan KR](apollo-qvp-machine-improvement-plan-ko.md) -
  Korean phased implementation plan for declarative topology, AP/SMD/RSE/SI
  router separation, ATU/APU policy, memory and signal routing, and FVP/QVP
  differential validation gates.
- [Apollo QBox Full Model Promotion](apollo-qbox-full-model/index.md) -
  Korean PRD/spec/design/task/verification document set for promoting
  safety, security, reset, power, access-control, and interrupt placeholders
  from `gs_memory`/stub surfaces to full QBox models.
- [QBox FVP Emulation Project](qbox-fvp-emulation-project.md) - project
  mission and workflow for implementing the Arm Zena CSS/RD-Aspen FVP behavior
  in QBox with SystemC/TLM/QEMU fidelity.
- [QBox Apollo FVP Full-System Design](qbox-apollo-fvp-full-system-design.md) -
  review draft for using local Apollo boot artifacts to emulate RSE, Safety
  Island CL0/CL1, and Primary Compute together in QBox.
- [QBox Apollo FVP Full-System Architecture KR](qbox-apollo-fvp-full-system-architecture-ko.md) -
  Korean implementation summary, SW architecture, design rationale, subsystem
  responsibilities, evidence model, and completion gate overview for the
  Apollo full-system QBox implementation.
- [QBox Apollo FVP Full-System Runbook KR](qbox-apollo-fvp-full-system-runbook-ko.md) -
  Korean execution guide for building, running, validating, and debugging the
  Apollo full-system QBox path.
- [QBox Apollo FVP Full-System Quickstart KR](qbox-apollo-fvp-full-system-quickstart-ko.md) -
  Korean quickstart for launching the Apollo full-system QBox path in tmux,
  watching subsystem UART logs, and checking run evidence.
- [QBox Apollo FVP Full-System Goal And Verification](qbox-apollo-fvp-full-system-goal-verification.md) -
  review contract for the full-system objective, non-completion points,
  G0-G5 completion gates, final evidence bundle, and strict verifier command.
- [QBox Apollo FVP Full-System Goal Completion Report KR](qbox-apollo-fvp-full-system-goal-completion-report-ko.md) -
  Korean completion report for the G0-G5 goal execution, live CL0/CL1 fix,
  final evidence bundle, and pushed commit.
- [QBox Apollo FVP Map Analysis](qbox-apollo-fvp-map-analysis.md) -
  source-backed memory map, interrupt map, ATU, and hardware block analysis for
  the Apollo full-system QBox design.
- [QBox Apollo FVP Full-System Tasks](qbox-apollo-fvp-full-system-tasks.md) -
  review backlog for the full-system QBox implementation stages and acceptance
  criteria, including the final strict verifier command
  `scripts/test/verify_qbox_apollo_fvp_full_completion.py --strict-final`.
- [Yocto Build And Kas](yocto-build-and-kas.md) - historical kas include stack,
  build variants, targets, and reproducibility levers. The active build path is
  the traditional Yocto `TEMPLATECONF` flow documented in the top-level
  `README.md`.
- [Yocto Layer And Recipe Map](yocto-layer-and-recipe-map.md) - local layers,
  dependencies, image recipes, machine configuration, and firmware recipes.
- [Yocto Layer And Recipe Review](yocto-layer-recipe-review.md) - review
  checklist and validation commands for newly created layers, recipes, appends,
  patches, and image metadata.
- [Safety Island And Zephyr](safety-island-and-zephyr.md) - Safety Island CL1,
  Zephyr module layout, HIPC, and PFDI surfaces.
- [Linux Kernel Source Review](linux-kernel-source-review.md) - review
  checklist and auto-review hook behavior for Linux kernel modules, kernel
  patches, cfg/scc fragments, and kernel metadata.
- [Validation, CI, And Runtime](validation-ci-and-runtime.md) - OEQA,
  pytest-based automation, GitLab CI, and runtime test dependencies.
- [Apollo FVP Validation Test Process KR](apollo-fvp-validation-test-process-ko.md) -
  Korean table summary of `run_test.sh` validation preparation, category
  flow, pass/fail rules, dependencies, and measured basic/functional runtime.
- [Headless FVP Boot Logs](fvp-log-boot.md) - non-interactive FVP launch with
  file-based stdout and per-console boot logs.
- [Generated Artifacts And Risks](generated-artifacts-and-risks.md) - active
  generated-output boundaries, historical deploy evidence, and operational
  risks.
- [Codex Project Expert Workflow](codex-project-expert-workflow.md) - the
  project-specific Codex agent, skill, and hook added with this analysis.

## Evidence Scope

The analysis is grounded in repository-local files and current generated
artifacts. Source evidence is cited as file paths and, where useful,
`path:line` references. Generated build outputs under `build/tmp_baremetal` are
treated as evidence of this checkout's current local state, not as upstream
source.

## Edit Scope

The generated Codex assets are intentionally repo-local:

- `.codex/agents/arm-auto-solutions-expert.toml`
- `.codex/skills/arm-auto-solutions/`
- `.omx/hooks/arm-auto-solutions-context.mjs`

No upstream source layer under `arm-zena-css/`, `sw-ref-stack/`, or `layers/`
was modified for this analysis.
