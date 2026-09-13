# ​0x8241, L2I_LFB_HIT_RD, Level 2 instruction cache demand fetch line-fill buffer hit

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8241--L2I-LFB-HIT-RD--Level-2-instruction-cache-demand-fetch-line-fill-buffer-hit>

##### `0x8241`, L2I\_LFB\_HIT\_RD, Level 2 instruction cache demand fetch line-fill buffer hit

The counter counts each demand access counted by [L2I\_CACHE\_HIT\_RD](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x81C1--L2I-CACHE-HIT-RD--Level-2-instruction-cache-demand-fetch-hit?lang=en#event_l2i_cache_hit_rd) that hits a recently fetched line in the Level 2 instruction or unified cache.

That is, the access hits a cache line that is in the process of being loaded into the Level 2 instruction or unified cache, and so does not generate a new refill, but has to wait for the previous refill to complete.
