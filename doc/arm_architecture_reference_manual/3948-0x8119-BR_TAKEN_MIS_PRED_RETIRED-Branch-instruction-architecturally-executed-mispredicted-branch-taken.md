# ​0x8119, BR_TAKEN_MIS_PRED_RETIRED, Branch instruction architecturally executed, mispredicted branch, taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8119--BR-TAKEN-MIS-PRED-RETIRED--Branch-instruction-architecturally-executed--mispredicted-branch--taken>

##### `0x8119`, BR\_TAKEN\_MIS\_PRED\_RETIRED, Branch instruction architecturally executed, mispredicted branch, taken

The counter counts each instruction counted by both [BR\_MIS\_PRED\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x0022--BR-MIS-PRED-RETIRED--Branch-instruction-architecturally-executed--mispredicted?lang=en#event_br_mis_pred_retired) and [PC\_WRITE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000C--PC-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--Software-change-of-the-PC?lang=en#event_pc_write_retired).

These are all branch instructions on the architecturally executed path, where the branch is mispredicted and taken.
