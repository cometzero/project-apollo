---
name: qbox-dev
description: Use for qbox, Qualcomm/QUIC QBox, SystemC, TLM-2.0, QEMU co-simulation, virtual platform development, Lua platform configuration, QemuInstance, QemuInstanceManager, CCI parameters, qbox monitor, UART/character backends, biflow_socket, backend_socket, target_socket, initiator_socket, memory map, IRQ wiring, Graphviz/DOT object graph generation, CMake presets, build/test debugging, and qbox SystemC/QEMU integration tasks. Trigger when the user asks to implement, debug, review, refactor, test, analyze, diagram, document, or inspect qbox/SystemC/QEMU virtual platform code or configuration.
---

# QBox Development Skill

## Purpose

Use this skill for QBox development tasks involving:

- QBox / qbox virtual platform development
- SystemC / TLM-2.0 modeling
- QEMU co-simulation through `libqbox` and `libqemu-cxx`
- qbox `systemc-components`, `qemu-components`, `platforms`, tests, and docs
- Lua platform configuration, CCI parameters, and QEMU instance setup
- CPU, memory, interrupt-controller, UART, backend, and monitor wiring
- Runtime object inspection and Graphviz/DOT/Mermaid architecture diagrams
- CMake preset build, test, runtime, and boot debugging workflows

For detailed checklists and patterns, read
`references/qbox-workflows.md` only when the task needs the extra detail.

## Core Behavior

1. Inspect before editing.
2. Do not guess qbox APIs. Search source, examples, docs, tests, and Lua
   platform files first.
3. Preserve SystemC timing, TLM socket direction, CCI parameter behavior,
   QEMU argument conventions, synchronization policy, and Lua object names
   unless the task requires a deliberate change.
4. Prefer small, focused edits and narrow build/test/simulation commands.
5. For diagrams, distinguish parsed relationships from inferred
   relationships.
6. Report files inspected, files changed, commands run, results, and
   remaining risks.

## First Inspection

Start with lightweight inspection:

```bash
pwd
git status --short
find . -maxdepth 3 -name 'README.md' -o -name 'CMakePresets.json' -o -name 'CMakeLists.txt'
find . -maxdepth 3 -type d | sort | sed -n '1,160p'
find . -maxdepth 4 -name '*.lua' | sort | sed -n '1,160p'
```

Search relevant qbox patterns:

```bash
rg -n "QemuInstanceManager|QemuInstance|moduletype|dylib_path|backend_socket|biflow_socket|target_socket|initiator_socket" README.md docs examples platforms tests libqbox libqemu-cxx systemc-components qemu-components 2>/dev/null
rg -n "SC_MODULE|SC_CTOR|SC_HAS_PROCESS|SC_THREAD|SC_METHOD|sc_module|sc_time|tlm::|tlm_utils" . 2>/dev/null
rg -n "monitor|server_port|qk_status|transport_dbg|char_backend|stdio|socket|sigquit|expect" README.md docs examples platforms tests systemc-components qemu-components libqbox 2>/dev/null
```

## Build and Test

Prefer project presets when available:

```bash
cmake --list-presets
cmake --preset gcc
cmake --build --preset gcc --parallel
ctest --preset gcc --output-on-failure
```

For focused checks:

```bash
cmake --build --preset <preset> --target <target>
ctest --preset <preset> -R <test-name> --output-on-failure
```

Use fallback `cmake -B build ...` only after checking project docs and
available presets. Do not delete build artifacts or perform broad rebuilds
without a reason.

## QBox Platform Checks

When inspecting or modifying a platform, identify:

- Platform entry file and Lua configuration files
- `QemuInstanceManager`, `QemuInstance`, QEMU target, CPU models, and QEMU args
- Router/address decoder, memory map, memories, ROM/RAM, and loaders
- Interrupt controller, IRQ lines, timer devices, UARTs, and backends
- Monitor server/endpoints, CCI parameters, and TLM socket bindings

For Lua platform files, validate:

- Unique object names
- Existing `moduletype` and `dylib_path`
- Valid constructor `args`
- Valid `qemu_inst` references
- Correct target/initiator/backend/biflow socket binding
- Non-overlapping address/size regions
- Correct IRQ line mapping and device tree consistency when Linux boots
- QEMU args, GDB ports, monitor ports, and host socket conflicts

Read `references/qbox-workflows.md` for detailed Lua, memory map, IRQ,
UART/backend, monitor, graph, boot, and runtime debugging workflows.

## SystemC/TLM and QEMU Rules

- Preserve initiator/target socket direction and TLM response status.
- Preserve address decoding, timing annotation, delta-cycle behavior,
  `sc_time`, and intentional `sc_stop` behavior.
- Avoid unsafe payload, extension, event, or dynamic module lifetimes.
- Do not introduce host wall-clock timing where simulation time is required.
- Do not change QEMU execution mode, `icount`, TCG threading, GDB ports, or
  networking without explaining determinism/performance implications.
- Handle `qemu_args` and CCI parameters according to existing repository
  conventions.

## Diagrams and Object Graphs

For qbox platform diagrams:

- Prefer runtime qbox monitor hierarchy when available.
- Otherwise parse Lua configuration, then C++ construction code, then logs.
- Output Graphviz DOT first; Mermaid is optional.
- Label inferred edges explicitly.
- If runtime monitor data is unavailable, state that the analysis is static.

## Output Format

Return:

- Summary
- Detected qbox context
- Files inspected
- Files changed
- Commands run
- Build/test/simulation result
- Root cause, if debugging
- Generated artifacts, if any
- Remaining risks
- Next recommended command
