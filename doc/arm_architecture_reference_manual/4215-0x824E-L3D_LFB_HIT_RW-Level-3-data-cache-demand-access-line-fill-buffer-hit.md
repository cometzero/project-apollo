# ​0x824E, L3D_LFB_HIT_RW, Level 3 data cache demand access line-fill buffer hit

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x824E--L3D-LFB-HIT-RW--Level-3-data-cache-demand-access-line-fill-buffer-hit>

##### `0x824E`, L3D\_LFB\_HIT\_RW, Level 3 data cache demand access line-fill buffer hit

The counter counts each demand access counted by [L3D\_CACHE\_HIT\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81CE--L3D-CACHE-HIT-RW--Level-3-data-cache-demand-access-hit?lang=en#event_l3d_cache_hit_rw) that hits a recently fetched line in the Level 3 data or unified cache.

That is, the access hits a cache line that is in the process of being loaded into the Level 3 data or unified cache, and so does not generate a new refill, but has to wait for the previous refill to complete.
