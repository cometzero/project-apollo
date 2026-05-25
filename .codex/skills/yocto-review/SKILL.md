---
name: yocto-review
description: Yocto/OpenEmbedded metadata review workflow for /build/arm/arm-auto-solutions. Use whenever a prompt mentions Yocto, OpenEmbedded, BitBake, kas layer updates, layers, recipes, .bb/.bbappend/.bbclass files, layer.conf, machine/distro/image configuration, PACKAGECONFIG, SRC_URI, FILES, RDEPENDS/RRECOMMENDS, do_install, patches, bbmask, sstate, package QA, yocto-check-layer, 로컬 패치, 레이어/레시피 리뷰, or when the yocto-auto-review hook reports pending Yocto metadata review.
---

# Yocto Review

Use this skill for focused review of Yocto metadata in
`/build/arm/arm-auto-solutions`.

## Intake

1. Read `.config.yaml` and confirm the active kas variant.
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
kas shell .config.yaml -c 'bitbake-layers show-layers'
kas shell .config.yaml -c 'bitbake-layers show-appends'
kas shell .config.yaml -c 'bitbake-layers show-overlayed'
kas shell .config.yaml -c 'yocto-check-layer -- <layer>'
```

For recipe changes:

```bash
kas shell .config.yaml -c 'bitbake <recipe> -c fetch'
kas shell .config.yaml -c 'bitbake <recipe> -c patch'
kas shell .config.yaml -c 'bitbake <recipe> -c compile'
kas shell .config.yaml -c 'bitbake <recipe> -c install'
kas shell .config.yaml -c 'bitbake <recipe> -c package_qa'
kas shell .config.yaml -c 'bitbake <recipe> -c populate_lic'
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
