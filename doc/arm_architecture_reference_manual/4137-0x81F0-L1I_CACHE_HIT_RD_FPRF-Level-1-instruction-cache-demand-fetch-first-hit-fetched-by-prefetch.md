# ​0x81F0, L1I_CACHE_HIT_RD_FPRF, Level 1 instruction cache demand fetch first hit, fetched by prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81F0--L1I-CACHE-HIT-RD-FPRF--Level-1-instruction-cache-demand-fetch-first-hit--fetched-by-prefetch>

##### `0x81F0`, L1I\_CACHE\_HIT\_RD\_FPRF, Level 1 instruction cache demand fetch first hit, fetched by prefetch

The counter counts each demand fetch first hit counted by [L1I\_CACHE\_HIT\_RD](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81C0--L1I-CACHE-HIT-RD--Level-1-instruction-cache-demand-fetch-hit?lang=en#event_l1i_cache_hit_rd) where the cache line was fetched in response to a prefetch instruction or by a hardware prefetcher.

That is, the [L1I\_CACHE\_REFILL\_PRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8288--L1I-CACHE-REFILL-PRF--Level-1-instruction-cache-refill--prefetch-hit?lang=en#event_l1i_cache_refill_prf) event was generated when the cache line was fetched into the cache.

Only the first hit by a demand access is counted. After this event is generated for a cache line, the event is not generated again for the same cache line while it remains in the cache.
