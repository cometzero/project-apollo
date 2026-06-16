---
name: arm-auto-solutions
description: Workspace workflow for this Arm Auto Solutions project. Use whenever a prompt mentions Arm Auto Solutions, Arm Zena CSS, RD-Aspen/RD Aspen, Apollo FVP, Yocto or BitBake builds, FVP boot/runtime/logs, EWAOL images, Safety Island or Zephyr, RSE, TF-A, TF-M, OP-TEE, SCP, U-Boot, PFDI, HIPC, sw-ref-stack, arm-zena-css, layers, build/tmp_baremetal artifacts, boot/빌드/부팅/검증/log analysis, or project-local Codex automation in this workspace.
---

# Arm Auto Solutions Project Skill

Use this skill for project work from the current project top directory.

All paths in commands, reports, and instructions are relative to the project
top directory unless an external tool explicitly requires an absolute path. Do
not hard-code machine-local roots or user home directories in project-local
guidance.

## Core Rule

Treat the root as a traditional Yocto/BitBake workspace, not a single Git
repository. The source ownership boundaries are:

- `arm-zena-css/` - Arm Zena CSS BSP, Safety Island, firmware, and Zena
  documentation.
- `sw-ref-stack/` - Arm Automotive Solutions shared images, EWAOL integration,
  test automation, and CI fragments.
- `layers/*` - external Yocto layers, usually pinned upstream/downstream.
- `build/conf/` - active local Yocto build configuration.
- `build/` other than `build/conf/` - generated output, useful for evidence
  only.
- `doc/`, `.codex/`, `.omx/` - repo-local analysis and Codex automation.

## Intake

1. Read `build/conf/local.conf`, `build/conf/bblayers.conf`, and
   `build/conf/templateconf.cfg` before build or runtime claims.
2. Check local instructions with:
   `find . -path ./build -prune -o -path ./.omx -prune -o -name AGENTS.md -print`
3. Use `git -C arm-zena-css status --short` and
   `git -C sw-ref-stack status --short` for nested source repos. The workspace
   root itself is not a Git repository.
4. Avoid broad recursive scans of `build/`. Use targeted deploy/log paths.
5. Separate static analysis, BitBake build validation, and FVP runtime
   validation in status reports.

## Subsystem Map

- Yocto build config:
  `build/conf/local.conf`, `build/conf/bblayers.conf`,
  `build/conf/templateconf.cfg`, `build.sh`, and
  `hsoc-stack/yocto/meta-hsoc-apollo/conf/templates/apollo-fvp/`
- RD-Aspen BSP and firmware:
  `arm-zena-css/yocto/meta-zena-css-bsp`
- Safety Island Zephyr:
  `arm-zena-css/components/safety_island/zephyr/src`,
  `arm-zena-css/yocto/meta-zena-css-safety-island`
- Shared images, EWAOL features, Xen, HIPC/PFDI Linux integration:
  `sw-ref-stack/yocto/meta-arm-auto-solutions`
- Test automation:
  `sw-ref-stack/test_automation`
- Current generated evidence:
  `build/tmp_baremetal/deploy/images/apollo-fvp`,
  `build/tmp_baremetal/log/cooker/apollo-fvp`

## Common Commands

Current build config:

```bash
sed -n '1,160p' build/conf/local.conf
sed -n '1,180p' build/conf/bblayers.conf
cat build/conf/templateconf.cfg
```

Current configured build:

```bash
./build.sh
```

Interactive BitBake shell:

```bash
source layers/poky/oe-init-build-env build
```

Current build evidence:

```bash
find build/tmp_baremetal/log/cooker/apollo-fvp -maxdepth 1 -type f | sort | tail
find build/tmp_baremetal/deploy/images/apollo-fvp -maxdepth 2 -type f | sort
```

Python test automation smoke checks:

```bash
python -m compileall sw-ref-stack/test_automation
pytest sw-ref-stack/test_automation/unittests
```

Yocto layer/recipe review:

```bash
source layers/poky/oe-init-build-env build
bitbake-layers show-layers
bitbake-layers show-recipes <recipe>
bitbake <recipe> -c package_qa
yocto-check-layer -- <layer>
```

Use `$yocto-review` for dedicated Yocto metadata review. The project-local
`yocto-auto-review` hook is invoked through Codex native hook events and queues
this skill automatically when new Yocto metadata paths are created or changed.

Use `references/yocto-layer-recipe-review.md` and
`doc/yocto-layer-recipe-review.md` when a task creates or reviews a Yocto
layer, recipe, append, patch, image feature, or machine metadata.

Linux kernel source review:

```bash
source layers/poky/oe-init-build-env build
bitbake <module-recipe> -c compile
bitbake <module-recipe> -c package_qa
bitbake virtual/kernel -c kernel_configcheck
```

Use `$linux-kernel-review` for dedicated Linux kernel source and kernel metadata
review. The project-local `linux-kernel-auto-review` hook is invoked through
Codex native hook events and queues this skill when Linux kernel source,
module, patch, or kernel config paths are created or changed.

## Reporting Standard

Close with:

- exact files changed,
- exact commands run,
- validation status as static/build/runtime,
- explicit blockers such as missing FVP, missing Artifactory credentials,
  missing build artifacts, or root not being a Git repository.

For more context, read `references/project-map.md` only when the task needs a
compact project map or subsystem routing reminder.
