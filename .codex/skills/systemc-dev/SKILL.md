---
name: systemc-dev
description: SystemC and TLM-2.0 development workflow for C++ hardware modeling. Use whenever a prompt mentions SystemC, TLM-2.0, sc_main, sc_module, SC_MODULE, SC_CTOR, SC_THREAD, SC_METHOD, SC_CTHREAD, sc_signal, sc_fifo, sc_event, sc_clock, reset behavior, delta cycles, sc_time, sc_stop, initiator/target sockets, b_transport, nb_transport, DMI, payload lifetime, hardware modeling, co-simulation, producer/consumer FIFO examples, or SystemC/TLM 구현/디버깅/리뷰/테스트.
---

# SystemC Development Skill

## Workflow

1. Inspect the repository before editing.
   - Find the build system: `CMakeLists.txt`, `Makefile`, `meson.build`,
     Bazel files, or scripts.
   - Find SystemC dependency setup: include paths, libraries, `pkg-config`,
     environment variables, or Dockerfiles.
   - Find entry points: `sc_main`, examples, tests, and simulation binaries.

2. Map the simulation structure.
   - Identify the `sc_module` hierarchy.
   - Identify processes: `SC_METHOD`, `SC_THREAD`, and `SC_CTHREAD`.
   - Identify ports, exports, channels, `sc_signal`, `sc_fifo`, `sc_event`,
     clocks, and resets.
   - For TLM, identify initiator/target sockets, transport interfaces,
     payload ownership, and timing annotation.

3. Before changing code, state the intended minimal edit.
   - Avoid broad rewrites.
   - Keep existing naming, formatting, C++ standard, and build conventions.
   - Prefer small compileable increments.

4. Check implementation safety.
   - Include correct SystemC headers.
   - Avoid unsafe lifetime of payloads, events, references, and dynamically
     allocated modules.
   - Preserve simulation timing and delta-cycle semantics.
   - Use `sc_time` for simulation time; do not substitute wall-clock time.
   - Avoid hidden races from process sensitivity or reset handling.

5. Verify with the narrowest useful command.
   - Build the smallest target first.
   - Run the relevant simulation or test.
   - Capture the command, result, failure output, and next step.
   - If build/test commands are unknown, infer from existing docs/scripts and
     ask only when blocked.

## Typical Commands

```bash
find . -name 'CMakeLists.txt' -o -name 'Makefile' -o -name '*.cpp' -o -name '*.h' | head -100
rg -n "int sc_main|sc_main\\(" .
rg -n "SC_MODULE|SC_CTOR|SC_THREAD|SC_METHOD|SC_CTHREAD|tlm::" src include test tests examples 2>/dev/null
cmake --build build -j
ctest --test-dir build --output-on-failure
```

## Review Focus

- Check process sensitivity, reset handling, and event ordering before
  changing behavior.
- For `SC_THREAD` and `SC_CTHREAD`, confirm blocking waits and reset behavior
  match the intended protocol.
- For `SC_METHOD`, confirm static/dynamic sensitivity and avoid accidental
  blocking calls.
- For `sc_fifo`, confirm bounded depth, blocking/non-blocking access, and
  termination behavior.
- For TLM-2.0, confirm socket binding, `b_transport` timing annotation,
  response status, DMI handling, payload extension lifetime, and ownership.
