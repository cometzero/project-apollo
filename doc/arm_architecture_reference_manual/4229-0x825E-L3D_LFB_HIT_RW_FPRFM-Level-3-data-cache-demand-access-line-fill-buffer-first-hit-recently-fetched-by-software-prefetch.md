# ​0x825E, L3D_LFB_HIT_RW_FPRFM, Level 3 data cache demand access line-fill buffer first hit, recently fetched by software prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x825E--L3D-LFB-HIT-RW-FPRFM--Level-3-data-cache-demand-access-line-fill-buffer-first-hit--recently-fetched-by-software-prefetch>

##### `0x825E`, L3D\_LFB\_HIT\_RW\_FPRFM, Level 3 data cache demand access line-fill buffer first hit, recently fetched by software prefetch

The counter counts each demand access line-fill buffer first hit counted by [L3D\_LFB\_HIT\_RW\_FPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x827E--L3D-LFB-HIT-RW-FPRF--Level-3-data-cache-demand-access-line-fill-buffer-first-hit--recently-fetched-by-prefetch?lang=en#event_l3d_lfb_hit_rw_fprf) where the cache line was fetched in response to a prefetch instruction.

That is, the access hits a cache line that is in the process of being loaded into the Level 3 data or unified cache, and so does not generate a new refill, but has to wait for the previous refill to complete, and the [L3D\_CACHE\_REFILL\_PRFM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8153--L3D-CACHE-REFILL-PRFM--Level-3-data-cache-refill--software-prefetch?lang=en#event_l3d_cache_refill_prfm) event was generated when the cache line was fetched into the cache.

Only the first hit by a demand access is counted. After this event is generated for a cache line, the event is not generated again for the same cache line while it remains in the cache.
