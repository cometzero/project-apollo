# ​0x82F4, ITLB_WALK_RETIRED, Instruction architecturally executed, at least one translation table walk

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x82F4--ITLB-WALK-RETIRED--Instruction-architecturally-executed--at-least-one-translation-table-walk>

##### `0x82F4`, ITLB\_WALK\_RETIRED, Instruction architecturally executed, at least one translation table walk

The counter counts each instruction which was [architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) counted by [INST\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0008--INST-RETIRED--Instruction-architecturally-executed?lang=en#event_inst_retired) that caused a refill of an instruction TLB involving at least one translation table walk access.

The counter does not count the instruction which was [architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) if any of the following are true:

- The access generates a Translation fault because the applicable [TCR\_ELx](/documentation/ddi0487/mc/-Part-K-Appendixes/-Appendix-K14-Registers-Index/-K14-1-Introduction-and-register-disambiguation/-K14-1-2-Register-name-disambiguation-by-Exception-level?lang=en#tcr_elx).EPDy bit is 1.
- FEAT\_E0PD is implemented and the access is an unprivileged access that generates a Translation fault because the applicable [TCR\_ELx](/documentation/ddi0487/mc/-Part-K-Appendixes/-Appendix-K14-Registers-Index/-K14-1-Introduction-and-register-disambiguation/-K14-1-2-Register-name-disambiguation-by-Exception-level?lang=en#tcr_elx).E0PDy bit is 1.

It is IMPLEMENTATION DEFINED whether the counter counts the instruction which was [architecturally executed](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacciiig) if the access generates a Translation fault for any other reason.
