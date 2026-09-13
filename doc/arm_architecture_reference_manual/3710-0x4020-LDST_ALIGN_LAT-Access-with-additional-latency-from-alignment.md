# ​0x4020, LDST_ALIGN_LAT, Access with additional latency from alignment

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4020--LDST-ALIGN-LAT--Access-with-additional-latency-from-alignment>

##### `0x4020`, LDST\_ALIGN\_LAT, Access with additional latency from alignment

The counter counts each access counted by [MEM\_ACCESS](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0013--MEM-ACCESS--Data-memory-access?lang=en#event_mem_access) that incurred additional latency due to the alignment of the address and size of data being accessed.

PMCEID1\_EL0[32] reads as 1 if this event is implemented and 0 otherwise.
