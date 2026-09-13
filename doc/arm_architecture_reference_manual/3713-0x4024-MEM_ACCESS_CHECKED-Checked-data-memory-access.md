# ​0x4024, MEM_ACCESS_CHECKED, Checked data memory access

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4024--MEM-ACCESS-CHECKED--Checked-data-memory-access>

##### `0x4024`, MEM\_ACCESS\_CHECKED, Checked data memory access

The counter counts each memory access counted by [MEM\_ACCESS](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0013--MEM-ACCESS--Data-memory-access?lang=en#event_mem_access) that accesses an Allocation Tag due to a Tag Check operation.

It is IMPLEMENTATION DEFINED whether the counter increments on a Tag Checked access made when Tag Check Faults are configured to be ignored by [SCTLR\_ELx](/documentation/ddi0487/mc/-Part-K-Appendixes/-Appendix-K14-Registers-Index/-K14-1-Introduction-and-register-disambiguation/-K14-1-2-Register-name-disambiguation-by-Exception-level?lang=en#sctlr_elx).TCF or [SCTLR\_ELx](/documentation/ddi0487/mc/-Part-K-Appendixes/-Appendix-K14-Registers-Index/-K14-1-Introduction-and-register-disambiguation/-K14-1-2-Register-name-disambiguation-by-Exception-level?lang=en#sctlr_elx).TCF0.

PMCEID1\_EL0[36] reads as 1 if this event is implemented and 0 otherwise.
