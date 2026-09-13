# Cluster full retention mode (FULL_RET)

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Cluster-power-modes/Cluster-full-retention-mode--FULL-RET->

### Cluster full retention mode (FULL\_RET)

Full retention mode (FULL\_RET) allows the L3 cache and snoop filter RAMs to be placed in retention state and the cache slice logic is powered down, if the L3 cache RAMs have not been accessed for a configurable period of time. In this mode, the contents of the L3 cache RAMs are retained and the slice logic is powered down, while the rest of the DynamIQ™ cluster shared logic remains powered up and operational.

The time period before the RAMs enter retention can be configured using the FULL\_RET field of the CLUSTERPWRCTLR register.

The Power Policy Units (PPUs) can be programmed to automatically control entry and exit from this mode without software intervention, see [Power and reset control with Power Policy Units](/documentation/107721/0001/Power-and-reset-control-with-Power-Policy-Units?lang=en "This chapter describes how to control the power mode and reset behavior for the DSU-120AE DynamIQ cluster, cores, and complexes using the Power Policy Units (PPUs).").

The length of time before the L3 cache RAMs enter this mode can be configured. Therefore, retention technologies that take multiple cycles to enter or exit retention can be used without significantly degrading performance.

This mode can be entered independently of the current core power modes and is transparent to software. When a core makes an access to the L3 cache, or the system sends a snoop, then the cluster requests to the cluster Power Policy Unit (PPU) that it moves from FULL\_RET mode to an ON mode to service the access.

Similar to functional retention mode (FUNC\_RET), in this mode the contents of the L3 cache RAMs are retained, whilst much of the cluster logic is powered up. However, in FULL\_RET mode additional power is saved because the cache slice logic is powered down.
