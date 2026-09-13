# ​0x8299, LL_CACHE_PRFM, Last level cache software prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8299--LL-CACHE-PRFM--Last-level-cache-software-prefetch>

##### `0x8299`, LL\_CACHE\_PRFM, Last level cache software prefetch

The counter counts each access counted by [LL\_CACHE\_PRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8287--LL-CACHE-PRF--Last-level-cache--prefetch-hit?lang=en#event_ll_cache_prf) that is due to a prefetch instruction.

This includes accesses to the Last level cache due to a refill of another cache caused by a prefetch instruction.

Arm recommends that this event is implemented if event [LL\_CACHE\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8298--LL-CACHE-RW--Last-level-cache-demand-access?lang=en#event_ll_cache_rw) is implemented.
