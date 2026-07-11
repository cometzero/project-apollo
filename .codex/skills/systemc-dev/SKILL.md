---
name: systemc-dev
description: SystemC and TLM-2.0 development workflow for this Apollo QBox project. Use for sc_module, sc_main, SC_THREAD/SC_METHOD, ports, events, reset, sc_time, delta cycles, TLM sockets, transport, DMI, payload lifetime, hardware models, co-simulation, review, debugging, or tests.
---

# SystemC Development

## Ownership And Intake

- reusable QBox components: `hsoc-stack/tools/qbox`
- Apollo-specific components: `hsoc-stack/tools/qbox-platform/systemc-components`
- active overlay build: `build/local-${MACHINE}/work/qbox-platform`

Read `build/conf/local.conf`, the owning repository README/CMake files, module
header and implementation, construction site, Lua binding, and tests before
editing. Use `$qbox-dev` as well when the change touches QEMU, Lua, CCI, the
platform map, or a full-system runner.

Use `agent_type = "systemc_dev"` (`gpt-5.6-sol`, high) for model
implementation and route QBox/QEMU integration with
`agent_type = "qbox_dev"` (`gpt-5.6-sol`, high). If `agent_type` is
unavailable, use the project leader and do not claim specialist selection.

## Model Checklist

1. Map module hierarchy, ports, exports, channels, events, clocks, and resets.
2. Map every `SC_METHOD`, `SC_THREAD`, and `SC_CTHREAD`, including sensitivity
   and blocking behavior.
3. For TLM, map initiator/target sockets, binding cardinality, address
   translation, payload ownership, extensions, timing, DMI, and debug access.
4. State the minimal behavior change and its observable test before editing.
5. Preserve existing C++14 and QBox conventions.

## Correctness Rules

- Preserve delta-cycle and event ordering; do not replace simulation time with
  wall-clock time.
- `SC_METHOD` must not block. Confirm initialization and dynamic sensitivity.
- `SC_THREAD`/`SC_CTHREAD` waits and reset behavior must match the protocol.
- Annotate `b_transport` delay and set response status on every path.
- Keep payloads, extensions, callbacks, and module references alive for their
  required lifetime.
- Validate DMI invalidation and address ranges when DMI is supported.
- Do not invent APIs or add broad abstractions for one component.

## Validation

Build the smallest owning target first:

```bash
cmake --build build/local-${MACHINE}/work/qbox-platform \
  --target <target> --parallel <jobs>
ctest --test-dir build/local-${MACHINE}/work/qbox-platform \
  -R <test-name> --output-on-failure
```

Then run the project contract when the component is integrated:

```bash
./local_build.sh qbox
python3 scripts/test/validate_qbox_apollo_fvp_full_map.py
```

Runtime claims require the relevant generated logs and result JSON. Report the
changed component, owning repository, command, test observation, timing
assumptions, and any unimplemented protocol behavior.
