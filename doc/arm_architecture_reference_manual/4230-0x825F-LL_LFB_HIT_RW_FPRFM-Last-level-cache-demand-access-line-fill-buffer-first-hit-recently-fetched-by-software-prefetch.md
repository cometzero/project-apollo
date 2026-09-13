# ​0x825F, LL_LFB_HIT_RW_FPRFM, Last level cache demand access line-fill buffer first hit, recently fetched by software prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x825F--LL-LFB-HIT-RW-FPRFM--Last-level-cache-demand-access-line-fill-buffer-first-hit--recently-fetched-by-software-prefetch>

##### `0x825F`, LL\_LFB\_HIT\_RW\_FPRFM, Last level cache demand access line-fill buffer first hit, recently fetched by software prefetch

The counter counts each demand access line-fill buffer first hit counted by [LL\_LFB\_HIT\_RW\_FPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x827F--LL-LFB-HIT-RW-FPRF--Last-level-cache-demand-access-line-fill-buffer-first-hit--recently-fetched-by-prefetch?lang=en#event_ll_lfb_hit_rw_fprf) where the cache line was fetched in response to a prefetch instruction.

That is, the access hits a cache line that is in the process of being loaded into the Last level cache, and so does not generate a new refill, but has to wait for the previous refill to complete, and the [LL\_CACHE\_REFILL\_PRFM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x829B--LL-CACHE-REFILL-PRFM--Last-level-cache-refill--software-prefetch?lang=en#event_ll_cache_refill_prfm) event was generated when the cache line was fetched into the cache.

Only the first hit by a demand access is counted. After this event is generated for a cache line, the event is not generated again for the same cache line while it remains in the cache.
