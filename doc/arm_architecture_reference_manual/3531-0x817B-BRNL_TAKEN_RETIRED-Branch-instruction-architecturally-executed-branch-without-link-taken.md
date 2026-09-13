# ​0x817B, BRNL_TAKEN_RETIRED, Branch instruction architecturally executed, branch without link, taken

Source: <https://developer.arm.com/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x817B--BRNL-TAKEN-RETIRED--Branch-instruction-architecturally-executed--branch-without-link--taken>

##### `0x817B`, BRNL\_TAKEN\_RETIRED, Branch instruction architecturally executed, branch without link, taken

The counter counts each [Software change of the PC](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-1-Definitions/-D14-1-1-Definition-of-terms?lang=en#cacigiji) counted by [PC\_WRITE\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x000C--PC-WRITE-RETIRED--Instruction-architecturally-executed--Condition-code-check-pass--Software-change-of-the-PC?lang=en#event_pc_write_retired) that is not counted by [BL\_TAKEN\_RETIRED](/documentation/ddi0487/mc/-Part-D-The-AArch64-System-Level-Architecture/-Chapter-D14-PMU-Event-Descriptions/-D14-3-Common-event-numbers/-0x817A--BL-TAKEN-RETIRED--Branch-instruction-architecturally-executed--branch-with-link--taken?lang=en#event_bl_taken_retired).

These are all branch without link instructions on the architecturally executed path, where the branch is taken.
