# QBox Focused Workflows

## Component Intake

Identify the component owner before editing:

- reusable component or QEMU wrapper: `hsoc-stack/tools/qbox`
- Apollo-specific component or glue: `hsoc-stack/tools/qbox-platform`
- QEMU device/model implementation: `hsoc-stack/tools/qemu`

Trace construction from Lua `moduletype` through the C++ registration target,
CCI parameters, sockets, bindings, memory map, IRQs, and runtime log name.

## SystemC And TLM

Check:

- process kind, sensitivity, reset, event ordering, and delta-cycle behavior
- `sc_time` annotation and synchronization with QEMU
- initiator/target socket direction and binding cardinality
- address range, alignment, overlap, decode translation, and response status
- payload and extension lifetime, byte enables, streaming width, DMI, and
  `transport_dbg`

Use focused component tests and the smallest build target. A test must observe
behavior, not only object construction.

## Lua Platform

For every object verify:

- exact `moduletype` and loaded library
- stable object name and CCI path
- address, size, bind target, socket name, and IRQ line
- referenced QEMU instance and CPU ownership
- UART backend direction and interactive/noninteractive behavior
- artifact paths passed by the runner

Run `python3 scripts/test/validate_qbox_apollo_fvp_full_map.py` after map or
binding changes.

## QEMU Integration

Prefer existing `QemuInstanceManager`, `QemuInstance`, and qemu-component
patterns. Verify target architecture, machine/device type, CPU model, reset
vector, GIC/IRQ wiring, RAM ownership, clock/timer ownership, and character
backend setup. Keep new QEMU-side implementation minimal when a QBox/SystemC
model can own the integration behavior cleanly.

Build and test libqemu artifacts through the project QBox build contract. Do
not replace or delete generated sysroots to force discovery.

## Build Ladder

```bash
cmake --build build/local-${MACHINE}/work/qbox-platform \
  --target <target> --parallel <jobs>
ctest --test-dir build/local-${MACHINE}/work/qbox-platform \
  -R <test-name> --output-on-failure
./local_build.sh qbox
```

Use the concrete configured machine in a shell command if `${MACHINE}` is not
exported.

## Runtime Ladder

1. Run static map and boundary checks.
2. Run the narrow component test.
3. Run Primary Compute direct boot when the change is AP-only.
4. Run the full Apollo system for cross-domain changes.
5. Audit full-system coverage from the generated `result.json`.

```bash
python3 scripts/run/run_qbox_apollo_fvp_linux.py --timeout 600
python3 scripts/run/run_qbox_apollo_fvp_full.py \
  --si-mode live-cl0-cl1 --timeout 600
python3 scripts/test/audit_qbox_apollo_fvp_full_coverage.py \
  --result-json <runtime-result.json> \
  --output build/qbox-apollo-qvp/full-coverage-audit.json
```

Use the lower-level RSE runner only for focused RSE compatibility evidence.

## Evidence

Record the exact binary, Lua config, images, command, timeout, result JSON,
per-domain logs, and the earliest failure. A running process, open tmux pane,
or CMake success is not boot proof.
