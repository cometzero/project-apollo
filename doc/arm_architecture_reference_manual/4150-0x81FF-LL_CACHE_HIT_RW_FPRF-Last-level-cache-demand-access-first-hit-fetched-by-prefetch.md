# ​0x81FF, LL_CACHE_HIT_RW_FPRF, Last level cache demand access first hit, fetched by prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81FF--LL-CACHE-HIT-RW-FPRF--Last-level-cache-demand-access-first-hit--fetched-by-prefetch>

##### `0x81FF`, LL\_CACHE\_HIT\_RW\_FPRF, Last level cache demand access first hit, fetched by prefetch

The counter counts each demand access first hit counted by [LL\_CACHE\_HIT\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81CF--LL-CACHE-HIT-RW--Last-level-cache-demand-access-hit?lang=en#event_ll_cache_hit_rw) where the cache line was fetched in response to a prefetch instruction or by a hardware prefetcher.

That is, the [LL\_CACHE\_REFILL\_PRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x828F--LL-CACHE-REFILL-PRF--Last-level-cache-refill--prefetch-hit?lang=en#event_ll_cache_refill_prf) event was generated when the cache line was fetched into the cache.

Only the first hit by a demand access is counted. After this event is generated for a cache line, the event is not generated again for the same cache line while it remains in the cache.
