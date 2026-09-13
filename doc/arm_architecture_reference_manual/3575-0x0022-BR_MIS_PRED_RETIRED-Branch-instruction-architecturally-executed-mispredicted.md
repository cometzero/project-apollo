# ​0x0022, BR_MIS_PRED_RETIRED, Branch instruction architecturally executed, mispredicted

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0022--BR-MIS-PRED-RETIRED--Branch-instruction-architecturally-executed--mispredicted>

##### `0x0022`, BR\_MIS\_PRED\_RETIRED, Branch instruction architecturally executed, mispredicted

The counter counts each branch instruction counted by [BR\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0021--BR-RETIRED--Instruction-architecturally-executed--branch?lang=en#event_br_retired) that was not correctly predicted.

If no program-flow prediction resources are implemented, this event counts all retired not-taken branches.

PMCEID1\_EL0[2] reads as 1 if this event is implemented and 0 otherwise.
