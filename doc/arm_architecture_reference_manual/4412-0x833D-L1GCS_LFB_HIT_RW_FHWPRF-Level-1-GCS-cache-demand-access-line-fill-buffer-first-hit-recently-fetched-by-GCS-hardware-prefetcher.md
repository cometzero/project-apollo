# ​0x833D, L1GCS_LFB_HIT_RW_FHWPRF, Level 1 GCS cache demand access line-fill buffer first hit, recently fetched by GCS hardware prefetcher

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x833D--L1GCS-LFB-HIT-RW-FHWPRF--Level-1-GCS-cache-demand-access-line-fill-buffer-first-hit--recently-fetched-by-GCS-hardware-prefetcher>

##### `0x833D`, L1GCS\_LFB\_HIT\_RW\_FHWPRF, Level 1 GCS cache demand access line-fill buffer first hit, recently fetched by GCS hardware prefetcher

The counter counts each demand access line-fill buffer first hit counted by [L1GCS\_LFB\_HIT\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x833C--L1GCS-LFB-HIT-RW--Level-1-GCS-cache-demand-access-line-fill-buffer-hit?lang=en#event_l1gcs_lfb_hit_rw) where the cache line was fetched by a GCS hardware prefetcher.

That is, the access hits a cache line that is in the process of being loaded into the Level 1 cache, and so does not generate a new refill, but has to wait for the previous refill to complete, and the [L1GCS\_CACHE\_REFILL\_HWPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8339--L1GCS-CACHE-REFILL-HWPRF--Level-1-GCS-cache-refill--hardware-prefetch?lang=en#event_l1gcs_cache_refill_hwprf) event was generated when the cache line was fetched into the cache.
