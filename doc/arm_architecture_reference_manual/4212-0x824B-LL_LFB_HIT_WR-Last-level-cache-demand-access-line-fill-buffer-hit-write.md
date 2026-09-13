# ​0x824B, LL_LFB_HIT_WR, Last level cache demand access line-fill buffer hit, write

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x824B--LL-LFB-HIT-WR--Last-level-cache-demand-access-line-fill-buffer-hit--write>

##### `0x824B`, LL\_LFB\_HIT\_WR, Last level cache demand access line-fill buffer hit, write

The counter counts each demand access counted by [LL\_CACHE\_HIT\_WR](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81CB--LL-CACHE-HIT-WR--Last-level-cache-demand-access-hit--write?lang=en#event_ll_cache_hit_wr) that hits a recently fetched line in the Last level cache.

That is, the access hits a cache line that is in the process of being loaded into the Last level cache, and so does not generate a new refill, but has to wait for the previous refill to complete.
