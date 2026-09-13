# ​0x81ED, L2D_CACHE_HIT_RW_FHWPRF, Level 2 data cache demand access first hit, fetched by hardware prefetcher

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81ED--L2D-CACHE-HIT-RW-FHWPRF--Level-2-data-cache-demand-access-first-hit--fetched-by-hardware-prefetcher>

##### `0x81ED`, L2D\_CACHE\_HIT\_RW\_FHWPRF, Level 2 data cache demand access first hit, fetched by hardware prefetcher

The counter counts each demand access first hit counted by [L2D\_CACHE\_HIT\_RW\_FPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81FD--L2D-CACHE-HIT-RW-FPRF--Level-2-data-cache-demand-access-first-hit--fetched-by-prefetch?lang=en#event_l2d_cache_hit_rw_fprf) where the cache line was fetched by a hardware prefetcher.

That is, the [L2D\_CACHE\_REFILL\_HWPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81BD--L2D-CACHE-REFILL-HWPRF--Level-2-data-cache-refill--hardware-prefetch?lang=en#event_l2d_cache_refill_hwprf) event was generated when the cache line was fetched into the cache.

Only the first hit by a demand access is counted. After this event is generated for a cache line, the event is not generated again for the same cache line while it remains in the cache.
