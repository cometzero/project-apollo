# ​0x83CE, N3_LFB1_HIT_RD, Cache type 1 at distance 3 demand access line-fill buffer hit, read

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x83CE--N3-LFB1-HIT-RD--Cache-type-1-at-distance-3-demand-access-line-fill-buffer-hit--read>

##### `0x83CE`, N3\_LFB1\_HIT\_RD, Cache type 1 at distance 3 demand access line-fill buffer hit, read

The counter counts each demand read counted by [N3\_LFB\_HIT\_RD](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x83C6--N3-LFB-HIT-RD--Cache-at-distance-3-demand-access-line-fill-buffer-hit--read?lang=en#event_n3_lfb_hit_rd) that hits a recently fetched line in a first cache type at distance 3.

That is, the read hits a cache line that is in the process of being loaded into the cache at distance 3, and so does not generate a new refill, but has to wait for the previous refill to complete.

The definition of cache types in the system is IMPLEMENTATION DEFINED, but must be similar for all devices in the system.
