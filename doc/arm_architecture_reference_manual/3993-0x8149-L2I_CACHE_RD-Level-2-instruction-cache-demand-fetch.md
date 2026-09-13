# ​0x8149, L2I_CACHE_RD, Level 2 instruction cache demand fetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8149--L2I-CACHE-RD--Level-2-instruction-cache-demand-fetch>

##### `0x8149`, L2I\_CACHE\_RD, Level 2 instruction cache demand fetch

The counter counts each access counted by [L2I\_CACHE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0027--L2I-CACHE--Level-2-instruction-cache-access?lang=en#event_l2i_cache) that is due to a demand [Instruction memory access](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cachjjbe).

This includes:

- Instruction prefetches made by the PE for [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) instructions.
- Accesses to the Level 2 instruction or unified cache due to a refill of another cache caused by a demand [Instruction memory access](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cachjjbe).

Arm recommends that this event is implemented if any of the following are true:

- Event [L2I\_CACHE\_PRFM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x814B--L2I-CACHE-PRFM--Level-2-instruction-cache-software-prefetch?lang=en#event_l2i_cache_prfm) is implemented.
- Event [L2I\_CACHE\_HWPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x814D--L2I-CACHE-HWPRF--Level-2-instruction-cache-hardware-prefetch?lang=en#event_l2i_cache_hwprf) is implemented.
