# ​0x8141, L1I_CACHE_RD, Level 1 instruction cache demand fetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8141--L1I-CACHE-RD--Level-1-instruction-cache-demand-fetch>

##### `0x8141`, L1I\_CACHE\_RD, Level 1 instruction cache demand fetch

The counter counts each access counted by [L1I\_CACHE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0014--L1I-CACHE--Level-1-instruction-cache-access?lang=en#event_l1i_cache) that is due to a demand [Instruction memory access](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cachjjbe).

This includes instruction prefetches made by the PE for [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) instructions.

Arm recommends that this event is implemented if any of the following are true:

- Event [L1I\_CACHE\_PRFM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8143--L1I-CACHE-PRFM--Level-1-instruction-cache-software-prefetch?lang=en#event_l1i_cache_prfm) is implemented.
- Event [L1I\_CACHE\_HWPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8145--L1I-CACHE-HWPRF--Level-1-instruction-cache-hardware-prefetch?lang=en#event_l1i_cache_hwprf) is implemented.
