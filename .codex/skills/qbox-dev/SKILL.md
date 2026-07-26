---
name: qbox-dev
description: QBox/SystemC/QEMU co-simulation workflow for Apollo. Use for QBox C++ components, QEMU/libqemu integration, Lua platforms, CCI parameters, TLM sockets, memory maps, IRQs, UART backends, monitor/debugging, build/test failures, runtime boot, or FVP-equivalence analysis.
---

# QBox Development

## Ownership

- reusable QBox core: `hsoc-stack/tools/qbox`
- Apollo/RD-Aspen overlay: `hsoc-stack/tools/qbox-platform`
- Apollo platform entrypoints: `hsoc-stack/tools/qbox-platform/platforms/apollo`
- local QEMU/libqemu: `hsoc-stack/tools/qemu`
- local build tree: `build/local-${MACHINE}/work/qbox-platform`
- QVP full-system evidence: `build/qbox-apollo-qvp`
- explicit FVP-comparison evidence: `build/qbox-apollo-fvp`

Archived candidates in `hsoc-stack/tools/qbox-platform/patch-qbox` are not
applied by normal builds. Change the owning repository directly unless the user
explicitly requests an archived patch.

Read `build/conf/local.conf`, `build/conf/bblayers.conf`,
`build/conf/templateconf.cfg`, relevant QBox READMEs, CMake files, Lua
entrypoints, and existing tests before editing. Delegate deep implementation
with `agent_type = "qbox_dev"` (`gpt-5.6-sol`, high); use
`agent_type = "systemc_dev"` (`gpt-5.6-sol`, high) for reusable
timing/component work. If `agent_type` is unavailable, use the project leader
and do not claim specialist selection.

## Fidelity Rules

- Prefer a real SystemC/TLM or libqemu-backed model over a register-only stub.
- Preserve C++14, QBox component patterns, CCI keys, Lua names, socket
  direction, address decode, IRQ topology, reset, simulation time, and QEMU
  ownership.
- Keep CPU-internal generic timers in QEMU CPU models. Model AP REFCLK through
  the Arm MMIO generic timer path and preserve secure/non-secure frame IRQs.
- Compare memory maps, interrupts, DT expectations, firmware handoffs, and
  driver probe evidence with the reference platform.
- Record temporary fidelity debt and a replacement plan.

## Inspection

```bash
git -C hsoc-stack/tools/qbox status --short --branch
git -C hsoc-stack/tools/qbox-platform status --short --branch
git -C hsoc-stack/tools/qemu status --short --branch
rg -n "QemuInstance|moduletype|dylib_path|target_socket|initiator_socket|backend_socket|biflow_socket" \
  hsoc-stack/tools/qbox hsoc-stack/tools/qbox-platform
rg -n "SC_MODULE|SC_THREAD|SC_METHOD|b_transport|sc_time" \
  hsoc-stack/tools/qbox hsoc-stack/tools/qbox-platform
```

Read `references/qbox-workflows.md` for focused component, Lua, QEMU, and
runtime checklists.

## Build And Static Validation

Use the project entrypoint first:

```bash
./local_build.sh qbox
```

For a narrow overlay target:

```bash
cmake --build build/local-${MACHINE}/work/qbox-platform \
  --target <target> --parallel <jobs>
ctest --test-dir build/local-${MACHINE}/work/qbox-platform \
  -R <test-name> --output-on-failure
```

Run applicable map and ownership checks:

```bash
git -C hsoc-stack/tools/qbox diff --check
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
python3 scripts/test/audit_qbox_core_boundary.py
```

## Runtime

Interactive boot/login launchers:

```bash
./run_qbox_local.sh
./run_qbox_yocto.sh
./run_qbox_yocto.sh --bsp
```

They use `live-cl0-cl1`, disable the shared post-login probe, and replace only
current-UID managed QBox sessions unless `--multi-session` is set. Do not use
their tmux/login marker alone as a full qualification claim.

```bash
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 --timeout 600
```

Inspect the generated `result.json`, per-domain UART logs, and coverage audit.
For timing/error regression, create the first JSON baseline with
`./run_qbox_boot_regression.sh --record-baseline`, then use
`./run_qbox_boot_regression.sh` for comparisons. QBox GDB targets are `qbox`,
`rse`, `si_cl0`, `si_cl1`, `tf-a`, `u-boot`, and `linux`; Yocto debug is
interactive and cannot be combined with `--headless`. Do not use tmux screen
contents alone as proof. Report files changed, owning repositories, commands,
build/runtime results, and unresolved fidelity gaps.
