# ​0x8234, LOCAL_MEM_PRFM, Access to memory attached to this device, software prefetch

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8234--LOCAL-MEM-PRFM--Access-to-memory-attached-to-this-device--software-prefetch>

##### `0x8234`, LOCAL\_MEM\_PRFM, Access to memory attached to this device, software prefetch

The counter counts each access counted by [LOCAL\_MEM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8230--LOCAL-MEM--Access-to-memory-attached-to-this-device?lang=en#event_local_mem) that is due to a prefetch instruction.

It is IMPLEMENTATION DEFINED whether an access to external memory due to a prefetch to a cache is counted by [LOCAL\_MEM\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8233--LOCAL-MEM-RW--Access-to-memory-attached-to-this-device--demand-access?lang=en#event_local_mem_rw) or [LOCAL\_MEM\_PRFM](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8234--LOCAL-MEM-PRFM--Access-to-memory-attached-to-this-device--software-prefetch?lang=en#event_local_mem_prfm).
