# ​0x8429, ISNP_HIT_N2, Snoop hit in cache at distance 2, instruction access

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8429--ISNP-HIT-N2--Snoop-hit-in-cache-at-distance-2--instruction-access>

##### `0x8429`, ISNP\_HIT\_N2, Snoop hit in cache at distance 2, instruction access

The counter counts each snoop counted by [ISNP\_HIT](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81B0--ISNP-HIT--Snoop-hit--instruction?lang=en#event_isnp_hit) that hits in a cache at distance 2.

The event is counted by the PE generating the snoop, not the PE being snooped.

The cache distance indicates the relative distance that the return data has traveled. The distance is a relative distance that is defined at the system level, allowing flexibility of use for different systems that may have differing levels of hierarchy.

The interpretation of distance is IMPLEMENTATION DEFINED, and should be the same for all PEs in the base system, and the same for both cache and memory distances.
