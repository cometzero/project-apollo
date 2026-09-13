# ​0x8143, L1I_CACHE_PRFM, Level 1 instruction cache software prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8143--L1I-CACHE-PRFM--Level-1-instruction-cache-software-prefetch>

##### `0x8143`, L1I\_CACHE\_PRFM, Level 1 instruction cache software prefetch

The counter counts each access counted by [L1I\_CACHE\_PRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8280--L1I-CACHE-PRF--Level-1-instruction-cache--prefetch-hit?lang=en#event_l1i_cache_prf) that is due to a prefetch instruction.

Arm recommends that this event is implemented if event [L1I\_CACHE\_RD](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8141--L1I-CACHE-RD--Level-1-instruction-cache-demand-fetch?lang=en#event_l1i_cache_rd) is implemented.
