# ​0x81EF, LL_CACHE_HIT_RW_FHWPRF, Last level cache demand access first hit, fetched by hardware prefetcher

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81EF--LL-CACHE-HIT-RW-FHWPRF--Last-level-cache-demand-access-first-hit--fetched-by-hardware-prefetcher>

##### `0x81EF`, LL\_CACHE\_HIT\_RW\_FHWPRF, Last level cache demand access first hit, fetched by hardware prefetcher

The counter counts each demand access first hit counted by [LL\_CACHE\_HIT\_RW\_FPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81FF--LL-CACHE-HIT-RW-FPRF--Last-level-cache-demand-access-first-hit--fetched-by-prefetch?lang=en#event_ll_cache_hit_rw_fprf) where the cache line was fetched by a hardware prefetcher.

That is, the [LL\_CACHE\_REFILL\_HWPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81BF--LL-CACHE-REFILL-HWPRF--Last-level-cache-refill--hardware-prefetch?lang=en#event_ll_cache_refill_hwprf) event was generated when the cache line was fetched into the cache.

Only the first hit by a demand access is counted. After this event is generated for a cache line, the event is not generated again for the same cache line while it remains in the cache.
