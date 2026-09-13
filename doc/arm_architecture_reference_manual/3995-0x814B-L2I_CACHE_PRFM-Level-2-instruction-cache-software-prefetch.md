# ​0x814B, L2I_CACHE_PRFM, Level 2 instruction cache software prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x814B--L2I-CACHE-PRFM--Level-2-instruction-cache-software-prefetch>

##### `0x814B`, L2I\_CACHE\_PRFM, Level 2 instruction cache software prefetch

The counter counts each access counted by [L2I\_CACHE\_PRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8281--L2I-CACHE-PRF--Level-2-instruction-cache--prefetch-hit?lang=en#event_l2i_cache_prf) that is due to a prefetch instruction.

This includes accesses to the Level 2 instruction or unified cache due to a refill of another cache caused by a prefetch instruction.

Arm recommends that this event is implemented if event [L2I\_CACHE\_RD](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8149--L2I-CACHE-RD--Level-2-instruction-cache-demand-fetch?lang=en#event_l2i_cache_rd) is implemented.
