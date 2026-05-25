# Generated Artifacts And Risks

Generated: 2026-05-15

## Summary

The workspace contains a large generated Yocto build under `build/`. Current
evidence shows a completed baremetal image build for `fvp-rd-aspen`, including
firmware, UEFI capsule, Zephyr CL1, FVP configuration, SPDX, and test data
artifacts. These files are useful evidence but should not be edited as source.

## Current Build Evidence

The current build log
`build/tmp_baremetal/log/cooker/fvp-rd-aspen/20260510034323.log` ends with:

```text
NOTE: Tasks Summary: Attempted 6590 tasks of which 4874 didn't need to be rerun and all succeeded.
```

This confirms a local successful `baremetal-image` build in the current
workspace state. It does not prove runtime boot or test success.

## Deploy Artifact Classes

The deploy directory
`build/tmp_baremetal/deploy/images/fvp-rd-aspen/` contains these artifact
classes:

| Class | Examples | Notes |
| --- | --- | --- |
| Primary Compute image | `baremetal-image-fvp-rd-aspen-20260510034403.wic` | Boot disk image for current baremetal build. |
| Linux kernel/modules | `Image--6.18.5...bin`, `modules--6.18.5...tgz` | Kernel version aligns with machine preference for Linux 6.18. |
| Firmware images | `fip-rdaspen.bin`, `fip_with_bl2.bin`, `bl2-rdaspen.bin`, `rse-rom-image.img`, `rse-flash-image.img`, `ap-flash-image.img` | TF-A/TF-M/RSE/AP flash chain artifacts. |
| Safety Island | `si0_ramfw.bin`, `si0_ramfw.elf`, `zephyr-demos-cl1.bin`, `zephyr-demos-cl1.elf` | Safety Island CL0/CL1 outputs. |
| Secure boot/capsule | `efi-capsule-update-image.img.uefi.capsule`, `signed_capsule_bl2.bin`, `signed_capsule_si0_ramfw.bin`, `signed_capsule_safety_island_cl1.bin`, `uefi-sb-authenticated-variables/*` | Present because UEFI capsule and signing fragments are included. |
| Metadata | `*.spdx.json`, `*.manifest`, `*.testdata.json`, `*.fvpconf` | Useful for reproducibility and runtime launch checks. |

## FVP Configuration Artifact

The generated `.fvpconf` identifies the provider as `fvp-rd-aspen-native`, the
executable as `FVP_Zena_CSS_Cfg2`, and sets paths to the current deploy images.
It also maps consoles for Safety Island CL1, Primary Compute, TF-A, RSE, and SCP
(`build/tmp_baremetal/deploy/images/fvp-rd-aspen/baremetal-image-fvp-rd-aspen-20260510034403.fvpconf:1`).

The generated config includes a Crypto plugin argument:

```text
--plugin .../fvp-rd-aspen-native/usr/bin/Crypto.so
```

Use this file as a launch-evidence reference, but prefer the project test
automation config for repeatable pytest runs.

## Generated vs Source Boundaries

Treat these directories as generated:

- `build/cache`
- `build/sstate-cache`
- `build/tmp_baremetal`
- `build/tmp_baremetal/work*`
- `build/tmp_baremetal/sysroots*`
- `build/tmp_baremetal/deploy`

Treat these directories as source:

- `arm-zena-css/`
- `sw-ref-stack/`
- `layers/*` when intentionally patching a local checkout
- `.config.yaml` as generated configuration input/state
- `doc/`, `.codex/`, `.omx/` for local Codex/project analysis state

## Operational Risks

### Root Directory Is Not A Git Repository

Running `git status` at `/build/arm/arm-auto-solutions` fails because the root
is not a Git worktree. Use `git -C arm-zena-css`, `git -C sw-ref-stack`, or
`git -C layers/<layer>` when checking source changes. Root-local files such as
`doc/` and `.codex/` are outside those nested Git repositories unless the user
has another external tracking mechanism.

### Generated Build Tree Is Large

Avoid broad recursive scans over `build/` unless the task is about local build
evidence. Prefer targeted paths:

```bash
find build/tmp_baremetal/deploy/images/fvp-rd-aspen -maxdepth 2 -type f
tail -80 build/tmp_baremetal/log/cooker/fvp-rd-aspen/20260510034323.log
```

### Runtime Validation Requires FVP And Plugins

A successful BitBake build does not imply successful runtime. FVP runtime checks
require the correct FVP binary, deploy artifacts, terminal mappings, networking
ports, and the Crypto plugin path. The test automation config documents required
FVP parameters and paths under
`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml`.

### Pinned SHAs Are Release-Specific

The current include stack uses `repos.pinned.yml`, which describes itself as the
v2.1 pinned SHA file. If a task asks for upstream branch behavior, inspect kas
includes and nested Git HEADs instead of assuming pinned release behavior.

### Editing External Layers Can Break Patch Flow

kas applies solution-owned patches to external layers. Prefer editing patch
sources under `arm-zena-css/yocto/kas/patches` or
`sw-ref-stack/yocto/kas/patches` when the intended durable change is a layer
patch. Direct edits in `layers/*` are easy to lose on a fresh kas checkout.

## Fast Evidence Commands

Current configuration:

```bash
sed -n '1,120p' .config.yaml
```

Current deployed image list:

```bash
find build/tmp_baremetal/deploy/images/fvp-rd-aspen -maxdepth 2 -type f | sort
```

Current build status:

```bash
tail -80 build/tmp_baremetal/log/cooker/fvp-rd-aspen/20260510034323.log
```

Nested repo status checks:

```bash
git -C arm-zena-css status --short
git -C sw-ref-stack status --short
git -C layers/meta-arm status --short
```
