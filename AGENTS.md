# Apollo workspace

Implement Arm Zena CSS RD-Aspen/Apollo behavior in QBox with SystemC/TLM/QEMU.
Prefer functional hardware models over driver-only shims; distinguish functional
compatibility from physical, timing or FVP parity.

## Ownership

The root repository pins nested Git repositories. Edit and commit at the owning
repository boundary; preserve unrelated changes.

- `arm-zena-css/`: externally managed, read-only reference; never commit here.
- `layers/`: external Yocto layers; patch only when explicitly in scope.
- `hsoc-stack/components/primary_compute/`: Linux, U-Boot, TF-A, OP-TEE.
- `hsoc-stack/components/system_mgmt/`: TF-M, SCP, Zephyr and `zephyr_hsoc_src`.
- `hsoc-stack/yocto/meta-hsoc-{bsp,auto-solutions}/`: owned BSP/product metadata.
- `hsoc-stack/tools/qbox/`: reusable QBox core.
- `hsoc-stack/tools/qbox-platform/`: Apollo overlay and platform models.
- `hsoc-stack/tools/qemu/`: active QEMU/libqemu source.
- `scripts/`, `tests/`, `doc/`: root tooling, tests and implementation evidence.
- `build/conf/`: local build inputs; other `build/` content is generated.
- Buildroot is retained source, not the supported root build workflow.
- `qbox-platform/patch-qbox/` holds archived candidates; normal builds must not
  automatically apply them to the checked-out QBox source.

## Build and runtime

`./yocto_build.sh` builds `nexios-image`; `--bsp` builds
`nexios-bsp-initramfs`. Confirm the requested machine and effective
`build/conf/{local.conf,bblayers.conf,templateconf.cfg}` for build/runtime work;
do not infer current configuration from this document. Serialize shared BitBake
builds and avoid changing their inputs while a build is running.

`./run_qbox_yocto.sh [--bsp]` is a boot/login launcher. It disables the shared
post-login probe, including headless use; use the canonical Python runner for
full post-login qualification. Launchers replace only current-UID managed QBox
sessions/processes; `--multi-session` preserves existing sessions.

Use matching machine artifacts for FVP comparison. For boot failures, identify
the earliest failing domain from logs before GDB/Iris escalation.

## Context and evidence

Consult relevant sections of `doc/arm_zena_css_dev_guide/` for hardware maps,
interrupts and firmware handoffs. Task-specific procedures live in
`.codex/skills/`; load only relevant references, not a fixed document bundle.

Prefer ready codebase-memory indexes for relationship discovery. Verify coverage
before exhaustive claims; use direct source inspection when incomplete.
`scripts/update_codebase_indexes.sh --list` is the canonical mapping. Explicit
refreshes run sequentially; never refresh large Linux indexes alongside builds
or another memory-intensive index. Routine refreshes do not delete projects.

Use focused checks first. Hardware behavior changes need active traffic/IRQ or
driver evidence, not just compilation. Keep generated QVP evidence under
`build/qbox-apollo-qvp/`; retain explicit FAIL/SKIP/UNSUPPORTED and fidelity gaps.
For model changes update the relevant platform README and
`doc/qbox-fvp-emulation-project.md` when their documented behavior/status changes.
