# Emulated memory retention mode (MEM_RET_EMU)

Source: <https://developer.arm.com/documentation/107721/0001/Power-management/Cluster-power-modes/Emulated-memory-retention-mode--MEM-RET-EMU->

### Emulated memory retention mode (MEM\_RET\_EMU)

In Emulated memory retention mode, the cluster behaves logically if it were in the Memory retention mode (MEM\_RET) except that the DynamIQ™ cluster shared logic remains powered. This means the L3 cache RAMs are in retention but the snoop filter RAMs and the rest of the DynamIQ Shared Unit-120AE (DSU-120AE) logic remains powered. Therefore, debug accesses to the cluster can be made.
