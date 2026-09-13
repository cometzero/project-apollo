# ​0x83A4, N1_CACHE_HIT_PRFM, Cache at distance 1, software prefetch hit

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x83A4--N1-CACHE-HIT-PRFM--Cache-at-distance-1--software-prefetch-hit>

##### `0x83A4`, N1\_CACHE\_HIT\_PRFM, Cache at distance 1, software prefetch hit

The counter counts each cache hit at distance 1 due to a software prefetch.

The cache distance indicates the relative distance that the return data has traveled. The distance is a relative distance that is defined at the system level, allowing flexibility of use for different systems that may have differing levels of hierarchy.

The interpretation of distance is IMPLEMENTATION DEFINED, and should be the same for all PEs in the base system, and the same for both cache and memory distances.
