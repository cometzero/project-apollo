# Generated Artifacts And Risks

Updated: 2026-06-18

## Summary

The workspace contains large generated Yocto, local-build, and QBox runtime
outputs under `build/`. Historical evidence in this document records an older
`fvp-rd-aspen` baremetal image build. The current active source/build
configuration uses `MACHINE = "apollo-fvp"` and writes local-build/QBox
evidence under `build/local-apollo-fvp/` and `build/qbox-apollo-fvp/`.

## Historical Build Evidence

The historical build log
`build/tmp_baremetal/log/cooker/fvp-rd-aspen/20260510034323.log` ends with:

```text
NOTE: Tasks Summary: Attempted 6590 tasks of which 4874 didn't need to be rerun and all succeeded.
```

This confirms a local successful `baremetal-image` build for that historical
workspace state. It does not prove current Apollo runtime boot or test success.

## Historical Deploy Artifact Classes

The historical deploy directory
`build/tmp_baremetal/deploy/images/fvp-rd-aspen/` contains these artifact
classes:

| Class | Examples | Notes |
| --- | --- | --- |
| Primary Compute image | `baremetal-image-fvp-rd-aspen-20260510034403.wic` | Boot disk image for the historical baremetal build. |
| Linux kernel/modules | `Image--6.18.5...bin`, `modules--6.18.5...tgz` | Kernel version aligns with machine preference for Linux 6.18. |
| Firmware images | `fip-rdaspen.bin`, `fip_with_bl2.bin`, `bl2-rdaspen.bin`, `rse-rom-image.img`, `rse-flash-image.img`, `ap-flash-image.img` | TF-A/TF-M/RSE/AP flash chain artifacts. |
| Safety Island | `si0_ramfw.bin`, `si0_ramfw.elf`, `zephyr-demos-cl1.bin`, `zephyr-demos-cl1.elf` | Safety Island CL0/CL1 outputs. |
| Secure boot/capsule | `efi-capsule-update-image.img.uefi.capsule`, `signed_capsule_bl2.bin`, `signed_capsule_si0_ramfw.bin`, `signed_capsule_safety_island_cl1.bin`, `uefi-sb-authenticated-variables/*` | Present because UEFI capsule and signing fragments are included. |
| Metadata | `*.spdx.json`, `*.manifest`, `*.testdata.json`, `*.fvpconf` | Useful for reproducibility and runtime launch checks. |

## Historical FVP Configuration Artifact

The generated `.fvpconf` identifies the provider as `fvp-rd-aspen-native`, the
executable as `FVP_Zena_CSS_Cfg2`, and sets paths to the historical deploy
images.
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
- `hsoc-stack/components/primary_compute/*`
- `hsoc-stack/components/system_mgmt/*`
- `hsoc-stack/yocto/meta-hsoc-auto-solutions`
- `hsoc-stack/yocto/meta-hsoc-bsp`
- `tools/qbox/`
- `tools/qemu/`
- `scripts/`
- `tests/`
- `layers/*` when intentionally patching a local checkout
- `build/conf/` as active local Yocto configuration
- `.config.yaml` as historical/generated kas configuration input/state
- `doc/`, `.codex/`, `.omx/` for local Codex/project analysis state

## Operational Risks

### Top-Level Git And Nested Source Ownership

The root directory is now a Git worktree for the `project-apollo` repository.
Most implementation source still belongs to nested submodules. Check both the
root and the relevant nested repository before claiming the tree is clean:

```bash
git status --short --branch
git submodule foreach --recursive 'git status --short --branch'
```

### Generated Build Tree Is Large

Avoid broad recursive scans over `build/` unless the task is about local build
evidence. Prefer targeted paths:

```bash
find build/tmp_baremetal/deploy/images/apollo-fvp -maxdepth 2 -type f
find build/qbox-apollo-fvp -maxdepth 2 \( -name result.json -o -name summary.txt \)
```

### Runtime Validation Requires FVP And Plugins

A successful BitBake build does not imply successful runtime. FVP runtime checks
require the correct FVP binary, deploy artifacts, terminal mappings, networking
ports, and the Crypto plugin path. The test automation config documents required
FVP parameters and paths under
`sw-ref-stack/test_automation/test_automation/configs/baremetal_config.yaml`.

### Pinned SHAs Are Release-Specific

The historical kas include stack uses `repos.pinned.yml`, which describes
itself as the v2.1 pinned SHA file. For the active workspace, inspect
`.gitmodules`, nested Git HEADs, and `build/conf/` before assuming pinned
release behavior.

### Editing External Layers Can Break Patch Flow

Historical kas flows applied solution-owned patches to external layers. For the
active Apollo workspace, prefer moving durable external-layer behavior into
`hsoc-stack/yocto/meta-hsoc-auto-solutions/dynamic-layers/` or
`hsoc-stack/yocto/meta-hsoc-bsp/`. Direct edits in `layers/*` are easy to lose
on a fresh checkout.

## Fast Evidence Commands

Current configuration:

```bash
sed -n '1,160p' build/conf/local.conf
sed -n '1,180p' build/conf/bblayers.conf
cat build/conf/templateconf.cfg
```

Historical deployed image list:

```bash
find build/tmp_baremetal/deploy/images/fvp-rd-aspen -maxdepth 2 -type f | sort
```

Historical build status:

```bash
tail -80 build/tmp_baremetal/log/cooker/fvp-rd-aspen/20260510034323.log
```

Nested repo status checks:

```bash
git status --short --branch
git submodule foreach --recursive 'git status --short --branch'
```
