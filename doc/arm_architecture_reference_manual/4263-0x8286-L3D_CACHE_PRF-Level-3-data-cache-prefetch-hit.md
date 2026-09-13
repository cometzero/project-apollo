# ​0x8286, L3D_CACHE_PRF, Level 3 data cache, prefetch hit

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8286--L3D-CACHE-PRF--Level-3-data-cache--prefetch-hit>

##### `0x8286`, L3D\_CACHE\_PRF, Level 3 data cache, prefetch hit

The counter counts each access counted by [L3D\_CACHE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x002B--L3D-CACHE--Level-3-data-cache-access?lang=en#event_l3d_cache) that is due to a prefetch instruction, or hardware prefetch.

This includes accesses to the Level 3 data or unified cache due to a refill of another cache caused by a prefetch instruction, or hardware prefetch.
