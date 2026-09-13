# ​0x81FC, L1D_CACHE_HIT_RW_FPRF, Level 1 data cache demand access first hit, fetched by prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81FC--L1D-CACHE-HIT-RW-FPRF--Level-1-data-cache-demand-access-first-hit--fetched-by-prefetch>

##### `0x81FC`, L1D\_CACHE\_HIT\_RW\_FPRF, Level 1 data cache demand access first hit, fetched by prefetch

The counter counts each demand access first hit counted by [L1D\_CACHE\_HIT\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81CC--L1D-CACHE-HIT-RW--Level-1-data-cache-demand-access-hit?lang=en#event_l1d_cache_hit_rw) where the cache line was fetched in response to a prefetch instruction or by a hardware prefetcher.

That is, the [L1D\_CACHE\_REFILL\_PRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x828C--L1D-CACHE-REFILL-PRF--Level-1-data-cache-refill--prefetch-hit?lang=en#event_l1d_cache_refill_prf) event was generated when the cache line was fetched into the cache.

Only the first hit by a demand access is counted. After this event is generated for a cache line, the event is not generated again for the same cache line while it remains in the cache.
