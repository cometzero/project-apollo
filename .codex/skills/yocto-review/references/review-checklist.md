# Yocto Review Checklist

## Layer

- `conf/layer.conf` has correct `BBFILES`, `BBFILE_COLLECTIONS`,
  `BBFILE_PATTERN`, `LAYERDEPENDS`, `LAYERSERIES_COMPAT`, and dynamic-layer
  handling.
- New layer dependencies are represented in kas config and not hidden by local
  build state.
- Layer-level QA overrides are narrow, documented, and not a broad escape hatch.
- `yocto-check-layer` is run for new layers or compatibility-sensitive changes
  when available.

## Recipe

- File name, `PN`, and `PV` match package identity and version.
- `SUMMARY`, `DESCRIPTION`, `HOMEPAGE`, `LICENSE`, and `LIC_FILES_CHKSUM` are
  accurate.
- `SRC_URI` is reproducible; archives have checksums and git recipes pin
  `SRCREV` unless explicitly development-only.
- Patches include `Upstream-Status:` and useful context.
- The closest existing class is inherited before custom tasks are added.
- `DEPENDS` and `RDEPENDS:${PN}` are scoped correctly.
- `do_install` writes only under `${D}` and package contents match `FILES:*`.
- `INSANE_SKIP:*` is package-scoped and justified.

## Project-Specific

- `meta-zena-css-bsp`: check machine, firmware, kernel, OP-TEE, TF-A, TF-M, and
  FVP coupling.
- `meta-zena-css-safety-island`: check Zephyr source coupling and patch-status
  QA.
- `meta-arm-auto-solutions`: check image features, HIPC, PFDI, Xen, demos, and
  runtime validation boundaries.
