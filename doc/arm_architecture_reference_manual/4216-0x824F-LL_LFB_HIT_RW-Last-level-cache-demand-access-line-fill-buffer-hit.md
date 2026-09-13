# ​0x824F, LL_LFB_HIT_RW, Last level cache demand access line-fill buffer hit

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x824F--LL-LFB-HIT-RW--Last-level-cache-demand-access-line-fill-buffer-hit>

##### `0x824F`, LL\_LFB\_HIT\_RW, Last level cache demand access line-fill buffer hit

The counter counts each demand access counted by [LL\_CACHE\_HIT\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81CF--LL-CACHE-HIT-RW--Last-level-cache-demand-access-hit?lang=en#event_ll_cache_hit_rw) that hits a recently fetched line in the Last level cache.

That is, the access hits a cache line that is in the process of being loaded into the Last level cache, and so does not generate a new refill, but has to wait for the previous refill to complete.
