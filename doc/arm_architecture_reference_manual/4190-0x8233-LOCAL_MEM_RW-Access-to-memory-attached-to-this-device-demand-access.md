# ​0x8233, LOCAL_MEM_RW, Access to memory attached to this device, demand access

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8233--LOCAL-MEM-RW--Access-to-memory-attached-to-this-device--demand-access>

##### `0x8233`, LOCAL\_MEM\_RW, Access to memory attached to this device, demand access

The counter counts each access counted by [LOCAL\_MEM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8230--LOCAL-MEM--Access-to-memory-attached-to-this-device?lang=en#event_local_mem) that is a demand [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega) or demand [Memory-write operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caccfcjj).

It is IMPLEMENTATION DEFINED whether an access to external memory due to a prefetch to a cache is counted by [LOCAL\_MEM\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8233--LOCAL-MEM-RW--Access-to-memory-attached-to-this-device--demand-access?lang=en#event_local_mem_rw) or [LOCAL\_MEM\_PRFM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8234--LOCAL-MEM-PRFM--Access-to-memory-attached-to-this-device--software-prefetch?lang=en#event_local_mem_prfm).
