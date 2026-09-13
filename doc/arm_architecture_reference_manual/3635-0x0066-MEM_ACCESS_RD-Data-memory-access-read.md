# ​0x0066, MEM_ACCESS_RD, Data memory access, read

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0066--MEM-ACCESS-RD--Data-memory-access--read>

##### `0x0066`, MEM\_ACCESS\_RD, Data memory access, read

If the [MEM\_ACCESS\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82A0--MEM-ACCESS-RW--Data-memory-access--demand-access?lang=en#event_mem_access_rw) event is implemented, the counter counts each access counted by [MEM\_ACCESS\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82A0--MEM-ACCESS-RW--Data-memory-access--demand-access?lang=en#event_mem_access_rw) that is a [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega).

If the [MEM\_ACCESS\_RW](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82A0--MEM-ACCESS-RW--Data-memory-access--demand-access?lang=en#event_mem_access_rw) event is not implemented, the counter counts each access counted by [MEM\_ACCESS](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0013--MEM-ACCESS--Data-memory-access?lang=en#event_mem_access) that is a [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega).

When FEAT\_PMUv3p8 is not implemented, this is an IMPLEMENTATION DEFINED event.
