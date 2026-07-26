---
name: arm-auto-solutions
description: Workspace workflow for this Arm Auto Solutions Apollo project. Use for Arm Zena CSS, RD-Aspen, Apollo QVP or FVP, Yocto/BitBake, QBox, SystemC, QEMU, Buildroot, firmware, Linux, Safety Island Zephyr, RSE, boot, logs, validation, and project-local agent routing.
---

# Arm Auto Solutions

Use this skill from the top-level Git superproject. Most implementation source
is owned by nested submodules; always identify the owning repository before
editing or committing.

## Required Intake

Read these files before any Yocto build or runtime claim:

```text
build/conf/local.conf
build/conf/bblayers.conf
build/conf/templateconf.cfg
```

The active baseline is:

- machine: `apollo-qvp`
- template: `hsoc-stack/yocto/meta-hsoc-auto-solutions/conf/templates/apollo-qvp`
- default image targets: `nexios-bsp-initramfs`, then `nexios-image`
- BSP-only build: `./yocto_build.sh --bsp`
- variant: `cfg2`
- Primary Compute CPUs: `4`
- BitBake TMPDIR: `build/tmp_baremetal`
- local build root: `build/local-${MACHINE}`
- QBox QVP runtime evidence: `build/qbox-apollo-qvp`
- explicit FVP-comparison QBox evidence: `build/qbox-apollo-fvp`

Apollo FVP remains a reference, comparison, and source-level debug path. Do
not describe it as the active Yocto default.

## Source Ownership

- `arm-zena-css/`: Arm reference BSP, design documentation, firmware, and FVP
  behavior.
- `sw-ref-stack/`: shared automotive images, demos, tests, and CI fragments.
- `hsoc-stack/components/primary_compute/`: Linux, U-Boot, TF-A, and OP-TEE.
- `hsoc-stack/components/system_mgmt/`: TF-M, SCP-firmware, and the Zephyr
  workspace.
- `hsoc-stack/components/system_mgmt/zephyrproject/zephyr`: upstream Zephyr.
- `hsoc-stack/components/system_mgmt/zephyrproject/zephyr_hsoc_src`: Apollo
  Safety Island CL1 sources.
- `hsoc-stack/yocto/meta-hsoc-auto-solutions/`: Apollo distro, image, template,
  and dynamic-layer policy.
- `hsoc-stack/yocto/meta-hsoc-bsp/`: Apollo BSP, firmware, kernel, signing, and
  secure-world metadata.
- `hsoc-stack/tools/qbox/`: reusable QBox core.
- `hsoc-stack/tools/qbox-platform/`: Apollo/RD-Aspen QBox overlay.
- `hsoc-stack/tools/qemu/`: QBox-local QEMU/libqemu source.
- `hsoc-stack/tools/buildroot/`: local initramfs/rootfs Buildroot source.
- `layers/`: pinned external Yocto layers; avoid direct edits unless requested.
- `build/`: generated evidence except for the active `build/conf/` inputs.

Read `references/project-map.md` when a task crosses more than one source zone.

## Specialist Routing

When the spawn surface supports it, pass the selected name below as the exact
`agent_type`. A task label or prompt mention alone does not activate the
registered TOML model. If `agent_type` is unavailable, execute in the project
leader (`gpt-5.6-sol`, high) and report that no specialist route was selected.

- Fast read-only ownership intake: `arm-auto-solutions-expert`
  (`gpt-5.6-terra`, medium).
- Arm architecture and firmware implementation: `arm-expert`
  (`gpt-5.6-sol`, high).
- Root-cause and boot triage: `debug-expert`
  (`gpt-5.6-sol`, xhigh).
- Linux/kernel/DTS implementation: `linux-kernel-expert` plus
  `$linux-kernel-review` (`gpt-5.6-sol`, high).
- QBox/QEMU/Lua implementation: `qbox_dev` plus `$qbox-dev`
  (`gpt-5.6-sol`, high).
- SystemC/TLM implementation: `systemc_dev` plus `$systemc-dev`
  (`gpt-5.6-sol`, high).
- Bounded test and evidence implementation: `test-expert`
  (`gpt-5.6-terra`, medium).
- Yocto read-only diagnosis/review: `yocto-expert` plus `$yocto-review`
  (`gpt-5.6-sol`, high).
- Yocto metadata implementation: `yocto_dev` plus `$yocto-dev`
  (`gpt-5.6-sol`, high).
- Safety Island CL1 Zephyr: `zephyr-expert` (`gpt-5.6-sol`, high).

## Build And Validation

Use the narrowest useful step first:

```bash
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/audit_qbox_core_boundary.py
./local_build.sh qbox
source layers/poky/oe-init-build-env build
bitbake <recipe> -c compile
bitbake nexios-bsp-initramfs -c rootfs
./yocto_build.sh --bsp
./yocto_build.sh
```

`./yocto_build.sh` builds the standalone BusyBox BSP image before the full
product image. `--bsp` builds only `nexios-bsp-initramfs`. The local flow uses
a separate Buildroot CPIO while reusing `nexios-bsp-init` and the BSP self-test
contract.

Interactive QBox login/BSP launch:

```bash
./run_qbox_local.sh
./run_qbox_yocto.sh
./run_qbox_yocto.sh --bsp
```

These launchers replace only current-UID managed QBox sessions by default;
`--multi-session` preserves existing sessions. They intentionally disable the
shared post-login probe. QBox full-system qualification uses:

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 --timeout 600
```

QBox debug supports `qbox`, `rse`, `si_cl0`, `si_cl1`, `tf-a`, `u-boot`, and
`linux` through `run_qbox_local.sh` or `run_qbox_yocto.sh`. Use
`run_qbox_local_debug.sh` for the multi-domain fixed-port layout. FVP QVP
debug uses `run_fvp.sh --machine apollo-qvp --debug <target>` with
lite-cornea/Iris.

Explicit FVP comparison runtime:

```bash
python3 scripts/run/runfvp_log_boot.py \
  --machine apollo-fvp \
  --fvpconf build/local-apollo-fvp/deploy/apollo-fvp-local.fvpconf \
  --out-dir build/local-apollo-fvp/fvp-boot \
  --timeout 900 --require all --min-runtime 70 --no-login
```

Never infer runtime success from BitBake or CMake success. Report exact files,
commands, logs/artifacts, skipped checks, and remaining fidelity gaps.
