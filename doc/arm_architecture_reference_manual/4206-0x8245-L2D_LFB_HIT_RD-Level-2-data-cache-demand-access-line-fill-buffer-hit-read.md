# ​0x8245, L2D_LFB_HIT_RD, Level 2 data cache demand access line-fill buffer hit, read

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8245--L2D-LFB-HIT-RD--Level-2-data-cache-demand-access-line-fill-buffer-hit--read>

##### `0x8245`, L2D\_LFB\_HIT\_RD, Level 2 data cache demand access line-fill buffer hit, read

The counter counts each demand access counted by [L2D\_CACHE\_HIT\_RD](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81C5--L2D-CACHE-HIT-RD--Level-2-data-cache-demand-access-hit--read?lang=en#event_l2d_cache_hit_rd) that hits a recently fetched line in the Level 2 data or unified cache.

That is, the access hits a cache line that is in the process of being loaded into the Level 2 data or unified cache, and so does not generate a new refill, but has to wait for the previous refill to complete.
