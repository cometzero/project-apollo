# ​0x8248, L1D_LFB_HIT_WR, Level 1 data cache demand access line-fill buffer hit, write

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8248--L1D-LFB-HIT-WR--Level-1-data-cache-demand-access-line-fill-buffer-hit--write>

##### `0x8248`, L1D\_LFB\_HIT\_WR, Level 1 data cache demand access line-fill buffer hit, write

The counter counts each demand access counted by [L1D\_CACHE\_HIT\_WR](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81C8--L1D-CACHE-HIT-WR--Level-1-data-cache-demand-access-hit--write?lang=en#event_l1d_cache_hit_wr) that hits a recently fetched line in the Level 1 data or unified cache.

That is, the access hits a cache line that is in the process of being loaded into the Level 1 data or unified cache, and so does not generate a new refill, but has to wait for the previous refill to complete.
