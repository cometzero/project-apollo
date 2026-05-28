---
name: yocto-review
description: Yocto/OpenEmbedded metadata review workflow for /build/arm/arm-auto-solutions. Use whenever a prompt mentions Yocto, OpenEmbedded, BitBake, layers, recipes, .bb/.bbappend/.bbclass files, layer.conf, machine/distro/image configuration, bblayers.conf, local.conf, PACKAGECONFIG, SRC_URI, FILES, RDEPENDS/RRECOMMENDS, do_install, patches, bbmask, sstate, package QA, yocto-check-layer, 로컬 패치, 레이어/레시피 리뷰, or when the yocto-auto-review hook reports pending Yocto metadata review.
---

# Yocto Review

Use this skill for focused review of Yocto metadata in
`/build/arm/arm-auto-solutions`.

## Intake

1. Read `build/conf/local.conf`, `build/conf/bblayers.conf`, and
   `build/conf/templateconf.cfg`.
2. If the request came from the auto-review hook, inspect
   `.omx/state/hooks/plugins/yocto-auto-review/data.json` for pending paths.
3. Read `doc/yocto-layer-recipe-review.md` for the full project checklist.
4. Keep source ownership boundaries:
   - `arm-zena-css/yocto/meta-zena-css-bsp`
   - `arm-zena-css/yocto/meta-zena-css-safety-island`
   - `sw-ref-stack/yocto/meta-arm-auto-solutions`
   - `layers/*` only when direct external-layer edits were explicitly made.

## Review Workflow

For layer changes:

```bash
source layers/poky/oe-init-build-env build
bitbake-layers show-layers
bitbake-layers show-appends
bitbake-layers show-overlayed
yocto-check-layer -- <layer>
```

For recipe changes:

```bash
source layers/poky/oe-init-build-env build
bitbake <recipe> -c fetch
bitbake <recipe> -c patch
bitbake <recipe> -c compile
bitbake <recipe> -c install
bitbake <recipe> -c package_qa
bitbake <recipe> -c populate_lic
```

Use `references/review-checklist.md` for a compact checklist during review.
Use `oelint-adv --release walnascar ...` only as optional static lint.

## Output

Report findings first, ordered by severity, with file and line references.
Then report:

- review paths,
- exact commands run,
- static, parse, task, image, and runtime evidence separately,
- skipped checks and blockers,
- whether the auto-review hook state still has pending paths.
