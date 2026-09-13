# ​0x8151, L3D_CACHE_PRFM, Level 3 data cache software prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8151--L3D-CACHE-PRFM--Level-3-data-cache-software-prefetch>

##### `0x8151`, L3D\_CACHE\_PRFM, Level 3 data cache software prefetch

The counter counts each access counted by [L3D\_CACHE\_PRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8286--L3D-CACHE-PRF--Level-3-data-cache--prefetch-hit?lang=en#event_l3d_cache_prf) that is due to a prefetch instruction.

This includes accesses to the Level 3 data or unified cache due to a refill of another cache caused by a prefetch instruction.

Arm recommends that this event is implemented if event [L3D\_CACHE\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8150--L3D-CACHE-RW--Level-3-data-cache-demand-access?lang=en#event_l3d_cache_rw) is implemented.
