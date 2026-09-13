# ​0x8182, BR_COND_TAKEN_RETIRED, Branch instruction architecturally executed, conditional branch, taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8182--BR-COND-TAKEN-RETIRED--Branch-instruction-architecturally-executed--conditional-branch--taken>

##### `0x8182`, BR\_COND\_TAKEN\_RETIRED, Branch instruction architecturally executed, conditional branch, taken

The counter counts each [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji) counted by both [BR\_COND\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x8181--BR-COND-RETIRED--Branch-instruction-architecturally-executed--conditional-branch?lang=en#event_br_cond_retired) and [PC\_WRITE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000C--PC-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--Software-change-of-the-PC?lang=en#event_pc_write_retired).

These are all conditional branch instructions on the architecturally executed path, where the branch is taken.
