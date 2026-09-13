# ​0x814A, L2D_CACHE_PRFM, Level 2 data cache software prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x814A--L2D-CACHE-PRFM--Level-2-data-cache-software-prefetch>

##### `0x814A`, L2D\_CACHE\_PRFM, Level 2 data cache software prefetch

The counter counts each access counted by [L2D\_CACHE\_PRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8285--L2D-CACHE-PRF--Level-2-data-cache--prefetch-hit?lang=en#event_l2d_cache_prf) that is due to a prefetch instruction.

This includes accesses to the Level 2 data or unified cache due to a refill of another cache caused by a prefetch instruction.

Arm recommends that this event is implemented if event [L2D\_CACHE\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8148--L2D-CACHE-RW--Level-2-data-cache-demand-access?lang=en#event_l2d_cache_rw) is implemented.
