# ​0x8148, L2D_CACHE_RW, Level 2 data cache demand access

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8148--L2D-CACHE-RW--Level-2-data-cache-demand-access>

##### `0x8148`, L2D\_CACHE\_RW, Level 2 data cache demand access

The counter counts each access counted by [L2D\_CACHE](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0016--L2D-CACHE--Level-2-data-cache-access?lang=en#event_l2d_cache) that is due to a demand [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega) or demand [Memory-write operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caccfcjj).

This includes:

- Accesses made by [speculatively executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacijece) instructions.
- Accesses to the Level 2 data or unified cache due to a refill of another cache caused by a demand [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega) or demand [Memory-write operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caccfcjj).

Arm recommends that this event is implemented if any of the following are true:

- Event [L2D\_CACHE\_PRFM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x814A--L2D-CACHE-PRFM--Level-2-data-cache-software-prefetch?lang=en#event_l2d_cache_prfm) is implemented.
- Event [L2D\_CACHE\_HWPRF](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8155--L2D-CACHE-HWPRF--Level-2-data-cache-hardware-prefetch?lang=en#event_l2d_cache_hwprf) is implemented.
