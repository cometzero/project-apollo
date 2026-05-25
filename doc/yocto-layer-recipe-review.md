# Yocto Layer And Recipe Review

Generated: 2026-05-15

## Purpose

Use this checklist when a new Yocto layer, recipe, append, machine
configuration, image feature, or patch is created in this workspace. The goal is
to catch metadata, dependency, license, patch, packaging, and reproducibility
issues before a full image build or FVP run.

This review is project-local to `/build/arm/arm-auto-solutions`. It uses the
active kas configuration in `.config.yaml` unless the change explicitly targets
another kas variant.

## Primary Source Areas

Review changes only in the source owner that owns the layer:

| Area | Typical review target |
| --- | --- |
| `arm-zena-css/yocto/meta-zena-css-bsp` | RD-Aspen BSP, machine, firmware, kernel, OP-TEE, TF-A, TF-M, FVP recipes. |
| `arm-zena-css/yocto/meta-zena-css-safety-island` | Safety Island Zephyr recipes, CL1 firmware integration, SI-specific QA. |
| `sw-ref-stack/yocto/meta-arm-auto-solutions` | Shared images, EWAOL features, Xen, HIPC/PFDI Linux integration, demos, OEQA. |
| `layers/*` | Pinned external layers; avoid direct edits unless explicitly requested. |

## Review Levels

Use the cheapest level that proves the requested change, then escalate only when
risk requires it.

| Level | Proves | Typical commands |
| --- | --- | --- |
| Static | File structure, style, layer dependencies, obvious recipe mistakes. | `rg`, `bitbake-layers show-*`, optional `oelint-adv`. |
| Parse | BitBake can parse the active layer graph and environment. | `bitbake -p`, `bitbake -e <recipe>`. |
| Task | The new or changed recipe passes the relevant task ladder. | `bitbake <recipe> -c fetch`, `-c patch`, `-c compile`, `-c install`, `-c package_qa`. |
| Image | The image using the layer/recipe still builds. | `kas build .config.yaml` or a narrower image target. |
| Runtime | Built artifacts boot and tests pass on FVP or hardware. | Route to `test-expert` or `debug-expert`. |

## Layer Review

For a new or changed layer, inspect `conf/layer.conf` first:

- `BBPATH` includes `${LAYERDIR}` only when the layer has configuration,
  classes, or includes that BitBake must find.
- `BBFILES` matches the intended `recipes-*/*/*.bb` and `.bbappend` layout.
- `BBFILE_COLLECTIONS` uses a unique collection name.
- `BBFILE_PATTERN_<collection>` points only at this layer.
- `LAYERDEPENDS_<collection>` names every layer required by recipes,
  appends, bbclasses, image features, machines, or dynamic layers.
- `LAYERSERIES_COMPAT_<collection>` matches the Yocto release used by the
  active kas stack.
- `BBFILES_DYNAMIC` is used for optional dynamic-layer metadata instead of
  making optional layers hard dependencies.
- Layer-level QA overrides are narrow and documented. Do not add broad
  `INSANE_SKIP` or `ERROR_QA` changes without a reason tied to a package,
  class, layer, or machine.

Run layer introspection from the active kas environment:

```bash
kas shell .config.yaml -c 'bitbake-layers show-layers'
kas shell .config.yaml -c 'bitbake-layers show-recipes'
kas shell .config.yaml -c 'bitbake-layers show-appends'
kas shell .config.yaml -c 'bitbake-layers show-overlayed'
kas shell .config.yaml -c 'bitbake-layers show-cross-depends'
```

For a new layer or a compatibility-sensitive layer change, run
`yocto-check-layer` inside the initialized Yocto environment. Include declared
dependencies and BSP machines when relevant:

```bash
kas shell .config.yaml -c 'yocto-check-layer --dependency <dep-layer> -- <layer>'
kas shell .config.yaml -c 'yocto-check-layer --machines fvp-rd-aspen -- <bsp-layer>'
```

Record the command output as compatibility evidence. If `yocto-check-layer` is
not available in the environment, classify that as a toolchain blocker rather
than a layer pass.

## Recipe Review

For a new or changed recipe, inspect the recipe file before building:

- File name, `PN`, and `PV` express the real package identity and version.
- `SUMMARY`, `DESCRIPTION`, `HOMEPAGE`, `SECTION`, and package purpose are
  accurate and short enough to be useful.
- `LICENSE` uses SPDX-style Yocto identifiers and `LIC_FILES_CHKSUM` points at
  upstream license text. A license checksum update needs a clear reason.
- `SRC_URI` is reproducible. Prefer fixed releases or fixed `SRCREV` values;
  avoid `AUTOREV` outside deliberate development-only workflows.
- Archive `SRC_URI` entries have checksums.
- Patch files have an `Upstream-Status:` tag and useful context.
- `inherit` uses the closest existing class (`cmake`, `meson`, `autotools`,
  `python_pep517`, `setuptools3`, `cargo`, `kernel-module`, `systemd`, and so
  on) before custom tasks are added.
- `DEPENDS` captures build-time dependencies. `RDEPENDS:${PN}` is used only for
  runtime dependencies that automatic shlib/pkgdata detection cannot infer.
