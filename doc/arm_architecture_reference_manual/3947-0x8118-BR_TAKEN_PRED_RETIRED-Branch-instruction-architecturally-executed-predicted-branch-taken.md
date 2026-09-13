# ​0x8118, BR_TAKEN_PRED_RETIRED, Branch instruction architecturally executed, predicted branch, taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8118--BR-TAKEN-PRED-RETIRED--Branch-instruction-architecturally-executed--predicted-branch--taken>

##### `0x8118`, BR\_TAKEN\_PRED\_RETIRED, Branch instruction architecturally executed, predicted branch, taken

The counter counts each instruction counted by both [BR\_PRED\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x811C--BR-PRED-RETIRED--Branch-instruction-architecturally-executed--predicted-branch?lang=en#event_br_pred_retired) and [PC\_WRITE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000C--PC-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--Software-change-of-the-PC?lang=en#event_pc_write_retired).

These are all branch instructions on the architecturally executed path, where the branch is correctly predicted and taken.
