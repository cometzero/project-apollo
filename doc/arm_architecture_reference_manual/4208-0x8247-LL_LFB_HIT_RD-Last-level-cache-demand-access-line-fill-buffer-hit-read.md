# ​0x8247, LL_LFB_HIT_RD, Last level cache demand access line-fill buffer hit, read

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8247--LL-LFB-HIT-RD--Last-level-cache-demand-access-line-fill-buffer-hit--read>

##### `0x8247`, LL\_LFB\_HIT\_RD, Last level cache demand access line-fill buffer hit, read

The counter counts each demand access counted by [LL\_CACHE\_HIT\_RD](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81C7--LL-CACHE-HIT-RD--Last-level-cache-demand-access-hit--read?lang=en#event_ll_cache_hit_rd) that hits a recently fetched line in the Last level cache.

That is, the access hits a cache line that is in the process of being loaded into the Last level cache, and so does not generate a new refill, but has to wait for the previous refill to complete.
