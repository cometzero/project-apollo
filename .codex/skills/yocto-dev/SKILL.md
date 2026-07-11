---
name: yocto-dev
description: Yocto/OpenEmbedded/BitBake development workflow for Apollo. Use for layers, recipes, bbappend, bbclass, MACHINE/BSP/distro/image configuration, PACKAGECONFIG, fetch/patch/build/package/rootfs tasks, systemd integration, kernel/U-Boot metadata, SDK, QA, licenses, sstate, mirrors, or build debugging.
---

# Yocto Development

## Active Project Contract

Read these inputs before any edit or build claim:

```text
build/conf/local.conf
build/conf/bblayers.conf
build/conf/templateconf.cfg
yocto_build.sh
```

Current baseline:

- Poky/Yocto: 5.2.4
- machine: `apollo-qvp`
- template: `hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp`
- image: `nexios-image`
- TMPDIR: `build/tmp_baremetal`
- variant: cfg2

The active environment is initialized with:

```bash
source layers/poky/oe-init-build-env build
```

## Layer Ownership

- product, distro, image, template, and dynamic-layer policy:
  `hsoc-stack/yocto/meta-hsoc-auto-solutions`
- BSP, firmware, kernel, module signing, OP-TEE, and machine integration:
  `hsoc-stack/yocto/meta-hsoc-bsp`
- shared automotive metadata: `sw-ref-stack/yocto/meta-arm-auto-solutions`
- reference Zena metadata: `arm-zena-css/yocto`
- pinned external layers: `layers`

Avoid editing `layers/*` unless the user explicitly requests an external-layer
change. Keep permanent product policy out of `build/conf/local.conf`.

## Core Rules

1. Inspect the final provider and variable values before editing metadata.
2. Start with the first failing task and its `log.do_*` / `run.do_*` under
   `build/tmp_baremetal/work`.
3. Use the narrowest task that can prove the change.
4. Do not run `cleanall`, delete downloads/sstate/TMPDIR, disable QA, or run a
   full image without a demonstrated need or explicit request.
5. Preserve license checks, package ownership, patch `Upstream-Status`, layer
   compatibility, and source repository boundaries.
6. Distinguish parse, task, image, deploy, and runtime evidence.

Read `references/workflows.md` for task-specific fetch, patch, packaging,
systemd, rootfs, kernel, and layer workflows.

## Inspection Commands

```bash
bitbake-layers show-layers
bitbake-layers show-appends
bitbake-layers show-recipes <recipe>
bitbake <recipe> -c listtasks
bitbake -e <recipe>
```

## Validation Ladder

Select only applicable stages:

```bash
bitbake <recipe> -c fetch
bitbake <recipe> -c unpack
bitbake <recipe> -c patch
bitbake <recipe> -c configure
bitbake <recipe> -c compile
bitbake <recipe> -c install
bitbake <recipe> -c package
bitbake <recipe> -c package_qa
bitbake <recipe> -c populate_lic
bitbake nexios-image -c rootfs
./yocto_build.sh
```

Use `$yocto-review` for review-only work. Route read-only diagnosis with
`agent_type = "yocto-expert"` (`gpt-5.6-sol`, high) and metadata
implementation with `agent_type = "yocto_dev"` (`gpt-5.6-sol`, high). If
`agent_type` is unavailable, use the project leader and do not claim
specialist selection.

Report environment detected, owning layer, files inspected/changed, exact
commands, task summary, produced artifacts, pre-existing failures, and runtime
checks not performed.
