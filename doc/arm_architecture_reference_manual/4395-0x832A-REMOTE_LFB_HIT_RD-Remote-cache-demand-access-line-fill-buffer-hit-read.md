# ​0x832A, REMOTE_LFB_HIT_RD, Remote cache demand access line-fill buffer hit, read

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x832A--REMOTE-LFB-HIT-RD--Remote-cache-demand-access-line-fill-buffer-hit--read>

##### `0x832A`, REMOTE\_LFB\_HIT\_RD, Remote cache demand access line-fill buffer hit, read

The counter counts each cache hit on a remote device counted by [REMOTE\_CACHE\_HIT\_RD](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8328--REMOTE-CACHE-HIT-RD--Remote-cache-demand-access-hit--read?lang=en#event_remote_cache_hit_rd) that hits a recently fetched line.

That is, the read hits a cache line that is in the process of being loaded into the cache attached to a remote device, and so does not generate a new refill, but has to wait for the previous refill to complete.
