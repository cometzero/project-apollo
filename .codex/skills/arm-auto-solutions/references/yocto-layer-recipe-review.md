# Yocto Layer And Recipe Review Reference

Use this reference when a task adds or reviews Yocto metadata in
`/build/arm/arm-auto-solutions`.

## First Choice Agent

Route Yocto metadata reviews to `yocto-expert`. Route runtime-only failures to
`test-expert` or `debug-expert` after build evidence exists.

## Source Boundaries

- `arm-zena-css/yocto/meta-zena-css-bsp`: RD-Aspen BSP, firmware, machine,
  kernel, FVP.
- `arm-zena-css/yocto/meta-zena-css-safety-island`: Safety Island Zephyr.
- `sw-ref-stack/yocto/meta-arm-auto-solutions`: images, HIPC, PFDI, Xen, demos,
  OEQA.
- `layers/*`: pinned external sources; avoid direct edits unless requested.

## Review Protocol

1. Read `.config.yaml` and confirm the target kas variant.
2. Inspect `conf/layer.conf` for `BBFILES`, `BBFILE_COLLECTIONS`,
   `LAYERDEPENDS`, `LAYERSERIES_COMPAT`, and dynamic-layer behavior.
3. Inspect recipes for identity, license, reproducible source fetch, patch
   status, correct class inheritance, dependency scope, package contents, and
   package-scoped QA exceptions.
4. Use `kas shell .config.yaml -c 'bitbake-layers show-*'` for layer graph and
   append/overlay evidence.
5. Use `kas shell .config.yaml -c 'bitbake <recipe> -c package_qa'` and
   `-c populate_lic` before claiming recipe validation.
6. Use `yocto-check-layer` for new layers or compatibility-sensitive changes
   when the tool is available in the kas environment.
7. Use `oelint-adv --release walnascar ...` only as optional static lint.

## Closeout

Separate static, parse, BitBake task, image, and runtime evidence. Mention
skipped optional tools separately from failed required checks.
