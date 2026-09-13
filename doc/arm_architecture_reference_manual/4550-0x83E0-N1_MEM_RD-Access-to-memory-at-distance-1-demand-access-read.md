# ​0x83E0, N1_MEM_RD, Access to memory at distance 1, demand access, read

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x83E0--N1-MEM-RD--Access-to-memory-at-distance-1--demand-access--read>

##### `0x83E0`, N1\_MEM\_RD, Access to memory at distance 1, demand access, read

The counter counts each demand read to memory at distance 1.

The memory distance indicates the relative distance that the return data has traveled. The distance is a relative distance that is defined at the system level, allowing flexibility of use for different systems that may have differing levels of hierarchy.

The interpretation of distance is IMPLEMENTATION DEFINED, and should be the same for all PEs in the base system, and the same for both cache and memory distances.
