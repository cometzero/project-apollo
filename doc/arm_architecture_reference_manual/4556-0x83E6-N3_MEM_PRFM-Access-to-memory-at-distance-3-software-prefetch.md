# ​0x83E6, N3_MEM_PRFM, Access to memory at distance 3, software prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x83E6--N3-MEM-PRFM--Access-to-memory-at-distance-3--software-prefetch>

##### `0x83E6`, N3\_MEM\_PRFM, Access to memory at distance 3, software prefetch

The counter counts each software prefetch to memory at distance 3.

The memory distance indicates the relative distance that the return data has traveled. The distance is a relative distance that is defined at the system level, allowing flexibility of use for different systems that may have differing levels of hierarchy.

Distance 3 represents a further distance of travel than distance 2.

The interpretation of distance is IMPLEMENTATION DEFINED, and should be the same for all PEs in the base system, and the same for both cache and memory distances.
