# ​0x8142, L1D_CACHE_PRFM, Level 1 data cache software prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8142--L1D-CACHE-PRFM--Level-1-data-cache-software-prefetch>

##### `0x8142`, L1D\_CACHE\_PRFM, Level 1 data cache software prefetch

The counter counts each access counted by [L1D\_CACHE\_PRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8284--L1D-CACHE-PRF--Level-1-data-cache--prefetch-hit?lang=en#event_l1d_cache_prf) that is due to a prefetch instruction.

Arm recommends that this event is implemented if event [L1D\_CACHE\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8140--L1D-CACHE-RW--Level-1-data-cache-demand-access?lang=en#event_l1d_cache_rw) is implemented.
