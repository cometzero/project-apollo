# ​0x4025, MEM_ACCESS_CHECKED_RD, Checked data memory access, read

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4025--MEM-ACCESS-CHECKED-RD--Checked-data-memory-access--read>

##### `0x4025`, MEM\_ACCESS\_CHECKED\_RD, Checked data memory access, read

The counter counts each [Memory-read operation](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#caceiega) counted by [MEM\_ACCESS\_CHECKED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x4024--MEM-ACCESS-CHECKED--Checked-data-memory-access?lang=en#event_mem_access_checked).

It is IMPLEMENTATION DEFINED whether the counter increments on a Tag Checked access made when Tag Check Faults are configured to be ignored by [SCTLR\_ELx](/documentation/ddi0487/mc/-Part-K-Appendixes/-Appendix-K14-Registers-Index/-K14-1-Introduction-and-register-disambiguation/-K14-1-2-Register-name-disambiguation-by-Exception-level?lang=en#sctlr_elx).TCF or [SCTLR\_ELx](/documentation/ddi0487/mc/-Part-K-Appendixes/-Appendix-K14-Registers-Index/-K14-1-Introduction-and-register-disambiguation/-K14-1-2-Register-name-disambiguation-by-Exception-level?lang=en#sctlr_elx).TCF0.

PMCEID1\_EL0[37] reads as 1 if this event is implemented and 0 otherwise.
