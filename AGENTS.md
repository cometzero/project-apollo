# AGENTS.md

This workspace is a kas-composed Arm Auto Solutions tree and a QBox
co-simulation development workspace. The top-level directory is not a single
Git repository; source ownership is in nested repositories.

## Project Mission

Implement the Arm Zena CSS RD-Aspen FVP behavior in QBox with SystemC/TLM/QEMU
so the QBox virtual platform is functionally equivalent to Arm FVP for the
active `fvp-rd-aspen` configuration. The target is high-fidelity emulation, not
driver-only shims: prefer real SystemC/TLM or libqemu-backed hardware models
over register-only stubs.

## Active Baseline

- Active generated kas config: `.config.yaml`
- Current machine: `fvp-rd-aspen`
- Current variant: `RD_ASPEN_VARIANT = "cfg2"`
- Current configured CPU count: `PC_CPUS_COUNT_DEFAULT = "4"`
- QBox platform under active development:
  `tools/qbox/platforms/fvp-rd-aspen/`
- QBox helper scripts:
  `scripts/build_qbox_fvp_rd_aspen_linux.sh`,
  `scripts/validate_qbox_fvp_rd_aspen_map.py`,
  `scripts/run_qbox_fvp_rd_aspen_linux.py`,
  `scripts/audit_qbox_fvp_rd_aspen_coverage.py`

## Source Boundaries

- `arm-zena-css/`: Arm Zena CSS BSP, RD-Aspen FVP docs, firmware, Safety
  Island, and kas fragments.
- `sw-ref-stack/`: Arm Automotive Solutions images, demos, test automation,
  and CI fragments.
- `layers/`: pinned upstream/downstream Yocto layers. Treat as external unless
  explicitly asked to patch them.
- `tools/qbox/`: QBox SystemC/TLM/QEMU platform implementation.
- `tools/qemu/`: local QEMU/libqemu source used by QBox.
- `build/`: generated evidence only. Do not treat as source.
- `doc/`: project analysis, implementation plans, and verification reports.
- `.codex/`: project-local Codex skills and sub-agent definitions.

## Required Working Style

1. Inspect before editing. Read `.config.yaml` before any build/runtime claim.
2. Use project-local skills when relevant:
   - `$arm-auto-solutions` for workspace routing and evidence standards.
   - `$qbox-dev` for QBox/SystemC/QEMU virtual platform work.
   - `$systemc-dev` for SystemC/TLM component implementation or review.
   - `$yocto-dev` / `$yocto-review` for Yocto metadata work.
   - `$linux-kernel-review` for kernel, DTS, Kconfig, driver, HIPC, RPMsg,
     remoteproc, or PFDI Linux work.
3. Keep changes scoped to the owning repository or project-local docs.
4. Preserve user changes. Do not reset nested repos or generated state unless
   explicitly requested.
5. Prefer log and artifact based validation over tmux-only screen output.

## FVP-To-QBox Implementation Rules

For each hardware block or IP:

1. Inventory the FVP-visible behavior from local RD-Aspen sources first:
   `arm-zena-css/documentation/`, machine config, FVP include files, generated
   DTB/DTS, firmware logs, and existing FVP boot logs.
2. Check official Arm documentation and TRMs for programming model, reset
   values, interrupts, register layout, timing assumptions, and integration
   constraints. Record document version and URL in the implementation notes.
3. Search for existing open-source SystemC/TLM models before writing a new
   model. Prefer permissive, upstream-friendly code and respect licenses.
4. Prefer real SystemC/TLM behavior or libqemu-backed models over stubs.
   Register-only stubs are temporary compatibility debt and must be documented
   with missing behavior and a replacement plan.
5. Preserve QBox conventions: C++14, SystemC/TLM-2.0, CCI parameters, Lua
   platform configuration, CMake target style, TLM socket direction, QEMU
   `QemuInstance` usage, and log-based test evidence.
6. Keep FVP/QBox memory maps, IRQ lines, device tree expectations, boot
   artifacts, and Linux driver evidence aligned.

## Validation Ladder

Use the narrowest meaningful command first, then broaden only when needed.

1. Static checks:
   - `python3 -m py_compile scripts/*.py` for changed Python helpers.
   - `git -C tools/qbox diff --check` for QBox changes.
   - `./scripts/validate_qbox_fvp_rd_aspen_map.py`
2. QBox build checks:
   - Build targeted modules first with `cmake --build tools/qbox/build --target
     <target> --parallel <n>`.
   - Build `platforms-vp` when Lua platform wiring changes.
3. Runtime checks:
   - Use `scripts/run_qbox_fvp_rd_aspen_linux.py` with file-backed output.
   - Use `--post-login-probe` when driver evidence matters.
4. Coverage checks:
   - Run `scripts/audit_qbox_fvp_rd_aspen_coverage.py` with the runtime
     `result.json` and log path.
5. FVP comparison:
   - Use non-interactive FVP log scripts and compare boot, memory-map, IRQ,
     device-tree, driver probe, and service evidence.

## Documentation Requirements

When adding or replacing a hardware model, update project-local evidence:

- `doc/qbox-fvp-emulation-project.md` for roadmap/status changes.
- `tools/qbox/platforms/fvp-rd-aspen/README.md` for platform-specific runtime
  instructions.
- `build/qbox-fvp-rd-aspen/` only for generated verification reports.

Final reports must include files changed, commands run, static/build/runtime
validation, and explicit blockers or fidelity gaps.
