# ​0x8337, L1GCS_CACHE_HIT_RW_FHWPRF, Level 1 GCS cache demand access first hit, fetched by GCS hardware prefetcher

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8337--L1GCS-CACHE-HIT-RW-FHWPRF--Level-1-GCS-cache-demand-access-first-hit--fetched-by-GCS-hardware-prefetcher>

##### `0x8337`, L1GCS\_CACHE\_HIT\_RW\_FHWPRF, Level 1 GCS cache demand access first hit, fetched by GCS hardware prefetcher

The counter counts each demand access first hit counted by [L1GCS\_CACHE\_HIT\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8336--L1GCS-CACHE-HIT-RW--Level-1-GCS-cache-demand-access-hit?lang=en#event_l1gcs_cache_hit_rw) where the cache line was fetched by a GCS hardware prefetcher.

That is, the [L1GCS\_CACHE\_REFILL\_HWPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8339--L1GCS-CACHE-REFILL-HWPRF--Level-1-GCS-cache-refill--hardware-prefetch?lang=en#event_l1gcs_cache_refill_hwprf) event was generated when the cache line was fetched into the cache.

Only the first hit by a demand access is counted. After this event is generated for a cache line, the event is not generated again for the same cache line while it remains in the cache.
