# ​0x8140, L1D_CACHE_RW, Level 1 data cache demand access

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8140--L1D-CACHE-RW--Level-1-data-cache-demand-access>

##### `0x8140`, L1D\_CACHE\_RW, Level 1 data cache demand access

The counter counts each access counted by [L1D\_CACHE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0004--L1D-CACHE--Level-1-data-cache-access?lang=en#event_l1d_cache) that is due to a demand [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega) or demand [Memory-write operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caccfcjj).

This includes accesses made by [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) instructions.

Arm recommends that this event is implemented if any of the following are true:

- Event [L1D\_CACHE\_PRFM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8142--L1D-CACHE-PRFM--Level-1-data-cache-software-prefetch?lang=en#event_l1d_cache_prfm) is implemented.
- Event [L1D\_CACHE\_HWPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8154--L1D-CACHE-HWPRF--Level-1-data-cache-hardware-prefetch?lang=en#event_l1d_cache_hwprf) is implemented.
