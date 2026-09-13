# ​0x8281, L2I_CACHE_PRF, Level 2 instruction cache, prefetch hit

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8281--L2I-CACHE-PRF--Level-2-instruction-cache--prefetch-hit>

##### `0x8281`, L2I\_CACHE\_PRF, Level 2 instruction cache, prefetch hit

The counter counts each access counted by [L2I\_CACHE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0027--L2I-CACHE--Level-2-instruction-cache-access?lang=en#event_l2i_cache) that is due to a prefetch instruction, or hardware prefetch.

This includes accesses to the Level 2 instruction or unified cache due to a refill of another cache caused by a prefetch instruction, or hardware prefetch.
