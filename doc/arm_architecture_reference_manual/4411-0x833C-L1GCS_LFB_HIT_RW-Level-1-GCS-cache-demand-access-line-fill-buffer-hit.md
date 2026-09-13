# ​0x833C, L1GCS_LFB_HIT_RW, Level 1 GCS cache demand access line-fill buffer hit

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x833C--L1GCS-LFB-HIT-RW--Level-1-GCS-cache-demand-access-line-fill-buffer-hit>

##### `0x833C`, L1GCS\_LFB\_HIT\_RW, Level 1 GCS cache demand access line-fill buffer hit

The counter counts each demand access counted by [L1GCS\_CACHE\_HIT\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8336--L1GCS-CACHE-HIT-RW--Level-1-GCS-cache-demand-access-hit?lang=en#event_l1gcs_cache_hit_rw) that hits a recently fetched line in a Level 1 cache.

That is, the access hits a cache line that is in the process of being loaded into the Level 1 cache, and so does not generate a new refill, but has to wait for the previous refill to complete.
