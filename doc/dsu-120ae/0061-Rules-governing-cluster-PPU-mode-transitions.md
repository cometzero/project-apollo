# Rules governing cluster PPU mode transitions

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Cluster-PPU-mode-transitions/Rules-governing-cluster-PPU-mode-transitions>

### Rules governing cluster PPU mode transitions

For the cluster Power Policy Unit (PPU) mode transitions, there is a set of rules that governs the transitions between each PPU mode. There is no requirement for the System Control Processor (SCP) to explicitly consider these constraints when programming the cluster PPU.

The following rules govern all transitions between cluster PPU modes:

- When transitioning from OFF to ON, any supported operating mode can be targeted.
- Transitions between operating modes only happen in the ON power mode.
- Active slice changes do not happen at the same time as active RAM changes.
- Switching between SFONLY and FULL ON traverses HALF ON.
- The operating mode is maintained when moving from ON to FUNC\_RET, FULL\_RET, or MEM\_RET power modes.

> ### Note
>
> For more information, see
> [Arm® Power Policy Unit Architecture Specification](https://developer.arm.com/documentation/den0051/latest).
