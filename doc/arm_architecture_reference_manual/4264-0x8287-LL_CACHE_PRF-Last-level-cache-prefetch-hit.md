# ​0x8287, LL_CACHE_PRF, Last level cache, prefetch hit

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8287--LL-CACHE-PRF--Last-level-cache--prefetch-hit>

##### `0x8287`, LL\_CACHE\_PRF, Last level cache, prefetch hit

The counter counts each access counted by [LL\_CACHE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0032--LL-CACHE--Last-level-cache-access?lang=en#event_ll_cache) that is due to a prefetch instruction, or hardware prefetch.

This includes accesses to the Last level cache due to a refill of another cache caused by a prefetch instruction, or hardware prefetch.
