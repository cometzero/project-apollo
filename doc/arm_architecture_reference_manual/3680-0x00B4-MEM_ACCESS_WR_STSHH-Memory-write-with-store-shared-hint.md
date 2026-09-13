# ​0x00B4, MEM_ACCESS_WR_STSHH, Memory write with store shared hint

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x00B4--MEM-ACCESS-WR-STSHH--Memory-write-with-store-shared-hint>

##### `0x00B4`, MEM\_ACCESS\_WR\_STSHH, Memory write with store shared hint

The counter counts each access counted by [MEM\_ACCESS\_WR](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0067--MEM-ACCESS-WR--Data-memory-access--write?lang=en#event_mem_access_wr) that has an associated store shared hint.

This hint indicates that the memory update should trigger a transaction that propagates the updated location to other PEs.
