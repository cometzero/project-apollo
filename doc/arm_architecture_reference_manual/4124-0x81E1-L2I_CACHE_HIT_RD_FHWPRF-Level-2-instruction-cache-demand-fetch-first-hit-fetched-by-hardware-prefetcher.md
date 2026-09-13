# ​0x81E1, L2I_CACHE_HIT_RD_FHWPRF, Level 2 instruction cache demand fetch first hit, fetched by hardware prefetcher

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81E1--L2I-CACHE-HIT-RD-FHWPRF--Level-2-instruction-cache-demand-fetch-first-hit--fetched-by-hardware-prefetcher>

##### `0x81E1`, L2I\_CACHE\_HIT\_RD\_FHWPRF, Level 2 instruction cache demand fetch first hit, fetched by hardware prefetcher

The counter counts each demand fetch first hit counted by [L2I\_CACHE\_HIT\_RD\_FPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81F1--L2I-CACHE-HIT-RD-FPRF--Level-2-instruction-cache-demand-fetch-first-hit--fetched-by-prefetch?lang=en#event_l2i_cache_hit_rd_fprf) where the cache line was fetched by a hardware prefetcher.

That is, the [L2I\_CACHE\_REFILL\_HWPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81B9--L2I-CACHE-REFILL-HWPRF--Level-2-instruction-cache-refill--hardware-prefetch?lang=en#event_l2i_cache_refill_hwprf) event was generated when the cache line was fetched into the cache.

Only the first hit by a demand access is counted. After this event is generated for a cache line, the event is not generated again for the same cache line while it remains in the cache.