- Custom tasks are idempotent and avoid host-path leakage.
- `do_install` writes only under `${D}` and uses deterministic install commands.
- `PACKAGES`, `FILES:*`, `SYSTEMD_SERVICE:*`, users/groups, config files, and
  image feature hooks match the intended runtime footprint.
- `INSANE_SKIP:*` is last resort, package-scoped, and justified in a comment.

Run a narrow task ladder before a full image build:

```bash
kas shell .config.yaml -c 'bitbake <recipe> -c fetch'
kas shell .config.yaml -c 'bitbake <recipe> -c unpack'
kas shell .config.yaml -c 'bitbake <recipe> -c patch'
kas shell .config.yaml -c 'bitbake <recipe> -c configure'
kas shell .config.yaml -c 'bitbake <recipe> -c compile'
kas shell .config.yaml -c 'bitbake <recipe> -c install'
kas shell .config.yaml -c 'bitbake <recipe> -c package'
kas shell .config.yaml -c 'bitbake <recipe> -c package_qa'
kas shell .config.yaml -c 'bitbake <recipe> -c populate_lic'
```

Use environment inspection when a value is surprising:

```bash
kas shell .config.yaml -c 'bitbake -e <recipe> | rg "^(PN|PV|S|B|D|WORKDIR|DEPENDS|RDEPENDS|SRC_URI|LICENSE|LIC_FILES_CHKSUM)="'
```

Check task logs under the recipe work directory when a task fails. In this
workspace, generated task logs are normally below `build/tmp_baremetal/work/`
and cooker logs are below `build/tmp_baremetal/log/cooker/fvp-rd-aspen/`.

## Static Lint Option

`oelint-adv` is optional but useful for recipe and layer policy review. Run it
only as an additional signal; BitBake parse/task/QA checks remain the authority.

```bash
oelint-adv --release walnascar <recipe-or-layer-files>
```

For `.bbappend` files, pass the append files explicitly. If `oelint-adv` is not
installed, report it as skipped optional lint rather than a validation failure.

## Codex Auto Review

The project-local `$yocto-review` skill lives under
`.codex/skills/yocto-review`. Use it for focused review of Yocto metadata.

Codex native hooks are already registered globally through
`~/.codex/hooks.json` and dispatch into OMX hook plugins. This project keeps the
Yocto behavior repo-local by implementing `.omx/hooks/yocto-auto-review.mjs`
instead of editing the global Codex hook file for a single workspace.

The hook watches Codex `PostToolUse` events for new or changed Yocto metadata
paths under `arm-zena-css/yocto/`, `sw-ref-stack/yocto/`, and `layers/`. It
ignores `.codex/`, `.omx/`, `doc/`, and `build/`.

When matching files are detected, the hook records pending review state under:

```text
.omx/state/hooks/plugins/yocto-auto-review/data.json
```

On `turn-complete`, the hook sends one deduplicated `$yocto-review` prompt to
the active Codex pane. If tmux side effects are unavailable, the pending state
and hook log remain as evidence and the review can be invoked manually with
`$yocto-review`.

## Project-Specific Review Patterns

For `meta-zena-css-bsp`:

- Check machine and firmware coupling before touching
  `conf/machine/fvp-rd-aspen.conf`, `recipes-bsp`, `recipes-security`, or kernel
  recipes.
- Firmware and separate-processor binaries can trigger architecture QA. Prefer
  proving intent from the recipe and package contents before adding
  `INSANE_SKIP`.

For `meta-zena-css-safety-island`:

- Confirm Zephyr recipe changes still match the Safety Island source tree under
  `arm-zena-css/components/safety_island/zephyr`.
- Patch status is treated as QA evidence in this layer, so new patches need an
  explicit `Upstream-Status:`.

For `meta-arm-auto-solutions`:

- Check `REQUIRED_IMAGE_FEATURES` and `CONFLICT_IMAGE_FEATURES` before changing
  image recipes or image feature classes.
- HIPC, PFDI, Xen, and demo recipes often cross kernel, user-space, image, and
  runtime validation boundaries. Do not claim runtime success from BitBake
  success alone.

## Closeout Evidence

A review closeout should include:

- changed layer/recipe paths,
- exact `kas shell`, `bitbake`, `bitbake-layers`, `yocto-check-layer`, or
  `oelint-adv` commands run,
- static, parse, task, image, and runtime status separated,
- skipped checks and concrete blockers,
- relevant log paths for any failure.

## References

- Yocto Project Development Tasks Manual, "Understanding and Creating Layers":
  https://docs.yoctoproject.org/dev/dev-manual/layers.html
- Yocto Project Development Tasks Manual, "Writing a New Recipe":
  https://docs.yoctoproject.org/dev/dev-manual/new-recipe.html
- Yocto Project Contributor Guide, "Recipe Style Guide":
  https://docs.yoctoproject.org/dev/contributor-guide/recipe-style-guide.html
- Yocto Project Reference Manual, "QA Error and Warning Messages":
  https://docs.yoctoproject.org/dev/ref-manual/qa-checks.html
- `oelint-adv` upstream repository:
  https://github.com/priv-kweihmann/oelint-adv
