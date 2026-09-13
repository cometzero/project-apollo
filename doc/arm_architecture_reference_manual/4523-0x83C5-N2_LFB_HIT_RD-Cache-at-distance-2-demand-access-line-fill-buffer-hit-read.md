# ​0x83C5, N2_LFB_HIT_RD, Cache at distance 2 demand access line-fill buffer hit, read

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x83C5--N2-LFB-HIT-RD--Cache-at-distance-2-demand-access-line-fill-buffer-hit--read>

##### `0x83C5`, N2\_LFB\_HIT\_RD, Cache at distance 2 demand access line-fill buffer hit, read

The counter counts each demand read counted by [N2\_CACHE\_HIT\_RD](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x83A1--N2-CACHE-HIT-RD--Cache-at-distance-2--demand-access-hit--read?lang=en#event_n2_cache_hit_rd) that hits a recently fetched line in a cache at distance 2.

That is, the read hits a cache line that is in the process of being loaded into the cache at distance 2, and so does not generate a new refill, but has to wait for the previous refill to complete.
