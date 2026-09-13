# ​0x81DC, L1D_CACHE_HIT_RW_FPRFM, Level 1 data cache demand access first hit, fetched by software prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81DC--L1D-CACHE-HIT-RW-FPRFM--Level-1-data-cache-demand-access-first-hit--fetched-by-software-prefetch>

##### `0x81DC`, L1D\_CACHE\_HIT\_RW\_FPRFM, Level 1 data cache demand access first hit, fetched by software prefetch

The counter counts each demand access first hit counted by [L1D\_CACHE\_HIT\_RW\_FPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81FC--L1D-CACHE-HIT-RW-FPRF--Level-1-data-cache-demand-access-first-hit--fetched-by-prefetch?lang=en#event_l1d_cache_hit_rw_fprf) where the cache line was fetched in response to a prefetch instruction.

That is, the [L1D\_CACHE\_REFILL\_PRFM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8146--L1D-CACHE-REFILL-PRFM--Level-1-data-cache-refill--software-prefetch?lang=en#event_l1d_cache_refill_prfm) event was generated when the cache line was fetched into the cache.

Only the first hit by a demand access is counted. After this event is generated for a cache line, the event is not generated again for the same cache line while it remains in the cache.
