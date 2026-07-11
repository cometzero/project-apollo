---
name: yocto-review
description: Review Yocto/OpenEmbedded metadata for this Apollo project. Use for layers, recipes, bbappend, bbclass, layer.conf, machine/distro/image config, PACKAGECONFIG, dependencies, tasks, patches, QA, licenses, sstate, or auto-review findings.
---

# Yocto Review

This is a findings-first review workflow. Use
`agent_type = "yocto-expert"` for read-only diagnosis and review
(`gpt-5.6-sol`, high), and route accepted implementation with
`agent_type = "yocto_dev"` (`gpt-5.6-sol`, high). If `agent_type` is
unavailable, use the project leader and do not claim specialist selection.

## Intake And Ownership

Read:

```text
build/conf/local.conf
build/conf/bblayers.conf
build/conf/templateconf.cfg
```

Active product layers:

- `hsoc-stack/yocto/meta-hsoc-auto-solutions`
- `hsoc-stack/yocto/meta-hsoc-bsp`

Also inspect `sw-ref-stack/yocto/meta-arm-auto-solutions` or `arm-zena-css/yocto`
when the change reaches those owners. Treat `layers/*` as external unless a
direct edit was explicitly requested.

If invoked from an automatic review hook, inspect the corresponding pending
state before reviewing. Use `doc/yocto-layer-recipe-review.md` and
`references/review-checklist.md` for the detailed checklist.

## Review Checks

For layers, inspect collection/pattern, priority, dependencies, compatible
series, dynamic layers, BBMASK, and QA policy. For recipes, inspect identity,
license checksums, source revision, patch status/order, inherited classes,
dependency scope, package contents, services, users, permissions, and
package-scoped QA exceptions.

Prove claims with final BitBake values rather than metadata text alone. Check
whether a changed task is reachable for active `apollo-qvp` and `nexios-image`.

## Validation

```bash
source layers/poky/oe-init-build-env build
bitbake-layers show-layers
bitbake-layers show-appends
bitbake-layers show-overlayed
bitbake <recipe> -c fetch
bitbake <recipe> -c patch
bitbake <recipe> -c compile
bitbake <recipe> -c package_qa
bitbake <recipe> -c populate_lic
```

Use `yocto-check-layer -- <layer>` for new or compatibility-sensitive layers
when available. `oelint-adv --release walnascar` is optional static evidence;
BitBake parse/task results are stronger.

Report findings first by severity with file/line, reachable failure path, and
why the issue is not a false positive. Then list reviewed paths, commands,
static/parse/task/image/runtime evidence separately, skipped checks, and
remaining hook state.
