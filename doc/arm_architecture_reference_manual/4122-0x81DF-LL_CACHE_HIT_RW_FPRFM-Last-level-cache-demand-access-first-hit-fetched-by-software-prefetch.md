# ​0x81DF, LL_CACHE_HIT_RW_FPRFM, Last level cache demand access first hit, fetched by software prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81DF--LL-CACHE-HIT-RW-FPRFM--Last-level-cache-demand-access-first-hit--fetched-by-software-prefetch>

##### `0x81DF`, LL\_CACHE\_HIT\_RW\_FPRFM, Last level cache demand access first hit, fetched by software prefetch

The counter counts each demand access first hit counted by [LL\_CACHE\_HIT\_RW\_FPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81FF--LL-CACHE-HIT-RW-FPRF--Last-level-cache-demand-access-first-hit--fetched-by-prefetch?lang=en#event_ll_cache_hit_rw_fprf) where the cache line was fetched in response to a prefetch instruction.

That is, the [LL\_CACHE\_REFILL\_PRFM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x829B--LL-CACHE-REFILL-PRFM--Last-level-cache-refill--software-prefetch?lang=en#event_ll_cache_refill_prfm) event was generated when the cache line was fetched into the cache.

Only the first hit by a demand access is counted. After this event is generated for a cache line, the event is not generated again for the same cache line while it remains in the cache.
