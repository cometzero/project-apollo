# Arm Auto Solutions Analysis

Generated: 2026-05-15

This directory contains Codex-facing analysis notes for the current
`/build/arm/arm-auto-solutions` workspace. The workspace is a kas-generated
multi-repository Yocto tree rather than a single Git repository. The notes keep
source repositories, generated build artifacts, and Codex automation surfaces
separate.

## Documents

- [Project Architecture](project-architecture.md) - workspace layout,
  subsystems, and current configuration.
- [Arm Zena CSS Hardware Blocks](arm-zena-css-hardware-blocks.md) - RD-Aspen
  hardware block map, Safety Island/RSE/Primary Compute relationships, and
  FVP-visible device evidence.
- [QBox FVP Emulation Project](qbox-fvp-emulation-project.md) - project
  mission and workflow for implementing the Arm Zena CSS/RD-Aspen FVP behavior
  in QBox with SystemC/TLM/QEMU fidelity.
- [Yocto Build And Kas](yocto-build-and-kas.md) - kas include stack, build
  variants, targets, and reproducibility levers.
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
- [Headless FVP Boot Logs](fvp-log-boot.md) - non-interactive FVP launch with
  file-based stdout and per-console boot logs.
- [Generated Artifacts And Risks](generated-artifacts-and-risks.md) - current
  deploy artifacts, generated directories, and operational risks.
- [Codex Project Expert Workflow](codex-project-expert-workflow.md) - the
  project-specific Codex agent, skill, and hook added with this analysis.

## Evidence Scope

The analysis is grounded in repository-local files and current generated
artifacts. Source evidence is cited as `path:line` references. Generated build
outputs under `build/tmp_baremetal` are treated as evidence of this checkout's
current local state, not as upstream source.

## Edit Scope

The generated Codex assets are intentionally repo-local:

- `.codex/agents/arm-auto-solutions-expert.toml`
- `.codex/skills/arm-auto-solutions/`
- `.omx/hooks/arm-auto-solutions-context.mjs`

No upstream source layer under `arm-zena-css/`, `sw-ref-stack/`, or `layers/`
was modified for this analysis.
