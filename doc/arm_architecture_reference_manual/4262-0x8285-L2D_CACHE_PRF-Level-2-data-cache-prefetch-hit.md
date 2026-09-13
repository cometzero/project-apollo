# ​0x8285, L2D_CACHE_PRF, Level 2 data cache, prefetch hit

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8285--L2D-CACHE-PRF--Level-2-data-cache--prefetch-hit>

##### `0x8285`, L2D\_CACHE\_PRF, Level 2 data cache, prefetch hit

The counter counts each access counted by [L2D\_CACHE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0016--L2D-CACHE--Level-2-data-cache-access?lang=en#event_l2d_cache) that is due to a prefetch instruction, or hardware prefetch.

This includes accesses to the Level 2 data or unified cache due to a refill of another cache caused by a prefetch instruction, or hardware prefetch.
