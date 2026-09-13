# Emulated off mode (OFF_EMU)

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Cluster-power-modes/Emulated-off-mode--OFF-EMU->

### Emulated off mode (OFF\_EMU)

In the Emulated off mode, the cluster behaves logically as if it were in the Off mode. However, the DynamIQ™ cluster shared logic remains powered including the L3 cache and snoop filter RAMs.

In this mode, the cluster behaves as if it were powered off for functional logic, but it allows the cluster to maintain debug context and access. On entering this mode, a Warm reset is applied to the cluster, resetting the functional logic but not resetting the debug logic. From the perspective of software running on the core, the cluster appears to be powered off.
