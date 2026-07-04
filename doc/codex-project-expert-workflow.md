# Codex Project Expert Workflow

Updated: 2026-07-04

## Summary

This workspace now has repo-local Codex automation for future sessions:

- Native project expert agent:
  `.codex/agents/arm-auto-solutions-expert.toml`
- Specialist native agents:
  `.codex/agents/yocto-expert.toml`,
  `.codex/agents/zephyr-expert.toml`,
  `.codex/agents/linux-kernel-expert.toml`,
  `.codex/agents/arm-expert.toml`,
  `.codex/agents/test-expert.toml`,
  `.codex/agents/debug-expert.toml`
- Project skill:
  `.codex/skills/arm-auto-solutions/SKILL.md`
- Yocto review skill:
  `.codex/skills/yocto-review/SKILL.md`
- Linux kernel review skill:
  `.codex/skills/linux-kernel-review/SKILL.md`
- OMX hook plugin:
  `.omx/hooks/arm-auto-solutions-context.mjs`
- Yocto auto-review hook plugin:
  `.omx/hooks/yocto-auto-review.mjs`
- Linux kernel auto-review hook plugin:
  `.omx/hooks/linux-kernel-auto-review.mjs`

These assets are scoped to Codex/OMX behavior and do not modify solution source
repositories.

## Project Expert Agent

The native agent is intended for grounded project analysis and implementation
guidance in this workspace. It encodes the important boundaries:

- Root is a Git repository that pins nested source repositories with
  submodules.
- `arm-zena-css/`, `sw-ref-stack/`, `hsoc-stack/components/*`,
  `hsoc-stack/yocto/*`, `hsoc-stack/tools/qbox/`,
  `hsoc-stack/tools/qbox-platform/`, `hsoc-stack/tools/qemu/`, and `layers/*`
  are separate source zones.
- `build/conf/` is active local Yocto configuration; the rest of `build/` is
  generated output and should be inspected only for evidence.
- Default outputs should include exact paths, commands, and validation evidence.

Use the agent when a future task needs Arm Auto Solutions, RD-Aspen/Apollo FVP,
Yocto, QBox, Safety Island, or FVP-aware project guidance.

## Specialist Agents

Use the specialist agents when a task has a clear technical owner:

| Agent | Use for |
| --- | --- |
| `yocto-expert` | kas, BitBake metadata, layer dependencies, image features, recipes, sstate, deploy artifacts, Yocto QA, and new layer/recipe review. |
| `zephyr-expert` | Safety Island CL1 Zephyr module, board/DTS/Kconfig/CMake, MHUv3, OpenAMP/RPMsg, and SI PFDI. |
| `linux-kernel-expert` | Linux kernel recipes/config, boot args, device tree, remoteproc/RPMsg, HIPC, PFDI kernel driver, and PREEMPT_RT surfaces. |
| `arm-expert` | Arm Zena CSS architecture, Cortex-A/R/M domains, RSE, TF-A, TF-M, OP-TEE, SCP, U-Boot, SystemReady, FVP, secure boot, and firmware update flows. |
| `test-expert` | OEQA, pytest test automation, FVP/FPGA validation, CI, log evidence, and blocker classification. |
| `debug-expert` | Cross-layer failure triage across kas, BitBake, artifacts, FVP boot, firmware, Linux, Safety Island, tests, and CI. |

## Project Skill

The skill is named `arm-auto-solutions`. It should trigger when a user asks for
work in `/build/arm/arm-auto-solutions`, Arm Zena CSS, RD-Aspen, Safety Island,
or the Arm Automotive Solutions software reference stack.

The skill's main job is to keep future Codex turns from making expensive or
unsafe assumptions. It directs Codex to:

- inspect `build/conf/local.conf`, `build/conf/bblayers.conf`, and
  `build/conf/templateconf.cfg` before build/runtime claims,
- preserve nested repo boundaries,
- avoid broad `build/` scans,
- choose source paths by subsystem,
- report build/runtime evidence separately.

The dedicated `yocto-review` skill handles new layer, recipe, append, patch,
image feature, and machine metadata reviews. It is also the target of the
`yocto-auto-review` hook.

The dedicated `linux-kernel-review` skill handles Linux kernel source, module,
patch, cfg/scc, Kconfig/Kbuild/Makefile, and kernel metadata reviews. It is the
target of the `linux-kernel-auto-review` hook.

## Project Hook

The hook plugin is an additive OMX hook under `.omx/hooks`. It updates
per-plugin state with a compact project context on session and turn lifecycle
events. It does not modify Codex goal state, source files, or build artifacts.

The Yocto auto-review hook is backed by Codex native hook events through the OMX
dispatcher. It watches tool events for changed Yocto metadata paths, records
pending review state in `.omx/state/hooks/plugins/yocto-auto-review/`, and sends
one deduplicated `$yocto-review` prompt when a turn completes.

The Linux kernel auto-review hook follows the same Codex-native hook pattern for
kernel source and metadata paths. It records state in
`.omx/state/hooks/plugins/linux-kernel-auto-review/` and sends one deduplicated
`$linux-kernel-review` prompt when a turn completes.

Validation commands:

```bash
omx hooks status
omx hooks validate
omx hooks test
```

The hook is intentionally conservative. It logs context availability and writes
hook state for tools that inspect OMX hook plugin state. It does not inject text
into prompts or send tmux keys.

## Recommended Future Intake

For future Codex work in this workspace, start with:

```bash
sed -n '1,160p' build/conf/local.conf
sed -n '1,180p' build/conf/bblayers.conf
cat build/conf/templateconf.cfg
find . -path ./build -prune -o -path ./.omx -prune -o -name AGENTS.md -print
git status --short --branch
git submodule status --recursive
```

Then choose the narrow source area:

- Yocto build config: `build/conf/`, `yocto_build.sh`,
  `hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-fvp/`
- Yocto layer/recipe review:
  `doc/yocto-layer-recipe-review.md`,
  `.codex/skills/arm-auto-solutions/references/yocto-layer-recipe-review.md`
- Linux kernel source review:
  `doc/linux-kernel-source-review.md`,
  `.codex/skills/linux-kernel-review/references/review-checklist.md`
- RD-Aspen BSP and upstream firmware metadata:
  `arm-zena-css/yocto/meta-zena-css-bsp`
- Apollo primary compute sources:
  `hsoc-stack/components/primary_compute/`
- Apollo system management and Safety Island sources:
  `hsoc-stack/components/system_mgmt/`
- Apollo Yocto metadata:
  `hsoc-stack/yocto/meta-hsoc-auto-solutions/`,
  `hsoc-stack/yocto/meta-hsoc-bsp/`
- QBox/QEMU platform sources:
  `hsoc-stack/tools/qbox/`,
  `hsoc-stack/tools/qbox-platform/`,
  `hsoc-stack/tools/qemu/`
- Automotive images/tests:
  `sw-ref-stack/yocto/meta-arm-auto-solutions`,
  `sw-ref-stack/test_automation`
- Generated evidence:
  `build/local-apollo-fvp/`,
  `build/qbox-apollo-fvp/`,
  `build/tmp_baremetal/deploy/images/apollo-fvp`,
  `build/tmp_baremetal/log/cooker/apollo-fvp`

## Evidence Policy

When closing work in this project, report:

- exact files changed,
- exact commands run,
- whether evidence is build-time, runtime, or static-only,
- explicit blockers such as missing FVP, missing Artifactory credentials,
  missing build artifacts, or dirty/out-of-sync nested repositories.
