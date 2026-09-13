---
name: qbox-dev
description: Integrate Apollo QBox components, Lua wiring and libqemu; debug provider builds or platform runtime.
---

# Apollo QBox

Own reusable components in `hsoc-stack/tools/qbox`, platform wiring in
`hsoc-stack/tools/qbox-platform`, and QEMU devices in `hsoc-stack/tools/qemu`.
Archived `patch-qbox/` files are not automatically applied.

Preserve C++14, CCI/Lua contracts, socket direction, QemuInstance ownership,
address decode, reset and IRQ behavior. Use actual SystemC/TLM or libqemu
behavior, and document remaining fidelity limits.

For the relevant operation, consult [workflows](references/qbox-workflows.md).
Compile narrowly with `./yocto_build.sh qbox-apollo-qvp-native -c compile`.
Run affected recipe `do_check` suites and guest traffic for driver-visible changes.
The root launcher disables post-login probing even in headless mode; its login
PASS is not full qualification.

Timer changes must retain CPU generic timers as per-core QEMU PPIs.
AP REFCLK uses the Arm MMIO generic timer at 125 MHz: non-secure frame 0 SPI 49,
secure frame 1 SPI 48, never a Hexagon/qct-qtimer alias.
SI0/CSS/RSE counter windows use host_gtimer control/read/sync behavior, not inert RAM.
