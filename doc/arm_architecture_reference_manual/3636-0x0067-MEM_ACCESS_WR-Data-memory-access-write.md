# ​0x0067, MEM_ACCESS_WR, Data memory access, write

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0067--MEM-ACCESS-WR--Data-memory-access--write>

##### `0x0067`, MEM\_ACCESS\_WR, Data memory access, write

If the [MEM\_ACCESS\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82A0--MEM-ACCESS-RW--Data-memory-access--demand-access?lang=en#event_mem_access_rw) event is implemented, the counter counts each access counted by [MEM\_ACCESS\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82A0--MEM-ACCESS-RW--Data-memory-access--demand-access?lang=en#event_mem_access_rw) that is a [Memory-write operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caccfcjj).

If the [MEM\_ACCESS\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82A0--MEM-ACCESS-RW--Data-memory-access--demand-access?lang=en#event_mem_access_rw) event is not implemented, the counter counts each access counted by [MEM\_ACCESS](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0013--MEM-ACCESS--Data-memory-access?lang=en#event_mem_access) that is a [Memory-write operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caccfcjj).

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
