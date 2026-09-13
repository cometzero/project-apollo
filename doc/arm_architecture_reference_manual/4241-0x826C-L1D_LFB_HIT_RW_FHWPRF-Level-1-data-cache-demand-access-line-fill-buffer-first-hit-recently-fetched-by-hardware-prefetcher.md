# ​0x826C, L1D_LFB_HIT_RW_FHWPRF, Level 1 data cache demand access line-fill buffer first hit, recently fetched by hardware prefetcher

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x826C--L1D-LFB-HIT-RW-FHWPRF--Level-1-data-cache-demand-access-line-fill-buffer-first-hit--recently-fetched-by-hardware-prefetcher>

##### `0x826C`, L1D\_LFB\_HIT\_RW\_FHWPRF, Level 1 data cache demand access line-fill buffer first hit, recently fetched by hardware prefetcher

The counter counts each demand access line-fill buffer first hit counted by [L1D\_LFB\_HIT\_RW\_FPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x827C--L1D-LFB-HIT-RW-FPRF--Level-1-data-cache-demand-access-line-fill-buffer-first-hit--recently-fetched-by-prefetch?lang=en#event_l1d_lfb_hit_rw_fprf) where the cache line was fetched by a hardware prefetcher.

That is, the access hits a cache line that is in the process of being loaded into the Level 1 data or unified cache, and so does not generate a new refill, but has to wait for the previous refill to complete, and the [L1D\_CACHE\_REFILL\_HWPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81BC--L1D-CACHE-REFILL-HWPRF--Level-1-data-cache-refill--hardware-prefetch?lang=en#event_l1d_cache_refill_hwprf) event was generated when the cache line was fetched into the cache.

Only the first hit by a demand access is counted. After this event is generated for a cache line, the event is not generated again for the same cache line while it remains in the cache.
