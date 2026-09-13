# Functional retention mode (FUNC_RET)

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Cluster-power-modes/Functional-retention-mode--FUNC-RET->

### Functional retention mode (FUNC\_RET)

Functional retention mode allows the L3 cache and snoop filter RAMs to be placed in a retention state if the L3 cache RAMs have not been accessed for a configurable period of time. In this mode, the contents of the L3 cache RAMs are retained, while the rest of the DynamIQ™ cluster shared logic remains powered up and operational.

The time period before the RAMs enter retention can be configured using the FUNC\_RET field of the IMP\_CLUSTERPWRCTLR\_EL1 register, see [IMP\_CLUSTERPWRCTLR\_EL1, Cluster Power Control Register](/documentation/107721/0001/AArch64-registers/AArch64-generic-system-control-registers-summary/IMP-CLUSTERPWRCTLR-EL1--Cluster-Power-Control-Register?lang=en "This register controls power features of the cluster.").

The Power Policy Units (PPUs) can be programmed to automatically control entry and exit from this mode without software intervention, see [Power and reset control with Power Policy Units](/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units?lang=en "This chapter describes how to control the power mode and reset behavior for the DSU-120AE DynamIQ cluster, cores, and complexes using the Power Policy Units (PPUs).").

The length of time before the L3 cache RAMs enter this mode can be configured. Therefore, retention technologies that take multiple cycles to enter or exit retention can be used without significantly degrading performance.

This mode can be entered independently of the current core power modes and is transparent to software. When a core makes an access to the L3 cache, or the system sends a snoop, then the cluster requests to the cluster Power Policy Unit (PPU) that it moves from FUNC\_RET mode to an ON mode to service the access.
