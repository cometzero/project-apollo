# ​0x8251, L2I_LFB_HIT_RD_FPRFM, Level 2 instruction cache demand fetch line-fill buffer first hit, recently fetched by software prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8251--L2I-LFB-HIT-RD-FPRFM--Level-2-instruction-cache-demand-fetch-line-fill-buffer-first-hit--recently-fetched-by-software-prefetch>

##### `0x8251`, L2I\_LFB\_HIT\_RD\_FPRFM, Level 2 instruction cache demand fetch line-fill buffer first hit, recently fetched by software prefetch

The counter counts each demand fetch line-fill buffer first hit counted by [L2I\_LFB\_HIT\_RD\_FPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8271--L2I-LFB-HIT-RD-FPRF--Level-2-instruction-cache-demand-fetch-line-fill-buffer-first-hit--recently-fetched-by-prefetch?lang=en#event_l2i_lfb_hit_rd_fprf) where the cache line was fetched in response to a prefetch instruction.

That is, the fetch hits a cache line that is in the process of being loaded into the Level 2 instruction or unified cache, and so does not generate a new refill, but has to wait for the previous refill to complete, and the [L2I\_CACHE\_REFILL\_PRFM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x814F--L2I-CACHE-REFILL-PRFM--Level-2-instruction-cache-refill--software-prefetch?lang=en#event_l2i_cache_refill_prfm) event was generated when the cache line was fetched into the cache.

Only the first hit by a demand access is counted. After this event is generated for a cache line, the event is not generated again for the same cache line while it remains in the cache.
